from fastapi import FastAPI
from routers.zoho import auth, folders

app = FastAPI()

# Register routers
app.include_router(auth.router)
app.include_router(folders.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True) #local
