# Directorio tests

Este directorio contiene todos los tests del proyecto organizados por tipo y funcionalidad.

## Propósito:

Asegurar la calidad y confiabilidad del código mediante:

- **Tests unitarios**: Validación de componentes individuales
- **Tests de integración**: Validación de interacciones entre componentes
- **Tests de infraestructura**: Validación de recursos CDK
- **Tests de regresión**: Prevención de errores en cambios futuros

## Estructura:

```
tests/
├── __init__.py
├── conftest.py              # Configuración global de pytest
├── unit/                    # Tests unitarios
│   ├── __init__.py
│   ├── test_constructs/     # Tests de constructs
│   │   ├── __init__.py
│   │   ├── test_storage/
│   │   └── test_compute/
│   ├── test_stacks/         # Tests de stacks
│   │   ├── __init__.py
│   │   ├── test_network_stack.py
│   │   └── test_api_stack.py
│   └── test_lambda/         # Tests de funciones Lambda
│       ├── __init__.py
│       ├── test_api/
│       └── test_workers/
├── integration/             # Tests de integración
│   ├── __init__.py
│   ├── test_api_integration.py
│   └── test_data_flow.py
├── fixtures/                # Datos de prueba
│   ├── __init__.py
│   ├── events/              # Eventos de prueba para Lambda
│   ├── responses/           # Respuestas mock
│   └── data/                # Datos de prueba
└── utils/                   # Utilidades para testing
    ├── __init__.py
    ├── mocks.py             # Mocks personalizados
    └── helpers.py           # Helpers para tests
```

## Tipos de tests:

### 1. Tests Unitarios (unit/)

#### Tests de Constructs:
```python
# test_constructs/test_storage/test_s3_bucket.py
import pytest
from aws_cdk import App, Stack
from aws_cdk.assertions import Template
from src.my_datalake.constructs.storage.s3_bucket import SecureS3Bucket

class TestSecureS3Bucket:
    def test_bucket_creation(self):
        app = App()
        stack = Stack(app, "TestStack")
        
        bucket = SecureS3Bucket(
            stack, "TestBucket",
            bucket_name="test-bucket"
        )
        
        template = Template.from_stack(stack)
        template.has_resource_properties("AWS::S3::Bucket", {
            "BucketName": "test-bucket",
            "BucketEncryption": {
                "ServerSideEncryptionConfiguration": [{
                    "ServerSideEncryptionByDefault": {
                        "SSEAlgorithm": "AES256"
                    }
                }]
            }
        })
```

#### Tests de Stacks:
```python
# test_stacks/test_network_stack.py
import pytest
from aws_cdk import App
from aws_cdk.assertions import Template
from src.my_datalake.stacks.network_stack import NetworkStack

class TestNetworkStack:
    def test_vpc_creation(self):
        app = App()
        config = {'environment': 'test'}
        
        stack = NetworkStack(app, "TestNetworkStack", config=config)
        template = Template.from_stack(stack)
        
        template.resource_count_is("AWS::EC2::VPC", 1)
        template.has_resource_properties("AWS::EC2::VPC", {
            "CidrBlock": "10.0.0.0/16"
        })
```

#### Tests de Lambda:
```python
# test_lambda/test_api/test_users_handler.py
import pytest
import json
from unittest.mock import patch, MagicMock
from src.my_datalake.lambda.api.users.handler import lambda_handler

class TestUsersHandler:
    @patch('src.my_datalake.lambda.api.users.handler.get_dynamodb_client')
    def test_get_users_success(self, mock_dynamodb):
        # Configurar mock
        mock_client = MagicMock()
        mock_dynamodb.return_value = mock_client
        mock_client.scan.return_value = {
            'Items': [{'id': {'S': '1'}, 'name': {'S': 'John'}}]
        }
        
        # Evento de prueba
        event = {
            'httpMethod': 'GET',
            'path': '/users'
        }
        
        # Ejecutar función
        response = lambda_handler(event, {})
        
        # Verificar resultado
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert len(body['users']) == 1
        assert body['users'][0]['name'] == 'John'
```

### 2. Tests de Integración (integration/)

```python
# test_api_integration.py
import pytest
import boto3
from moto import mock_dynamodb, mock_lambda
from src.my_datalake.lambda.api.users.handler import lambda_handler

@mock_dynamodb
@mock_lambda
class TestApiIntegration:
    def setup_method(self):
        # Configurar recursos mock
        self.dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        self.table = self.dynamodb.create_table(
            TableName='users-table',
            KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
    
    def test_full_user_workflow(self):
        # Test completo de flujo de usuario
        pass
```

## Configuración de pytest:

### conftest.py:
```python
import pytest
import os
from unittest.mock import patch

@pytest.fixture(autouse=True)
def setup_environment():
    """Configurar variables de entorno para tests"""
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    os.environ['LOG_LEVEL'] = 'DEBUG'
    yield
    # Cleanup si es necesario

@pytest.fixture
def mock_aws_credentials():
    """Mock de credenciales AWS"""
    with patch.dict(os.environ, {
        'AWS_ACCESS_KEY_ID': 'testing',
        'AWS_SECRET_ACCESS_KEY': 'testing',
        'AWS_SECURITY_TOKEN': 'testing',
        'AWS_SESSION_TOKEN': 'testing'
    }):
        yield

@pytest.fixture
def sample_event():
    """Evento de prueba para Lambda"""
    return {
        'httpMethod': 'GET',
        'path': '/test',
        'headers': {'Content-Type': 'application/json'},
        'body': None
    }
```

## Utilidades de testing:

### mocks.py:
```python
from unittest.mock import MagicMock
import boto3

class MockAWSClients:
    @staticmethod
    def mock_dynamodb_client():
        client = MagicMock()
        client.scan.return_value = {'Items': []}
        client.put_item.return_value = {}
        return client
    
    @staticmethod
    def mock_s3_client():
        client = MagicMock()
        client.get_object.return_value = {'Body': MagicMock()}
        return client
```

### helpers.py:
```python
import json
from typing import Dict, Any

def create_api_event(
    method: str = 'GET',
    path: str = '/',
    body: Dict[str, Any] = None,
    headers: Dict[str, str] = None
) -> Dict[str, Any]:
    """Crear evento de API Gateway para tests"""
    return {
        'httpMethod': method,
        'path': path,
        'headers': headers or {'Content-Type': 'application/json'},
        'body': json.dumps(body) if body else None
    }

def assert_lambda_response(
    response: Dict[str, Any],
    expected_status: int = 200,
    expected_body_keys: list = None
):
    """Validar respuesta de Lambda"""
    assert response['statusCode'] == expected_status
    if expected_body_keys:
        body = json.loads(response['body'])
        for key in expected_body_keys:
            assert key in body
```

## Comandos de testing:

```bash
# Ejecutar todos los tests
npm run test

# Tests con coverage
npm run test -- --cov=src --cov-report=html

# Tests específicos
npm run test tests/unit/test_stacks/

# Tests con verbose output
npm run test -- -v

# Tests en modo watch
npm run test -- --watch
```

## Mejores prácticas:

1. **Cobertura**: Mantener >80% de cobertura de código
2. **Aislamiento**: Tests independientes entre sí
3. **Mocking**: Mock de servicios AWS externos
4. **Fixtures**: Reutilizar datos de prueba
5. **Naming**: Nombres descriptivos para tests
6. **Documentation**: Documentar tests complejos
7. **Performance**: Tests rápidos y eficientes
8. **CI/CD**: Integración con pipeline de CI/CD
