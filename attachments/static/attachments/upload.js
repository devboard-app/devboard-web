// Generic attach-a-file widget: two fetch calls around the browser's own PUT
// of the file bytes straight to MinIO. devboard-web never sees the bytes.
//
// Drop `templates/attachments/upload_widget.html` into any page and listen
// for the `attachment-uploaded` event on the `[data-upload-widget]` element
// to wire the result into that page's own form (comment body, avatar field).

function getCookie(name) {
    const match = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return match ? decodeURIComponent(match.pop()) : '';
}

async function uploadAttachment(file, { contextType, contextId } = {}) {
    const csrftoken = getCookie('csrftoken');

    const requestResp = await fetch('/api/attachments/request-upload/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken },
        body: JSON.stringify({
            filename: file.name,
            content_type: file.type,
            size: file.size,
            context_type: contextType || null,
            context_id: contextId || null,
        }),
    });
    if (!requestResp.ok) {
        const err = await requestResp.json().catch(() => ({}));
        throw new Error(err.detail || 'Could not start upload.');
    }
    const { attachment_id, upload_url } = await requestResp.json();

    const putResp = await fetch(upload_url, {
        method: 'PUT',
        headers: { 'Content-Type': file.type },
        body: file,
    });
    if (!putResp.ok) {
        throw new Error('Uploading the file failed.');
    }

    const confirmResp = await fetch(`/api/attachments/${attachment_id}/confirm/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': csrftoken },
    });
    if (!confirmResp.ok) {
        const err = await confirmResp.json().catch(() => ({}));
        throw new Error(err.detail || 'Could not confirm the upload.');
    }
    return confirmResp.json();
}

function initUploadWidget(root) {
    const form = root.querySelector('[data-upload-form]');
    const input = root.querySelector('[data-upload-input]');
    const status = root.querySelector('[data-upload-status]');

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const file = input.files[0];
        if (!file) return;

        status.textContent = 'Uploading...';
        try {
            const attachment = await uploadAttachment(file, {
                contextType: root.dataset.contextType,
                contextId: root.dataset.contextId,
            });
            status.textContent = `Uploaded: ${attachment.filename}`;
            form.reset();
            root.dispatchEvent(new CustomEvent('attachment-uploaded', { detail: attachment, bubbles: true }));
        } catch (err) {
            status.textContent = err.message;
        }
    });
}

document.querySelectorAll('[data-upload-widget]').forEach(initUploadWidget);
