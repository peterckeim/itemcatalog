from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Series, Part, User

engine = create_engine('sqlite:///relayDatabase.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Create dummy users
User1 = User(name="Ethan Bradberry", email="e.bradberry@notadomain.com")
session.add(User1)
session.commit()

User2 = User(name="Rob Onofrey", email="roff@notadomaineither.com", picture="https://media.licdn.com/media/p/1/000/095/019/227b5f8.jpg")
session.add(User2)
session.commit()

# Part List for 896 Series Relays
partSeries1 = Series(user_id=1, name="896", manufacturer="Song Chuan", description="Automotive Mini ISO relays available with PCB or Quick Connect terminals")
session.add(partSeries1)
session.commit()

partNumber = Part(user_id=1, name="896H-1AH-C-R1-U03-12VDC", footprint="Mini ISO High Powered", enclosure="Dust Cover (Flux Tight - IP65)", contactForm="single pole normally open",
					enhancement="resistor, high-temp wire around coil, bigger contacts, more robust", voltage="12 Volts DC",  series=partSeries1)
session.add(partNumber)
session.commit()

partNumber = Part(user_id=1, name="896-1CH-C1-12VDC", footprint="Mini ISO", enclosure="Flanged Cover (Flux Tight - IP65)", contactForm="single pole double throw",
					enhancement="none", voltage="12 Volts DC",  series=partSeries1)
session.add(partNumber)
session.commit()

partNumber = Part(user_id=1, name="896H-1CH-C1S-12VDC", footprint="Mini ISO High Powered", enclosure="Steel Bracket (Flux Tight - IP65)", contactForm="single pole double throw",
					enhancement="none", voltage="12 Volts DC",  series=partSeries1)
session.add(partNumber)
session.commit()

partNumber = Part(user_id=1, name="896H-1AH-D1-R1-12VDC", footprint="Mini ISO High Powered", enclosure="Flanged Cover (Unsealed)", contactForm="single pole normally open",
					enhancement="680Ohm Resistor parallel to coil", voltage="12 Volts DC",  series=partSeries1)
session.add(partNumber)
session.commit()

# Part List for G8V Series Relays
partSeries2 = Series(user_id=2, name="G8V", manufacturer="OMRON", description="Automotive Micro 280 relay with reduced outer length and width")
session.add(partSeries2)
session.commit()

partNumber = Part(user_id=2, name="G8V1A7TRDC12", footprint="Micro 280", enclosure="Dust Cover (Unsealed)", contactForm="single pole normally open",
					enhancement="resistor", voltage="12 Volts DC",  series=partSeries2)
session.add(partNumber)
session.commit()


