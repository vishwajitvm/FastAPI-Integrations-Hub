from flask import Flask
from config import Config
from blueprints.auth import auth_bp
from blueprints.folders import folders_bp

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config["SECRET_KEY"]

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(folders_bp)

if __name__ == '__main__':
    app.run(port=8000, debug=True)
