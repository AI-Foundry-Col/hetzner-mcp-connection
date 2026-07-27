"""
Cliente principal para la API de Hetzner Cloud

Sigue los principios NUPP:
- Open: Cliente abierto y extensible
- Minimalist: Implementación limpia y eficiente
- Modular: Fácil de extender con nuevos endpoints
"""

import json
import logging
import time
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union

import requests
from tenacity import Retrying, stop_after_attempt, wait_exponential

from hetzner_mcp.core.config import settings
from hetzner_mcp.core.exceptions import (
    HetznerAPIError,
    HetznerAuthenticationError,
    HetznerRateLimitError,
    HetznerResourceNotFoundError,
    HetznerSafeModeError,
    create_exception_from_api_error,
)

logger = logging.getLogger(__name__)

T = TypeVar("T")


class HetznerClient:
    """
    Cliente principal para interactuar con la API de Hetzner Cloud.
    
    Este cliente proporciona métodos para todas las operaciones de la API de Hetzner,
    incluyendo servidores, volúmenes, redes, firewalls, load balancers, etc.
    
    Ejemplo de uso:
        client = HetznerClient()
        servers = client.servers.list()
        for server in servers:
            print(f"Servidor: {server.name} (ID: {server.id})")
    """

    def __init__(self, api_token: Optional[str] = None, api_url: Optional[str] = None):
        """
        Inicializar el cliente de Hetzner.
        
        Args:
            api_token: Token de API de Hetzner Cloud. Si no se proporciona,
                      se usará el de la configuración.
            api_url: URL base de la API. Si no se proporciona,
                    se usará el de la configuración.
        """
        self.api_token = api_token or settings.hetzner_api_token
        self.api_url = api_url or settings.hetzner_api_url
        self.timeout = settings.request_timeout
        self.max_retries = settings.max_retries
        self.retry_delay = settings.retry_delay
        self.safe_mode = settings.safe_mode
        self.protected_servers = set(settings.protected_servers)
        
        # Validar configuración
        if not self.api_token:
            raise ValueError("Se requiere un token de API de Hetzner. Configura HETZNER_API_TOKEN.")
        
        # Configurar logging
        self._setup_logging()
        
        # Headers por defecto
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
            "User-Agent": "hetzner-mcp-connection/1.0.0",
        }

    def _setup_logging(self) -> None:
        """Configurar el logging según la configuración."""
        log_level = getattr(logging, settings.log_level, logging.INFO)
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    def _check_safe_mode(self, operation: str) -> None:
        """Verificar si la operación está permitida en modo seguro."""
        write_operations = ["create", "update", "delete", "poweroff", "reboot", "reset"]
        if self.safe_mode and any(op in operation.lower() for op in write_operations):
            raise HetznerSafeModeError(operation)

    def _check_protected_server(self, server_id: int, operation: str) -> None:
        """Verificar si el servidor está protegido."""
        if server_id in self.protected_servers:
            raise HetznerSafeModeError(f"{operation} en servidor protegido {server_id}")

    def _handle_response(
        self, response: requests.Response, expected_status: int = 200
    ) -> Dict[str, Any]:
        """Manejar la respuesta de la API."""
        if response.status_code == expected_status:
            try:
                return response.json()
            except json.JSONDecodeError:
                return {}
        
        # Manejar errores
        try:
            error_data = response.json()
            error_info = error_data.get("error", {})
        except (json.JSONDecodeError, KeyError):
            error_info = {"code": "unknown", "message": response.text or "Error desconocido"}
        
        # Crear excepción adecuada
        exception = create_exception_from_api_error(
            response.status_code,
            error_info,
            f"Error {response.status_code}: {response.text}"
        )
        
        logger.error(f"Error de API: {exception}")
        raise exception

    def _retry_on_rate_limit(func: Callable[..., T]) -> Callable[..., T]:
        """Decorator para reintentar en caso de rate limit."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            retrying = Retrying(
                stop=stop_after_attempt(settings.max_retries),
                wait=wait_exponential(multiplier=1, min=settings.retry_delay, max=10),
                retry=(
                    lambda e: isinstance(e, HetznerRateLimitError)
                    and getattr(e, "retry_after", 0) > 0
                ),
            )
            try:
                return retrying(func)(*args, **kwargs)
            except Exception as e:
                if isinstance(e, HetznerRateLimitError):
                    raise
                raise HetznerRateLimitError(
                    "Máximo de reintentos alcanzado",
                    retry_after=0,
                    details={"attempts": settings.max_retries}
                )
        return wrapper

    # =========================================================================
    # Métodos HTTP Base
    # =========================================================================

    @_retry_on_rate_limit
    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        expected_status: int = 200,
    ) -> Dict[str, Any]:
        """Realizar una request HTTP síncrona."""
        url = f"{self.api_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                params=params,
                data=data,
                json=json_data,
                timeout=self.timeout,
            )
            return self._handle_response(response, expected_status)
        except requests.exceptions.Timeout:
            raise HetznerAPIError(
                f"Timeout al conectar a {url}",
                status_code=408,
                error_code="timeout",
            )
        except requests.exceptions.ConnectionError as e:
            raise HetznerAPIError(
                f"Error de conexión: {e}",
                status_code=502,
                error_code="connection_error",
            )

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Request GET."""
        return self._request("GET", endpoint, params=params, expected_status=200)

    def _post(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        expected_status: int = 201,
    ) -> Dict[str, Any]:
        """Request POST."""
        return self._request("POST", endpoint, json_data=json_data, expected_status=expected_status)

    def _put(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        expected_status: int = 200,
    ) -> Dict[str, Any]:
        """Request PUT."""
        return self._request("PUT", endpoint, json_data=json_data, expected_status=expected_status)

    def _delete(self, endpoint: str, expected_status: int = 204) -> Dict[str, Any]:
        """Request DELETE."""
        return self._request("DELETE", endpoint, expected_status=expected_status)

    # =========================================================================
    # Propiedades para sub-clientes (se importarán después)
    # =========================================================================

    @property
    def servers(self):
        """API de servidores."""
        from hetzner_mcp.servers import ServerAPI
        if not hasattr(self, "_servers"):
            self._servers = ServerAPI(self)
        return self._servers

    @property
    def volumes(self):
        """API de volúmenes."""
        from hetzner_mcp.storage import VolumeAPI
        if not hasattr(self, "_volumes"):
            self._volumes = VolumeAPI(self)
        return self._volumes

    @property
    def networks(self):
        """API de redes."""
        from hetzner_mcp.networking import NetworkAPI
        if not hasattr(self, "_networks"):
            self._networks = NetworkAPI(self)
        return self._networks

    @property
    def firewalls(self):
        """API de firewalls."""
        from hetzner_mcp.networking import FirewallAPI
        if not hasattr(self, "_firewalls"):
            self._firewalls = FirewallAPI(self)
        return self._firewalls

    @property
    def load_balancers(self):
        """API de load balancers."""
        from hetzner_mcp.networking import LoadBalancerAPI
        if not hasattr(self, "_load_balancers"):
            self._load_balancers = LoadBalancerAPI(self)
        return self._load_balancers

    @property
    def ssh_keys(self):
        """API de claves SSH."""
        from hetzner_mcp.core import SSHKeyAPI
        if not hasattr(self, "_ssh_keys"):
            self._ssh_keys = SSHKeyAPI(self)
        return self._ssh_keys

    @property
    def images(self):
        """API de imágenes."""
        from hetzner_mcp.storage import ImageAPI
        if not hasattr(self, "_images"):
            self._images = ImageAPI(self)
        return self._images

    @property
    def isos(self):
        """API de ISOs."""
        from hetzner_mcp.core import ISOAPI
        if not hasattr(self, "_isos"):
            self._isos = ISOAPI(self)
        return self._isos

    @property
    def server_types(self):
        """API de tipos de servidor."""
        from hetzner_mcp.core import ServerTypeAPI
        if not hasattr(self, "_server_types"):
            self._server_types = ServerTypeAPI(self)
        return self._server_types

    @property
    def locations(self):
        """API de localizaciones."""
        from hetzner_mcp.core import LocationAPI
        if not hasattr(self, "_locations"):
            self._locations = LocationAPI(self)
        return self._locations

    @property
    def datacenters(self):
        """API de datacenters."""
        from hetzner_mcp.core import DatacenterAPI
        if not hasattr(self, "_datacenters"):
            self._datacenters = DatacenterAPI(self)
        return self._datacenters

    @property
    def actions(self):
        """API de acciones."""
        from hetzner_mcp.core import ActionAPI
        if not hasattr(self, "_actions"):
            self._actions = ActionAPI(self)
        return self._actions
