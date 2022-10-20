from datetime import datetime, timedelta

from fastapi import Depends
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import Optional
from pydantic import BaseModel
from pydantic import Field



class TokenData(BaseModel):
    id: Optional[str] = None

class UserModel(BaseModel):
    id: Optional[str] = None
    email: str = Field(..., example="email@test.com")
    first_name: str = Field(..., example="User 1")
    password: str = Field(..., example="sdgsg34987")
    is_admin: Optional[bool] = None


    @classmethod
    def create_access_token(
        self, *, sub: str, jwt_secret: str, algorithm
    ) -> str:
        # WARNING!! not secure
        payload = {}
        lifetime = timedelta(minutes=48)
        expire = datetime.utcnow() + lifetime
        payload["type"] = "access_token"
        payload["exp"] = expire
        payload["iat"] = datetime.utcnow()
        payload["sub"] = str(sub)
        return jwt.encode(payload, jwt_secret, algorithm=algorithm)


class ProductModel(BaseModel):
    # sku, name, price and brand.
    id: Optional[str] = None
    sku: str = Field(..., example="sku-stl")
    name: str = Field(..., example="Product a")
    price: str = Field(..., example="12.0")
    brand: str = Field(..., example="Brand")