def page_context(page: dict) -> dict:
    """Turn a {count, limit, offset, results} envelope into template-ready nav vars.

    Every list endpoint across the backends returns this same shape, so every
    list page in devboard-web needs the same prev/next math -- computed here
    once instead of in template arithmetic (Django templates can't do it).
    """
    count, limit, offset = page['count'], page['limit'], page['offset']
    return {
        'results': page['results'],
        'count': count,
        'limit': limit,
        'offset': offset,
        'has_prev': offset > 0,
        'has_next': offset + limit < count,
        'prev_offset': max(offset - limit, 0),
        'next_offset': offset + limit,
    }
