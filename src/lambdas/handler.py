from fastapi import FastAPI
from mangum import Mangum

from app.utils import logger as _logger
from app.api.endpoints.user_endopoint import UserRouter
from app.api.endpoints.product_enpoint import ProductRouter
from app.domain.service_layer import (
    UserService,
    ProductService,
)
from app.adapters.repository import (
    UsersRepository,
    ProductRepository,
    get_db,
)

logger = _logger.get_logger()

app = FastAPI(title="Products service")

db, client = get_db()
user_repo = UsersRepository(db=db, client=client)
user_service = UserService(repository=user_repo)
users_router = UserRouter(user_service=user_service)

product_repo = ProductRepository(db=db, client=client)
product_service = ProductService(repository=product_repo)
product_router = ProductRouter(
    product_service=product_service,
    user_service=user_service,
)

@app.get("/")
async def root():
    return {"message": "products service :)"}

app.include_router(users_router.router)
app.include_router(product_router.router)
main = Mangum(app)

