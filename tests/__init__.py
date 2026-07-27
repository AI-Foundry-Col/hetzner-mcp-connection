"""
Tests para Hetzner MCP Connection
"""

import os
import sys
from unittest.mock import Mock, patch

# Configurar entorno de testing
os.environ["HETZNER_API_TOKEN"] = "test_token"
os.environ["SAFE_MODE"] = "true"

# Mockear el cliente de Hetzner
sys.modules["hetzner_mcp.core.client"] = Mock()
sys.modules["hetzner_mcp.servers"] = Mock()
sys.modules["hetzner_mcp.networking"] = Mock()
sys.modules["hetzner_mcp.storage"] = Mock()
