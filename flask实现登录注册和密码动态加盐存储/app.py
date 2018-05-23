from flask import Flask, request, render_template
import hmac, random
import pymysql


app = Flask(__name__)


# 使用hmac算法对用户的密码进行动态加盐摘要算法存储
def hmac_md5(key, s):
    return hmac.new(key.encode('utf-8'), s.encode('utf-8'), 'MD5').hexdigest()

class User:
    def __init__(self, username, password):
        self.username = username
        self.key = ''.join([chr(random.randint(48, 122)) for i in range(20)])
        self.password = hmac_md5(self.key, password)

# 连接数据库
def connect_db():
    conn = pymysql.connect(host='127.0.0.1', user='root', passwd='720428', db='mysql')
    cur = conn.cursor()
    return conn, cur

# 数据库表单检查
def table_check():
    conn, cur = connect_db()
    cur.execute('use users')
    cur.execute("select * from information_schema.tables where table_name='user_tb'")
    cur.fetchall()
    nrows = int(cur.rowcount)
    if nrows == 0:
        cur.execute('create table user_tb (id bigint(8) not null auto_increment , name varchar(20) , password varchar(100), password_key varchar(100), primary key(id))')
        conn.commit()
        cur.close()
        conn.close()

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route('/signin', methods=['GET'])
def signin_form():
    return render_template('signin.html')

@app.route('/signup', methods=['GET'])
def signup_form():
    return render_template('signup.html')

@app.route('/signin', methods=['POST'])
def signin():
    username = request.form['username']
    password = request.form['password']
    conn, cur = connect_db()
    cur.execute('use users')
    try:
        cur.execute('select * from user_tb where name=%s', [username, ])
        data = cur.fetchall()
        nrows = int(cur.rowcount)
        if nrows == 0:
            return render_template('signin.html', message='Wrong username')
        else:
            input_password = hmac_md5(data[0][3], password)
            if input_password == data[0][2]:
                return render_template('signin-ok.html', username=username)
            return render_template('signin.html', message='Wrong password')
    finally:
        cur.close()
        conn.close()

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    password = request.form['password']
    conn, cur = connect_db()
    cur.execute('use users')
    try:
        cur.execute('select * from user_tb where name=%s', [username,])
        data = cur.fetchall()
        nrows = int(cur.rowcount)
        if nrows == 0:
            new_user = User(username, password)
            cur.execute('insert into user_tb(name, password_key, password) values (%s, %s, %s)', [new_user.username, new_user.key, new_user.password])
            conn.commit()
            return render_template('signup-ok.html', message='You have created your account successfully!You can sign in now.', username=username)
        else:
            return render_template('signup.html', message='username {} has already exists')
    except Exception as e:
        return render_template('signup.html', message='Error!')
    finally:
        cur.close()
        conn.close()
    
    

if __name__ == '__main__':
    table_check()
    # 若不配置host和port，则默认是localhost,端口为5000
    # 若配置，如写作app.run('', 8000)，就是localhost，端口8000
    app.run('', 8080)