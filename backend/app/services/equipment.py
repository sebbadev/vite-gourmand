from datetime import date
from app.schemas.order import EquipmentPenaltyCheck

DELAI_MAX_JOURS_RESTITUTION = 10
MONTANT_PENALITE_FORFAITAIRE = 600.00


def check_equipment_penalty(date_prestation: date, date_controle: Optional[date] = None) -> EquipmentPenaltyCheck:
    """
    Règle de Gestion RG-04 :
    Vérifie si le délai maximal de 10 jours pour la restitution du matériel prêté
    (vaisselle, chafing dish) est dépassé à la date de contrôle (par défaut aujourd'hui).
    Si le délai est dépassé, une indemnité forfaitaire de 600 € est exigible (CGV).
    """
    if date_controle is None:
        date_controle = date.today()

    jours_ecoules = (date_controle - date_prestation).days
    depassement = jours_ecoules > DELAI_MAX_JOURS_RESTITUTION

    return EquipmentPenaltyCheck(
        date_prestation=date_prestation,
        jours_ecoules=max(0, jours_ecoules),
        depassement=depassement,
        penalite_forfaitaire=MONTANT_PENALITE_FORFAITAIRE if depassement else 0.0
    )