from flask import Flask, request, render_template_string, redirect, session, send_file
import sqlite3
import os
import subprocess

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
    # Vulnerability 1: SQL Injection
    # CodeQL may detect:
    # - Direct string concatenation to build SQL queries
    # - Lack of parameterized queries
    # - User input directly used in SQL queries
    # Possible false positives:
    # - Complex query building processes may be difficult to accurately track user input
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    user = cursor.fetchone()
    conn.close()
    return str(user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Vulnerability 2: Insecure Password Storage
        # CodeQL may detect:
        # - Hardcoded credentials
        # - Plaintext password comparison
        # Possible false positives:
        # - Hardcoded credentials in test code or example code
        if username == 'admin' and password == 'password123':
            session['logged_in'] = True
            return redirect('/admin')
    return render_template_string('<form method="post">Username: <input name="username"> Password: <input name="password" type="password"> <input type="submit"></form>')

@app.route('/admin')
def admin():
    # Vulnerability 3: Insecure Session Management
    # CodeQL may have difficulty detecting:
    # - Simple session state checks may not be viewed as vulnerabilities
    # - Lack of more complex session management mechanisms
    # Possible false positives:
    # - Legitimate simple session checks might be misjudged as insecure
    if not session.get('logged_in'):
        return redirect('/login')
    return "Welcome to the admin panel!"

@app.route('/download')
def download_file():
    filename = request.args.get('filename')
    # Vulnerability 4: Path Traversal
    # CodeQL may detect:
    # - Direct use of user input as file paths
    # - Lack of path normalization or validation
    # Possible false positives:
    # - Complex file operation logic may make it difficult to accurately track user input
    return send_file(filename)

@app.route('/run_command')
def run_command():
    command = request.args.get('command')
    # Vulnerability 5: Command Injection
    # CodeQL may detect:
    # - Direct passing of user input to shell execution
    # - Use of shell=True parameter
    # Possible false positives:
    # - Low, as this is an obvious security issue
    output = subprocess.check_output(command, shell=True)
    return output

@app.route('/render')
def render_template():
    template = request.args.get('template', '{{1+1}}')
    # Vulnerability 6: Server-Side Template Injection (SSTI)
    # CodeQL may detect:
    # - Direct rendering of user-provided template strings
    # - Use of unsafe template rendering functions
    # Possible false positives:
    # - Complex template rendering processes may be difficult to accurately track user input
    return render_template_string(template)

@app.errorhandler(404)
def page_not_found(e):
    # Vulnerability 7: Information Leakage in Error Handling
    # CodeQL may have difficulty detecting:
    # - Direct display of user input in error pages
    # - Lack of sanitization for error messages
    # Possible false positives:
    # - High, as error handling implementation may vary by application
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
    # Vulnerability 8: Debug Mode Enabled
    # CodeQL may detect:
    # - Enabling debug mode in the main execution environment
    # - Insecure server configuration
    # Possible false positives:
    # - Low to medium, depending on the context of the environment
    app.run(host='0.0.0.0', debug=True)