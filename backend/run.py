import os
import uvicorn

if __name__ == "__main__":
    use_reload = os.getenv("AICERT_RELOAD", "false").lower() == "true"
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=use_reload,
    )