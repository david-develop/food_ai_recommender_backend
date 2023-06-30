from functools import wraps
from typing import Optional
from fastapi import Depends, HTTPException, status, APIRouter, Request, Response, Form
from passlib.context import CryptContext
from jose import jwt, JWTError
import os
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import ValidationError
from food_api.database.models import UserSignUp, User


router = APIRouter(
    prefix="/auth", tags=["auth"], responses={401: {"user": "Not authorized"}}
)

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="access_token")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.username: Optional[str] = None
        self.password: Optional[str] = None

    async def create_oauth_form(self):
        form = await self.request.form()
        self.username = form.get("username")
        self.password = form.get("password")


def get_password_hash(password):
    return bcrypt_context.hash(password)


def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)


async def get_user(request: Request, email: str):
    users_colletion = request.app.mongodb.users
    user = await users_colletion.find_one({"email": email})
    return user


async def authenticate_user(request: Request, email: str, password: str):
    user = await get_user(request, email)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user


def create_access_token(
    email: str, user_id: str, expires_delta: Optional[timedelta] = None
):
    encode = {"sub": email, "id": user_id}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    encode.update({"exp": expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str):
    try:
        if token is None:
            return None
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("PAYLOAD ------------>", payload)
        email: str = payload.get("sub")
        user_id: str = payload.get("id")
        if email is None or user_id is None:
            return None
        return {"email": email, "id": user_id}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )


def validate_fields_form(email: str, password: str, name: str = "Dummy"):
    try:
        user = UserSignUp(email=email, name=name, password=password)
        return user
    except ValidationError as e:
        error_fields = e.errors()
        # itereate over the error fields and return custom error messages
        for field in error_fields:
            if field["type"] == "value_error.email":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email"
                )
            field_name = field["loc"][0]
            if field_name == "password":
                if field["type"] == "value_error.any_str.min_length":
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Password must be at least 8 characters long",
                    )
                if field["type"] == "value_error.str.regex":
                    msg = "The password can consist of any combination of letters (lowercase or uppercase), digits, and special characters from the set @$!%*?&."
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST, detail=msg
                    )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.errors())


def admin_only():
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get("request")
            bearer = request.headers.get("Authorization")
            token = bearer.split(" ")[1]
            if not token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token"
                )
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                user_email = payload.get("sub")
                user = await get_user(request, user_email)
                if user.get("role") != "admin":
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Admin role required",
                    )
                return await func(*args, **kwargs)
            except JWTError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
                )
        return wrapper
    return decorator


@router.post("/token")
async def login_access_token(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    user = await authenticate_user(request, form_data.username, form_data.password)
    print(user)
    if not user:
        return None
    token_expires = timedelta(minutes=60)
    access_token = create_access_token(
        user["email"], str(user["id"]), expires_delta=token_expires
    )
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return access_token


# login with form data
@router.post("/login")
async def login(request: Request):
    try:
        form = LoginForm(request)
        await form.create_oauth_form()
        if not form.username or not form.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Bad credentials"
            )

        response = Response()
        validate_user_cookie = await login_access_token(
            request, response, form_data=form
        )
        print(validate_user_cookie)
        if not validate_user_cookie:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )
        return {"message": "Logged in", "token": validate_user_cookie}
    except Exception as e:
        print(e)
        msg = "Error in credentials"
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=msg
            )


@router.get("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return response


@router.post("/register")
async def register(
    request: Request,
    email: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    password_2: str = Form(...),
):
    print(email, username, password, password_2)
    users_colletion = request.app.mongodb.users
    user = await users_colletion.find_one({"email": email})
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )
    if password != password_2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords don't match"
        )
    validate_fields_form(email=email, name=username, password=password)
    try:
        hashed_password = get_password_hash(password)
        user_model = User(name=username, email=email, hashed_password=hashed_password)

        await users_colletion.insert_one(user_model.dict())
        return {"message": "User created successfully"}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/users/me")
async def get_user_me(token: str = Depends(oauth2_scheme)):
    current_user = await get_current_user(token)
    return current_user
