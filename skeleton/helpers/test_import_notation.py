#!/usr/bin/env python3
"""
Ejemplo de uso del paquete hg_aws_helpers con la notación helpers.hg_aws_helpers
para demostrar cómo se usará cuando esté en AWS Artifact
"""

import sys
from pathlib import Path

# Agregar el directorio helpers al path para simular la importación desde AWS Artifact
helpers_path = Path(__file__).parent
sys.path.insert(0, str(helpers_path))

# Importar usando la notación helpers.hg_aws_helpers
from hg_aws_helpers import ConfigLoader, ConfigConverter


def demo_config_loader():
    """Demostrar el uso de ConfigLoader con archivos de configuración reales"""
    print("🔧 === Demo ConfigLoader con archivos de configuración reales ===\n")
    
    # Ruta a los archivos de configuración de ejemplo
    config_base_path = "/home/efigueroa/Proyectos/AWS-QDeveloper/proyectos/Projen-template/config"
    
    # 1. Cargar configuración base
    print("📋 1. Cargando configuración base (base.toml):")
    base_loader = ConfigLoader(config_file=f"{config_base_path}/base.toml")
    base_config = base_loader.load_config()
    
    print(f"   • Proyecto: {base_config.project.name}")
    print(f"   • Descripción: {base_config.project.description}")
    print(f"   • Región AWS: {base_config.aws.region}")
    print(f"   • Account ID: {base_config.aws.account_id}")
    print(f"   • VPC CIDR: {base_config.network.vpc_cidr}")
    print(f"   • NAT Gateways: {base_config.network.nat_gateways}")
    print(f"   • Instance Type: {base_config.compute.instance_type}")
    print(f"   • DB Engine: {base_config.database.engine}")
    
    # 2. Cargar configuración de desarrollo
    print("\n🔧 2. Cargando configuración de desarrollo (env.dev.toml):")
    dev_loader = ConfigLoader(config_file=f"{config_base_path}/env.dev.toml")
    dev_config = dev_loader.load_config()
    
    print(f"   • Ambiente: {dev_config.project.environment}")
    print(f"   • NAT Gateways: {dev_config.network.nat_gateways}")
    print(f"   • WAF habilitado: {dev_config.security.enable_waf}")
    print(f"   • CloudTrail habilitado: {dev_config.security.enable_cloudtrail}")
    print(f"   • GuardDuty habilitado: {dev_config.security.enable_guardduty}")
    print(f"   • Instance Type: {dev_config.compute.instance_type}")
    print(f"   • Min Capacity: {dev_config.compute.min_capacity}")
    
    # 3. Demostrar acceso con valores por defecto
    print("\n⚙️  3. Demostrando acceso con valores por defecto:")
    print(f"   • Backup retention (con default): {dev_config.database.get('backup_retention_days', 30)} días")
    print(f"   • Custom setting (no existe): {dev_config.custom.get('some_setting', 'valor_por_defecto')}")
    
    # 4. Demostrar acceso a configuraciones anidadas
    print("\n📊 4. Configuraciones anidadas y complejas:")
    if hasattr(base_config.storage, 'lifecycle_rules'):
        print("   • Reglas de lifecycle S3:")
        for rule in base_config.storage.lifecycle_rules:
            print(f"     - Prefix: {rule.get('prefix', 'N/A')}, Expiración: {rule.get('expiration_days', 'N/A')} días")
    
    # 5. Demostrar tags
    print("\n🏷️  5. Tags de recursos:")
    print(f"   • Tags base: {base_config.tags.to_dict()}")
    print(f"   • Tags dev: {dev_config.tags.to_dict()}")


