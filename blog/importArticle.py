#-*- coding:utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from blog.models import Article, create_db_tables

import sys

engine = create_engine('sqlite:///:blog:', echo = True)
create_db_tables(engine)
Session = sessionmaker(bind=engine)

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

session = Session()
session.add(article)
session.commit()
