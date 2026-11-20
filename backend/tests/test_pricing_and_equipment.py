from datetime import date, timedelta
from unittest.mock import MagicMock
import pytest
from fastapi import HTTPException

from app.models.entities import Menu
from app.schemas.order import OrderItemCreate
from app.services.pricing import calculate_order_quote
from app.services.equipment import check_equipment_penalty


def make_mock_menu(menu_id: int = 1, titre: str = "Menu Test", min_pers: int = 10, prix: float = 40.0) -> Menu:
    """Fabrique un objet Menu simulé en mémoire sans solliciter PostgreSQL."""
    menu = MagicMock(spec=Menu)
    menu.menu_id = menu_id
    menu.titre = titre
    menu.nombre_personnes_min = min_pers
    menu.prix_par_personne = prix
    menu.is_active = True
    menu.is_deleted = False
    return menu


# --- TESTS TARIFICATION (RG-01, RG-02, RG-03) ---

def test_quote_standard_sans_remise():
    """RG-01 & RG-03 : 10 convives (minimum exact) à 40 €, livraison à 10 km."""
    db = MagicMock()
    db.execute.return_value.scalar_one_or_none.return_value = make_mock_menu(min_pers=10, prix=40.0)

    items = [OrderItemCreate(menu_id=1, quantite=10)]
    quote = calculate_order_quote(items=items, distance_km=10.0, db=db)

    assert quote.sous_total_brut == 400.0
    assert quote.eligible_remise is False
    assert quote.remise_appliquee == 0.0
    assert quote.frais_livraison == 10.90  # 5.00 + 10 * 0.59
    assert quote.prix_total == 410.90


def test_quote_avec_remise_volume_10_pourcent():
    """RG-02 : Seuil min (10) + 5 = 15 convives -> remise de 10% déclenchée."""
    db = MagicMock()
    db.execute.return_value.scalar_one_or_none.return_value = make_mock_menu(min_pers=10, prix=40.0)

    items = [OrderItemCreate(menu_id=1, quantite=15)]
    quote = calculate_order_quote(items=items, distance_km=0.0, db=db)

    assert quote.sous_total_brut == 600.0
    assert quote.eligible_remise is True
    assert quote.remise_appliquee == 60.0       # 10% de 600 €
    assert quote.sous_total_apres_remise == 540.0
    assert quote.frais_livraison == 5.0         # Forfait minimal 5.00 €
    assert quote.prix_total == 545.0


def test_quote_quantite_inferieure_au_minimum_echoue():
    """RG-01 : Rejet HTTP 400 si la quantité est inférieure au minimum requis par le menu."""
    db = MagicMock()
    db.execute.return_value.scalar_one_or_none.return_value = make_mock_menu(min_pers=10, prix=40.0)

    items = [OrderItemCreate(menu_id=1, quantite=8)]
    with pytest.raises(HTTPException) as exc_info:
        calculate_order_quote(items=items, distance_km=5.0, db=db)

    assert exc_info.value.status_code == 400
    assert "requiert un minimum de" in exc_info.value.detail

# --- TESTS MATÉRIEL & PÉNALITÉ 600 € (RG-04) ---

def test_materiel_dans_les_delais():
    """RG-04 : Prestation il y a 7 jours (<= 10 jours) -> pas de pénalité."""
    date_prest = date.today() - timedelta(days=7)
    res = check_equipment_penalty(date_prestation=date_prest)

    assert res.jours_ecoules == 7
    assert res.depassement is False
    assert res.penalite_forfaitaire == 0.0


def test_materiel_en_retard_penalite_600():
    """RG-04 : Prestation il y a 12 jours (> 10 jours) -> pénalité forfaitaire de 600 €."""
    date_prest = date.today() - timedelta(days=12)
    res = check_equipment_penalty(date_prestation=date_prest)

    assert res.jours_ecoules == 12
    assert res.depassement is True
    assert res.penalite_forfaitaire == 600.0