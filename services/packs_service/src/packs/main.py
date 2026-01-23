from fastapi import FastAPI

from packs.api.router import pack_router
from packs.exc.exception_handlers import register_pack_exception_handlers

app = FastAPI()
@app.get("/")
def read_root():
    return {"Hello": "sss"}

app.include_router(pack_router)

register_pack_exception_handlers(app)
