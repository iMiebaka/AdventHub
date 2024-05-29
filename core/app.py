from fastapi import FastAPI
from core.routers import account
from core.routers import exhortation
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