import os

DB_URL = 'sqlite:///' + os.path.abspath("db.db")
X_RAPID_API_KEY = os.environ.get('X_RAPID_API_KEY')

