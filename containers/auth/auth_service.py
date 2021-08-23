#!/bin/python3
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
        try: self.client_id = os.environ['auth0_client_id']
        except: raise UnboundLocalError('auth0_client_id')

        try: self.client_secret = os.environ['auth0_client_secret']
        except: raise UnboundLocalError('auth0_client_secret')

        try: self.api_base_url = os.environ['auth0_api_base_url']
        except: raise UnboundLocalError('auth0_api_base_url')

        try: self.api_base_url = os.environ['auth0_access_token_url']
        except: raise UnboundLocalError('auth0_access_token_url')

        try: self.authorize_url = os.environ['auth0_authorize_url']
        except: raise UnboundLocalError('auth0_authorize_url')

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
        

