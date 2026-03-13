from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from database import get_db
import models
import utils

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/admin/login") # For swagger UI

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, utils.SECRET_KEY, algorithms=[utils.ALGORITHM])
        user_identifier: str = payload.get("sub")
        role: str = payload.get("role")
        if user_identifier is None or role is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    if role == "admin":
        user = db.query(models.Admin).filter(models.Admin.email == user_identifier).first()
    elif role == "student":
        user = db.query(models.Student).filter(models.Student.reg_number == user_identifier).first()
    else:
        raise credentials_exception

    if user is None:
        raise credentials_exception
    
    # Attach role to the user object dynamically for downstream checking
    user.role = role
    return user

def get_current_admin(current_user = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return current_user

def get_current_student(current_user = Depends(get_current_user)):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Not authorized")
    return current_user
