# AWS CDK Python Project Template

Una plantilla Projen centralizada para proyectos de infraestructura como código (IaC) usando AWS CDK con Python. Esta plantilla proporciona una base robusta y reutilizable que fomenta las mejores prácticas de la industria en cuanto a coherencia, seguridad, mantenibilidad y escalabilidad.

## Contenido de la Plantilla

Esta plantilla incluye:

- **AWS CDK v2.x**: Última versión estable compatible
- **Python 3.11**: Configuración optimizada para desarrollo CDK
- **Projen**: Gestión automatizada de configuración de proyecto
- **Multi-ambiente**: Soporte para dev, staging y prod con configuraciones específicas
- **Documentación**: Sphinx con tema Read the Docs y generación automática
- **CDK Nag**: Validaciones de seguridad y mejores prácticas integradas
- **Testing**: Framework completo con pytest, coverage y mocking
- **Linting y Formateo**: Black, flake8, isort, mypy y bandit
- **Pre-commit Hooks**: Validaciones automáticas antes de commits
- **CI/CD Ready**: Configuración preparada para pipelines de integración continua

## Prerrequisitos

Antes de usar esta plantilla, asegúrate de tener instalado:

- **Node.js** (v18 o superior): Para Projen y CDK CLI
- **npm**: Gestor de paquetes de Node.js
- **AWS CDK CLI**: `npm install -g aws-cdk`
- **Python** (3.11 o superior): Runtime para el desarrollo
- **pip**: Gestor de paquetes de Python
- **Projen CLI**: `npm install -g projen`
- **AWS CLI**: Configurado con credenciales apropiadas

### Instalación de Projen CLI

```bash
npm install -g projen
```

## Cómo Usar esta Plantilla

### Método 1: Script Automatizado (Recomendado)

El método más fácil y confiable es usar el script automatizado que maneja toda la configuración:

```bash
# Descargar el script de generación
curl -O https://raw.githubusercontent.com/efigueroah/cdk-python-template/main/create-project-from-template.sh
chmod +x create-project-from-template.sh

# Crear un nuevo proyecto
./create-project-from-template.sh <nombre-proyecto> <nombre-modulo>

# Ejemplo:
./create-project-from-template.sh my-infrastructure my_infrastructure
```

**Ventajas del script automatizado:**
- ✅ Descarga automática del template desde GitHub
- ✅ Configuración completa del entorno virtual Python
- ✅ Instalación automática de todas las dependencias
- ✅ Sustitución correcta de variables del template
- ✅ Formateo automático del código generado
- ✅ Inicialización del repositorio Git
- ✅ Verificación de funcionamiento

### Método 2: Projen Nativo (Limitado)

**⚠️ Nota:** El comando nativo de Projen tiene limitaciones con repositorios de GitHub y puede no funcionar correctamente:

```bash
# Este método puede fallar con el error "remote-git is not a git command"
projen new --from git::https://github.com/efigueroah/cdk-python-template.git --name <project-name> --module-name <module-name>
```

**Por esta razón, recomendamos usar el script automatizado.**

### 2. Configuración Inicial

Si usaste el script automatizado, la mayoría de la configuración ya está lista. Solo necesitas:

```bash
# Navegar al directorio del proyecto
cd <project-name>

# El entorno virtual y dependencias ya están instalados por el script
# Activar el entorno virtual (si no está activo)
source .env/bin/activate

# Configurar pre-commit hooks (opcional pero recomendado)
pre-commit install
```

Si usaste el método manual de Projen, necesitarás:

```bash
# Navegar al directorio del proyecto
cd <project-name>

# Crear y activar entorno virtual
python3 -m venv .env
source .env/bin/activate

# Instalar dependencias de Python
pip install -r requirements.txt

# Instalar dependencias de desarrollo
pip install -r requirements-dev.txt

# Configurar pre-commit hooks (opcional pero recomendado)
pre-commit install
```

### 3. Configurar Ambientes

Edita el archivo `src/<module-name>/config.py` para configurar tus cuentas y regiones de AWS:

