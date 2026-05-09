from typing import Optional
from pathlib import Path
from datetime import date

from pydantic import BaseModel, Field
from .AbstractBaseResource import AbstractBaseResource
from ..services.MySQLDataService import MySQLDataService


class Order(BaseModel):
    orderNumber: int
    orderDate: date
    requiredDate: date
    shippedDate: Optional[date] = None
    status: str
    comments: Optional[str] = None
    customerNumber: int


class OrderCollection(BaseModel):
    items: list[Order] = Field(default_factory=list)

class OrderResource(AbstractBaseResource):
    def __init__(self, config: dict | None = None):
        cfg = dict(config or {})
        super().__init__(cfg)
        self.service_config = {
            "table" : "orders"
        }
        self.primary_key_field = "orderNumber"
        self.service = MySQLDataService(self.service_config)

    def get(self, template: dict) -> OrderCollection:
        rows = self.service.retrieveByTemplate(template)
        return OrderCollection(
            items=[Order.model_validate(r) for r in rows]
        )

    
    def get_by_id(self, id: int) -> Order:
        input_dict = {self.primary_key_field : id}
        row = self.service.retrieveByPrimaryKey(input_dict)
        if not row:
            raise ValueError(f"No Order with id {id!r}")
        return Order.model_validate(row)

    
    def post(self, new_data: Order) -> int:
        data = new_data.model_dump()
        order_number = data.get("orderNumber")
        if order_number is None or order_number == 0:
            raise ValueError("Order Number should be defined")
        return self.service.create(data)

    
    def delete(self, id: int) -> int:
        input_dict = {self.primary_key_field : id}
        return self.service.deleteByPrimaryKey(input_dict)

    
    def put(self, orderNumber: int, new_data: Order) -> int:
        input_dict = {self.primary_key_field : orderNumber}
        data = new_data.model_dump()
        data["orderNumber"] = int(orderNumber)
        return self.service.updateByPrimaryKey(input_dict, data)

