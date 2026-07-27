"""
Modelos Pydantic para la API de Hetzner Cloud

Sigue los principios NUPP:
- Open: Modelos abiertos y extensibles
- Minimalist: Solo los campos esenciales
- Modular: Cada recurso en su propio modelo
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import Field, field_validator
from typing_extensions import TypedDict


# =============================================================================
# Enums
# =============================================================================


class ActionCommand(str, Enum):
    """Comandos de acciones de Hetzner."""

    ADD_TO_PLACEMENT_GROUP = "add_to_placement_group"
    ATTACH_ISO = "attach_iso"
    ATTACH_TO_NETWORK = "attach_to_network"
    CHANGE_ALIAS_IPS = "change_alias_ips"
    CHANGE_DNS_PTR = "change_dns_ptr"
    CHANGE_PROTECTION = "change_protection"
    CHANGE_TYPE = "change_type"
    CREATE_IMAGE = "create_image"
    DETACH_FROM_NETWORK = "detach_from_network"
    DETACH_ISO = "detach_iso"
    DISABLE_BACKUP = "disable_backup"
    DISABLE_RESCUE = "disable_rescue"
    ENABLE_BACKUP = "enable_backup"
    ENABLE_RESCUE = "enable_rescue"
    POWEROFF = "poweroff"
    POWERON = "poweron"
    REBOOT = "reboot"
    REBUILD = "rebuild"
    REMOVE_FROM_PLACEMENT_GROUP = "remove_from_placement_group"
    REQUEST_CONSOLE = "request_console"
    RESET = "reset"
    RESET_PASSWORD = "reset_password"
    SHUTDOWN = "shutdown"
    # Acciones de volumen
    ATTACH = "attach"
    DETACH = "detach"
    RESIZE = "resize"
    # Acciones de firewall
    APPLY_TO_RESOURCES = "apply_to_resources"
    REMOVE_FROM_RESOURCES = "remove_from_resources"
    SET_RULES = "set_rules"
    # Acciones de load balancer
    ADD_SERVICE = "add_service"
    ADD_TARGET = "add_target"
    ATTACH_TO_NETWORK_LB = "attach_to_network"
    CHANGE_ALGORITHM = "change_algorithm"
    CHANGE_DNS_PTR_LB = "change_dns_ptr"
    CHANGE_PROTECTION_LB = "change_protection"
    CHANGE_TYPE_LB = "change_type"
    DELETE_SERVICE = "delete_service"
    DETACH_FROM_NETWORK_LB = "detach_from_network"
    DISABLE_PUBLIC_INTERFACE = "disable_public_interface"
    ENABLE_PUBLIC_INTERFACE = "enable_public_interface"
    REMOVE_TARGET = "remove_target"
    UPDATE_SERVICE = "update_service"
    # Acciones de IP
    ASSIGN = "assign"
    UNASSIGN = "unassign"
    CHANGE_DNS_PTR_IP = "change_dns_ptr"
    CHANGE_PROTECTION_IP = "change_protection"


class ActionStatus(str, Enum):
    """Estados de las acciones."""

    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"


class ServerStatus(str, Enum):
    """Estados del servidor."""

    OFF = "off"
    RUNNING = "running"
    INITIALIZING = "initializing"
    REBOOTING = "rebooting"
    MIGRATING = "migrating"
    DELETING = "deleting"
    UNKNOWN = "unknown"


class ServerTypeClass(str, Enum):
    """Clases de tipos de servidor."""

    SHARED = "shared"
    DEDICATED = "dedicated"


class ImageType(str, Enum):
    """Tipos de imágenes."""

    SYSTEM = "system"
    SNAPSHOT = "snapshot"
    BACKUP = "backup"
    APP = "app"


class ImageStatus(str, Enum):
    """Estados de las imágenes."""

    AVAILABLE = "available"
    CREATING = "creating"
    ERROR = "error"


class ISOStatus(str, Enum):
    """Estados de los ISOs."""

    AVAILABLE = "available"
    CREATING = "creating"


class ISOType(str, Enum):
    """Tipos de ISOs."""

    PUBLIC = "public"
    PRIVATE = "private"


class VolumeStatus(str, Enum):
    """Estados de los volúmenes."""

    AVAILABLE = "available"
    IN_USE = "in_use"
    CREATING = "creating"
    MIGRATING = "migrating"
    DELETING = "deleting"


class FirewallProtocol(str, Enum):
    """Protocolos de firewall."""

    TCP = "tcp"
    UDP = "udp"
    ICMP = "icmp"
    ESP = "esp"
    GRE = "gre"


class FirewallDirection(str, Enum):
    """Direcciones de firewall."""

    IN = "in"
    OUT = "out"


class FirewallAction(str, Enum):
    """Acciones de firewall."""

    ACCEPT = "ACCEPT"
    DROP = "DROP"
    REJECT = "REJECT"


class LoadBalancerAlgorithmType(str, Enum):
    """Tipos de algoritmo de load balancer."""

    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    SOURCE_IP_HASH = "source_ip_hash"


class LoadBalancerProtocol(str, Enum):
    """Protocolos de load balancer."""

    HTTP = "http"
    HTTPS = "https"
    TCP = "tcp"


class LoadBalancerStatus(str, Enum):
    """Estados de load balancer."""

    ACTIVE = "active"
    INITIALIZING = "initializing"
    DELETING = "deleting"
    ERROR = "error"


class NetworkType(str, Enum):
    """Tipos de subnet."""

    CLOUD = "cloud"
    SERVER = "server"
    VSWITCH = "vswitch"


class IPType(str, Enum):
    """Tipos de IP."""

    IPv4 = "ipv4"
    IPv6 = "ipv6"


class ProtectionStatus(str, Enum):
    """Estados de protección."""

    UNPROTECTED = "unprotected"
    PROTECTED = "protected"


class PlacementGroupType(str, Enum):
    """Tipos de placement group."""

    SPREAD = "spread"


# =============================================================================
# Modelos Base
# =============================================================================


class Pagination(TypedDict):
    """Información de paginación."""

    page: int
    per_page: int
    previous_page: Optional[int]
    next_page: Optional[int]
    last_page: Optional[int]
    total_entries: Optional[int]


class Meta(TypedDict):
    """Metadatos de la respuesta."""

    pagination: Optional[Pagination]


class ResourceReference(TypedDict):
    """Referencia a un recurso."""

    id: int
    type: str


class ErrorDetails(TypedDict):
    """Detalles de error."""

    code: str
    message: str
    details: Optional[Dict[str, Any]]


# =============================================================================
# Modelos Principales
# =============================================================================


class ServerType(BaseModel):
    """Tipo de servidor de Hetzner."""

    id: int
    name: str
    description: str
    cores: int
    memory: float  # GB
    disk: int  # GB
    storage_type: str
    cpu_type: str
    architecture: str
    included_traffic: Optional[int] = None
    outgoing_traffic: Optional[int] = None
    prices: List[Dict[str, Any]] = Field(default_factory=list)
    available_in: List[Dict[str, Any]] = Field(default_factory=list)

    @property
    def price_per_month(self) -> Optional[float]:
        """Obtener precio mensual."""
        for price in self.prices:
            if price.get("billing_model") == "monthly":
                return float(price.get("price_per_month", {}).get("net", 0))
        return None

    @property
    def price_per_hour(self) -> Optional[float]:
        """Obtener precio por hora."""
        for price in self.prices:
            if price.get("billing_model") == "hourly":
                return float(price.get("price_per_hour", {}).get("net", 0))
        return None


class Server(BaseModel):
    """Servidor de Hetzner."""

    id: int
    name: str
    status: ServerStatus
    created: datetime
    server_type: Dict[str, Any]  # ServerType
    datacenter: Optional[Dict[str, Any]] = None
    image: Optional[Dict[str, Any]] = None
    iso: Optional[Dict[str, Any]] = None
    rescue_enabled: bool = False
    backup_window: Optional[str] = None
    outgoing_traffic: Optional[int] = None
    incoming_traffic: Optional[int] = None
    included_traffic: Optional[int] = None
    ipv4_address: Optional[str] = None
    ipv6_address: Optional[str] = None
    ipv6_network: Optional[str] = None
    volumes: List[Dict[str, Any]] = Field(default_factory=list)
    primary_disk_size: Optional[int] = None
    primary_ipv4: Optional[Dict[str, Any]] = None
    primary_ipv6: Optional[Dict[str, Any]] = None
    labels: Dict[str, str] = Field(default_factory=dict)
    protection: Dict[str, bool] = Field(default_factory=dict)
    locked: bool = False

    @property
    def is_running(self) -> bool:
        """Verificar si el servidor está en ejecución."""
        return self.status == ServerStatus.RUNNING

    @property
    def is_protected(self) -> bool:
        """Verificar si el servidor está protegido."""
        return self.protection.get("delete", False) or self.protection.get("rebuild", False)

    @property
    def public_ipv4(self) -> Optional[str]:
        """Obtener IP pública IPv4."""
        return self.ipv4_address or (self.primary_ipv4.get("ip") if self.primary_ipv4 else None)

    @property
    def public_ipv6(self) -> Optional[str]:
        """Obtener IP pública IPv6."""
        return self.ipv6_address

    def get_label(self, key: str, default: str = "") -> str:
        """Obtener valor de una etiqueta."""
        return self.labels.get(key, default)


class Action(BaseModel):
    """Acción de Hetzner."""

    id: int
    command: ActionCommand
    status: ActionStatus
    started: datetime
    finished: Optional[datetime] = None
    progress: int = 0
    resources: List[ResourceReference] = Field(default_factory=list)
    error: Optional[Dict[str, Any]] = None

    @property
    def is_completed(self) -> bool:
        """Verificar si la acción está completada."""
        return self.status in [ActionStatus.SUCCESS, ActionStatus.ERROR]

    @property
    def is_successful(self) -> bool:
        """Verificar si la acción fue exitosa."""
        return self.status == ActionStatus.SUCCESS

    @property
    def is_failed(self) -> bool:
        """Verificar si la acción falló."""
        return self.status == ActionStatus.ERROR


class ActionListResponse(BaseModel):
    """Respuesta de lista de acciones."""

    actions: List[Action] = Field(default_factory=list)
    meta: Optional[Meta] = None


class Image(BaseModel):
    """Imagen de Hetzner."""

    id: int
    type: ImageType
    status: Optional[ImageStatus] = None
    name: str
    description: Optional[str] = None
    image_size: Optional[float] = None  # GB
    disk_size: Optional[int] = None  # GB
    created: Optional[datetime] = None
    created_from: Optional[Dict[str, Any]] = None
    bound_to: Optional[int] = None  # Server ID
    os_flavor: Optional[str] = None
    os_version: Optional[str] = None
    rapid_deploy: bool = False
    protection: Dict[str, bool] = Field(default_factory=dict)
    labels: Dict[str, str] = Field(default_factory=dict)
    deprecated: Optional[datetime] = None

    @property
    def is_available(self) -> bool:
        """Verificar si la imagen está disponible."""
        return self.status == ImageStatus.AVAILABLE


class ISO(BaseModel):
    """ISO de Hetzner."""

    id: int
    name: str
    description: Optional[str] = None
    type: ISOType
    status: Optional[ISOStatus] = None
    deprecated: Optional[datetime] = None


class Datacenter(BaseModel):
    """Datacenter de Hetzner."""

    id: int
    name: str
    description: str
    location: Dict[str, Any]  # Location
    server_types: Dict[str, Any] = Field(default_factory=dict)


class Location(BaseModel):
    """Localización de Hetzner."""

    id: int
    name: str
    description: str
    country: str
    city: str
    latitude: float
    longitude: float
    network_zone: str
    datacenters: List[Dict[str, Any]] = Field(default_factory=list)


class Volume(BaseModel):
    """Volumen de Hetzner."""

    id: int
    name: str
    created: datetime
    size: int  # GB
    status: VolumeStatus
    location: Dict[str, Any]  # Location
    server: Optional[Dict[str, Any]] = None  # Server
    linux_device: Optional[str] = None
    protection: Dict[str, bool] = Field(default_factory=dict)
    labels: Dict[str, str] = Field(default_factory=dict)

    @property
    def is_attached(self) -> bool:
        """Verificar si el volumen está conectado a un servidor."""
        return self.server is not None

    @property
    def is_available(self) -> bool:
        """Verificar si el volumen está disponible."""
        return self.status == VolumeStatus.AVAILABLE


class Network(BaseModel):
    """Red de Hetzner."""

    id: int
    name: str
    created: datetime
    ip_range: str
    subnets: List[Dict[str, Any]] = Field(default_factory=list)
    routes: List[Dict[str, Any]] = Field(default_factory=list)
    servers: List[Dict[str, Any]] = Field(default_factory=list)
    protection: Dict[str, bool] = Field(default_factory=dict)
    labels: Dict[str, str] = Field(default_factory=dict)


class Subnet(BaseModel):
    """Subred de Hetzner."""

    id: int
    type: NetworkType
    network_id: int
    network: str  # CIDR
    subnet: str  # CIDR
    gateway: str
    vswitch_id: Optional[int] = None
    ip_range: str


class FirewallRule(BaseModel):
    """Regla de firewall."""

    direction: FirewallDirection
    protocol: Optional[FirewallProtocol] = None
    port: Optional[Union[str, int]] = None
    source_ips: Optional[List[str]] = None
    destination_ips: Optional[List[str]] = None
    action: FirewallAction
    description: Optional[str] = None


class Firewall(BaseModel):
    """Firewall de Hetzner."""

    id: int
    name: str
    created: datetime
    rules: List[FirewallRule] = Field(default_factory=list)
    applied_to: List[Dict[str, Any]] = Field(default_factory=list)  # Resources
    labels: Dict[str, str] = Field(default_factory=dict)
    protection: Dict[str, bool] = Field(default_factory=dict)


class PrimaryIP(BaseModel):
    """IP primaria de Hetzner."""

    id: int
    type: IPType
    ip: str
    created: datetime
    datacenter: Optional[Dict[str, Any]] = None
    assigned_to: Optional[Dict[str, Any]] = None  # Server
    auto_delete: bool = False
    protection: Dict[str, bool] = Field(default_factory=dict)
    labels: Dict[str, str] = Field(default_factory=dict)
    name: Optional[str] = None
    dns_ptr: Optional[List[str]] = None


class FloatingIP(BaseModel):
    """IP flotante de Hetzner."""

    id: int
    type: IPType
    ip: str
    created: datetime
    description: Optional[str] = None
    server: Optional[Dict[str, Any]] = None  # Server
    dns_ptr: Optional[List[str]] = None
    blocked: bool = False
    home_location: Optional[Dict[str, Any]] = None
    protection: Dict[str, bool] = Field(default_factory=dict)
    labels: Dict[str, str] = Field(default_factory=dict)


class LoadBalancerType(BaseModel):
    """Tipo de load balancer de Hetzner."""

    id: int
    name: str
    description: str
    max_services: int
    max_targets: int
    max_assigned_certificates: int
    prices: List[Dict[str, Any]] = Field(default_factory=list)
    available_in: List[Dict[str, Any]] = Field(default_factory=list)


class LoadBalancerService(BaseModel):
    """Servicio de load balancer."""

    id: int
    protocol: LoadBalancerProtocol
    listen_port: int
    destination_port: int
    proxyprotocol: bool = False
    health_check: Optional[Dict[str, Any]] = None
    http: Optional[Dict[str, Any]] = None


class LoadBalancerTarget(BaseModel):
    """Target de load balancer."""

    id: int
    type: str  # server, ip
    server: Optional[Dict[str, Any]] = None
    ip: Optional[Dict[str, Any]] = None
    use_private_ip: bool = False
    health_status: Optional[List[str]] = None


class LoadBalancer(BaseModel):
    """Load balancer de Hetzner."""

    id: int
    name: str
    created: datetime
    status: LoadBalancerStatus
    public_net: Dict[str, Any]  # Network info
    private_net: Optional[List[Dict[str, Any]]] = None
    location: Dict[str, Any]  # Location
    load_balancer_type: Dict[str, Any]  # LoadBalancerType
    algorithm: Dict[str, Any] = Field(default_factory=dict)
    services: List[LoadBalancerService] = Field(default_factory=list)
    targets: List[LoadBalancerTarget] = Field(default_factory=list)
    protection: Dict[str, bool] = Field(default_factory=dict)
    labels: Dict[str, str] = Field(default_factory=dict)
    outgoing_traffic: Optional[int] = None
    incoming_traffic: Optional[int] = None
    included_traffic: Optional[int] = None


class PlacementGroup(BaseModel):
    """Grupo de placement de Hetzner."""

    id: int
    name: str
    created: datetime
    type: PlacementGroupType
    servers: List[Dict[str, Any]] = Field(default_factory=list)
    labels: Dict[str, str] = Field(default_factory=dict)
    protection: Dict[str, bool] = Field(default_factory=dict)


class SSHKey(BaseModel):
    """Clave SSH de Hetzner."""

    id: int
    name: str
    fingerprint: str
    public_key: str
    created: datetime
    labels: Dict[str, str] = Field(default_factory=dict)
    protection: Dict[str, bool] = Field(default_factory=dict)


class Certificate(BaseModel):
    """Certificado de Hetzner."""

    id: int
    name: str
    certificate: str
    private_key: Optional[str] = None
    created: datetime
    status: str
    domain_names: List[str] = Field(default_factory=list)
    labels: Dict[str, str] = Field(default_factory=dict)
    protection: Dict[str, bool] = Field(default_factory=dict)
    used_by: List[Dict[str, Any]] = Field(default_factory=list)


class Backup(BaseModel):
    """Backup de Hetzner."""

    id: int
    type: str
    status: str
    started: datetime
    finished: Optional[datetime] = None
    server: Dict[str, Any]  # Server
    image: Optional[Dict[str, Any]] = None


# =============================================================================
# Request Models
# =============================================================================


class CreateServerRequest(BaseModel):
    """Request para crear un servidor."""

    name: str = Field(..., min_length=1, max_length= 64)
    server_type: Union[str, int] = Field(..., description="Nombre o ID del tipo de servidor")
    image: Union[str, int] = Field(..., description="Nombre o ID de la imagen")
    location: Union[str, int] = Field(..., description="Nombre o ID de la localización")
    ssh_keys: Optional[List[Union[str, int]]] = Field(
        default=None, description="Lista de nombres o IDs de claves SSH"
    )
    volumes: Optional[List[Union[str, int]]] = Field(
        default=None, description="Lista de nombres o IDs de volúmenes"
    )
    networks: Optional[List[Union[str, int]]] = Field(
        default=None, description="Lista de nombres o IDs de redes"
    )
    user_data: Optional[str] = Field(default=None, description="User data para cloud-init")
    labels: Optional[Dict[str, str]] = Field(default=None, description="Etiquetas del servidor")
    backup_window: Optional[str] = Field(
        default=None, description="Ventana de backup (ej: 00-06)"
    )
    ipv4_address: Optional[str] = Field(default=None, description="IPv4 estática")
    ipv6_address: Optional[str] = Field(default=None, description="IPv6 estática")
    firewall_ids: Optional[List[int]] = Field(default=None, description="IDs de firewalls")
    placement_group_id: Optional[int] = Field(default=None, description="ID del placement group")
    start_after_create: bool = Field(default=True, description="Iniciar después de crear")
    automount: bool = Field(default=False, description="Montar automáticamente volúmenes")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        import re
        if not re.match(r"^[a-zA-Z0-9-]+$", v):
            raise ValueError("El nombre solo puede contener letras, números y guiones")
        return v


class UpdateServerRequest(BaseModel):
    """Request para actualizar un servidor."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=64)
    labels: Optional[Dict[str, Optional[str]]] = Field(default=None)
    user_data: Optional[str] = Field(default=None)
    backup_window: Optional[str] = Field(default=None)


