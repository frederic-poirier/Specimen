from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from backend.core.db import Base, engine
# Ensure models are imported before create_all so tables exist
from backend.api import folder as folders
from backend.api import scan as scan_api
import time

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Fontbase API")
app.mount("/api/fonts", StaticFiles(directory="C:\\Users\\fredm\\Code\\Specimen\\backend\\subset"), name="fonts")
app.include_router(folders.router, prefix="/api")
app.include_router(scan_api.router)
