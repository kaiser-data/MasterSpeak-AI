def test_import_api_only():
    """Test that backend.main imports without filesystem dependencies."""
    import importlib
    m = importlib.import_module("backend.main")
    assert hasattr(m, "app")
    assert hasattr(m.app, "include_router")