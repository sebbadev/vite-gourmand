def test_catalogue_public_accessible_sans_token(client):
    """Un visiteur non connecté peut consulter les menus et les listes de filtres."""
    res_menus = client.get("/api/v1/menus")
    assert res_menus.status_code == 200
    assert isinstance(res_menus.json(), list)

    res_filtres = client.get("/api/v1/menus/filtres")
    assert res_filtres.status_code == 200
    data = res_filtres.json()
    assert "themes" in data and "regimes" in data and "allergenes" in data


def test_routes_protegees_sans_token_retournent_401(client):
    """Toute route nécessitant une authentification doit renvoyer 401 sans jeton."""
    assert client.get("/api/v1/auth/me").status_code == 401
    assert client.get("/api/v1/commandes/me").status_code == 401
    assert client.get("/api/v1/admin/stats").status_code == 401


def test_client_interdit_sur_routes_employe_et_admin(client, client_token_headers):
    """Un Client authentifié reçoit 403 Forbidden sur les routes back-office."""
    # Tentative d'accès aux statistiques Admin
    res_stats = client.get("/api/v1/admin/stats", headers=client_token_headers)
    assert res_stats.status_code == 403

    # Tentative de création d'un menu (réservé Employé/Admin)
    payload_menu = {
        "titre": "Menu Pirate",
        "nombre_personnes_min": 5,
        "prix_par_personne": 20.0,
        "description": "Test",
        "quantite_disponible": 10,
        "images_url": "/test.webp",
        "plat_ids": [1],
        "theme_ids": [1]
    }
    res_menu = client.post("/api/v1/menus", json=payload_menu, headers=client_token_headers)
    assert res_menu.status_code == 403


def test_employe_interdit_sur_stats_admin(client, employe_token_headers):
    """Un Employé a accès au back-office opérationnel, mais pas aux stats financières Admin (403)."""
    res_stats = client.get("/api/v1/admin/stats", headers=employe_token_headers)
    assert res_stats.status_code == 403