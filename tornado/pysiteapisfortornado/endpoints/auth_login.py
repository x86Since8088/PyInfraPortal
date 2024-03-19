# pysiteapisfortornado/endpoints/auth_login.py
import tornado.web
import json

class api_auth_login_handler(tornado.web.RequestHandler):
    def post(self):
        # Parse the JSON body of the request
        try:
            body = json.loads(self.request.body)
            username = body.get("username")
            password = body.get("password")

            # Simulate login validation
            if username == "admin" and password == "secret":
                self.write({"status": "success", "message": "Login successful"})
            else:
                self.write({"status": "error", "message": "Invalid username or password"})
        
        except json.JSONDecodeError:
            self.set_status(400) # Bad Request
            self.write({"status": "error", "message": "Invalid JSON format"})
