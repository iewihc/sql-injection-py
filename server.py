from flask import Flask, request, render_template_string
import sqlite3

app = Flask(__name__)

app.config['SECRET_KEY'] = "flag{SSTI_123456}"

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/users')
def get_user():
    username = request.args.get('username')
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # 不安全的查询 - SQL 注入漏洞
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    user = cursor.fetchone()
    conn.close()
    return str(user)

@app.errorhandler(404)
def page_not_found(e):
    template = '''
{%% block body %%}
    <div class="center-content error">
        <h1>Oops! That page doesn't exist.</h1>
        <h3>%s</h3>
    </div> 
{%% endblock %%}
''' % (request.args.get('404_url'))
    return render_template_string(template), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)