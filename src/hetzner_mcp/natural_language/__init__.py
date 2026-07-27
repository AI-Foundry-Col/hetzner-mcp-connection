"""
Procesamiento de Lenguaje Natural para Hetzner MCP

Permite interactuar con Hetzner Cloud en español de manera natural.
"""

from hetzner_mcp.natural_language.processor import NaturalLanguageProcessor
from hetzner_mcp.natural_language.intents import (
    ServerIntentHandler,
    VolumeIntentHandler,
    NetworkIntentHandler,
    FirewallIntentHandler,
    BackupIntentHandler,
    MonitoringIntentHandler,
    AutomationIntentHandler,
)

__all__ = [
    "NaturalLanguageProcessor",
    "ServerIntentHandler",
    "VolumeIntentHandler",
    "NetworkIntentHandler",
    "FirewallIntentHandler",
    "BackupIntentHandler",
    "MonitoringIntentHandler",
    "AutomationIntentHandler",
]
