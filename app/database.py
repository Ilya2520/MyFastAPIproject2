import os
import uuid
from sqlalchemy import create_engine, Column, String, Integer, Float, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.dialects.postgresql import UUID

POSTGRES_USER = os.environ.get('POSTGRES_USER')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
POSTGRES_HOST = 'db'
POSTGRES_PORT = '5432'
POSTGRES_DB = os.environ.get('POSTGRES_DB')

DATABASE_URL = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'

engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()
#
# engine = create_engine('postgresql://postgres:1234@localhost:5432/postgres')
# Base = declarative_base()
# Session = sessionmaker(bind=engine)
# session = Session()


class MenuModel(Base):
    __tablename__ = 'menus'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String)
    description = Column(String)
    submenus = relationship("SubmenuModel", back_populates="menu")

class SubmenuModel(Base):
    __tablename__ = 'submenus'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String)
    description = Column(String)
    menu_id = Column(UUID(as_uuid=True), ForeignKey("menus.id"))
    menu = relationship("MenuModel", back_populates="submenus")
    dishes = relationship("DishModel", back_populates="submenu")

class DishModel(Base):
    __tablename__ = 'dishes'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String)
    description = Column(String)
    price = Column(String)
    submenu_id = Column(UUID(as_uuid=True), ForeignKey("submenus.id"))
    submenu = relationship("SubmenuModel", back_populates="dishes")

Base.metadata.create_all(bind=engine)



def clear_database(session: Session):
    session.query(DishModel).delete()
    session.query(SubmenuModel).delete()
    session.query(MenuModel).delete()
    session.commit()
