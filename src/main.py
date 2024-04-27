import uvicorn
from fastapi import FastAPI
from sqlalchemy_utils import create_database, database_exists

import src.marketdata.router
from src.database import engine
from src.manage import apply_migrations, wait_for_postgres

app = FastAPI()
app.include_router(src.marketdata.router.router)


@app.on_event("startup")
async def create_database_and_apply_migrations():
    wait_for_postgres()
    if not database_exists(str(engine.url)):
        create_database(str(engine.url))
    apply_migrations()


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Hello, World!"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
