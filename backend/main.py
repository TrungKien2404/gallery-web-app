from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, List
import jwt, bcrypt, os, uuid, shutil
from sqlalchemy import or_
from database import SessionLocal, engine, Base
import models, schemas
from sqlalchemy import func

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Gallery App API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

SECRET_KEY = "change-this-in-production"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def hash_password(p):
    return bcrypt.hashpw(p.encode(), bcrypt.gensalt()).decode()


def verify_password(p, h):
    return bcrypt.checkpw(p.encode(), h.encode())


def create_token(data):
    d = data.copy()
    d["exp"] = datetime.utcnow() + timedelta(hours=24)
    return jwt.encode(d, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        uid = payload.get("sub")
        if uid is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = db.query(models.User).filter(models.User.id == int(uid)).first()

    except:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(models.User).filter(models.User.id == uid).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@app.post("/auth/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(400, "Email already registered")
    if db.query(models.User).filter(models.User.username == user.username).first():
        raise HTTPException(400, "Username taken")
    u = models.User(
        username=user.username, email=user.email, password=hash_password(user.password)
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


@app.post("/auth/login", response_model=schemas.Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form.username).first()
    if not user or not verify_password(form.password, user.password):
        raise HTTPException(401, "Incorrect credentials")
    token = create_token({"sub": str(user.id)})

    return {"access_token": token, "token_type": "bearer"}
    # return {"access_token": create_token({"sub": user.id}), "token_type": "bearer"}


@app.get("/auth/me", response_model=schemas.UserOut)
def me(current_user=Depends(get_current_user)):
    return current_user


@app.post("/photos", response_model=schemas.PhotoOut)
async def upload_photo(
    title: str = Form(...),
    description: str = Form(""),
    file: UploadFile = File(...),
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    ext = os.path.splitext(file.filename)[1]
    fname = f"{uuid.uuid4()}{ext}"
    with open(f"{UPLOAD_DIR}/{fname}", "wb") as buf:
        shutil.copyfileobj(file.file, buf)
    p = models.Photo(
        title=title,
        description=description,
        image_url=f"/uploads/{fname}",
        user_id=current_user.id,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


# @app.get("/photos", response_model=List[schemas.PhotoOut])
# def get_photos(
#     search: Optional[str] = None,
#     db=Depends(get_db),
#     current_user=Depends(get_current_user),
# ):
#     q = db.query(models.Photo).filter(models.Photo.user_id == current_user.id)
#     if search:
#         q = q.filter(
#             or_(
#                 models.Photo.title.ilike(f"%{search}%"),
#                 models.Photo.description.ilike(f"%{search}%"),
#             )
#         )
#     return q.order_by(models.Photo.uploaded_at.desc()).all()

@app.get("/photos", response_model=List[schemas.PhotoOut])
def get_photos(
    search: Optional[str] = None,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    q = db.query(models.Photo).filter(models.Photo.user_id == current_user.id)

    if search:
        q = q.filter(models.Photo.title.ilike(f"%{search}%"))

    photos = q.order_by(models.Photo.uploaded_at.desc()).all()

    result = []
    for p in photos:
        like_count = db.query(func.count(models.Like.id)).filter(
            models.Like.photo_id == p.id
        ).scalar()

        liked = db.query(models.Like).filter(
            models.Like.user_id == current_user.id,
            models.Like.photo_id == p.id
        ).first() is not None

        result.append({
            "id": p.id,
            "title": p.title,
            "description": p.description,
            "image_url": p.image_url,
            "uploaded_at": p.uploaded_at,
            "user_id": p.user_id,
            "like_count": like_count,
            "liked": liked
        })

    return result

@app.get("/photos/{photo_id}", response_model=schemas.PhotoOut)
def get_photo(
    photo_id: int,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    p = (
        db.query(models.Photo)
        .filter(
            models.Photo.id == photo_id,
            models.Photo.user_id == current_user.id
        )
        .first()
    )

    if not p:
        raise HTTPException(404, "Not found")

    # ✅ Đếm like
    like_count = db.query(func.count(models.Like.id)).filter(
        models.Like.photo_id == p.id
    ).scalar()

    # ✅ Check user đã like chưa (QUAN TRỌNG)
    liked = db.query(models.Like).filter(
    models.Like.user_id == current_user.id,
    models.Like.photo_id == p.id
    ).first() is not None

    # ✅ Trả về sạch, không dùng __dict__
    return {
        "id": p.id,
        "title": p.title,
        "description": p.description,
        "image_url": p.image_url,
        "uploaded_at": p.uploaded_at,
        "user_id": p.user_id,
        "like_count": like_count,
        "liked": liked
    }


@app.put("/photos/{photo_id}", response_model=schemas.PhotoOut)
def update_photo(
    photo_id: int,
    update: schemas.PhotoUpdate,
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    p = (
        db.query(models.Photo)
        .filter(models.Photo.id == photo_id, models.Photo.user_id == current_user.id)
        .first()
    )
    if not p:
        raise HTTPException(404, "Not found")
    if update.title is not None:
        p.title = update.title
    if update.description is not None:
        p.description = update.description
    db.commit()
    db.refresh(p)
    return p


@app.delete("/photos/{photo_id}")
def delete_photo(
    photo_id: int, db=Depends(get_db), current_user=Depends(get_current_user)
):
    p = (
        db.query(models.Photo)
        .filter(models.Photo.id == photo_id, models.Photo.user_id == current_user.id)
        .first()
    )
    if not p:
        raise HTTPException(404, "Not found")
    path = p.image_url.lstrip("/")
    if os.path.exists(path):
        os.remove(path)
    db.delete(p)
    db.commit()
    return {"message": "Deleted"}


# LIKE
@app.post("/photos/{photo_id}/like")
def like_photo(
    photo_id: int, db=Depends(get_db), current_user=Depends(get_current_user)
):
    existing = (
        db.query(models.Like)
        .filter(
            models.Like.user_id == current_user.id, models.Like.photo_id == photo_id
        )
        .first()
    )

    if existing:
        raise HTTPException(400, "Already liked")

    like = models.Like(user_id=current_user.id, photo_id=photo_id)
    db.add(like)
    db.commit()

    return {"message": "Liked"}


# UNLIKE
@app.delete("/photos/{photo_id}/like")
def unlike_photo(
    photo_id: int, db=Depends(get_db), current_user=Depends(get_current_user)
):
    like = (
        db.query(models.Like)
        .filter(
            models.Like.user_id == current_user.id, models.Like.photo_id == photo_id
        )
        .first()
    )

    if not like:
        raise HTTPException(404, "Not liked")

    db.delete(like)
    db.commit()

    return {"message": "Unliked"}

# // UPLOAD NHIỀU ẢNH CÙNG LÚC


@app.post("/photos/multiple")
async def upload_multiple(
    files: List[UploadFile] = File(...),
    title: str = Form(...),
    description: str = Form(""),
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    result = []

    for file in files:
        ext = os.path.splitext(file.filename)[1]
        fname = f"{uuid.uuid4()}{ext}"

        with open(f"{UPLOAD_DIR}/{fname}", "wb") as buf:
            shutil.copyfileobj(file.file, buf)

        p = models.Photo(
            title=title,
            description=description,
            image_url=f"/uploads/{fname}",
            user_id=current_user.id
        )

        db.add(p)
        db.commit()
        db.refresh(p)

        result.append(p)

    return result
