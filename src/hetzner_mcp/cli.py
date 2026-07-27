"""
Interfaz de Línea de Comandos para Hetzner MCP Connection

Sigue los principios NUPP:
- Open: CLI abierta y extensible
- Minimalist: Comandos simples y directos
- Modular: Comandos organizados por recurso
"""

import json
import logging
import sys
from typing import Any, Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

from hetzner_mcp.core.client import HetznerClient
from hetzner_mcp.core.config import get_settings, reset_settings
from hetzner_mcp.natural_language.processor import NaturalLanguageProcessor

# Configurar logging
logging.basicConfig(
    level=getattr(logging, get_settings().log_level, logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configurar consola Rich
console = Console()


class CLIFormatter:
    """Formateador de salida para la CLI."""

    @staticmethod
    def format_server(server: dict, verbose: bool = False) -> str:
        """Formatear información de un servidor."""
        if verbose:
            table = Table(title=f"Servidor: {server.get('name', 'N/A')}", box=box.ROUNDED)
            table.add_column("Propiedad", style="cyan")
            table.add_column("Valor", style="green")
            
            table.add_row("ID", str(server.get("id", "N/A")))
            table.add_row("Nombre", server.get("name", "N/A"))
            table.add_row("Estado", server.get("status", "N/A"))
            table.add_row("Tipo", server.get("server_type", {}).get("name", "N/A"))
            table.add_row("Localización", server.get("datacenter", {}).get("name", "N/A"))
            table.add_row("IPv4", server.get("ipv4_address", "N/A"))
            table.add_row("IPv6", server.get("ipv6_address", "N/A"))
            table.add_row("Creado", server.get("created", "N/A"))
            
            return str(table)
        else:
            status_color = "green" if server.get("status") == "running" else "red"
            return f"[{status_color}]{server.get('name', 'N/A')}[/{status_color}] (ID: {server.get('id', 'N/A')}, Estado: {server.get('status', 'N/A')})"

    @staticmethod
    def format_server_list(servers: list, verbose: bool = False) -> str:
        """Formatear lista de servidores."""
        if not servers:
            return "No se encontraron servidores"
        
        if verbose:
            output = []
            for server in servers:
                output.append(CLIFormatter.format_server(server, True))
                output.append("")
            return "\n".join(output)
        else:
            table = Table(title="Servidores", box=box.ROUNDED)
            table.add_column("ID", style="cyan", width=8)
            table.add_column("Nombre", style="green", width=20)
            table.add_column("Estado", style="magenta", width=12)
            table.add_column("Tipo", style="blue", width=15)
            table.add_column("IPv4", style="yellow", width=15)
            
            for server in servers:
                status_color = "green" if server.get("status") == "running" else "red"
                table.add_row(
                    str(server.get("id", "N/A")),
                    server.get("name", "N/A"),
                    f"[{status_color}]{server.get('status', 'N/A')}[/{status_color}]",
                    server.get("server_type", {}).get("name", "N/A"),
                    server.get("ipv4_address", "N/A"),
                )
            
            return str(table)

    @staticmethod
    def format_volume(volume: dict, verbose: bool = False) -> str:
        """Formatear información de un volumen."""
        if verbose:
            table = Table(title=f"Volumen: {volume.get('name', 'N/A')}", box=box.ROUNDED)
            table.add_column("Propiedad", style="cyan")
            table.add_column("Valor", style="green")
            
            table.add_row("ID", str(volume.get("id", "N/A")))
            table.add_row("Nombre", volume.get("name", "N/A"))
            table.add_row("Tamaño", f"{volume.get('size', 0)} GB")
            table.add_row("Estado", volume.get("status", "N/A"))
            table.add_row("Localización", volume.get("location", {}).get("name", "N/A"))
            table.add_row("Servidor", volume.get("server", {}).get("name", "N/A"))
            
            return str(table)
        else:
            return f"{volume.get('name', 'N/A')} (ID: {volume.get('id', 'N/A')}, {volume.get('size', 0)} GB, Estado: {volume.get('status', 'N/A')})"

    @staticmethod
    def format_volume_list(volumes: list, verbose: bool = False) -> str:
        """Formatear lista de volúmenes."""
        if not volumes:
            return "No se encontraron volúmenes"
        
        if verbose:
            output = []
            for volume in volumes:
                output.append(CLIFormatter.format_volume(volume, True))
                output.append("")
            return "\n".join(output)
        else:
            table = Table(title="Volúmenes", box=box.ROUNDED)
            table.add_column("ID", style="cyan", width=8)
            table.add_column("Nombre", style="green", width=20)
            table.add_column("Tamaño", style="blue", width=10)
            table.add_column("Estado", style="magenta", width=12)
            
            for volume in volumes:
                table.add_row(
                    str(volume.get("id", "N/A")),
                    volume.get("name", "N/A"),
                    f"{volume.get('size', 0)} GB",
                    volume.get("status", "N/A"),
                )
            
            return str(table)

    @staticmethod
    def format_network(network: dict, verbose: bool = False) -> str:
        """Formatear información de una red."""
        if verbose:
            table = Table(title=f"Red: {network.get('name', 'N/A')}", box=box.ROUNDED)
            table.add_column("Propiedad", style="cyan")
            table.add_column("Valor", style="green")
            
            table.add_row("ID", str(network.get("id", "N/A")))
            table.add_row("Nombre", network.get("name", "N/A"))
            table.add_row("Rango IP", network.get("ip_range", "N/A"))
            table.add_row("Subredes", str(len(network.get("subnets", []))))
            table.add_row("Servidores", str(len(network.get("servers", []))))
            
            return str(table)
        else:
            return f"{network.get('name', 'N/A')} (ID: {network.get('id', 'N/A')}, Rango: {network.get('ip_range', 'N/A')})"

    @staticmethod
    def format_network_list(networks: list, verbose: bool = False) -> str:
        """Formatear lista de redes."""
        if not networks:
            return "No se encontraron redes"
        
        if verbose:
            output = []
            for network in networks:
                output.append(CLIFormatter.format_network(network, True))
                output.append("")
            return "\n".join(output)
        else:
            table = Table(title="Redes", box=box.ROUNDED)
            table.add_column("ID", style="cyan", width=8)
            table.add_column("Nombre", style="green", width=20)
            table.add_column("Rango IP", style="blue", width=15)
            
            for network in networks:
                table.add_row(
                    str(network.get("id", "N/A")),
                    network.get("name", "N/A"),
                    network.get("ip_range", "N/A"),
                )
            
            return str(table)

    @staticmethod
    def format_firewall(firewall: dict, verbose: bool = False) -> str:
        """Formatear información de un firewall."""
        if verbose:
            table = Table(title=f"Firewall: {firewall.get('name', 'N/A')}", box=box.ROUNDED)
            table.add_column("Propiedad", style="cyan")
            table.add_column("Valor", style="green")
            
            table.add_row("ID", str(firewall.get("id", "N/A")))
            table.add_row("Nombre", firewall.get("name", "N/A"))
            table.add_row("Reglas", str(len(firewall.get("rules", []))))
            table.add_row("Recursos", str(len(firewall.get("applied_to", []))))
            
            return str(table)
        else:
            return f"{firewall.get('name', 'N/A')} (ID: {firewall.get('id', 'N/A')}, Reglas: {len(firewall.get('rules', []))})"

    @staticmethod
    def format_firewall_list(firewalls: list, verbose: bool = False) -> str:
        """Formatear lista de firewalls."""
        if not firewalls:
            return "No se encontraron firewalls"
        
        if verbose:
            output = []
            for firewall in firewalls:
                output.append(CLIFormatter.format_firewall(firewall, True))
                output.append("")
            return "\n".join(output)
        else:
            table = Table(title="Firewalls", box=box.ROUNDED)
            table.add_column("ID", style="cyan", width=8)
            table.add_column("Nombre", style="green", width=20)
            table.add_column("Reglas", style="blue", width=10)
            
            for firewall in firewalls:
                table.add_row(
                    str(firewall.get("id", "N/A")),
                    firewall.get("name", "N/A"),
                    str(len(firewall.get("rules", []))),
                )
            
            return str(table)

    @staticmethod
    def format_action(action: dict) -> str:
        """Formatear información de una acción."""
        table = Table(title=f"Acción: {action.get('command', 'N/A')}", box=box.ROUNDED)
        table.add_column("Propiedad", style="cyan")
        table.add_column("Valor", style="green")
        
        table.add_row("ID", str(action.get("id", "N/A")))
        table.add_row("Comando", action.get("command", "N/A"))
        table.add_row("Estado", action.get("status", "N/A"))
        table.add_row("Progreso", f"{action.get('progress', 0)}%")
        table.add_row("Iniciada", action.get("started", "N/A"))
        if action.get("finished"):
            table.add_row("Finalizada", action.get("finished", "N/A"))
        
        return str(table)

    @staticmethod
    def format_result(result: dict) -> str:
        """Formatear resultado genérico."""
        if result.get("success") is False:
            return Panel(
                f"[red]❌ Error: {result.get('error', 'Error desconocido')}[/red]",
                title="Error",
                border_style="red",
            )
        
        action = result.get("metadata", {}).get("intent", "unknown")
        resource = result.get("metadata", {}).get("resource_type", "recurso")
        message = result.get("message", "Operación completada")
        
        return Panel(
            f"[green]✅ {message}[/green]",
            title=f"{action.capitalize()} - {resource}",
            border_style="green",
        )

    @staticmethod
    def format_json(data: Any) -> str:
        """Formatear datos como JSON."""
        return json.dumps(data, indent=2, ensure_ascii=False, default=str)


# =============================================================================
# Comandos Principales
# =============================================================================

@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Modo verboso")
@click.option("--json", "-j", is_flag=True, help="Salida en formato JSON")
@click.option("--config", "-c", help="Archivo de configuración")
def cli(verbose: bool, json_output: bool, config: Optional[str] = None):
    """
    Hetzner MCP Connection - CLI para gestionar Hetzner Cloud en español
    
    Ejemplos:
        hetzner-mcp servers list
        hetzner-mcp servers create --name mi-servidor --type cx21 --location nbg1
        hetzner-mcp chat "Crear un servidor con Ubuntu 22.04"
    """
    # Cargar configuración si se especifica
    if config:
        import os
        os.environ["HETZNER_API_TOKEN"] = ""  # Forzar recarga
        reset_settings()
        # TODO: Cargar configuración del archivo
    
    # Guardar estado global
    cli.ctx.obj = {"verbose": verbose, "json": json_output}


# =============================================================================
# Comandos de Servidores
# =============================================================================

@cli.group()
def servers():
    """Gestionar servidores de Hetzner Cloud."""
    pass


@servers.command()
@click.option("--name", "-n", help="Filtrar por nombre")
@click.option("--status", "-s", help="Filtrar por estado")
@click.option("--label", "-l", help="Filtrar por etiqueta")
@click.option("--all", "-a", is_flag=True, help="Mostrar todos los detalles")
def list(name: Optional[str], status: Optional[str], label: Optional[str], all: bool):
    """Listar servidores."""
    client = HetznerClient()
    
    try:
        servers = client.servers.list(
            name=name,
            status=status,
            label_selector=label,
        )
        
        if cli.ctx.obj.get("json"):
            click.echo(CLIFormatter.format_json(servers.model_dump()))
        else:
            output = CLIFormatter.format_server_list([s.model_dump() for s in servers.servers], all)
            console.print(output)
            
            # Mostrar información de paginación
            if servers.meta and servers.meta.pagination:
                pag = servers.meta.pagination
                console.print(f"\nPágina {pag.page} de {pag.last_page or 1}, Total: {pag.total_entries or 0}")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@servers.command()
@click.argument("server_id", type=int)
def get(server_id: int):
    """Obtener información de un servidor."""
    client = HetznerClient()
    
    try:
        server = client.servers.get(server_id)
        
        if cli.ctx.obj.get("json"):
            click.echo(CLIFormatter.format_json(server.model_dump()))
        else:
            console.print(CLIFormatter.format_server(server.model_dump(), True))
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@servers.command()
@click.option("--name", "-n", required=True, help="Nombre del servidor")
@click.option("--type", "-t", default="cx21", help="Tipo de servidor")
@click.option("--location", "-l", default="nbg1", help="Localización")
@click.option("--image", "-i", default="ubuntu-22.04", help="Imagen")
@click.option("--ssh-key", "-k", help="ID o nombre de clave SSH")
@click.option("--volume", "-v", help="ID o nombre de volumen")
@click.option("--network", help="ID o nombre de red")
@click.option("--user-data", help="User data para cloud-init")
@click.option("--no-start", is_flag=True, help="No iniciar después de crear")
def create(name: str, type: str, location: str, image: str, ssh_key: Optional[str], 
          volume: Optional[str], network: Optional[str], user_data: Optional[str], 
          no_start: bool):
    """Crear un servidor."""
    from hetzner_mcp.core.models import CreateServerRequest
    
    client = HetznerClient()
    
    try:
        # Preparar SSH keys
        ssh_keys = []
        if ssh_key:
            ssh_keys = [ssh_key]
        
        # Preparar volúmenes
        volumes = []
        if volume:
            volumes = [volume]
        
        # Preparar redes
        networks = []
        if network:
            networks = [network]
        
        request = CreateServerRequest(
            name=name,
            server_type=type,
            location=location,
            image=image,
            ssh_keys=ssh_keys,
            volumes=volumes,
            networks=networks,
            user_data=user_data,
            start_after_create=not no_start,
        )
        
        server = client.servers.create(request)
        
        if cli.ctx.obj.get("json"):
            click.echo(CLIFormatter.format_json(server.model_dump()))
        else:
            console.print(Panel(
                f"[green]✅ Servidor '{server.name}' creado con ID {server.id}[/green]",
                title="Servidor Creado",
                border_style="green",
            ))
            console.print(CLIFormatter.format_server(server.model_dump(), cli.ctx.obj.get("verbose", False)))
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@servers.command()
@click.argument("server_id", type=int)
@click.option("--name", "-n", help="Nuevo nombre")
@click.option("--label", "-l", multiple=True, help="Etiquetas (puede repetirse)")
def update(server_id: int, name: Optional[str], label: tuple):
    """Actualizar un servidor."""
    from hetzner_mcp.core.models import UpdateServerRequest
    
    client = HetznerClient()
    
    try:
        # Convertir etiquetas a dict
        labels = {}
        if label:
            for l in label:
                if "=" in l:
                    key, value = l.split("=", 1)
                    labels[key] = value
                else:
                    labels[l] = "true"
        
        request = UpdateServerRequest(
            name=name,
            labels=labels if labels else None,
        )
        
        server = client.servers.update(server_id, request)
        
        if cli.ctx.obj.get("json"):
            click.echo(CLIFormatter.format_json(server.model_dump()))
        else:
            console.print(Panel(
                f"[green]✅ Servidor '{server.name}' actualizado[/green]",
                title="Servidor Actualizado",
                border_style="green",
            ))
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@servers.command()
@click.argument("server_id", type=int)
@click.option("--force", "-f", is_flag=True, help="Forzar eliminación")
def delete(server_id: int, force: bool):
    """Eliminar un servidor."""
    client = HetznerClient()
    
    try:
        server = client.servers.get(server_id)
        
        if not force:
            click.confirm(
                f"¿Estás seguro de eliminar el servidor '{server.name}' (ID: {server.id})?",
                abort=True,
            )
        
        client.servers.delete(server_id)
        
        console.print(Panel(
            f"[green]✅ Servidor '{server.name}' eliminado[/green]",
            title="Servidor Eliminado",
            border_style="green",
        ))
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@servers.command()
@click.argument("server_id", type=int)
def start(server_id: int):
    """Iniciar un servidor."""
    client = HetznerClient()
    
    try:
        server = client.servers.get(server_id)
        action = client.servers.start(server_id)
        
        if cli.ctx.obj.get("json"):
            click.echo(CLIFormatter.format_json({
                "server": server.model_dump(),
                "action": action.model_dump(),
            }))
        else:
            console.print(Panel(
                f"[green]▶️ Servidor '{server.name}' está siendo iniciado[/green]",
                title="Servidor Iniciado",
                border_style="green",
            ))
            console.print(CLIFormatter.format_action(action.model_dump()))
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@servers.command()
@click.argument("server_id", type=int)
def stop(server_id: int):
    """Parar un servidor."""
    client = HetznerClient()
    
    try:
        server = client.servers.get(server_id)
        action = client.servers.stop(server_id)
        
        if cli.ctx.obj.get("json"):
            click.echo(CLIFormatter.format_json({
                "server": server.model_dump(),
                "action": action.model_dump(),
            }))
        else:
            console.print(Panel(
                f"[yellow]⏹️ Servidor '{server.name}' está siendo detenido[/yellow]",
                title="Servidor Detenido",
                border_style="yellow",
            ))
            console.print(CLIFormatter.format_action(action.model_dump()))
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@servers.command()
@click.argument("server_id", type=int)
def reboot(server_id: int):
    """Reiniciar un servidor."""
    client = HetznerClient()
    
    try:
        server = client.servers.get(server_id)
        action = client.servers.reboot(server_id)
        
        if cli.ctx.obj.get("json"):
            click.echo(CLIFormatter.format_json({
                "server": server.model_dump(),
                "action": action.model_dump(),
            }))
        else:
            console.print(Panel(
                f"[blue]🔄 Servidor '{server.name}' está siendo reiniciado[/blue]",
                title="Servidor Reiniciado",
                border_style="blue",
            ))
            console.print(CLIFormatter.format_action(action.model_dump()))
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@servers.command()
@click.argument("server_id", type=int)
def reset(server_id: int):
    """Resetear un servidor."""
    client = HetznerClient()
    
    try:
        server = client.servers.get(server_id)
        action = client.servers.reset(server_id)
        
        if cli.ctx.obj.get("json"):
            click.echo(CLIFormatter.format_json({
                "server": server.model_dump(),
                "action": action.model_dump(),
            }))
        else:
            console.print(Panel(
                f"[blue]🔄 Servidor '{server.name}' está siendo reseteado[/blue]",
                title="Servidor Reseteado",
                border_style="blue",
            ))
            console.print(CLIFormatter.format_action(action.model_dump()))
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@servers.command()
@click.argument("server_id", type=int)
def backup(server_id: int):
    """Crear backup de un servidor."""
    client = HetznerClient()
    
    try:
        server = client.servers.get(server_id)
        action = client.servers.create_image(server_id, description="Backup manual")
        
        if cli.ctx.obj.get("json"):
            click.echo(CLIFormatter.format_json({
                "server": server.model_dump(),
                "action": action.model_dump(),
            }))
        else:
            console.print(Panel(
                f"[green]💾 Backup creado para servidor '{server.name}'[/green]",
                title="Backup Creado",
                border_style="green",
            ))
            console.print(CLIFormatter.format_action(action.model_dump()))
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@servers.command()
@click.argument("server_id", type=int)
def metrics(server_id: int):
    """Obtener métricas de un servidor."""
    client = HetznerClient()
    
    try:
        metrics = client.servers.get_metrics(server_id, type="cpu")
        
        if cli.ctx.obj.get("json"):
            click.echo(CLIFormatter.format_json(metrics))
        else:
            console.print(Panel(
                CLIFormatter.format_json(metrics),
                title=f"Métricas del Servidor {server_id}",
                border_style="blue",
            ))
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


# =============================================================================
# Comandos de Volúmenes
# =============================================================================

@cli.group()
def volumes():
    """Gestionar volúmenes de Hetzner Cloud."""
    pass


@volumes.command()
@click.option("--name", "-n", help="Filtrar por nombre")
@click.option("--all", "-a", is_flag=True, help="Mostrar todos los detalles")
def list(name: Optional[str], all: bool):
    """Listar volúmenes."""
    client = HetznerClient()
    
    try:
        volumes = client.volumes.list(name=name)
        
        if cli.ctx.obj.get("json"):
            click.echo(CLIFormatter.format_json(volumes.model_dump()))
        else:
            console.print(CLIFormatter.format_volume_list([v.model_dump() for v in volumes.volumes], all))
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@volumes.command()
@click.argument("volume_id", type=int)
def get(volume_id: int):
    """Obtener información de un volumen."""
    client = HetznerClient()
    
    try:
        volume = client.volumes.get(volume_id)
        
        if cli.ctx.obj.get("json"):
            click.echo(CLIFormatter.format_json(volume.model_dump()))
        else:
            console.print(CLIFormatter.format_volume(volume.model_dump(), True))
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@volumes.command()
@click.option("--name", "-n", required=True, help="Nombre del volumen")
@click.option("--size", "-s", type=int, required=True, help="Tamaño en GB")
@click.option("--location", "-l", default="nbg1", help="Localización")
def create(name: str, size: int, location: str):
    """Crear un volumen."""
    from hetzner_mcp.core.models import CreateVolumeRequest
    
    client = HetznerClient()
    
    try:
        request = CreateVolumeRequest(
            name=name,
            size=size,
            location=location,
        )
        
        volume = client.volumes.create(request)
        
        if cli.ctx.obj.get("json"):
            click.echo(CLIFormatter.format_json(volume.model_dump()))
        else:
            console.print(Panel(
                f"[green]✅ Volumen '{volume.name}' creado con ID {volume.id}[/green]",
                title="Volumen Creado",
                border_style="green",
            ))
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@volumes.command()
@click.argument("volume_id", type=int)
@click.argument("server_id", type=int)
def attach(volume_id: int, server_id: int):
    """Conectar volumen a servidor."""
    client = HetznerClient()
    
    try:
        volume = client.volumes.get(volume_id)
        server = client.servers.get(server_id)
        action = client.volumes.attach(volume_id, server_id)
        
        if cli.ctx.obj.get("json"):
            click.echo(CLIFormatter.format_json({
                "volume": volume.model_dump(),
                "server": server.model_dump(),
                "action": action.model_dump(),
            }))
        else:
            console.print(Panel(
                f"[green]✅ Volumen '{volume.name}' conectado a servidor '{server.name}'[/green]",
                title="Volumen Conectado",
                border_style="green",
            ))
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@volumes.command()
@click.argument("volume_id", type=int)
def detach(volume_id: int):
    """Desconectar volumen de servidor."""
    client = HetznerClient()
    
    try:
        volume = client.volumes.get(volume_id)
        action = client.volumes.detach(volume_id)
        
        if cli.ctx.obj.get("json"):
            click.echo(CLIFormatter.format_json({
                "volume": volume.model_dump(),
                "action": action.model_dump(),
            }))
        else:
            console.print(Panel(
                f"[green]✅ Volumen '{volume.name}' desconectado[/green]",
                title="Volumen Desconectado",
                border_style="green",
            ))
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@volumes.command()
@click.argument("volume_id", type=int)
@click.option("--force", "-f", is_flag=True, help="Forzar eliminación")
def delete(volume_id: int, force: bool):
    """Eliminar un volumen."""
    client = HetznerClient()
    
    try:
        volume = client.volumes.get(volume_id)
        
        if not force:
            click.confirm(
                f"¿Estás seguro de eliminar el volumen '{volume.name}' (ID: {volume.id})?",
                abort=True,
            )
        
        client.volumes.delete(volume_id)
        
        console.print(Panel(
            f"[green]✅ Volumen '{volume.name}' eliminado[/green]",
            title="Volumen Eliminado",
            border_style="green",
        ))
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


# =============================================================================
# Comandos de Redes
# =============================================================================

@cli.group()
def networks():
    """Gestionar redes de Hetzner Cloud."""
    pass


@networks.command()
@click.option("--name", "-n", help="Filtrar por nombre")
@click.option("--all", "-a", is_flag=True, help="Mostrar todos los detalles")
def list(name: Optional[str], all: bool):
    """Listar redes."""
    client = HetznerClient()
    
    try:
        networks = client.networks.list(name=name)
        
        if cli.ctx.obj.get("json"):
            click.echo(CLIFormatter.format_json(networks.model_dump()))
        else:
            console.print(CLIFormatter.format_network_list([n.model_dump() for n in networks.networks], all))
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@networks.command()
@click.argument("network_id", type=int)
def get(network_id: int):
    """Obtener información de una red."""
    client = HetznerClient()
    
    try:
        network = client.networks.get(network_id)
        
        if cli.ctx.obj.get("json"):
            click.echo(CLIFormatter.format_json(network.model_dump()))
        else:
            console.print(CLIFormatter.format_network(network.model_dump(), True))
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@networks.command()
@click.option("--name", "-n", required=True, help="Nombre de la red")
@click.option("--ip-range", required=True, help="Rango IP en notación CIDR")
def create(name: str, ip_range: str):
    """Crear una red."""
    from hetzner_mcp.core.models import CreateNetworkRequest
    
    client = HetznerClient()
    
    try:
        request = CreateNetworkRequest(
            name=name,
            ip_range=ip_range,
        )
        
        network = client.networks.create(request)
        
        if cli.ctx.obj.get("json"):
            click.echo(CLIFormatter.format_json(network.model_dump()))
        else:
            console.print(Panel(
                f"[green]✅ Red '{network.name}' creada con ID {network.id}[/green]",
                title="Red Creada",
                border_style="green",
            ))
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@networks.command()
@click.argument("network_id", type=int)
@click.argument("server_id", type=int)
def attach(network_id: int, server_id: int):
    """Conectar servidor a red."""
    client = HetznerClient()
    
    try:
        network = client.networks.get(network_id)
        server = client.servers.get(server_id)
        action = client.networks.attach_server(network_id, server_id)
        
        if cli.ctx.obj.get("json"):
            click.echo(CLIFormatter.format_json({
                "network": network.model_dump(),
                "server": server.model_dump(),
                "action": action.model_dump(),
            }))
        else:
            console.print(Panel(
                f"[green]✅ Servidor '{server.name}' conectado a red '{network.name}'[/green]",
                title="Conexión Realizada",
                border_style="green",
            ))
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@networks.command()
@click.argument("network_id", type=int)
@click.argument("server_id", type=int)
def detach(network_id: int, server_id: int):
    """Desconectar servidor de red."""
    client = HetznerClient()
    
    try:
        network = client.networks.get(network_id)
        server = client.servers.get(server_id)
        action = client.networks.detach_server(network_id, server_id)
        
        if cli.ctx.obj.get("json"):
            click.echo(CLIFormatter.format_json({
                "network": network.model_dump(),
                "server": server.model_dump(),
                "action": action.model_dump(),
            }))
        else:
            console.print(Panel(
                f"[green]✅ Servidor '{server.name}' desconectado de red '{network.name}'[/green]",
                title="Desconexión Realizada",
                border_style="green",
            ))
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@networks.command()
@click.argument("network_id", type=int)
@click.option("--force", "-f", is_flag=True, help="Forzar eliminación")
def delete(network_id: int, force: bool):
    """Eliminar una red."""
    client = HetznerClient()
    
    try:
        network = client.networks.get(network_id)
        
        if not force:
            click.confirm(
                f"¿Estás seguro de eliminar la red '{network.name}' (ID: {network.id})?",
                abort=True,
            )
        
        client.networks.delete(network_id)
        
        console.print(Panel(
            f"[green]✅ Red '{network.name}' eliminada[/green]",
            title="Red Eliminada",
            border_style="green",
        ))
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


# =============================================================================
# Comandos de Firewalls
# =============================================================================

@cli.group()
def firewalls():
    """Gestionar firewalls de Hetzner Cloud."""
    pass


@firewalls.command()
@click.option("--name", "-n", help="Filtrar por nombre")
@click.option("--all", "-a", is_flag=True, help="Mostrar todos los detalles")
def list(name: Optional[str], all: bool):
    """Listar firewalls."""
    client = HetznerClient()
    
    try:
        firewalls = client.firewalls.list(name=name)
        
        if cli.ctx.obj.get("json"):
            click.echo(CLIFormatter.format_json(firewalls.model_dump()))
        else:
            console.print(CLIFormatter.format_firewall_list([f.model_dump() for f in firewalls.firewalls], all))
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@firewalls.command()
@click.argument("firewall_id", type=int)
def get(firewall_id: int):
    """Obtener información de un firewall."""
    client = HetznerClient()
    
    try:
        firewall = client.firewalls.get(firewall_id)
        
        if cli.ctx.obj.get("json"):
            click.echo(CLIFormatter.format_json(firewall.model_dump()))
        else:
            console.print(CLIFormatter.format_firewall(firewall.model_dump(), True))
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@firewalls.command()
@click.option("--name", "-n", required=True, help="Nombre del firewall")
def create(name: str):
    """Crear un firewall."""
    from hetzner_mcp.core.models import CreateFirewallRequest
    
    client = HetznerClient()
    
    try:
        # Reglas por defecto
        rules = [
            {
                "direction": "in",
                "protocol": "tcp",
                "port": "80",
                "action": "ACCEPT",
                "description": "HTTP",
            },
            {
                "direction": "in",
                "protocol": "tcp",
                "port": "443",
                "action": "ACCEPT",
                "description": "HTTPS",
            },
            {
                "direction": "in",
                "protocol": "tcp",
                "port": "22",
                "action": "ACCEPT",
                "description": "SSH",
            },
        ]
        
        request = CreateFirewallRequest(
            name=name,
            rules=rules,
        )
        
        firewall = client.firewalls.create(request)
        
        if cli.ctx.obj.get("json"):
            click.echo(CLIFormatter.format_json(firewall.model_dump()))
        else:
            console.print(Panel(
                f"[green]✅ Firewall '{firewall.name}' creado con ID {firewall.id}[/green]",
                title="Firewall Creado",
                border_style="green",
            ))
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@firewalls.command()
@click.argument("firewall_id", type=int)
@click.option("--force", "-f", is_flag=True, help="Forzar eliminación")
def delete(firewall_id: int, force: bool):
    """Eliminar un firewall."""
    client = HetznerClient()
    
    try:
        firewall = client.firewalls.get(firewall_id)
        
        if not force:
            click.confirm(
                f"¿Estás seguro de eliminar el firewall '{firewall.name}' (ID: {firewall.id})?",
                abort=True,
            )
        
        client.firewalls.delete(firewall_id)
        
        console.print(Panel(
            f"[green]✅ Firewall '{firewall.name}' eliminado[/green]",
            title="Firewall Eliminado",
            border_style="green",
        ))
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


# =============================================================================
# Comando Chat (Lenguaje Natural)
# =============================================================================

@cli.command()
@click.argument("command", nargs=-1, required=False)
@click.option("--interactive", "-i", is_flag=True, help="Modo interactivo")
def chat(command: tuple, interactive: bool):
    """
    Interactuar con Hetzner Cloud en lenguaje natural (español).
    
    Ejemplos:
        hetzner-mcp chat "Crear un servidor con Ubuntu 22.04 en Nuremberg"
        hetzner-mcp chat "¿Cuántos servidores tengo?"
        hetzner-mcp chat "Apagar todos los servidores con etiqueta 'test'"
        hetzner-mcp chat -i  # Modo interactivo
    """
    client = HetznerClient()
    nlp = NaturalLanguageProcessor(client)
    
    if interactive:
        console.print(Panel(
            "[bold green]Modo Chat Interactivo[/bold green]\n\n"
            "Escribe comandos en español para gestionar Hetzner Cloud.\n"
            "Ejemplos:\n"
            "  - 'Crear un servidor con Ubuntu 22.04'\n"
            "  - 'Listar todos mis servidores'\n"
            "  - 'Apagar el servidor con ID 12345'\n"
            "  - '¿Cuál es mi servidor más costoso?'\n\n"
            "Escribe 'salir' o 'exit' para terminar.",
            title="Hetzner MCP Chat",
            border_style="green",
        ))
        
        history = []
        
        while True:
            try:
                user_input = console.input("\n[bold cyan]>>> [/bold cyan]")
                
                if user_input.lower() in ["salir", "exit", "quit", "q"]:
                    console.print("[yellow]¡Hasta luego![/yellow]")
                    break
                
                if not user_input.strip():
                    continue
                
                result = nlp.chat(user_input, history)
                history.append(result)
                
                # Formatear salida
                if cli.ctx.obj.get("json"):
                    click.echo(CLIFormatter.format_json(result))
                else:
                    console.print(f"\n[bold green]{result['bot_response']}[/bold green]")
                    
            except KeyboardInterrupt:
                console.print("\n[yellow]¡Hasta luego![/yellow]")
                break
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
    else:
        # Modo no interactivo
        if not command:
            console.print("[yellow]Uso: hetzner-mcp chat <comando>[/yellow]")
            console.print("[yellow]Ejemplo: hetzner-mcp chat \"Crear un servidor\"[/yellow]")
            return
        
        full_command = " ".join(command)
        result = nlp.process(full_command)
        
        if cli.ctx.obj.get("json"):
            click.echo(CLIFormatter.format_json(result))
        else:
            console.print(CLIFormatter.format_result(result))


# =============================================================================
# Comando de Versión
# =============================================================================

@cli.command()
def version():
    """Mostrar versión de la aplicación."""
    from hetzner_mcp import __version__, __author__, __description__
    
    console.print(Panel(
        f"[bold green]Hetzner MCP Connection[/bold green]\n\n"
        f"Versión: {__version__}\n"
        f"Autor: {__author__}\n"
        f"Descripción: {__description__}\n\n"
        f"[dim]Sigue los principios NUPP de OMIMO: Open, Minimalist, Modular[/dim]",
        title="Información de Versión",
        border_style="green",
    ))


# =============================================================================
# Comando de Configuración
# =============================================================================

@cli.command()
def config():
    """Mostrar configuración actual."""
    console.print(Panel(
        f"[bold green]Configuración Actual[/bold green]\n\n"
        f"API URL: {get_settings().hetzner_api_url}\n"
        f"Timeout: {get_settings().request_timeout}s\n"
        f"Max Retries: {get_settings().max_retries}\n"
        f"Retry Delay: {get_settings().retry_delay}s\n"
        f"Log Level: {get_settings().log_level}\n"
        f"Page Size: {get_settings().page_size}\n"
        f"Safe Mode: {get_settings().safe_mode}\n"
        f"Protected Servers: {get_settings().protected_servers}",
        title="Configuración",
        border_style="blue",
    ))


# =============================================================================
# Función Principal
# =============================================================================

def main():
    """Función principal de la CLI."""
    cli(obj={})


if __name__ == "__main__":
    main()
