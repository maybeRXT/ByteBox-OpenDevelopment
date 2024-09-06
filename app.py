from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# File paths
ACCOUNTS_FILE = 'accounts.txt'
POSTS_FILE = 'posts.txt'

# Helper functions
def read_accounts():
    accounts = []
    if os.path.exists(ACCOUNTS_FILE):
        with open(ACCOUNTS_FILE, 'r') as file:
            for line in file:
                username, password, bytes = line.strip().split(',')
                if username == "Founder":
                    bytes = "Founder"
                accounts.append({'username': username, 'password': password, 'bytes': bytes if bytes == "Founder" else int(bytes)})
    return accounts

def write_accounts(accounts):
    with open(ACCOUNTS_FILE, 'w') as file:
        for account in accounts:
            file.write(f"{account['username']},{account['password']},{account['bytes']}\n")

def read_posts():
    posts = []
    if os.path.exists(POSTS_FILE):
        with open(POSTS_FILE, 'r') as file:
            for line in file:
                username, bytes, title, content, hearts, comments = line.strip().split('|')
                comments = comments.split(';') if comments else []
                posts.append({'username': username, 'bytes': int(bytes), 'title': title, 'content': content, 'hearts': int(hearts), 'comments': comments})
    return posts

def write_posts(posts):
    with open(POSTS_FILE, 'w') as file:
        for post in posts:
            comments = ';'.join(post['comments'])
            file.write(f"{post['username']}|{post['bytes']}|{post['title']}|{post['content']}|{post['hearts']}|{comments}\n")

@app.route('/')
def home():
    session.clear()
    return redirect(url_for('signin'))

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        accounts = read_accounts()
        for account in accounts:
            if account['username'] == username and account['password'] == password:
                session['username'] = username
                session['bytes'] = account['bytes']
                return redirect(url_for('index'))
        return 'Invalid username or password'
    return render_template('signin.html')

@app.route('/createaccount', methods=['GET', 'POST'])
def createaccount():
    if request.method == ['POST']:
        username = request.form['username']
        password = request.form['password']
        accounts = read_accounts()
        accounts.append({'username': username, 'password': password, 'bytes': 0})
        write_accounts(accounts)
        return redirect(url_for('signin'))
    return render_template('createaccount.html')

@app.route('/index')
def index():
    if 'username' not in session:
        return redirect(url_for('signin'))
    posts = read_posts()
    posts.sort(key=lambda x: x['hearts'], reverse=True)  # Sort posts by hearts
    return render_template('index.html', posts=posts, username=session['username'], bytes=session['bytes'])

@app.route('/post', methods=['POST'])
def post():
    if 'username' not in session:
        return redirect(url_for('signin'))
    title = request.form['title']
    content = request.form['content']
    posts = read_posts()
    user_bytes = session['bytes'] if session['bytes'] == "Founder" else int(session['bytes'])
    posts.append({'username': session['username'], 'bytes': user_bytes + 5, 'title': title, 'content': content, 'hearts': 0, 'comments': []})
    session['bytes'] = user_bytes + 5 if session['bytes'] != "Founder" else "Founder"
    write_posts(posts)
    update_account_bytes(session['username'], 5)
    return redirect(url_for('index'))

@app.route('/comment/<int:post_index>', methods=['POST'])
def comment(post_index):
    if 'username' not in session:
        return redirect(url_for('signin'))
    comment_content = request.form['comment']
    posts = read_posts()
    posts[post_index]['comments'].append(f"{session['username']}: {comment_content}")
    posts[post_index]['bytes'] += 1
    write_posts(posts)
    update_account_bytes(posts[post_index]['username'], 1)
    return redirect(url_for('index'))

@app.route('/heart/<int:post_index>', methods=['POST'])
def heart(post_index):
    if 'username' not in session:
        return redirect(url_for('signin'))
    posts = read_posts()
    posts[post_index]['hearts'] += 1
    posts[post_index]['bytes'] += 10
    write_posts(posts)
    update_account_bytes(posts[post_index]['username'], 10)
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('signin'))

@app.route('/check_account')
def check_account():
    if 'username' in session:
        accounts = read_accounts()
        for account in accounts:
            if account['username'] == session['username']:
                return jsonify(bytes=account['bytes'])
    return jsonify(bytes=0)

def update_account_bytes(username, bytes):
    accounts = read_accounts()
    for account in accounts:
        if account['username'] == username:
            if account['bytes'] != "Founder":
                account['bytes'] += bytes
            break
    write_accounts(accounts)

if __name__ == '__main__':
    app.run(debug=True)
