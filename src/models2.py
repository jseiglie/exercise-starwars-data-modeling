from __future__ import annotations
from typing import List
from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy import Column
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from eralchemy2 import render_er

class Base(DeclarativeBase):
    pass
#ejemplo en la documentacion de SQLAlchemy v2
class User(Base):
    __tablename__ = "user_account"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    fullname: Mapped[Optional[str]]
    addresses: Mapped[List["Address"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"

class Address(Base):
    __tablename__ = "address"
    id: Mapped[int] = mapped_column(primary_key=True)
    email_address: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    user: Mapped["User"] = relationship(back_populates="addresses")
    def __repr__(self) -> str:
        return f"Address(id={self.id!r}, email_address={self.email_address!r})"
    

#Many to many using association TABLE
#definicion de la tabla
Association_table = Table(
    #NOMBRE DE LA TABLA
    "association_table",
    #necesario
    Base.metadata,
    #Columna ("nombre", ForeignKey(a donde se conecta), primary_key=True) --> SIEMPRE A LA PRIMARY KEY, ASI QUE AL ID
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("planet_id", ForeignKey("planets.id"), primary_key=True),
    Column("movies_id", ForeignKey("movies.id"), primary_key=True),
    Column("people_id", ForeignKey("people.id"), primary_key=True)
)


#todas las class son MODELOS
#nombres siempre en PLURAL
class Users(Base):
    #consejo, siempre poner los nombres a las tablas con __tablename__
    __tablename__= "users"
    #id, siempre primary_key, por aqui conectamos las tablas y siempre será lo mismo
    id: Mapped[int] = mapped_column(primary_key=True)
    #columna: Mapped[tipo de dato] = mapped_column(si es String y quieres ponerle una cantidad de caracteres, lo defines aqui) 
    email: Mapped[str] = mapped_column(String(120))
    password: Mapped[str] = mapped_column(String(250))
    #one to one
    #columna = relationship("modelo", back_populates="columna que va a recibir la info en el modelo al que conectamos")
    profile = relationship("Profiles", back_populates="user")
    #one to MANY
    #Mapped[List["Posts"]] porque es relacion MANY, asi que recibimos mas de un valor
    #columna: Mapped[List["modelo"]] = relationship(
    #     back_populates="columna donde se refleja en el modelo que conectamos", cascade="all, delete-orphan" --> para que al borrar en uno se borre en el modelo conectado
    #)
    posts: Mapped[List["Posts"]] = relationship(
          back_populates="user", cascade="all, delete-orphan"
   )
    #many-to-many por TABLE
    #columna: Mapped[List[modelo]] relationship(secondary="TABLA de asociacion", back_populates="columna de la TABLA de asociacion a la que conectamos")
    fav_people: Mapped[List[People]] = relationship(secondary="association_table", back_populates="user_id")
    fav_planets: Mapped[List[Planets]] = relationship(secondary="association_table", back_populates="user_id")
    fav_movies: Mapped[List[Movies]] = relationship(secondary="association_table", back_populates="user_id")
        
    #many-to-many POR CLASS
    #columna           Mapped[List[modelo de asociacion]] = relationship(back_populates="donde se reflejara el modelo de asociacion")
    fav_class_planets: Mapped[List[AssociationClass]] = relationship(back_populates="class_user_planets")
    fav_class_people: Mapped[List[AssociationClass]] = relationship(back_populates="class_user_people")
    fav_class_movies: Mapped[List[AssociationClass]] = relationship(back_populates="class_user_movies")


#Usamos List en fav_class_movies: Mapped[List[AssociationClass]] y en fav_planets: Mapped[List[Planets]] 
# porque se van a recibir mas de un valor, ya que es una relacion muchos a mucho

class Profiles(Base):
    __tablename__= "profiles"
    id: Mapped[int] = mapped_column(primary_key=True)
    fullname: Mapped[str] = mapped_column(String(120))
    #one to one
    #columna =mapped_column(ForeignKey("id del modelo al que conectamos")) 
    user_id = mapped_column(ForeignKey("users.id"))
    #columna = relationship("modelo", back_populates="columna del modelo al que conectamos donde se refleja")
    user = relationship("User", back_populates="profile")

class Posts(Base):
    __tablename__= "posts"
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(String(120))
    image_url: Mapped[str] = mapped_column(String(120))
    #one to many
    #columna: Mapped[int] = mapped_column(ForeignKey("id del modelo al que conectamos")) 
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))


class Planets(Base):
    __tablename__= "planets"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
        #many-to-many using TABLE
    user_id: Mapped[List[Users]] = relationship(secondary=Association_table, back_populates="fav_planets")
            #many-to-may using CLASS
    #columna       mapped[List["tabla de asociacion por clase"]] = relationship(back_populates="campo donde se reflejara, en este caso, lo queremos en USERS")
    class_user_id: Mapped[List["AssociationClass"]] = relationship(back_populates="fav_class_planets")

class People(Base):
    __tablename__= "people"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
        #many-to-many using TABLE
        #columna mapped[List["modelo"]] = relationship(secondary=tabla de asociacion, back_populates="campo donde se reflejara, en este caso, lo queremos en USERS" )
    user_id: Mapped[List[Users]] = relationship(secondary=Association_table, back_populates="fav_people")
        #many-to-may using CLASS
    #columna       mapped[List["tabla de asociacion por clase"]] = relationship(back_populates="campo donde se reflejara, en este caso, lo queremos en USERS")
    class_user_id: Mapped[List["AssociationClass"]] = relationship(back_populates="fav_class_people")



class Movies(Base):
    __tablename__= "movies"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
        #many-to-many using TABLE
    #columna mapped[List["modelo"]] = relationship(secondary=tabla de asociacion, back_populates="campo donde se reflejara, en este caso, lo queremos en USERS" )
    user_id: Mapped[List[Users]] = relationship(secondary=Association_table, back_populates="fav_movies")
    #many-to-may using CLASS
    #columna       mapped[List["tabla de asociacion por clase"]] = relationship(back_populates="campo donde se reflejara, en este caso, lo queremos en USERS")
    class_user_id: Mapped[List["AssociationClass"]] = relationship(back_populates="fav_class_movies")

#association CLASS usado para cuando se quieren añadir datos extras ademas de la relacion, añadimos unas notas del usuario de su favorito como ejemplo
class AssociationClass(Base):
    __tablename__= "association_class"
    #traemos a la clase los id con mapped_column y ForeignKey
    planet_id: Mapped[int] = mapped_column(ForeignKey("planets.id"), primary_key=True)
    people_id: Mapped[int] = mapped_column(ForeignKey("people.id"), primary_key=True)
    movies_id: Mapped[int] = mapped_column(ForeignKey("movies.id"), primary_key=True)
    #Si puede estar vacio el campo le pones Optional cuando hacemos el Mapped
    notas: Mapped[Optional[str]]= mapped_column(String(250))
    #hacemos que se cree la relacion bidireccional
    #columna             Mapped[modelo]    = relationship(back_populates = "campo del modelo donde veremos la info")
    class_user_planets : Mapped["Planets"] = relationship(back_populates="class_user_id")
    class_user_people : Mapped["People"] = relationship(back_populates="class_user_id")
    class_user_movies : Mapped["Movies"] = relationship(back_populates="class_user_id")





## Draw from SQLAlchemy base
render_er(Base, 'diagram.png')
