from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__, template_folder='templates')
CORS(app)
print(app.root_path)


#agent = request.headers.get('User-Agent')
#if ('iphone' or 'android' or 'blackberry') in agent.lower():
#    path += 'mobile/'
#else:
#    path += 'desktop/'

def gen_path():
        user_agent = request.headers.get("User-Agent", "").lower()
        phones = ["android", "iphone", "ipad", "blackberry"]
        for i in phones:
            if i in user_agent:
                path = "mobile/"
                return path
        else:
            path = "desktop/"
            return path


@app.route('/')
def landing():
    path = gen_path()
    path += "landing/index.html"
    return render_template(path)


@app.route('/login')
def login():
    path = "/common/login.html"
    return render_template(path)

@app.route('/register')
def register():
    path = "/common/register.html"
    return render_template(path)

@app.route('/staff/home')
def staff_home():
    path = gen_path()
    path += "staff_homepage/index.html"
    return render_template(path)

@app.route('/student/home')
def student_home():
    path = gen_path()
    path += "student_homepage/index.html"
    return render_template(path)

if __name__ == '__main__':
    app.run(debug=True)