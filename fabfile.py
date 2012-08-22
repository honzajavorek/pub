# -*- coding: utf-8 -*-


from fabric.api import *


def deploy():
    local('git push origin master')
    local('git push heroku master')


def run():
    local('heroku run --app polar-brushlands-3976 python pub.py')
