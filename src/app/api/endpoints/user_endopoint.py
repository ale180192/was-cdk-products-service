from typing import Any
from fastapi import (
    APIRouter,
    HTTPException,
    Depends
)
from fastapi.security import OAuth2PasswordRequestForm

from app.domain.service_layer import UserService
from app.domain.models import UserModel
from app.api.schemas import user_schema

router = APIRouter()

class UserRouter:

    def __init__(self, user_service: UserService):
        self.user_service = user_service
    
    @property
    def router(self):
        api_router = APIRouter(prefix="/v1/users", tags=["users"])
        
        @api_router.get("/")
        def list_users():
            return self.user_service.list()

        @api_router.post("/")
        def create_user(user_model: UserModel):
            return self.user_service.create(user_model=user_model)


        @api_router.post(
            "/signup",
            response_model=user_schema.UserSignupResponse,
            status_code=201
        )
        def create_user_signup(
            *,
            user_signup: user_schema.UserSignupRequest
        ) -> Any:
            # WARNING!! enumeration because it gives the information
            # if the user exist or not.
            try:
                return self.user_service.signup(
                    email=user_signup.email,
                    password=user_signup.password,
                    first_name=user_signup.first_name
                )
            except self.user_service.UserAlreadyExistsException as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"The email {user_signup.email} is already registered"
                )

        @api_router.post("/login")
        def login(
            login: user_schema.LoginRequest
        ) -> Any:
            """
            Get the JWT for a user with data from OAuth2 request form body.
            """

            token = self.user_service.authenticate(
                email=login.email, password=login.password
            )
            if not token:
                raise HTTPException(
                    status_code=400, detail="Incorrect username or password"
                )

            return {
                "access_token": token,
                "token_type": "bearer",
            } 
            

        return api_router