```python
ENVIRONMENTS = {
    "dev": {
        "account": "123456789012",  # Reemplaza con tu cuenta de desarrollo
        "region": "us-east-1",
        # ... otras configuraciones
    },
    "prod": {
        "account": "987654321098",  # Reemplaza con tu cuenta de producción
        "region": "us-east-1",
        # ... otras configuraciones
    }
}
```

### 4. Primeros Pasos

```bash
# Verificar que todo funciona correctamente (si usaste el script, ya está verificado)
projen test

# Sintetizar la aplicación CDK
projen synth
# o usando CDK directamente:
cdk synth

# Ver diferencias (requiere stack existente)
projen diff
# o usando CDK directamente:
cdk diff

# Desplegar a desarrollo
ENV=dev projen deploy:env
# o usando CDK directamente:
cdk deploy --context environment=dev

# Generar documentación
projen docs:build
```

**Nota:** El script automatizado ya verifica que `cdk synth` funcione correctamente durante la creación del proyecto.

## 🎯 Demos y Ejemplos

En la carpeta [`demos/`](./demos/) encontrarás proyectos de ejemplo que demuestran diferentes patrones y arquitecturas usando esta plantilla:

### [📊 my-datalake](./demos/my-datalake/) - Data Lake Architecture
- **Arquitectura completa de Data Lake** con S3, Glue, y Athena
- **Gestión de datos por capas**: Raw, processed, y curated
- **Políticas de lifecycle** y configuraciones de seguridad
- **Stack único** para simplicidad de despliegue

### [🏗️ multi-stack-demo](./demos/multi-stack-demo/) - Multi-Stack Architecture  
- **Arquitectura multi-stack** con separación de responsabilidades
- **Network Stack**: VPC, subnets, internet gateway
- **Storage Stack**: S3 buckets con diferentes lifecycle policies
- **Referencias cruzadas** entre stacks
- **24 tests comprehensivos** y validaciones CDK Nag
- **Estructura organizada**: `src/stacks/{función}/{recurso}/`

Estos demos sirven como:
- ✅ **Ejemplos prácticos** de uso de la plantilla
- ✅ **Patrones de arquitectura** probados y documentados  
- ✅ **Punto de partida** para proyectos reales
- ✅ **Mejores prácticas** de seguridad y testing

Para usar cualquier demo:
```bash
cd demos/[nombre-del-demo]
source .env/bin/activate
cdk list
python -m pytest tests/ -v
cdk deploy --all
```

## Estructura del Proyecto Generado

```
<project-name>/
├── .projenrc.py              # Configuración de Projen
├── .vscode/                  # Configuración de VS Code
├── docs/                     # Documentación con Sphinx
├── src/<module-name>/        # Código fuente principal
│   ├── app.py               # Punto de entrada CDK
│   ├── config.py            # Configuración por ambientes
│   ├── constructs/          # Constructs personalizados
│   ├── stacks/              # Definiciones de stacks
│   └── lambda/              # Código de funciones Lambda
├── tests/                    # Tests unitarios e integración
│   ├── unit/                # Tests unitarios
│   └── integration/         # Tests de integración
├── assets/                   # Assets estáticos y recursos
├── requirements.txt          # Dependencias de producción
├── requirements-dev.txt      # Dependencias de desarrollo
└── README.md                # Documentación del proyecto
```

## Comandos Disponibles

### Desarrollo

```bash
# Formatear código
npm run format

# Ejecutar linting
npm run lint

# Ejecutar tests
npm run test

# Tests con coverage
npm run test -- --cov=src --cov-report=html

# Pre-commit hooks
npm run pre-commit
```

### CDK

```bash
# Sintetizar para ambiente específico
ENV=dev npm run synth:env

# Desplegar a ambiente específico
ENV=prod npm run deploy:env

# Destruir ambiente específico
ENV=dev npm run destroy:env

# Ver diferencias
ENV=prod npm run diff:env
```

### Documentación

```bash
# Construir documentación
npm run docs:build

# Limpiar documentación
npm run docs:clean

# Abrir documentación en navegador
npm run docs:open

# Generar diagrama de arquitectura
npm run diagram
```

