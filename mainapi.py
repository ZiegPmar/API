from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
import logging
import jwt
import datetime
from passlib.context import CryptContext
from models import Base, User, Role

# Configuration
DATABASE_URL = "mysql+mysqlconnector://evan:ziegheil69@217.154.21.156/rfid_access"
SECRET_KEY = "CeLnMdpToken69000*"
ALGORITHM = "HS256"

# DB + ORM
engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

# Logger
logging.basicConfig(filename="api_logs.txt", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# -----------------------------
# --- MODELS Pydantic
# -----------------------------

class Badge(BaseModel):
    uid: str
    prenom: str
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str

# -----------------------------
# --- DEPENDANCES
# -----------------------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_access_token(data: dict, expires_delta: datetime.timedelta = None):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + (expires_delta or datetime.timedelta(hours=4))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=401, detail="Token invalide ou expiré")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username != "EvanPierreSarah":
            raise credentials_exception
        return username
    except jwt.PyJWTError:
        raise credentials_exception

# -----------------------------
# --- MIDDLEWARE
# -----------------------------

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logging.info(f"Requête {request.method} reçue sur {request.url}")
    response = await call_next(request)
    logging.info(f"Réponse envoyée avec statut {response.status_code}")
    return response

# -----------------------------
# --- ROUTES
# -----------------------------

@app.get("/")
def home():
    return {"message": "Bienvenue sur l'API RFID connectée à MySQL 🎉"}

@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username == "EvanPierreSarah" and form_data.password == "CeLnMdpToken69000*":
        token = create_access_token({"sub": form_data.username})
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Identifiants invalides")

@app.post("/badge")
def add_badge(badge: Badge, user=Depends(get_current_user), db: Session = Depends(get_db)):
    badge.uid = badge.uid.replace(" ", "").lower()  # nettoie l'uid avant insertion
    existing = db.query(User).filter(User.uid == badge.uid).first()
    if existing:
        raise HTTPException(status_code=400, detail="Badge déjà enregistré")
    new_user = User(uid=badge.uid, prenom=badge.prenom, role=badge.role)
    db.add(new_user)
    db.commit()
    return {"message": "Badge ajouté", "uid": badge.uid, "prenom": badge.prenom, "role": badge.role}

@app.get("/scan/{badge_uid}")
def scan_badge(badge_uid: str, user=Depends(get_current_user), db: Session = Depends(get_db)):
    badge_uid = badge_uid.replace(" ", "").lower()  # nettoie l'uid scanné
    badge = db.query(User).filter(User.uid == badge_uid).first()
    if badge:
        return {"message": "Badge reconnu", "id": badge.uid, "role": badge.role, "prenom": badge.prenom}
    return {"message": "Badge non reconnu"}

@app.put("/badge/{badge_uid}")
def update_badge(badge_uid: str, badge: Badge, user=Depends(get_current_user), db: Session = Depends(get_db)):
    badge_uid = badge_uid.replace(" ", "").lower()  # nettoie avant la recherche
    user_db = db.query(User).filter(User.uid == badge_uid).first()
    if not user_db:
        raise HTTPException(status_code=404, detail="Badge non trouvé")
    user_db.prenom = badge.prenom
    user_db.role = badge.role
    db.commit()
    return {"message": "Badge mis à jour", "uid": badge_uid, "prenom": badge.prenom, "role": badge.role}

@app.delete("/badge/{badge_uid}")
def delete_badge(badge_uid: str, user=Depends(get_current_user), db: Session = Depends(get_db)):
    badge_uid = badge_uid.replace(" ", "").lower()  # nettoie avant la recherche
    user_db = db.query(User).filter(User.uid == badge_uid).first()
    if not user_db:
        raise HTTPException(status_code=404, detail="Badge non trouvé")
    db.delete(user_db)
    db.commit()
    return {"message": "Badge supprimé", "uid": badge_uid}
