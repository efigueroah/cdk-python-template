#!/usr/bin/env python3
"""
Plantilla Projen para proyectos AWS CDK con Python
Configuración centralizada para proyectos de infraestructura como código
"""

import os

from projen import Task, TaskStep
from projen.awscdk import AwsCdkPythonApp

# Configuración del proyecto personalizada
module_name = "multi_stack_demo"
project_name = "multi-stack-demo"

# Configuración del proyecto AWS CDK Python
project = AwsCdkPythonApp(
    # Información básica del proyecto
    name=project_name,
    module_name=module_name,
    author_email="efigueroah@gmail.com",
    author_name="Euclides Figueroa",
    version="0.1.0",
    description=f"AWS CDK Python project: multi-stack-demo",
    # Configuración de CDK
    cdk_version="2.150.0",
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
        # CDK Nag para validaciones de seguridad
        "cdk-nag>=2.27.0",
        # Documentación
        "sphinx>=7.2.0",
        "sphinx-rtd-theme>=2.0.0",
        # Utilidades
        "pre-commit>=3.6.0",
    ],
    # Configuración de pytest
    pytest_options={
        "test_match": ["tests/**/*_test.py", "tests/**/test_*.py"],
    },
    # Configuración de sample code (deshabilitado para plantilla)
    sample=False,
)

# Tareas personalizadas para multi-ambiente

# Tarea para síntesis con ambiente específico
synth_task = project.add_task(
    "synth:env", description="Synthesize CDK app for specific environment"
)
synth_task.exec("cdk synth --context environment=${ENV:-dev}")

# Tarea para deploy con ambiente específico
deploy_task = project.add_task(
    "deploy:env", description="Deploy CDK app to specific environment"
)
deploy_task.exec(
    "cdk deploy --context environment=${ENV:-dev} --require-approval never"
)

# Tarea para destroy con ambiente específico
destroy_task = project.add_task(
    "destroy:env", description="Destroy CDK app from specific environment"
)
destroy_task.exec("cdk destroy --context environment=${ENV:-dev} --force")

# Tarea para diff con ambiente específico
diff_task = project.add_task(
    "diff:env", description="Show diff for specific environment"
)
diff_task.exec("cdk diff --context environment=${ENV:-dev}")

# Tarea para formateo de código
format_task = project.add_task("format", description="Format code with black and isort")
format_task.exec("black .")
format_task.exec("isort .")

# Tarea para linting
lint_task = project.add_task("lint", description="Run linting checks")
lint_task.exec("flake8 .")
lint_task.exec("mypy .")

# Generar el proyecto
project.synth()
