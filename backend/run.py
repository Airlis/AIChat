from app import create_app
import os
from dotenv import load_dotenv

load_dotenv()

config_name = os.getenv('FLASK_ENV', 'development')
app = create_app(f'config.{config_name.capitalize()}Config')


if __name__ == '__main__':
    app.run(debug=True)