from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Text, 
    DateTime, Date, Time, ForeignKey, Enum, Table, func
)
from sqlalchemy.orm import relationship, DeclarativeBase
import enum

# --- 1. Python Enums for Business Logic & Type Safety ---

class DishType(enum.Enum):
    ENTREE = "Entrée"
    MAIN_DISH = "Plat principal"
    ACCOMPAGNEMENT = "Accompagnement"
    DESSERT = "Dessert"

class Equipment(enum.Enum):
    INCLUDED = "Inclus"
    NON_INCLUDED = "Non inclus"
    RETURNED = "Retourné"

class Rating(enum.Enum):
    CRITICAL = 'Critique'
    TO_IMPROVE = 'À améliorer'
    ACCEPTABLE = 'Correct'
    GOOD = 'Bien'
    EXCELLENT = 'Excellent'

class OrderStatus(enum.Enum):
    PENDING = "En attente de validation"
    CONFIRMED = "Acceptée"
    CANCELLED = "Annulée"
    PREPARING = "En préparation"
    READY = "En cours de livraison"
    DELIVERED = "Livrée"
    COMPLETED = "Terminée"

class PaymentStatus(enum.Enum):    
    DUE = "En attente de règlement"
    CANCELLED = "Annulée"
    PAID = "Réglée"

class ReviewStatus(enum.Enum):
    PENDING = "En attente"
    APPROVED = "Approuvé"
    ANSWERED = "Répondu"
    REJECTED = "Rejeté"

class UserRole(enum.Enum):
    ADMIN = "Administrateur"
    CHEF = "Chef"
    EMPLOYE = "Employé"
    CLIENT = "Client"

class ContactMode(str, enum.Enum):
    TELEPHONE = "Téléphone"
    EMAIL = "Email"

# --- 2. Base & Association Tables ---

class Base(DeclarativeBase):
    pass

# Association tables for Many-to-Many relationships
menus_plats = Table(
    "menus_plats", Base.metadata,
    Column("menu_id", Integer, ForeignKey("menus.menu_id", ondelete="CASCADE"), primary_key=True),
    Column("plat_id", Integer, ForeignKey("plats.plat_id", ondelete="CASCADE"), primary_key=True),
)

menus_themes = Table(
    "menus_themes", Base.metadata,
    Column("menu_id", Integer, ForeignKey("menus.menu_id", ondelete="CASCADE"), primary_key=True),
    Column("theme_id", Integer, ForeignKey("themes.theme_id", ondelete="CASCADE"), primary_key=True),
)

plats_allergenes = Table(
    "plats_allergenes", Base.metadata,
    Column("plat_id", Integer, ForeignKey("plats.plat_id", ondelete="CASCADE"), primary_key=True),
    Column("allergene_id", Integer, ForeignKey("allergenes.allergene_id", ondelete="CASCADE"), primary_key=True),
)

plats_regimes = Table(
    "plats_regimes", Base.metadata,
    Column("plat_id", Integer, ForeignKey("plats.plat_id", ondelete="CASCADE"), primary_key=True),
    Column("regime_id", Integer, ForeignKey("regimes.regime_id", ondelete="CASCADE"), primary_key=True),
)

plats_themes = Table(
    "plats_themes", Base.metadata,
    Column("plat_id", Integer, ForeignKey("plats.plat_id", ondelete="CASCADE"), primary_key=True),
    Column("theme_id", Integer, ForeignKey("themes.theme_id", ondelete="CASCADE"), primary_key=True),
)

# --- 3. Models ---

