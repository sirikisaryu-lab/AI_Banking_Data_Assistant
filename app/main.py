from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from core.query_router import handle_query
from pathlib import Path

app = FastAPI()

# Serve static files (e.g., HTML)
ui_path = Path(__file__).parent.parent / "ui"
app.mount("/ui", StaticFiles(directory=ui_path), name="ui")

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    html_file = ui_path / "html.html"
    return HTMLResponse(content=html_file.read_text(), status_code=200)

@app.post("/query")
async def query_endpoint(request: Request):
    data = await request.json()
    query = data.get("query")
    if not query:
        return {"error": "Query is required"}

    # Conversation history sent by the frontend as prior turns.
    conversation_history = data.get("conversation_history", [])

    result = handle_query(query, conversation_history=conversation_history)

    return {
        "response":       result.get("response", ""),
        "explainability": result.get("explainability", {})
    }