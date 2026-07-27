"""
Tests para el cliente de Hetzner
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from hetzner_mcp.core.client import HetznerClient
from hetzner_mcp.core.config import settings
from hetzner_mcp.core.exceptions import (
    HetznerAPIError,
    HetznerAuthenticationError,
    HetznerRateLimitError,
    HetznerSafeModeError,
)


@pytest.fixture
def mock_client():
    """Crear un cliente mock para testing."""
    with patch("hetzner_mcp.core.client.requests") as mock_requests:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"test": "data"}
        mock_requests.request.return_value = mock_response
        
        client = HetznerClient(api_token="test_token")
        yield client


class TestHetznerClient:
    """Tests para HetznerClient."""

    def test_init_with_token(self):
        """Test inicialización con token."""
        client = HetznerClient(api_token="test_token")
        assert client.api_token == "test_token"
        assert client.api_url == settings.hetzner_api_url

    def test_init_without_token_raises(self):
        """Test que falla sin token."""
        with patch.object(settings, "hetzner_api_token", ""):
            with pytest.raises(ValueError, match="Se requiere un token de API"):
                HetznerClient()

    def test_headers(self):
        """Test headers del cliente."""
        client = HetznerClient(api_token="test_token")
        assert "Authorization" in client.headers
        assert client.headers["Authorization"] == "Bearer test_token"
        assert client.headers["Content-Type"] == "application/json"

    def test_safe_mode_check(self):
        """Test verificación de modo seguro."""
        client = HetznerClient(api_token="test_token")
        client.safe_mode = True
        
        with pytest.raises(HetznerSafeModeError):
            client._check_safe_mode("delete_server")

    def test_protected_server_check(self):
        """Test verificación de servidor protegido."""
        client = HetznerClient(api_token="test_token")
        client.protected_servers = {123}
        
        with pytest.raises(HetznerSafeModeError):
            client._check_protected_server(123, "delete_server")

    @patch("hetzner_mcp.core.client.requests")
    def test_request_success(self, mock_requests):
        """Test request exitoso."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"server": {"id": 1, "name": "test"}}
        mock_requests.request.return_value = mock_response
        
        client = HetznerClient(api_token="test_token")
        result = client._request("GET", "servers")
        
        assert result == {"server": {"id": 1, "name": "test"}}

    @patch("hetzner_mcp.core.client.requests")
    def test_request_error(self, mock_requests):
        """Test request con error."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "error": {
                "code": "unauthorized",
                "message": "Invalid token"
            }
        }
        mock_requests.request.return_value = mock_response
        
        client = HetznerClient(api_token="test_token")
        
        with pytest.raises(HetznerAuthenticationError):
            client._request("GET", "servers")

    @patch("hetzner_mcp.core.client.requests")
    def test_request_timeout(self, mock_requests):
        """Test request con timeout."""
        mock_requests.request.side_effect = Exception("Timeout")
        
        client = HetznerClient(api_token="test_token")
        
        with pytest.raises(HetznerAPIError, match="Timeout"):
            client._request("GET", "servers")


class TestServerProperties:
    """Tests para propiedades de sub-clientes."""

    def test_servers_property(self):
        """Test propiedad servers."""
        client = HetznerClient(api_token="test_token")
        assert hasattr(client, "servers")

    def test_volumes_property(self):
        """Test propiedad volumes."""
        client = HetznerClient(api_token="test_token")
        assert hasattr(client, "volumes")

    def test_networks_property(self):
        """Test propiedad networks."""
        client = HetznerClient(api_token="test_token")
        assert hasattr(client, "networks")

    def test_firewalls_property(self):
        """Test propiedad firewalls."""
        client = HetznerClient(api_token="test_token")
        assert hasattr(client, "firewalls")
