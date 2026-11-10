Changelog - Vite & Gourmand


# 🎯 Description du document

>Ce log enregistre tous les changements et leurs références effectués au cours du projet

---

## [Unreleased] - Phase 3 (Core Backend)

### Changed
- **Sécurité / Hachage :** Remplacement de `passlib` par `bcrypt` natif pour éliminer les bugs d'incompatibilité de version et garantir un hachage direct sécurisé ($2b$).
- **Sécurité / Tokens JWT :** Remplacement de `python-jose` par `PyJWT` (compatible RFC 7519, activement maintenu).

### Documentation
- Mise à jour du backlog de la tâche P3-03 (Sécurité & Authentification).
