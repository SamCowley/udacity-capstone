#!/bin/python3
import configparser
import authlib.integrations.flask_client as auth
import requests
import flask
import os

class Auth0:
    def __init__(self, app):
        self.app = app

        self.init_config()
        self.oauth = auth.OAuth(self.app)

        self.auth0 = self.oauth.register(
                'auth0',
                client_id        = self.client_id,
                client_secret    = self.client_secret,
                api_base_url     = self.api_base_url,
                access_token_url = self.access_token_url,
                authorize_url    = self.authorize_url,
                client_kwargs    = {
                    'scope': 'openid profile email',
                },
        )

    def init_config(self):
        missing_values = []

        # Get all configuration
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')

        # Add auth0 if it doesn't exist
        if 'auth0' not in self.config: self.config['auth0'] = {}

        # Retrieve all values
        self.client_id = self.config['auth0'].get('client_id')
        if self.client_id in [None, '']: missing_values.append('client_id')

        try:
            self.client_secret = os.environ['auth0_client_secret']
        except:
            self.client_secret = ''
            missing_values.append('auth0_client_secret')

        self.api_base_url = self.config['auth0'].get('api_base_url')
        if self.api_base_url in [None, '']:
            missing_values.append('api_base_url')

        self.access_token_url = self.config['auth0'].get('access_token_url')
        if self.access_token_url in [None, '']:
            missing_values.append('access_token_url')

        self.authorize_url = self.config['auth0'].get('authorize_url')
        if self.authorize_url in [None, '']:
            missing_values.append('authorize_url')

        # Add missing fields and raise an exception
        if len(missing_values) != 0:
            self.config['auth0']['client_id'] = str(self.client_id)
            self.config['auth0']['api_base_url'] = str(self.api_base_url)
            self.config['auth0']['access_token_url'] = str(self.access_token_url)
            self.config['auth0']['authorize_url'] = str(self.authorize_url)
            with open('config.ini', 'w') as configfile:
                self.config.write(configfile)
            raise UnboundLocalError('Missing values: ' + str(missing_values))


    def login(self):
        callback_url=flask.request.url_root + "api/v0/auth/callback"
        return self.auth0.authorize_redirect(redirect_uri=callback_url)

    def callback(self):
        self.auth0.authorize_access_token()
        resp = self.auth0.get('userinfo')
        userinfo = resp.json()

        return userinfo

    def token(self, username, password):
        resp = self.auth0.login(
            self.client_id,
            self.client_secret,
            username,
            password,
            'openid profile email',
            audience=self.api_base_url + "api/v2/",
            grant_type='password')
        return resp
        

