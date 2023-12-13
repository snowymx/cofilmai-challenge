import os
from src.apis import apis
from prisma import Prisma
from fastapi import FastAPI

app = FastAPI()
app.include_router(apis, prefix="/apis")
prisma = Prisma(datasource={
        'url': os.environ.get('DATABASE_URL'),
    })

print(os.environ.get('DATABASE_URL'))

@app.on_event("startup")
async def startup():
    await prisma.connect()


@app.on_event("shutdown")
async def shutdown():
    await prisma.disconnect()


@app.get("/")
def read_root():
    return {"version": "1.0.0"}
