# HG AWS Helpers - Versión Mejorada

Este paquete proporciona clases reutilizables y robustas para tareas comunes en proyectos AWS CDK en Python, con un enfoque en el manejo centralizado de parámetros de configuración.

## Características Principales

- **Soporte Multi-formato**: Carga y manejo de configuraciones en TOML, JSON y YAML.
- **Configuraciones Multi-ambiente**: Soporte para configuraciones base y específicas por ambiente (dev, prod, stage, etc.).
- **Interfaz Intuitiva**: Acceso a parámetros mediante notación de atributos y métodos con valores por defecto.
- **Conversión entre Formatos**: Herramientas para convertir configuraciones entre diferentes formatos.
- **Integración con CDK Context**: Importación y exportación de configuraciones desde/hacia la sección `context` de CDK.

## Instalación

```bash
# Desde el directorio raíz del proyecto
pip install -e ./hg_aws_helpers-q
```

## Uso Básico

### ConfigLoader

La clase `ConfigLoader` permite cargar y acceder a configuraciones en múltiples formatos.

```python
from hg_aws_helpers import ConfigLoader

# Cargar configuración desde archivo TOML
config_loader = ConfigLoader("./config/proyecto-ejemplo-dev.toml")
config = config_loader.load_config()

# Acceso a parámetros con notación de atributos
project_name = config.project.name
environment = config.project.environment

# Acceso a parámetros con método get() y valores por defecto
nat_gateways = config.network.get('nat_gateways', 2)
```

### Soporte Multi-ambiente

```python
# Cargar configuración con ambiente específico
config_loader = ConfigLoader(
    config_file="./config/proyecto-ejemplo.toml",
    environment="prod"
)
config = config_loader.load_config()

# La configuración incluirá valores específicos del ambiente "prod"
```

### ConfigConverter

La clase `ConfigConverter` permite convertir configuraciones entre formatos y manejar la integración con CDK context.

```python
from hg_aws_helpers import ConfigConverter

converter = ConfigConverter()

# Convertir archivo TOML a JSON
json_file = converter.convert_file(
    input_file="./config/proyecto-ejemplo.toml",
    output_format="json"
)

# Importar sección context de cdk.json a TOML
toml_context = converter.import_cdk_context(
    cdk_json_path="./cdk.json",
    output_format="toml"
)

# Exportar configuración a sección context de cdk.json
updated_cdk = converter.export_to_cdk_context(
    config_file="./config/proyecto-ejemplo.toml",
    cdk_json_path="./cdk.json",
    environment="dev"
)
```

## Estructura de Archivos de Configuración

### Archivo Base

```toml
# base.toml
[project]
name = "proyecto-ejemplo"
description = "Proyecto de ejemplo"

[aws]
region = "us-east-1"
account_id = "123456789012"

[network]
vpc_cidr = "10.0.0.0/16"
nat_gateways = 1
```

### Archivo de Ambiente

```toml
# env.prod.toml
[project]
environment = "prod"

[network]
nat_gateways = 3
```

### Archivo de Proyecto Específico

```toml
# proyecto-ejemplo-dev.toml
[project]
name = "proyecto-ejemplo-dev"
tags = { Owner = "DevOps", Environment = "Development" }
```

## Ejemplos Avanzados

### Validación de Parámetros Requeridos

```python
# Validar que ciertos parámetros existan
required_keys = [
    "project.name",
    "aws.region",
    "aws.account_id"
]

try:
    config_loader.validate_required_keys(required_keys)
    print("Configuración válida")
except KeyError as e:
    print(f"Error de configuración: {e}")
```

### Obtener Configuración de AWS

```python
# Obtener configuración específica de AWS
aws_config = config_loader.get_aws_config()
print(f"Account ID: {aws_config['account_id']}")
print(f"Region: {aws_config['region']}")
print(f"Tags: {aws_config['tags']}")
```

### Convertir entre Múltiples Formatos

```python
# Convertir de TOML a JSON y luego a YAML
json_file = converter.convert_file(
    input_file="./config/proyecto-ejemplo.toml",
    output_format="json"
)

yaml_file = converter.convert_file(
    input_file=json_file,
    output_format="yaml"
)
```

## Integración con AWS CDK

```python
from aws_cdk import core as cdk
from hg_aws_helpers import ConfigLoader

# Cargar configuración
config_loader = ConfigLoader("./config/proyecto-ejemplo-dev.toml", environment="dev")
config = config_loader.load_config()

# Crear app CDK
app = cdk.App()

# Crear stack con parámetros de configuración
stack = MyStack(app, "MyStack",
    env=cdk.Environment(
        account=config.aws.get('account_id'),
        region=config.aws.get('region')
    ),
    project_name=config.project.name,
    vpc_cidr=config.network.get('vpc_cidr'),
    nat_gateways=config.network.get('nat_gateways', 1)
)

app.synth()
```
