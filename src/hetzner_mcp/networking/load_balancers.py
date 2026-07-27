"""
API de Load Balancers de Hetzner Cloud
"""

from typing import Any, Dict, List, Optional

from hetzner_mcp.core.config import get_settings
from hetzner_mcp.core.exceptions import HetznerSafeModeError
from hetzner_mcp.core.models import (
    Action,
    ActionListResponse,
    CreateLoadBalancerRequest,
    LoadBalancer,
    LoadBalancerListResponse,
)


class LoadBalancerAPI:
    """API para gestionar load balancers de Hetzner Cloud."""

    def __init__(self, client: Any):
        """
        Inicializar la API de load balancers.
        
        Args:
            client: Instancia del cliente principal de Hetzner
        """
        self.client = client
        self.safe_mode = get_settings().safe_mode

    def _check_safe_mode(self, operation: str) -> None:
        """Verificar si la operación está permitida en modo seguro."""
        write_operations = ["create", "update", "delete", "add", "remove", "change", "attach", "detach"]
        if self.safe_mode and any(op in operation.lower() for op in write_operations):
            raise HetznerSafeModeError(operation)

    def list(
        self,
        name: Optional[str] = None,
        label_selector: Optional[str] = None,
        page: int = 1,
        per_page: int = get_settings().page_size,
    ) -> LoadBalancerListResponse:
        """
        Listar load balancers.
        
        Args:
            name: Filtrar por nombre
            label_selector: Filtrar por selector de etiquetas
            page: Número de página
            per_page: Resultados por página
            
        Returns:
            LoadBalancerListResponse: Lista de load balancers con paginación
        """
        params = {
            "page": page,
            "per_page": per_page,
        }
        if name:
            params["name"] = name
        if label_selector:
            params["label_selector"] = label_selector
        
        data = self.client._get("load_balancers", params=params)
        return LoadBalancerListResponse(**data)

    def get(self, lb_id: int) -> LoadBalancer:
        """
        Obtener un load balancer por ID.
        
        Args:
            lb_id: ID del load balancer
            
        Returns:
            LoadBalancer: Objeto load balancer
        """
        data = self.client._get(f"load_balancers/{lb_id}")
        return LoadBalancer(**data["load_balancer"])

    def get_by_name(self, name: str) -> Optional[LoadBalancer]:
        """
        Obtener un load balancer por nombre.
        
        Args:
            name: Nombre del load balancer
            
        Returns:
            LoadBalancer o None si no se encuentra
        """
        lbs = self.list(name=name)
        if lbs.load_balancers:
            return lbs.load_balancers[0]
        return None

    def list_all(self) -> List[LoadBalancer]:
        """
        Listar todos los load balancers (sin paginación).
        
        Returns:
            List[LoadBalancer]: Todos los load balancers
        """
        all_lbs = []
        page = 1
        
        while True:
            response = self.list(page=page, per_page=50)
            all_lbs.extend(response.load_balancers)
            
            if not response.meta or not response.meta.pagination or not response.meta.pagination.next_page:
                break
            
            page = response.meta.pagination.next_page
        
        return all_lbs

    def create(self, request: CreateLoadBalancerRequest) -> LoadBalancer:
        """
        Crear un load balancer.
        
        Args:
            request: Request con los datos del load balancer
            
        Returns:
            LoadBalancer: Load balancer creado
        """
        self._check_safe_mode("create_load_balancer")
        
        lb_data = request.model_dump(exclude_unset=True)
        data = self.client._post("load_balancers", json_data={"load_balancer": lb_data})
        return LoadBalancer(**data["load_balancer"])

    def update(
        self,
        lb_id: int,
        name: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None,
    ) -> LoadBalancer:
        """
        Actualizar un load balancer.
        
        Args:
            lb_id: ID del load balancer
            name: Nuevo nombre
            labels: Nuevas etiquetas
            
        Returns:
            LoadBalancer: Load balancer actualizado
        """
        self._check_safe_mode("update_load_balancer")
        
        payload = {}
        if name:
            payload["name"] = name
        if labels:
            payload["labels"] = labels
        
        data = self.client._put(f"load_balancers/{lb_id}", json_data={"load_balancer": payload})
        return LoadBalancer(**data["load_balancer"])

    def delete(self, lb_id: int) -> None:
        """
        Eliminar un load balancer.
        
        Args:
            lb_id: ID del load balancer
        """
        self._check_safe_mode("delete_load_balancer")
        
        self.client._delete(f"load_balancers/{lb_id}")

    def add_service(
        self,
        lb_id: int,
        protocol: str,
        listen_port: int,
        destination_port: int,
        **kwargs,
    ) -> Action:
        """
        Añadir un servicio a un load balancer.
        
        Args:
            lb_id: ID del load balancer
            protocol: Protocolo (http, https, tcp)
            listen_port: Puerto de escucha
            destination_port: Puerto de destino
            **kwargs: Argumentos adicionales
            
        Returns:
            Action: Acción de adición
        """
        self._check_safe_mode("add_service")
        
        payload = {
            "protocol": protocol,
            "listen_port": listen_port,
            "destination_port": destination_port,
            **kwargs
        }
        data = self.client._post(f"load_balancers/{lb_id}/actions/add_service", json_data=payload)
        return Action(**data["action"])

    def update_service(
        self,
        lb_id: int,
        service_id: int,
        **kwargs,
    ) -> Action:
        """
        Actualizar un servicio de load balancer.
        
        Args:
            lb_id: ID del load balancer
            service_id: ID del servicio
            **kwargs: Argumentos a actualizar
            
        Returns:
            Action: Acción de actualización
        """
        self._check_safe_mode("update_service")
        
        data = self.client._post(
            f"load_balancers/{lb_id}/actions/update_service",
            json_data={"service_id": service_id, **kwargs}
        )
        return Action(**data["action"])

    def delete_service(self, lb_id: int, service_id: int) -> Action:
        """
        Eliminar un servicio de load balancer.
        
        Args:
            lb_id: ID del load balancer
            service_id: ID del servicio
            
        Returns:
            Action: Acción de eliminación
        """
        self._check_safe_mode("delete_service")
        
        data = self.client._post(
            f"load_balancers/{lb_id}/actions/delete_service",
            json_data={"service_id": service_id}
        )
        return Action(**data["action"])

    def add_target(
        self,
        lb_id: int,
        target_type: str,
        target_id: int,
        **kwargs,
    ) -> Action:
        """
        Añadir un target a un load balancer.
        
        Args:
            lb_id: ID del load balancer
            target_type: Tipo de target (server, ip)
            target_id: ID del target
            **kwargs: Argumentos adicionales
            
        Returns:
            Action: Acción de adición
        """
        self._check_safe_mode("add_target")
        
        payload = {
            "type": target_type,
            f"{target_type}_id": target_id,
            **kwargs
        }
        data = self.client._post(f"load_balancers/{lb_id}/actions/add_target", json_data=payload)
        return Action(**data["action"])

    def remove_target(self, lb_id: int, target_id: int) -> Action:
        """
        Remover un target de un load balancer.
        
        Args:
            lb_id: ID del load balancer
            target_id: ID del target
            
        Returns:
            Action: Acción de remoción
        """
        self._check_safe_mode("remove_target")
        
        data = self.client._post(
            f"load_balancers/{lb_id}/actions/remove_target",
            json_data={"target_id": target_id}
        )
        return Action(**data["action"])

    def change_algorithm(
        self,
        lb_id: int,
        algorithm_type: str,
    ) -> Action:
        """
        Cambiar el algoritmo de un load balancer.
        
        Args:
            lb_id: ID del load balancer
            algorithm_type: Tipo de algoritmo (round_robin, least_connections, source_ip_hash)
            
        Returns:
            Action: Acción de cambio
        """
        self._check_safe_mode("change_algorithm")
        
        data = self.client._post(
            f"load_balancers/{lb_id}/actions/change_algorithm",
            json_data={"algorithm": {"type": algorithm_type}}
        )
        return Action(**data["action"])

    def change_type(
        self,
        lb_id: int,
        lb_type: Union[str, int],
    ) -> Action:
        """
        Cambiar el tipo de load balancer.
        
        Args:
            lb_id: ID del load balancer
            lb_type: Tipo de load balancer
            
        Returns:
            Action: Acción de cambio
        """
        self._check_safe_mode("change_type")
        
        data = self.client._post(
            f"load_balancers/{lb_id}/actions/change_type",
            json_data={"load_balancer_type": lb_type}
        )
        return Action(**data["action"])

    def enable_public_interface(self, lb_id: int) -> Action:
        """
        Habilitar interfaz pública.
        
        Args:
            lb_id: ID del load balancer
            
        Returns:
            Action: Acción de habilitación
        """
        self._check_safe_mode("enable_public_interface")
        
        data = self.client._post(f"load_balancers/{lb_id}/actions/enable_public_interface")
        return Action(**data["action"])

    def disable_public_interface(self, lb_id: int) -> Action:
        """
        Deshabilitar interfaz pública.
        
        Args:
            lb_id: ID del load balancer
            
        Returns:
            Action: Acción de deshabilitación
        """
        self._check_safe_mode("disable_public_interface")
        
        data = self.client._post(f"load_balancers/{lb_id}/actions/disable_public_interface")
        return Action(**data["action"])

    def attach_to_network(self, lb_id: int, network_id: int, ip: Optional[str] = None) -> Action:
        """
        Conectar a una red.
        
        Args:
            lb_id: ID del load balancer
            network_id: ID de la red
            ip: IP opcional
            
        Returns:
            Action: Acción de conexión
        """
        self._check_safe_mode("attach_to_network")
        
        payload = {"network": network_id}
        if ip:
            payload["ip"] = ip
        
        data = self.client._post(f"load_balancers/{lb_id}/actions/attach_to_network", json_data=payload)
        return Action(**data["action"])

    def detach_from_network(self, lb_id: int, network_id: int) -> Action:
        """
        Desconectar de una red.
        
        Args:
            lb_id: ID del load balancer
            network_id: ID de la red
            
        Returns:
            Action: Acción de desconexión
        """
        self._check_safe_mode("detach_from_network")
        
        data = self.client._post(
            f"load_balancers/{lb_id}/actions/detach_from_network",
            json_data={"network": network_id}
        )
        return Action(**data["action"])

    def change_protection(self, lb_id: int, delete: bool = True) -> Action:
        """
        Cambiar la protección de eliminación.
        
        Args:
            lb_id: ID del load balancer
            delete: Si se debe proteger contra eliminación
            
        Returns:
            Action: Acción de cambio de protección
        """
        self._check_safe_mode("change_protection")
        
        data = self.client._post(
            f"load_balancers/{lb_id}/actions/change_protection",
            json_data={"delete": delete}
        )
        return Action(**data["action"])

    def change_dns_ptr(self, lb_id: int, dns_ptr: str) -> Action:
        """
        Cambiar el DNS PTR.
        
        Args:
            lb_id: ID del load balancer
            dns_ptr: DNS PTR
            
        Returns:
            Action: Acción de cambio
        """
        self._check_safe_mode("change_dns_ptr")
        
        data = self.client._post(
            f"load_balancers/{lb_id}/actions/change_dns_ptr",
            json_data={"dns_ptr": dns_ptr}
        )
        return Action(**data["action"])

    def get_actions(self, lb_id: int, page: int = 1, per_page: int = 25) -> ActionListResponse:
        """
        Obtener acciones de un load balancer.
        
        Args:
            lb_id: ID del load balancer
            page: Número de página
            per_page: Resultados por página
            
        Returns:
            ActionListResponse: Lista de acciones
        """
        data = self.client._get(f"load_balancers/{lb_id}/actions", params={"page": page, "per_page": per_page})
        return ActionListResponse(**data)

    def get_metrics(
        self,
        lb_id: int,
        type: str,
        start: Optional[str] = None,
        end: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Obtener métricas de un load balancer.
        
        Args:
            lb_id: ID del load balancer
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
        
        data = self.client._get(f"load_balancers/{lb_id}/metrics", params=params)
        return data
