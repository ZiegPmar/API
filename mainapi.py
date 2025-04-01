from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import logging

# Configuration du logging
logging.basicConfig(
    filename="api_logs.txt",  # Fichier de logs
    level=logging.INFO,        # Niveau de log
    format="%(asctime)s - %(levelname)s - %(message)s",
)

app = FastAPI()

# Bdd ( pas une vraie, c'est une simulation )
badge_db = {}

class Badge(BaseModel):
    id: str
    role: str

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logging.info(f"Requête {request.method} reçue sur {request.url}")
    response = await call_next(request)
    logging.info(f"Réponse envoyée avec statut {response.status_code}")
    return response

@app.get("/")
def home():
    logging.info("Accès à la page d'accueil")
    return {"message": "Bienvenue sur mon API FastAPI RFID 🚀"}

# Ajouter un badge
@app.post("/badge")
def add_badge(badge: Badge):
    if badge.id in badge_db:
        logging.warning(f"Tentative d'ajout d'un badge déjà existant : {badge.id}")
        raise HTTPException(status_code=400, detail="Badge déjà enregistré")
    badge_db[badge.id] = badge.role
    logging.info(f"Badge ajouté : ID={badge.id}, Role={badge.role}")
    return {"message": "Badge ajouté", "id": badge.id, "role": badge.role}

# Vérifier un badge
@app.get("/scan/{badge_id}")
def scan_badge(badge_id: str):
    if badge_id in badge_db:
        logging.info(f"Badge reconnu : ID={badge_id}, Role={badge_db[badge_id]}")
        return {"message": "Badge reconnu", "id": badge_id, "role": badge_db[badge_id]}
    logging.warning(f"Badge non reconnu : {badge_id}")
    return {"message": "Badge non reconnu"}

# Modifier un badge
@app.put("/badge/{badge_id}")
def update_badge(badge_id: str, badge: Badge):
    if badge_id not in badge_db:
        logging.warning(f"Tentative de modification d'un badge non trouvé : {badge_id}")
        raise HTTPException(status_code=404, detail="Badge non trouvé")
    badge_db[badge_id] = badge.role
    logging.info(f"Badge mis à jour : ID={badge_id}, Nouveau Role={badge.role}")
    return {"message": "Badge mis à jour", "id": badge_id, "role": badge.role}

# Supprimer un badge
@app.delete("/badge/{badge_id}")
def delete_badge(badge_id: str):
    if badge_id not in badge_db:
        logging.warning(f"Tentative de suppression d'un badge non trouvé : {badge_id}")
        raise HTTPException(status_code=404, detail="Badge non trouvé")
    del badge_db[badge_id]
    logging.info(f"Badge supprimé : ID={badge_id}")
    return {"message": "Badge supprimé", "id": badge_id}
