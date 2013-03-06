#!/usr/bin/env python

import os
import re
import requests
import sys

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Convert from Heroku style DATABASE_URL to Sqlalchemy style, if necessary 
db_url = os.environ.get('DATABASE_URL')
DATABASE_URL = re.sub('^postgres:', 'postgresql:', db_url)

engine = create_engine(DATABASE_URL, echo=False)
Base = declarative_base(engine)

class Instance(Base):
    """"""
    __tablename__ = 'launcher_instance'
    __table_args__ = {'autoload':True}
 
def loadSession():
    """"""
    metadata = Base.metadata
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

def get_instance_id():
    """Use EC2 metadata to get instance id."""
    response = requests.get('http://169.254.169.254/latest/meta-data/instance-id')
    return response.text

def update_instance_state(session, state):
    instance_name = get_instance_id()
    instance = session.query(Instance).\
                    filter(Instance.name == instance_name).\
                    one()
    instance.state = state
    session.add(instance)
    session.commit()

def main():
    if len(sys.argv[1:]) == 1 and sys.argv[1] in ['running', 'terminated']:
        state = sys.argv[1]
    else:
        print "Usage: %s [running|terminated]" % sys.argv[0]
        sys.exit(1)

    session = loadSession()
    update_instance_state(session, state)
    session.close()


if __name__ == "__main__":
    main()
