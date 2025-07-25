# Directorio assets

Este directorio contiene archivos estáticos y recursos que son utilizados por la infraestructura CDK durante el despliegue.

## Propósito:

Centralizar todos los assets estáticos necesarios para el despliegue:

- **Archivos de configuración**: Templates, políticas, scripts
- **Código fuente**: Archivos que se copian a recursos AWS
- **Documentos**: Archivos que se suben a S3 u otros servicios
- **Certificados**: Certificados SSL/TLS para desarrollo local

## Estructura típica:

```
assets/
├── __init__.py
├── lambda/                  # Assets para funciones Lambda
│   ├── layers/             # Código para Lambda Layers
│   │   ├── python-utils/
│   │   │   └── python/
│   │   │       └── lib/
│   │   │           └── python3.11/
│   │   │               └── site-packages/
│   │   └── nodejs-utils/
│   │       └── nodejs/
│   │           └── node_modules/
│   └── deployment-packages/ # Paquetes pre-compilados
├── policies/               # Políticas IAM y resource-based
│   ├── iam/
│   │   ├── lambda-execution-role.json
│   │   └── s3-access-policy.json
│   ├── s3/
│   │   └── bucket-policy-template.json
│   └── api-gateway/
│       └── resource-policy.json
├── scripts/                # Scripts de automatización
│   ├── deployment/
│   │   ├── pre-deploy.sh
│   │   └── post-deploy.sh
│   ├── database/
│   │   ├── init-schema.sql
│   │   └── seed-data.sql
│   └── monitoring/
│       └── setup-dashboards.py
├── templates/              # Templates de configuración
│   ├── cloudformation/
│   │   └── custom-resource.yaml
│   ├── docker/
│   │   ├── Dockerfile.lambda
│   │   └── docker-compose.yml
│   └── kubernetes/
│       └── deployment.yaml
├── static/                 # Archivos estáticos web
│   ├── html/
│   │   ├── index.html
│   │   └── error.html
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   └── app.js
│   └── images/
│       └── logo.png
├── certificates/           # Certificados para desarrollo
│   ├── dev/
│   │   ├── server.crt
│   │   └── server.key
│   └── README.md           # Instrucciones para certificados
└── data/                   # Datos de inicialización
    ├── seed/
    │   ├── users.json
    │   └── products.json
    └── config/
        ├── dev-config.json
        └── prod-config.json
```

## Tipos de assets:

### 1. Lambda Assets

#### Lambda Layers:
```
assets/lambda/layers/python-utils/
└── python/
    └── lib/
        └── python3.11/
            └── site-packages/
                ├── requests/
                ├── boto3/
                └── custom_utils/
```

Uso en CDK:
```python
layer = _lambda.LayerVersion(
    self, "UtilsLayer",
    code=_lambda.Code.from_asset("assets/lambda/layers/python-utils"),
    compatible_runtimes=[_lambda.Runtime.PYTHON_3_11]
)
```

#### Deployment Packages:
Para funciones Lambda con dependencias complejas pre-compiladas.

### 2. Policy Assets

#### IAM Policies:
```json
// assets/policies/iam/lambda-execution-role.json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        }
    ]
}
```

Uso en CDK:
```python
with open("assets/policies/iam/lambda-execution-role.json") as f:
    policy_document = json.load(f)

role = iam.Role(
    self, "LambdaRole",
    assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
    inline_policies={
        "LambdaExecutionPolicy": iam.PolicyDocument.from_json(policy_document)
    }
)
```

### 3. Script Assets

#### Deployment Scripts:
```bash
#!/bin/bash
# assets/scripts/deployment/pre-deploy.sh

echo "Running pre-deployment checks..."

# Verificar conectividad AWS
aws sts get-caller-identity

# Verificar recursos existentes
aws cloudformation describe-stacks --stack-name my-stack || echo "Stack not found"

echo "Pre-deployment checks completed"
```

#### Database Scripts:
```sql
-- assets/scripts/database/init-schema.sql
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
```

### 4. Template Assets

#### CloudFormation Templates:
```yaml
# assets/templates/cloudformation/custom-resource.yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Custom resource for data initialization'

Resources:
  CustomResourceFunction:
    Type: AWS::Lambda::Function
    Properties:
      Runtime: python3.11
      Handler: index.handler
      Code:
        ZipFile: |
          import json
          import boto3
          def handler(event, context):
              # Custom resource logic
              return {'Status': 'SUCCESS'}
```

#### Docker Templates:
```dockerfile
# assets/templates/docker/Dockerfile.lambda
FROM public.ecr.aws/lambda/python:3.11

# Copiar requirements y instalar dependencias
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install -r requirements.txt

# Copiar código de la función
COPY lambda_function.py ${LAMBDA_TASK_ROOT}

CMD ["lambda_function.lambda_handler"]
```

### 5. Static Assets

Para aplicaciones web o contenido estático:

```html
<!-- assets/static/html/index.html -->
<!DOCTYPE html>
<html>
<head>
    <title>My CDK App</title>
    <link rel="stylesheet" href="/css/styles.css">
</head>
<body>
    <h1>Welcome to My CDK Application</h1>
    <script src="/js/app.js"></script>
</body>
</html>
```

### 6. Configuration Data

```json
// assets/data/config/dev-config.json
{
    "database": {
        "host": "dev-db.example.com",
        "port": 5432,
        "name": "myapp_dev"
    },
    "api": {
        "base_url": "https://dev-api.example.com",
        "timeout": 30
    },
    "features": {
        "debug_mode": true,
        "cache_enabled": false
    }
}
```

## Integración con CDK:

### Asset Bundling:
```python
# Para archivos individuales
policy_doc = _lambda.Code.from_asset("assets/policies/lambda-policy.json")

# Para directorios completos
static_assets = s3_deployment.Source.asset("assets/static")

# Para assets con bundling personalizado
bundled_asset = _lambda.Code.from_asset(
    "assets/lambda/my-function",
    bundling=BundlingOptions(
        image=_lambda.Runtime.PYTHON_3_11.bundling_image,
        command=["bash", "-c", "pip install -r requirements.txt -t /asset-output && cp -au . /asset-output"]
    )
)
```

### S3 Deployment:
```python
s3_deployment.BucketDeployment(
    self, "StaticAssets",
    sources=[s3_deployment.Source.asset("assets/static")],
    destination_bucket=website_bucket,
    destination_key_prefix="static/"
)
```

## Mejores prácticas:

1. **Organización**: Estructura clara por tipo de asset
2. **Versionado**: Incluir assets en control de versiones
3. **Seguridad**: No incluir secretos o credenciales
4. **Optimización**: Minimizar tamaño de assets
5. **Documentation**: Documentar propósito de cada asset
6. **Testing**: Validar assets antes del despliegue
7. **Cleanup**: Remover assets no utilizados
8. **Naming**: Convenciones consistentes de nomenclatura

## Comandos útiles:

```bash
# Validar políticas IAM
aws iam validate-policy-document --policy-document file://assets/policies/iam/my-policy.json

# Validar templates CloudFormation
aws cloudformation validate-template --template-body file://assets/templates/cloudformation/my-template.yaml

# Comprimir assets para Lambda
cd assets/lambda/my-function && zip -r ../../../my-function.zip .

# Sincronizar assets estáticos con S3
aws s3 sync assets/static/ s3://my-bucket/static/ --delete
```
