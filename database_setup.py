from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
 
Base = declarative_base()

class User(Base):
	__tablename__ = 'user'
	
	name = Column(String(80), nullable = False)
	id = Column(Integer, primary_key = True)
	email = Column(String(80), nullable = False)
	picture = Column(String, default="/static/blank_user.gif")
	
	@property
	def serialize(self):
		"""Return object data in easily serializeable format"""
		return {
			'name'         : self.name,
			'id'         : self.id,
			'email'         : self.email,
			'picture'         : self.picture,
			}

class Series(Base):
	__tablename__ = 'series'
	
	id = Column(Integer, primary_key=True)
	name = Column(String(250), nullable=False)
	manufacturer = Column(String(50))
	description = Column(String(500))
	user_id = Column(Integer,ForeignKey('user.id'))
	user = relationship(User)
	parts = relationship("Part", cascade="all, delete-orphan")
		
	@property
	def serialize(self):
		"""Return object data in easily serializeable format"""
		return {
			'name'         : self.name,
			'manufacturer' : self.manufacturer,
			'description'  : self.description,
			'id'           : self.id,
			'user'		   : self.user_id
			}
 
class Part(Base):
	__tablename__ = 'part'
	
	name = Column(String(80), nullable = False)
	id = Column(Integer, primary_key = True)
	footprint = Column(String(100))
	contactForm = Column(String(50))
	enclosure = Column(String(100))
	enhancement = Column(String(200))
	voltage = Column(String(100))
	series_id = Column(Integer,ForeignKey('series.id'))
	series = relationship(Series)
	user_id = Column(Integer,ForeignKey('user.id'))
	user  = relationship(User)
	
	@property
	def serialize(self):
		"""Return object data in easily serializeable format"""
		return {
			'name'         : self.name,
			'id'             : self.id,
			'footprint'      : self.footprint,
			'contactForm'    : self.contactForm,
			'enclosure'      : self.enclosure,
			'enhancement'    : self.enhancement,
			'voltage'        : self.voltage,
			'series'         : self.series_id,
			'user'           : self.user_id
			}

engine = create_engine('sqlite:///relayDatabase.db')
 

Base.metadata.create_all(engine)
