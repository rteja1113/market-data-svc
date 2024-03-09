from fastapi import FastAPI

import src.marketdata.router

app = FastAPI()
app.include_router(src.marketdata.router.router)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Hello, World!"}
