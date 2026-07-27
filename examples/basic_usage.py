#!/usr/bin/env python3
"""
Ejemplo de uso básico de Hetzner MCP Connection

Este ejemplo muestra cómo usar el cliente de Hetzner para realizar
operaciones básicas con servidores, volúmenes y redes.
"""

from hetzner_mcp import HetznerClient
from hetzner_mcp.core.models import CreateServerRequest, CreateVolumeRequest


def main():
    """Ejemplo de uso básico."""
    
    # Inicializar el cliente
    print("🔹 Inicializando cliente de Hetzner...")
    client = HetznerClient()
    
    # Listar servidores
    print("\n📋 Listando servidores...")
    servers = client.servers.list()
    print(f"Encontrados {len(servers.servers)} servidores")
    for server in servers.servers:
        print(f"  - {server.name} (ID: {server.id}, Estado: {server.status})")
    
    # Obtener información de un servidor específico
    if servers.servers:
        server_id = servers.servers[0].id
        print(f"\n📄 Obteniendo información del servidor {server_id}...")
        server = client.servers.get(server_id)
        print(f"Nombre: {server.name}")
        print(f"Tipo: {server.server_type.get('name', 'N/A')}")
        print(f"Localización: {server.datacenter.get('name', 'N/A')}")
        print(f"IPv4: {server.ipv4_address}")
        print(f"IPv6: {server.ipv6_address}")
    
    # Listar tipos de servidor
    print("\n💻 Listando tipos de servidor...")
    server_types = client.server_types.list()
    print(f"Disponibles {len(server_types.server_types)} tipos de servidor")
    for st in server_types.server_types[:5]:  # Mostrar primeros 5
        print(f"  - {st.name}: {st.cores} cores, {st.memory}GB RAM, {st.disk}GB disco")
    
    # Listar localizaciones
    print("\n🌍 Listando localizaciones...")
    locations = client.locations.list()
    print(f"Disponibles {len(locations.locations)} localizaciones")
    for loc in locations.locations:
        print(f"  - {loc.name} ({loc.city}, {loc.country})")
    
    # Listar imágenes
    print("\n🖼️ Listando imágenes...")
    images = client.images.list(type="system")
    print(f"Disponibles {len(images.images)} imágenes de sistema")
    for img in images.images[:5]:  # Mostrar primeras 5
        print(f"  - {img.name} ({img.os_flavor} {img.os_version})")
    
    # Listar volúmenes
    print("\n💾 Listando volúmenes...")
    volumes = client.volumes.list()
    print(f"Encontrados {len(volumes.volumes)} volúmenes")
    for vol in volumes.volumes:
        print(f"  - {vol.name} (ID: {vol.id}, {vol.size}GB, Estado: {vol.status})")
    
    # Listar redes
    print("\n🌐 Listando redes...")
    networks = client.networks.list()
    print(f"Encontradas {len(networks.networks)} redes")
    for net in networks.networks:
        print(f"  - {net.name} (ID: {net.id}, Rango: {net.ip_range})")
    
    # Listar firewalls
    print("\n🔥 Listando firewalls...")
    firewalls = client.firewalls.list()
    print(f"Encontrados {len(firewalls.firewalls)} firewalls")
    for fw in firewalls.firewalls:
        print(f"  - {fw.name} (ID: {fw.id}, Reglas: {len(fw.rules)})")
    
    print("\n✅ Ejemplo completado exitosamente!")


if __name__ == "__main__":
    main()
