"""
Excepciones personalizadas para Hetzner MCP Connection

Sigue los principios NUPP:
- Open: Excepciones claras y documentadas
- Minimalist: Jerarquía simple y efectiva
- Modular: Fácil de extender con nuevas excepciones
"""

from typing import Any, Dict, Optional


class HetznerError(Exception):
    """Excepción base para todos los errores de Hetzner MCP."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} | Detalles: {self.details}"
        return self.message

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message={self.message!r}, details={self.details!r})"


class HetznerAPIError(HetznerError):
    """Error general de la API de Hetzner."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, details)
        self.status_code = status_code
        self.error_code = error_code

    def __str__(self) -> str:
        parts = [self.message]
        if self.status_code:
            parts.append(f"Status: {self.status_code}")
        if self.error_code:
            parts.append(f"Código: {self.error_code}")
        if self.details:
            parts.append(f"Detalles: {self.details}")
        return " | ".join(parts)


class HetznerAuthenticationError(HetznerAPIError):
    """Error de autenticación con la API de Hetzner."""

    def __init__(
        self,
        message: str = "Error de autenticación: Token de API inválido o expirado",
        status_code: int = 401,
        error_code: str = "unauthorized",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, status_code, error_code, details)


class HetznerRateLimitError(HetznerAPIError):
    """Error por exceder el límite de requests."""

    def __init__(
        self,
        message: str = "Límite de requests excedido",
        status_code: int = 429,
        error_code: str = "rate_limit_exceeded",
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, status_code, error_code, details)
        self.retry_after = retry_after

    def __str__(self) -> str:
        base = super().__str__()
        if self.retry_after:
            base += f" | Reintentar en: {self.retry_after} segundos"
        return base


class HetznerResourceNotFoundError(HetznerAPIError):
    """Recurso no encontrado en la API de Hetzner."""

    def __init__(
        self,
        resource_type: str,
        resource_id: Any,
        message: Optional[str] = None,
        status_code: int = 404,
        error_code: str = "not_found",
        details: Optional[Dict[str, Any]] = None,
    ):
        msg = message or f"{resource_type} con ID '{resource_id}' no encontrado"
        super().__init__(msg, status_code, error_code, details)
        self.resource_type = resource_type
        self.resource_id = resource_id


class HetznerValidationError(HetznerAPIError):
    """Error de validación de datos."""

    def __init__(
        self,
        message: str = "Error de validación de datos",
        fields: Optional[Dict[str, list]] = None,
        status_code: int = 422,
        error_code: str = "invalid_input",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, status_code, error_code, details)
        self.fields = fields or {}

    def __str__(self) -> str:
        base = super().__str__()
        if self.fields:
            field_errors = ", ".join(f"{k}: {v}" for k, v in self.fields.items())
            base += f" | Campos: {field_errors}"
        return base


class HetznerConflictError(HetznerAPIError):
    """Error por conflicto de recursos."""

    def __init__(
        self,
        message: str = "Conflicto: El recurso ya existe o está en uso",
        status_code: int = 409,
        error_code: str = "conflict",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, status_code, error_code, details)


class HetznerForbiddenError(HetznerAPIError):
    """Error de permisos insuficientes."""

    def __init__(
        self,
        message: str = "Permisos insuficientes para realizar esta operación",
        status_code: int = 403,
        error_code: str = "forbidden",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, status_code, error_code, details)


class HetznerServerError(HetznerAPIError):
    """Error interno del servidor de Hetzner."""

    def __init__(
        self,
        message: str = "Error interno del servidor de Hetzner",
        status_code: int = 500,
        error_code: str = "server_error",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, status_code, error_code, details)


class HetznerSafeModeError(HetznerError):
    """Error al intentar realizar una operación en modo seguro."""

    def __init__(
        self,
        operation: str,
        message: str = "Operación bloqueada en modo seguro",
        details: Optional[Dict[str, Any]] = None,
    ):
        full_message = f"{message}: {operation}"
        super().__init__(full_message, details)
        self.operation = operation


class HetznerProtectedResourceError(HetznerError):
    """Error al intentar modificar un recurso protegido."""

    def __init__(
        self,
        resource_type: str,
        resource_id: Any,
        message: str = "Recurso protegido",
        details: Optional[Dict[str, Any]] = None,
    ):
        full_message = f"{message}: {resource_type} con ID '{resource_id}' está protegido"
        super().__init__(full_message, details)
        self.resource_type = resource_type
        self.resource_id = resource_id


# Mapeo de errores de la API de Hetzner a excepciones personalizadas
ERROR_MAPPING: Dict[str, type] = {
    "unauthorized": HetznerAuthenticationError,
    "token_readonly": HetznerAuthenticationError,
    "forbidden": HetznerForbiddenError,
    "resource_limit_exceeded": HetznerForbiddenError,
    "not_found": HetznerResourceNotFoundError,
    "invalid_input": HetznerValidationError,
    "uniqueness_error": HetznerConflictError,
    "conflict": HetznerConflictError,
    "rate_limit_exceeded": HetznerRateLimitError,
    "server_error": HetznerServerError,
    "maintenance": HetznerServerError,
    "deprecated_api_endpoint": HetznerAPIError,
    "json_error": HetznerValidationError,
    "method_not_allowed": HetznerAPIError,
    "locked": HetznerConflictError,
    "protected": HetznerForbiddenError,
    "resource_unavailable": HetznerForbiddenError,
    "service_error": HetznerServerError,
    "unsupported_error": HetznerAPIError,
    "bad_gateway": HetznerServerError,
    "unavailable": HetznerServerError,
    "timeout": HetznerServerError,
}


def create_exception_from_api_error(
    status_code: int,
    error_data: Dict[str, Any],
    default_message: str = "Error de la API de Hetzner",
) -> HetznerAPIError:
    """Crear excepción adecuada a partir de datos de error de la API."""
    error_code = error_data.get("code", "unknown")
    message = error_data.get("message", default_message)
    details = error_data.get("details", {})

    # Buscar la clase de excepción adecuada
    exception_class = ERROR_MAPPING.get(error_code, HetznerAPIError)

    # Crear instancia con parámetros adecuados
    if exception_class == HetznerValidationError and "fields" in details:
        return exception_class(
            message=message,
            fields=details.get("fields"),
            status_code=status_code,
            error_code=error_code,
            details=details,
        )

    return exception_class(
        message=message,
        status_code=status_code,
        error_code=error_code,
        details=details,
    )
