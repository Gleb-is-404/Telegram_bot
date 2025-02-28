from sqlalchemy import create_engine, MetaData, Table, create_engine, Column, Integer, String, inspect, BigInteger, DateTime, Float, JSON
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.types import PickleType
from sqlalchemy import or_
from sqlalchemy.dialects.postgresql import ARRAY
Engine = create_engine('postgresql://postgres:Pi2ruha_322@localhost/my_data_base')

Base = declarative_base()
class Users(Base):
	__tablename__ = 'users'
	id = Column(BigInteger, primary_key=True)
	First_Name = Column(String(50))
	Last_Name = Column(String(50))
	Username = Column(String(50))
	Age = Column(Integer)
	Language = Column(String(50))
	Country = Column(String(50))
	Readed_News=Column(JSON)
	def __repr__(self):
		return f"Id={id}, First Name={self.first_name}, Last Name={self.last_name}, Username={self.username}, Age={self.age}, Language={self.language} Coutry={self.country}, Ideology={self.ideology}"
class News_Base(Base):
	__tablename__ = 'news'
	id = Column(BigInteger, primary_key=True, autoincrement=True)
	Head_Line = Column(String(255))
	Sentences=Column(ARRAY(String(600)))
	Head_Line_Vector = Column(ARRAY(Float))
	Date_Time = Column(ARRAY(String(100)))
	Country = Column(String(100))
	Topic = Column(ARRAY(String(80)))
	def __repr__(self):
		return f"Id={id}, Headline={self.Head_Line}, Vector={0}, Data time={self.Date_Time}, Country={self.Country}, Topic={self.Topic}"
Base.metadata.create_all(Engine)