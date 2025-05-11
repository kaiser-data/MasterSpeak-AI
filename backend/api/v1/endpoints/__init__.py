# backend/api/v1/endpoints/__init__.py

"""
API v1 endpoints for MasterSpeak AI
Organized by functionality
"""

from . import auth, analysis, users, speeches, health

__all__ = ["auth", "analysis", "users", "speeches", "health"]