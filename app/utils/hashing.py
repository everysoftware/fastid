from passlib.context import CryptContext

hasher = CryptContext(schemes=["bcrypt"], deprecated="auto")
