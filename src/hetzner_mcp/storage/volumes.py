"""
API de Volúmenes de Hetzner Cloud
"""

from typing import Any, Dict, List, Optional

from hetzner_mcp.core.config import settings
from hetzner_mcp.core.exceptions import HetznerSafeModeError
from hetzner_mcp.core.models import (
    Action,
    ActionListResponse,
    CreateVolumeRequest,
    Volume,
    VolumeListResponse,
)


class VolumeAPI:
    """API para gestionar volúmenes de Hetzner Cloud."""

    def __init__(self, client: Any):
        """
        Inicializar la API de volúmenes.
        
        Args:
            client: Instancia del cliente principal de Hetzner
        """
        self.client = client
        self.safe_mode = settings.safe_mode

    def _check_safe_mode(self, operation: str) -> None:
        """Verificar si la operación está permitida en modo seguro."""
        write_operations = ["create", "update", "delete", "attach", "detach", "resize"]
        if self.safe_mode and any(op in operation.lower() for op in write_operations):
            raise HetznerSafeModeError(operation)

    def list(
        self,
        name: Optional[str] = None,
        label_selector: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        per_page: int = settings.page_size,
    ) -> VolumeListResponse:
        """
        Listar volúmenes.
        
        Args:
            name: Filtrar por nombre
            label_selector: Filtrar por selector de etiquetas
            status: Filtrar por estado
            page: Número de página
            per_page: Resultados por página
            
        Returns:
            VolumeListResponse: Lista de volúmenes con paginación
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
        
        data = self.client._get("volumes", params=params)
        return VolumeListResponse(**data)

    def get(self, volume_id: int) -> Volume:
        """
        Obtener un volumen por ID.
        
        Args:
            volume_id: ID del volumen
            
        Returns:
            Volume: Objeto volumen
        """
        data = self.client._get(f"volumes/{volume_id}")
        return Volume(**data["volume"])

    def get_by_name(self, name: str) -> Optional[Volume]:
        """
        Obtener un volumen por nombre.
        
        Args:
            name: Nombre del volumen
            
        Returns:
            Volume o None si no se encuentra
        """
        volumes = self.list(name=name)
        if volumes.volumes:
            return volumes.volumes[0]
        return None

    def list_all(self) -> List[Volume]:
        """
        Listar todos los volúmenes (sin paginación).
        
        Returns:
            List[Volume]: Todos los volúmenes
        """
        all_volumes = []
        page = 1
        
        while True:
            response = self.list(page=page, per_page=50)
            all_volumes.extend(response.volumes)
            
            if not response.meta or not response.meta.pagination or not response.meta.pagination.next_page:
                break
            
            page = response.meta.pagination.next_page
        
        return all_volumes

    def create(self, request: CreateVolumeRequest) -> Volume:
        """
        Crear un volumen.
        
        Args:
            request: Request con los datos del volumen
            
        Returns:
            Volume: Volumen creado
        """
        self._check_safe_mode("create_volume")
        
        volume_data = request.model_dump(exclude_unset=True)
        data = self.client._post("volumes", json_data={"volume": volume_data})
        return Volume(**data["volume"])

    def update(self, volume_id: int, name: Optional[str] = None, labels: Optional[Dict[str, str]] = None) -> Volume:
        """
        Actualizar un volumen.
        
        Args:
            volume_id: ID del volumen
            name: Nuevo nombre
            labels: Nuevas etiquetas
            
        Returns:
            Volume: Volumen actualizado
        """
        self._check_safe_mode("update_volume")
        
        payload = {}
        if name:
            payload["name"] = name
        if labels:
            payload["labels"] = labels
        
        data = self.client._put(f"volumes/{volume_id}", json_data={"volume": payload})
        return Volume(**data["volume"])

    def delete(self, volume_id: int) -> None:
        """
        Eliminar un volumen.
        
        Args:
            volume_id: ID del volumen
        """
        self._check_safe_mode("delete_volume")
        
        self.client._delete(f"volumes/{volume_id}")

    def attach(self, volume_id: int, server_id: int, automount: bool = True) -> Action:
        """
        Conectar un volumen a un servidor.
        
        Args:
            volume_id: ID del volumen
            server_id: ID del servidor
            automount: Si se debe montar automáticamente
            
        Returns:
            Action: Acción de conexión
        """
        self._check_safe_mode("attach_volume")
        
        payload = {"server": server_id, "automount": automount}
        data = self.client._post(f"volumes/{volume_id}/actions/attach", json_data=payload)
        return Action(**data["action"])

    def detach(self, volume_id: int) -> Action:
        """
        Desconectar un volumen de un servidor.
        
        Args:
            volume_id: ID del volumen
            
        Returns:
            Action: Acción de desconexión
        """
        self._check_safe_mode("detach_volume")
        
        data = self.client._post(f"volumes/{volume_id}/actions/detach")
        return Action(**data["action"])

    def resize(self, volume_id: int, size: int) -> Action:
        """
        Redimensionar un volumen.
        
        Args:
            volume_id: ID del volumen
            size: Nuevo tamaño en GB
            
        Returns:
            Action: Acción de redimensionamiento
        """
        self._check_safe_mode("resize_volume")
        
        data = self.client._post(f"volumes/{volume_id}/actions/resize", json_data={"size": size})
        return Action(**data["action"])

    def change_protection(self, volume_id: int, delete: bool = True) -> Action:
        """
        Cambiar la protección de eliminación de un volumen.
        
        Args:
            volume_id: ID del volumen
            delete: Si se debe proteger contra eliminación
            
        Returns:
            Action: Acción de cambio de protección
        """
        self._check_safe_mode("change_protection")
        
        data = self.client._post(
            f"volumes/{volume_id}/actions/change_protection",
            json_data={"delete": delete}
        )
        return Action(**data["action"])

    def get_actions(self, volume_id: int, page: int = 1, per_page: int = 25) -> ActionListResponse:
        """
        Obtener acciones de un volumen.
        
        Args:
            volume_id: ID del volumen
            page: Número de página
            per_page: Resultados por página
            
        Returns:
            ActionListResponse: Lista de acciones
        """
        data = self.client._get(f"volumes/{volume_id}/actions", params={"page": page, "per_page": per_page})
        return ActionListResponse(**data)
