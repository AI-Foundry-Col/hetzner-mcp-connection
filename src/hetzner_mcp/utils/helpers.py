"""
Funciones utilitarias para Hetzner MCP Connection

Sigue los principios NUPP:
- Open: Funciones abiertas y reutilizables
- Minimalist: Implementaciones simples y eficientes
- Modular: Cada función tiene un propósito claro
"""

import re
import time
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union

from hetzner_mcp.core.client import HetznerClient
from hetzner_mcp.core.exceptions import HetznerAPIError

T = TypeVar("T")


def validate_server_name(name: str) -> bool:
    """
    Validar nombre de servidor.
    
    Args:
        name: Nombre a validar
        
    Returns:
        bool: True si el nombre es válido
    """
    if not name:
        return False
    
    if len(name) < 1 or len(name) > 64:
        return False
    
    # Solo letras, números y guiones
    if not re.match(r"^[a-zA-Z0-9-]+$", name):
        return False
    
    # No puede empezar o terminar con guión
    if name.startswith("-") or name.endswith("-"):
        return False
    
    return True


def validate_ip_address(ip: str) -> bool:
    """
    Validar dirección IP (IPv4 o IPv6).
    
    Args:
        ip: Dirección IP a validar
        
    Returns:
        bool: True si la IP es válida
    """
    # Validar IPv4
    ipv4_pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
    if re.match(ipv4_pattern, ip):
        parts = ip.split(".")
        for part in parts:
            if not 0 <= int(part) <= 255:
                return False
        return True
    
    # Validar IPv6 (simplificado)
    ipv6_pattern = r"^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$"
    if re.match(ipv6_pattern, ip):
        return True
    
    # IPv6 comprimida
    ipv6_compressed_pattern = r"^(([0-9a-fA-F]{1,4}(:[0-9a-fA-F]{1,4})*)?)::(([0-9a-fA-F]{1,4}(:[0-9a-fA-F]{1,4})*)?)$"
    if re.match(ipv6_compressed_pattern, ip):
        return True
    
    return False


def validate_cidr(cidr: str) -> bool:
    """
    Validar notación CIDR.
    
    Args:
        cidr: Notación CIDR a validar
        
    Returns:
        bool: True si el CIDR es válido
    """
    if not cidr:
        return False
    
    # Separar IP y prefijo
    parts = cidr.split("/")
    if len(parts) != 2:
        return False
    
    ip, prefix = parts
    
    # Validar IP
    if not validate_ip_address(ip):
        return False
    
    # Validar prefijo
    try:
        prefix_int = int(prefix)
        if ip.count(":") > 0:  # IPv6
            if prefix_int < 0 or prefix_int > 128:
                return False
        else:  # IPv4
            if prefix_int < 0 or prefix_int > 32:
                return False
    except ValueError:
        return False
    
    return True


def parse_size(size: Union[str, int, float]) -> int:
    """
    Parsear tamaño a GB.
    
    Args:
        size: Tamaño (puede ser "10GB", "10 GB", "10", 10)
        
    Returns:
        int: Tamaño en GB
    """
    if isinstance(size, (int, float)):
        return int(size)
    
    if isinstance(size, str):
        size = size.strip().upper()
        
        # Remover unidades
        if size.endswith("GB"):
            size = size[:-2]
        elif size.endswith("G"):
            size = size[:-1]
        elif size.endswith("MB"):
            size = str(int(float(size[:-2]) / 1024))
        elif size.endswith("M"):
            size = str(int(float(size[:-1]) / 1024))
        elif size.endswith("TB"):
            size = str(int(float(size[:-2]) * 1024))
        elif size.endswith("T"):
            size = str(int(float(size[:-1]) * 1024))
        
        try:
            return int(float(size))
        except ValueError:
            raise ValueError(f"Formato de tamaño inválido: {size}")
    
    raise ValueError(f"Tipo de tamaño no soportado: {type(size)}")


def format_size(size_gb: Union[int, float]) -> str:
    """
    Formatear tamaño en formato legible.
    
    Args:
        size_gb: Tamaño en GB
        
    Returns:
        str: Tamaño formateado
    """
    size = float(size_gb)
    
    if size >= 1024:
        return f"{size / 1024:.2f} TB"
    elif size >= 1:
        return f"{size:.2f} GB"
    elif size >= 0.001:
        return f"{size * 1024:.2f} MB"
    else:
        return f"{size * 1024 * 1024:.2f} KB"


