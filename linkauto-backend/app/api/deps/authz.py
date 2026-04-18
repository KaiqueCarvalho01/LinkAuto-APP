from __future__ import annotations

from collections.abc import Callable

from fastapi import Depends, HTTPException, status

from app.api.deps.authn import AuthenticatedUser, get_current_user


def require_roles(*allowed_roles: str) -> Callable[[AuthenticatedUser], AuthenticatedUser]:
    allowed = set(allowed_roles)

    def role_dependency(
        current_user: AuthenticatedUser = Depends(get_current_user),
    ) -> AuthenticatedUser:
        if allowed.intersection(current_user.roles):
            return current_user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "FORBIDDEN", "message": "User does not have required role."},
        )

    return role_dependency
