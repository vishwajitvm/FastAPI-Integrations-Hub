from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.zoho import auth, folders
from routers.chatbot.app.query import routes

from routers.zoho import auth, folders,org_info

app = FastAPI()

# Add this block to enable CORS
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(folders.router)
app.include_router(org_info.router)
app.include_router(routes.chat_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
