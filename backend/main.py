from fastapi import FastAPI
from backend.core.db import Base, engine
from backend.api import folder as folders

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Fontbase API")
app.include_router(folders.router, prefix="/api")
