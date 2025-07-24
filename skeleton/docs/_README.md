# Directorio docs

Este directorio contiene toda la documentación del proyecto, incluyendo documentación técnica, arquitectura y guías de uso.

## Estructura:

```
docs/
├── conf.py              # Configuración de Sphinx
├── index.rst            # Página principal de la documentación
├── architecture/        # Documentación de arquitectura
│   ├── overview.rst     # Visión general del sistema
│   ├── components.rst   # Componentes y servicios
│   └── diagrams/        # Diagramas de arquitectura
├── api/                 # Documentación de API
│   └── modules.rst      # Documentación auto-generada de módulos
├── guides/              # Guías de usuario y desarrollo
│   ├── deployment.rst   # Guía de despliegue
│   ├── development.rst  # Guía de desarrollo
│   └── troubleshooting.rst # Solución de problemas
└── _build/              # Archivos generados (ignorado en git)
```

## Herramientas utilizadas:

### Sphinx
- **Propósito**: Generador de documentación principal
- **Configuración**: `conf.py`
- **Formato**: reStructuredText (.rst)

### Extensiones incluidas:
- `sphinx.ext.autodoc`: Documentación automática desde docstrings
- `sphinx.ext.viewcode`: Enlaces al código fuente
- `sphinx.ext.napoleon`: Soporte para docstrings de Google/NumPy
- `sphinxcontrib.mermaid`: Diagramas Mermaid
- `sphinx_rtd_theme`: Tema Read the Docs

### cdk-dia
- **Propósito**: Generación automática de diagramas de arquitectura CDK
- **Uso**: `npm run diagram`
- **Salida**: `docs/architecture/diagrams/`

## Comandos disponibles:

```bash
# Construir documentación
npm run docs:build

# Limpiar archivos generados
npm run docs:clean

# Abrir documentación en navegador
npm run docs:open

# Generar diagrama de arquitectura
npm run diagram
```

## Mejores prácticas:

1. **Docstrings**: Documenta todas las clases y métodos públicos
2. **Arquitectura**: Mantén diagramas actualizados con cambios de infraestructura
3. **Guías**: Incluye ejemplos prácticos y casos de uso
4. **Versionado**: Documenta cambios importantes en cada release
