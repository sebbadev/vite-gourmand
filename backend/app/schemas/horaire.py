from datetime import time
from pydantic import BaseModel, ConfigDict


class HoraireRead(BaseModel):
    horaire_id: int
    jour: str
    heure_ouverture: time
    heure_fermeture: time

    model_config = ConfigDict(from_attributes=True)


class HoraireUpdate(BaseModel):
    heure_ouverture: time
    heure_fermeture: time