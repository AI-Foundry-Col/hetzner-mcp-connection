"""
Hetzner MCP Connection

MCP para conectar Mistral Work a los servicios VPS de Hetzner Cloud.
Permite interacción en lenguaje natural (español) y automatización de tareas.

Basado en los principios NUPP de OMIMO: Open, Minimalist, Modular
"""

from hetzner_mcp.core.client import HetznerClient
from hetzner_mcp.core.config import settings
from hetzner_mcp.core.exceptions import (
    HetznerAPIError,
    HetznerAuthenticationError,
    HetznerRateLimitError,
    HetznerResourceNotFoundError,
    HetznerValidationError,
)
from hetzner_mcp.core.models import (
    Action,
    ActionListResponse,
    Backup,
    Certificate,
    Datacenter,
    Firewall,
    FloatingIP,
    Image,
    ISO,
    LoadBalancer,
    LoadBalancerType,
    Location,
    Network,
    Pagination,
    PlacementGroup,
    PrimaryIP,
    Server,
    ServerType,
    SSHKey,
    Volume,
)

__version__ = "1.0.0"
__author__ = "AI Foundry Col"
__description__ = "MCP para conectar Mistral Work a Hetzner Cloud VPS"
__license__ = "MIT"

# Re-exportar todo para facilidad de uso
__all__ = [
    # Cliente
    "HetznerClient",
    # Configuración
    "settings",
    # Excepciones
    "HetznerAPIError",
    "HetznerAuthenticationError",
    "HetznerRateLimitError",
    "HetznerResourceNotFoundError",
    "HetznerValidationError",
    # Modelos
    "Action",
    "ActionListResponse",
    "Backup",
    "Certificate",
    "Datacenter",
    "Firewall",
    "FloatingIP",
    "Image",
    "ISO",
    "LoadBalancer",
    "LoadBalancerType",
    "Location",
    "Network",
    "Pagination",
    "PlacementGroup",
    "PrimaryIP",
    "Server",
    "ServerType",
    "SSHKey",
    "Volume",
]
