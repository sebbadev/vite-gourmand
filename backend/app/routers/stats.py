from typing import Optional
from fastapi import APIRouter, Depends, Query
from app.core.database import get_mongo_db
from app.core.deps import require_admin
from app.models.entities import Utilisateur
from app.schemas.stats import (
    AdminStatsResponse,
    GlobalKPIs,
    TopMenuStat,
    MonthlyRevenueStat,
)

router = APIRouter(prefix="/admin", tags=["Administration & Statistiques NoSQL"])


@router.get(
    "/stats",
    response_model=AdminStatsResponse,
    summary="Tableau de bord analytique (Pipelines d'agrégation MongoDB)"
)
async def get_admin_stats(
    annee: Optional[int] = Query(None, ge=2020, le=2100, description="Filtrer les statistiques sur une année donnée (ex: 2026)"),
    current_user: Utilisateur = Depends(require_admin),
    mongo = Depends(get_mongo_db)
):
    """
    Agrège les données dénormalisées de la collection MongoDB 'commandes_stats' :
    1. KPIs financiers globaux (CA HT, TVA, CA TTC, panier moyen, remises)
    2. Classement des menus les plus vendus ($unwind sur le sous-document menus)
    3. Évolution mensuelle du chiffre d'affaires
    Réservé exclusivement aux administrateurs.
    """
    match_stage = {}
    if annee is not None:
        match_stage["annee"] = annee

    # --- 1. Pipeline KPIs Globaux ---
    kpi_pipeline = []
    if match_stage:
        kpi_pipeline.append({"$match": match_stage})

    kpi_pipeline.append({
        "$group": {
            "_id": None,
            "nombre_commandes": {"$sum": 1},
            "ca_ht": {"$sum": "$montant_ht"},
            "tva_collectee": {"$sum": "$montant_tva"},
            "ca_ttc": {"$sum": "$montant_ttc"},
            "panier_moyen_ttc": {"$avg": "$montant_ttc"},
            "total_remises": {"$sum": "$remise_appliquee"},
            "total_frais_livraison": {"$sum": "$frais_livraison"}
        }
    })

    kpi_cursor = mongo.commandes_stats.aggregate(kpi_pipeline)
    kpi_docs = await kpi_cursor.to_list(length=1)

    if kpi_docs:
        raw = kpi_docs[0]
        kpis = GlobalKPIs(
            nombre_commandes=raw.get("nombre_commandes", 0),
            ca_ht=round(raw.get("ca_ht", 0.0), 2),
            tva_collectee=round(raw.get("tva_collectee", 0.0), 2),
            ca_ttc=round(raw.get("ca_ttc", 0.0), 2),
            panier_moyen_ttc=round(raw.get("panier_moyen_ttc", 0.0), 2),
            total_remises=round(raw.get("total_remises", 0.0), 2),
            total_frais_livraison=round(raw.get("total_frais_livraison", 0.0), 2),
        )
    else:
        kpis = GlobalKPIs()

    # --- 2. Pipeline Top Menus ($unwind sur le tableau imbriqué 'menus') ---
    menus_pipeline = []
    if match_stage:
        menus_pipeline.append({"$match": match_stage})

    menus_pipeline.extend([
        {"$unwind": "$menus"},
        {
            "$group": {
                "_id": {
                    "menu_id": "$menus.menu_id",
                    "titre": "$menus.titre"
                },
                "portions_vendues": {"$sum": "$menus.quantite"},
                "ca_genere_brut": {"$sum": "$menus.total_ligne"}
            }
        },
        {"$sort": {"ca_genere_brut": -1, "portions_vendues": -1}}
    ])

    menus_cursor = mongo.commandes_stats.aggregate(menus_pipeline)
    menus_docs = await menus_cursor.to_list(length=50)

    top_menus = [
        TopMenuStat(
            menu_id=doc["_id"]["menu_id"],
            titre=doc["_id"]["titre"],
            portions_vendues=doc["portions_vendues"],
            ca_genere_brut=round(doc["ca_genere_brut"], 2)
        )
        for doc in menus_docs
    ]

    # --- 3. Pipeline Évolution Mensuelle ---
    monthly_pipeline = []
    if match_stage:
        monthly_pipeline.append({"$match": match_stage})

    monthly_pipeline.extend([
        {
            "$group": {
                "_id": {
                    "annee": "$annee",
                    "mois": "$mois"
                },
                "nombre_commandes": {"$sum": 1},
                "ca_ht": {"$sum": "$montant_ht"},
                "ca_ttc": {"$sum": "$montant_ttc"}
            }
        },
        {"$sort": {"_id.annee": 1, "_id.mois": 1}}
    ])

    monthly_cursor = mongo.commandes_stats.aggregate(monthly_pipeline)
    monthly_docs = await monthly_cursor.to_list(length=24)

    evolution_mensuelle = [
        MonthlyRevenueStat(
            annee=doc["_id"]["annee"],
            mois=doc["_id"]["mois"],
            nombre_commandes=doc["nombre_commandes"],
            ca_ht=round(doc["ca_ht"], 2),
            ca_ttc=round(doc["ca_ttc"], 2)
        )
        for doc in monthly_docs
    ]

    return AdminStatsResponse(
        filtre_annee=annee,
        kpis_globaux=kpis,
        top_menus=top_menus,
        evolution_mensuelle=evolution_mensuelle
    )