class SuperAdminOnlyModelAdmin:
    """Django Admin access for cross-organization models is reserved to active SUPER_ADMINs."""

    @staticmethod
    def _is_active_super_admin(user):
        return bool(
            user
            and user.is_authenticated
            and user.is_active
            and getattr(user, "can_login", False)
            and getattr(user, "role", None) == "SUPER_ADMIN"
        )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not self._is_active_super_admin(request.user):
            return queryset.none()
        return queryset

    def has_module_permission(self, request):
        return self._is_active_super_admin(request.user)

    def has_view_permission(self, request, obj=None):
        return self._is_active_super_admin(request.user)

    def has_add_permission(self, request):
        return self._is_active_super_admin(request.user)

    def has_change_permission(self, request, obj=None):
        return self._is_active_super_admin(request.user)

    def has_delete_permission(self, request, obj=None):
        return self._is_active_super_admin(request.user)
