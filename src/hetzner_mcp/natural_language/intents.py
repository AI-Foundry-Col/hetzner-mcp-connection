"""
Handlers de Intenciones para Procesamiento de Lenguaje Natural

Cada handler se encarga de procesar intenciones específicas para un tipo de recurso.

Sigue los principios NUPP:
- Open: Handlers abiertos y extensibles
- Minimalist: Lógica simple y enfocada
- Modular: Cada recurso tiene su propio handler
"""

import re
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

from hetzner_mcp.core.client import HetznerClient
from hetzner_mcp.core.models import Server, Volume, Network, Firewall, Action
from hetzner_mcp.core.exceptions import HetznerAPIError


class BaseIntentHandler(ABC):
    """Handler base para intenciones."""

    def __init__(self, client: HetznerClient):
        """
        Inicializar el handler.
        
        Args:
            client: Cliente de Hetzner
        """
        self.client = client

    @abstractmethod
    def handle_create(self, text: str, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Manejar intención de crear."""
        pass

    @abstractmethod
    def handle_list(self, text: str, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Manejar intención de listar."""
        pass

    @abstractmethod
    def handle_delete(self, text: str, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Manejar intención de eliminar."""
        pass

    @abstractmethod
    def handle_update(self, text: str, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Manejar intención de actualizar."""
        pass

    def handle_start(self, text: str, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Manejar intención de iniciar."""
        return {"success": False, "error": "Operación no soportada para este recurso"}

    def handle_stop(self, text: str, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Manejar intención de parar."""
        return {"success": False, "error": "Operación no soportada para este recurso"}

    def handle_reboot(self, text: str, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Manejar intención de reiniciar."""
        return {"success": False, "error": "Operación no soportada para este recurso"}

    def handle_backup(self, text: str, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Manejar intención de backup."""
        return {"success": False, "error": "Operación no soportada para este recurso"}

    def handle_restore(self, text: str, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Manejar intención de restaurar."""
        return {"success": False, "error": "Operación no soportada para este recurso"}

    def handle_attach(self, text: str, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Manejar intención de conectar."""
        return {"success": False, "error": "Operación no soportada para este recurso"}

    def handle_detach(self, text: str, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Manejar intención de desconectar."""
        return {"success": False, "error": "Operación no soportada para este recurso"}

    def handle_configure(self, text: str, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Manejar intención de configurar."""
        return {"success": False, "error": "Operación no soportada para este recurso"}

    def handle_monitor(self, text: str, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Manejar intención de monitorear."""
        return {"success": False, "error": "Operación no soportada para este recurso"}

    def handle_automate(self, text: str, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Manejar intención de automatizar."""
        return {"success": False, "error": "Operación no soportada para este recurso"}

    def handle_search(self, text: str, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Manejar intención de buscar."""
        return self.handle_list(text, params, context)

    def handle_filter(self, text: str, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Manejar intención de filtrar."""
        return self.handle_list(text, params, context)

    def handle_sort(self, text: str, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Manejar intención de ordenar."""
        return self.handle_list(text, params, context)

    def handle_unknown(self, text: str, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Manejar intención desconocida."""
        return {"success": False, "error": f"Intención desconocida: {text}"}

    def _extract_server_id(self, text: str, params: Dict[str, Any]) -> Optional[int]:
        """Extraer ID de servidor del texto o parámetros."""
        # Buscar en parámetros
        if "ids" in params and params["ids"]:
            return params["ids"][0]
        
        # Buscar en texto
        id_match = re.search(r"(?:servidor|server|id|ID|número|num)[:\s]+(\d+)", text)
        if id_match:
            return int(id_match.group(1))
        
        # Buscar nombre de servidor
        name_match = re.search(r"(?:servidor|server|llamado|con nombre|'|\")([a-zA-Z0-9-]+)", text)
        if name_match:
            server = self.client.servers.get_by_name(name_match.group(1))
            if server:
                return server.id
        
        return None

    def _extract_volume_id(self, text: str, params: Dict[str, Any]) -> Optional[int]:
        """Extraer ID de volumen del texto o parámetros."""
        if "ids" in params and params["ids"]:
            return params["ids"][0]
        
        id_match = re.search(r"(?:volumen|volume|id|ID)[:\s]+(\d+)", text)
        if id_match:
            return int(id_match.group(1))
        
        name_match = re.search(r"(?:volumen|volume|llamado|'|\")([a-zA-Z0-9-]+)", text)
        if name_match:
            volumes = self.client.volumes.list(name=name_match.group(1))
            if volumes.volumes:
                return volumes.volumes[0].id
        
        return None


class ServerIntentHandler(BaseIntentHandler):
    """Handler para intenciones de servidores."""

    def handle_create(self, text: str, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Crear un servidor."""
        from hetzner_mcp.core.models import CreateServerRequest
        
        # Valores por defecto
        server_name = params.get("name", "auto-server")
        server_type = params.get("server_type", "cx21")
        location = params.get("location", "nbg1")
        image = params.get("image", "ubuntu-22.04")
        
        # Crear request
        request = CreateServerRequest(
            name=server_name,
            server_type=server_type,
            location=location,
            image=image,
            start_after_create=True,
        )
        
        try:
            server = self.client.servers.create(request)
            return {
                "success": True,
                "action": "create",
                "resource_type": "server",
                "data": server.model_dump(),
                "message": f"Servidor '{server.name}' creado exitosamente con ID {server.id}",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "action": "create",
                "resource_type": "server",
            }

    def handle_list(self, text: str, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Listar servidores."""
        try:
            # Extraer filtros
            name = params.get("name")
            label_selector = params.get("label")
            status = params.get("status")
            
            # Listar servidores
            servers = self.client.servers.list(
                name=name,
                label_selector=label_selector,
                status=status,
            )
            
            return {
                "success": True,
                "action": "list",
                "resource_type": "server",
                "data": [s.model_dump() for s in servers.servers],
                "count": len(servers.servers),
                "message": f"Encontrados {len(servers.servers)} servidores",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "action": "list",
                "resource_type": "server",
            }

    def handle_delete(self, text: str, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Eliminar un servidor."""
        server_id = self._extract_server_id(text, params)
        
        if not server_id:
            return {
                "success": False,
                "error": "No se pudo determinar el ID del servidor a eliminar",
                "action": "delete",
                "resource_type": "server",
            }
        
        try:
            server = self.client.servers.get(server_id)
            self.client.servers.delete(server_id)
            
            return {
                "success": True,
                "action": "delete",
                "resource_type": "server",
                "data": {"id": server_id, "name": server.name},
                "message": f"Servidor '{server.name}' eliminado exitosamente",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "action": "delete",
                "resource_type": "server",
            }

    def handle_update(self, text: str, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Actualizar un servidor."""
        server_id = self._extract_server_id(text, params)
        
        if not server_id:
            return {
                "success": False,
                "error": "No se pudo determinar el ID del servidor a actualizar",
                "action": "update",
                "resource_type": "server",
            }
        
        try:
            from hetzner_mcp.core.models import UpdateServerRequest
            
            # Crear request con los parámetros disponibles
            request_data = {}
            if "name" in params:
                request_data["name"] = params["name"]
            if "labels" in params:
                request_data["labels"] = params["labels"]
            
            request = UpdateServerRequest(**request_data)
            server = self.client.servers.update(server_id, request)
            
            return {
                "success": True,
                "action": "update",
                "resource_type": "server",
                "data": server.model_dump(),
                "message": f"Servidor '{server.name}' actualizado",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "action": "update",
                "resource_type": "server",
            }

    def handle_start(self, text: str, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Iniciar un servidor."""
        server_id = self._extract_server_id(text, params)
        
        if not server_id:
            return {
                "success": False,
                "error": "No se pudo determinar el ID del servidor a iniciar",
                "action": "start",
                "resource_type": "server",
            }
        
        try:
            server = self.client.servers.get(server_id)
            action = self.client.servers.start(server_id)
            
            return {
                "success": True,
                "action": "start",
                "resource_type": "server",
                "data": {
                    "server": server.model_dump(),
                    "action": action.model_dump(),
                },
                "message": f"Servidor '{server.name}' está siendo iniciado",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "action": "start",
                "resource_type": "server",
            }

    def handle_stop(self, text: str, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Parar un servidor."""
        server_id = self._extract_server_id(text, params)
        
        if not server_id:
            return {
                "success": False,
                "error": "No se pudo determinar el ID del servidor a parar",
                "action": "stop",
                "resource_type": "server",
            }
        
        try:
            server = self.client.servers.get(server_id)
            action = self.client.servers.stop(server_id)
            
            return {
                "success": True,
                "action": "stop",
                "resource_type": "server",
                "data": {
                    "server": server.model_dump(),
                    "action": action.model_dump(),
                },
                "message": f"Servidor '{server.name}' está siendo detenido",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "action": "stop",
                "resource_type": "server",
            }

    def handle_reboot(self, text: str, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Reiniciar un servidor."""
        server_id = self._extract_server_id(text, params)
        
        if not server_id:
            return {
                "success": False,
                "error": "No se pudo determinar el ID del servidor a reiniciar",
                "action": "reboot",
                "resource_type": "server",
            }
        
        try:
            server = self.client.servers.get(server_id)
            action = self.client.servers.reboot(server_id)
            
            return {
                "success": True,
                "action": "reboot",
                "resource_type": "server",
                "data": {
                    "server": server.model_dump(),
                    "action": action.model_dump(),
                },
                "message": f"Servidor '{server.name}' está siendo reiniciado",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "action": "reboot",
                "resource_type": "server",
            }

    def handle_backup(self, text: str, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Crear backup de un servidor."""
        server_id = self._extract_server_id(text, params)
        
        if not server_id:
            return {
                "success": False,
                "error": "No se pudo determinar el ID del servidor para backup",
                "action": "backup",
                "resource_type": "server",
            }
        
        try:
            server = self.client.servers.get(server_id)
            action = self.client.servers.create_image(server_id, description="Backup automático")
            
            return {
                "success": True,
                "action": "backup",
                "resource_type": "server",
                "data": {
                    "server": server.model_dump(),
                    "action": action.model_dump(),
                },
                "message": f"Backup creado para servidor '{server.name}'",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "action": "backup",
                "resource_type": "server",
            }

    def handle_monitor(self, text: str, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Obtener estado/métricas de servidores."""
        server_id = self._extract_server_id(text, params)
        
        if server_id:
            # Monitorear servidor específico
            try:
                server = self.client.servers.get(server_id)
                metrics = self.client.servers.get_metrics(server_id, type="cpu")
                
                return {
                    "success": True,
                    "action": "monitor",
                    "resource_type": "server",
                    "data": {
                        "server": server.model_dump(),
                        "metrics": metrics,
                    },
                    "message": f"Métricas para servidor '{server.name}'",
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "action": "monitor",
                    "resource_type": "server",
                }
        else:
            # Monitorear todos los servidores
            try:
                servers = self.client.servers.list_all()
                status_summary = {
                    "total": len(servers),
                    "running": sum(1 for s in servers if s.status == "running"),
                    "stopped": sum(1 for s in servers if s.status == "off"),
                    "other": sum(1 for s in servers if s.status not in ["running", "off"]),
                }
                
                return {
                    "success": True,
                    "action": "monitor",
                    "resource_type": "server",
                    "data": {
                        "summary": status_summary,
                        "servers": [s.model_dump() for s in servers],
                    },
                    "message": f"Resumen: {status_summary['running']} servidores en ejecución, {status_summary['stopped']} detenidos",
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "action": "monitor",
                    "resource_type": "server",
                }


class VolumeIntentHandler(BaseIntentHandler):
    """Handler para intenciones de volúmenes."""

    def handle_create(self, text: str, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Crear un volumen."""
        from hetzner_mcp.core.models import CreateVolumeRequest
        
        volume_name = params.get("name", "auto-volume")
        size = params.get("size", 50)
        location = params.get("location", "nbg1")
        
        request = CreateVolumeRequest(
            name=volume_name,
            size=size,
            location=location,
        )
        
        try:
            volume = self.client.volumes.create(request)
            return {
                "success": True,
                "action": "create",
                "resource_type": "volume",
                "data": volume.model_dump(),
                "message": f"Volumen '{volume.name}' creado con ID {volume.id}",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "action": "create",
                "resource_type": "volume",
            }

    def handle_list(self, text: str, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Listar volúmenes."""
        try:
            name = params.get("name")
            label_selector = params.get("label")
            
            volumes = self.client.volumes.list(
                name=name,
                label_selector=label_selector,
            )
            
            return {
                "success": True,
                "action": "list",
                "resource_type": "volume",
                "data": [v.model_dump() for v in volumes.volumes],
                "count": len(volumes.volumes),
                "message": f"Encontrados {len(volumes.volumes)} volúmenes",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "action": "list",
                "resource_type": "volume",
            }

    def handle_delete(self, text: str, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Eliminar un volumen."""
        volume_id = self._extract_volume_id(text, params)
        
        if not volume_id:
            return {
                "success": False,
                "error": "No se pudo determinar el ID del volumen a eliminar",
                "action": "delete",
                "resource_type": "volume",
            }
        
        try:
            volume = self.client.volumes.get(volume_id)
            self.client.volumes.delete(volume_id)
            
            return {
                "success": True,
                "action": "delete",
                "resource_type": "volume",
                "data": {"id": volume_id, "name": volume.name},
                "message": f"Volumen '{volume.name}' eliminado",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "action": "delete",
                "resource_type": "volume",
            }

    def handle_attach(self, text: str, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Conectar volumen a servidor."""
        volume_id = self._extract_volume_id(text, params)
        server_id = self._extract_server_id(text, params)
        
        if not volume_id or not server_id:
            return {
                "success": False,
                "error": "No se pudo determinar el ID del volumen o servidor",
                "action": "attach",
                "resource_type": "volume",
            }
        
        try:
            volume = self.client.volumes.get(volume_id)
            server = self.client.servers.get(server_id)
            action = self.client.volumes.attach(volume_id, server_id)
            
            return {
                "success": True,
                "action": "attach",
                "resource_type": "volume",
                "data": {
                    "volume": volume.model_dump(),
                    "server": server.model_dump(),
                    "action": action.model_dump(),
                },
                "message": f"Volumen '{volume.name}' conectado a servidor '{server.name}'",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "action": "attach",
                "resource_type": "volume",
            }

    def handle_detach(self, text: str, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Desconectar volumen de servidor."""
        volume_id = self._extract_volume_id(text, params)
        
        if not volume_id:
            return {
                "success": False,
                "error": "No se pudo determinar el ID del volumen",
                "action": "detach",
                "resource_type": "volume",
            }
        
        try:
            volume = self.client.volumes.get(volume_id)
            action = self.client.volumes.detach(volume_id)
            
            return {
                "success": True,
                "action": "detach",
                "resource_type": "volume",
                "data": {
                    "volume": volume.model_dump(),
                    "action": action.model_dump(),
                },
                "message": f"Volumen '{volume.name}' desconectado",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "action": "detach",
                "resource_type": "volume",
            }


class NetworkIntentHandler(BaseIntentHandler):
    """Handler para intenciones de redes."""

    def handle_create(self, text: str, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Crear una red."""
        from hetzner_mcp.core.models import CreateNetworkRequest
        
        network_name = params.get("name", "auto-network")
        ip_range = params.get("ip_range", "10.0.0.0/16")
        
        request = CreateNetworkRequest(
            name=network_name,
            ip_range=ip_range,
        )
        
        try:
            network = self.client.networks.create(request)
            return {
                "success": True,
                "action": "create",
                "resource_type": "network",
                "data": network.model_dump(),
                "message": f"Red '{network.name}' creada con ID {network.id}",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "action": "create",
                "resource_type": "network",
            }

    def handle_list(self, text: str, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Listar redes."""
        try:
            name = params.get("name")
            label_selector = params.get("label")
            
            networks = self.client.networks.list(
                name=name,
                label_selector=label_selector,
            )
            
            return {
                "success": True,
                "action": "list",
                "resource_type": "network",
                "data": [n.model_dump() for n in networks.networks],
                "count": len(networks.networks),
                "message": f"Encontradas {len(networks.networks)} redes",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "action": "list",
                "resource_type": "network",
            }

    def handle_delete(self, text: str, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Eliminar una red."""
        network_id = self._extract_network_id(text, params)
        
        if not network_id:
            return {
                "success": False,
                "error": "No se pudo determinar el ID de la red",
                "action": "delete",
                "resource_type": "network",
            }
        
        try:
            network = self.client.networks.get(network_id)
            self.client.networks.delete(network_id)
            
            return {
                "success": True,
                "action": "delete",
                "resource_type": "network",
                "data": {"id": network_id, "name": network.name},
                "message": f"Red '{network.name}' eliminada",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "action": "delete",
                "resource_type": "network",
            }

    def _extract_network_id(self, text: str, params: Dict[str, Any]) -> Optional[int]:
        """Extraer ID de red del texto o parámetros."""
        if "ids" in params and params["ids"]:
            return params["ids"][0]
        
        id_match = re.search(r"(?:red|network|id|ID)[:\s]+(\d+)", text)
        if id_match:
            return int(id_match.group(1))
        
        name_match = re.search(r"(?:red|network|llamado|'|\")([a-zA-Z0-9-]+)", text)
        if name_match:
            networks = self.client.networks.list(name=name_match.group(1))
            if networks.networks:
                return networks.networks[0].id
        
        return None


class FirewallIntentHandler(BaseIntentHandler):
    """Handler para intenciones de firewalls."""

    def handle_create(self, text: str, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Crear un firewall."""
        from hetzner_mcp.core.models import CreateFirewallRequest, FirewallRule
        
        firewall_name = params.get("name", "auto-firewall")
        
        # Crear regla por defecto (aceptar todo)
        rules = [
            {
                "direction": "in",
                "protocol": "tcp",
                "port": "80",
                "action": "ACCEPT",
                "description": "HTTP",
            },
            {
                "direction": "in",
                "protocol": "tcp",
                "port": "443",
                "action": "ACCEPT",
                "description": "HTTPS",
            },
            {
                "direction": "in",
                "protocol": "tcp",
                "port": "22",
                "action": "ACCEPT",
                "description": "SSH",
            },
        ]
        
        request = CreateFirewallRequest(
            name=firewall_name,
            rules=rules,
        )
        
        try:
            firewall = self.client.firewalls.create(request)
            return {
                "success": True,
                "action": "create",
                "resource_type": "firewall",
                "data": firewall.model_dump(),
                "message": f"Firewall '{firewall.name}' creado con ID {firewall.id}",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "action": "create",
                "resource_type": "firewall",
            }

    def handle_list(self, text: str, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Listar firewalls."""
        try:
            name = params.get("name")
            label_selector = params.get("label")
            
            firewalls = self.client.firewalls.list(
                name=name,
                label_selector=label_selector,
            )
            
            return {
                "success": True,
                "action": "list",
                "resource_type": "firewall",
                "data": [f.model_dump() for f in firewalls.firewalls],
                "count": len(firewalls.firewalls),
                "message": f"Encontrados {len(firewalls.firewalls)} firewalls",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "action": "list",
                "resource_type": "firewall",
            }

    def handle_configure(self, text: str, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Configurar reglas de firewall."""
        firewall_id = self._extract_firewall_id(text, params)
        
        if not firewall_id:
            return {
                "success": False,
                "error": "No se pudo determinar el ID del firewall",
                "action": "configure",
                "resource_type": "firewall",
            }
        
        # Extraer reglas del texto
        rules = self._extract_firewall_rules(text)
        
        try:
            action = self.client.firewalls.set_rules(firewall_id, rules)
            
            return {
                "success": True,
                "action": "configure",
                "resource_type": "firewall",
                "data": {
                    "firewall_id": firewall_id,
                    "rules": rules,
                    "action": action.model_dump(),
                },
                "message": f"Reglas de firewall actualizadas",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "action": "configure",
                "resource_type": "firewall",
            }

    def _extract_firewall_id(self, text: str, params: Dict[str, Any]) -> Optional[int]:
        """Extraer ID de firewall del texto o parámetros."""
        if "ids" in params and params["ids"]:
            return params["ids"][0]
        
        id_match = re.search(r"(?:firewall|cortafuegos|id|ID)[:\s]+(\d+)", text)
        if id_match:
            return int(id_match.group(1))
        
        name_match = re.search(r"(?:firewall|cortafuegos|llamado|'|\")([a-zA-Z0-9-]+)", text)
        if name_match:
            firewalls = self.client.firewalls.list(name=name_match.group(1))
            if firewalls.firewalls:
                return firewalls.firewalls[0].id
        
        return None

    def _extract_firewall_rules(self, text: str) -> List[Dict[str, Any]]:
        """Extraer reglas de firewall del texto."""
        rules = []
        
        # Buscar patrones de reglas
        # Ejemplo: "permitir puerto 80 tcp", "bloquear puerto 22", etc.
        rule_patterns = [
            (r"(?:permitir|aceptar|allow)[:\s]+puerto[:\s]+(\d+)\s*(?:tcp|udp)?", "ACCEPT"),
            (r"(?:bloquear|denegar|drop)[:\s]+puerto[:\s]+(\d+)\s*(?:tcp|udp)?", "DROP"),
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
        
        return rules if rules else [
            {
                "direction": "in",
                "protocol": "tcp",
                "port": "22",
                "action": "ACCEPT",
            }
        ]


class BackupIntentHandler(BaseIntentHandler):
    """Handler para intenciones de backup."""

    def handle_create(self, text: str, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Crear backup."""
        server_id = self._extract_server_id(text, params)
        
        if not server_id:
            return {
                "success": False,
                "error": "No se pudo determinar el ID del servidor para backup",
                "action": "create",
                "resource_type": "backup",
            }
        
        try:
            server = self.client.servers.get(server_id)
            action = self.client.servers.create_image(server_id, description="Backup manual")
            
            return {
                "success": True,
                "action": "create",
                "resource_type": "backup",
                "data": {
                    "server": server.model_dump(),
                    "action": action.model_dump(),
                },
                "message": f"Backup creado para servidor '{server.name}'",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "action": "create",
                "resource_type": "backup",
            }

    def handle_list(self, text: str, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Listar backups."""
        try:
            images = self.client.images.list(type="snapshot")
            
            return {
                "success": True,
                "action": "list",
                "resource_type": "backup",
                "data": [i.model_dump() for i in images.images],
                "count": len(images.images),
                "message": f"Encontrados {len(images.images)} backups",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "action": "list",
                "resource_type": "backup",
            }

    def handle_restore(self, text: str, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Restaurar desde backup."""
        # Extraer ID de imagen (backup)
        image_id = self._extract_image_id(text, params)
        server_id = self._extract_server_id(text, params)
        
        if not image_id or not server_id:
            return {
                "success": False,
                "error": "No se pudo determinar el ID de la imagen o servidor",
                "action": "restore",
                "resource_type": "backup",
            }
        
        try:
            server = self.client.servers.get(server_id)
            action = self.client.servers.rebuild(server_id, image=image_id)
            
            return {
                "success": True,
                "action": "restore",
                "resource_type": "backup",
                "data": {
                    "server": server.model_dump(),
                    "image_id": image_id,
                    "action": action.model_dump(),
                },
                "message": f"Servidor '{server.name}' está siendo restaurado desde backup",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "action": "restore",
                "resource_type": "backup",
            }

    def _extract_image_id(self, text: str, params: Dict[str, Any]) -> Optional[int]:
        """Extraer ID de imagen del texto o parámetros."""
        if "ids" in params and params["ids"]:
            return params["ids"][0]
        
        id_match = re.search(r"(?:imagen|image|backup|id|ID)[:\s]+(\d+)", text)
        if id_match:
            return int(id_match.group(1))
        
        return None


class MonitoringIntentHandler(BaseIntentHandler):
    """Handler para intenciones de monitoreo."""

    def handle_list(self, text: str, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Obtener estado de todos los recursos."""
        return self.handle_monitor(text, params, context)

    def handle_monitor(self, text: str, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Monitorear recursos."""
        # Determinar qué monitorear
        resource_type = "server"  # Por defecto
        
        if "volumen" in text or "volume" in text:
            resource_type = "volume"
        elif "red" in text or "network" in text:
            resource_type = "network"
        
        try:
            if resource_type == "server":
                servers = self.client.servers.list_all()
                status_summary = {
                    "total": len(servers),
                    "running": sum(1 for s in servers if s.status == "running"),
                    "stopped": sum(1 for s in servers if s.status == "off"),
                    "other": sum(1 for s in servers if s.status not in ["running", "off"]),
                }
                
                return {
                    "success": True,
                    "action": "monitor",
                    "resource_type": "server",
                    "data": {
                        "summary": status_summary,
                        "servers": [s.model_dump() for s in servers],
                    },
                    "message": f"Monitoreo: {status_summary['running']} servidores en ejecución",
                }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "action": "monitor",
                "resource_type": resource_type,
            }


class AutomationIntentHandler(BaseIntentHandler):
    """Handler para intenciones de automatización."""

    def handle_automate(self, text: str, params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Automatizar tareas."""
        # Analizar el tipo de automatización
        if "backup" in text or "copia" in text:
            return self._automate_backup(text, params)
        elif "escalar" in text or "scale" in text:
            return self._automate_scale(text, params)
        elif "desplegar" in text or "deploy" in text:
            return self._automate_deploy(text, params)
        else:
            return {
                "success": False,
                "error": "Tipo de automatización no reconocido",
                "action": "automate",
                "resource_type": "automation",
            }

    def _automate_backup(self, text: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Automatizar backups."""
        try:
            # Obtener todos los servidores
            servers = self.client.servers.list_all()
            
            # Crear backup para cada servidor
            results = []
            for server in servers:
                action = self.client.servers.create_image(
                    server.id,
                    description="Backup automático"
                )
                results.append({
                    "server_id": server.id,
                    "server_name": server.name,
                    "action_id": action.id,
                })
            
            return {
                "success": True,
                "action": "automate",
                "resource_type": "backup",
                "data": {
                    "servers": len(servers),
                    "backups_created": len(results),
                    "results": results,
                },
                "message": f"Backups creados para {len(servers)} servidores",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "action": "automate",
                "resource_type": "backup",
            }

    def _automate_scale(self, text: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Automatizar escalado."""
        # Extraer parámetros de escalado
        count = params.get("count", 1)
        server_type = params.get("server_type", "cx21")
        
        try:
            from hetzner_mcp.core.models import CreateServerRequest
            
            # Crear múltiples servidores
            results = []
            for i in range(count):
                request = CreateServerRequest(
                    name=f"auto-scale-{i+1}",
                    server_type=server_type,
                    location="nbg1",
                    image="ubuntu-22.04",
                )
                server = self.client.servers.create(request)
                results.append(server.model_dump())
            
            return {
                "success": True,
                "action": "automate",
                "resource_type": "scale",
                "data": {
                    "servers_created": len(results),
                    "servers": results,
                },
                "message": f"Escalado: {len(results)} servidores creados",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "action": "automate",
                "resource_type": "scale",
            }

    def _automate_deploy(self, text: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Automatizar despliegue."""
        try:
            from hetzner_mcp.core.models import CreateServerRequest
            
            # Crear servidor con configuración estándar
            request = CreateServerRequest(
                name="auto-deploy",
                server_type="cx21",
                location="nbg1",
                image="ubuntu-22.04",
            )
            
            server = self.client.servers.create(request)
            
            return {
                "success": True,
                "action": "automate",
                "resource_type": "deploy",
                "data": server.model_dump(),
                "message": f"Servidor '{server.name}' desplegado",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "action": "automate",
                "resource_type": "deploy",
            }
