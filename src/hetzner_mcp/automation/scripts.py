"""
Scripts de Automatización para Hetzner Cloud

Sigue los principios NUPP:
- Open: Scripts abiertos y personalizables
- Minimalist: Lógica simple y efectiva
- Modular: Cada script es independiente
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from hetzner_mcp.core.client import HetznerClient
from hetzner_mcp.core.models import Server, Volume, Action

logger = logging.getLogger(__name__)


class AutomationScript:
    """Script base para automatización."""

    def __init__(self, client: HetznerClient):
        """
        Inicializar el script.
        
        Args:
            client: Cliente de Hetzner
        """
        self.client = client
        self.results = []
        self.errors = []

    def run(self, **kwargs) -> Dict[str, Any]:
        """Ejecutar el script."""
        self.results = []
        self.errors = []
        
        try:
            result = self._execute(**kwargs)
            return {
                "success": True,
                "results": self.results,
                "errors": self.errors,
                "data": result,
            }
        except Exception as e:
            self.errors.append(str(e))
            return {
                "success": False,
                "results": self.results,
                "errors": self.errors,
                "error": str(e),
            }

    def _execute(self, **kwargs) -> Any:
        """Método a implementar por cada script."""
        raise NotImplementedError("Debe implementar el método _execute")

    def _log_result(self, message: str, data: Any = None) -> None:
        """Registrar un resultado."""
        result = {
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "data": data,
        }
        self.results.append(result)
        logger.info(message)

    def _log_error(self, message: str, error: Any = None) -> None:
        """Registrar un error."""
        error_info = {
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "error": str(error) if error else None,
        }
        self.errors.append(error_info)
        logger.error(message)


class BackupScript(AutomationScript):
    """Script para crear backups de servidores."""

    def _execute(
        self,
        server_ids: Optional[List[int]] = None,
        all_servers: bool = False,
        wait: bool = False,
        timeout: int = 300,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Ejecutar backup de servidores.
        
        Args:
            server_ids: Lista de IDs de servidores específicos
            all_servers: Si se debe hacer backup de todos los servidores
            wait: Si se debe esperar a que las acciones completen
            timeout: Timeout en segundos para esperar acciones
            
        Returns:
            Dict con información de los backups creados
        """
        backup_results = []
        
        # Obtener servidores a respaldar
        if all_servers:
            servers = self.client.servers.list_all()
        elif server_ids:
            servers = [self.client.servers.get(sid) for sid in server_ids]
        else:
            raise ValueError("Debe especificar server_ids o all_servers=True")
        
        self._log_result(f"Iniciando backup de {len(servers)} servidores")
        
        # Crear backup para cada servidor
        for server in servers:
            try:
                self._log_result(f"Creando backup para servidor {server.name} (ID: {server.id})")
                
                action = self.client.servers.create_image(
                    server.id,
                    description=f"Backup automático - {datetime.now().isoformat()}"
                )
                
                # Esperar a que la acción complete (opcional)
                if wait:
                    final_action = self.client.actions.wait_for_completion(
                        action.id,
                        timeout=timeout
                    )
                    action = final_action
                
                backup_results.append({
                    "server_id": server.id,
                    "server_name": server.name,
                    "action_id": action.id,
                    "status": action.status,
                    "timestamp": datetime.now().isoformat(),
                })
                
                self._log_result(f"Backup creado para {server.name}", {"action_id": action.id})
                
            except Exception as e:
                self._log_error(f"Error creando backup para {server.name}", e)
                backup_results.append({
                    "server_id": server.id,
                    "server_name": server.name,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                })
        
        return {
            "total_servers": len(servers),
            "successful": len([r for r in backup_results if "error" not in r]),
            "failed": len([r for r in backup_results if "error" in r]),
            "backups": backup_results,
        }


