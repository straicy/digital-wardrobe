from datetime import datetime

from sqlalchemy import ForeignKey, Identity, Unicode
from sqlalchemy.dialects.mssql import DATETIME2, NVARCHAR
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    username: Mapped[str] = mapped_column(Unicode(50), unique=True)
    email: Mapped[str] = mapped_column(Unicode(255), unique=True)
    password_hash: Mapped[str] = mapped_column(Unicode(255))
    created_at: Mapped[datetime | None] = mapped_column(DATETIME2())


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    name: Mapped[str] = mapped_column(Unicode(100), unique=True)


class ClothingItem(Base):
    __tablename__ = "clothing_items"

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    name: Mapped[str] = mapped_column(Unicode(150))
    brand: Mapped[str | None] = mapped_column(Unicode(100))
    color: Mapped[str | None] = mapped_column(Unicode(50))
    description: Mapped[str | None] = mapped_column(NVARCHAR(length=None))
    image_path: Mapped[str | None] = mapped_column(Unicode(500))
    created_at: Mapped[datetime | None] = mapped_column(DATETIME2())


class Outfit(Base):
    __tablename__ = "outfits"

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(Unicode(150))
    description: Mapped[str | None] = mapped_column(NVARCHAR(length=None))
    created_at: Mapped[datetime | None] = mapped_column(DATETIME2())


class OutfitItem(Base):
    __tablename__ = "outfit_items"

    outfit_id: Mapped[int] = mapped_column(
        ForeignKey("outfits.id"), primary_key=True
    )
    clothing_item_id: Mapped[int] = mapped_column(
        ForeignKey("clothing_items.id"), primary_key=True
    )