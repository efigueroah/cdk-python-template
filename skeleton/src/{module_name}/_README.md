# Directorio src/{module_name}

Este es el directorio principal del código fuente de la aplicación CDK. Contiene toda la lógica de infraestructura como código organizada en módulos específicos.

## Estructura:

```
src/{module_name}/
├── __init__.py          # Inicialización del módulo
├── app.py              # Punto de entrada de la aplicación CDK
├── config.py           # Configuración centralizada
├── constructs/         # Constructs personalizados reutilizables
├── stacks/             # Definiciones de stacks CDK
├── lambda/             # Código de funciones Lambda
└── utils/              # Utilidades y helpers
```

## Archivos principales:

### app.py
- **Propósito**: Punto de entrada principal de la aplicación CDK
- **Responsabilidades**:
  - Inicialización de la aplicación CDK
  - Configuración de contexto y ambientes
  - Instanciación de stacks principales
  - Aplicación de CDK Nag para validaciones de seguridad

### config.py
- **Propósito**: Configuración centralizada del proyecto
- **Contenido**:
  - Configuraciones por ambiente (dev, staging, prod)
  - Parámetros de AWS (cuentas, regiones)
  - Configuraciones de servicios
  - Variables de entorno

## Subdirectorios:

### constructs/
Constructs personalizados y reutilizables que encapsulan patrones comunes de infraestructura.

### stacks/
Definiciones de stacks CDK organizadas por funcionalidad o servicio.

### lambda/
Código fuente de las funciones Lambda organizadas por función o servicio.

### utils/
Utilidades, helpers y funciones comunes utilizadas en todo el proyecto.

## Convenciones de nomenclatura:

- **Clases**: PascalCase (ej: `MyCustomConstruct`)
- **Archivos**: snake_case (ej: `my_custom_construct.py`)
- **Variables**: snake_case (ej: `my_variable`)
- **Constantes**: UPPER_SNAKE_CASE (ej: `MY_CONSTANT`)

## Mejores prácticas:

1. **Separación de responsabilidades**: Cada archivo debe tener una responsabilidad clara
2. **Reutilización**: Crear constructs para patrones repetitivos
3. **Configuración**: Usar config.py para todas las configuraciones
4. **Documentación**: Documentar todas las clases y métodos públicos
5. **Testing**: Cada componente debe tener tests correspondientes