def wait_for_action(
    client: HetznerClient,
    action_id: int,
    timeout: int = 300,
    poll_interval: float = 1.0,
) -> Any:
    """
    Esperar a que una acción se complete.
    
    Args:
        client: Cliente de Hetzner
        action_id: ID de la acción
        timeout: Timeout en segundos
        poll_interval: Intervalo de polling en segundos
        
    Returns:
        Action: Acción completada
    """
    start_time = time.time()
    
    while True:
        action = client.actions.get(action_id)
        
        if action.is_completed:
            return action
        
        if time.time() - start_time > timeout:
            raise HetznerAPIError(
                f"Timeout esperando la acción {action_id}",
                status_code=408,
                error_code="timeout",
            )
        
        time.sleep(poll_interval)


def get_resource_by_name_or_id(
    client: HetznerClient,
    resource_type: str,
    identifier: Union[str, int],
) -> Any:
    """
    Obtener un recurso por nombre o ID.
    
    Args:
        client: Cliente de Hetzner
        resource_type: Tipo de recurso (server, volume, network, firewall)
        identifier: Nombre o ID del recurso
        
    Returns:
        Recurso encontrado
    """
    if isinstance(identifier, int):
        # Es un ID
        if resource_type == "server":
            return client.servers.get(identifier)
        elif resource_type == "volume":
            return client.volumes.get(identifier)
        elif resource_type == "network":
            return client.networks.get(identifier)
        elif resource_type == "firewall":
            return client.firewalls.get(identifier)
        else:
            raise ValueError(f"Tipo de recurso no soportado: {resource_type}")
    
    # Es un nombre
    if resource_type == "server":
        server = client.servers.get_by_name(str(identifier))
        if server:
            return server
    elif resource_type == "volume":
        volume = client.volumes.get_by_name(str(identifier))
        if volume:
            return volume
    elif resource_type == "network":
        network = client.networks.get_by_name(str(identifier))
        if network:
            return network
    elif resource_type == "firewall":
        firewall = client.firewalls.get_by_name(str(identifier))
        if firewall:
            return firewall
    
    raise ValueError(f"Recurso {identifier} no encontrado")


def batch_operation(
    client: HetznerClient,
    resource_type: str,
    operation: str,
    identifiers: List[Union[str, int]],
    **kwargs
) -> Dict[str, Any]:
    """
    Ejecutar una operación en batch sobre múltiples recursos.
    
    Args:
        client: Cliente de Hetzner
        resource_type: Tipo de recurso
        operation: Operación a ejecutar
        identifiers: Lista de identificadores de recursos
        **kwargs: Argumentos adicionales para la operación
        
    Returns:
        Dict con resultados de la operación
    """
    results = {
        "success": [],
        "failed": [],
    }
    
    for identifier in identifiers:
        try:
            resource = get_resource_by_name_or_id(client, resource_type, identifier)
            
            if operation == "start" and resource_type == "server":
                action = client.servers.start(resource.id)
                results["success"].append({
                    "id": resource.id,
                    "name": getattr(resource, "name", str(resource.id)),
                    "action_id": action.id,
                })
            elif operation == "stop" and resource_type == "server":
                action = client.servers.stop(resource.id)
                results["success"].append({
                    "id": resource.id,
                    "name": getattr(resource, "name", str(resource.id)),
                    "action_id": action.id,
                })
            elif operation == "reboot" and resource_type == "server":
                action = client.servers.reboot(resource.id)
                results["success"].append({
                    "id": resource.id,
                    "name": getattr(resource, "name", str(resource.id)),
                    "action_id": action.id,
                })
            elif operation == "delete" and resource_type == "server":
                client.servers.delete(resource.id)
                results["success"].append({
                    "id": resource.id,
                    "name": getattr(resource, "name", str(resource.id)),
                })
            elif operation == "backup" and resource_type == "server":
                action = client.servers.create_image(resource.id, description="Backup batch")
                results["success"].append({
                    "id": resource.id,
                    "name": getattr(resource, "name", str(resource.id)),
                    "action_id": action.id,
                })
            else:
                results["failed"].append({
                    "id": identifier,
                    "error": f"Operación no soportada: {operation} en {resource_type}",
                })
                
        except Exception as e:
            results["failed"].append({
                "id": identifier,
                "error": str(e),
            })
    
    return results
