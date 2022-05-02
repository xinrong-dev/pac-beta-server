[![Build Status](https://img.shields.io/circleci/build/bb/metalgear121/pac-client?token=3dee960889ae341ab0a6b5a333b481d1f0426866)](https://circleci.com/bb/metalgear121/pac-server)
[![Python Version](https://img.shields.io/badge/Python-v3.7.5-blue)](https://www.python.org)
[![Django Version](https://img.shields.io/badge/Django-v3.1.2-blue)](https://www.djangoproject.com)

# Platform for Artist's Collaboration
A web service for artists working in several fields

## Overview

- Art works collaboration and sharing
- Chat between artists
- Following between users
- Multimedia and tags for art works
- SimpleUI for django admin
- Firebase OAuth2

## Getting Started

First clone the repository from Github and switch to the new directory:

    $ git clone git@github.com/xinrong-dev/pac-beta-server.git
    $ cd pac
    
Activate the virtualenv for your project.
    
Install project dependencies:

    $ pip install -r requirements/local.txt
    
    
Then simply apply the migrations:

    $ python manage.py migrate
    

You can now run the development server:

    $ python manage.py runserver