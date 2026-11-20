from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union
import bcrypt
import jwt

from app.core.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vérifie qu'un mot de passe en clair correspond à son empreinte hachée (hash).
    Gère la conversion chaîne de caractères (string) vers octets (bytes) pour bcrypt natif.
    """
    password_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def get_password_hash(password: str) -> str:
    """
    Génère une empreinte hachée (hash) salée avec un coût (work factor) de 12.
    """
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def create_access_token(
    subject: Union[str, Any],
    role: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Génère un jeton d'authentification JWT (JSON Web Token) signé en HS256.
    Le jeton contient l'identifiant utilisateur (sub - Subject) et son rôle métier (role).
    """
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        "sub": str(subject),
        "role": str(role),
        "iat": int(now.timestamp()),       # Émis le (Issued At)
        "exp": int(expire.timestamp())     # Expire le (Expiration Time)
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Décode et valide la signature cryptographique ainsi que la date d'expiration du jeton.
    Lève jwt.PyJWTError si le jeton est invalide ou expiré.
    """
    payload = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM]
    )
    return payload