#-*- coding:utf-8 -*-

import sys
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

from readers import MarkdownReader
from customExceptions import TooMuchMetaCarac

Base = declarative_base()
dbEngine = create_engine('sqlite:////home/flex/www/alternativebit/public_html/Blog/blog/blog/bdd.sqlite')
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
            self.categories = []
            session = dbSession()
            for categoryName in categories:
                try:
                    category = session.query(Category).\
                        filter(Category.name == categoryName).one()
                except NoResultFound:
                    category = Category(categoryName)
                self.categories.append(category)
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
            for categoryName in allCategoriesString[0].split(', '):
                try:
                    category = session.query(Category).\
                        filter(Category.name == categoryName).one()
                except:
                    category = Category(categoryName)
                self.categories.append(category)
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

    
    def __repr__(self):
        
        return "<Article(%s by '%s')>" % (self.title, self.author)
                                                                                      

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
                                                                                              
                                                                                              
                                                                                              
                                                                                              
                                                                                              
                                                                                              