class Utilisateur(Base):
    __tablename__ = "utilisateurs"
    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String(50), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    prenom = Column(String(50), nullable=False)
    nom = Column(String(50), nullable=False)
    telephone = Column(String(50))
    adresse = Column(String(255))
    code_postal = Column(String(50))
    ville = Column(String(50))
    pays = Column(String(50))
    # Using the UserRole Enum class
    role = Column(Enum(UserRole), nullable=False, default=UserRole.CLIENT)
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
    is_active = Column(Boolean, nullable=False, server_default='true')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)

    plats = relationship("Plat", secondary=menus_plats, back_populates="menus")
    themes = relationship("Theme", secondary=menus_themes, back_populates="menus")
    avis = relationship("Avis", back_populates="menu")

    @property
    def allergenes(self):
        allergen_list = []
        for plat in self.plats:
            for allergene in plat.allergenes:
                if allergene not in allergen_list:
                    allergen_list.append(allergene)
        return allergen_list

    @property
    def regimes_valides(self):
        if not self.plats: return []
        common_regimes = {r.libelle for r in self.plats[0].regimes}
        for plat in self.plats[1:]:
            common_regimes &= {r.libelle for r in plat.regimes}
            if not common_regimes: break
        return list(common_regimes)

class Plat(Base):
    __tablename__ = "plats"
    plat_id = Column(Integer, primary_key=True, index=True)
    titre = Column(String(50), nullable=False)
    type_de_plat = Column(Enum(DishType), nullable=False) # Linked to DishType Enum
    images_url = Column(String(255))

    menus = relationship("Menu", secondary=menus_plats, back_populates="plats")
    allergenes = relationship("Allergene", secondary=plats_allergenes, back_populates="plats")
    regimes = relationship("Regime", secondary=plats_regimes, back_populates="plats")
    themes = relationship("Theme", secondary=plats_themes, back_populates="plats")

class Commande(Base):
    __tablename__ = "commandes"
    commande_id = Column(Integer, primary_key=True, index=True)
    numero_commande = Column(String(50), nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey("utilisateurs.user_id"), nullable=False)
    date_prestation = Column(Date, nullable=False)
    heure_livraison = Column(DateTime(timezone=True), nullable=False)
    prix_total = Column(Float, nullable=False)
    remise_appliquee = Column(Float)
    statut = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    date_commande = Column(DateTime(timezone=True), server_default=func.now())
    statut_paiement = Column(Enum(PaymentStatus), default=PaymentStatus.DUE)
    statut_materiel = Column(Enum(Equipment), default=Equipment.INCLUDED)
    is_deleted = Column(Boolean, default=False)
    motif_annulation = Column(Text, nullable=True)
    mode_contact_annulation = Column(Enum(ContactMode), name="contact_mode", nullable=True)
    contact_client_effectue = Column(Boolean, default=False)
    client = relationship("Utilisateur", back_populates="commandes")
    details = relationship("CommandeDetail", back_populates="commande")

class CommandeDetail(Base):
    __tablename__ = "commande_details"
    detail_id = Column(Integer, primary_key=True, index=True)
    commande_id = Column(Integer, ForeignKey("commandes.commande_id"), nullable=False)
    menu_id = Column(Integer, ForeignKey("menus.menu_id"), nullable=False)
    quantite = Column(Integer, nullable=False)
    prix_applique = Column(Float, nullable=False)
    
    commande = relationship("Commande", back_populates="details")

class Avis(Base):
    __tablename__ = "avis"
    avis_id = Column(Integer, primary_key=True, index=True)
    description = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("utilisateurs.user_id"))
    menu_id = Column(Integer, ForeignKey("menus.menu_id"))
    statut = Column(Enum(ReviewStatus), default=ReviewStatus.PENDING)
    qualite = Column(Enum(Rating))
    service = Column(Enum(Rating))
    prix = Column(Enum(Rating))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_deleted = Column(Boolean, default=False)

    auteur = relationship("Utilisateur", back_populates="avis")
    menu = relationship("Menu", back_populates="avis")

class Horaire(Base):
    __tablename__ = "horaires"
    horaire_id = Column(Integer, primary_key=True)
    jour = Column(String(50), nullable=False)
    heure_ouverture = Column(Time, nullable=False)
    heure_fermeture = Column(Time, nullable=False)

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