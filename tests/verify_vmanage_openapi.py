#!/usr/bin/env python3
"""
Quick verification script to check the OpenAPI spec for vmanage configuration.
This script can be run manually to verify the fix before starting a server.
"""

import json
import os
import sys

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# Set config to vmanage
os.environ["MOCK_CONFIG_FOLDER"] = os.path.join(os.path.dirname(__file__), "..", "configs", "vmanage")

from app.factory import create_app
from config.loader import load_auth_config

print("=" * 70)
print("🔍 Verifying vManage OpenAPI Security Schemes")
print("=" * 70)

# Load the auth config
auth_config = load_auth_config()
configured_methods = list(auth_config.get("authentication_methods", {}).keys())

print(f"\n📝 Configured in vmanage/auth.json ({len(configured_methods)} methods):")
for method in configured_methods:
    method_type = auth_config["authentication_methods"][method].get("type", "unknown")
    print(f"   • {method} (type: {method_type})")

# Create the app
app = create_app()

# Get the OpenAPI schema
openapi_schema = app.openapi()

# Get security schemes
security_schemes = openapi_schema.get("components", {}).get("securitySchemes", {})

print(f"\n🔐 Security Schemes in OpenAPI spec ({len(security_schemes)} schemes):")
for scheme_name, scheme_config in security_schemes.items():
    scheme_type = scheme_config.get("type", "unknown")
    scheme_name_or_header = scheme_config.get("name", scheme_config.get("scheme", ""))
    print(f"   • {scheme_name} (type: {scheme_type}, name/scheme: {scheme_name_or_header})")

# Verification
print(f"\n✅ Verification:")
missing = [m for m in configured_methods if m not in security_schemes]
extra = [s for s in security_schemes if s not in configured_methods]

if not missing and not extra:
    print(f"   ✓ Perfect match! All {len(configured_methods)} configured methods are present")
    print(f"   ✓ No extra security schemes found")
    print(f"\n🎉 SUCCESS: OpenAPI spec correctly reflects auth.json configuration!")
else:
    if missing:
        print(f"   ✗ Missing from OpenAPI: {missing}")
    if extra:
        print(f"   ⚠️  Extra in OpenAPI: {extra}")
    if missing:
        print(f"\n❌ FAILURE: Some configured methods are missing from OpenAPI spec")
        sys.exit(1)

# Save the schema to a temp file for manual inspection if needed
output_file = "/tmp/vmanage_openapi_schema.json"
with open(output_file, "w") as f:
    json.dump(openapi_schema, f, indent=2)

print(f"\n💾 Full OpenAPI schema saved to: {output_file}")
print(f"   You can inspect it with: cat {output_file} | jq '.components.securitySchemes'")

print("\n" + "=" * 70)
print("✅ All checks passed! You can now start the server with:")
print("   mockctl start -c vmanage -p 8000")
print("   Then visit: http://localhost:8000/docs")
print("=" * 70)
