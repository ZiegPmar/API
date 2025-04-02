from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pymysql

# Configuration de la BDD
DATABASE_URL = "mysql+pymysql://evan:ziegheil69@217.154.21.156/rfid_access"

# Création de l'engine SQLAlchemy
engine = create_engine(DATABASE_URL)

# Création de la session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Vérification de la connexion à la BDD
def check_db_connection():
    try:
        with engine.connect() as connection:
            print("✅ Connexion à la base de données réussie !")
    except Exception as e:
        print(f"❌ Erreur de connexion à la base de données : {e}")

# Test connexion
if __name__ == "__main__":
    check_db_connection()
