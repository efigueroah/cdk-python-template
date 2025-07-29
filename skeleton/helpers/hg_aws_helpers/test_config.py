"""
Pruebas unitarias para ConfigLoader y ConfigConverter
"""

import json
import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import toml
import yaml
from config_converter import ConfigConverter
from config_loader import ConfigLoader, ConfigSection


class TestConfigSection(unittest.TestCase):
    """Pruebas para la clase ConfigSection"""

    def test_attribute_access(self):
        """Probar acceso a atributos"""
        data = {
            "project": {"name": "test-project", "environment": "dev"},
            "aws": {"region": "us-east-1"},
        }

        section = ConfigSection(data)

        # Acceso a atributos existentes
        self.assertEqual(section.project.name, "test-project")
        self.assertEqual(section.project.environment, "dev")
        self.assertEqual(section.aws.region, "us-east-1")

        # Acceso a atributos no existentes
        self.assertEqual(section.database.host, {})

        # Método get con valor por defecto
        self.assertEqual(
            section.project.get("description", "No description"), "No description"
        )
        self.assertEqual(section.project.get("name"), "test-project")

    def test_to_dict(self):
        """Probar conversión a diccionario"""
        data = {"key": "value", "nested": {"key": "value"}}
        section = ConfigSection(data)
        self.assertEqual(section.to_dict(), data)


class TestConfigLoader(unittest.TestCase):
    """Pruebas para la clase ConfigLoader"""

    def setUp(self):
        """Configuración inicial para las pruebas"""
        self.temp_dir = TemporaryDirectory()
        self.config_dir = Path(self.temp_dir.name)

        # Crear archivos de prueba
        self._create_test_files()

    def tearDown(self):
        """Limpieza después de las pruebas"""
        self.temp_dir.cleanup()

    def _create_test_files(self):
        """Crear archivos de prueba"""
        # Archivo base.toml
        base_toml = """
[project]
name = "test-project"
description = "Test project"

[aws]
region = "us-east-1"
account_id = "123456789012"

[network]
vpc_cidr = "10.0.0.0/16"
nat_gateways = 1
"""

        with open(self.config_dir / "base.toml", "w", encoding="utf-8") as f:
            f.write(base_toml)

        # Archivo env.dev.toml
        dev_toml = """
[project]
environment = "dev"

[network]
nat_gateways = 1
"""

        with open(self.config_dir / "env.dev.toml", "w", encoding="utf-8") as f:
            f.write(dev_toml)

        # Archivo env.prod.toml
        prod_toml = """
[project]
environment = "prod"

[network]
nat_gateways = 3
"""

        with open(self.config_dir / "env.prod.toml", "w", encoding="utf-8") as f:
            f.write(prod_toml)

        # Archivo proyecto-test.toml
        project_toml = """
[project]
name = "proyecto-test"
tags = { Owner = "DevOps", Environment = "Development" }
"""

        with open(self.config_dir / "proyecto-test.toml", "w", encoding="utf-8") as f:
            f.write(project_toml)

        # Archivo proyecto-test.json
        project_json = {
            "project": {
                "name": "proyecto-test-json",
                "tags": {"Owner": "DevOps", "Environment": "Development"},
            }
        }

        with open(self.config_dir / "proyecto-test.json", "w", encoding="utf-8") as f:
            json.dump(project_json, f, indent=2)

        # Archivo proyecto-test.yaml
        project_yaml = """
project:
  name: proyecto-test-yaml
  tags:
    Owner: DevOps
    Environment: Development
"""

        with open(self.config_dir / "proyecto-test.yaml", "w", encoding="utf-8") as f:
            f.write(project_yaml)

    def test_load_toml_config(self):
        """Probar carga de configuración TOML"""
        loader = ConfigLoader(
            config_file="proyecto-test.toml", config_dir=str(self.config_dir)
        )

        config = loader.load_config()

        self.assertEqual(config.project.name, "proyecto-test")
        self.assertEqual(config.project.tags.get("Owner"), "DevOps")

        # Verificar fusión con base.toml
        self.assertEqual(config.aws.region, "us-east-1")
        self.assertEqual(config.network.vpc_cidr, "10.0.0.0/16")

    def test_load_json_config(self):
        """Probar carga de configuración JSON"""
        loader = ConfigLoader(
            config_file="proyecto-test.json", config_dir=str(self.config_dir)
        )

        config = loader.load_config()

        self.assertEqual(config.project.name, "proyecto-test-json")
        self.assertEqual(config.project.tags.get("Owner"), "DevOps")

        # Verificar fusión con base.toml
        self.assertEqual(config.aws.region, "us-east-1")

    def test_load_yaml_config(self):
        """Probar carga de configuración YAML"""
        loader = ConfigLoader(
            config_file="proyecto-test.yaml", config_dir=str(self.config_dir)
        )

        config = loader.load_config()

        self.assertEqual(config.project.name, "proyecto-test-yaml")
        self.assertEqual(config.project.tags.get("Owner"), "DevOps")

        # Verificar fusión con base.toml
        self.assertEqual(config.aws.region, "us-east-1")

    def test_environment_config(self):
        """Probar configuración con ambiente específico"""
        # Ambiente dev
        dev_loader = ConfigLoader(
            config_file="proyecto-test.toml",
            config_dir=str(self.config_dir),
            environment="dev",
        )

        dev_config = dev_loader.load_config()

        self.assertEqual(dev_config.project.environment, "dev")
        self.assertEqual(dev_config.network.nat_gateways, 1)

        # Ambiente prod
        prod_loader = ConfigLoader(
            config_file="proyecto-test.toml",
            config_dir=str(self.config_dir),
            environment="prod",
        )

        prod_config = prod_loader.load_config()

        self.assertEqual(prod_config.project.environment, "prod")
        self.assertEqual(prod_config.network.nat_gateways, 3)

    def test_get_methods(self):
        """Probar métodos get"""
        loader = ConfigLoader(
            config_file="proyecto-test.toml", config_dir=str(self.config_dir)
        )

        loader.load_config()

        # Método get con notación de punto
        self.assertEqual(loader.get("project.name"), "proyecto-test")
        self.assertEqual(loader.get("aws.region"), "us-east-1")

        # Método get con valor por defecto
        self.assertEqual(loader.get("database.host", "localhost"), "localhost")

        # Método get_section
        aws_section = loader.get_section("aws")
        self.assertEqual(aws_section.get("region"), "us-east-1")
        self.assertEqual(aws_section.get("account_id"), "123456789012")

    def test_required_keys(self):
        """Probar validación de claves requeridas"""
        loader = ConfigLoader(
            config_file="proyecto-test.toml", config_dir=str(self.config_dir)
        )

        loader.load_config()

        # Claves existentes
        self.assertTrue(loader.validate_required_keys(["project.name", "aws.region"]))

        # Claves no existentes
        with self.assertRaises(KeyError):
            loader.validate_required_keys(["database.host", "database.port"])

        # Método get_required
        self.assertEqual(loader.get_required("project.name"), "proyecto-test")

        with self.assertRaises(KeyError):
            loader.get_required("database.host")

    def test_aws_config(self):
        """Probar método get_aws_config"""
        loader = ConfigLoader(
            config_file="proyecto-test.toml", config_dir=str(self.config_dir)
        )

        loader.load_config()

        aws_config = loader.get_aws_config()

        self.assertEqual(aws_config["account_id"], "123456789012")
        self.assertEqual(aws_config["region"], "us-east-1")
        self.assertEqual(aws_config["tags"]["Owner"], "DevOps")


