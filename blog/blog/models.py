#-*- coding:utf-8 -*-

import sys
import hashlib
from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (Column,
                        DateTime,
                        String,
                        Integer,
                        Table,
                        ForeignKey,
                        create_engine)
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from pyramid.security import (Everyone,
                              Allow,
                              Authenticated)

from readers import MarkdownReader
from customExceptions import TooMuchMetaCarac

Base = declarative_base()
dbEngine = create_engine('sqlite:///:blog:')
#dbEngine = create_engine('sqlite:////home/flex/www/alternativebit/public_html/Blog/blog/blog/bdd.sqlite')
dbSession = sessionmaker(bind=dbEngine)


"Association tables"
category_article = \
  Table('articleCategory', Base.metadata,
        Column('category_id', Integer, ForeignKey('category.id')),
        Column('article_id', Integer, ForeignKey('articles.id'))
      )

def create_db_tables(engine):
    Base.metadata.create_all(engine)
    
class Article(Base):
    """Article container
    This class represents an article object wich contains various
    informations about an blog article such as author, date, content,
    etc... Base is a declarative sqlachemy's base. This must be declared
    in the main file of the application."""
    
    __tablename__ = 'articles'
    id = Column(Integer, primary_key = True)
    title = Column(String)
    date = Column(DateTime)
    author = Column(String)
    content = Column(String)
    categories = relationship('Category',\
        secondary=category_article,\
        backref='articles')
                                  
    def __init__(self, mdFilePath, title=None, date=None,  author=None,\
                 content=None, categories=None):
        """Create Article from attributes or a markdown File.
        
        Categories must be a tuple. Content must be in HTML format.
        If you want to set an article without mdFile,
        you must set the first parameter
        to None"""
        
        if (title and date and author and content and categories):
            self.title=title
            self.date=date
            self.author=author
            self.content=content
            session = dbSession()
            self.set_categories_by_name(session,categories)
            session.close()
        else:
            md=MarkdownReader()
            self.content, meta=md.read(mdFilePath)
            try:
                self._process_meta(meta)
            except TooMuchMetaCarac, e:
                print e
                                                      
                                                      
    def _process_meta(self, meta):
        """Analyse and process meta caracteristics dictionnary """

        try:
            allCategoriesString=meta['categories']
            session = dbSession()
            self.set_categories_by_name(session,
                                        allCategoriesString[0].\
                                        split(' ,'))
            session.close()
        except KeyError:
            self.categories=[]
        try:
            author=meta['author']
            self.author=author[0]
        except KeyError:
            print("No author specified in the markdown file.")
            sys.exit(-1)
        try:
            date=meta['date']
            self.date=date[0]
        except KeyError:
            print("No date specified in the markdown file.\
            Choosing today's date for this article.")
            self.date = datetime.now()
        if self.date==None:
            print "Exiting"
            sys.exit(-1)
        try:
            title=meta['title']
            self.title=title[0]
        except KeyError:
            print("No title specified in the markdown file,\
            exiting.")
            sys.exit(-1)

            
    def set_categories_by_name(self, session, categoriesNameList):
        """Set a list of categories to an article"""

        self.categories = []
        for categoryName in categoriesNameList:
            try:
                category = session.query(Category).\
                    filter(Category.name == categoryName).one()
            except:
                category = Category(categoryName)
            self.categories.append(category)

    
    def __repr__(self):
        
        return "<Article (%s by '%s')>" % (self.title, self.author)
                                                                                      

class Category(Base):
    """Category class
    
    This class represents a cathegory. Categorys must be
    created manually in the database before adding an article.
    """
    
    __tablename__ = 'category'
    id = Column(Integer, primary_key = True)
    name = Column(String, nullable = False, unique = True)
                                                                                          
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Category %s>" % (self.name)
                                                                                              

class User(Base):
    """User class

    This class represents a user. Users are stored in the
    same database than articles and projects.
    """

    __tablename__ = 'users'
    id = Column(Integer, primary_key = True)
    name = Column(String, nullable = False, unique = True)
    password = Column(String, nullable = False)
    group = Column(String)

    def __init__(self, name, password, group):
        self.name = name
        self.password = hashlib.sha512(password).hexdigest()
        self.group = group

    def __repr__(self):
        return "<User %s>" % (self.name)

    @classmethod
    def check_user_password(cls, name, password):
        """Predicate that check if the password of an user
        is correct.
        """

        session = dbSession()
        try:
            user = session.query(User).\
                filter(User.name == name).one()
        except NoResultFound:
            return False
        session.close()
        return (user.password == hashlib.sha512(password).hexdigest())

    @classmethod
    def find_user(cls, username):
        """Find a user in the database.

        Returns false if the user don't exists, else the user
        object
        """
          
        session = dbSession()
        try:
            user = session.query(User).\
                filter(User.name == username).one()
        except NoResultFound:
            return False
        session.close()
        return user

            
class Project(Base):
    """Project class

    This class represents a project.
    """

    __tablename__ = "projects"
    id = Column(Integer, primary_key = True)
    title = Column(String, nullable = False)
    content = Column(String)
    author = Column(String)

    def __init__(self, title, content, author):
        self.title = title
        self.content = content
        self.author = author

    def __repr__(self):
        return "<Project %s>" % (self.title)

class RootFactory(object):
    __acl__ = [
        (Allow, Everyone, 'view'),
        (Allow, Authenticated, 'admin')
    ]

    def __init__(self, request):
        pass # pragma: no cover
