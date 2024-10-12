from fastapi import APIRouter

from polls import adapters
from polls.schemas import FastLogin, LoginRequest, RegisterRequest, TokenRequest
from polls.adapters.user import create_access_token

router = APIRouter(prefix="/user", tags=["users"])


@router.post("/login", response_model=FastLogin)
async def post_login(
    login_request: LoginRequest,
) -> FastLogin:
    user = await adapters.verify_password(
        login_request.username, login_request.password
    )
    return FastLogin.from_orm(user)


@router.post("/register", response_model=FastLogin)
async def post_register(
    register_request: RegisterRequest,
) -> FastLogin:
    user = await adapters.register_user(
        register_request.username, register_request.password, register_request.email
    )
    return FastLogin.from_orm(user)


@router.post("/token")
async def post_token(token_request: TokenRequest):
    token = create_access_token(data={"sub": token_request.username})
    return {"access_token": token, "token_type": "bearer"}
