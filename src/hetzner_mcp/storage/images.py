"""
API de Imágenes de Hetzner Cloud
"""

from typing import Any, Dict, List, Optional

from hetzner_mcp.core.config import settings
from hetzner_mcp.core.exceptions import HetznerSafeModeError
from hetzner_mcp.core.models import (
    Action,
    ActionListResponse,
    Image,
    ImageListResponse,
)


class ImageAPI:
    """API para gestionar imágenes de Hetzner Cloud."""

    def __init__(self, client: Any):
        """
        Inicializar la API de imágenes.
        
        Args:
            client: Instancia del cliente principal de Hetzner
        """
        self.client = client
        self.safe_mode = settings.safe_mode

    def _check_safe_mode(self, operation: str) -> None:
        """Verificar si la operación está permitida en modo seguro."""
        write_operations = ["update", "delete", "change_protection"]
        if self.safe_mode and any(op in operation.lower() for op in write_operations):
            raise HetznerSafeModeError(operation)

    def list(
        self,
        type: Optional[str] = None,
        name: Optional[str] = None,
        label_selector: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        per_page: int = settings.page_size,
    ) -> ImageListResponse:
        """
        Listar imágenes.
        
        Args:
            type: Filtrar por tipo (system, snapshot, backup, app)
            name: Filtrar por nombre
            label_selector: Filtrar por selector de etiquetas
            status: Filtrar por estado
            page: Número de página
            per_page: Resultados por página
            
        Returns:
            ImageListResponse: Lista de imágenes con paginación
        """
        params = {
            "page": page,
            "per_page": per_page,
        }
        if type:
            params["type"] = type
        if name:
            params["name"] = name
        if label_selector:
            params["label_selector"] = label_selector
        if status:
            params["status"] = status
        
        data = self.client._get("images", params=params)
        return ImageListResponse(**data)

    def get(self, image_id: int) -> Image:
        """
        Obtener una imagen por ID.
        
        Args:
            image_id: ID de la imagen
            
        Returns:
            Image: Objeto imagen
        """
        data = self.client._get(f"images/{image_id}")
        return Image(**data["image"])

    def get_by_name(self, name: str, type: Optional[str] = None) -> Optional[Image]:
        """
        Obtener una imagen por nombre.
        
        Args:
            name: Nombre de la imagen
            type: Tipo de imagen (opcional)
            
        Returns:
            Image o None si no se encuentra
        """
        images = self.list(name=name, type=type)
        if images.images:
            return images.images[0]
        return None

    def list_all(self, type: Optional[str] = None) -> List[Image]:
        """
        Listar todas las imágenes (sin paginación).
        
        Args:
            type: Filtrar por tipo (opcional)
            
        Returns:
            List[Image]: Todas las imágenes
        """
        all_images = []
        page = 1
        
        while True:
            response = self.list(type=type, page=page, per_page=50)
            all_images.extend(response.images)
            
            if not response.meta or not response.meta.pagination or not response.meta.pagination.next_page:
                break
            
            page = response.meta.pagination.next_page
        
        return all_images

    def update(
        self,
        image_id: int,
        description: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None,
    ) -> Image:
        """
        Actualizar una imagen.
        
        Args:
            image_id: ID de la imagen
            description: Nueva descripción
            labels: Nuevas etiquetas
            
        Returns:
            Image: Imagen actualizada
        """
        self._check_safe_mode("update_image")
        
        payload = {}
        if description:
            payload["description"] = description
        if labels:
            payload["labels"] = labels
        
        data = self.client._put(f"images/{image_id}", json_data={"image": payload})
        return Image(**data["image"])

    def delete(self, image_id: int) -> None:
        """
        Eliminar una imagen.
        
        Args:
            image_id: ID de la imagen
        """
        self._check_safe_mode("delete_image")
        
        self.client._delete(f"images/{image_id}")

    def change_protection(self, image_id: int, delete: bool = True) -> Action:
        """
        Cambiar la protección de eliminación de una imagen.
        
        Args:
            image_id: ID de la imagen
            delete: Si se debe proteger contra eliminación
            
        Returns:
            Action: Acción de cambio de protección
        """
        self._check_safe_mode("change_protection")
        
        data = self.client._post(
            f"images/{image_id}/actions/change_protection",
            json_data={"delete": delete}
        )
        return Action(**data["action"])

    def get_actions(self, image_id: int, page: int = 1, per_page: int = 25) -> ActionListResponse:
        """
        Obtener acciones de una imagen.
        
        Args:
            image_id: ID de la imagen
            page: Número de página
            per_page: Resultados por página
            
        Returns:
            ActionListResponse: Lista de acciones
        """
        data = self.client._get(f"images/{image_id}/actions", params={"page": page, "per_page": per_page})
        return ActionListResponse(**data)
