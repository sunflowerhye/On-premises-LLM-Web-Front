from flask import Flask
from flask_cors import CORS
from task1 import task1
from task2 import task2
from task3 import task3
from task4 import task4

app = Flask(__name__)
CORS(app)

# Blueprint 등록
app.register_blueprint(task1, url_prefix='/task1')
app.register_blueprint(task2, url_prefix='/task2')
app.register_blueprint(task3, url_prefix='/task3')
app.register_blueprint(task4, url_prefix='/task4')

if __name__ == '__main__':
    app.run(debug=True)
