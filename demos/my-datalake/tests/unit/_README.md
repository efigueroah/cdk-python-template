# Directorio tests/unit

Este directorio contiene todos los tests unitarios del proyecto, organizados para reflejar la estructura del código fuente.

## Propósito:

Los tests unitarios validan componentes individuales de forma aislada:

- **Constructs**: Validación de recursos CDK generados
- **Stacks**: Validación de configuración de stacks
- **Lambda functions**: Validación de lógica de negocio
- **Utilities**: Validación de funciones helper

## Estructura:

```
unit/
├── __init__.py
├── test_constructs/         # Tests de constructs personalizados
│   ├── __init__.py
│   ├── test_base/
│   │   └── test_base_construct.py
│   ├── test_storage/
│   │   ├── test_s3_bucket.py
│   │   └── test_dynamodb_table.py
│   ├── test_compute/
│   │   ├── test_lambda_function.py
│   │   └── test_ecs_service.py
│   └── test_networking/
│       ├── test_vpc.py
│       └── test_load_balancer.py
├── test_stacks/             # Tests de stacks CDK
│   ├── __init__.py
│   ├── test_base/
│   │   ├── test_network_stack.py
│   │   └── test_security_stack.py
│   ├── test_compute/
│   │   └── test_lambda_stack.py
│   ├── test_storage/
│   │   └── test_database_stack.py
│   └── test_api/
│       └── test_api_gateway_stack.py
├── test_lambda/             # Tests de funciones Lambda
│   ├── __init__.py
│   ├── test_shared/
│   │   ├── test_utils.py
│   │   └── test_aws_clients.py
│   ├── test_api/
│   │   ├── test_users/
│   │   └── test_auth/
│   ├── test_workers/
│   │   └── test_data_processor/
│   └── test_triggers/
│       └── test_s3_trigger/
└── test_utils/              # Tests de utilidades
    ├── __init__.py
    └── test_config.py
```

## Patrones de testing:

### 1. Tests de Constructs CDK:

```python
import pytest
from aws_cdk import App, Stack
from aws_cdk.assertions import Template, Match
from src.my_datalake.constructs.storage.s3_bucket import SecureS3Bucket

class TestSecureS3Bucket:
    def setup_method(self):
        """Configuración para cada test"""
        self.app = App()
        self.stack = Stack(self.app, "TestStack")
    
    def test_creates_encrypted_bucket(self):
        """Test que el bucket se crea con encriptación"""
        bucket = SecureS3Bucket(
            self.stack, "TestBucket",
            bucket_name="test-bucket",
            enable_encryption=True
        )
        
        template = Template.from_stack(self.stack)
        
        # Verificar que el bucket existe
        template.has_resource("AWS::S3::Bucket", {
            "Properties": {
                "BucketName": "test-bucket",
                "BucketEncryption": {
                    "ServerSideEncryptionConfiguration": [{
                        "ServerSideEncryptionByDefault": {
                            "SSEAlgorithm": "AES256"
                        }
                    }]
                }
            }
        })
    
    def test_creates_bucket_policy(self):
        """Test que se crea la política del bucket"""
        bucket = SecureS3Bucket(
            self.stack, "TestBucket",
            bucket_name="test-bucket",
            enable_public_read_access=False
        )
        
        template = Template.from_stack(self.stack)
        
        # Verificar política de bucket
        template.has_resource("AWS::S3::BucketPolicy", {
            "Properties": {
                "PolicyDocument": {
                    "Statement": Match.array_with([
                        Match.object_like({
                            "Effect": "Deny",
                            "Principal": "*",
                            "Action": "s3:GetObject"
                        })
                    ])
                }
            }
        })
    
    def test_validates_bucket_name(self):
        """Test validación de nombre de bucket"""
        with pytest.raises(ValueError, match="Bucket name cannot be empty"):
            SecureS3Bucket(
                self.stack, "TestBucket",
                bucket_name=""
            )
```

### 2. Tests de Stacks:

```python
import pytest
from aws_cdk import App
from aws_cdk.assertions import Template
from src.my_datalake.stacks.network_stack import NetworkStack

class TestNetworkStack:
    def setup_method(self):
        """Configuración para cada test"""
        self.app = App()
        self.config = {
            'environment': 'test',
            'vpc_cidr': '10.0.0.0/16',
            'availability_zones': ['us-east-1a', 'us-east-1b']
        }
    
    def test_creates_vpc_with_correct_cidr(self):
        """Test creación de VPC con CIDR correcto"""
        stack = NetworkStack(
            self.app, "TestNetworkStack",
            config=self.config
        )
        
        template = Template.from_stack(stack)
        
        template.has_resource_properties("AWS::EC2::VPC", {
            "CidrBlock": "10.0.0.0/16",
            "EnableDnsHostnames": True,
            "EnableDnsSupport": True
        })
    
    def test_creates_public_and_private_subnets(self):
        """Test creación de subnets públicas y privadas"""
        stack = NetworkStack(
            self.app, "TestNetworkStack",
            config=self.config
        )
        
        template = Template.from_stack(stack)
        
        # Verificar subnets públicas
        template.resource_count_is("AWS::EC2::Subnet", 4)  # 2 públicas + 2 privadas
        
        # Verificar Internet Gateway
        template.resource_count_is("AWS::EC2::InternetGateway", 1)
        
        # Verificar NAT Gateways
        template.resource_count_is("AWS::EC2::NatGateway", 2)
    
    def test_exports_vpc_id(self):
        """Test que se exporta el VPC ID"""
        stack = NetworkStack(
            self.app, "TestNetworkStack",
            config=self.config
        )
        
        template = Template.from_stack(stack)
        
        template.has_output("VpcId", {
            "Export": {
                "Name": "test-vpc-id"
            }
        })
```

