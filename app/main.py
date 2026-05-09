from __future__ import annotations

import os
import sys
from pathlib import Path
from datetime import date

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


if __package__ in (None, ""):
    # Supports running this file directly (e.g., PyCharm "main.py" debug config).
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from app.resources.HarryPotterResource import (
        HarryPotterCharacter,
        HarryPotterCollection,
        HarryPotterResource,
    )
    from app.resources.CustomerResource import(
        Customer,
        CustomerCollection,
        CustomerResource,
    )

    from app.resources.OrderDetails import (
        OrderDetails,
        OrderDetailsCollection,
        OrderDetailsResource
    )

    from app.resources.OrderResource import (
        Order,
        OrderCollection,
        OrderResource,
    )
else:
    from .resources.HarryPotterResource import (
        HarryPotterCharacter,
        HarryPotterCollection,
        HarryPotterResource,
    )

    from .resources.CustomerResource import(
        Customer,
        CustomerCollection,
        CustomerResource,
    )

    from .resources.OrderDetails import (
        OrderDetails,
        OrderDetailsCollection,
        OrderDetailsResource
    )

    from .resources.OrderResource import (
        Order,
        OrderCollection,
        OrderResource,
    )


def _get_app_name() -> str:
    # Keep settings minimal in this starter; use environment variables when needed.
    return os.getenv("APP_NAME", "Starter FastAPI App")


app = FastAPI(title=_get_app_name(), version="0.1.0")
harry_potter_resource = HarryPotterResource()
customer_resource = CustomerResource()
order_resource = OrderResource()
order_details_resource = OrderDetailsResource()


class EchoRequest(BaseModel):
    message: str


@app.get("/", tags=["root"])
def read_root() -> dict[str, str]:
    return {"message": "Hello from FastAPI"}


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/echo", tags=["echo"])
def echo(payload: EchoRequest) -> EchoRequest:
    return payload

# TODO: check codes and handle DB errors

@app.get("/customers", tags=["customers"])
def get_customer(
    customerName: str | None = None,
    contactLastName: str | None = None,
    contactFirstName: str | None = None,
    phone: str | None = None,
    addressLine1: str | None = None,
    addressLine2: str | None = None,
    city: str | None = None,
    state: str | None = None,
    postalCode: str | None = None,
    country: str | None = None,
    salesRepEmployeeNumber: int | None = None,
    creditLimit: float | None = None,
) -> CustomerCollection:
    template_dict = {}
    if customerName is not None:
        template_dict["customerName"] = customerName
    if contactLastName is not None:
        template_dict["contactLastName"] = contactLastName
    if contactFirstName is not None:
        template_dict["contactFirstName"] = contactFirstName
    if phone is not None:
        template_dict["phone"] = phone
    if addressLine1 is not None:
        template_dict["addressLine1"] = addressLine1
    if addressLine2 is not None:
        template_dict["addressLine2"] = addressLine2
    if city is not None:
        template_dict["city"] = city
    if state is not None:
        template_dict["state"] = state
    if postalCode is not None:
        template_dict["postalCode"] = postalCode
    if country is not None:
        template_dict["country"] = country
    if salesRepEmployeeNumber is not None:
        template_dict["salesRepEmployeeNumber"] = salesRepEmployeeNumber
    if creditLimit is not None:
        template_dict["creditLimit"] = creditLimit
    return customer_resource.get(template_dict)

@app.get("/orders", tags=["orders"])
def get_orders(
    orderDate: date | None = None,
    requiredDate: date | None = None,
    shippedDate: date | None = None,
    status: str | None = None,
    comments: str | None = None,
    customerNumber: int | None = None,
) -> OrderCollection:
    template_dict = {}
    if orderDate is not None:
        template_dict["orderDate"] = orderDate
    if requiredDate is not None:
        template_dict["requiredDate"] = requiredDate
    if shippedDate is not None:
        template_dict["shippedDate"] = shippedDate
    if status is not None:
        template_dict["status"] = status
    if comments is not None:
        template_dict["comments"] = comments
    if customerNumber is not None:
        template_dict["customerNumber"] = customerNumber
    return order_resource.get(template_dict)

@app.get("/orderdetails", tags=["orderdetails"])
def get_orderdetails(
    quantityOrdered: int | None = None,
    priceEach: float | None = None,
    orderLineNumber: int | None = None,
) -> OrderDetailsCollection:
    template_dict = {}
    if quantityOrdered is not None:
        template_dict["quantityOrdered"] = quantityOrdered
    if priceEach is not None:
        template_dict["priceEach"] = priceEach
    if orderLineNumber is not None:
        template_dict["orderLineNumber"] = orderLineNumber
    return order_details_resource.get(template_dict)

@app.post("/customers", tags=["customers"])
def create_customer(new_data: Customer) -> int:
    try:
        new_id = customer_resource.post(new_data)
        return new_id
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.post("/orders", tags=["orders"])
def create_orders(new_data: Order) -> int:
    try:
        new_id = order_resource.post(new_data)
        return new_id
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@app.post("/orderdetails", tags=["orderdetails"])
def create_order_details(new_data: OrderDetails):
    try:
        new_id = order_details_resource.post(new_data)
        return new_id
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.get("/customers/{customerNumber}", tags=["customer"])
def get_customer_by_id(customerNumber: int) -> Customer:
    try:
        return customer_resource.get_by_id(customerNumber)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    
@app.get("/orders/{orderNumber}", tags=["orders"])
def get_order_by_id(orderNumber: int) -> Order:
    try:
        return order_resource.get_by_id(orderNumber)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    
@app.get("/orders/{orderNumber}/orderdetails/{productCode}", tags=["orderdetails"])
def get_orderdetails_by_id(orderNumber: int, productCode: str) -> OrderDetails:
    try:
        return order_details_resource.get_by_id(orderNumber, productCode)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    
@app.delete("/customers/{customerNumber}", tags=["customers"])
def delete_customer(customerNumber: int):
    try:
        deleted = customer_resource.delete(customerNumber)
        return {"deleted": deleted}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

@app.delete("/orders/{orderNumber}", tags=["orders"])
def delete_order(orderNumber: int):
    try:
        deleted = order_resource.delete(orderNumber)
        return {"deleted": deleted}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    
@app.delete("/orders/{orderNumber}/orderdetails/{productCode}", tags=["orderdetails"])
def delete_orderdetails(orderNumber: int, productCode: str):
    try:
        deleted = order_details_resource.delete(orderNumber, productCode)
        return {"deleted": deleted}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

@app.put("/customers/{customerNumber}", tags=["customer"])
def put_customer_by_id(customerNumber: int, new_data: Customer) -> dict:
    try:
        updated = customer_resource.put(customerNumber, new_data)
        return {"updated": updated}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

@app.put("/orders/{orderNumber}", tags=["orders"])
def put_order_by_id(orderNumber: int, new_data: Order) -> dict:
    try:
        updated = order_resource.put(orderNumber, new_data)
        return {"updated": updated}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

@app.put("/orders/{orderNumber}/orderdetails/{productCode}", tags=["orderdetails"])
def put_orderdetails_by_id(
    orderNumber: int,
    productCode: str,
    new_data: OrderDetails
) -> dict:
    try:
        updated = order_details_resource.put(orderNumber, productCode, new_data)
        return {"updated": updated}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))

    uvicorn.run(app, host=host, port=port)

