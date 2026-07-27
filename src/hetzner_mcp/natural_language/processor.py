"""
Procesador de Lenguaje Natural para Hetzner MCP

Este módulo permite convertir comandos en español a acciones en la API de Hetzner.

Sigue los principios NUPP:
- Open: Procesamiento abierto y extensible
- Minimalist: Lógica simple y efectiva
- Modular: Handlers separados para cada tipo de recurso
"""

import re
from typing import Any, Dict, List, Optional, Tuple, Union

from hetzner_mcp.core.client import HetznerClient
from hetzner_mcp.core.models import Server, Volume, Network, Firewall, Action
from hetzner_mcp.natural_language.intents import (
    ServerIntentHandler,
    VolumeIntentHandler,
    NetworkIntentHandler,
    FirewallIntentHandler,
    BackupIntentHandler,
    MonitoringIntentHandler,
    AutomationIntentHandler,
)


class NaturalLanguageProcessor:
    """
    Procesador de lenguaje natural para interactuar con Hetzner Cloud.
    
    Este procesador analiza comandos en español y los convierte en acciones
    concretas sobre la API de Hetzner Cloud.
    
    Ejemplo de uso:
        client = HetznerClient()
        nlp = NaturalLanguageProcessor(client)
        
        # Procesar un comando
        result = nlp.process("Crear un servidor con Ubuntu 22.04 en Nuremberg")
        print(result)
        
        # Procesar una pregunta
        result = nlp.process("¿Cuántos servidores tengo?")
        print(result)
    """

    def __init__(self, client: HetznerClient):
        """
        Inicializar el procesador de lenguaje natural.
        
        Args:
            client: Cliente de Hetzner
        """
        self.client = client
        self.intent_handlers = {
            "server": ServerIntentHandler(client),
            "servidor": ServerIntentHandler(client),
            "volume": VolumeIntentHandler(client),
            "volumen": VolumeIntentHandler(client),
            "network": NetworkIntentHandler(client),
            "red": NetworkIntentHandler(client),
            "firewall": FirewallIntentHandler(client),
            "cortafuegos": FirewallIntentHandler(client),
            "backup": BackupIntentHandler(client),
            "copia": BackupIntentHandler(client),
            "monitor": MonitoringIntentHandler(client),
            "monitoreo": MonitoringIntentHandler(client),
            "automation": AutomationIntentHandler(client),
            "automatizacion": AutomationIntentHandler(client),
        }
        
        # Patrones para extraer parámetros
        self.param_patterns = {
            "server_name": r"(?:nombre|llamado|con nombre|'|\")([a-zA-Z0-9-]+)(?:'|\"|$)",
            "server_type": r"(?:tipo|modelo|plan)[:\s]+([a-zA-Z0-9-]+)",
            "location": r"(?:en|ubicación|localización|datacenter|dc)[:\s]+([a-zA-Z0-9-]+)",
            "image": r"(?:imagen|sistema operativo|os|SO)[:\s]+([a-zA-Z0-9-.]+)",
            "size": r"(?:tamaño|size|GB|gb)[:\s]+(\d+)",
            "count": r"(\d+)",
            "ip_address": r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})",
            "label": r"(?:etiqueta|label|tag)[:\s]+([a-zA-Z0-9-]+)",
            "time": r"(?:durante|por|duración)[:\s]+(\d+)\s*(?:minutos|horas|días|min|h|d)",
        }

    def _normalize_text(self, text: str) -> str:
        """Normalizar el texto: minúsculas, sin acentos, etc."""
        import unicodedata
        
        # Convertir a minúsculas
        text = text.lower()
        
        # Remover acentos
        text = unicodedata.normalize('NFD', text)
        text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
        
        # Remover caracteres especiales (excepto números y letras)
        text = re.sub(r"[^a-z0-9\s:.,;¿?¡!-]", " ", text)
        
        # Remover espacios múltiples
        text = re.sub(r"\s+", " ", text).strip()
        
        return text

    def _extract_intent(self, text: str) -> Tuple[str, str]:
        """
        Extraer la intención principal del texto.
        
        Args:
            text: Texto normalizado
            
        Returns:
            Tuple[intención, texto_restante]
        """
        # Patrones de intenciones
        intent_patterns = [
            # Crear
            (r"(?:crear|nuevo|construir|desplegar|provisionar|hacer)", "create"),
            # Listar/Obtener
            (r"(?:listar|mostrar|ver|obtener|consultar|cuantos|cuantas|qué|que|cuál|cuales)", "list"),
            # Eliminar
            (r"(?:eliminar|borrar|remover|quitar|destruir|deshacerse de)", "delete"),
            # Actualizar/Modificar
            (r"(?:actualizar|modificar|cambiar|editar|renombrar|actualiza)", "update"),
            # Iniciar
            (r"(?:iniciar|encender|arrancar|prender|start|power on|poweron)", "start"),
            # Parar
            (r"(?:parar|detener|apagar|stop|power off|poweroff|shutdown)", "stop"),
            # Reiniciar
            (r"(?:reiniciar|rebootear|reboot|restart|reinicar)", "reboot"),
            # Backup
            (r"(?:backup|copia de seguridad|respaldo|guardar|salvar)", "backup"),
            # Restaurar
            (r"(?:restaurar|recuperar|restore|volver)", "restore"),
            # Conectar
            (r"(?:conectar|adjuntar|attach|asociar|vincular)", "attach"),
            # Desconectar
            (r"(?:desconectar|desadjuntar|detach|desasociar|desvincular)", "detach"),
            # Configurar
            (r"(?:configurar|ajustar|setear|pon|pone|configura)", "configure"),
            # Monitorear
            (r"(?:monitorear|chequear|revisar|verificar|check|status|estado)", "monitor"),
            # Automatizar
            (r"(?:automatizar|programar|agendar|schedule|automatico)", "automate"),
            # Buscar
            (r"(?:buscar|encontrar|localizar|find|search)", "search"),
            # Filtrar
            (r"(?:filtrar|filtrado|filter)", "filter"),
            # Ordenar
            (r"(?:ordenar|sort|organizar)", "sort"),
        ]
        
        for pattern, intent in intent_patterns:
            if re.search(pattern, text):
                # Remover el patrón del texto
                remaining = re.sub(pattern, "", text).strip()
                return intent, remaining
        
        # Si no se encuentra intención, asumir "list"
        return "list", text

    def _extract_resource_type(self, text: str) -> str:
        """Extraer el tipo de recurso del texto."""
        resource_patterns = [
            (r"(?:servidor|server|vps|maquina virtual|vm|instancia)", "server"),
            (r"(?:volumen|volume|disco|storage|almacenamiento)", "volume"),
            (r"(?:red|network|subred|subnet|lan|vlan)", "network"),
            (r"(?:firewall|cortafuegos|regla de firewall|reglas de firewall)", "firewall"),
            (r"(?:backup|copia|respaldo|snapshot|imagen|image)", "backup"),
            (r"(?:ip|direccion ip|dirección ip|ip flotante|floating ip)", "ip"),
            (r"(?:load balancer|balanceador|balanceador de carga)", "load_balancer"),
            (r"(?:ssh|clave ssh|llave ssh|key)", "ssh_key"),
            (r"(?:certificado|certificate|ssl|tls)", "certificate"),
            (r"(?:accion|action|tarea|operacion)", "action"),
        ]
        
        for pattern, resource in resource_patterns:
            if re.search(pattern, text):
                return resource
        
        # Por defecto, asumir servidor
        return "server"

    def _extract_parameters(self, text: str) -> Dict[str, Any]:
        """Extraer parámetros del texto."""
        params = {}
        
        # Extraer nombre
        name_match = re.search(r"(?:nombre|llamado|con nombre|'|\")([a-zA-Z0-9-]+)(?:'|\"|\s|$)", text)
        if name_match:
            params["name"] = name_match.group(1)
        
        # Extraer tipo de servidor
        type_match = re.search(r"(?:tipo|modelo|plan)[:\s]+([a-zA-Z0-9-]+)", text)
        if type_match:
            params["server_type"] = type_match.group(1)
        
        # Extraer ubicación
        location_match = re.search(r"(?:en|ubicación|localización|datacenter|dc)[:\s]+([a-zA-Z0-9-]+)", text)
        if location_match:
            params["location"] = location_match.group(1)
        
        # Extraer imagen
        image_match = re.search(r"(?:imagen|sistema operativo|os|SO)[:\s]+([a-zA-Z0-9-.]+)", text)
        if image_match:
            params["image"] = image_match.group(1)
        
        # Extraer tamaño
        size_match = re.search(r"(?:tamaño|size|GB|gb|gigas)[:\s]+(\d+)", text)
        if size_match:
            params["size"] = int(size_match.group(1))
        
        # Extraer cantidad
        count_match = re.search(r"(\d+)\s+(?:servidores|volúmenes|redes|servidor|volumen|red)", text)
        if count_match:
            params["count"] = int(count_match.group(1))
        
        # Extraer IP
        ip_match = re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", text)
        if ip_match:
            params["ip"] = ip_match.group(1)
        
        # Extraer etiqueta
        label_match = re.search(r"(?:etiqueta|label|tag)[:\s]+([a-zA-Z0-9-]+)", text)
        if label_match:
            params["label"] = label_match.group(1)
        
        # Extraer tiempo/duración
        time_match = re.search(r"(?:durante|por|duración)[:\s]+(\d+)\s*(?:minutos|horas|días|min|h|d)", text)
        if time_match:
            params["time"] = int(time_match.group(1))
        
        # Extraer IDs numéricos
        id_matches = re.findall(r"(?:id|ID|número|num)[:\s]+(\d+)", text)
        if id_matches:
            params["ids"] = [int(id) for id in id_matches]
        
        return params

    def _get_handler(self, resource_type: str) -> Any:
        """Obtener el handler adecuado para el tipo de recurso."""
        return self.intent_handlers.get(resource_type, ServerIntentHandler(self.client))

    def process(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Procesar un comando en español.
        
        Args:
            text: Texto del comando en español
            context: Contexto adicional (opcional)
            
        Returns:
            Dict con el resultado del procesamiento
        """
        # Normalizar el texto
        normalized = self._normalize_text(text)
        
        # Extraer intención y tipo de recurso
        intent, remaining = self._extract_intent(normalized)
        resource_type = self._extract_resource_type(remaining)
        
        # Extraer parámetros
        params = self._extract_parameters(normalized)
        
        # Obtener el handler adecuado
        handler = self._get_handler(resource_type)
        
        # Procesar según la intención
        try:
            if intent == "create":
                result = handler.handle_create(remaining, params, context)
            elif intent == "list":
                result = handler.handle_list(remaining, params, context)
            elif intent == "delete":
                result = handler.handle_delete(remaining, params, context)
            elif intent == "update":
                result = handler.handle_update(remaining, params, context)
            elif intent == "start":
                result = handler.handle_start(remaining, params, context)
            elif intent == "stop":
                result = handler.handle_stop(remaining, params, context)
            elif intent == "reboot":
                result = handler.handle_reboot(remaining, params, context)
            elif intent == "backup":
                result = handler.handle_backup(remaining, params, context)
            elif intent == "restore":
                result = handler.handle_restore(remaining, params, context)
            elif intent == "attach":
                result = handler.handle_attach(remaining, params, context)
            elif intent == "detach":
                result = handler.handle_detach(remaining, params, context)
            elif intent == "configure":
                result = handler.handle_configure(remaining, params, context)
            elif intent == "monitor":
                result = handler.handle_monitor(remaining, params, context)
            elif intent == "automate":
                result = handler.handle_automate(remaining, params, context)
            elif intent == "search":
                result = handler.handle_search(remaining, params, context)
            elif intent == "filter":
                result = handler.handle_filter(remaining, params, context)
            elif intent == "sort":
                result = handler.handle_sort(remaining, params, context)
            else:
                result = handler.handle_unknown(remaining, params, context)
        except Exception as e:
            result = {
                "success": False,
                "error": str(e),
                "intent": intent,
                "resource_type": resource_type,
                "params": params,
            }
        
        # Añadir metadatos al resultado
        result["metadata"] = {
            "original_text": text,
            "normalized_text": normalized,
            "intent": intent,
            "resource_type": resource_type,
            "extracted_params": params,
        }
        
        return result

    def process_batch(self, commands: List[str]) -> List[Dict[str, Any]]:
        """
        Procesar múltiples comandos.
        
        Args:
            commands: Lista de comandos en español
            
        Returns:
            Lista de resultados
        """
        results = []
        for cmd in commands:
            results.append(self.process(cmd))
        return results

    def chat(self, message: str, history: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Modo chat interactivo.
        
        Args:
            message: Mensaje del usuario
            history: Historial de la conversación
            
        Returns:
            Respuesta en formato de chat
        """
        # Procesar el mensaje
        result = self.process(message)
        
        # Formatear la respuesta
        response = {
            "user_message": message,
            "bot_response": self._format_response(result),
            "result": result,
        }
        
        if history:
            response["history"] = history + [response]
        
        return response

    def _format_response(self, result: Dict[str, Any]) -> str:
        """Formatear el resultado como una respuesta legible."""
        if result.get("success") is False:
            return f"❌ Error: {result.get('error', 'Error desconocido')}"
        
        intent = result.get("metadata", {}).get("intent", "unknown")
        resource = result.get("metadata", {}).get("resource_type", "servidor")
        
        if intent == "list":
            count = len(result.get("data", []))
            return f"📋 Encontré {count} {resource}(es)"
        elif intent == "create":
            name = result.get("data", {}).get("name", "el recurso")
            return f"✅ {resource.capitalize()} '{name}' creado exitosamente"
        elif intent == "delete":
            name = result.get("data", {}).get("name", "el recurso")
            return f"🗑️ {resource.capitalize()} '{name}' eliminado"
        elif intent == "start":
            name = result.get("data", {}).get("name", "el servidor")
            return f"▶️ {name} iniciado"
        elif intent == "stop":
            name = result.get("data", {}).get("name", "el servidor")
            return f"⏹️ {name} detenido"
        elif intent == "reboot":
            name = result.get("data", {}).get("name", "el servidor")
            return f"🔄 {name} reiniciado"
        elif intent == "backup":
            name = result.get("data", {}).get("name", "el servidor")
            return f"💾 Backup creado para {name}"
        else:
            return f"✅ Operación completada: {intent} en {resource}"

    def get_suggestions(self, partial_text: str) -> List[str]:
        """
        Obtener sugerencias de autocompletado.
        
        Args:
            partial_text: Texto parcial del usuario
            
        Returns:
            Lista de sugerencias
        """
        suggestions = []
        
        # Sugerencias de intenciones
        intent_suggestions = [
            "crear un servidor",
            "listar servidores",
            "eliminar servidor",
            "iniciar servidor",
            "parar servidor",
            "reiniciar servidor",
            "crear volumen",
            "hacer backup",
            "configurar firewall",
            "monitorear servidores",
        ]
        
        # Filtrar sugerencias que empiezan con el texto parcial
        for suggestion in intent_suggestions:
            if suggestion.startswith(partial_text.lower()):
                suggestions.append(suggestion)
        
        return suggestions[:5]  # Retornar máximo 5 sugerencias
