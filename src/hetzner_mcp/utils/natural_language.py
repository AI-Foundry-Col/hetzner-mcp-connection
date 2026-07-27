"""
Utilidades para Procesamiento de Lenguaje Natural

Este módulo contiene funciones utilitarias para extraer información
de comandos en lenguaje natural.
"""

import re
from typing import Any, Dict, List, Optional, Tuple


def extract_server_specs(text: str) -> Dict[str, Any]:
    """
    Extraer especificaciones de servidor del texto.
    
    Args:
        text: Texto a analizar
        
    Returns:
        Dict con especificaciones de servidor
    """
    specs = {}
    
    # Extraer nombre
    name_match = re.search(r"(?:nombre|llamado|con nombre|'|\")([a-zA-Z0-9-]+)(?:'|\"|\s|$)", text)
    if name_match:
        specs["name"] = name_match.group(1)
    
    # Extraer tipo de servidor
    type_match = re.search(r"(?:tipo|modelo|plan|servidor)[:\s]+([a-zA-Z0-9-]+)", text)
    if type_match:
        specs["server_type"] = type_match.group(1)
    
    # Extraer ubicación
    location_match = re.search(r"(?:en|ubicación|localización|datacenter|dc)[:\s]+([a-zA-Z0-9-]+)", text)
    if location_match:
        specs["location"] = location_match.group(1)
    
    # Extraer imagen
    image_match = re.search(r"(?:imagen|sistema operativo|os|SO)[:\s]+([a-zA-Z0-9-.]+)", text)
    if image_match:
        specs["image"] = image_match.group(1)
    
    # Extraer tamaño de disco (si aplica)
    disk_match = re.search(r"(?:disco|almacenamiento|storage)[:\s]+(\d+)\s*(?:GB|gb|gigas)", text)
    if disk_match:
        specs["disk_size"] = int(disk_match.group(1))
    
    # Extraer RAM (si aplica)
    ram_match = re.search(r"(?:ram|memoria)[:\s]+(\d+)\s*(?:GB|gb|gigas)", text)
    if ram_match:
        specs["memory"] = int(ram_match.group(1))
    
    # Extraer CPU (si aplica)
    cpu_match = re.search(r"(?:cpu|cores|núcleos)[:\s]+(\d+)", text)
    if cpu_match:
        specs["cores"] = int(cpu_match.group(1))
    
    return specs


def extract_volume_specs(text: str) -> Dict[str, Any]:
    """
    Extraer especificaciones de volumen del texto.
    
    Args:
        text: Texto a analizar
        
    Returns:
        Dict con especificaciones de volumen
    """
    specs = {}
    
    # Extraer nombre
    name_match = re.search(r"(?:nombre|llamado|con nombre|'|\")([a-zA-Z0-9-]+)(?:'|\"|\s|$)", text)
    if name_match:
        specs["name"] = name_match.group(1)
    
    # Extraer tamaño
    size_match = re.search(r"(?:tamaño|size|GB|gb|gigas)[:\s]+(\d+)", text)
    if size_match:
        specs["size"] = int(size_match.group(1))
    
    # Extraer ubicación
    location_match = re.search(r"(?:en|ubicación|localización|datacenter|dc)[:\s]+([a-zA-Z0-9-]+)", text)
    if location_match:
        specs["location"] = location_match.group(1)
    
    return specs


def extract_network_specs(text: str) -> Dict[str, Any]:
    """
    Extraer especificaciones de red del texto.
    
    Args:
        text: Texto a analizar
        
    Returns:
        Dict con especificaciones de red
    """
    specs = {}
    
    # Extraer nombre
    name_match = re.search(r"(?:nombre|llamado|con nombre|'|\")([a-zA-Z0-9-]+)(?:'|\"|\s|$)", text)
    if name_match:
        specs["name"] = name_match.group(1)
    
    # Extraer rango IP
    ip_range_match = re.search(r"(?:rango ip|ip range|red)[:\s]+([\d.]+/\d+)", text)
    if ip_range_match:
        specs["ip_range"] = ip_range_match.group(1)
    
    return specs


def extract_firewall_specs(text: str) -> Dict[str, Any]:
    """
    Extraer especificaciones de firewall del texto.
    
    Args:
        text: Texto a analizar
        
    Returns:
        Dict con especificaciones de firewall
    """
    specs = {}
    
    # Extraer nombre
    name_match = re.search(r"(?:nombre|llamado|con nombre|'|\")([a-zA-Z0-9-]+)(?:'|\"|\s|$)", text)
    if name_match:
        specs["name"] = name_match.group(1)
    
    # Extraer reglas
    rules = []
    
    # Buscar patrones de reglas
    rule_patterns = [
        (r"(?:permitir|aceptar|allow)[:\s]+puerto[:\s]+(\d+)", "ACCEPT"),
        (r"(?:bloquear|denegar|drop)[:\s]+puerto[:\s]+(\d+)", "DROP"),
        (r"(?:abrir|open)[:\s]+puerto[:\s]+(\d+)", "ACCEPT"),
        (r"(?:cerrar|close)[:\s]+puerto[:\s]+(\d+)", "DROP"),
    ]
    
    for pattern, action in rule_patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            port = match.group(1)
            rules.append({
                "direction": "in",
                "protocol": "tcp",
                "port": port,
                "action": action,
            })
    
    if rules:
        specs["rules"] = rules
    
    return specs


