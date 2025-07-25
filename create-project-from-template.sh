#!/bin/bash

# Script para crear un nuevo proyecto CDK Python usando el template desde GitHub
# Uso: ./create-project-from-template.sh <nombre-proyecto> <nombre-modulo> [repo-url]

set -e

# Configuración por defecto
DEFAULT_TEMPLATE_REPO="https://github.com/efigueroah/cdk-python-template.git"
TEMP_DIR="temp-template-$$"

# Función para limpiar archivos temporales
cleanup() {
    if [ -d "$TEMP_DIR" ]; then
        echo "🧹 Limpiando archivos temporales..."
        rm -rf "$TEMP_DIR"
    fi
}

# Configurar trap para limpiar en caso de error
trap cleanup EXIT

# Función para mostrar ayuda
show_help() {
    echo "Uso: $0 <nombre-proyecto> <nombre-modulo> [repo-url]"
    echo ""
    echo "Argumentos:"
    echo "  nombre-proyecto    Nombre del proyecto (ej: my-infrastructure)"
    echo "  nombre-modulo      Nombre del módulo Python (ej: my_infrastructure)"
    echo "  repo-url          URL del repositorio template (opcional)"
    echo ""
    echo "Ejemplos:"
    echo "  $0 my-infrastructure my_infrastructure"
    echo "  $0 my-app my_app https://github.com/usuario/mi-template.git"
    echo ""
    echo "Repositorio por defecto: $DEFAULT_TEMPLATE_REPO"
}

