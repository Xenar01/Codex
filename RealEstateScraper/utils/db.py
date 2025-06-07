"""SQLAlchemy models and helpers for storing scraped data."""

import os
import yaml
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship


def _get_db_url():
    cfg_path = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
    cfg_path = os.path.abspath(cfg_path)
    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    return cfg.get("database", {}).get("url", "sqlite:///realestate.db")


engine = create_engine(_get_db_url(), echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Site(Base):
    __tablename__ = "sites"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    url = Column(String)


class Listing(Base):
    __tablename__ = "listings"
    id = Column(Integer, primary_key=True)
    site_id = Column(Integer, ForeignKey("sites.id"))
    title = Column(String)
    price = Column(String)
    description = Column(Text)
    location = Column(String)
    phone = Column(String)
    site = relationship("Site", backref="listings")


class Image(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True)
    listing_id = Column(Integer, ForeignKey("listings.id"))
    path = Column(String)
    listing = relationship("Listing", backref="images")


def init_db():
    Base.metadata.create_all(bind=engine)


def save_listing(session, site_name: str, data: dict) -> None:
    site = session.query(Site).filter_by(name=site_name).first()
    if not site:
        site = Site(name=site_name, url=data.get("site_url", ""))
        session.add(site)
        session.commit()

    listing = Listing(
        site=site,
        title=data.get("title"),
        price=data.get("price"),
        description=data.get("description"),
        location=data.get("location"),
        phone=data.get("phone"),
    )
    session.add(listing)
    session.commit()

    for img_path in data.get("images", []):
        session.add(Image(listing=listing, path=img_path))
    session.commit()
