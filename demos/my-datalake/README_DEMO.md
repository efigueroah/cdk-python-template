# My DataLake - Proyecto Demo

Este proyecto demuestra el uso de la plantilla de Projen para crear una infraestructura de Data Lake en AWS usando CDK con Python.

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                    AWS Account                              │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                   S3 Bucket                         │    │
│  │  my-datalake-{account}-{region}                     │    │
│  │                                                     │    │
│  │  ✅ Encryption: S3 Managed (AES256)                │    │
│  │  ✅ Block Public Access: Enabled                   │    │
│  │  ✅ Versioning: Enabled                            │    │
│  │  ✅ SSL Enforcement: Required                      │    │
│  │  ✅ Lifecycle Rules:                               │    │
│  │     • Standard → IA (30 days)                      │    │
│  │     • IA → Glacier (90 days)                       │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 📦 Recursos Desplegados

### S3 Bucket
- **Propósito**: Almacenamiento principal del Data Lake
- **Nombre**: `my-datalake-281611232941-us-east-2` (ejemplo)
- **Región**: us-east-2 (configurable)

### Políticas de Seguridad
- **Bucket Policy**: Deniega todas las operaciones sin SSL
- **IAM Roles**: Para auto-delete objects (solo desarrollo)

## 🛡️ Seguridad Implementada

### Configuraciones de Seguridad
| Característica | Estado | Descripción |
|----------------|--------|-------------|
| Block Public Access | ✅ Habilitado | Previene acceso público accidental |
| Encriptación | ✅ S3 Managed | Datos encriptados en reposo |
| SSL/TLS | ✅ Obligatorio | Todas las conexiones deben usar HTTPS |
| Versionado | ✅ Habilitado | Protección contra eliminación accidental |
| Lifecycle Rules | ✅ Configurado | Optimización automática de costos |

### CDK Nag Validaciones
| Regla | Estado | Justificación |
|-------|--------|---------------|
| AwsSolutions-S1 | 🔕 Suprimida | Server access logging no requerido para desarrollo |
| AwsSolutions-S2 | 🔕 Suprimida | Acceso público bloqueado por configuración |
| AwsSolutions-S10 | 🔕 Suprimida | SSL enforcement habilitado explícitamente |
| AwsSolutions-IAM5 | 🔕 Suprimida | Permisos wildcard necesarios para auto-delete |

## 🚀 Comandos Disponibles

### Desarrollo
```bash
# Activar entorno virtual
source .env/bin/activate

# Instalar dependencias
pip install -r requirements-dev.txt

# Ejecutar tests
python -m pytest tests/ -v

# Formatear código
black .
isort .

# Linting
flake8 .
```

### CDK
```bash
# Generar template CloudFormation
cdk synth

# Listar stacks
cdk list

# Validar diferencias
cdk diff

# Desplegar
cdk deploy my-datalake-dev

# Eliminar
cdk destroy my-datalake-dev
```

## 📊 Estructura del Proyecto

```
my-datalake/
├── app.py                      # Punto de entrada CDK
├── my_datalake/
│   ├── __init__.py
│   └── main.py                 # Stack principal con S3 bucket
├── tests/
│   ├── __init__.py
│   └── test_example.py         # Tests de validación
├── .env/                       # Entorno virtual Python
├── cdk.out/                    # Templates generados
├── requirements.txt            # Dependencias producción
├── requirements-dev.txt        # Dependencias desarrollo
├── .projenrc.py               # Configuración Projen
├── cdk.json                   # Configuración CDK
└── README_DEMO.md             # Este archivo
```

## 🧪 Tests Implementados

### Cobertura de Tests
- ✅ Creación del bucket S3
- ✅ Propiedades de seguridad
- ✅ Configuración de lifecycle
- ✅ Política de SSL enforcement
- ✅ Presencia de excepciones CDK Nag

### Ejecutar Tests
```bash
# Tests con verbose
python -m pytest tests/ -v

# Tests con cobertura
python -m pytest tests/ --cov=my_datalake

# Tests específicos
python -m pytest tests/test_example.py::test_s3_bucket_created -v
```

## 💰 Estimación de Costos

### S3 Standard (primeros 30 días)
- **Almacenamiento**: $0.023 por GB/mes
- **Requests**: $0.0004 por 1,000 PUT requests
- **Transferencia**: Gratis dentro de la misma región

### S3 Standard-IA (30-90 días)
- **Almacenamiento**: $0.0125 por GB/mes
- **Retrieval**: $0.01 por GB recuperado

### S3 Glacier (después de 90 días)
- **Almacenamiento**: $0.004 por GB/mes
- **Retrieval**: $0.01 por GB + tiempo de espera

> **Nota**: Los precios son aproximados para us-east-1. Consulta la [calculadora de precios de AWS](https://calculator.aws) para estimaciones precisas.

## 🔧 Personalización

### Cambiar Región
```python
# En app.py
dev_env = Environment(
    account=os.getenv("CDK_DEFAULT_ACCOUNT"), 
    region="us-west-2"  # Cambiar región
)
```

### Modificar Lifecycle Rules
```python
# En my_datalake/main.py
lifecycle_rules=[
    s3.LifecycleRule(
        id="CustomTransition",
        enabled=True,
        transitions=[
            s3.Transition(
                storage_class=s3.StorageClass.INFREQUENT_ACCESS,
                transition_after=Duration.days(60)  # Personalizar días
            )
        ]
    )
]
```

### Agregar Notificaciones
```python
# Ejemplo: Notificación a Lambda
from aws_cdk import aws_s3_notifications as s3n

data_lake_bucket.add_event_notification(
    s3.EventType.OBJECT_CREATED,
    s3n.LambdaDestination(my_lambda_function)
)
```

## 🚨 Consideraciones de Producción

### Cambios Necesarios para Producción
1. **Remover auto-delete**: `auto_delete_objects=False`
2. **Cambiar removal policy**: `RemovalPolicy.RETAIN`
3. **Habilitar logging**: Configurar CloudTrail y access logs
4. **Backup**: Implementar cross-region replication
5. **Monitoreo**: Agregar CloudWatch alarms
6. **Acceso**: Implementar IAM roles específicos

### Ejemplo de Configuración de Producción
```python
data_lake_bucket = s3.Bucket(
    self,
    "DataLakeBucket",
    bucket_name=f"my-datalake-prod-{self.account}-{self.region}",
    block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
    encryption=s3.BucketEncryption.KMS_MANAGED,  # KMS para producción
    enforce_ssl=True,
    versioned=True,
    removal_policy=RemovalPolicy.RETAIN,  # Retener en producción
    # auto_delete_objects=True,  # REMOVER para producción
)
```

## 📚 Recursos Adicionales

- [AWS CDK Python Reference](https://docs.aws.amazon.com/cdk/api/v2/python/)
- [AWS S3 Best Practices](https://docs.aws.amazon.com/AmazonS3/latest/userguide/security-best-practices.html)
- [CDK Nag Rules](https://github.com/cdklabs/cdk-nag)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)

## 🤝 Contribuir

1. Fork el repositorio
2. Crear una rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit los cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

---

**Creado con**: AWS CDK + Python + Projen + CDK Nag
**Autor**: Demostración de plantilla
**Fecha**: $(date +%Y-%m-%d)
