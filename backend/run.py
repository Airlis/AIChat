from app import create_app
import os
from dotenv import load_dotenv
from app.extensions import db


load_dotenv()

config_name = os.getenv('FLASK_ENV', 'development')
app = create_app(f'config.{config_name.capitalize()}Config')

@app.cli.command("init-db")
def init_db():
    """Initialize the database."""
    db.create_all()
    print('Database initialized!')

if __name__ == '__main__':
    app.run(debug=True)