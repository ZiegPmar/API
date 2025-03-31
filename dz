from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import logging
import jwt
import datetime
from passlib.context import CryptContext

# Clé secrète pour signer les JWT
SECRET_KEY = "CeLnMdpToken69000*"
ALGORITHM = "HS256"

# Configuration du logging
logging.basicConfig(
    filename="api_logs.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

app = FastAPI()

# Simuler une base de données d'utilisateurs
fake_users_db = {
    "admin": {
        "username": "admin",
        "full_name": "Admin User",
        "hashed_password": "$2b$12$VbZz.vCd1JihsQdoRyRVhuF5VmH/z0V6WBp7.1K1E5F2kZog7HIHy",  # "password"
        "disabled": False,
    }
}

# Configuration de l'authentification
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Simulation d'une base de données de badges
badge_db = {}

class Badge(BaseModel):
    id: str
    role: str
    owner: str

class Token(BaseModel):
    access_token: str
    token_type: str

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(username: str, password: str):
    user = fake_users_db.get(username)
    if not user or not verify_password(password, user["hashed_password"]):
        return False
    return user

def create_access_token(data: dict, expires_delta: datetime.timedelta):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token invalide")
        return fake_users_db.get(username)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expiré")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token invalide")

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Identifiants invalides")
    
    access_token = create_access_token(data={"sub": user["username"]}, expires_delta=datetime.timedelta(hours=1))
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/")
def home():
    logging.info("Accès à la page d'accueil")
    return {"message": "Bienvenue sur mon API sécurisée avec JWT 🚀"}

@app.post("/badge")
def add_badge(badge: Badge, user: str = Depends(get_current_user)):
    if badge.id in badge_db:
        logging.warning(f"Tentative d'ajout d'un badge déjà existant : {badge.id}")
        raise HTTPException(status_code=400, detail="Badge déjà enregistré")
    badge_db[badge.id] = {"role": badge.role, "owner": badge.owner}
    logging.info(f"Badge ajouté : ID={badge.id}, Role={badge.role}, Propriétaire={badge.owner}")
    return {"message": "Badge ajouté", "id": badge.id, "role": badge.role, "owner": badge.owner}

@app.get("/scan/{badge_id}")
def scan_badge(badge_id: str, user: str = Depends(get_current_user)):
    if badge_id in badge_db:
        logging.info(f"Badge reconnu : ID={badge_id}, Role={badge_db[badge_id]['role']}, Propriétaire={badge_db[badge_id]['owner']}")
        return {"message": "Badge reconnu", "id": badge_id, "role": badge_db[badge_id]['role'], "owner": badge_db[badge_id]['owner']}
    logging.warning(f"Badge non reconnu : {badge_id}")
    return {"message": "Badge non reconnu"}

@app.put("/badge/{badge_id}")
def update_badge(badge_id: str, badge: Badge, user: str = Depends(get_current_user)):
    if badge_id not in badge_db:
        logging.warning(f"Tentative de modification d'un badge non trouvé : {badge_id}")
        raise HTTPException(status_code=404, detail="Badge non trouvé")
    badge_db[badge_id] = {"role": badge.role, "owner": badge.owner}
    logging.info(f"Badge mis à jour : ID={badge_id}, Nouveau Role={badge.role}, Nouveau Propriétaire={badge.owner}")
    return {"message": "Badge mis à jour", "id": badge_id, "role": badge.role, "owner": badge.owner}

@app.delete("/badge/{badge_id}")
def delete_badge(badge_id: str, user: str = Depends(get_current_user)):
    if badge_id not in badge_db:
        logging.warning(f"Tentative de suppression d'un badge non trouvé : {badge_id}")
        raise HTTPException(status_code=404, detail="Badge non trouvé")
    del badge_db[badge_id]
    logging.info(f"Badge supprimé : ID={badge_id}")
    return {"message": "Badge supprimé", "id": badge_id}
