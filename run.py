import os
from app import create_app
from flask_migrate import Migrate
from app import db


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)
if __name__ == '__main__':
    app.run()