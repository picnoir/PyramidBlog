#-*- coding:utf-8 -*-

from models import User, dbSession


def groupFinder(username, request):
    """Find the groups associated to an
    user.
    """
    
    user = User.find_user(username)
    if user != False:
        return [user.group]
    else:
        return []

        
