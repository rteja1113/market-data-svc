from fastapi import FastAPI

import src.marketdata.router

app = FastAPI()
app.include_router(src.marketdata.router.router)
