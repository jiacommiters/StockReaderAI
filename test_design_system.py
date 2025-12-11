"""
Test script untuk memastikan design system ter-load dengan benar
"""

import os
import sys

# Test CSS file exists
css_path = os.path.join('static', 'css', 'design-system.css')
if os.path.exists(css_path):
    print(f"✅ CSS file found at: {css_path}")
    with open(css_path, 'r', encoding='utf-8') as f:
        css_content = f.read()
        print(f"✅ CSS file size: {len(css_content)} characters")
else:
    print(f"❌ CSS file NOT found at: {css_path}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Files in static/: {os.listdir('static') if os.path.exists('static') else 'static/ does not exist'}")

# Test components module
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from components.ui_components import load_design_system, render_header
    print("✅ Components module imported successfully")
except Exception as e:
    print(f"❌ Error importing components: {e}")

print("\n✅ All tests completed!")

