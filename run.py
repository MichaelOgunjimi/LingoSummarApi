from app import create_app
from dotenv import load_dotenv
import os

load_dotenv()

app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('FLASK_RUN_PORT', 5500))
    app.run(port=port)
    print(f'Running on http://localhost:{port}')