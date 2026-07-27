# Guía de Uso - Hetzner MCP Connection

## 📖 Introducción

**Hetzner MCP Connection** es un **Model Context Protocol (MCP)** que permite a agentes de IA como **Mistral Work** interactuar con los servicios VPS de **Hetzner Cloud** de manera natural en español, así como automatizar tareas complejas.

Este documento te guiará a través de las principales funcionalidades y ejemplos de uso.

## 🚀 Instalación

### Requisitos Previos

- Python 3.10 o superior
- Cuenta en [Hetzner Cloud](https://console.hetzner.cloud/)
- Token de API de Hetzner Cloud

### Pasos de Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/AI-Foundry-Col/hetzner-mcp-connection.git
   cd hetzner-mcp-connection
   ```

2. **Crear entorno virtual:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Configurar token de API:**
   ```bash
   cp .env.example .env
   # Editar .env con tu token de API
   ```

## 🛠️ Configuración

### Archivo .env

```bash
# Token de API de Hetzner Cloud (requerido)
HETZNER_API_TOKEN=tu_token_de_api_aqui

# URL de la API (opcional)
HETZNER_API_URL=https://api.hetzner.cloud/v1

# Configuración de conexión
REQUEST_TIMEOUT=30
MAX_RETRIES=3
RETRY_DELAY=1

# Configuración de logging
LOG_LEVEL=INFO
LOG_FORMAT=simple

# Configuración de paginación
PAGE_SIZE=25

# Configuración de seguridad
SAFE_MODE=false
PROTECTED_SERVERS=123,456,789
```

### Obtener Token de API

1. Inicia sesión en [Hetzner Cloud Console](https://console.hetzner.cloud/)
2. Ve a **Security** → **API Tokens**
3. Haz clic en **Generate API Token**
4. Copia el token generado (¡solo se muestra una vez!)

## 🎯 Uso Básico

### CLI Principal

#### Listar recursos

```bash
# Listar servidores
hetzner-mcp servers list

# Listar servidores con filtros
hetzner-mcp servers list --name mi-servidor --status running

# Listar volúmenes
hetzner-mcp volumes list

# Listar redes
hetzner-mcp networks list

# Listar firewalls
hetzner-mcp firewalls list
```

#### Crear recursos

```bash
# Crear un servidor
hetzner-mcp servers create --name mi-servidor --type cx21 --location nbg1 --image ubuntu-22.04

# Crear un volumen
hetzner-mcp volumes create --name mi-volumen --size 100 --location nbg1

# Crear una red
hetzner-mcp networks create --name mi-red --ip-range 10.0.0.0/16

# Crear un firewall
hetzner-mcp firewalls create --name mi-firewall
```

#### Gestionar servidores

```bash
# Obtener información de un servidor
hetzner-mcp servers get 12345

# Iniciar un servidor
hetzner-mcp servers start 12345

# Parar un servidor
hetzner-mcp servers stop 12345

# Reiniciar un servidor
hetzner-mcp servers reboot 12345

# Resetear un servidor
hetzner-mcp servers reset 12345

# Crear backup de un servidor
hetzner-mcp servers backup 12345

# Eliminar un servidor
hetzner-mcp servers delete 12345
```

#### Gestionar volúmenes

```bash
# Obtener información de un volumen
hetzner-mcp volumes get 12345

# Conectar volumen a servidor
hetzner-mcp volumes attach 12345 67890

# Desconectar volumen de servidor
hetzner-mcp volumes detach 12345

# Eliminar un volumen
hetzner-mcp volumes delete 12345
```

#### Gestionar redes

```bash
# Obtener información de una red
hetzner-mcp networks get 12345

# Conectar servidor a red
hetzner-mcp networks attach 12345 67890

# Desconectar servidor de red
hetzner-mcp networks detach 12345 67890

# Eliminar una red
hetzner-mcp networks delete 12345
```

## 🤖 Modo Chat (Lenguaje Natural)

El modo chat permite interactuar con Hetzner Cloud usando lenguaje natural en español.

### Uso básico

```bash
# Procesar un comando en español
hetzner-mcp chat "Crear un servidor con Ubuntu 22.04 en Nuremberg"

# Procesar una pregunta
hetzner-mcp chat "¿Cuántos servidores tengo?"

# Procesar una acción compleja
hetzner-mcp chat "Apagar todos los servidores con etiqueta 'test'"
```

### Modo interactivo

```bash
# Iniciar modo chat interactivo
hetzner-mcp chat -i

# O simplemente
hetzner-mcp chat --interactive
```

### Ejemplos de comandos en español

#### Creación
- "Crear un servidor llamado 'web-prod' con tipo cx31 en Frankfurt"
- "Crear un volumen de 200GB llamado 'data-storage'"
- "Crear una red privada con rango 10.0.0.0/16"
- "Crear un firewall con reglas para HTTP, HTTPS y SSH"

#### Consulta
- "¿Qué servidores tengo?"
- "Listar todos mis volúmenes"
- "Mostrar información del servidor con ID 12345"
- "¿Cuántos servidores están en ejecución?"

#### Gestión
- "Iniciar el servidor 'web-prod'"
- "Parar todos los servidores"
- "Reiniciar el servidor con ID 12345"
- "Hacer backup de todos mis servidores"

#### Automatización
- "Crear 3 servidores con Ubuntu 22.04"
- "Hacer backup de todos los servidores y notificar"
- "Escalar mi infraestructura añadiendo 2 servidores más"

## 📊 Ejemplos de Automatización

### 1. Backup Automático

```python
from hetzner_mcp import HetznerClient
from hetzner_mcp.automation import BackupWorkflow

# Inicializar cliente
client = HetznerClient()

# Crear workflow de backup
backup_workflow = BackupWorkflow(client)

# Ejecutar backup de todos los servidores
result = backup_workflow.run(all_servers=True, wait=True)

print(f"Backups creados: {result['data']['successful']}")
```

### 2. Despliegue Automático

```python
from hetzner_mcp import HetznerClient
from hetzner_mcp.automation import DeployWorkflow

# Configuración de despliegue
config = {
    "server": {
        "name": "production-web",
        "type": "cx31",
        "location": "hel1",
        "image": "ubuntu-22.04",
    },
    "volume": {
        "create": True,
        "size": 100,
    },
    "firewall": {
        "create": True,
        "rules": [
            {"direction": "in", "protocol": "tcp", "port": "80", "action": "ACCEPT"},
            {"direction": "in", "protocol": "tcp", "port": "443", "action": "ACCEPT"},
            {"direction": "in", "protocol": "tcp", "port": "22", "action": "ACCEPT"},
        ],
    },
}

# Inicializar cliente
client = HetznerClient()

# Crear workflow de despliegue
deploy_workflow = DeployWorkflow(client)

# Ejecutar despliegue
result = deploy_workflow.run(config=config)

print(f"Servidor desplegado: {result['data']['server']['name']}")
```

### 3. Escalado Automático

```python
from hetzner_mcp import HetznerClient
from hetzner_mcp.automation import ScaleWorkflow

# Inicializar cliente
client = HetznerClient()

# Crear workflow de escalado
scale_workflow = ScaleWorkflow(client)

# Escalar a 5 servidores
result = scale_workflow.run(
    count=5,
    server_type="cx21",
    location="nbg1",
    image="ubuntu-22.04",
    prefix="scale-"
)

print(f"Servidores creados: {result['data']['created']}")
```

### 4. Monitoreo

```python
from hetzner_mcp import HetznerClient
from hetzner_mcp.automation import MonitoringWorkflow

# Inicializar cliente
client = HetznerClient()

# Crear workflow de monitoreo
monitor_workflow = MonitoringWorkflow(client)

# Monitorear todos los servidores
result = monitor_workflow.run(resource_type="server")

summary = result['data']['servers']['summary']
print(f"Servidores: {summary['total']}")
print(f"  - En ejecución: {summary['running']}")
print(f"  - Detenidos: {summary['stopped']}")
print(f"  - Otros: {summary['other']}")
```

## 🔧 Uso Programático

### Inicialización

```python
from hetzner_mcp import HetznerClient

# Inicializar cliente
client = HetznerClient()

# O con token específico
client = HetznerClient(api_token="tu_token_aqui")
```

### Gestión de Servidores

```python
from hetzner_mcp.core.models import CreateServerRequest, UpdateServerRequest

# Crear un servidor
request = CreateServerRequest(
    name="mi-servidor",
    server_type="cx21",
    location="nbg1",
    image="ubuntu-22.04",
    ssh_keys=["mi-clave-ssh"],
    start_after_create=True,
)
server = client.servers.create(request)

# Actualizar un servidor
update_request = UpdateServerRequest(
    name="nuevo-nombre",
    labels={"entorno": "produccion"},
)
updated_server = client.servers.update(server.id, update_request)

# Iniciar/Parar/Reiniciar
client.servers.start(server.id)
client.servers.stop(server.id)
client.servers.reboot(server.id)

# Eliminar
client.servers.delete(server.id)
```

### Gestión de Volúmenes

```python
from hetzner_mcp.core.models import CreateVolumeRequest

# Crear un volumen
volume_request = CreateVolumeRequest(
    name="mi-volumen",
    size=100,
    location="nbg1",
)
volume = client.volumes.create(volume_request)

# Conectar a servidor
action = client.volumes.attach(volume.id, server.id)

# Desconectar
action = client.volumes.detach(volume.id)

# Eliminar
client.volumes.delete(volume.id)
```

### Gestión de Redes

```python
from hetzner_mcp.core.models import CreateNetworkRequest

# Crear una red
network_request = CreateNetworkRequest(
    name="mi-red",
    ip_range="10.0.0.0/16",
)
network = client.networks.create(network_request)

# Conectar servidor a red
action = client.networks.attach_server(network.id, server.id)

# Desconectar
action = client.networks.detach_server(network.id, server.id)

# Eliminar
client.networks.delete(network.id)
```

### Gestión de Firewalls

```python
from hetzner_mcp.core.models import CreateFirewallRequest

# Crear un firewall
firewall_request = CreateFirewallRequest(
    name="mi-firewall",
    rules=[
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
    ],
)
firewall = client.firewalls.create(firewall_request)

# Aplicar a servidor
action = client.firewalls.apply_to_resources(
    firewall.id,
    [{"type": "server", "server": {"id": server.id}}]
)

# Eliminar
client.firewalls.delete(firewall.id)
```

## 📚 Procesamiento de Lenguaje Natural

### Uso básico

```python
from hetzner_mcp import HetznerClient
from hetzner_mcp.natural_language import NaturalLanguageProcessor

# Inicializar
client = HetznerClient()
nlp = NaturalLanguageProcessor(client)

# Procesar comando
result = nlp.process("Crear un servidor con Ubuntu 22.04 en Nuremberg")

if result["success"]:
    print(f"Operación exitosa: {result['message']}")
else:
    print(f"Error: {result['error']}")
```

### Modo chat

```python
# Modo chat
response = nlp.chat("Hola, ¿qué servidores tengo?")
print(response["bot_response"])
```

### Procesamiento por lotes

```python
# Procesar múltiples comandos
commands = [
    "Crear un servidor llamado web-1",
    "Crear un servidor llamado web-2",
    "Iniciar ambos servidores",
]

results = nlp.process_batch(commands)
for result in results:
    print(result["message"])
```

### Sugerencias de autocompletado

```python
# Obtener sugerencias
suggestions = nlp.get_suggestions("crear un")
print(suggestions)
# ['crear un servidor', 'crear un volumen', 'crear una red']
```

## 🔒 Seguridad

### Modo Seguro

El modo seguro previene operaciones destructivas:

```bash
# Activar modo seguro
export SAFE_MODE=true

# O en el archivo .env
SAFE_MODE=true
```

En modo seguro, las operaciones como `delete`, `update`, `stop`, etc. estarán bloqueadas.

### Servidores Protegidos

Puedes proteger servidores específicos:

```bash
# En el archivo .env
PROTECTED_SERVERS=123,456,789
```

Los servidores con estos IDs no podrán ser eliminados o modificados.

## 📊 Tipos de Recursos Soportados

### Servidores (Servers)
- ✅ Listar servidores
- ✅ Crear servidor
- ✅ Modificar servidor
- ✅ Eliminar servidor
- ✅ Iniciar/Parar/Reiniciar
- ✅ Acciones avanzadas (rescue, rebuild, etc.)
- ✅ Obtener métricas

### Volúmenes (Volumes)
- ✅ Listar volúmenes
- ✅ Crear volumen
- ✅ Modificar volumen
- ✅ Eliminar volumen
- ✅ Conectar/Desconectar a servidores
- ✅ Redimensionar volumen

### Redes (Networks)
- ✅ Listar redes
- ✅ Crear red
- ✅ Modificar red
- ✅ Eliminar red
- ✅ Conectar/Desconectar servidores

### Firewalls
- ✅ Listar firewalls
- ✅ Crear firewall
- ✅ Modificar firewall
- ✅ Eliminar firewall
- ✅ Aplicar a recursos
- ✅ Configurar reglas

### Load Balancers
- ✅ Listar load balancers
- ✅ Crear load balancer
- ✅ Modificar load balancer
- ✅ Eliminar load balancer
- ✅ Gestionar servicios y targets

### Imágenes (Images)
- ✅ Listar imágenes
- ✅ Crear snapshot
- ✅ Modificar imagen
- ✅ Eliminar imagen

### SSH Keys
- ✅ Listar claves SSH
- ✅ Crear clave SSH
- ✅ Eliminar clave SSH

### Certificados
- ✅ Listar certificados
- ✅ Crear certificado
- ✅ Modificar certificado
- ✅ Eliminar certificado

## 📈 Buenas Prácticas

### 1. Manejo de Errores

Siempre maneja excepciones:

```python
from hetzner_mcp.core.exceptions import HetznerAPIError

try:
    server = client.servers.get(12345)
except HetznerAPIError as e:
    print(f"Error: {e}")
```

### 2. Esperar Acciones

Algunas operaciones son asíncronas. Usa `wait_for_action`:

```python
from hetzner_mcp.utils import wait_for_action

action = client.servers.start(12345)
final_action = wait_for_action(client, action.id, timeout=300)

if final_action.status == "success":
    print("Servidor iniciado exitosamente")
```

### 3. Paginación

Para listar todos los recursos sin paginación:

```python
all_servers = client.servers.list_all()
all_volumes = client.volumes.list_all()
all_networks = client.networks.list_all()
```

### 4. Búsqueda por Nombre o ID

Usa la función utilitaria:

```python
from hetzner_mcp.utils import get_resource_by_name_or_id

# Obtener servidor por nombre o ID
server = get_resource_by_name_or_id(client, "server", "mi-servidor")
# O por ID
server = get_resource_by_name_or_id(client, "server", 12345)
```

### 5. Operaciones en Batch

```python
from hetzner_mcp.utils import batch_operation

# Iniciar múltiples servidores
results = batch_operation(
    client,
    resource_type="server",
    operation="start",
    identifiers=[12345, 67890, 11111]
)

print(f"Éxitos: {len(results['success'])}")
print(f"Fallos: {len(results['failed'])}")
```

## 🔧 Solución de Problemas

### Error de Autenticación

**Problema:** `HetznerAuthenticationError: Error de autenticación`

**Solución:**
1. Verifica que tu token de API es correcto
2. Asegúrate de que el token no ha expirado
3. Genera un nuevo token en la consola de Hetzner

### Límite de Requests

**Problema:** `HetznerRateLimitError: Límite de requests excedido`

**Solución:**
1. Espera unos minutos antes de continuar
2. Aumenta el tiempo entre requests
3. Usa menos requests en paralelo

### Recurso No Encontrado

**Problema:** `HetznerResourceNotFoundError: Server con ID '12345' no encontrado`

**Solución:**
1. Verifica que el ID es correcto
2. Asegúrate de que el recurso existe
3. Verifica que estás en el proyecto correcto

### Timeout

**Problema:** `HetznerAPIError: Timeout al conectar a la API`

**Solución:**
1. Verifica tu conexión a internet
2. Aumenta el timeout en la configuración
3. Prueba de nuevo más tarde

## 📚 Documentación Adicional

- [Referencia de la API](api-reference.md)
- [Ejemplos Avanzados](advanced-examples.md)
- [Automatización](automation.md)
- [Solución de Problemas](troubleshooting.md)

## 🙏 Soporte

- **Issues:** [GitHub Issues](https://github.com/AI-Foundry-Col/hetzner-mcp-connection/issues)
- **Discusión:** [GitHub Discussions](https://github.com/AI-Foundry-Col/hetzner-mcp-connection/discussions)
- **Email:** contact@aifoundry.col

---

**Hecho con ❤️ por AI Foundry Col**

*Open, Minimalist, Modular - Siguiendo los principios NUPP de OMIMO*
