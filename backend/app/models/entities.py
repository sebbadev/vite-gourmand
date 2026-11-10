import enum
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Text,
    DateTime, Date, Time, ForeignKey, Enum, Table, func
)
from sqlalchemy.orm import relationship

from app.core.database import Base


# --- 1. Énumérations Python alignées sur les ENUMs natifs PostgreSQL ---

class DishType(str, enum.Enum):
    ENTREE = "Entrée"
    MAIN_DISH = "Plat principal"
    ACCOMPAGNEMENT = "Accompagnement"
    DESSERT = "Dessert"


class Equipment(str, enum.Enum):
    INCLUDED = "Inclus"
    NON_INCLUDED = "Non inclus"
    RETURNED = "Retourné"


class Rating(str, enum.Enum):
    CRITICAL = "Critique"
    TO_IMPROVE = "À améliorer"
    ACCEPTABLE = "Correct"
    GOOD = "Bien"
    EXCELLENT = "Excellent"


class OrderStatus(str, enum.Enum):
    PENDING = "En attente de validation"
    CONFIRMED = "Acceptée"
    CANCELLED = "Annulée"
    PREPARING = "En préparation"
    READY = "En cours de livraison"
    DELIVERED = "Livrée"
    COMPLETED = "Terminée"


class PaymentStatus(str, enum.Enum):
    DUE = "En attente de règlement"
    CANCELLED = "Annulée"
    PAID = "Réglée"


class ReviewStatus(str, enum.Enum):
    PENDING = "En attente"
    APPROVED = "Approuvé"
    ANSWERED = "Répondu"
    REJECTED = "Rejeté"


class UserRole(str, enum.Enum):
    ADMIN = "Administrateur"
    CHEF = "Chef"
    EMPLOYE = "Employé"
    CLIENT = "Client"


class ContactMode(str, enum.Enum):
    TELEPHONE = "Téléphone"
    EMAIL = "Email"


# Helper pour réutiliser les ENUMs existants dans PostgreSQL sans les recréer
def pg_enum(enum_cls, name: str):
    return Enum(
        enum_cls,
        name=name,
        values_callable=lambda x: [e.value for e in x],
        create_type=False
    )


# --- 2. Tables d'association (Many-to-Many) ---

menus_plats = Table(
    "menus_plats",
    Base.metadata,
    Column("menu_id", Integer, ForeignKey("menus.menu_id", ondelete="CASCADE"), primary_key=True),
    Column("plat_id", Integer, ForeignKey("plats.plat_id", ondelete="CASCADE"), primary_key=True),
)

menus_themes = Table(
    "menus_themes",
    Base.metadata,
    Column("menu_id", Integer, ForeignKey("menus.menu_id", ondelete="CASCADE"), primary_key=True),
    Column("theme_id", Integer, ForeignKey("themes.theme_id", ondelete="CASCADE"), primary_key=True),
)

plats_allergenes = Table(
    "plats_allergenes",
    Base.metadata,
    Column("plat_id", Integer, ForeignKey("plats.plat_id", ondelete="CASCADE"), primary_key=True),
    Column("allergene_id", Integer, ForeignKey("allergenes.allergene_id", ondelete="CASCADE"), primary_key=True),
)

plats_regimes = Table(
    "plats_regimes",
    Base.metadata,
    Column("plat_id", Integer, ForeignKey("plats.plat_id", ondelete="CASCADE"), primary_key=True),
    Column("regime_id", Integer, ForeignKey("regimes.regime_id", ondelete="CASCADE"), primary_key=True),
)

plats_themes = Table(
    "plats_themes",
    Base.metadata,
    Column("plat_id", Integer, ForeignKey("plats.plat_id", ondelete="CASCADE"), primary_key=True),
    Column("theme_id", Integer, ForeignKey("themes.theme_id", ondelete="CASCADE"), primary_key=True),
)


# --- 3. Modèles ORM alignés sur le schéma existant ---

class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String(50), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    prenom = Column(String(50), nullable=False)
    nom = Column(String(50), nullable=False)
    telephone = Column(String(50), nullable=True)
    adresse = Column(String(255), nullable=True)
    code_postal = Column(String(50), nullable=True)
    ville = Column(String(50), nullable=True)
    pays = Column(String(50), nullable=True)
    role = Column(pg_enum(UserRole, "user_role"), nullable=False, default=UserRole.CLIENT)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)

    commandes = relationship("Commande", back_populates="client")
    avis = relationship("Avis", back_populates="auteur")


