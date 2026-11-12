from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class ContactCreate(BaseModel):
    nom: str = Field(..., min_length=2, max_length=50)
    prenom: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    telephone: Optional[str] = Field(None, max_length=20)
    objet: str = Field(..., min_length=3, max_length=120)
    message: str = Field(..., min_length=10, max_length=2000)
    rgpd_consent: bool = Field(..., description="Consentement RGPD obligatoire")


class ContactRead(BaseModel):
    id: str
    nom: str
    prenom: str
    email: str
    telephone: Optional[str] = None
    objet: str
    message: str
    traite: bool
    created_at: datetime