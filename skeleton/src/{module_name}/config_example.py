#!/usr/bin/env python3
"""
Ejemplo de uso de la configuración centralizada con hg_aws_helpers
"""

from .config import get_project_config, create_sample_config_files


def demo_configuration_usage():
    """Demostrar el uso de la configuración centralizada"""
    
    print("🔧 === Demo de Configuración Centralizada con hg_aws_helpers ===\n")
    
    # 1. Crear archivos de configuración de ejemplo
    print("📝 1. Creando archivos de configuración de ejemplo...")
    create_sample_config_files("dev")
    
    # 2. Cargar configuración para desarrollo
    print("\n🔧 2. Cargando configuración para desarrollo:")
    dev_config = get_project_config("dev")
    config = dev_config.config
    
    print(f"   • Proyecto: {config.project.name}")
    print(f"   • Ambiente: {config.project.environment}")
    print(f"   • Cuenta AWS: {config.aws.get('account', config.aws.get('account_id'))}")
    print(f"   • Región: {config.aws.region}")
    
    # 3. Demostrar acceso a configuración de red
    print("\n🌐 3. Configuración de red:")
    print(f"   • VPC CIDR: {config.network.vpc_cidr}")
    print(f"   • NAT Gateways: {config.network.nat_gateways}")
    print(f"   • Subnets públicas: {config.network.get('public_subnets', 'No definidas')}")
    
    # 4. Demostrar configuración de cómputo
    print("\n💻 4. Configuración de cómputo:")
    instance_types = config.compute.get('instance_types', {})
    print(f"   • Instancia pequeña: {instance_types.get('small', 'No definida')}")
    print(f"   • Instancia mediana: {instance_types.get('medium', 'No definida')}")
    print(f"   • Instancia grande: {instance_types.get('large', 'No definida')}")
    
    # 5. Demostrar configuración de base de datos
    print("\n🗄️  5. Configuración de base de datos:")
    print(f"   • Clase de instancia: {config.database.instance_class}")
    print(f"   • Almacenamiento: {config.database.allocated_storage} GB")
    print(f"   • Retención de backup: {config.database.backup_retention_days} días")
    print(f"   • Multi-AZ: {config.database.get('multi_az', False)}")
    
    # 6. Demostrar generación de nombres
    print("\n🏷️  6. Generación de nombres estandarizados:")
    print(f"   • Nombre de recurso S3: {dev_config.get_resource_name('data-bucket')}")
    print(f"   • Nombre de stack de red: {dev_config.get_stack_name('network')}")
    print(f"   • Nombre de stack de API: {dev_config.get_stack_name('api')}")
    
    # 7. Demostrar tags
    print("\n🏷️  7. Tags del proyecto:")
    tags = config.tags.to_dict() if hasattr(config.tags, 'to_dict') else config.tags
    for key, value in tags.items():
        print(f"   • {key}: {value}")
    
    # 8. Comparar con configuración de producción
    print("\n🚀 8. Comparación con configuración de producción:")
    prod_config = get_project_config("prod")
    prod_config_obj = prod_config.config
    
    print("   Diferencias clave:")
    print(f"   • NAT Gateways - Dev: {config.network.nat_gateways}, Prod: {prod_config_obj.network.nat_gateways}")
    print(f"   • DB Multi-AZ - Dev: {config.database.get('multi_az', False)}, Prod: {prod_config_obj.database.get('multi_az', False)}")
    print(f"   • Monitoreo detallado - Dev: {config.monitoring.detailed_monitoring}, Prod: {prod_config_obj.monitoring.detailed_monitoring}")
    
    # 9. Demostrar exportación a CDK context
    print("\n📤 9. Exportación a CDK context:")
    try:
        dev_config.export_to_cdk_context()
    except Exception as e:
        print(f"   ⚠️  Nota: {e}")
        print("   💡 Esto funcionará cuando existan archivos de configuración externos")
    
    print("\n✅ Demo completado exitosamente!")
    print("\n💡 Próximos pasos:")
    print("   1. Edita los archivos config/base.toml y config/env.dev.toml")
    print("   2. Personaliza la configuración según tus necesidades")
    print("   3. Usa config.network.vpc_cidr en lugar de config['vpc_cidr']")
    print("   4. Aprovecha el acceso por atributos para código más limpio")


def demo_stack_integration():
    """Demostrar cómo integrar la configuración en stacks CDK"""
    
    print("\n🏗️  === Demo de Integración con Stacks CDK ===\n")
    
    # Ejemplo de cómo usar la configuración en un stack
    config = get_project_config("dev").config
    
    print("📋 Ejemplo de uso en NetworkStack:")
    print(f"""
from aws_cdk import Stack, aws_ec2 as ec2
from .config import get_project_config

class NetworkStack(Stack):
    def __init__(self, scope, construct_id, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        
        # Cargar configuración
        project_config = get_project_config(self.environment)
        config = project_config.config
        
        # Crear VPC usando configuración
        self.vpc = ec2.Vpc(
            self, "VPC",
            cidr=config.network.vpc_cidr,
            max_azs=len(config.network.get('availability_zones', [])),
            nat_gateways=config.network.nat_gateways,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="Private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24
                )
            ]
        )
        
        # Aplicar tags desde configuración
        for key, value in config.tags.to_dict().items():
            self.vpc.node.add_metadata(key, value)
""")
    
    print("📋 Parámetros que se usarían:")
    print(f"   • VPC CIDR: {config.network.vpc_cidr}")
    print(f"   • NAT Gateways: {config.network.nat_gateways}")
    print(f"   • Zonas de disponibilidad: {config.network.get('availability_zones', 'Auto-detectar')}")


if __name__ == "__main__":
    demo_configuration_usage()
    demo_stack_integration()
