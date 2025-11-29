from datetime import datetime, timedelta
from typing import Union
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

app = FastAPI()

# origin ที่อนุญาตให้เรียกได้
origins = [
    "http://localhost:3000",          # ตอน dev frontend รันที่นี่
    "http://127.0.0.1:3000",
    "https://smartcut-v0--smartcut-goodfilm.asia-southeast1.hosted.app/",
    "https://your-frontend-domain.com"  # ถ้ามี domain จริง ให้ใส่เพิ่ม
    # จะเพิ่ม origin อื่นได้อีก เช่น mobile/web app อื่น ๆ
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # หรือ ["*"] ถ้าจะเปิดโล่ง (ใช้เฉพาะตอน dev)
    allow_credentials=True,
    allow_methods=["*"],            # GET, POST, PUT, DELETE ทั้งหมด
    allow_headers=["*"],            # อนุญาตทุก header เช่น Authorization, Content-Type
)

# Secret key settings
SECRET_KEY = "supersecretkey"  # Change this in production!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Fake database
fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$pbkdf2-sha256$29000$uFcqpdR6730PoRTivJcy5g$Gk0WpN83X.YnqIHW1JS.yhIIEMCX9vNz9E/9MhlJ/fQ", # "secret"
        "disabled": False,
    }
}

# Models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Union[str, None] = None

class User(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None

class UserInDB(User):
    hashed_password: str

# Security utilities
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    return None

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user(fake_users_db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/")
def read_root(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello {current_user.full_name} from Cloud Run! Hey 123"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/test")
def test(current_user: User = Depends(get_current_user)):
    return {"message": "This is a protected test message"}
