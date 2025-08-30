"""
Main application entrypoint (developer convenience).
- Starts the ASGI server (uvicorn) pointing to backend.app.asgi:app.
- Keeps all code comments and naming in English for professionalism.
"""

import os
import uvicorn
from api.asgi import app

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info", reload=os.getenv("DEV_MODE", "0") == "1")
