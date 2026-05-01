"""
GamePilot - Main Entry Point
Launches the FastAPI server for the GamePilot AI gameplay assistant.
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "gamepilot.app.api.server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
