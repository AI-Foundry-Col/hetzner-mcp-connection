# Hetzner MCP Connection

![Hetzner Cloud](https://img.shields.io/badge/Hetzner-Cloud-0073aa.svg)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

**MCP para conectar Mistral Work a los servicios VPS de Hetzner**

Este proyecto implementa un **Model Context Protocol (MCP)** que permite a agentes de IA como **Mistral Work** interactuar con los servicios VPS de **Hetzner Cloud** de manera natural en español, así como automatizar tareas complejas.

## 🎯 Características Principales

- ✅ **Interacción en Lenguaje Natural**: Conversación en español con el VPS
- ✅ **Gestión Completa de Servidores**: Crear, modificar, eliminar servidores
- ✅ **Redes y Firewalls**: Configuración de redes, firewalls y balanceadores
- ✅ **Almacenamiento**: Gestión de volúmenes y backups
- ✅ **Automatización**: Scripts y workflows predefinidos
- ✅ **Principios NUPP/OMIMO**: Diseño Open, Minimalist, Modular
- ✅ **API REST Completa**: Integración con toda la API de Hetzner Cloud

## 📋 Principios NUPP Aplicados

Este proyecto sigue los **6 Principios Casi Universales de Proyectos (NUPP)** de OMIMO:

1. **Enfócate en el Valor** - Cada función entrega valor real al usuario
2. **Mantén las Cosas Simple** - Diseño minimalista y fácil de usar
3. **Adapta el Enfoque** - Modular para diferentes necesidades
4. **Enfócate en los Cuellos de Botella** - Optimización de operaciones críticas
5. **Sé Transparente** - Código abierto y documentación clara
6. **Usa el Sentido Común** - Soluciones prácticas y efectivas

## 🚀 Instalación

### Requisitos Previos

- Python 3.10 o superior
- Cuenta en [Hetzner Cloud](https://console.hetzner.cloud/)
- API Token de Hetzner Cloud

### Instalación

```bash
# Clonar el repositorio
git clone https://github.com/AI-Foundry-Col/hetzner-mcp-connection.git
cd hetzner-mcp-connection

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -e ".[dev]"

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tu API token
```

### Configuración Inicial

Crea un archivo `.env` en la raíz del proyecto:

```bash
# Token de API de Hetzner Cloud
HETZNER_API_TOKEN=tu_token_aqui

# Configuración opcional
HETZNER_API_URL=https://api.hetzner.cloud/v1
REQUEST_TIMEOUT=30
MAX_RETRIES=3

# Configuración de logging
LOG_LEVEL=INFO
```

## 🛠️ Uso

### CLI Principal

```bash
# Ver ayuda general
hetzner-mcp --help

# Listar servidores
hetzner-mcp servers list

# Crear un servidor
hetzner-mcp servers create --name mi-servidor --type cx21 --location nbg1 --image ubuntu-22.04

# Interacción en lenguaje natural
hetzner-mcp chat "Crear un servidor con 4GB RAM en Frankfurt"
```

### Ejemplos de Commands

```bash
# Gestión de servidores
hetzner-mcp servers list
hetzner-mcp servers create --name web-server --type cx31 --location hel1 --image ubuntu-22.04
hetzner-mcp servers start 12345
hetzner-mcp servers stop 12345
hetzner-mcp servers reboot 12345
hetzner-mcp servers delete 12345

# Gestión de redes
hetzner-mcp networks list
hetzner-mcp networks create --name mi-red --ip-range 10.0.0.0/16

# Gestión de firewalls
hetzner-mcp firewalls list
hetzner-mcp firewalls create --name mi-firewall --rules '{"in": "ACCEPT", "out": "ACCEPT"}'

# Gestión de volúmenes
hetzner-mcp volumes list
hetzner-mcp volumes create --name mi-volumen --size 100 --location nbg1

# Automatización
hetzner-mcp automation deploy --config deploy_config.yaml
hetzner-mcp automation backup --server-id 12345
```

### Modo Chat (Lenguaje Natural)

```bash
# Iniciar modo interactivo
hetzner-mcp chat

# O usar comandos directos
hetzner-mcp chat "¿Qué servidores tengo actualmente?"
hetzner-mcp chat "Crear un servidor con Ubuntu 22.04 en Nuremberg"
hetzner-mcp chat "Apagar todos los servidores con etiqueta 'test'"
hetzner-mcp chat "Hacer backup de todos mis servidores de producción"
```

## 📚 Documentación

- [Guía de Uso](docs/usage.md)
- [Referencia de la API](docs/api-reference.md)
- [Ejemplos Avanzados](docs/advanced-examples.md)
- [Automatización](docs/automation.md)
- [Solución de Problemas](docs/troubleshooting.md)

## 🏗️ Arquitectura

```
hetzner-mcp-connection/
├── src/
│   └── hetzner_mcp/
│       ├── __init__.py
│       ├── cli.py              # Interfaz de línea de comandos
│       ├── config.py           # Configuración
│       ├── core/
│       │   ├── __init__.py
│       │   ├── client.py        # Cliente HTTP base
│       │   ├── exceptions.py    # Excepciones personalizadas
│       │   └── models.py        # Modelos Pydantic
│       ├── servers/
│       │   ├── __init__.py
│       │   ├── server.py        # Gestión de servidores
│       │   └── actions.py       # Acciones de servidores
│       ├── networking/
│       │   ├── __init__.py
│       │   ├── networks.py      # Gestión de redes
│       │   ├── firewalls.py     # Gestión de firewalls
│       │   └── load_balancers.py # Balanceadores
│       ├── storage/
│       │   ├── __init__.py
│       │   ├── volumes.py       # Gestión de volúmenes
│       │   └── backups.py       # Gestión de backups
│       ├── automation/
│       │   ├── __init__.py
│       │   ├── workflows.py     # Workflows de automatización
│       │   └── scripts.py       # Scripts predefinidos
│       └── utils/
│           ├── __init__.py
│           ├── helpers.py       # Funciones utilitarias
│           └── natural_language.py # Procesamiento de lenguaje natural
├── tests/
│   ├── __init__.py
│   ├── test_client.py
│   ├── test_servers.py
│   └── test_automation.py
├── docs/
│   ├── usage.md
│   ├── api-reference.md
│   └── automation.md
├── examples/
│   ├── basic_usage.py
│   ├── automation_script.py
│   └── chat_example.py
├── pyproject.toml
├── README.md
└── .env.example
```

## 🔧 API de Hetzner Cloud Cubierta

### Servidores (Servers)
- ✅ Listar servidores
- ✅ Crear servidor
- ✅ Modificar servidor
- ✅ Eliminar servidor
- ✅ Iniciar/Parar/Reiniciar
- ✅ Acciones avanzadas (rescue, rebuild, etc.)

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

### Balanceadores de Carga (Load Balancers)
- ✅ Listar balanceadores
- ✅ Crear balanceador
- ✅ Modificar balanceador
- ✅ Eliminar balanceador

### Almacenamiento (Storage)
- ✅ Listar volúmenes
- ✅ Crear volumen
- ✅ Modificar volumen
- ✅ Eliminar volumen
- ✅ Conectar/Desconectar volúmenes

### Imágenes (Images)
- ✅ Listar imágenes
- ✅ Crear snapshot
- ✅ Modificar imagen
- ✅ Eliminar imagen

### SSH Keys
- ✅ Listar claves SSH
- ✅ Crear clave SSH
- ✅ Eliminar clave SSH

## 🤖 Integración con Mistral Work

Este MCP está diseñado para integrarse con **Mistral Work** y otros agentes de IA. La interfaz de lenguaje natural permite:

1. **Consultas en Español**: "¿Cuántos servidores tengo en Frankfurt?"
2. **Acciones Complejas**: "Crear un cluster de 3 servidores con balanceador"
3. **Automatización Inteligente**: "Hacer backup de todos los servidores y notificar por email"
4. **Análisis**: "¿Cuál es mi servidor más costoso?"

### Ejemplo de Integración

```python
from hetzner_mcp import HetznerClient
from hetzner_mcp.natural_language import NaturalLanguageProcessor

# Inicializar cliente
client = HetznerClient()

# Procesador de lenguaje natural
nlp = NaturalLanguageProcessor(client)

# Procesar comando en español
response = nlp.process("Crear un servidor con Ubuntu 22.04 y 4GB RAM en Nuremberg")
print(response)
```

## 📊 Ejemplos de Automatización

### 1. Despliegue Automático

```yaml
# deploy_config.yaml
server:
  name: production-web
  type: cx31
  location: hel1
  image: ubuntu-22.04
  ssh_keys: [my-ssh-key]
  labels:
    environment: production
    role: web

volume:
  name: production-data
  size: 100
  location: hel1

firewall:
  name: production-firewall
  rules:
    in: ACCEPT
    out: ACCEPT
```

### 2. Backup Automático

```python
from hetzner_mcp.automation import BackupWorkflow

# Crear workflow de backup
backup_workflow = BackupWorkflow(client)
backup_workflow.run_all_servers()
```

### 3. Escalado Automático

```python
from hetzner_mcp.automation import ScaleWorkflow

# Escalar servidores basados en métricas
scale_workflow = ScaleWorkflow(client)
scale_workflow.scale_based_on_cpu(threshold=80)
```

## 🔒 Seguridad

- **Token de API**: Nunca se almacena en el código, solo en variables de entorno
- **Validación de Entrada**: Todos los inputs son validados con Pydantic
- **Manejo de Errores**: Excepciones claras y manejo de rate limiting
- **Logging Seguro**: Información sensible se mascara en los logs

## 📈 Contribución

Las contribuciones son bienvenidas. Por favor sigue estos pasos:

1. Fork el repositorio
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Haz commit de tus cambios (`git commit -m 'Añadir nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

### Estándares de Código

- **Formato**: Black
- **Linter**: Ruff
- **Tipado**: MyPy
- **Tests**: Pytest
- **Cobertura**: 80% mínimo

```bash
# Ejecutar tests
pytest

# Formatear código
black src/ tests/

# Verificar linting
ruff check src/ tests/

# Verificar tipos
mypy src/
```

## 📄 Licencia

Este proyecto está licenciado bajo la **MIT License**. Ver el archivo [LICENSE](LICENSE) para más detalles.

## 🙏 Agradecimientos

- [Hetzner Cloud](https://www.hetzner.com/cloud) por su excelente API
- [OMIMO](https://omimo.org/) por los principios NUPP
- [Mistral AI](https://mistral.ai/) por la inspiración

## 📞 Soporte

- **Issues**: [GitHub Issues](https://github.com/AI-Foundry-Col/hetzner-mcp-connection/issues)
- **Discusión**: [GitHub Discussions](https://github.com/AI-Foundry-Col/hetzner-mcp-connection/discussions)
- **Email**: contact@aifoundry.col

---

**Hecho con ❤️ por AI Foundry Col**

*Open, Minimalist, Modular - Siguiendo los principios NUPP de OMIMO*