### 3. Tests de Lambda Functions:

```python
import pytest
import json
from unittest.mock import patch, MagicMock
from src.my_datalake.lambda.api.users.handler import lambda_handler, process_event

class TestUsersHandler:
    def setup_method(self):
        """Configuración para cada test"""
        self.sample_event = {
            'httpMethod': 'GET',
            'path': '/users',
            'headers': {'Content-Type': 'application/json'},
            'queryStringParameters': None,
            'body': None
        }
        self.sample_context = MagicMock()
    
    @patch('src.my_datalake.lambda.api.users.handler.get_dynamodb_client')
    def test_get_users_success(self, mock_dynamodb):
        """Test obtención exitosa de usuarios"""
        # Configurar mock
        mock_client = MagicMock()
        mock_dynamodb.return_value = mock_client
        mock_client.scan.return_value = {
            'Items': [
                {'id': {'S': '1'}, 'name': {'S': 'John Doe'}},
                {'id': {'S': '2'}, 'name': {'S': 'Jane Smith'}}
            ]
        }
        
        # Ejecutar función
        response = lambda_handler(self.sample_event, self.sample_context)
        
        # Verificar respuesta
        assert response['statusCode'] == 200
        assert 'application/json' in response['headers']['Content-Type']
        
        body = json.loads(response['body'])
        assert 'users' in body
        assert len(body['users']) == 2
        assert body['users'][0]['name'] == 'John Doe'
    
    @patch('src.my_datalake.lambda.api.users.handler.get_dynamodb_client')
    def test_get_users_dynamodb_error(self, mock_dynamodb):
        """Test manejo de error de DynamoDB"""
        # Configurar mock para error
        mock_client = MagicMock()
        mock_dynamodb.return_value = mock_client
        mock_client.scan.side_effect = Exception("DynamoDB error")
        
        # Ejecutar función
        response = lambda_handler(self.sample_event, self.sample_context)
        
        # Verificar respuesta de error
        assert response['statusCode'] == 500
        body = json.loads(response['body'])
        assert 'error' in body
    
    def test_process_event_with_filters(self):
        """Test procesamiento de evento con filtros"""
        event = {
            'queryStringParameters': {
                'status': 'active',
                'limit': '10'
            }
        }
        
        with patch('src.my_datalake.lambda.api.users.handler.get_dynamodb_client') as mock_dynamodb:
            mock_client = MagicMock()
            mock_dynamodb.return_value = mock_client
            mock_client.scan.return_value = {'Items': []}
            
            result = process_event(event)
            
            # Verificar que se llamó scan con filtros
            mock_client.scan.assert_called_once()
            call_args = mock_client.scan.call_args[1]
            assert 'FilterExpression' in call_args
    
    def test_invalid_http_method(self):
        """Test método HTTP no soportado"""
        event = self.sample_event.copy()
        event['httpMethod'] = 'DELETE'
        
        response = lambda_handler(event, self.sample_context)
        
        assert response['statusCode'] == 405
        body = json.loads(response['body'])
        assert 'Method not allowed' in body['error']
```

### 4. Tests de Utilities:

```python
import pytest
import os
from unittest.mock import patch
from src.my_datalake.lambda.shared.utils import setup_logging, get_env_var

class TestUtils:
    def test_setup_logging_default_level(self):
        """Test configuración de logging con nivel por defecto"""
        logger = setup_logging('test_logger')
        
        assert logger.name == 'test_logger'
        assert logger.level == 20  # INFO level
    
    @patch.dict(os.environ, {'LOG_LEVEL': 'DEBUG'})
    def test_setup_logging_custom_level(self):
        """Test configuración de logging con nivel personalizado"""
        logger = setup_logging('test_logger')
        
        assert logger.level == 10  # DEBUG level
    
    def test_get_env_var_exists(self):
        """Test obtención de variable de entorno existente"""
        with patch.dict(os.environ, {'TEST_VAR': 'test_value'}):
            result = get_env_var('TEST_VAR')
            assert result == 'test_value'
    
    def test_get_env_var_not_exists_with_default(self):
        """Test obtención de variable de entorno no existente con default"""
        result = get_env_var('NON_EXISTENT_VAR', 'default_value')
        assert result == 'default_value'
    
    def test_get_env_var_not_exists_without_default(self):
        """Test obtención de variable de entorno no existente sin default"""
        result = get_env_var('NON_EXISTENT_VAR')
        assert result is None
```

## Mejores prácticas para tests unitarios:

1. **Aislamiento**: Cada test debe ser independiente
2. **Mocking**: Mock de dependencias externas (AWS, DB, etc.)
3. **Naming**: Nombres descriptivos que expliquen qué se está probando
4. **Setup/Teardown**: Usar fixtures para configuración común
5. **Assertions**: Verificaciones específicas y claras
6. **Coverage**: Cubrir casos de éxito, error y edge cases
7. **Performance**: Tests rápidos (< 1 segundo cada uno)
8. **Documentation**: Documentar tests complejos

## Comandos útiles:

```bash
# Ejecutar solo tests unitarios
npm run test tests/unit/

# Tests con coverage específico
npm run test tests/unit/ -- --cov=src/my_datalake/constructs

# Test específico
npm run test tests/unit/test_constructs/test_storage/test_s3_bucket.py::TestSecureS3Bucket::test_creates_encrypted_bucket

# Tests en modo verbose
npm run test tests/unit/ -- -v
```
