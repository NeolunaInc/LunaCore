from enum import Enum


class Role(Enum):
    VIEWER = 1
    OPERATOR = 2
    ADMIN = 3


def check_permission(user_role: Role, required_role: Role) -> bool:
    """
    Check if the user has the required permission based on role hierarchy.
    ADMIN > OPERATOR > VIEWER
    """
    return user_role.value >= required_role.value
