"""
Configuración del cliente Hetzner MCP

Sigue los principios NUPP:
- Open: Configuración abierta y personalizable
- Minimalist: Solo lo esencial
- Modular: Fácil de extender
"""

from functools import lru_cache
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración principal de la aplicación."""

    # Configuración de API
    hetzner_api_token: str = Field(
        default="",
        description="Token de API de Hetzner Cloud",
        env="HETZNER_API_TOKEN",
    )
    hetzner_api_url: str = Field(
        default="https://api.hetzner.cloud/v1",
        description="URL base de la API de Hetzner",
        env="HETZNER_API_URL",
    )

    # Configuración de conexión
    request_timeout: int = Field(
        default=30,
        ge=5,
        le=300,
        description="Timeout para requests en segundos",
        env="REQUEST_TIMEOUT",
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Número máximo de reintentos",
        env="MAX_RETRIES",
    )
    retry_delay: float = Field(
        default=1.0,
        ge=0.1,
        le=10.0,
        description="Retraso entre reintentos en segundos",
        env="RETRY_DELAY",
    )

    # Configuración de logging
    log_level: str = Field(
        default="INFO",
        description="Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
        env="LOG_LEVEL",
    )
    log_format: str = Field(
        default="simple",
        description="Formato de logging (simple, detailed, json)",
        env="LOG_FORMAT",
    )

    # Configuración de paginación
    page_size: int = Field(
        default=25,
        ge=1,
        le=50,
        description="Número de resultados por página",
        env="PAGE_SIZE",
    )

    # Configuración de automatización
    backup_dir: str = Field(
        default="./backups",
        description="Directorio para backups locales",
        env="BACKUP_DIR",
    )
    auto_prefix: str = Field(
        default="auto-",
        description="Prefijo para recursos creados automáticamente",
        env="AUTO_PREFIX",
    )

    # Configuración de seguridad
    safe_mode: bool = Field(
        default=False,
        description="Modo seguro (solo lectura)",
        env="SAFE_MODE",
    )
    protected_servers: List[int] = Field(
        default_factory=list,
        description="Lista de IDs de servidores protegidos",
        env="PROTECTED_SERVERS",
    )

    # Validación
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"log_level debe ser uno de {valid_levels}")
        return v.upper()

    @field_validator("log_format")
    @classmethod
    def validate_log_format(cls, v: str) -> str:
        valid_formats = ["simple", "detailed", "json"]
        if v.lower() not in valid_formats:
            raise ValueError(f"log_format debe ser uno de {valid_formats}")
        return v.lower()

    @field_validator("protected_servers")
    @classmethod
    def validate_protected_servers(cls, v: List[int]) -> List[int]:
        # Convertir de string a lista si es necesario
        if isinstance(v, str):
            if v.strip() == "":
                return []
            try:
                return [int(x.strip()) for x in v.split(",") if x.strip()]
            except ValueError:
                raise ValueError("protected_servers debe ser una lista de enteros")
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    """Obtener la configuración (cacheada)."""
    return Settings()


# Instancia global de configuración
settings = get_settings()


def reset_settings() -> None:
    """Reiniciar la caché de configuración."""
    get_settings.cache_clear()
