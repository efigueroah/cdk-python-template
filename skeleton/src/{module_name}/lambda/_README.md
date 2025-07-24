# Directorio lambda

Este directorio contiene el código fuente de las funciones AWS Lambda organizadas por funcionalidad o servicio.

## Propósito:

Centralizar todo el código de funciones Lambda con una estructura organizada que facilite:

- **Mantenimiento**: Código organizado por funcionalidad
- **Reutilización**: Librerías compartidas entre funciones
- **Testing**: Tests unitarios y de integración
- **Deployment**: Empaquetado automático con CDK

## Estructura típica:

```
lambda/
├── __init__.py
├── shared/                  # Código compartido entre funciones
│   ├── __init__.py
│   ├── utils.py            # Utilidades comunes
│   ├── models.py           # Modelos de datos
│   ├── exceptions.py       # Excepciones personalizadas
│   └── aws_clients.py      # Clientes AWS configurados
├── api/                    # Funciones de API
│   ├── __init__.py
│   ├── users/
│   │   ├── handler.py      # GET /users
│   │   └── requirements.txt
│   ├── auth/
│   │   ├── handler.py      # Autenticación
│   │   └── requirements.txt
│   └── health/
│       ├── handler.py      # Health check
│       └── requirements.txt
├── workers/                # Funciones de procesamiento
│   ├── __init__.py
│   ├── data_processor/
│   │   ├── handler.py      # Procesamiento de datos
│   │   └── requirements.txt
│   └── file_processor/
│       ├── handler.py      # Procesamiento de archivos
│       └── requirements.txt
└── triggers/               # Funciones disparadas por eventos
    ├── __init__.py
    ├── s3_trigger/
    │   ├── handler.py      # Trigger de S3
    │   └── requirements.txt
    └── dynamodb_stream/
        ├── handler.py      # DynamoDB Streams
        └── requirements.txt
```

## Organización por función:

Cada función Lambda debe tener su propio directorio con:

### Archivos requeridos:
- `handler.py`: Punto de entrada de la función
- `requirements.txt`: Dependencias específicas (opcional)

### Archivos opcionales:
- `config.py`: Configuración específica de la función
- `models.py`: Modelos de datos específicos
- `utils.py`: Utilidades específicas de la función
- `tests/`: Tests unitarios de la función

## Estructura de handler:

```python
# handler.py
import json
import logging
from typing import Dict, Any
from shared.utils import setup_logging
from shared.aws_clients import get_dynamodb_client

# Configurar logging
logger = setup_logging(__name__)

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handler principal de la función Lambda
    
    Args:
        event: Evento de entrada
        context: Contexto de Lambda
        
    Returns:
        Respuesta de la función
    """
    try:
        logger.info(f"Processing event: {json.dumps(event)}")
        
        # Lógica de la función
        result = process_event(event)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(result)
        }
        
    except Exception as e:
        logger.error(f"Error processing event: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Internal server error'})
        }

def process_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """Procesar el evento específico"""
    # Implementación específica
    pass
```

## Código compartido (shared/):

### utils.py
```python
import logging
import os
from typing import Any

def setup_logging(name: str) -> logging.Logger:
    """Configurar logging estándar"""
    logger = logging.getLogger(name)
    logger.setLevel(os.getenv('LOG_LEVEL', 'INFO'))
    return logger

def get_env_var(name: str, default: Any = None) -> str:
    """Obtener variable de entorno con valor por defecto"""
    return os.getenv(name, default)
```

### aws_clients.py
```python
import boto3
from botocore.config import Config

# Configuración común para clientes AWS
AWS_CONFIG = Config(
    region_name=os.getenv('AWS_REGION', 'us-east-1'),
    retries={'max_attempts': 3}
)

def get_dynamodb_client():
    """Cliente DynamoDB configurado"""
    return boto3.client('dynamodb', config=AWS_CONFIG)

def get_s3_client():
    """Cliente S3 configurado"""
    return boto3.client('s3', config=AWS_CONFIG)
```

## Integración con CDK:

```python
# En el stack CDK
from aws_cdk import aws_lambda as _lambda

# Función Lambda desde directorio
api_function = _lambda.Function(
    self, "ApiFunction",
    runtime=_lambda.Runtime.PYTHON_3_11,
    handler="handler.lambda_handler",
    code=_lambda.Code.from_asset("src/{module_name}/lambda/api/users"),
    environment={
        'LOG_LEVEL': 'INFO',
        'TABLE_NAME': table.table_name
    }
)
```

## Mejores prácticas:

1. **Separación de responsabilidades**: Una función por responsabilidad
2. **Código compartido**: Usar shared/ para evitar duplicación
3. **Logging**: Logging estructurado y consistente
4. **Error handling**: Manejo robusto de errores
5. **Environment variables**: Configuración a través de variables de entorno
6. **Dependencies**: requirements.txt específico por función si es necesario
7. **Testing**: Tests unitarios para cada función
8. **Performance**: Optimizar cold starts y memoria
9. **Security**: Principio de menor privilegio en permisos IAM
10. **Monitoring**: CloudWatch metrics y alarms
