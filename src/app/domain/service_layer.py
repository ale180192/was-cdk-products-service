from typing import Any, List, Optional
from uuid import uuid4
from fastapi import Depends
from jose import jwt, JWTError

from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer

from app.adapters.repository import (
    UserRepositoryAbstract,
    ProductRepository
)
from app.domain.models import (
    UserModel,
    ProductModel,
    TokenData
)
from app.api.schemas import user_schema

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="users/login"
)
PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")
JWT_SECRET = "testsecretkey123"
ALGORITHM="HS256"

class UserService:

    def __init__(self, repository: UserRepositoryAbstract) -> None:
        self.repository = repository

    class UserAlreadyExistsException(Exception):
        pass

    def list(self) -> List:
        repo = self.repository.get_all()
        return repo

    def create_admin(self, user_model: UserModel):
        user_model.id = uuid4().hex
        user_model.is_admin = True
        user = self.repository.create(user=user_model.dict())
        return user

    def create(self, user_model: UserModel):
        user_model.id = uuid4().hex
        user_model.is_admin = False
        self.repository.create(user=user_model.dict())
        return user_model

    def signup(self,
        email: str,
        password: str,
        first_name: str
    ) -> UserModel:
        user_db = self.repository.get_by_email(email=email)
        if user_db:
            raise self.UserAlreadyExistsException("")

        user_model = UserModel(
            id=uuid4().hex,
            is_admin=False,
            email=email,
            first_name=first_name,
            password=PWD_CONTEXT.hash(password)
        )
        return self.create(user_model=user_model)


    def authenticate(
        self,
        *,
        email: str,
        password: str
    ) -> Optional[UserModel]:
        user = self.repository.get_by_email(email=email)
        if not user:
            return None

        if not self.verify_password(password, user.get("password")):
            return None

        return UserModel.create_access_token(
            sub=user.get("id"),
            jwt_secret=JWT_SECRET,
            algorithm=ALGORITHM
        )


    @classmethod
    def verify_password(
        cls,
        plain_password: str,
        hashed_password: str
    ) -> bool:
        return PWD_CONTEXT.verify(plain_password, hashed_password)


    def get_current_user(
        self, token: str = Depends(oauth2_scheme)
    ):
        # credentials_exception = HTTPException(
        #     status_code=status.HTTP_401_UNAUTHORIZED,
        #     detail="Could not validate credentials",
        #     headers={"WWW-Authenticate": "Bearer"},
        # )
        try:
            payload = jwt.decode(
                token,
                JWT_SECRET,
                algorithms=[ALGORITHM],
                options={"verify_aud": False},
            )
            id: str = payload.get("sub")
            if id is None:
                raise Exception("id is None")

            token_data = TokenData(id=id)
        except JWTError:
            raise

        user = self.repository.get_by_id(id=token_data.id)
        if user is None:
            raise Exception("the user does not exist.")
        
        return user

class ProductService:

    class ProductAlreadyExistsException(Exception):
        pass

    def __init__(self, repository: ProductRepository) -> None:
        self.repository = repository


    def create(self, product_model: ProductModel):
        product_model.id = uuid4().hex
        product = self.repository.get_by_sku(sku=product_model.sku)
        if product:
            raise self.ProductAlreadyExistsException("")

        self.repository.create(product=product_model.dict())
        return product_model

    def list(self) -> List:
        repo = self.repository.get_all()
        items = []
        for item in repo:
            if item.get("sku"):
                items.append(item)
        
        return items

    def update(self, id: str, product_model: ProductModel) -> List:
        current_product = self.repository.get_by_id(id=id)
        if current_product.get("sku") == product_model.sku:
            product_updated = self.repository.update(id=id, product=product_model.dict())
        
        else:
            product_updated = self.repository.update_with_sku(
                id=id, product=product_model.dict(),
                current_sku=current_product.get("sku")
            )


        return product_updated