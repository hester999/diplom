from flask import Flask, send_from_directory
from routes import file_upload
import os
app = Flask(__name__, static_folder='../static', template_folder='../templates')


DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://admin:123@localhost:5432/vulnerable_db')



app.config['DATABASE_URL'] = DATABASE_URL
app.register_blueprint(file_upload)

app.secret_key = "supersecretkey"
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
