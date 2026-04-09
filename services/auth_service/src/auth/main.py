from fastapi import FastAPI
from auth.api.v1.router import auth_router

app = FastAPI()

app.include_router(auth_router, prefix='/api/v1')
