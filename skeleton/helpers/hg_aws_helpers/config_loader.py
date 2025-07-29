"""
Config Loader para proyectos AWS CDK
Maneja la carga y validación de archivos de configuración en múltiples formatos
(TOML, JSON, YAML) con soporte para configuraciones multi-ambiente.
"""

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import toml
import yaml


class ConfigSection:
    """
    Clase para acceder a secciones de configuración con notación de atributos
    y soporte para valores por defecto.
    """

    def __init__(self, data: Dict[str, Any]):
        self._data = data or {}

    def __getattr__(self, name: str) -> Union["ConfigSection", Any]:
        """Permite acceso a secciones como atributos: config.project.name"""
        if name in self._data:
            value = self._data[name]
            if isinstance(value, dict):
                return ConfigSection(value)
            return value
        return ConfigSection({})

    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtener valor con soporte para valor por defecto

        Args:
            key: Clave a buscar
            default: Valor por defecto si la clave no existe

        Returns:
            Valor encontrado o valor por defecto
        """
        return self._data.get(key, default)

    def __contains__(self, key: str) -> bool:
        """Permite usar 'in' para verificar si una clave existe"""
        return key in self._data

    def __repr__(self) -> str:
        """Representación legible de la sección"""
        return f"ConfigSection({self._data})"

    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario"""
        return self._data