class CreateVolumeRequest(BaseModel):
    """Request para crear un volumen."""

    name: str = Field(..., min_length=1, max_length=64)
    size: int = Field(..., ge=10, le=10000, description="Tamaño en GB")
    location: Union[str, int] = Field(..., description="Nombre o ID de la localización")
    labels: Optional[Dict[str, str]] = Field(default=None)
    automount: bool = Field(default=True, description="Montar automáticamente")
    format: Optional[str] = Field(default=None, description="Formato (ext4, xfs, etc.)")


class CreateNetworkRequest(BaseModel):
    """Request para crear una red."""

    name: str = Field(..., min_length=1, max_length=64)
    ip_range: str = Field(..., description="Rango IP en notación CIDR (ej: 10.0.0.0/16)")
    labels: Optional[Dict[str, str]] = Field(default=None)


class CreateFirewallRequest(BaseModel):
    """Request para crear un firewall."""

    name: str = Field(..., min_length=1, max_length=64)
    rules: List[Dict[str, Any]] = Field(..., description="Lista de reglas de firewall")
    labels: Optional[Dict[str, str]] = Field(default=None)


class CreateLoadBalancerRequest(BaseModel):
    """Request para crear un load balancer."""

    name: str = Field(..., min_length=1, max_length=64)
    load_balancer_type: Union[str, int] = Field(
        ..., description="Nombre o ID del tipo de load balancer"
    )
    location: Union[str, int] = Field(..., description="Nombre o ID de la localización")
    algorithm: Dict[str, Any] = Field(
        default_factory=dict, description="Configuración del algoritmo"
    )
    labels: Optional[Dict[str, str]] = Field(default=None)


