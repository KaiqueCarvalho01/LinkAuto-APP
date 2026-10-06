"""Reusable `Annotated` dependency aliases for route signatures."""

from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from app.api.deps.authn import AuthenticatedUser, get_current_user
from app.api.deps.authz import require_roles
from app.core import Settings, get_settings
from app.core.database import get_db

DbSession = Annotated[Session, Depends(get_db)]
AppSettings = Annotated[Settings, Depends(get_settings)]
CurrentUser = Annotated[AuthenticatedUser, Depends(get_current_user)]
CurrentAluno = Annotated[AuthenticatedUser, Depends(require_roles("ALUNO"))]
CurrentInstrutor = Annotated[AuthenticatedUser, Depends(require_roles("INSTRUTOR"))]
CurrentAdmin = Annotated[AuthenticatedUser, Depends(require_roles("ADMIN"))]
