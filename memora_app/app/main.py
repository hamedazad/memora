from fastapi import FastAPI, APIRouter

app = FastAPI()
router = APIRouter(prefix="/api")  # All routes start with /api

@router.post("/chat")
def chat():
    return {"message": "Chat works"}

app.include_router(router)
