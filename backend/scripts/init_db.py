from backend.core.db import engine, Base
from backend.models import folder as _folder_model  # noqa: F401
from backend.models import font as _font_model  # noqa: F401

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    # Use ASCII to avoid Windows console encoding issues
    print("[OK] Base de donnees initialisee")
