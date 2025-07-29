"""
Config Converter para proyectos AWS CDK
Maneja la conversión entre formatos de configuración y la integración con CDK context
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import toml
import yaml


class ConfigConverter:
    """
    Clase para convertir configuraciones entre formatos y manejar la integración con CDK context
    """

    # Formatos soportados y sus extensiones
    SUPPORTED_FORMATS = {"toml": ".toml", "json": ".json", "yaml": ".yaml"}

    def __init__(self, config_dir: str = "config"):
        """
        Inicializar ConfigConverter

        Args:
            config_dir: Directorio donde buscar/guardar archivos de configuración
        """
        self.config_dir = Path(config_dir)

        # Crear directorio si no existe
        if not self.config_dir.exists():
            self.config_dir.mkdir(parents=True, exist_ok=True)

    def convert_file(
        self, input_file: str, output_format: str, output_file: Optional[str] = None
    ) -> str:
        """
        Convertir archivo de configuración a otro formato

        Args:
            input_file: Ruta al archivo de entrada
            output_format: Formato de salida ('toml', 'json', 'yaml')
            output_file: Ruta al archivo de salida (opcional)

        Returns:
            str: Ruta al archivo de salida

        Raises:
            FileNotFoundError: Si el archivo de entrada no existe
            ValueError: Si el formato no es soportado
        """
        input_path = Path(input_file)

        if not input_path.exists():
            raise FileNotFoundError(f"Archivo de entrada no encontrado: {input_path}")

        # Detectar formato de entrada
        input_format = self._detect_format(input_path)

        # Validar formato de salida
        if output_format not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Formato de salida no soportado: {output_format}")

        # Generar nombre de archivo de salida si no se especificó
        if not output_file:
            output_file = input_path.stem + self.SUPPORTED_FORMATS[output_format]
            output_path = self.config_dir / output_file
        else:
            output_path = Path(output_file)

        # Cargar datos del archivo de entrada
        data = self._load_file(input_path, input_format)

        # Guardar datos en el formato de salida
        self._save_file(data, output_path, output_format)

        return str(output_path)

    def import_cdk_context(
        self,
        cdk_json_path: str,
        output_format: str = "toml",
        output_file: Optional[str] = None,
    ) -> str:
        """
        Importar sección context de un archivo cdk.json a un formato específico

        Args:
            cdk_json_path: Ruta al archivo cdk.json
            output_format: Formato de salida ('toml', 'json', 'yaml')
            output_file: Ruta al archivo de salida (opcional)

        Returns:
            str: Ruta al archivo de salida

        Raises:
            FileNotFoundError: Si el archivo cdk.json no existe
            ValueError: Si el formato no es soportado
        """
        cdk_path = Path(cdk_json_path)

        if not cdk_path.exists():
            raise FileNotFoundError(f"Archivo cdk.json no encontrado: {cdk_path}")

        # Validar formato de salida
        if output_format not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Formato de salida no soportado: {output_format}")

        # Generar nombre de archivo de salida si no se especificó
        if not output_file:
            output_file = f"cdk-context{self.SUPPORTED_FORMATS[output_format]}"
            output_path = self.config_dir / output_file
        else:
            output_path = Path(output_file)

        # Cargar datos del archivo cdk.json
        with open(cdk_path, "r", encoding="utf-8") as f:
            cdk_data = json.load(f)

        # Extraer sección context
        context_data = cdk_data.get("context", {})

        # Guardar datos en el formato de salida
        self._save_file(context_data, output_path, output_format)

        return str(output_path)

    def export_to_cdk_context(
        self, config_file: str, cdk_json_path: str, environment: Optional[str] = None
    ) -> str:
        """
        Exportar configuración a la sección context de un archivo cdk.json

        Args:
            config_file: Ruta al archivo de configuración
            cdk_json_path: Ruta al archivo cdk.json
            environment: Ambiente específico (dev, prod, stage, etc.)

        Returns:
            str: Ruta al archivo cdk.json actualizado

        Raises:
            FileNotFoundError: Si alguno de los archivos no existe
        """
        config_path = Path(config_file)
        cdk_path = Path(cdk_json_path)

        if not config_path.exists():
            raise FileNotFoundError(
                f"Archivo de configuración no encontrado: {config_path}"
            )

        # Detectar formato de entrada
        input_format = self._detect_format(config_path)

        # Cargar datos del archivo de configuración
        config_data = self._load_file(config_path, input_format)

        # Si se especificó un ambiente, filtrar configuración
        if environment and "environments" in config_data:
            env_data = config_data.get("environments", {}).get(environment, {})
            if env_data:
                # Fusionar datos base con datos de ambiente
                base_data = {
                    k: v for k, v in config_data.items() if k != "environments"
                }
                config_data = self._deep_merge(base_data, env_data)

        # Cargar o crear archivo cdk.json
        if cdk_path.exists():
            with open(cdk_path, "r", encoding="utf-8") as f:
                cdk_data = json.load(f)
        else:
            cdk_data = {}

        # Actualizar sección context
        if "context" not in cdk_data:
            cdk_data["context"] = {}

        # Fusionar configuración con context existente
        cdk_data["context"] = self._deep_merge(cdk_data["context"], config_data)

        # Guardar archivo cdk.json actualizado
        with open(cdk_path, "w", encoding="utf-8") as f:
            json.dump(cdk_data, f, indent=2)

        return str(cdk_path)

    def _detect_format(self, file_path: Path) -> str:
        """
        Detectar formato basado en la extensión del archivo

        Args:
            file_path: Ruta al archivo

        Returns:
            str: Formato detectado ('toml', 'json', 'yaml')

        Raises:
            ValueError: Si el formato no es soportado
        """
        suffix = file_path.suffix.lower()

        if suffix == ".toml":
            return "toml"
        elif suffix == ".json":
            return "json"
        elif suffix in [".yaml", ".yml"]:
            return "yaml"
        else:
            raise ValueError(f"Formato no soportado para el archivo: {file_path}")

    def _load_file(self, file_path: Path, format_type: str) -> Dict[str, Any]:
        """
        Cargar archivo según su formato

        Args:
            file_path: Ruta al archivo
            format_type: Formato del archivo ('toml', 'json', 'yaml')

        Returns:
            Dict: Datos cargados

        Raises:
            ValueError: Si hay un error al cargar el archivo
        """
        with open(file_path, "r", encoding="utf-8") as f:
            if format_type == "toml":
                return toml.load(f)
            elif format_type == "json":
                return json.load(f)
            elif format_type == "yaml":
                return yaml.safe_load(f)
            else:
                raise ValueError(f"Formato no soportado: {format_type}")

    def _save_file(self, data: Dict[str, Any], file_path: Path, format_type: str):
        """
        Guardar datos en un archivo según el formato especificado

        Args:
            data: Datos a guardar
            file_path: Ruta al archivo
            format_type: Formato del archivo ('toml', 'json', 'yaml')

        Raises:
            ValueError: Si hay un error al guardar el archivo
        """
        with open(file_path, "w", encoding="utf-8") as f:
            if format_type == "toml":
                toml.dump(data, f)
            elif format_type == "json":
                json.dump(data, f, indent=2)
            elif format_type == "yaml":
                yaml.dump(data, f, default_flow_style=False)
            else:
                raise ValueError(f"Formato no soportado: {format_type}")

    def _deep_merge(self, base: Dict, update: Dict) -> Dict:
        """
        Fusión profunda de diccionarios

        Args:
            base: Diccionario base
            update: Diccionario con actualizaciones

        Returns:
            Dict: Diccionario fusionado
        """
        result = base.copy()
        for key, value in update.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result
