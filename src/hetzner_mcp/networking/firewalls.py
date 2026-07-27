"""
API de Firewalls de Hetzner Cloud
"""

from typing import Any, Dict, List, Optional

from hetzner_mcp.core.config import settings
from hetzner_mcp.core.exceptions import HetznerSafeModeError
from hetzner_mcp.core.models import (
    Action,
    ActionListResponse,
    CreateFirewallRequest,
    Firewall,
    FirewallListResponse,
)


class FirewallAPI:
    """API para gestionar firewalls de Hetzner Cloud."""

    def __init__(self, client: Any):
        """
        Inicializar la API de firewalls.
        
        Args:
            client: Instancia del cliente principal de Hetzner
        """
        self.client = client
        self.safe_mode = settings.safe_mode

    def _check_safe_mode(self, operation: str) -> None:
        """Verificar si la operación está permitida en modo seguro."""
        write_operations = ["create", "update", "delete", "apply", "remove", "set_rules"]
        if self.safe_mode and any(op in operation.lower() for op in write_operations):
            raise HetznerSafeModeError(operation)

    def list(
        self,
        name: Optional[str] = None,
        label_selector: Optional[str] = None,
        page: int = 1,
        per_page: int = settings.page_size,
    ) -> FirewallListResponse:
        """
        Listar firewalls.
        
        Args:
            name: Filtrar por nombre
            label_selector: Filtrar por selector de etiquetas
            page: Número de página
            per_page: Resultados por página
            
        Returns:
            FirewallListResponse: Lista de firewalls con paginación
        """
        params = {
            "page": page,
            "per_page": per_page,
        }
        if name:
            params["name"] = name
        if label_selector:
            params["label_selector"] = label_selector
        
        data = self.client._get("firewalls", params=params)
        return FirewallListResponse(**data)

    def get(self, firewall_id: int) -> Firewall:
        """
        Obtener un firewall por ID.
        
        Args:
            firewall_id: ID del firewall
            
        Returns:
            Firewall: Objeto firewall
        """
        data = self.client._get(f"firewalls/{firewall_id}")
        return Firewall(**data["firewall"])

    def get_by_name(self, name: str) -> Optional[Firewall]:
        """
        Obtener un firewall por nombre.
        
        Args:
            name: Nombre del firewall
            
        Returns:
            Firewall o None si no se encuentra
        """
        firewalls = self.list(name=name)
        if firewalls.firewalls:
            return firewalls.firewalls[0]
        return None

    def list_all(self) -> List[Firewall]:
        """
        Listar todos los firewalls (sin paginación).
        
        Returns:
            List[Firewall]: Todos los firewalls
        """
        all_firewalls = []
        page = 1
        
        while True:
            response = self.list(page=page, per_page=50)
            all_firewalls.extend(response.firewalls)
            
            if not response.meta or not response.meta.pagination or not response.meta.pagination.next_page:
                break
            
            page = response.meta.pagination.next_page
        
        return all_firewalls

    def create(self, request: CreateFirewallRequest) -> Firewall:
        """
        Crear un firewall.
        
        Args:
            request: Request con los datos del firewall
            
        Returns:
            Firewall: Firewall creado
        """
        self._check_safe_mode("create_firewall")
        
        firewall_data = request.model_dump(exclude_unset=True)
        data = self.client._post("firewalls", json_data={"firewall": firewall_data})
        return Firewall(**data["firewall"])

    def update(
        self,
        firewall_id: int,
        name: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None,
        rules: Optional[List[Dict[str, Any]]] = None,
    ) -> Firewall:
        """
        Actualizar un firewall.
        
        Args:
            firewall_id: ID del firewall
            name: Nuevo nombre
            labels: Nuevas etiquetas
            rules: Nuevas reglas
            
        Returns:
            Firewall: Firewall actualizado
        """
        self._check_safe_mode("update_firewall")
        
        payload = {}
        if name:
            payload["name"] = name
        if labels:
            payload["labels"] = labels
        if rules:
            payload["rules"] = rules
        
        data = self.client._put(f"firewalls/{firewall_id}", json_data={"firewall": payload})
        return Firewall(**data["firewall"])

    def delete(self, firewall_id: int) -> None:
        """
        Eliminar un firewall.
        
        Args:
            firewall_id: ID del firewall
        """
        self._check_safe_mode("delete_firewall")
        
        self.client._delete(f"firewalls/{firewall_id}")

    def apply_to_resources(
        self,
        firewall_id: int,
        resources: List[Dict[str, Any]],
    ) -> Action:
        """
        Aplicar firewall a recursos.
        
        Args:
            firewall_id: ID del firewall
            resources: Lista de recursos (servidores, etc.)
            
        Returns:
            Action: Acción de aplicación
        """
        self._check_safe_mode("apply_firewall")
        
        payload = {"resources": resources}
        data = self.client._post(
            f"firewalls/{firewall_id}/actions/apply_to_resources",
            json_data=payload
        )
        return Action(**data["action"])

    def remove_from_resources(
        self,
        firewall_id: int,
        resources: List[Dict[str, Any]],
    ) -> Action:
        """
        Remover firewall de recursos.
        
        Args:
            firewall_id: ID del firewall
            resources: Lista de recursos
            
        Returns:
            Action: Acción de remoción
        """
        self._check_safe_mode("remove_firewall")
        
        payload = {"resources": resources}
        data = self.client._post(
            f"firewalls/{firewall_id}/actions/remove_from_resources",
            json_data=payload
        )
        return Action(**data["action"])

    def set_rules(
        self,
        firewall_id: int,
        rules: List[Dict[str, Any]],
    ) -> Action:
        """
        Establecer reglas de firewall.
        
        Args:
            firewall_id: ID del firewall
            rules: Lista de reglas
            
        Returns:
            Action: Acción de configuración
        """
        self._check_safe_mode("set_firewall_rules")
        
        payload = {"rules": rules}
        data = self.client._post(
            f"firewalls/{firewall_id}/actions/set_rules",
            json_data=payload
        )
        return Action(**data["action"])

    def change_protection(self, firewall_id: int, delete: bool = True) -> Action:
        """
        Cambiar la protección de eliminación de un firewall.
        
        Args:
            firewall_id: ID del firewall
            delete: Si se debe proteger contra eliminación
            
        Returns:
            Action: Acción de cambio de protección
        """
        self._check_safe_mode("change_protection")
        
        data = self.client._post(
            f"firewalls/{firewall_id}/actions/change_protection",
            json_data={"delete": delete}
        )
        return Action(**data["action"])

    def get_actions(self, firewall_id: int, page: int = 1, per_page: int = 25) -> ActionListResponse:
        """
        Obtener acciones de un firewall.
        
        Args:
            firewall_id: ID del firewall
            page: Número de página
            per_page: Resultados por página
            
        Returns:
            ActionListResponse: Lista de acciones
        """
        data = self.client._get(f"firewalls/{firewall_id}/actions", params={"page": page, "per_page": per_page})
        return ActionListResponse(**data)
