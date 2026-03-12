from fastapi import Depends,HTTPException,APIRouter
from app.db.session import get_db
from core.dependecies import get_current_user, require_roles
from core.security import create_token, hash_password, verify_password
from models.user import User
from schemas.user_schema import UserCreate, UserResponse
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
router = APIRouter()
@router.post("/register")
def register(user:UserCreate,db:Session = Depends(get_db)):
    # ,current_user = Depends(require_roles(["admin"]))
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400,detail="Email already registered")
    hashed = hash_password(user.password)
    new_user =User(
        name=user.name,
        email=user.email,
        password=hashed,
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(),db:Session=Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not verify_password(form_data.password,user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token= create_token({
         "sub":str(user.id),
         "role":user.role,
         "name":user.name
    })
    return{
        "access_token":token,
        "token_type":"bearer",
        "name":user.name,
        "role":user.role
    }
@router.get("/me")
def get_me(current_user = Depends(get_current_user)):
    return current_user
@router.get("/users", response_model=list[UserResponse])
def get_users(
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["admin"]))
):
    return db.query(User).all()
@router.delete("/user/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin"])),
):
    # prevent admin from deleting themselves
    if int(current_user["id"]) == user_id:
        raise HTTPException(status_code=400, detail="You cannot delete your own account")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"message": f"User {user.name} deleted successfully"}