def demo_config_converter():
    """Demostrar el uso de ConfigConverter"""
    print("\n🔄 === Demo ConfigConverter ===\n")
    
    config_base_path = "/home/efigueroa/Proyectos/AWS-QDeveloper/proyectos/Projen-template/config"
    
    converter = ConfigConverter()
    
    # 1. Convertir TOML a JSON
    print("📝 1. Convirtiendo base.toml a JSON:")
    json_file = converter.convert_file(
        input_file=f"{config_base_path}/base.toml",
        output_format="json"
    )
    print(f"   • Archivo generado: {json_file}")
    
    # 2. Convertir TOML a YAML
    print("\n📝 2. Convirtiendo env.dev.toml a YAML:")
    yaml_file = converter.convert_file(
        input_file=f"{config_base_path}/env.dev.toml",
        output_format="yaml"
    )
    print(f"   • Archivo generado: {yaml_file}")
    
    # 3. Trabajar con CDK context si existe
    cdk_json_path = f"{config_base_path}/cdk.json"
    if Path(cdk_json_path).exists():
        print(f"\n⚙️  3. Importando context de CDK desde {cdk_json_path}:")
        context_file = converter.import_cdk_context(
            cdk_json_path=cdk_json_path,
            output_format="toml"
        )
        print(f"   • Context importado a: {context_file}")


def demo_integration_with_cdk():
    """Demostrar cómo se integraría con AWS CDK"""
    print("\n🏗️  === Demo Integración con AWS CDK ===\n")
    
    config_base_path = "/home/efigueroa/Proyectos/AWS-QDeveloper/proyectos/Projen-template/config"
    
    # Simular carga de configuración para un stack CDK
    print("📋 Cargando configuración para Stack CDK:")
    
    # Cargar configuración base y de ambiente
    base_loader = ConfigLoader(config_file=f"{config_base_path}/base.toml")
    base_config = base_loader.load_config()
    
    dev_loader = ConfigLoader(config_file=f"{config_base_path}/env.dev.toml")
    dev_config = dev_loader.load_config()
    
    # Simular parámetros que se pasarían a un stack CDK
    print("\n🎯 Parámetros para NetworkStack:")
    print(f"   • vpc_cidr: '{base_config.network.vpc_cidr}'")
    print(f"   • nat_gateways: {dev_config.network.nat_gateways}")
    print(f"   • public_subnets: {base_config.network.public_subnets}")
    print(f"   • private_subnets: {base_config.network.private_subnets}")
    
    print("\n🎯 Parámetros para ComputeStack:")
    print(f"   • instance_type: '{dev_config.compute.instance_type}'")
    print(f"   • min_capacity: {dev_config.compute.min_capacity}")
    print(f"   • max_capacity: {dev_config.compute.max_capacity}")
    print(f"   • desired_capacity: {dev_config.compute.desired_capacity}")
    
    print("\n🎯 Parámetros para DatabaseStack:")
    print(f"   • engine: '{base_config.database.engine}'")
    print(f"   • instance_class: '{dev_config.database.instance_class}'")
    print(f"   • allocated_storage: {dev_config.database.allocated_storage}")
    print(f"   • multi_az: {dev_config.database.multi_az}")
    print(f"   • backup_retention_days: {dev_config.database.backup_retention_days}")
    
    print("\n🎯 Configuración de AWS Environment:")
    print(f"   • account: '{base_config.aws.account_id}'")
    print(f"   • region: '{dev_config.aws.region}'")
    
    print("\n🏷️  Tags comunes:")
    base_tags = base_config.tags.to_dict()
    dev_tags = dev_config.tags.to_dict()
    merged_tags = {**base_tags, **dev_tags}
    for key, value in merged_tags.items():
        print(f"   • {key}: '{value}'")


if __name__ == "__main__":
    print("🚀 Demostrando el uso del paquete hg_aws_helpers")
    print("=" * 60)
    
    try:
        demo_config_loader()
        demo_config_converter()
        demo_integration_with_cdk()
        
        print("\n✅ Todas las demostraciones completadas exitosamente!")
        print("\n💡 El paquete hg_aws_helpers está listo para ser usado en proyectos CDK")
        print("   Importación recomendada: from helpers.hg_aws_helpers import ConfigLoader, ConfigConverter")
        
    except Exception as e:
        print(f"\n❌ Error durante la demostración: {e}")
        import traceback
        traceback.print_exc()
