from fastapi import FastAPI

from cards.api.router import card_router
from cards.exc.exception_handlers import register_card_exception_handlers

app = FastAPI()
@app.get("/")
def read_root():
    return {"Hello": "sss"}

app.include_router(card_router)

register_card_exception_handlers(app)
