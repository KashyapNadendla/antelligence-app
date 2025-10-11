# CORS Debug Configuration
# If issues persist, temporarily use this more permissive configuration

from fastapi.middleware.cors import CORSMiddleware

def add_permissive_cors(app):
    """
    Adds a very permissive CORS configuration for development/debugging.
    Use this temporarily to diagnose CORS issues.
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins (development only!)
        allow_credentials=False,  # Must be False when using allow_origins=["*"]
        allow_methods=["*"],  # Allow all methods
        allow_headers=["*"],  # Allow all headers
    )
    print("⚠️ WARNING: Using permissive CORS (allow all origins). For development only!")

