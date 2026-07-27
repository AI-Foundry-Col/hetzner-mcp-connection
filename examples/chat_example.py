#!/usr/bin/env python3
"""
Ejemplo de uso del procesador de lenguaje natural

Este ejemplo muestra cómo usar el procesador de lenguaje natural
para interactuar con Hetzner Cloud en español.
"""

from hetzner_mcp import HetznerClient
from hetzner_mcp.natural_language import NaturalLanguageProcessor


def main():
    """Ejemplo de uso del procesador de lenguaje natural."""
    
    # Inicializar el cliente y el procesador
    print("🔹 Inicializando cliente y procesador de lenguaje natural...")
    client = HetznerClient()
    nlp = NaturalLanguageProcessor(client)
    
    # Ejemplos de comandos en español
    commands = [
        "Listar todos mis servidores",
        "¿Cuántos servidores tengo?",
        "Crear un servidor con Ubuntu 22.04 en Nuremberg",
        "Iniciar el servidor con ID 12345",
        "Parar todos los servidores con etiqueta 'test'",
        "Hacer backup de todos mis servidores",
        "Crear un volumen de 100GB en Frankfurt",
        "¿Cuál es mi servidor más costoso?",
        "Monitorear el estado de todos los servidores",
    ]
    
    print("\n💬 Procesando comandos en español:\n")
    
    for i, command in enumerate(commands, 1):
        print(f"{i}. Comando: [bold cyan]{command}[/bold cyan]")
        
        try:
            result = nlp.process(command)
            
            # Mostrar resultado
            if result.get("success"):
                print(f"   ✅ Resultado: {result.get('message', 'Operación exitosa')}")
                
                # Mostrar datos adicionales si existen
                if "data" in result and isinstance(result["data"], list):
                    print(f"   📊 Elementos encontrados: {len(result['data'])}")
                elif "data" in result and isinstance(result["data"], dict):
                    if "name" in result["data"]:
                        print(f"   📝 Nombre: {result['data']['name']}")
                    if "id" in result["data"]:
                        print(f"   🆔 ID: {result['data']['id']}")
            else:
                print(f"   ❌ Error: {result.get('error', 'Error desconocido')}")
            
            # Mostrar metadatos
            metadata = result.get("metadata", {})
            print(f"   📋 Intención: {metadata.get('intent', 'desconocida')}")
            print(f"   🏷️  Tipo de recurso: {metadata.get('resource_type', 'desconocido')}")
            
        except Exception as e:
            print(f"   ❌ Excepción: {e}")
        
        print()
    
    # Ejemplo de modo chat
    print("\n💬 Ejemplo de modo chat:\n")
    
    chat_commands = [
        "Hola, ¿qué servidores tengo?",
        "Crear un servidor llamado 'mi-web' con tipo cx21",
        "¿Cuál es la IP del servidor 'mi-web'?",
        "Apagar el servidor 'mi-web'",
    ]
    
    for command in chat_commands:
        result = nlp.chat(command)
        print(f"Usuario: {result['user_message']}")
        print(f"Bot: {result['bot_response']}")
        print()
    
    print("✅ Ejemplo de lenguaje natural completado!")


if __name__ == "__main__":
    # Configurar Rich para mejor visualización
    from rich.console import Console
    console = Console()
    
    # Reemplazar print con console.print para colores
    import builtins
    original_print = builtins.print
    
    def rich_print(*args, **kwargs):
        if args and isinstance(args[0], str):
            console.print(*args, **kwargs)
        else:
            original_print(*args, **kwargs)
    
    builtins.print = rich_print
    
    try:
        main()
    finally:
        builtins.print = original_print
