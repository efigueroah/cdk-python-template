# Demos - AWS CDK Python Projects

Esta carpeta contiene proyectos de demostración que muestran diferentes patrones y mejores prácticas para el desarrollo de infraestructura como código usando AWS CDK con Python.

## 📁 Demos Disponibles

### 1. [my-datalake](./my-datalake/) - Data Lake Architecture Demo
**Propósito**: Demostración de una arquitectura completa de Data Lake en AWS

**Características principales**:
- **S3 Buckets**: Raw, processed y curated data layers
- **AWS Glue**: Data Catalog y ETL jobs
- **Amazon Athena**: Query engine para análisis
- **IAM Roles**: Configuración de permisos granulares
- **Lifecycle Policies**: Gestión automática del ciclo de vida de datos
- **Security**: Encryption, SSL enforcement, y acceso controlado

**Casos de uso**:
- Arquitecturas de Big Data
- Data Analytics pipelines
- Data warehousing moderno
- Procesamiento de datos a gran escala

**Stack único**: Todos los recursos en un solo stack para simplicidad

---

### 2. [multi-stack-demo](./multi-stack-demo/) - Multi-Stack Architecture Demo
**Propósito**: Demostración de arquitectura multi-stack con separación de responsabilidades

**Características principales**:
- **Network Stack**: VPC, subnets, internet gateway
- **Storage Stack**: Primary y backup S3 buckets con diferentes lifecycle policies
- **Cross-stack references**: Outputs e imports entre stacks
- **Independent deployment**: Cada stack se puede desplegar independientemente
- **CDK Nag integration**: Validaciones de seguridad automatizadas
- **Comprehensive testing**: 24 tests cubriendo funcionalidad y seguridad

**Casos de uso**:
- Arquitecturas empresariales complejas
- Separación de responsabilidades por equipos
- Despliegues independientes por componente
- Gestión granular de infraestructura

**Estructura organizada**: `src/stacks/{función}/{recurso}/`

## 🚀 Cómo Usar los Demos

### Prerrequisitos
- Python 3.8+
- AWS CLI configurado
- AWS CDK CLI instalado
- Permisos apropiados en AWS

### Pasos Generales

1. **Navegar al demo deseado**:
   ```bash
   cd demos/[nombre-del-demo]
   ```

2. **Activar entorno virtual**:
   ```bash
   source .env/bin/activate
   ```

3. **Instalar dependencias** (si es necesario):
   ```bash
   pip install -r requirements.txt
   ```

4. **Listar stacks disponibles**:
   ```bash
   cdk list
   ```

5. **Ejecutar tests**:
   ```bash
   python -m pytest tests/ -v
   ```

6. **Sintetizar templates**:
   ```bash
   cdk synth
   ```

7. **Desplegar**:
   ```bash
   cdk deploy --all
   ```

## 📋 Comparación de Demos

| Aspecto | my-datalake | multi-stack-demo |
|---------|-------------|------------------|
| **Arquitectura** | Single stack | Multi-stack |
| **Complejidad** | Media | Alta |
| **Servicios AWS** | S3, Glue, Athena, IAM | VPC, S3, EC2 |
| **Casos de uso** | Data Analytics | Infraestructura empresarial |
| **Deployment** | Stack único | Stacks independientes |
| **Testing** | Tests básicos | 24 tests comprehensivos |
| **Organización** | Estructura simple | Estructura escalable |

## 🛠️ Patrones Demostrados

### Patrones de Seguridad
- ✅ CDK Nag integration
- ✅ IAM least privilege
- ✅ S3 encryption y SSL enforcement
- ✅ VPC security groups
- ✅ Resource-level permissions

### Patrones de Arquitectura
- ✅ Single-stack simplicity (my-datalake)
- ✅ Multi-stack separation (multi-stack-demo)
- ✅ Cross-stack references
- ✅ Resource lifecycle management
- ✅ Environment-specific configurations

### Patrones de Testing
- ✅ Unit testing con pytest
- ✅ CloudFormation template validation
- ✅ Resource configuration testing
- ✅ Security compliance testing
- ✅ Cross-stack integration testing

## 📚 Recursos Adicionales

- [AWS CDK Developer Guide](https://docs.aws.amazon.com/cdk/v2/guide/)
- [AWS CDK API Reference](https://docs.aws.amazon.com/cdk/api/v2/)
- [CDK Patterns](https://cdkpatterns.com/)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)

## 🤝 Contribuciones

Estos demos están diseñados para ser:
- **Educativos**: Mostrar mejores prácticas
- **Extensibles**: Base para proyectos reales
- **Mantenibles**: Código limpio y bien documentado
- **Seguros**: Configuraciones de seguridad por defecto

¡Siéntete libre de usar estos demos como punto de partida para tus propios proyectos!
