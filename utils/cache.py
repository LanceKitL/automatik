"""
Shared Flask-Caching Cache instance.

Created as a module-level singleton so both app.py and controllers
can import it without circular-dependency issues.

Usage:
    from utils.cache import cache
    cache.set("key", value)
    value = cache.get("key")
"""

from flask_caching import Cache

# Singleton Cache instance; must be initialised with an app via
# cache.init_app(app) before the first request.
cache = Cache()
