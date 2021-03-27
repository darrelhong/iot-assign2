import os
from flask import Flask


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        DATABASE=os.path.join(app.instance_path, 'cloud_db.sqlite'),
    )


    from cloud_server.cloud import cloud
    app.register_blueprint(cloud)

    from . import db
    db.init_app(app)

    return app