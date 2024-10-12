import jwt
import datetime
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from jwt.exceptions import InvalidTokenError
from mysite import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/token")

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


User = get_user_model()


@sync_to_async
def get_user(username):
    try:
        return User.objects.get(username=username)
    except User.DoesNotExist:
        return None


@sync_to_async
def create_user(username, password, email):
    try:
        return User.objects.create_user(
            username=username, password=password, email=email
        )
    except User.DoesNotExist:
        return None


def create_access_token(data: dict, expires_delta: datetime.timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


credentials_exception = HTTPException(
    status_code=401,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=401,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    return username


async def get_current_user(token: str = Depends(oauth2_scheme)):
    username = get_token(token)
    user = await get_user(username)
    if user is None:
        raise credentials_exception
    return user
