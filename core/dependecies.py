import os 
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt ,JWTError
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM  = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
def get_current_user(token:str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        return{
             "id"  : payload.get("sub"),
            "role": payload.get("role"),
            "name": payload.get("name") 
        }
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
def require_roles(allowed_roles:list):
    def checker(current_user=Depends(get_current_user)):
        if current_user["role"] not in allowed_roles:
            raise HTTPException(status_code=403, detail="Access denied")
        return current_user
    return checker