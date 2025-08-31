"""Domain models using SQLAlchemy ORM."""from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, DateTime, Text, JSON
from datetime import datetime
from typing import List, Optional


class Base(DeclarativeBase):
    pass


class Creator(Base):
    __tablename__ = "creators"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), index=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    contents: Mapped[List["ContentAsset"]] = relationship(back_populates="creator")


class ContentAsset(Base):
    __tablename__ = "content_assets"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("creators.id"), index=True)
    media_type: Mapped[str] = mapped_column(String(50), index=True)  # audio|image|video|text
    title: Mapped[str] = mapped_column(String(300))
    metadata: Mapped[dict] = mapped_column(JSON, default={})
    storage_uri: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    creator: Mapped[Creator] = relationship(back_populates="contents")


class ProtectionRecord(Base):
    __tablename__ = "protection_records"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("content_assets.id"), index=True)
    fingerprint: Mapped[str] = mapped_column(String(512), index=True)
    method: Mapped[str] = mapped_column(String(100))  # watermarking|hashing|blockchain
    details: Mapped[dict] = mapped_column(JSON, default={})
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class CollaborationMatch(Base):
    __tablename__ = "collaboration_matches"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("content_assets.id"), index=True)
    partner_name: Mapped[str] = mapped_column(String(200))
    score: Mapped[int] = mapped_column(Integer)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