class ScaleScript(AutomationScript):
    """Script para escalar servidores."""

    def _execute(
        self,
        count: int = 1,
        server_type: str = "cx21",
        location: str = "nbg1",
        image: str = "ubuntu-22.04",
        prefix: str = "scale-",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Ejecutar escalado de servidores.
        
        Args:
            count: Número de servidores a crear
            server_type: Tipo de servidor
            location: Localización
            image: Imagen
            prefix: Prefijo para nombres de servidores
            
        Returns:
            Dict con información de los servidores creados
        """
        from hetzner_mcp.core.models import CreateServerRequest
        
        created_servers = []
        
        self._log_result(f"Creando {count} servidores de tipo {server_type}")
        
        for i in range(count):
            try:
                server_name = f"{prefix}{i+1}-{datetime.now().strftime('%Y%m%d')}"
                
                request = CreateServerRequest(
                    name=server_name,
                    server_type=server_type,
                    location=location,
                    image=image,
                    start_after_create=True,
                )
                
                server = self.client.servers.create(request)
                created_servers.append(server.model_dump())
                
                self._log_result(f"Servidor {server.name} creado", {"id": server.id})
                
            except Exception as e:
                self._log_error(f"Error creando servidor {i+1}", e)
        
        return {
            "requested": count,
            "created": len(created_servers),
            "servers": created_servers,
        }


class DeployScript(AutomationScript):
    """Script para despliegue de aplicaciones."""

    def _execute(
        self,
        config: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Ejecutar despliegue.
        
        Args:
            config: Configuración de despliegue
            
        Returns:
            Dict con información del despliegue
        """
        from hetzner_mcp.core.models import CreateServerRequest
        
        if not config:
            # Configuración por defecto
            config = {
                "server": {
                    "name": f"deploy-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                    "type": "cx21",
                    "location": "nbg1",
                    "image": "ubuntu-22.04",
                },
                "volume": {
                    "create": True,
                    "size": 50,
                },
                "firewall": {
                    "create": True,
                    "rules": [
                        {"direction": "in", "protocol": "tcp", "port": "80", "action": "ACCEPT"},
                        {"direction": "in", "protocol": "tcp", "port": "443", "action": "ACCEPT"},
                        {"direction": "in", "protocol": "tcp", "port": "22", "action": "ACCEPT"},
                    ],
                },
            }
        
        self._log_result("Iniciando despliegue")
        
        # Crear servidor
        server_config = config.get("server", {})
        server_request = CreateServerRequest(
            name=server_config.get("name", f"deploy-{datetime.now().strftime('%Y%m%d')}"),
            server_type=server_config.get("type", "cx21"),
            location=server_config.get("location", "nbg1"),
            image=server_config.get("image", "ubuntu-22.04"),
        )
        
        server = self.client.servers.create(server_request)
        self._log_result(f"Servidor {server.name} creado", {"id": server.id})
        
        # Crear volumen si está configurado
        volume_config = config.get("volume", {})
        volume = None
        if volume_config.get("create", False):
            from hetzner_mcp.core.models import CreateVolumeRequest
            
            volume_request = CreateVolumeRequest(
                name=f"vol-{server.name}",
                size=volume_config.get("size", 50),
                location=server_config.get("location", "nbg1"),
            )
            volume = self.client.volumes.create(volume_request)
            self._log_result(f"Volumen {volume.name} creado", {"id": volume.id})
            
            # Conectar volumen al servidor
            self.client.volumes.attach(volume.id, server.id)
            self._log_result(f"Volumen {volume.name} conectado a servidor {server.name}")
        
        # Crear firewall si está configurado
        firewall_config = config.get("firewall", {})
        firewall = None
        if firewall_config.get("create", False):
            from hetzner_mcp.core.models import CreateFirewallRequest
            
            firewall_request = CreateFirewallRequest(
                name=f"fw-{server.name}",
                rules=firewall_config.get("rules", []),
            )
            firewall = self.client.firewalls.create(firewall_request)
            self._log_result(f"Firewall {firewall.name} creado", {"id": firewall.id})
            
            # Aplicar firewall al servidor
            self.client.firewalls.apply_to_resources(
                firewall.id,
                [{"type": "server", "server": {"id": server.id}}]
            )
            self._log_result(f"Firewall {firewall.name} aplicado a servidor {server.name}")
        
        return {
            "server": server.model_dump(),
            "volume": volume.model_dump() if volume else None,
            "firewall": firewall.model_dump() if firewall else None,
        }


class MonitoringScript(AutomationScript):
    """Script para monitoreo de recursos."""

    def _execute(
        self,
        resource_type: str = "server",
        check_status: bool = True,
        check_metrics: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Ejecutar monitoreo.
        
        Args:
            resource_type: Tipo de recurso a monitorear
            check_status: Verificar estado
            check_metrics: Verificar métricas
            
        Returns:
            Dict con información de monitoreo
        """
        monitoring_data = {}
        
        self._log_result(f"Iniciando monitoreo de {resource_type}")
        
        if resource_type == "server":
            servers = self.client.servers.list_all()
            
            status_summary = {
                "total": len(servers),
                "running": 0,
                "stopped": 0,
                "other": 0,
            }
            
            server_details = []
            
            for server in servers:
                status = server.status
                if status == "running":
                    status_summary["running"] += 1
                elif status == "off":
                    status_summary["stopped"] += 1
                else:
                    status_summary["other"] += 1
                
                server_info = {
                    "id": server.id,
                    "name": server.name,
                    "status": status,
                    "ipv4": server.ipv4_address,
                    "ipv6": server.ipv6_address,
                }
                
                if check_metrics:
                    try:
                        metrics = self.client.servers.get_metrics(server.id, type="cpu")
                        server_info["metrics"] = metrics
                    except Exception as e:
                        server_info["metrics_error"] = str(e)
                
                server_details.append(server_info)
            
            monitoring_data["servers"] = {
                "summary": status_summary,
                "details": server_details,
            }
        
        elif resource_type == "volume":
            volumes = self.client.volumes.list_all()
            
            volume_summary = {
                "total": len(volumes),
                "available": sum(1 for v in volumes if v.status == "available"),
                "in_use": sum(1 for v in volumes if v.status == "in_use"),
                "other": sum(1 for v in volumes if v.status not in ["available", "in_use"]),
            }
            
            monitoring_data["volumes"] = {
                "summary": volume_summary,
                "details": [v.model_dump() for v in volumes],
            }
        
        elif resource_type == "network":
            networks = self.client.networks.list_all()
            
            network_summary = {
                "total": len(networks),
                "details": [n.model_dump() for n in networks],
            }
            
            monitoring_data["networks"] = network_summary
        
        return monitoring_data
