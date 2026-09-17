import json

from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from web.services.client import call
from web.services.exceptions import ServiceError


async def upload_widget_test_view(request):
    if not request.session.get('access_token'):
        return redirect('/login/')
    return render(request, 'attachments/upload_test.html')


@require_POST
async def request_upload_view(request):
    if not request.session.get('access_token'):
        return JsonResponse({'detail': 'Authentication required.', 'errors': None}, status=401)

    try:
        body = json.loads(request.body)
    except ValueError:
        return JsonResponse({'detail': 'Invalid JSON body.', 'errors': None}, status=400)

    try:
        response = await call(request, 'POST', 'attachments', '/attachments/request-upload/', json=body)
    except ServiceError as exc:
        return JsonResponse({'detail': exc.detail, 'errors': exc.errors}, status=exc.status_code)

    return JsonResponse(response.json())


@require_POST
async def confirm_upload_view(request, attachment_id):
    if not request.session.get('access_token'):
        return JsonResponse({'detail': 'Authentication required.', 'errors': None}, status=401)

    try:
        response = await call(request, 'POST', 'attachments', f'/attachments/{attachment_id}/confirm/')
    except ServiceError as exc:
        return JsonResponse({'detail': exc.detail, 'errors': exc.errors}, status=exc.status_code)

    return JsonResponse(response.json())
