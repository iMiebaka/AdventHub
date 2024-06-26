from fastapi import FastAPI
from src.routers import account
from src.routers import exhortation
from src.routers import comment
from src.routers import reaction
from src.routers import highlighter
from src.routers import request
from starlette.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Advent Hub"}


app.include_router(account.router)
app.include_router(exhortation.router)
app.include_router(comment.router)
app.include_router(reaction.router)
app.include_router(highlighter.router)
app.include_router(request.router)