### Seguridad

```bash
# Análisis de seguridad con CDK Nag
npm run security

# Análisis de vulnerabilidades
npm run lint  # Incluye bandit para seguridad
```

## Guía de Actualización del Proyecto

### Sincronizar con la Última Versión de la Plantilla

Para mantener tu proyecto actualizado con las mejoras de la plantilla:

```bash
# 1. Actualizar configuración de Projen
npx projen

# 2. Revisar cambios generados
git diff

# 3. Resolver conflictos si los hay
# Edita manualmente los archivos en conflicto

# 4. Confirmar cambios
git add .
git commit -m "Update project configuration from template"
```

### Manejo de Conflictos

Cuando actualices la plantilla, pueden surgir conflictos en:

- **Archivos de configuración**: `.projenrc.py`, `requirements.txt`
- **Archivos de documentación**: `docs/conf.py`, `README.md`
- **Configuración de herramientas**: `.vscode/settings.json`, `.pre-commit-config.yaml`

**Resolución recomendada:**

1. Revisa cada conflicto cuidadosamente
2. Mantén tus personalizaciones específicas del proyecto
3. Adopta las mejoras de la plantilla cuando sea apropiado
4. Prueba que todo funcione después de resolver conflictos

### Advertencias Importantes

- **Nunca edites archivos generados automáticamente** por Projen (marcados con comentarios de advertencia)
- **Siempre ejecuta tests** después de actualizar la plantilla
- **Revisa la documentación** de cambios importantes en nuevas versiones
- **Haz backup** de personalizaciones importantes antes de actualizar

## Desarrollo de la Plantilla

### Para Contribuidores

Si necesitas mantener o mejorar esta plantilla:

```bash
# Clonar el repositorio de la plantilla
git clone https://github.com/efigueroah/cdk-python-template.git
cd cdk-python-template

# Hacer cambios en .projen/main.py o skeleton/
# ...

# Probar la plantilla localmente
projen new --from . --name test-project --module-name test_project

# Verificar que el proyecto generado funciona
cd test-project
pip install -r requirements.txt
npm run test
npm run synth
```

### Estructura de la Plantilla

```
template-repo/
├── .projen/
│   └── main.py              # Configuración principal de Projen
├── skeleton/                # Archivos base a copiar
│   ├── src/{module_name}/   # Código fuente template
│   ├── tests/               # Tests template
│   ├── docs/                # Documentación template
│   └── assets/              # Assets template
└── README.md               # Este archivo
```

### Mejores Prácticas para Mantenimiento

1. **Versionado semántico**: Usa tags para versiones de la plantilla
2. **Changelog**: Mantén un registro de cambios importantes
3. **Testing**: Prueba la plantilla con proyectos reales antes de publicar
4. **Documentación**: Actualiza este README con cada cambio significativo
5. **Compatibilidad**: Considera el impacto en proyectos existentes

## Soporte y Contribuciones

### Reportar Problemas

Si encuentras problemas con la plantilla:

1. Verifica que tienes las versiones correctas de las herramientas
2. Revisa la documentación y ejemplos
3. Busca en issues existentes del repositorio: https://github.com/efigueroah/cdk-python-template/issues
4. Crea un nuevo issue con detalles específicos

### Contribuir Mejoras

Las contribuciones son bienvenidas:

1. Fork del repositorio: https://github.com/efigueroah/cdk-python-template
2. Crea una rama para tu feature/fix
3. Implementa los cambios
4. Prueba con proyectos de ejemplo
5. Envía un pull request con descripción detallada

## Licencia

Este proyecto está licenciado bajo [MIT License](LICENSE).

## Recursos Adicionales

- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/)
- [Projen Documentation](https://projen.io/)
- [CDK Nag Rules](https://github.com/cdklabs/cdk-nag)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
- [Python CDK Examples](https://github.com/aws-samples/aws-cdk-examples/tree/master/python)

---

**Creado por [Euclides Figueroa](https://github.com/efigueroah)** - Especialista en DevOps y AWS
