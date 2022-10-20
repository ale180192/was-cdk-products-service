from typing import Any
from fastapi import (
    APIRouter,
    HTTPException,
    Depends
)
from fastapi.security import OAuth2PasswordRequestForm

from app.domain.service_layer import (
    UserService,
    ProductService,
)
from app.domain.models import UserModel
from app.api.schemas import user_schema
from app.domain.models import ProductModel

router = APIRouter()

class ProductRouter:

    def __init__(
        self,
        user_service: UserService,
        product_service: ProductService
    ):
        self.user_service = user_service
        self.product_service = product_service
    
    @property
    def router(self):
        api_router = APIRouter(prefix="/v1/products", tags=["products"])
        
        @api_router.get("/")
        def list_products():
            return self.product_service.list()

        @api_router.post("/")
        def create_product(
            product_model: ProductModel,
            user = Depends(self.user_service.get_current_user)
        ):
            try:
                return self.product_service.create(product_model=product_model)
            except self.product_service.ProductAlreadyExistsException as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"The product sku {product_model.sku} already exists."
                )

        @api_router.put("/{product_id}")
        def update_product(
            product_id: str,
            product_model: ProductModel,
            user = Depends(self.user_service.get_current_user)
        ):
            try:
                return self.product_service.update(id=product_id, product_model=product_model)
            except self.product_service.ProductAlreadyExistsException as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"The product sku {product_model.sku} already exists."
                )


        return api_router
