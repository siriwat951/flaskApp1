from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from app import db
from .contact import Contact


class AuthUser(db.Model, UserMixin, SerializerMixin):
    __tablename__ = "auth_users"
    # primary keys are required by SQLAlchemy
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(1000))
    password = db.Column(db.String(100))
    avatar_url = db.Column(db.String(100))

    # ---------------START EDIT-------------------
    username = db.Column(db.String(1000), unique=True, nullable=True)
    # ---------------END EDIT---------------------

    # Define relationship to PrivateContact
    private_contacts = db.relationship(
        "PrivateContact", back_populates="owner", cascade="all, delete-orphan"
    )

    def __init__(self, email, name, password, avatar_url, username=None):
        self.email = email
        self.name = name
        self.password = password
        self.avatar_url = avatar_url
        # ---------------START EDIT-------------------
        self.username = username
        # ---------------END EDIT---------------------

    def update(self, email, name, avatar_url):
        self.email = email
        self.name = name
        self.avatar_url = avatar_url


class PrivateContact(Contact, SerializerMixin):
    # owner_id = db.Column(db.Integer, db.ForeignKey('auth_users.id'))
    owner_id = db.Column(
        db.Integer,
        db.ForeignKey("auth_users.id", ondelete="CASCADE"),
        nullable=False,
    )

    owner = db.relationship("AuthUser", back_populates="private_contacts")
    # Exclude relationships from serialization
    serialize_rules = ("-owner",)

    def __init__(self, firstname, lastname, phone, owner_id):
        super().__init__(firstname, lastname, phone)
        self.owner_id = owner_id