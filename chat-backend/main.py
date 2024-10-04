from fastapi import FastAPI, WebSocket

from routers.chat_router import router as chat_router

app = FastAPI(
    root_path="/api"
)


app.include_router(chat_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}

