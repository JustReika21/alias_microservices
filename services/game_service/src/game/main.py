from fastapi import FastAPI
from game.api.router import game_router

app = FastAPI()


app.include_router(game_router)
