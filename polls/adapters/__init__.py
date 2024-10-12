from typing import Type, TypeVar

from django.db import models
from fastapi import HTTPException, Path
from django.contrib.auth import password_validation
from django.contrib.auth.hashers import check_password

from polls.models import Choice, Question
from polls.adapters.user import create_access_token, create_user, get_user


ModelT = TypeVar("ModelT", bound=models.Model)


async def retrieve_object(model_class: Type[ModelT], id: int) -> ModelT:
    instance = await model_class.objects.filter(pk=id).afirst()  # type:ignore
    if not instance:
        raise HTTPException(status_code=404, detail="Object not found.")
    return instance


async def retrieve_question(q_id: int = Path(..., description="get question from db")):
    return await retrieve_object(Question, q_id)


async def retrieve_choice(c_id: int = Path(..., description="get choice from db")):
    return await retrieve_object(Choice, c_id)


async def retrieve_questions():
    return [q async for q in Question.objects.all()]


async def retrieve_choices():
    return [c async for c in Choice.objects.all()]


async def verify_password(username: str, password: str):
    user = await get_user(username)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if not check_password(password, user.password):
        raise HTTPException(status_code=400, detail="Invalid password")
    access_token = create_access_token(data={"sub": username})
    user.token = access_token
    return user


async def register_user(username: str, password: str, email: str):
    if not username or not password or not email:
        raise HTTPException(status_code=400, detail="Invalid input")
    user = await get_user(username)
    if user is not None:
        raise HTTPException(status_code=400, detail="User already exists")

    try:
        password_validation.validate_password(password=password)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    register = await create_user(username=username, password=password, email=email)
    access_token = create_access_token(data={"sub": username})
    register.token = access_token
    return register
