#!/usr/bin/env python

import os
import re
import requests
import sys

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

# Convert from Heroku style DATABASE_URL to Sqlalchemy style, if necessary 
db_url = os.environ.get('DATABASE_URL')
DATABASE_URL = re.sub('^postgres:', 'postgresql:', db_url)

engine = create_engine(DATABASE_URL, poolclass=NullPool)
Base = declarative_base(engine)

class User(Base):
    """"""
    __tablename__ = 'auth_user'
    __table_args__ = {'autoload':True}
 
def loadSession():
    """"""
    metadata = Base.metadata
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

def get_players(session):
    """Return list of player names for whitelist.txt"""
    query = (session.query(User.username)
                .filter(User.is_active == True)
                .order_by(User.username)
	        )
    return [player[0].encode('utf-8') for player in query]

def get_ops(session):
    """Return list of player names for ops.txt."""
    query = (session.query(User.username)
                .filter(User.is_staff == True)
                .filter(User.is_active == True)
        		.order_by(User.username)
	        )
    return [ops[0].encode('utf-8') for ops in query]

def write_names(names, filename):
    """Write list of names to filename."""
    with open(filename, 'w') as f:
        for name in names:
            f.write("%s\n" % name)
   
def main():
    if len(sys.argv) != 1:
        print "Usage: %s" % sys.argv[0]
        sys.exit(1)

    session = loadSession()

    whitelist_file = '/opt/msm/servers/default/white-list.txt'
    ops_file = '/opt/msm/servers/default/ops.txt'

    write_names(get_players(session), whitelist_file)
    write_names(get_ops(session), ops_file)

    session.close()


if __name__ == "__main__":
    main()
