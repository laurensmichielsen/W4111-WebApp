from typing import Optional

from pydantic import BaseModel, Field
from .AbstractBaseResource import AbstractBaseResource
from ..services.MySQLDataService import MySQLDataService

class Customer(BaseModel):
    customerNumber: int
    customerName: str
    contactLastName: str
    contactFirstName: str
    phone: str
    addressLine1: str
    addressLine2: Optional[str] = None
    city: str
    state: Optional[str] = None
    postalCode: Optional[str] = None
    country: str
    salesRepEmployeeNumber: Optional[int] = None
    creditLimit: Optional[float] = None

class CustomerCollection(BaseModel):
    items: list[Customer] = Field(default_factory=list)


class CustomerResource(AbstractBaseResource):
    def __init__(self, config: dict | None = None):
        cfg = dict(config or {})
        super().__init__(cfg)

        self.service_config = {
            "table" : "customers"
        }
        self.primary_key_field = "customerNumber"
        self.service = MySQLDataService(self.service_config)
    
    def get(self, template: dict) -> CustomerCollection:
        rows = self.service.retrieveByTemplate(template)
        return CustomerCollection(
            items=[Customer.model_validate(r) for r in rows]
        )

    
    def get_by_id(self, id: int) -> Customer:
        input_dict = {self.primary_key_field : id}
        row = self.service.retrieveByPrimaryKey(input_dict)
        if not row:
            raise ValueError(f"No Customer with id {id!r}")
        return Customer.model_validate(row)

    
    def post(self, new_data: Customer) -> int:
        data = new_data.model_dump()
        customer_number = data.get(self.primary_key_field)
        if customer_number is None or customer_number == 0:
            raise ValueError("Customer Number should be defined")
        return self.service.create(data)

    
    def delete(self, id: int) -> int:
        input_dict = {self.primary_key_field : id}
        return self.service.deleteByPrimaryKey(input_dict)

    
    def put(self, customerNumber: int, new_data: Customer) -> int:
        input_dict = {self.primary_key_field : customerNumber}
        data = new_data.model_dump()
        return self.service.updateByPrimaryKey(input_dict, data)

