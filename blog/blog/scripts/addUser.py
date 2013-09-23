#-*- coding:utf-8 -*-

from blog.models import (User,
                         dbSession,
                         dbEngine,
                         create_db_tables)

create_db_tables(dbEngine)
username = str( raw_input( 'Username? '))
password = str( raw_input( 'Password? '))
group = str( raw_input( 'Group (user, admin) ? '))

user = User(username, password, group)
session = dbSession()
session.add(user)
session.commit()
session.close()
