from services.authz.rbac import Role, check_permission


class TestRBAC:
    def test_viewer_has_viewer_permission(self):
        assert check_permission(Role.VIEWER, Role.VIEWER) is True

    def test_viewer_does_not_have_operator_permission(self):
        assert check_permission(Role.VIEWER, Role.OPERATOR) is False

    def test_viewer_does_not_have_admin_permission(self):
        assert check_permission(Role.VIEWER, Role.ADMIN) is False

    def test_operator_has_viewer_permission(self):
        assert check_permission(Role.OPERATOR, Role.VIEWER) is True

    def test_operator_has_operator_permission(self):
        assert check_permission(Role.OPERATOR, Role.OPERATOR) is True

    def test_operator_does_not_have_admin_permission(self):
        assert check_permission(Role.OPERATOR, Role.ADMIN) is False

    def test_admin_has_all_permissions(self):
        assert check_permission(Role.ADMIN, Role.VIEWER) is True
        assert check_permission(Role.ADMIN, Role.OPERATOR) is True
        assert check_permission(Role.ADMIN, Role.ADMIN) is True
