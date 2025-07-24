#!/usr/bin/env python3
"""
Plantilla Projen para proyectos AWS CDK con Python
Configuración centralizada para proyectos de infraestructura como código
"""

from projen.awscdk import AwsCdkPythonApp
from projen import Task, TaskStep
import os

# Obtener el nombre del módulo desde las opciones del proyecto
module_name = os.environ.get('PROJEN_MODULE_NAME', 'my_cdk_app')
project_name = os.environ.get('PROJEN_PROJECT_NAME', 'my-cdk-project')

# Configuración del proyecto AWS CDK Python
project = AwsCdkPythonApp(
    # Información básica del proyecto
    name=project_name,
    module_name=module_name,
    author_email="devops@myorg.com",
    author_name="DevOps Team",
    version="0.1.0",
    description=f"AWS CDK Python project: {project_name}",
    
    # Configuración de Python y CDK
    python_version="3.11",
    cdk_version="2.150.0",
    
    # Configuración de Git
    git_ignore_options={
        "ignore_patterns": [
            # Python
            "__pycache__/",
            "*.py[cod]",
            "*$py.class",
            "*.so",
            ".Python",
            "build/",
            "develop-eggs/",
            "dist/",
            "downloads/",
            "eggs/",
            ".eggs/",
            "lib/",
            "lib64/",
            "parts/",
            "sdist/",
            "var/",
            "wheels/",
            "*.egg-info/",
            ".installed.cfg",
            "*.egg",
            
            # CDK
            "*.d.ts",
            "*.js",
            "node_modules/",
            "cdk.out/",
            "cdk.context.json",
            
            # IDE
            ".vscode/settings.json",
            ".idea/",
            "*.swp",
            "*.swo",
            "*~",
            
            # OS
            ".DS_Store",
            "Thumbs.db",
            
            # Logs
            "*.log",
            "logs/",
            
            # Environment
            ".env",
            ".env.local",
            ".env.*.local",
            
            # Documentation build
            "docs/_build/",
            "docs/build/",
            
            # Coverage
            ".coverage",
            "htmlcov/",
            ".pytest_cache/",
        ]
    },
    
    # Configuración de dependencias de producción
    deps=[
        "aws-cdk-lib>=2.150.0",
        "constructs>=10.0.0",
        "boto3>=1.34.0",
        "pydantic>=2.5.0",
        "python-dotenv>=1.0.0",
    ],
    
    # Configuración de dependencias de desarrollo
    dev_deps=[
        # Testing
        "pytest>=7.4.0",
        "pytest-cov>=4.1.0",
        "pytest-mock>=3.12.0",
        "moto>=4.2.0",
        
        # Linting y formateo
        "black>=23.12.0",
        "flake8>=6.1.0",
        "isort>=5.13.0",
        "mypy>=1.8.0",
        "bandit>=1.7.5",
        
        # CDK específico
        "aws-cdk.assertions>=2.150.0",
        "cdk-nag>=2.27.0",
        
        # Documentación
        "sphinx>=7.2.0",
        "sphinx-rtd-theme>=2.0.0",
        "sphinx-autodoc-typehints>=1.25.0",
        "sphinxcontrib-mermaid>=0.9.2",
        "cdk-dia>=0.8.0",
        
        # Utilidades
        "pre-commit>=3.6.0",
        "commitizen>=3.13.0",
    ],
    
    # Configuración de pytest
    pytest_options={
        "test_match": ["tests/**/*_test.py", "tests/**/test_*.py"],
        "pytest_ini_options": {
            "testpaths": ["tests"],
            "python_files": ["test_*.py", "*_test.py"],
            "python_classes": ["Test*"],
            "python_functions": ["test_*"],
            "addopts": [
                "--verbose",
                "--tb=short",
                "--cov=src",
                "--cov-report=html",
                "--cov-report=term-missing",
                "--cov-fail-under=80"
            ]
        }
    },
    
    # Configuración de sample code (deshabilitado para plantilla)
    sample=False,
)

