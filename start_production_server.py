from waitress import serve
from app import app

serve(app, port=5000)
