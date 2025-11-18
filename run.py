from app import create_app
from dotenv import load_dotenv
import os
import sys

print("Loading environment variables...", file=sys.stderr, flush=True)
load_dotenv()

print("Creating Flask app...", file=sys.stderr, flush=True)
app = create_app()
print("✓ Flask app ready", file=sys.stderr, flush=True)

if __name__ == '__main__':
    port = int(os.getenv('FLASK_RUN_PORT', 5500))
    app.run(port=port)
    print(f'Running on http://localhost:{port}')