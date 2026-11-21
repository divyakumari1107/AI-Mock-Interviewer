import os
import sys

# Ensure project root is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))

if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from app import app


# WSGI middleware to accurately resolve Vercel serverless request path
class VercelPathFixer:
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        matched = environ.get("HTTP_X_MATCHED_PATH")
        if matched:
            environ["PATH_INFO"] = matched.split("?")[0]
        else:
            path = environ.get("PATH_INFO", "")
            for prefix in ["/api/index.py", "/api/index"]:
                if path == prefix:
                    environ["PATH_INFO"] = "/"
                    break
                elif path.startswith(prefix + "/"):
                    environ["PATH_INFO"] = path[len(prefix):]
                    break
        return self.wsgi_app(environ, start_response)


app.wsgi_app = VercelPathFixer(app.wsgi_app)

# Vercel entrypoints
handler = app
application = app
