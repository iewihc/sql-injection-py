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
    # 漏洞1: SQL注入
    # CodeQL可能检测:
    # - 直接字符串拼接构建SQL查询
    # - 未使用参数化查询
    # - 用户输入直接用于SQL查询
    # 可能的误报:
    # - 如果查询构建过程复杂,可能难以准确追踪用户输入
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
        # 漏洞2: 不安全的密码存储
        # CodeQL可能检测:
        # - 硬编码的凭证
        # - 明文密码比较
        # 可能的误报:
        # - 测试代码或示例代码中的硬编码凭证
        if username == 'admin' and password == 'password123':
            session['logged_in'] = True
            return redirect('/admin')
    return render_template_string('<form method="post">Username: <input name="username"> Password: <input name="password" type="password"> <input type="submit"></form>')

@app.route('/admin')
def admin():
    # 漏洞3: 不安全的会话管理
    # CodeQL可能难以检测:
    # - 简单的会话状态检查可能不被视为漏洞
    # - 缺乏更复杂的会话管理机制
    # 可能的误报:
    # - 合法的简单会话检查可能被误判为不安全
    if not session.get('logged_in'):
        return redirect('/login')
    return "Welcome to the admin panel!"

@app.route('/download')
def download_file():
    filename = request.args.get('filename')
    # 漏洞4: 路径穿越
    # CodeQL可能检测:
    # - 直接使用用户输入作为文件路径
    # - 缺少路径规范化或验证
    # 可能的误报:
    # - 如果文件操作逻辑复杂,可能难以准确追踪用户输入
    return send_file(filename)

@app.route('/run_command')
def run_command():
    command = request.args.get('command')
    # 漏洞5: 命令注入
    # CodeQL可能检测:
    # - 直接将用户输入传递给shell执行
    # - 使用shell=True参数
    # 可能的误报:
    # - 低,因为这是一个明显的安全问题
    output = subprocess.check_output(command, shell=True)
    return output

@app.route('/render')
def render_template():
    template = request.args.get('template', '{{1+1}}')
    # 漏洞6: 服务器端模板注入 (SSTI)
    # CodeQL可能检测:
    # - 直接渲染用户提供的模板字符串
    # - 使用不安全的模板渲染函数
    # 可能的误报:
    # - 如果模板渲染过程复杂,可能难以准确追踪用户输入
    return render_template_string(template)

@app.errorhandler(404)
def page_not_found(e):
    # 漏洞7: 错误处理中的信息泄露
    # CodeQL可能难以检测:
    # - 在错误页面中直接显示用户输入
    # - 缺乏对错误消息的净化
    # 可能的误报:
    # - 高,因为错误处理的实现可能因应用而异
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
    # 漏洞8: 调试模式启用
    # CodeQL可能检测:
    # - 在主执行环境中启用调试模式
    # - 不安全的服务器配置
    # 可能的误报:
    # - 低到中等,取决于环境上下文
    app.run(host='0.0.0.0', debug=True)