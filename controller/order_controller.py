from typing import List, Optional

from fastapi import HTTPException, APIRouter

from model.order import Order
from model.order_close import OrderClose
from model.order_item_quantity import OrderItemQuantity
from model.order_request import OrderRequest
from model.order_response import OrderResponse
from model.order_status import OrderStatus
from repository import order_repository, order_item_repository
from service import order_service, user_service

router = APIRouter(
    prefix="/order",
    tags=["order"]
)


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_by_id(order_id: int) -> Optional[OrderResponse]:
    return await order_service.get_order_by_id(order_id)


@router.get("/user/{user_id}")
async def get_order_by_user_id(user_id: int):
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id:{user_id} not found...")
    try:
        orders = await order_service.get_order_by_user_id(user_id)
        if not orders:
            return None
        return orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching orders. error: {e}")


@router.get("/temp/{user_id}")
async def get_temp_order(user_id: int):
    try:
        user = await user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail=f"User with id:{user_id} not found...")
        temp_order = await order_service.get_temp_order_by_user_id(user_id)
        if not temp_order:
            return HTTPException(status_code=404, detail="TEMP Order not found")
        return temp_order
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/", response_model=Optional[List[Order]])
async def get_all_orders():
    try:
        return await order_service.get_all_orders()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching all orders. Error: {e}")


@router.post("/")
async def create_order(order_request: OrderRequest):
    try:
        return await order_service.create_order(order_request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{order_id}")
async def update_order(order_id: int, order_request: OrderRequest):
    try:
        order = await order_repository.get_order_by_id(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        if order.status == OrderStatus.CLOSE:
            raise HTTPException(status_code=400, detail="Order is already closed")

        await order_service.update_order(order_id, order_request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/update_order_quantities/")
async def update_temp_order_quantities(request: OrderItemQuantity):
    try:
        await order_service.update_temp_order(request.user_id, request.item_id, request.quantity)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


@router.put("/purchase/{order_id}")
async def update_order_status(request: OrderClose):
    try:
        order = await order_service.get_order_by_id(request.order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        if order.status == OrderStatus.CLOSE:
            raise HTTPException(status_code=400, detail="Order is already closed")

        await order_service.update_order_status(request.user_id, request.shipping_address, request.status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/{order_id}")
async def delete_order_by_id(order_id: int):
    try:
        order = await order_service.get_order_by_id(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        await order_service.delete_order_by_id(order_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{order_id}/item/{item_id}")
async def delete_item_from_order(order_id: int, item_id: int):
    try:
        order = await order_service.get_order_by_id(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        if order.status == OrderStatus.CLOSE:
            raise HTTPException(status_code=400, detail="Order is closed, you can't delete items.")

        order_items = await order_item_repository.get_order_items_by_order_id(order_id)
        if not any(item.item_id == item_id for item in order_items):
            raise HTTPException(status_code=404, detail=f"Item with id:{item_id} is not in the order.")

        await order_service.delete_item_from_order(order_id, item_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
