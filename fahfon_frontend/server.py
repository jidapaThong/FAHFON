from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
app = FastAPI()
app.mount("/static", StaticFiles(directory="build/static"), name="static")

@app.get("/{subroute:path}")
async def handle_subroute(subroute: str):
    file_path = os.path.join(os.getcwd(),"build","index.html")
    return FileResponse(file_path)