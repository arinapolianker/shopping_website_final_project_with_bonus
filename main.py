from fastapi import FastAPI
from repository.database import database
from controller.user_controller import router as user_router
from controller.item_controller import router as item_router
from controller.order_controller import router as order_router
from controller.favorite_item_controller import router as favorite_item_router
from controller.auth_controller import router as auth_router
from controller.churn_prediction_controller import router as user_data_router


app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

app.include_router(user_router)
app.include_router(item_router)
app.include_router(order_router)
app.include_router(favorite_item_router)
app.include_router(auth_router)
app.include_router(user_data_router)