# Configuración de contexto CDK para multi-ambiente
project.cdk_config.context.update({
    "@aws-cdk/aws-lambda:recognizeLayerVersion": True,
    "@aws-cdk/core:checkSecretUsage": True,
    "@aws-cdk/core:target-partitions": ["aws", "aws-cn"],
    "@aws-cdk/aws-autoscaling:generateLaunchTemplateInsteadOfLaunchConfig": True,
    "@aws-cdk/aws-iam:minimizePolicies": True,
    "@aws-cdk/core:validateSnapshotRemovalPolicy": True,
    "@aws-cdk/aws-codepipeline:crossAccountKeyAliasStackSafeResourceName": True,
    "@aws-cdk/aws-s3:createDefaultLoggingPolicy": True,
    "@aws-cdk/aws-sns-subscriptions:restrictSqsDescryption": True,
    "@aws-cdk/aws-apigateway:disableCloudWatchRole": False,
    "@aws-cdk/core:enablePartitionLiterals": True,
    "@aws-cdk/aws-events:eventsTargetQueueSameAccount": True,
    "@aws-cdk/aws-iam:standardizedServicePrincipals": True,
    "@aws-cdk/aws-ecs:disableExplicitDeploymentControllerForCircuitBreaker": True,
    "@aws-cdk/aws-iam:importedRoleStackSafeDefaultPolicyName": True,
    "@aws-cdk/aws-s3:serverAccessLogsUseBucketPolicy": True,
    "@aws-cdk/aws-route53-patters:useCertificate": True,
    "@aws-cdk/customresources:installLatestAwsSdkDefault": False,
    "@aws-cdk/aws-rds:databaseProxyUniqueResourceName": True,
    "@aws-cdk/aws-codedeploy:removeAlarmsFromDeploymentGroup": True,
    "@aws-cdk/aws-apigateway:authorizerChangeDeploymentLogicalId": True,
    "@aws-cdk/aws-ec2:launchTemplateDefaultUserData": True,
    "@aws-cdk/aws-secretsmanager:useAttachedSecretResourcePolicyForSecretTargetAttachments": True,
    "@aws-cdk/aws-redshift:columnId": True,
    "@aws-cdk/aws-stepfunctions-tasks:enableLogging": True,
    "@aws-cdk/aws-ec2:restrictDefaultSecurityGroup": True,
    "@aws-cdk/aws-apigateway:requestValidatorUniqueId": True,
    "@aws-cdk/aws-kms:aliasNameRef": True,
    "@aws-cdk/aws-autoscaling:generateLaunchTemplateInsteadOfLaunchConfig": True,
    "@aws-cdk/core:includePrefixInUniqueNameGeneration": True,
    "@aws-cdk/aws-opensearchservice:enableLogging": True,
    "@aws-cdk/aws-neptune:clusterParameterGroupPortFix": True,
    "@aws-cdk/aws-efs:denyAnonymousAccess": True,
    "@aws-cdk/aws-opensearchservice:enforceHttps": True,
    "@aws-cdk/aws-s3:eventBridgeNotificationToSns": True,
    "@aws-cdk/aws-cloudfront-origins:useOriginAccessControlForS3Origins": True,
    "@aws-cdk/aws-codepipeline:defaultPipelineTypeToV2": True,
    "@aws-cdk/aws-kms:reduceCrossAccountRegionPolicyScope": True,
    "@aws-cdk/aws-eks:nodegroupNameAttribute": True,
    "@aws-cdk/aws-ec2:ebsDefaultGp3Volume": True,
    "@aws-cdk/aws-ecs:removeDefaultDeploymentAlarm": False,
    
    # Configuración de ambientes
    "environments": {
        "dev": {
            "account": "123456789012",  # Placeholder - debe ser reemplazado
            "region": "us-east-1"
        },
        "prod": {
            "account": "123456789012",  # Placeholder - debe ser reemplazado
            "region": "us-east-1"
        }
    },
    "default_env": "dev"
})

# Tareas personalizadas para multi-ambiente

# Tarea para síntesis con ambiente específico
synth_task = project.add_task("synth:env", 
    description="Synthesize CDK app for specific environment",
    steps=[
        TaskStep.exec("cdk synth --context environment=${ENV:-dev}")
    ]
)

# Tarea para deploy con ambiente específico
deploy_task = project.add_task("deploy:env",
    description="Deploy CDK app to specific environment", 
    steps=[
        TaskStep.exec("cdk deploy --context environment=${ENV:-dev} --require-approval never")
    ]
)

# Tarea para destroy con ambiente específico
destroy_task = project.add_task("destroy:env",
    description="Destroy CDK app from specific environment",
    steps=[
        TaskStep.exec("cdk destroy --context environment=${ENV:-dev} --force")
    ]
)

# Tarea para diff con ambiente específico
diff_task = project.add_task("diff:env",
    description="Show diff for specific environment",
    steps=[
        TaskStep.exec("cdk diff --context environment=${ENV:-dev}")
    ]
)

# Tareas de documentación
docs_build_task = project.add_task("docs:build",
    description="Build documentation with Sphinx",
    steps=[
        TaskStep.exec("sphinx-build -b html docs docs/_build/html")
    ]
)

docs_clean_task = project.add_task("docs:clean",
    description="Clean documentation build",
    steps=[
        TaskStep.exec("rm -rf docs/_build/")
    ]
)

docs_open_task = project.add_task("docs:open",
    description="Open documentation in browser",
    steps=[
        TaskStep.exec("python -m webbrowser docs/_build/html/index.html")
    ]
)

# Tarea para generar diagrama de arquitectura
diagram_task = project.add_task("diagram",
    description="Generate architecture diagram",
    steps=[
        TaskStep.exec("cdk-dia --target docs/architecture.png")
    ]
)

# Tarea para análisis de seguridad con CDK Nag
security_task = project.add_task("security",
    description="Run security analysis with CDK Nag",
    steps=[
        TaskStep.exec("python -c \"from cdk_nag import AwsSolutionsChecks; print('CDK Nag configured - run synth to see security checks')\"")
    ]
)

# Tarea para formateo de código
format_task = project.add_task("format",
    description="Format code with black and isort",
    steps=[
        TaskStep.exec("black src/ tests/"),
        TaskStep.exec("isort src/ tests/")
    ]
)

# Tarea para linting
lint_task = project.add_task("lint",
    description="Run linting checks",
    steps=[
        TaskStep.exec("flake8 src/ tests/"),
        TaskStep.exec("mypy src/"),
        TaskStep.exec("bandit -r src/")
    ]
)

# Tarea para pre-commit hooks
precommit_task = project.add_task("pre-commit",
    description="Run pre-commit hooks",
    steps=[
        TaskStep.exec("pre-commit run --all-files")
    ]
)

# Copiar archivos del skeleton
project.add_files_from_dir("skeleton")

# Configuración adicional de archivos
project.add_git_ignore("*.pyc")
project.add_git_ignore("__pycache__/")
project.add_git_ignore(".env")
project.add_git_ignore("cdk.out/")
project.add_git_ignore("docs/_build/")

# Generar el proyecto
project.synth()
