from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

path = "./web/"

agent = request.headers.get('User-Agent')
if ('iphone' or 'android' or 'blackberry') in agent.lower():
    path += 'mobile/'
else:
    path += 'desktop/'

@app.route('/')
def index():
    return render_template('./web/Homepage/index.html')


@app.route('/login')
def index():
    return render_template('./web/Login/index.html')


if __name__ == '__main__':
    app.run(debug=True)