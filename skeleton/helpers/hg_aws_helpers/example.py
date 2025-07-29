"""
Ejemplo de uso de las clases ConfigLoader y ConfigConverter
"""

import os
from pathlib import Path

from config_converter import ConfigConverter
from config_loader import ConfigLoader


def create_example_files():
    """Crear archivos de ejemplo para demostrar el uso de las clases"""
    # Crear directorio de configuración si no existe
    config_dir = Path("./example_config")
    config_dir.mkdir(exist_ok=True)

    # Crear archivo base.toml
    base_toml = """
[project]
name = "proyecto-ejemplo"
description = "Proyecto de ejemplo para demostrar el uso de ConfigLoader"

[aws]
region = "us-east-1"
account_id = "123456789012"

[network]
vpc_cidr = "10.0.0.0/16"
nat_gateways = 1
"""

    with open(config_dir / "base.toml", "w", encoding="utf-8") as f:
        f.write(base_toml)

    # Crear archivo de ambiente dev
    dev_toml = """
[project]
environment = "dev"

[network]
nat_gateways = 1
"""

    with open(config_dir / "env.dev.toml", "w", encoding="utf-8") as f:
        f.write(dev_toml)

    # Crear archivo de ambiente prod
    prod_toml = """
[project]
environment = "prod"

[network]
nat_gateways = 3
"""

    with open(config_dir / "env.prod.toml", "w", encoding="utf-8") as f:
        f.write(prod_toml)

    # Crear archivo de proyecto específico
    project_toml = """
[project]
name = "proyecto-ejemplo-dev"
tags = { Owner = "DevOps", Environment = "Development" }
"""

    with open(config_dir / "proyecto-ejemplo-dev.toml", "w", encoding="utf-8") as f:
        f.write(project_toml)

    # Crear archivo cdk.json de ejemplo
    cdk_json = """{
  "app": "npx ts-node --prefer-ts-exts bin/my-cdk-app.ts",
  "context": {
    "@aws-cdk/core:enableStackNameDuplicates": "true",
    "aws-cdk:enableDiffNoFail": "true",
    "@aws-cdk/core:stackRelativeExports": "true"
  }
}"""

    with open(config_dir / "cdk.json", "w", encoding="utf-8") as f:
        f.write(cdk_json)

    print(f"Archivos de ejemplo creados en {config_dir}")


def example_config_loader():
    """Ejemplo de uso de ConfigLoader"""
    print("\n=== Ejemplo de uso de ConfigLoader ===\n")

    # Cargar configuración básica
    config_loader = ConfigLoader(
        config_file="proyecto-ejemplo-dev.toml",
        config_dir="./example_config",
        environment="dev",
    )

    config = config_loader.load_config()

    # Acceso a parámetros con notación de atributos
    print(f"Nombre del proyecto: {config.project.name}")
    print(f"Ambiente: {config.project.environment}")
    print(f"Región AWS: {config.aws.region}")

    # Acceso a parámetros con método get() y valores por defecto
    nat_gateways = config.network.get("nat_gateways", 2)
    print(f"NAT Gateways: {nat_gateways}")

    # Acceso a parámetros que no existen con valores por defecto
    database_instances = config.database.get("instances", 1)
    print(f"Instancias de base de datos: {database_instances}")

    # Cargar configuración para ambiente prod
    prod_config_loader = ConfigLoader(
        config_file="proyecto-ejemplo-dev.toml",
        config_dir="./example_config",
        environment="prod",
    )

    prod_config = prod_config_loader.load_config()

    # Comparar valores entre ambientes
    print(f"\nComparación entre ambientes:")
    print(f"NAT Gateways (dev): {config.network.get('nat_gateways')}")
    print(f"NAT Gateways (prod): {prod_config.network.get('nat_gateways')}")


def example_config_converter():
    """Ejemplo de uso de ConfigConverter"""
    print("\n=== Ejemplo de uso de ConfigConverter ===\n")

    converter = ConfigConverter(config_dir="./example_config")

    # Convertir archivo TOML a JSON
    json_file = converter.convert_file(
        input_file="./example_config/proyecto-ejemplo-dev.toml", output_format="json"
    )
    print(f"Archivo convertido a JSON: {json_file}")

    # Convertir archivo TOML a YAML
    yaml_file = converter.convert_file(
        input_file="./example_config/proyecto-ejemplo-dev.toml", output_format="yaml"
    )
    print(f"Archivo convertido a YAML: {yaml_file}")

    # Importar sección context de cdk.json a TOML
    toml_context = converter.import_cdk_context(
        cdk_json_path="./example_config/cdk.json", output_format="toml"
    )
    print(f"Context de CDK importado a TOML: {toml_context}")

    # Exportar configuración a sección context de cdk.json
    updated_cdk = converter.export_to_cdk_context(
        config_file="./example_config/proyecto-ejemplo-dev.toml",
        cdk_json_path="./example_config/cdk.json",
        environment="dev",
    )
    print(f"Configuración exportada a CDK context: {updated_cdk}")


if __name__ == "__main__":
    create_example_files()
    example_config_loader()
    example_config_converter()
