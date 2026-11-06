def telemed_global_context(request):
    """
    Injects platform-wide clinical and user role information into every template.
    """
    if not hasattr(request, 'user') or not request.user.is_authenticated:
        return {
            'is_parent': False,
            'is_doctor': False,
            'is_admin': False,
            'active_child_count': 0,
            'platform_name': 'CareNest Pediatric Teledermatology',
        }

    is_parent = request.user.is_parent() if hasattr(request.user, 'is_parent') else False
    is_doctor = request.user.is_doctor() if hasattr(request.user, 'is_doctor') else False
    is_admin = request.user.is_admin() if hasattr(request.user, 'is_admin') else False

    child_count = 0
    if is_parent and hasattr(request.user, 'children'):
        child_count = request.user.children.count()

    return {
        'is_parent': is_parent,
        'is_doctor': is_doctor,
        'is_admin': is_admin,
        'active_child_count': child_count,
        'platform_name': 'CareNest Pediatric Teledermatology',
    }

