from app import app
from app import hw_views

@app.route('/')
def home():
    return "Flask says 'Hello world!'"


