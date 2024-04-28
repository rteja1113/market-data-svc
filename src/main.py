import uvicorn
from fastapi import FastAPI

import src.marketdata.router
from src.common import logging_utils
from src.manage import wait_for_postgres

app = FastAPI()
app.include_router(src.marketdata.router.router)
logger = logging_utils.create_logger(__name__)


@app.on_event("startup")
async def create_database_and_apply_migrations():
    wait_for_postgres()


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Hello, World!"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
