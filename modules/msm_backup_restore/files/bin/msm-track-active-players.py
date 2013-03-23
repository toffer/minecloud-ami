#!/usr/bin/env python

import os
import re
import requests
import time

from datetime import datetime
from pygtail import Pygtail
from sqlalchemy import create_engine
from sqlalchemy import exc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
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

class Instance(Base):
    """"""
    __tablename__ = 'launcher_instance'
    __table_args__ = {'autoload':True}
 
class MCSession(Base):
    """"""
    __tablename__ = 'launcher_session'
    __table_args__ = {'autoload':True}

# Add foreign key relationships    
MCSession.user = relationship(User, primaryjoin=MCSession.user_id == User.id)
MCSession.instance = relationship(Instance, primaryjoin=MCSession.instance_id == Instance.id)
 
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

def login(session, player_name, login_time):
    user = session.query(User).\
                filter(User.username == player_name).\
                one()
    instance = session.query(Instance).\
                    filter(Instance.name == get_instance_id()).\
                    one()
    login_dt = datetime.strptime(login_time,'%Y-%m-%d %H:%M:%S')
    mc_session = MCSession(user_id=user.id,
                           instance_id=instance.id,
                           login=login_dt)
    session.add(mc_session)
    try:
        session.commit()
    except exc.IntegrityError:
        session.rollback()
    except:
        raise
    # Remove obj from session, so subsequent logouts in same DB session will
    # work. (Foreign key relations will be part of obj upon requerying DB.)
    if mc_session in session:
        session.expunge(mc_session)


def logout(session, player_name, logout_time):
    instance_name = get_instance_id()
    logout_dt = datetime.strptime(logout_time,'%Y-%m-%d %H:%M:%S')
    session.query(MCSession).\
        join(User).\
        join(Instance).\
        filter(MCSession.logout==None).\
        filter(User.username==player_name).\
        filter(Instance.name==instance_name).\
        update({'logout': logout_dt})
    session.commit()

def main():
    session = loadSession()

    # FIXME: Don't hardcode server name. Handle multiple worlds?
    LOG = '/opt/msm/servers/default/server.log'
    unread = Pygtail(LOG)

    # Regexes
    login_regex = re.compile('(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \[INFO\] (.+)\[/([0-9.]+):\d+\] logged in')
    logout_regex = re.compile('(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \[INFO\] (.+) lost connection: disconnect')

    for line in unread:
        login_match = login_regex.search(line)
        logout_match = logout_regex.search(line)
        if login_match:
            (date, player_name, ip) = login_match.groups()
            login(session, player_name, date)
        elif logout_match:
            (date, player_name) = logout_match.groups()
            logout(session, player_name, date)


if __name__ == "__main__":
    main()
