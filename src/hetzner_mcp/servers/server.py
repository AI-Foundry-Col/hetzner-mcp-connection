"""
API de Servidores de Hetzner Cloud

Sigue los principios NUPP:
- Open: API abierta y documentada
- Minimalist: Solo lo esencial para gestionar servidores
- Modular: Fácil de extender con nuevas funcionalidades
"""

from typing import Any, Dict, List, Optional, Union

from hetzner_mcp.core.config import get_settings
from hetzner_mcp.core.exceptions import HetznerSafeModeError
from hetzner_mcp.core.models import (
    Action,
    ActionListResponse,
    CreateServerRequest,
    Server,
    ServerListResponse,
    UpdateServerRequest,
)


class ServerAPI:
    """API para gestionar servidores de Hetzner Cloud."""

    def __init__(self, client: Any):
        """
        Inicializar la API de servidores.
        
        Args:
            client: Instancia del cliente principal de Hetzner
        """
        self.client = client
        self.safe_mode = get_settings().safe_mode
        self.protected_servers = set(get_settings().protected_servers)

    def _check_safe_mode(self, operation: str) -> None:
        """Verificar si la operación está permitida en modo seguro."""
        write_operations = ["create", "update", "delete", "poweroff", "reboot", "reset"]
        if self.safe_mode and any(op in operation.lower() for op in write_operations):
            raise HetznerSafeModeError(operation)

    def _check_protected_server(self, server_id: int, operation: str) -> None:
        """Verificar si el servidor está protegido."""
        if server_id in self.protected_servers:
            raise HetznerSafeModeError(f"{operation} en servidor protegido {server_id}")

    def list(
        self,
        name: Optional[str] = None,
        label_selector: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        per_page: int = get_settings().page_size,
    ) -> ServerListResponse:
        """
        Listar servidores.
        
        Args:
            name: Filtrar por nombre de servidor
            label_selector: Filtrar por selector de etiquetas
            status: Filtrar por estado
            page: Número de página
            per_page: Resultados por página
            
        Returns:
            ServerListResponse: Lista de servidores con paginación
        """
        params = {
            "page": page,
            "per_page": per_page,
        }
        if name:
            params["name"] = name
        if label_selector:
            params["label_selector"] = label_selector
        if status:
            params["status"] = status
        
        data = self.client._get("servers", params=params)
        return ServerListResponse(**data)

    def get(self, server_id: int) -> Server:
        """
        Obtener un servidor por ID.
        
        Args:
            server_id: ID del servidor
            
        Returns:
            Server: Objeto servidor
        """
        data = self.client._get(f"servers/{server_id}")
        return Server(**data["server"])

    def get_by_name(self, name: str) -> Optional[Server]:
        """
        Obtener un servidor por nombre.
        
        Args:
            name: Nombre del servidor
            
        Returns:
            Server o None si no se encuentra
        """
        servers = self.list(name=name)
        if servers.servers:
            return servers.servers[0]
        return None

    def list_all(self) -> List[Server]:
        """
        Listar todos los servidores (sin paginación).
        
        Returns:
            List[Server]: Todos los servidores
        """
        all_servers = []
        page = 1
        
        while True:
            response = self.list(page=page, per_page=50)
            all_servers.extend(response.servers)
            
            if not response.meta or not response.meta.pagination or not response.meta.pagination.next_page:
                break
            
            page = response.meta.pagination.next_page
        
        return all_servers

    def create(self, request: CreateServerRequest) -> Server:
        """
        Crear un servidor.
        
        Args:
            request: Request con los datos del servidor
            
        Returns:
            Server: Servidor creado
        """
        self._check_safe_mode("create_server")
        
        # Convertir request a dict
        server_data = request.model_dump(exclude_unset=True)
        
        # Manejar campos especiales
        if "ssh_keys" in server_data and server_data["ssh_keys"]:
            server_data["ssh_keys"] = [
                {"id": kid if isinstance(kid, int) else {"name": kid} }
                for kid in server_data["ssh_keys"]
            ]
        
        if "volumes" in server_data and server_data["volumes"]:
            server_data["volumes"] = [
                {"id": vid if isinstance(vid, int) else {"name": vid} }
                for vid in server_data["volumes"]
            ]
        
        if "networks" in server_data and server_data["networks"]:
            server_data["networks"] = [
                {"id": nid if isinstance(nid, int) else {"name": nid} }
                for nid in server_data["networks"]
            ]
        
        data = self.client._post("servers", json_data={"server": server_data})
        return Server(**data["server"])

    def update(self, server_id: int, request: UpdateServerRequest) -> Server:
        """
        Actualizar un servidor.
        
        Args:
            server_id: ID del servidor
            request: Request con los datos a actualizar
            
        Returns:
            Server: Servidor actualizado
        """
        self._check_safe_mode("update_server")
        self._check_protected_server(server_id, "update_server")
        
        server_data = request.model_dump(exclude_unset=True)
        data = self.client._put(f"servers/{server_id}", json_data={"server": server_data})
        return Server(**data["server"])

    def delete(self, server_id: int) -> None:
        """
        Eliminar un servidor.
        
        Args:
            server_id: ID del servidor
        """
        self._check_safe_mode("delete_server")
        self._check_protected_server(server_id, "delete_server")
        
        self.client._delete(f"servers/{server_id}")

    def start(self, server_id: int) -> Action:
        """
        Iniciar un servidor.
        
        Args:
            server_id: ID del servidor
            
        Returns:
            Action: Acción de inicio
        """
        self._check_safe_mode("start_server")
        
        data = self.client._post(f"servers/{server_id}/actions/poweron")
        return Action(**data["action"])

    def stop(self, server_id: int) -> Action:
        """
        Parar un servidor.
        
        Args:
            server_id: ID del servidor
            
        Returns:
            Action: Acción de parada
        """
        self._check_safe_mode("stop_server")
        self._check_protected_server(server_id, "stop_server")
        
        data = self.client._post(f"servers/{server_id}/actions/poweroff")
        return Action(**data["action"])

    def reboot(self, server_id: int) -> Action:
        """
        Reiniciar un servidor.
        
        Args:
            server_id: ID del servidor
            
        Returns:
            Action: Acción de reinicio
        """
        self._check_safe_mode("reboot_server")
        self._check_protected_server(server_id, "reboot_server")
        
        data = self.client._post(f"servers/{server_id}/actions/reboot")
        return Action(**data["action"])

    def reset(self, server_id: int) -> Action:
        """
        Resetear un servidor.
        
        Args:
            server_id: ID del servidor
            
        Returns:
            Action: Acción de reset
        """
        self._check_safe_mode("reset_server")
        self._check_protected_server(server_id, "reset_server")
        
        data = self.client._post(f"servers/{server_id}/actions/reset")
        return Action(**data["action"])

    def shutdown(self, server_id: int) -> Action:
        """
        Apagar un servidor (graceful shutdown).
        
        Args:
            server_id: ID del servidor
            
        Returns:
            Action: Acción de apagado
        """
        self._check_safe_mode("shutdown_server")
        self._check_protected_server(server_id, "shutdown_server")
        
        data = self.client._post(f"servers/{server_id}/actions/shutdown")
        return Action(**data["action"])

    def enable_backup(self, server_id: int, backup_window: Optional[str] = None) -> Action:
        """
        Habilitar backups para un servidor.
        
        Args:
            server_id: ID del servidor
            backup_window: Ventana de backup (ej: "00-06")
            
        Returns:
            Action: Acción de habilitación de backup
        """
        self._check_safe_mode("enable_backup")
        
        payload = {}
        if backup_window:
            payload["backup_window"] = backup_window
        
        data = self.client._post(f"servers/{server_id}/actions/enable_backup", json_data=payload)
        return Action(**data["action"])

    def disable_backup(self, server_id: int) -> Action:
        """
        Deshabilitar backups para un servidor.
        
        Args:
            server_id: ID del servidor
            
        Returns:
            Action: Acción de deshabilitación de backup
        """
        self._check_safe_mode("disable_backup")
        
        data = self.client._post(f"servers/{server_id}/actions/disable_backup")
        return Action(**data["action"])

    def enable_rescue(self, server_id: int, ssh_keys: Optional[List[int]] = None) -> Action:
        """
        Habilitar modo rescue para un servidor.
        
        Args:
            server_id: ID del servidor
            ssh_keys: Lista de IDs de claves SSH
            
        Returns:
            Action: Acción de habilitación de rescue
        """
        self._check_safe_mode("enable_rescue")
        
        payload = {}
        if ssh_keys:
            payload["ssh_keys"] = [{"id": kid} for kid in ssh_keys]
        
        data = self.client._post(f"servers/{server_id}/actions/enable_rescue", json_data=payload)
        return Action(**data["action"])

    def disable_rescue(self, server_id: int) -> Action:
        """
        Deshabilitar modo rescue para un servidor.
        
        Args:
            server_id: ID del servidor
            
        Returns:
            Action: Acción de deshabilitación de rescue
        """
        self._check_safe_mode("disable_rescue")
        
        data = self.client._post(f"servers/{server_id}/actions/disable_rescue")
        return Action(**data["action"])

    def rebuild(
        self,
        server_id: int,
        image: Union[str, int],
        ssh_keys: Optional[List[int]] = None,
    ) -> Action:
        """
        Reconstruir un servidor con una nueva imagen.
        
        Args:
            server_id: ID del servidor
            image: Nombre o ID de la imagen
            ssh_keys: Lista de IDs de claves SSH
            
        Returns:
            Action: Acción de reconstrucción
        """
        self._check_safe_mode("rebuild_server")
        self._check_protected_server(server_id, "rebuild_server")
        
        payload = {"image": image}
        if ssh_keys:
            payload["ssh_keys"] = [{"id": kid} for kid in ssh_keys]
        
        data = self.client._post(f"servers/{server_id}/actions/rebuild", json_data=payload)
        return Action(**data["action"])

    def change_type(
        self,
        server_id: int,
        server_type: Union[str, int],
        upgrade_disk: bool = False,
    ) -> Action:
        """
        Cambiar el tipo de servidor.
        
        Args:
            server_id: ID del servidor
            server_type: Nombre o ID del tipo de servidor
            upgrade_disk: Si se debe actualizar el disco
            
        Returns:
            Action: Acción de cambio de tipo
        """
        self._check_safe_mode("change_type")
        self._check_protected_server(server_id, "change_type")
        
        payload = {"server_type": server_type, "upgrade_disk": upgrade_disk}
        data = self.client._post(f"servers/{server_id}/actions/change_type", json_data=payload)
        return Action(**data["action"])

    def create_image(
        self,
        server_id: int,
        description: Optional[str] = None,
        type: str = "snapshot",
    ) -> Action:
        """
        Crear una imagen (snapshot) de un servidor.
        
        Args:
            server_id: ID del servidor
            description: Descripción de la imagen
            type: Tipo de imagen (snapshot, backup)
            
        Returns:
            Action: Acción de creación de imagen
        """
        self._check_safe_mode("create_image")
        
        payload = {"type": type}
        if description:
            payload["description"] = description
        
        data = self.client._post(f"servers/{server_id}/actions/create_image", json_data=payload)
        return Action(**data["action"])

    def get_actions(self, server_id: int, page: int = 1, per_page: int = 25) -> ActionListResponse:
        """
        Obtener acciones de un servidor.
        
        Args:
            server_id: ID del servidor
            page: Número de página
            per_page: Resultados por página
            
        Returns:
            ActionListResponse: Lista de acciones
        """
        data = self.client._get(f"servers/{server_id}/actions", params={"page": page, "per_page": per_page})
        return ActionListResponse(**data)

    def get_metrics(
        self,
        server_id: int,
        type: str,
        start: Optional[str] = None,
        end: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Obtener métricas de un servidor.
        
        Args:
            server_id: ID del servidor
            type: Tipo de métrica
            start: Fecha de inicio
            end: Fecha de fin
            
        Returns:
            Dict: Datos de métricas
        """
        params = {"type": type}
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        
        data = self.client._get(f"servers/{server_id}/metrics", params=params)
        return data

    def wait_for_action(
        self,
        action_id: int,
        timeout: int = 300,
        poll_interval: float = 1.0,
    ) -> Action:
        """
        Esperar a que una acción se complete.
        
        Args:
            action_id: ID de la acción
            timeout: Timeout en segundos
            poll_interval: Intervalo de polling en segundos
            
        Returns:
            Action: Acción completada
        """
        import time
        
        start_time = time.time()
        
        while True:
            action = self.client.actions.get(action_id)
            
            if action.is_completed:
                return action
            
            if time.time() - start_time > timeout:
                from hetzner_mcp.core.exceptions import HetznerAPIError
                raise HetznerAPIError(
                    f"Timeout esperando la acción {action_id}",
                    status_code=408,
                    error_code="timeout",
                )
            
            time.sleep(poll_interval)
