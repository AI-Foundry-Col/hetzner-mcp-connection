"""
API de Redes de Hetzner Cloud
"""

from typing import Any, Dict, List, Optional, Union

from hetzner_mcp.core.config import get_settings
from hetzner_mcp.core.exceptions import HetznerSafeModeError
from hetzner_mcp.core.models import (
    Action,
    ActionListResponse,
    CreateNetworkRequest,
    Network,
    NetworkListResponse,
)


class NetworkAPI:
    """API para gestionar redes de Hetzner Cloud."""

    def __init__(self, client: Any):
        """
        Inicializar la API de redes.
        
        Args:
            client: Instancia del cliente principal de Hetzner
        """
        self.client = client
        self.safe_mode = get_settings().safe_mode

    def _check_safe_mode(self, operation: str) -> None:
        """Verificar si la operación está permitida en modo seguro."""
        write_operations = ["create", "update", "delete", "attach", "detach"]
        if self.safe_mode and any(op in operation.lower() for op in write_operations):
            raise HetznerSafeModeError(operation)

    def list(
        self,
        name: Optional[str] = None,
        label_selector: Optional[str] = None,
        page: int = 1,
        per_page: int = get_settings().page_size,
    ) -> NetworkListResponse:
        """
        Listar redes.
        
        Args:
            name: Filtrar por nombre
            label_selector: Filtrar por selector de etiquetas
            page: Número de página
            per_page: Resultados por página
            
        Returns:
            NetworkListResponse: Lista de redes con paginación
        """
        params = {
            "page": page,
            "per_page": per_page,
        }
        if name:
            params["name"] = name
        if label_selector:
            params["label_selector"] = label_selector
        
        data = self.client._get("networks", params=params)
        return NetworkListResponse(**data)

    def get(self, network_id: int) -> Network:
        """
        Obtener una red por ID.
        
        Args:
            network_id: ID de la red
            
        Returns:
            Network: Objeto red
        """
        data = self.client._get(f"networks/{network_id}")
        return Network(**data["network"])

    def get_by_name(self, name: str) -> Optional[Network]:
        """
        Obtener una red por nombre.
        
        Args:
            name: Nombre de la red
            
        Returns:
            Network o None si no se encuentra
        """
        networks = self.list(name=name)
        if networks.networks:
            return networks.networks[0]
        return None

    def list_all(self) -> List[Network]:
        """
        Listar todas las redes (sin paginación).
        
        Returns:
            List[Network]: Todas las redes
        """
        all_networks = []
        page = 1
        
        while True:
            response = self.list(page=page, per_page=50)
            all_networks.extend(response.networks)
            
            if not response.meta or not response.meta.pagination or not response.meta.pagination.next_page:
                break
            
            page = response.meta.pagination.next_page
        
        return all_networks

    def create(self, request: CreateNetworkRequest) -> Network:
        """
        Crear una red.
        
        Args:
            request: Request con los datos de la red
            
        Returns:
            Network: Red creada
        """
        self._check_safe_mode("create_network")
        
        network_data = request.model_dump(exclude_unset=True)
        data = self.client._post("networks", json_data={"network": network_data})
        return Network(**data["network"])

    def update(
        self,
        network_id: int,
        name: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None,
        ip_range: Optional[str] = None,
    ) -> Network:
        """
        Actualizar una red.
        
        Args:
            network_id: ID de la red
            name: Nuevo nombre
            labels: Nuevas etiquetas
            ip_range: Nuevo rango IP
            
        Returns:
            Network: Red actualizada
        """
        self._check_safe_mode("update_network")
        
        payload = {}
        if name:
            payload["name"] = name
        if labels:
            payload["labels"] = labels
        if ip_range:
            payload["ip_range"] = ip_range
        
        data = self.client._put(f"networks/{network_id}", json_data={"network": payload})
        return Network(**data["network"])

    def delete(self, network_id: int) -> None:
        """
        Eliminar una red.
        
        Args:
            network_id: ID de la red
        """
        self._check_safe_mode("delete_network")
        
        self.client._delete(f"networks/{network_id}")

    def attach_server(self, network_id: int, server_id: int, ip: Optional[str] = None) -> Action:
        """
        Conectar un servidor a una red.
        
        Args:
            network_id: ID de la red
            server_id: ID del servidor
            ip: IP opcional para asignar
            
        Returns:
            Action: Acción de conexión
        """
        self._check_safe_mode("attach_server_to_network")
        
        payload = {"server": server_id}
        if ip:
            payload["ip"] = ip
        
        data = self.client._post(f"networks/{network_id}/actions/attach_to_network", json_data=payload)
        return Action(**data["action"])

    def detach_server(self, network_id: int, server_id: int) -> Action:
        """
        Desconectar un servidor de una red.
        
        Args:
            network_id: ID de la red
            server_id: ID del servidor
            
        Returns:
            Action: Acción de desconexión
        """
        self._check_safe_mode("detach_server_from_network")
        
        payload = {"server": server_id}
        data = self.client._post(f"networks/{network_id}/actions/detach_from_network", json_data=payload)
        return Action(**data["action"])

    def get_actions(self, network_id: int, page: int = 1, per_page: int = 25) -> ActionListResponse:
        """
        Obtener acciones de una red.
        
        Args:
            network_id: ID de la red
            page: Número de página
            per_page: Resultados por página
            
        Returns:
            ActionListResponse: Lista de acciones
        """
        data = self.client._get(f"networks/{network_id}/actions", params={"page": page, "per_page": per_page})
        return ActionListResponse(**data)