class CreateSSHKeyRequest(BaseModel):
    """Request para crear una clave SSH."""

    name: str = Field(..., min_length=1, max_length=64)
    public_key: str = Field(..., description="Clave pública SSH")
    labels: Optional[Dict[str, str]] = Field(default=None)

    @field_validator("public_key")
    @classmethod
    def validate_public_key(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("La clave pública no puede estar vacía")
        # Validar formato básico de clave SSH
        if not v.startswith(("ssh-", "ecdsa-", "ed25519-")):
            raise ValueError("Formato de clave SSH inválido")
        return v


# =============================================================================
# Response Models
# =============================================================================


class ServerListResponse(BaseModel):
    """Respuesta de lista de servidores."""

    servers: List[Server] = Field(default_factory=list)
    meta: Optional[Meta] = None


class VolumeListResponse(BaseModel):
    """Respuesta de lista de volúmenes."""

    volumes: List[Volume] = Field(default_factory=list)
    meta: Optional[Meta] = None


class NetworkListResponse(BaseModel):
    """Respuesta de lista de redes."""

    networks: List[Network] = Field(default_factory=list)
    meta: Optional[Meta] = None


class FirewallListResponse(BaseModel):
    """Respuesta de lista de firewalls."""

    firewalls: List[Firewall] = Field(default_factory=list)
    meta: Optional[Meta] = None


class LoadBalancerListResponse(BaseModel):
    """Respuesta de lista de load balancers."""

    load_balancers: List[LoadBalancer] = Field(default_factory=list)
    meta: Optional[Meta] = None


class SSHKeyListResponse(BaseModel):
    """Respuesta de lista de claves SSH."""

    ssh_keys: List[SSHKey] = Field(default_factory=list)
    meta: Optional[Meta] = None


class ImageListResponse(BaseModel):
    """Respuesta de lista de imágenes."""

    images: List[Image] = Field(default_factory=list)
    meta: Optional[Meta] = None


class ISOListResponse(BaseModel):
    """Respuesta de lista de ISOs."""

    isos: List[ISO] = Field(default_factory=list)
    meta: Optional[Meta] = None


class ServerTypeListResponse(BaseModel):
    """Respuesta de lista de tipos de servidor."""

    server_types: List[ServerType] = Field(default_factory=list)
    meta: Optional[Meta] = None


class LocationListResponse(BaseModel):
    """Respuesta de lista de localizaciones."""

    locations: List[Location] = Field(default_factory=list)
    meta: Optional[Meta] = None


class DatacenterListResponse(BaseModel):
    """Respuesta de lista de datacenters."""

    datacenters: List[Datacenter] = Field(default_factory=list)
    meta: Optional[Meta] = None


# =============================================================================
# Base Model for Pydantic
# =============================================================================

from pydantic import BaseModel