class TestConfigConverter(unittest.TestCase):
    """Pruebas para la clase ConfigConverter"""

    def setUp(self):
        """Configuración inicial para las pruebas"""
        self.temp_dir = TemporaryDirectory()
        self.config_dir = Path(self.temp_dir.name)

        # Crear archivos de prueba
        self._create_test_files()

    def tearDown(self):
        """Limpieza después de las pruebas"""
        self.temp_dir.cleanup()

    def _create_test_files(self):
        """Crear archivos de prueba"""
        # Archivo proyecto-test.toml
        project_toml = """
[project]
name = "proyecto-test"
tags = { Owner = "DevOps", Environment = "Development" }

[aws]
region = "us-east-1"
account_id = "123456789012"
"""

        with open(self.config_dir / "proyecto-test.toml", "w", encoding="utf-8") as f:
            f.write(project_toml)

        # Archivo cdk.json
        cdk_json = """{
  "app": "npx ts-node --prefer-ts-exts bin/my-cdk-app.ts",
  "context": {
    "@aws-cdk/core:enableStackNameDuplicates": "true",
    "aws-cdk:enableDiffNoFail": "true"
  }
}"""

        with open(self.config_dir / "cdk.json", "w", encoding="utf-8") as f:
            f.write(cdk_json)

    def test_convert_toml_to_json(self):
        """Probar conversión de TOML a JSON"""
        converter = ConfigConverter(config_dir=str(self.config_dir))

        json_file = converter.convert_file(
            input_file=str(self.config_dir / "proyecto-test.toml"), output_format="json"
        )

        # Verificar que el archivo existe
        self.assertTrue(Path(json_file).exists())

        # Verificar contenido
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(data["project"]["name"], "proyecto-test")
        self.assertEqual(data["aws"]["region"], "us-east-1")

    def test_convert_toml_to_yaml(self):
        """Probar conversión de TOML a YAML"""
        converter = ConfigConverter(config_dir=str(self.config_dir))

        yaml_file = converter.convert_file(
            input_file=str(self.config_dir / "proyecto-test.toml"), output_format="yaml"
        )

        # Verificar que el archivo existe
        self.assertTrue(Path(yaml_file).exists())

        # Verificar contenido
        with open(yaml_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        self.assertEqual(data["project"]["name"], "proyecto-test")
        self.assertEqual(data["aws"]["region"], "us-east-1")

    def test_import_cdk_context(self):
        """Probar importación de CDK context"""
        converter = ConfigConverter(config_dir=str(self.config_dir))

        toml_file = converter.import_cdk_context(
            cdk_json_path=str(self.config_dir / "cdk.json"), output_format="toml"
        )

        # Verificar que el archivo existe
        self.assertTrue(Path(toml_file).exists())

        # Verificar contenido
        with open(toml_file, "r", encoding="utf-8") as f:
            data = toml.load(f)

        self.assertEqual(data["@aws-cdk/core:enableStackNameDuplicates"], "true")
        self.assertEqual(data["aws-cdk:enableDiffNoFail"], "true")

    def test_export_to_cdk_context(self):
        """Probar exportación a CDK context"""
        converter = ConfigConverter(config_dir=str(self.config_dir))

        cdk_file = converter.export_to_cdk_context(
            config_file=str(self.config_dir / "proyecto-test.toml"),
            cdk_json_path=str(self.config_dir / "cdk.json"),
        )

        # Verificar que el archivo existe
        self.assertTrue(Path(cdk_file).exists())

        # Verificar contenido
        with open(cdk_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(data["context"]["project"]["name"], "proyecto-test")
        self.assertEqual(data["context"]["aws"]["region"], "us-east-1")
        self.assertEqual(
            data["context"]["@aws-cdk/core:enableStackNameDuplicates"], "true"
        )


if __name__ == "__main__":
    unittest.main()
