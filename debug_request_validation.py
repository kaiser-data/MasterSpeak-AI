#!/usr/bin/env python3
"""
Debug script to check what routes are actually registered and what models are used
"""

import sys
import os
sys.path.insert(0, '/Users/marty/CodingProjects/claude-code-projects/MasterSpeak-AI')

try:
    from backend.main import app
    
    print("🔍 Registered Routes:")
    print("=" * 50)
    
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            path = route.path
            methods = getattr(route, 'methods', [])
            if 'POST' in methods and 'analysis' in path:
                print(f"📍 {methods} {path}")
                
                # Check if route has dependencies that validate request body
                if hasattr(route, 'dependant'):
                    dependant = route.dependant
                    print(f"   Dependencies: {len(dependant.dependencies) if dependant.dependencies else 0}")
                    
                    # Check body field
                    if hasattr(dependant, 'body_params') and dependant.body_params:
                        print(f"   Body params: {dependant.body_params}")
                    
                    # Check query/form params
                    if hasattr(dependant, 'query_params') and dependant.query_params:
                        print(f"   Query params: {[p.name for p in dependant.query_params]}")
                    
                    if hasattr(dependant, 'form_params') and dependant.form_params:
                        print(f"   Form params: {[p.name for p in dependant.form_params]}")
                
    print("=" * 50)

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()