def extract_action_specs(text: str) -> Dict[str, Any]:
    """
    Extraer especificaciones de acción del texto.
    
    Args:
        text: Texto a analizar
        
    Returns:
        Dict con especificaciones de acción
    """
    specs = {}
    
    # Extraer IDs de recursos
    id_matches = re.findall(r"(?:id|ID|número|num)[:\s]+(\d+)", text)
    if id_matches:
        specs["ids"] = [int(id) for id in id_matches]
    
    # Extraer nombres de recursos
    name_matches = re.findall(r"(?:servidor|volumen|red|firewall)[:\s]+(['\"]?)([a-zA-Z0-9-]+)\1", text)
    if name_matches:
        specs["names"] = [name for _, name in name_matches]
    
    # Extraer tiempo/duración
    time_match = re.search(r"(?:durante|por|duración|timeout)[:\s]+(\d+)\s*(?:segundos|seg|s|minutos|min|m|horas|h|días|d)", text)
    if time_match:
        specs["time"] = int(time_match.group(1))
    
    return specs


def extract_filter_specs(text: str) -> Dict[str, Any]:
    """
    Extraer especificaciones de filtro del texto.
    
    Args:
        text: Texto a analizar
        
    Returns:
        Dict con especificaciones de filtro
    """
    specs = {}
    
    # Extraer estado
    status_match = re.search(r"(?:estado|status)[:\s]+([a-zA-Z]+)", text)
    if status_match:
        specs["status"] = status_match.group(1)
    
    # Extraer etiqueta
    label_match = re.search(r"(?:etiqueta|label|tag)[:\s]+([a-zA-Z0-9-]+)", text)
    if label_match:
        specs["label"] = label_match.group(1)
    
    # Extraer nombre
    name_match = re.search(r"(?:nombre|name)[:\s]+([a-zA-Z0-9-]+)", text)
    if name_match:
        specs["name"] = name_match.group(1)
    
    return specs


def parse_natural_command(command: str) -> Dict[str, Any]:
    """
    Parsear un comando en lenguaje natural.
    
    Args:
        command: Comando en español
        
    Returns:
        Dict con el comando parseado
    """
    import unicodedata
    
    # Normalizar el texto
    normalized = command.lower()
    normalized = unicodedata.normalize('NFD', normalized)
    normalized = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
    
    # Determinar tipo de recurso
    resource_type = "server"  # Por defecto
    
    if any(word in normalized for word in ["volumen", "volume", "disco", "storage"]):
        resource_type = "volume"
    elif any(word in normalized for word in ["red", "network", "subred"]):
        resource_type = "network"
    elif any(word in normalized for word in ["firewall", "cortafuegos"]):
        resource_type = "firewall"
    elif any(word in normalized for word in ["backup", "copia", "respaldo"]):
        resource_type = "backup"
    elif any(word in normalized for word in ["ip", "direccion"]):
        resource_type = "ip"
    
    # Determinar acción
    action = "list"  # Por defecto
    
    if any(word in normalized for word in ["crear", "nuevo", "construir", "desplegar"]):
        action = "create"
    elif any(word in normalized for word in ["eliminar", "borrar", "remover", "quitar"]):
        action = "delete"
    elif any(word in normalized for word in ["actualizar", "modificar", "cambiar", "editar"]):
        action = "update"
    elif any(word in normalized for word in ["iniciar", "encender", "arrancar", "start"]):
        action = "start"
    elif any(word in normalized for word in ["parar", "detener", "apagar", "stop"]):
        action = "stop"
    elif any(word in normalized for word in ["reiniciar", "rebootear", "reboot"]):
        action = "reboot"
    elif any(word in normalized for word in ["backup", "copia", "respaldo"]):
        action = "backup"
    elif any(word in normalized for word in ["restaurar", "recuperar", "restore"]):
        action = "restore"
    elif any(word in normalized for word in ["conectar", "adjuntar", "attach"]):
        action = "attach"
    elif any(word in normalized for word in ["desconectar", "desadjuntar", "detach"]):
        action = "detach"
    
    # Extraer especificaciones según el tipo de recurso
    specs = {}
    
    if resource_type == "server":
        specs = extract_server_specs(normalized)
    elif resource_type == "volume":
        specs = extract_volume_specs(normalized)
    elif resource_type == "network":
        specs = extract_network_specs(normalized)
    elif resource_type == "firewall":
        specs = extract_firewall_specs(normalized)
    
    # Extraer filtros
    filters = extract_filter_specs(normalized)
    specs.update(filters)
    
    # Extraer IDs y nombres
    action_specs = extract_action_specs(normalized)
    specs.update(action_specs)
    
    return {
        "action": action,
        "resource_type": resource_type,
        "specs": specs,
        "original": command,
        "normalized": normalized,
    }
