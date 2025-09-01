"""Инициализация модуля presentation/dependencies."""

from .session_deps import (
    get_session_id,
    get_or_create_session_id,
    get_optional_session_id,
    auto_session,
    require_session,
    SessionDependency
)

from .di_deps import (
    get_db_session,
    get_register_package_use_case,
    get_get_packages_use_case,
    get_get_package_details_use_case,
    get_get_package_types_use_case
)

__all__ = [
    "get_session_id",
    "get_or_create_session_id", 
    "get_optional_session_id",
    "auto_session",
    "require_session",
    "SessionDependency",
    "get_db_session",
    "get_register_package_use_case",
    "get_get_packages_use_case",
    "get_get_package_details_use_case",
    "get_get_package_types_use_case"
]
