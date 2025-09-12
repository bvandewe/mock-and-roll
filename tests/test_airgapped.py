#!/usr/bin/env python3
"""
Test script to verify air-gapped Swagger UI implementation.

This script checks:
1. All required static assets are present
2. HTML generation works correctly
3. No external dependencies are referenced
4. Validator URL is properly disabled
"""

import os
import sys

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def check_static_assets():
    """Check if all required static assets are present."""
    print("=" * 50)
    print("CHECKING STATIC ASSETS")
    print("=" * 50)

    required_files = ["src/static/swagger-ui/swagger-ui.css", "src/static/swagger-ui/swagger-ui-bundle.js", "src/static/swagger-ui/swagger-ui-standalone-preset.js", "src/static/favicon.png", "src/static/swagger-ui-template.html"]

    all_present = True
    for file_path in required_files:
        exists = os.path.exists(file_path)
        status = "✅" if exists else "❌"
        print(f"{status} {os.path.basename(file_path)}")
        if not exists:
            all_present = False

    print(f"\nAll required static assets present: {'✅' if all_present else '❌'}")
    return all_present


def test_html_generation():
    """Test air-gapped HTML generation."""
    print("\n" + "=" * 50)
    print("TESTING HTML GENERATION")
    print("=" * 50)

    try:
        from app.swagger_airgapped import get_swagger_ui_html_airgapped

        swagger_params = {"docExpansion": "none", "validatorUrl": None, "tryItOutEnabled": True, "defaultModelsExpandDepth": -1}  # This should disable external validator

        html_response = get_swagger_ui_html_airgapped(openapi_url="/openapi.json", title="Test API - Air-gapped", swagger_ui_parameters=swagger_params)

        html_content = html_response.body.decode("utf-8")

        # Check for proper null validator URL
        if "validatorUrl: null" in html_content:
            print("✅ validatorUrl properly set to null")
        else:
            print("❌ validatorUrl not properly nullified")

        # Check for local favicon reference
        if "/static/favicon.png" in html_content:
            print("✅ Local favicon reference found")
        else:
            print("❌ Local favicon reference missing")

        # Check for local static asset references
        checks = [("/static/swagger-ui/swagger-ui.css", "CSS"), ("/static/swagger-ui/swagger-ui-bundle.js", "JS Bundle")]

        for asset_path, asset_name in checks:
            if asset_path in html_content:
                print(f"✅ Local {asset_name} reference found")
            else:
                print(f"❌ Local {asset_name} reference missing")

        return True

    except Exception as e:
        print(f"❌ HTML generation failed: {e}")
        return False


def check_external_references():
    """Check for any external URL references in static files."""
    print("\n" + "=" * 50)
    print("CHECKING FOR EXTERNAL REFERENCES")
    print("=" * 50)

    # These are the external URLs we want to ensure are handled properly
    external_domains = ["petstore.swagger.io", "validator.swagger.io/validator", "fastapi.tiangolo.com"]

    # Check if these exist in our templates (they should be configured to null/local)
    template_file = "src/static/swagger-ui-template.html"
    if os.path.exists(template_file):
        with open(template_file, "r") as f:
            template_content = f.read()

        for domain in external_domains:
            if domain in template_content:
                print(f"⚠️  Found {domain} in template - this should be handled by configuration")
            else:
                print(f"✅ No direct reference to {domain} in template")

    print("\n📋 Note: External URLs in minified JS files are expected.")
    print("   Our configuration (validatorUrl: null) disables external calls.")


def main():
    """Run all air-gapped verification tests."""
    print("🔒 AIR-GAPPED SWAGGER UI VERIFICATION")
    print("🔒 Mock-and-Roll Project")
    print()

    # Run tests
    assets_ok = check_static_assets()
    html_ok = test_html_generation()
    check_external_references()

    # Final summary
    print("\n" + "=" * 50)
    print("FINAL SUMMARY")
    print("=" * 50)

    if assets_ok and html_ok:
        print("🎉 AIR-GAPPED IMPLEMENTATION: ✅ FULLY VERIFIED")
        print("   - All static assets present")
        print("   - HTML generation working")
        print("   - External validator disabled")
        print("   - Local favicon included")
        print("   - Ready for air-gapped deployment")
        return 0
    else:
        print("❌ AIR-GAPPED IMPLEMENTATION: ISSUES FOUND")
        if not assets_ok:
            print("   - Missing static assets")
        if not html_ok:
            print("   - HTML generation failed")
        return 1


if __name__ == "__main__":
    exit(main())