class Menu(Base):
    __tablename__ = "menus"

    menu_id = Column(Integer, primary_key=True, index=True)
    titre = Column(String(50), nullable=False)
    nombre_personnes_min = Column(Integer, nullable=False)
    prix_par_personne = Column(Float, nullable=False)
    description = Column(Text, nullable=False)
    quantite_disponible = Column(Integer, nullable=False)
    images_url = Column(String(255), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)

    plats = relationship("Plat", secondary=menus_plats, back_populates="menus")
    themes = relationship("Theme", secondary=menus_themes, back_populates="menus")
    avis = relationship("Avis", back_populates="menu")


class Plat(Base):
    __tablename__ = "plats"

    plat_id = Column(Integer, primary_key=True, index=True)
    titre = Column(String(50), nullable=False)
    type_de_plat = Column(pg_enum(DishType, "dish_types"), nullable=False)
    images_url = Column(String(255), nullable=True)

    menus = relationship("Menu", secondary=menus_plats, back_populates="plats")
    allergenes = relationship("Allergene", secondary=plats_allergenes, back_populates="allergenes")
    regimes = relationship("Regime", secondary=plats_regimes, back_populates="regimes")
    themes = relationship("Theme", secondary=plats_themes, back_populates="themes")


class Commande(Base):
    __tablename__ = "commandes"

    commande_id = Column(Integer, primary_key=True, index=True)
    numero_commande = Column(String(50), nullable=False, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("utilisateurs.user_id"), nullable=False)
    date_prestation = Column(Date, nullable=False)
    heure_livraison = Column(Time, nullable=False)
    adresse_livraison = Column(String(255), nullable=True)
    distance_km = Column(Float, default=0.0)
    frais_livraison = Column(Float, default=0.0)
    prix_total = Column(Float, nullable=False)
    remise_appliquee = Column(Float, default=0.0)
    statut = Column(pg_enum(OrderStatus, "order_status"), default=OrderStatus.PENDING)
    date_commande = Column(DateTime(timezone=True), server_default=func.now())
    statut_paiement = Column(pg_enum(PaymentStatus, "payment_status"), default=PaymentStatus.DUE)
    statut_materiel = Column(pg_enum(Equipment, "equipment"), default=Equipment.INCLUDED)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)
    motif_annulation = Column(Text, nullable=True)
    mode_contact_annulation = Column(pg_enum(ContactMode, "contact_mode"), nullable=True)
    contact_client_effectue = Column(Boolean, default=False)

    client = relationship("Utilisateur", back_populates="commandes")
    details = relationship("CommandeDetail", back_populates="commande", cascade="all, delete-orphan")


class CommandeDetail(Base):
    __tablename__ = "commande_details"

    detail_id = Column(Integer, primary_key=True, index=True)
    commande_id = Column(Integer, ForeignKey("commandes.commande_id"), nullable=False)
    menu_id = Column(Integer, ForeignKey("menus.menu_id"), nullable=False)
    quantite = Column(Integer, nullable=False)
    prix_applique = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)

    commande = relationship("Commande", back_populates="details")
    menu = relationship("Menu")


class Avis(Base):
    __tablename__ = "avis"

    avis_id = Column(Integer, primary_key=True, index=True)
    description = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("utilisateurs.user_id"), nullable=True)
    menu_id = Column(Integer, ForeignKey("menus.menu_id"), nullable=True)
    statut = Column(pg_enum(ReviewStatus, "review_status"), default=ReviewStatus.PENDING)
    qualite = Column(pg_enum(Rating, "notes"), nullable=True)
    service = Column(pg_enum(Rating, "notes"), nullable=True)
    prix = Column(pg_enum(Rating, "notes"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)

    auteur = relationship("Utilisateur", back_populates="avis")
    menu = relationship("Menu", back_populates="avis")


class Horaire(Base):
    __tablename__ = "horaires"

    horaire_id = Column(Integer, primary_key=True)
    jour = Column(String(50), nullable=False)
    heure_ouverture = Column(Time, nullable=False)
    heure_fermeture = Column(Time, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)


class Allergene(Base):
    __tablename__ = "allergenes"

    allergene_id = Column(Integer, primary_key=True)
    libelle = Column(String(50), nullable=False)

    plats = relationship("Plat", secondary=plats_allergenes, back_populates="allergenes")


class Regime(Base):
    __tablename__ = "regimes"

    regime_id = Column(Integer, primary_key=True)
    libelle = Column(String(50), nullable=False)

    plats = relationship("Plat", secondary=plats_regimes, back_populates="regimes")


class Theme(Base):
    __tablename__ = "themes"

    theme_id = Column(Integer, primary_key=True)
    libelle = Column(String(50), nullable=False)

    menus = relationship("Menu", secondary=menus_themes, back_populates="themes")
    plats = relationship("Plat", secondary=plats_themes, back_populates="themes")