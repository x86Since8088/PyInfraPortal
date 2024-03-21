# pysiteapisfortornado/endpoints/auth_login.py
import tornado.web
import json
import jwt
import datetime
from .. import data

class api_auth_login(tornado.web.RequestHandler):
    async def post(self):
        username = self.get_body_argument("username", None)
        password = self.get_body_argument("password", None)
        redirect = self.get_body_argument("redirect", None)

        if username == PySiteConfig['AUTH_USERNAME'] and password == PySiteConfig['AUTH_PASSWORD']:
            payload = {
                "sub": username,
                "iat": datetime.datetime.utcnow(),
                "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=PySiteConfig['JWT']['TOKEN_EXPIRATION_SECONDS']),
            }
            token = jwt.encode(payload, PySiteConfig['JWT']['SECRET_KEY'], algorithm=PySiteConfig['JWT']['JWT_ALGORITHM'])
            self.set_secure_cookie(PySiteConfig['JWT']['COOKIE_NAME'], token, httponly=PySiteConfig['JWT']['COOKIE_HTTPONLY'])

            if redirect:
                self.redirect(redirect)  # Remember to validate or sanitize the redirect URL
            else:
                self.write("Authentication successful.")
        else:
            self.set_status(401)
            self.write("Invalid username or password")
