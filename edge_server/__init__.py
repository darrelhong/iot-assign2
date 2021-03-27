import os
from flask import Flask


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        DATABASE=os.path.join(app.instance_path, 'edge_db.sqlite'),
    )


    from edge_server.edge import edge
    app.register_blueprint(edge)

    from . import db
    db.init_app(app)

    return app