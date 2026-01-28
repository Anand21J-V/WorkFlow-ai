import os
from flask import Flask
from flask_cors import CORS
from routes import health_bp, ingest_bp, inspect_bp, query_bp, quiz_bp, memory_bp

def create_app():
    app = Flask(__name__)
    CORS(app)

    app.register_blueprint(health_bp)
    app.register_blueprint(ingest_bp)
    app.register_blueprint(inspect_bp)
    app.register_blueprint(query_bp)
    app.register_blueprint(quiz_bp)
    app.register_blueprint(memory_bp)

    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)