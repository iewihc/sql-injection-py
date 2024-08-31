import sqlite3

def get_user(username):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # 不安全的查询 - 存在SQL注入漏洞
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    
    user = cursor.fetchone()
    conn.close()
    return user

# 使用示例
user_input = input("Enter username: ")
result = get_user(user_input)
print(result)