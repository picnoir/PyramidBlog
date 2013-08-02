#-*- coding:utf-8 -*-
from sqlalchemy import create_engine

from blog.models import (Article,
                         create_db_tables,
                         dbSession,
                         dbEngine)

import sys

create_db_tables(dbEngine)

try:
    fileName = sys.argv[1]
except IndexError:
    sys.stderr.write('Merci de spécifier un nom de fichier.')
    sys.exit(-1)
try:
    article = Article(fileName)
except IOError:
    sys.stderr.write('Nom de fichier incorrect.')
    sys.exit(-1)

session = dbSession()
session.close_all()
session.add(article)
session.commit()
