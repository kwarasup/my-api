from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
with open("hash.txt", "w") as f:
    f.write(pwd_context.hash("secret"))
