def test_app_imports():
    """Test that backend.main imports without errors."""
    import importlib
    m = importlib.import_module("backend.main")
    assert hasattr(m, "app")
    assert hasattr(m.app, "include_router")
    
def test_health_endpoint_exists():
    """Test that health endpoint is properly configured."""
    import importlib
    m = importlib.import_module("backend.main")
    # Check that the health endpoint is registered
    routes = [route.path for route in m.app.routes]
    assert "/health" in routes