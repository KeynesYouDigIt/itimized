#! /usr/bin/env python

#switch on the app on, has funcs to reset the db

import logging
from tastr import *
from tastr.models import *
from flask_script import Manager, prompt_bool
from flask_migrate import Migrate, MigrateCommand
from sqlalchemy.exc import IntegrityError

mgmt = Manager(app)
migrate = Migrate(app, db)

mgmt.add_command('db', MigrateCommand)
# run python db_switch.py db migrate -m "message"
# and
# python db_switch.py db upgrade -m "message"
# to migrate the db base on changes made to models.py

@mgmt.command
def drop_db():
    if prompt_bool("Are you sure you would like to permanently"+
        " erase this data? You should do an upgrade of the db after this"):
        
        db.drop_all()
        print "dropped db"

if __name__ == '__main__':
    mgmt.run()