class ConfigLoader:
    """
    Clase para cargar y manejar configuraciones desde archivos en múltiples formatos
    con soporte para configuraciones multi-ambiente.
    """

    # Formatos soportados y sus extensiones
    SUPPORTED_FORMATS = {
        "toml": [".toml"],
        "json": [".json"],
        "yaml": [".yaml", ".yml"],
    }

    # Cache de configuraciones cargadas
    _cache: Dict[str, Dict[str, Any]] = {}

    def __init__(
        self,
        config_file: Optional[str] = None,
        config_dir: str = "config",
        environment: Optional[str] = None,
        format_type: Optional[str] = None,
    ):
        """
        Inicializar ConfigLoader

        Args:
            config_file: Ruta al archivo de configuración (opcional)
            config_dir: Directorio donde buscar archivos de configuración
            environment: Ambiente específico (dev, prod, stage, etc.)
            format_type: Formato explícito ('toml', 'json', 'yaml')
        """
        self.config_dir = Path(config_dir)
        self.config_file = config_file
        self.environment = environment
        self.format_type = format_type
        self.config_data: Dict[str, Any] = {}

        # Si se proporciona un archivo, cargarlo inmediatamente
        if config_file:
            self.load_config()

    def load_config(self, config_file: Optional[str] = None) -> ConfigSection:
        """
        Cargar archivo de configuración en el formato detectado

        Args:
            config_file: Ruta al archivo de configuración (opcional)

        Returns:
            ConfigSection: Objeto de configuración con acceso por atributos

        Raises:
            FileNotFoundError: Si el archivo no existe
            ValueError: Si el formato no es soportado
        """
        if config_file:
            self.config_file = config_file

        if not self.config_file:
            raise ValueError("No se ha especificado un archivo de configuración")

        config_path = self._resolve_config_path()

        # Verificar cache
        cache_key = str(config_path.absolute())
        if cache_key in self._cache:
            self.config_data = self._cache[cache_key]
            return ConfigSection(self.config_data)

        if not config_path.exists():
            raise FileNotFoundError(
                f"Archivo de configuración no encontrado: {config_path}"
            )

        # Detectar formato si no se especificó
        if not self.format_type:
            self.format_type = self._detect_format(config_path)

        # Cargar configuración según formato
        try:
            self.config_data = self._load_by_format(config_path)

            # Cargar configuración base si existe
            self._merge_base_config()

            # Cargar configuración específica de ambiente si se especificó
            if self.environment:
                self._merge_environment_config()

            # Guardar en cache
            self._cache[cache_key] = self.config_data

            return ConfigSection(self.config_data)

        except Exception as e:
            raise ValueError(
                f"Error al cargar configuración desde {config_path}: {str(e)}"
            )

    def _resolve_config_path(self) -> Path:
        """
        Resolver ruta completa al archivo de configuración

        Returns:
            Path: Ruta absoluta al archivo de configuración
        """
        if os.path.isabs(self.config_file):
            return Path(self.config_file)
        return self.config_dir / self.config_file

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

        for format_name, extensions in self.SUPPORTED_FORMATS.items():
            if suffix in extensions:
                return format_name

        raise ValueError(f"Formato no soportado para el archivo: {file_path}")

    def _load_by_format(self, file_path: Path) -> Dict[str, Any]:
        """
        Cargar archivo según su formato

        Args:
            file_path: Ruta al archivo

        Returns:
            Dict: Datos de configuración cargados

        Raises:
            ValueError: Si hay un error al cargar el archivo
        """
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

            if self.format_type == "toml":
                return toml.loads(content)
            elif self.format_type == "json":
                return json.loads(content)
            elif self.format_type == "yaml":
                return yaml.safe_load(content)
            else:
                raise ValueError(f"Formato no soportado: {self.format_type}")

    def _merge_base_config(self):
        """
        Fusionar con configuración base si existe

        La configuración base puede estar en cualquiera de los formatos soportados.
        Se busca en el siguiente orden: toml, json, yaml.
        """
        for format_name, extensions in self.SUPPORTED_FORMATS.items():
            for ext in extensions:
                base_path = self.config_dir / f"base{ext}"
                if base_path.exists():
                    with open(base_path, "r", encoding="utf-8") as f:
                        if format_name == "toml":
                            base_config = toml.load(f)
                        elif format_name == "json":
                            base_config = json.load(f)
                        elif format_name == "yaml":
                            base_config = yaml.safe_load(f)

                        # Fusionar configuraciones (config actual sobrescribe base)
                        self.config_data = self._deep_merge(
                            base_config, self.config_data
                        )
                    return

    def _merge_environment_config(self):
        """
        Fusionar con configuración específica de ambiente si existe

        La configuración de ambiente puede estar en cualquiera de los formatos soportados.
        """
        env = self.environment.lower()

        for format_name, extensions in self.SUPPORTED_FORMATS.items():
            for ext in extensions:
                env_path = self.config_dir / f"env.{env}{ext}"
                if env_path.exists():
                    with open(env_path, "r", encoding="utf-8") as f:
                        if format_name == "toml":
                            env_config = toml.load(f)
                        elif format_name == "json":
                            env_config = json.load(f)
                        elif format_name == "yaml":
                            env_config = yaml.safe_load(f)

                        # Fusionar configuraciones (ambiente sobrescribe config actual)
                        self.config_data = self._deep_merge(
                            self.config_data, env_config
                        )
                    return

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

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Obtener valor usando notación de punto

        Args:
            key_path: Ruta a la clave usando notación de punto (ej: 'project.name')
            default: Valor por defecto si la clave no existe

        Returns:
            Valor encontrado o valor por defecto
        """
        keys = key_path.split(".")
        value = self.config_data

        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

    def get_section(self, section: str) -> ConfigSection:
        """
        Obtener sección completa como objeto ConfigSection

        Args:
            section: Nombre de la sección

        Returns:
            ConfigSection: Sección de configuración
        """
        return ConfigSection(self.config_data.get(section, {}))

    def get_required(self, key_path: str) -> Any:
        """
        Obtener valor requerido

        Args:
            key_path: Ruta a la clave usando notación de punto

        Returns:
            Valor encontrado

        Raises:
            KeyError: Si la clave no existe
        """
        value = self.get(key_path)
        if value is None:
            raise KeyError(f"Parámetro requerido no encontrado: {key_path}")
        return value

    def validate_required_keys(self, required_keys: List[str]) -> bool:
        """
        Validar claves requeridas

        Args:
            required_keys: Lista de claves requeridas

        Returns:
            bool: True si todas las claves existen

        Raises:
            KeyError: Si alguna clave no existe
        """
        missing_keys = []

        for key in required_keys:
            if self.get(key) is None:
                missing_keys.append(key)

        if missing_keys:
            raise KeyError(
                f"Parámetros requeridos faltantes: {', '.join(missing_keys)}"
            )

        return True

    def get_aws_config(self) -> Dict[str, Any]:
        """
        Obtener configuración de AWS

        Returns:
            Dict: Configuración de AWS
        """
        return {
            "account_id": self.get("aws.account_id"),
            "region": self.get("aws.region"),
            "tags": self.get("project.tags", {}),
        }

    def to_dict(self) -> Dict[str, Any]:
        """
        Convertir configuración a diccionario

        Returns:
            Dict: Configuración como diccionario
        """
        return self.config_data

    @classmethod
    def from_file(
        cls,
        config_file: str,
        config_dir: str = "config",
        environment: Optional[str] = None,
        format_type: Optional[str] = None,
    ) -> "ConfigLoader":
        """
        Crear ConfigLoader desde archivo

        Args:
            config_file: Ruta al archivo de configuración
            config_dir: Directorio donde buscar archivos de configuración
            environment: Ambiente específico (dev, prod, stage, etc.)
            format_type: Formato explícito ('toml', 'json', 'yaml')

        Returns:
            ConfigLoader: Instancia de ConfigLoader
        """
        loader = cls(
            config_file=config_file,
            config_dir=config_dir,
            environment=environment,
            format_type=format_type,
        )
        loader.load_config()
        return loader
