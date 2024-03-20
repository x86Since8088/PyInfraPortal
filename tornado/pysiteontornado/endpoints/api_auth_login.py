# pysiteapisfortornado/endpoints/auth_login.py
import tornado.web
import json
import jwt
import datetime
from .. import config

class api_auth_login(tornado.web.RequestHandler):
    async def post(self):
        username = self.get_body_argument("username", None)
        password = self.get_body_argument("password", None)
        redirect = self.get_body_argument("redirect", None)

        if username == config['AUTH_USERNAME'] and password == config['AUTH_PASSWORD']:
            payload = {
                "sub": username,
                "iat": datetime.datetime.utcnow(),
                "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=config['JWT']['TOKEN_EXPIRATION_SECONDS']),
            }
            token = jwt.encode(payload, config['JWT']['SECRET_KEY'], algorithm=config['JWT']['JWT_ALGORITHM'])
            self.set_secure_cookie(config['JWT']['COOKIE_NAME'], token, httponly=config['JWT']['COOKIE_HTTPONLY'])

            if redirect:
                self.redirect(redirect)  # Remember to validate or sanitize the redirect URL
            else:
                self.write("Authentication successful.")
        else:
            self.set_status(401)
            self.write("Invalid username or password")
