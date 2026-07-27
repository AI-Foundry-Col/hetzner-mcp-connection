"""
Acciones de Servidores de Hetzner Cloud

Este módulo contiene funciones para manejar acciones específicas de servidores.
"""

from typing import Any, Dict, List, Optional

from hetzner_mcp.core.client import HetznerClient
from hetzner_mcp.core.models import Action, Server


class ServerActionAPI:
    """API para acciones avanzadas de servidores."""

    def __init__(self, client: HetznerClient):
        """
        Inicializar la API de acciones de servidores.
        
        Args:
            client: Cliente de Hetzner
        """
        self.client = client

    def enable_backup(self, server_id: int, backup_window: Optional[str] = None) -> Action:
        """Habilitar backups para un servidor."""
        payload = {}
        if backup_window:
            payload["backup_window"] = backup_window
        
        data = self.client._post(f"servers/{server_id}/actions/enable_backup", json_data=payload)
        return Action(**data["action"])

    def disable_backup(self, server_id: int) -> Action:
        """Deshabilitar backups para un servidor."""
        data = self.client._post(f"servers/{server_id}/actions/disable_backup")
        return Action(**data["action"])

    def enable_rescue(self, server_id: int, ssh_keys: Optional[List[int]] = None) -> Action:
        """Habilitar modo rescue para un servidor."""
        payload = {}
        if ssh_keys:
            payload["ssh_keys"] = [{"id": kid} for kid in ssh_keys]
        
        data = self.client._post(f"servers/{server_id}/actions/enable_rescue", json_data=payload)
        return Action(**data["action"])

    def disable_rescue(self, server_id: int) -> Action:
        """Deshabilitar modo rescue para un servidor."""
        data = self.client._post(f"servers/{server_id}/actions/disable_rescue")
        return Action(**data["action"])

    def rebuild(
        self,
        server_id: int,
        image: Union[str, int],
        ssh_keys: Optional[List[int]] = None,
    ) -> Action:
        """Reconstruir un servidor con una nueva imagen."""
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
        """Cambiar el tipo de servidor."""
        payload = {"server_type": server_type, "upgrade_disk": upgrade_disk}
        data = self.client._post(f"servers/{server_id}/actions/change_type", json_data=payload)
        return Action(**data["action"])

    def create_image(
        self,
        server_id: int,
        description: Optional[str] = None,
        type: str = "snapshot",
    ) -> Action:
        """Crear una imagen (snapshot) de un servidor."""
        payload = {"type": type}
        if description:
            payload["description"] = description
        
        data = self.client._post(f"servers/{server_id}/actions/create_image", json_data=payload)
        return Action(**data["action"])

    def change_protection(
        self,
        server_id: int,
        delete: bool = True,
        rebuild: bool = True,
    ) -> Action:
        """Cambiar la protección de un servidor."""
        payload = {"delete": delete, "rebuild": rebuild}
        data = self.client._post(f"servers/{server_id}/actions/change_protection", json_data=payload)
        return Action(**data["action"])

    def request_console(self, server_id: int) -> Action:
        """Solicitar acceso a la consola de un servidor."""
        data = self.client._post(f"servers/{server_id}/actions/request_console")
        return Action(**data["action"])

    def reset_password(self, server_id: int) -> Action:
        """Resetear la contraseña de root de un servidor."""
        data = self.client._post(f"servers/{server_id}/actions/reset_password")
        return Action(**data["action"])

    def change_dns_ptr(self, server_id: int, ip: str, dns_ptr: str) -> Action:
        """Cambiar el DNS PTR de una IP de servidor."""
        payload = {"ip": ip, "dns_ptr": dns_ptr}
        data = self.client._post(f"servers/{server_id}/actions/change_dns_ptr", json_data=payload)
        return Action(**data["action"])

    def attach_iso(self, server_id: int, iso_id: int) -> Action:
        """Adjuntar un ISO a un servidor."""
        payload = {"iso": iso_id}
        data = self.client._post(f"servers/{server_id}/actions/attach_iso", json_data=payload)
        return Action(**data["action"])

    def detach_iso(self, server_id: int) -> Action:
        """Desadjuntar ISO de un servidor."""
        data = self.client._post(f"servers/{server_id}/actions/detach_iso")
        return Action(**data["action"])

    def attach_to_placement_group(self, server_id: int, placement_group_id: int) -> Action:
        """Adjuntar servidor a un placement group."""
        payload = {"placement_group": placement_group_id}
        data = self.client._post(f"servers/{server_id}/actions/add_to_placement_group", json_data=payload)
        return Action(**data["action"])

    def remove_from_placement_group(self, server_id: int, placement_group_id: int) -> Action:
        """Remover servidor de un placement group."""
        payload = {"placement_group": placement_group_id}
        data = self.client._post(f"servers/{server_id}/actions/remove_from_placement_group", json_data=payload)
        return Action(**data["action"])

    def attach_to_network(self, server_id: int, network_id: int, ip: Optional[str] = None) -> Action:
        """Adjuntar servidor a una red."""
        payload = {"network": network_id}
        if ip:
            payload["ip"] = ip
        
        data = self.client._post(f"servers/{server_id}/actions/attach_to_network", json_data=payload)
        return Action(**data["action"])

    def detach_from_network(self, server_id: int, network_id: int) -> Action:
        """Desadjuntar servidor de una red."""
        payload = {"network": network_id}
        data = self.client._post(f"servers/{server_id}/actions/detach_from_network", json_data=payload)
        return Action(**data["action"])

    def change_alias_ips(self, server_id: int, alias_ips: List[str]) -> Action:
        """Cambiar las IPs alias de un servidor."""
        payload = {"alias_ips": alias_ips}
        data = self.client._post(f"servers/{server_id}/actions/change_alias_ips", json_data=payload)
        return Action(**data["action"])
