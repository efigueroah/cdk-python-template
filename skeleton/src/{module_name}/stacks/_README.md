# Directorio stacks

Este directorio contiene las definiciones de stacks CDK que representan unidades lógicas de infraestructura desplegable.

## Propósito:

Los stacks son unidades de despliegue que agrupan recursos relacionados. Cada stack debe tener:

- **Responsabilidad única**: Un propósito específico y bien definido
- **Independencia**: Mínimas dependencias con otros stacks
- **Configurabilidad**: Soporte para múltiples ambientes
- **Observabilidad**: Logging y monitoreo integrados

## Estructura típica:

```
stacks/
├── __init__.py
├── base/                    # Stacks base y compartidos
│   ├── __init__.py
│   ├── network_stack.py     # VPC, subnets, gateways
│   └── security_stack.py    # IAM roles, security groups
├── compute/                 # Stacks de cómputo
│   ├── __init__.py
│   ├── lambda_stack.py      # Funciones Lambda
│   └── ecs_stack.py         # Servicios ECS
├── storage/                 # Stacks de almacenamiento
│   ├── __init__.py
│   ├── database_stack.py    # RDS, DynamoDB
│   └── storage_stack.py     # S3, EFS
├── api/                     # Stacks de API
│   ├── __init__.py
│   ├── api_gateway_stack.py # API Gateway
│   └── graphql_stack.py     # AppSync
└── monitoring/              # Stacks de monitoreo
    ├── __init__.py
    ├── logging_stack.py     # CloudWatch Logs
    └── alerting_stack.py    # CloudWatch Alarms
```

## Tipos de stacks:

### 1. Stacks Base
- **network_stack.py**: VPC, subnets, NAT gateways, VPC endpoints
- **security_stack.py**: IAM roles, security groups, KMS keys
- **dns_stack.py**: Route 53, certificados SSL

### 2. Stacks de Aplicación
- **api_stack.py**: API Gateway, Lambda authorizers
- **compute_stack.py**: Lambda functions, ECS services
- **storage_stack.py**: Bases de datos, buckets S3

### 3. Stacks de Soporte
- **monitoring_stack.py**: CloudWatch dashboards, alarms
- **cicd_stack.py**: CodePipeline, CodeBuild
- **backup_stack.py**: AWS Backup, snapshots

## Convenciones:

### Nomenclatura:
- Archivos: `{purpose}_stack.py`
- Clases: `{Purpose}Stack`
- Stack ID: `{Environment}-{Purpose}-Stack`

### Estructura de clase:
```python
class MyApplicationStack(Stack):
    def __init__(
        self, 
        scope: Construct, 
        construct_id: str,
        config: Dict[str, Any],
        **kwargs
    ):
        super().__init__(scope, construct_id, **kwargs)
        
        # Validaciones
        self._validate_config(config)
        
        # Variables de configuración
        self.config = config
        self.environment = config.get('environment', 'dev')
        
        # Recursos
        self._create_resources()
        
        # Outputs
        self._create_outputs()
    
    def _validate_config(self, config: Dict[str, Any]) -> None:
        """Validar configuración requerida"""
        pass
    
    def _create_resources(self) -> None:
        """Crear recursos del stack"""
        pass
    
    def _create_outputs(self) -> None:
        """Crear outputs del stack"""
        pass
```

## Configuración por ambiente:

Cada stack debe soportar configuración específica por ambiente:

```python
# En config.py
STACK_CONFIGS = {
    'dev': {
        'instance_type': 't3.micro',
        'min_capacity': 1,
        'max_capacity': 2
    },
    'prod': {
        'instance_type': 't3.large',
        'min_capacity': 2,
        'max_capacity': 10
    }
}
```

## Dependencias entre stacks:

### Cross-stack references:
```python
# En network_stack.py
self.vpc_id = CfnOutput(
    self, "VpcId",
    value=self.vpc.vpc_id,
    export_name=f"{self.environment}-vpc-id"
)

# En compute_stack.py
vpc_id = Fn.import_value(f"{self.environment}-vpc-id")
```

### Stack dependencies:
```python
# En app.py
network_stack = NetworkStack(app, "NetworkStack", config=config)
compute_stack = ComputeStack(app, "ComputeStack", config=config)
compute_stack.add_dependency(network_stack)
```

## Mejores prácticas:

1. **Separación lógica**: Un stack por dominio funcional
2. **Configuración externa**: Usar config.py para parámetros
3. **Validación**: Validar configuración en el constructor
4. **Outputs**: Exportar recursos que otros stacks necesiten
5. **Tagging**: Aplicar tags consistentes a todos los recursos
6. **Naming**: Usar convenciones de nomenclatura consistentes
7. **Documentation**: Documentar propósito y dependencias
8. **Testing**: Unit tests para cada stack
