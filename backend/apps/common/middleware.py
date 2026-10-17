from django.http import HttpResponseForbidden


class SuperAdminOnlyAdminSiteMiddleware:
    """Block authenticated staff from all Django Admin routes unless they are active SUPER_ADMINs."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/admin/") and request.path != "/admin/login/":
            user = getattr(request, "user", None)
            if user is not None and user.is_authenticated and not (
                user.is_staff
                and user.is_active
                and user.can_login
                and user.role == "SUPER_ADMIN"
            ):
                return HttpResponseForbidden("Django Admin is reserved to active SUPER_ADMIN accounts.")
        return self.get_response(request)