# Verificar argumentos
if [ $# -lt 2 ] || [ $# -gt 3 ]; then
    echo "❌ Error: Número incorrecto de argumentos"
    echo ""
    show_help
    exit 1
fi

PROJECT_NAME=$1
MODULE_NAME=$2
TEMPLATE_REPO=${3:-$DEFAULT_TEMPLATE_REPO}

# Validar nombres
if [[ ! "$PROJECT_NAME" =~ ^[a-zA-Z0-9_-]+$ ]]; then
    echo "❌ Error: El nombre del proyecto solo puede contener letras, números, guiones y guiones bajos"
    exit 1
fi

if [[ ! "$MODULE_NAME" =~ ^[a-zA-Z_][a-zA-Z0-9_]*$ ]]; then
    echo "❌ Error: El nombre del módulo debe ser un identificador Python válido"
    exit 1
fi

# Verificar que el directorio del proyecto no exista
if [ -d "$PROJECT_NAME" ]; then
    echo "❌ Error: El directorio '$PROJECT_NAME' ya existe"
    exit 1
fi

echo "🚀 Creando proyecto '$PROJECT_NAME' con módulo '$MODULE_NAME'..."
echo "📦 Usando template: $TEMPLATE_REPO"

# Verificar dependencias
echo "🔍 Verificando dependencias..."
command -v git >/dev/null 2>&1 || { echo "❌ Error: git no está instalado"; exit 1; }
command -v projen >/dev/null 2>&1 || { echo "❌ Error: projen no está instalado. Instalar con: npm install -g projen"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "❌ Error: python3 no está instalado"; exit 1; }

# Crear enlace simbólico de python si no existe
if ! command -v python >/dev/null 2>&1; then
    echo "🔗 Creando enlace simbólico python -> python3..."
    if command -v sudo >/dev/null 2>&1; then
        sudo ln -sf $(which python3) /usr/local/bin/python 2>/dev/null || {
            echo "⚠️  No se pudo crear enlace simbólico global. Continuando..."
        }
    fi
fi

# Descargar template desde GitHub
echo "⬇️  Descargando template desde GitHub..."
git clone --depth 1 "$TEMPLATE_REPO" "$TEMP_DIR" || {
    echo "❌ Error: No se pudo clonar el repositorio $TEMPLATE_REPO"
    echo "   Verifica que la URL sea correcta y que tengas acceso al repositorio"
    exit 1
}

# Verificar que el template tenga la estructura correcta
if [ ! -f "$TEMP_DIR/.projen/main.py" ]; then
    echo "❌ Error: El repositorio no parece ser un template de Projen válido"
    echo "   Se esperaba encontrar el archivo .projen/main.py"
    exit 1
fi

echo "✅ Template descargado correctamente"

# Crear directorio temporal para el proyecto
TEMP_PROJECT_DIR="temp-project-$$"
mkdir "$TEMP_PROJECT_DIR"
cd "$TEMP_PROJECT_DIR"

# Crear proyecto base con projen
echo "📦 Creando proyecto base con Projen..."
projen new awscdk-app-py --name "$PROJECT_NAME" --module-name "$MODULE_NAME"

# Crear .projenrc.py simplificado basado en el template
echo "⚙️  Aplicando configuración del template..."

cat > .projenrc.py << EOF
#!/usr/bin/env python3
"""
Plantilla Projen para proyectos AWS CDK con Python
Configuración centralizada para proyectos de infraestructura como código
"""

from projen.awscdk import AwsCdkPythonApp
from projen import Task, TaskStep
import os

# Configuración del proyecto personalizada
module_name = '$MODULE_NAME'
project_name = '$PROJECT_NAME'

# Configuración del proyecto AWS CDK Python
project = AwsCdkPythonApp(
    # Información básica del proyecto
    name=project_name,
    module_name=module_name,
    author_email="efigueroah@gmail.com",
    author_name="Euclides Figueroa",
    version="0.1.0",
    description=f"AWS CDK Python project: {project_name}",
    
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
synth_task = project.add_task("synth:env", 
    description="Synthesize CDK app for specific environment")
synth_task.exec("cdk synth --context environment=\${ENV:-dev}")

# Tarea para deploy con ambiente específico
deploy_task = project.add_task("deploy:env",
    description="Deploy CDK app to specific environment")
deploy_task.exec("cdk deploy --context environment=\${ENV:-dev} --require-approval never")

# Tarea para destroy con ambiente específico
destroy_task = project.add_task("destroy:env",
    description="Destroy CDK app from specific environment")
destroy_task.exec("cdk destroy --context environment=\${ENV:-dev} --force")

# Tarea para diff con ambiente específico
diff_task = project.add_task("diff:env",
    description="Show diff for specific environment")
diff_task.exec("cdk diff --context environment=\${ENV:-dev}")

# Tarea para formateo de código
format_task = project.add_task("format",
    description="Format code with black and isort")
format_task.exec("black .")
format_task.exec("isort .")

# Tarea para linting
lint_task = project.add_task("lint",
    description="Run linting checks")
lint_task.exec("flake8 .")
lint_task.exec("mypy .")

# Generar el proyecto
project.synth()
EOF

echo "✅ Configuración adaptada correctamente"

# Copiar archivos del skeleton si existe
if [ -d "../$TEMP_DIR/skeleton" ]; then
    echo "📁 Copiando archivos del skeleton..."
    
    # Copiar archivos normales
    find "../$TEMP_DIR/skeleton" -type f -not -path "*/.*" -exec cp {} . \; 2>/dev/null || true
    
    # Copiar directorios y archivos ocultos
    for item in "../$TEMP_DIR/skeleton"/{*,.*}; do
        if [ -e "$item" ] && [ "$(basename "$item")" != "." ] && [ "$(basename "$item")" != ".." ]; then
            cp -r "$item" . 2>/dev/null || true
        fi
    done
    
    echo "✅ Archivos del skeleton copiados"
else
    echo "ℹ️  No se encontró directorio skeleton en el template"
fi

# Función para sustituir variables en nombres de archivos y directorios
substitute_template_variables() {
    echo "🔄 Sustituyendo variables del template..."
    
    # Sustituir en nombres de directorios (de más profundo a menos profundo)
    find . -depth -type d -name "*{module_name}*" | while read -r dir; do
        new_dir=$(echo "$dir" | sed "s/{module_name}/$MODULE_NAME/g")
        if [ "$dir" != "$new_dir" ]; then
            echo "   📁 Renombrando directorio: $dir -> $new_dir"
            mv "$dir" "$new_dir" 2>/dev/null || true
        fi
    done
    
    # Sustituir en nombres de archivos
    find . -type f -name "*{module_name}*" | while read -r file; do
        new_file=$(echo "$file" | sed "s/{module_name}/$MODULE_NAME/g")
        if [ "$file" != "$new_file" ]; then
            echo "   📄 Renombrando archivo: $file -> $new_file"
            mv "$file" "$new_file" 2>/dev/null || true
        fi
    done
    
    # Sustituir en contenido de archivos
    find . -type f \( -name "*.py" -o -name "*.md" -o -name "*.txt" -o -name "*.yml" -o -name "*.yaml" -o -name "*.json" \) | while read -r file; do
        if grep -q "{module_name}" "$file" 2>/dev/null; then
            echo "   📝 Sustituyendo contenido en: $file"
            sed -i "s/{module_name}/$MODULE_NAME/g" "$file" 2>/dev/null || true
        fi
        if grep -q "{project_name}" "$file" 2>/dev/null; then
            echo "   📝 Sustituyendo contenido en: $file"
            sed -i "s/{project_name}/$PROJECT_NAME/g" "$file" 2>/dev/null || true
        fi
    done
    
    echo "✅ Variables del template sustituidas"
}

# Ejecutar sustitución de variables
substitute_template_variables

# Ejecutar projen para aplicar la configuración
echo "🔧 Aplicando configuración de Projen..."
projen || {
    echo "❌ Error al ejecutar projen. Revisa la configuración del template."
    exit 1
}

# Formatear código si la tarea existe
echo "✨ Formateando código..."
if projen --help | grep -q "format"; then
    projen format || echo "⚠️  No se pudo ejecutar el formateo automático"
fi

# Volver al directorio original y mover el proyecto
cd ..
mv "$TEMP_PROJECT_DIR" "$PROJECT_NAME"

# Corregir el entorno virtual Python
echo "🐍 Corrigiendo entorno virtual Python..."
cd "$PROJECT_NAME"

# Eliminar entorno virtual temporal que puede estar mal configurado
if [ -d ".env" ]; then
    rm -rf .env
    echo "   🗑️  Eliminando entorno virtual temporal"
fi

# Verificar si virtualenv está disponible, si no, instalarlo
if ! command -v virtualenv >/dev/null 2>&1; then
    echo "   📦 Instalando virtualenv..."
    pip install virtualenv || {
        echo "⚠️  No se pudo instalar virtualenv, usando python3 -m venv como fallback"
        python3 -m venv .env
    }
else
    # Crear entorno virtual limpio con virtualenv
    echo "   🔧 Creando entorno virtual con virtualenv..."
    virtualenv .env
fi

# Activar entorno virtual y reinstalar dependencias
echo "   📚 Instalando dependencias en el entorno virtual corregido..."
source .env/bin/activate

# Actualizar pip
python -m pip install --upgrade pip >/dev/null 2>&1

# Instalar dependencias de producción
pip install -r requirements.txt >/dev/null 2>&1

# Instalar dependencias de desarrollo
pip install -r requirements-dev.txt >/dev/null 2>&1

echo "✅ Entorno virtual corregido y dependencias instaladas"

# Volver al directorio padre
cd ..

echo ""
echo "🎉 ¡Proyecto '$PROJECT_NAME' creado exitosamente!"
echo ""
echo "📋 Próximos pasos:"
echo "   1. cd $PROJECT_NAME"
echo "   2. Personalizar el código en $MODULE_NAME/"
echo "   3. Ejecutar 'projen synth' para verificar"
echo "   4. Ejecutar 'ENV=dev projen deploy:env' para desplegar"
echo ""
echo "🛠️  Comandos útiles disponibles:"
echo "   - projen                    # Regenerar archivos de configuración"
echo "   - projen synth              # Sintetizar CDK"
echo "   - projen test               # Ejecutar tests"

# Mostrar comandos específicos del template si existen
cd "$PROJECT_NAME"
if projen --help | grep -q "synth:env"; then
    echo "   - projen synth:env          # Sintetizar para ambiente específico"
    echo "   - ENV=prod projen deploy:env # Desplegar a producción"
fi
if projen --help | grep -q "format"; then
    echo "   - projen format             # Formatear código"
fi
if projen --help | grep -q "lint"; then
    echo "   - projen lint               # Ejecutar linting"
fi
cd ..

echo ""
echo "📖 Para más información, revisa el README del proyecto creado."
echo "🔗 Template usado: $TEMPLATE_REPO"
