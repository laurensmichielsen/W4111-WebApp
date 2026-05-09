from decimal import Decimal
from pydantic import BaseModel, Field

from .AbstractBaseResource import AbstractBaseResource
from ..services.MySQLDataService import MySQLDataService

class OrderDetails(BaseModel):
    orderNumber: int
    productCode: str
    quantityOrdered: int
    priceEach: Decimal
    orderLineNumber: int


class OrderDetailsCollection(BaseModel):
    items: list[OrderDetails] = Field(default_factory=list)


class OrderDetailsResource(AbstractBaseResource):
    def __init__(self, config: dict | None = None):
        cfg = dict(config or {})
        super().__init__(cfg)

        self.service_config = {
            "table": "orderdetails"
        }
        self.orderNumber = "orderNumber"
        self.productCode = "productCode"
        self.service = MySQLDataService(self.service_config)

    def get_by_id(self, orderNumber: int, productCode: str) -> OrderDetails:
        input_dict = {self.orderNumber : orderNumber, self.productCode : productCode}
        row = self.service.retrieveByPrimaryKey(input_dict)
        if not row:
            raise ValueError(
                f"No order detail for orderNumber={orderNumber}, productCode={productCode}"
            )
        return OrderDetails.model_validate(row)

    def get(self, template: dict) -> OrderDetailsCollection:
        rows = self.service.retrieveByTemplate(template)
        return OrderDetailsCollection(
            items=[OrderDetails.model_validate(r) for r in rows]
        )

    def post(self, new_data: OrderDetails) -> dict:
        data = new_data.model_dump()
        dictionary = {self.orderNumber : data["orderNumber"], self.productCode : data["productCode"]}
        return self.service.create(data, dictionary)

    def put(self, orderNumber: int, productCode: str, new_data: OrderDetails) -> int:
        input_dict = {self.orderNumber : orderNumber, self.productCode : productCode}
        data = new_data.model_dump()
        return self.service.updateByPrimaryKey(input_dict, data)

    def delete(self, orderNumber: int, productCode: str) -> int:
        input_dict = {self.orderNumber : orderNumber, self.productCode : productCode}
        return self.service.deleteByPrimaryKey(input_dict)