import os

from flask import Flask, render_template, request, flash, url_for, session
from flask_sqlalchemy import SQLAlchemy
# from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager
from passlib.hash import bcrypt

app = Flask(__name__)
app.config.from_mapping(
SECRET_KEY='devevelopmentsamplebullshitpassword',
SECURITY_PASSWORD_SALT='ninjinshirishiri',
# DATABASE=os.path.join(app.instance_path, 'stub.sqlite'),
SQLALCHEMY_DATABASE_URI="postgresql+psycopg2://team5:1qazxsw2@localhost/team5db",
JWT_TOKEN_LOCATION=["cookies", "headers"],
)

# jwt = JWTManager(app)
db = SQLAlchemy(app)

##### Database

class Product(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(), unique=True, nullable=False)
  price = db.Column(db.Integer, nullable=False)
  out_of_stock = db.Column(db.Boolean, nullable=False, default=False)
  kind = db.Column(db.String(), nullable=False) # this is enum in fact
  date = db.Column(db.Date) # null if kind == P

class Student(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  sid = db.Column(db.String(), nullable=False, unique=True)
  password_hash = db.Column(db.String(), nullable=False)
  expense = db.Column(db.Integer, nullable=False)

  def authenticate(self, pw):
    return bcrypt.verify(pw, self.password_hash)

##### Routes

@app.route("/")
def index():
  return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
  if request.method == "GET":
    return render_template("login.html")
  
  sid = request.form['sid']
  pw = request.form['password']
  error = None
  user = None

  if not sid:
    error = '学籍番号を入力してください'
  elif not pw:
    error = 'パスワードを入力してください'
  else:
    user = Student.query.filter_by(sid=sid).first()
    if not user or not user.authenticate(pw):
      error = "パスワードか学籍番号が間違っています。"
  
  if error is None:
    # access_token = create_access_token(identity=sid)
    session.clear()
    session['sid'] = sid
    flash('ログインしました。')
    return redirect(url_for('index'))

  flash(error)
  return render_template('login.html')

@app.route('/logout', methods=["POST"])
def logout():
  session.clear()
  flash('ログアウトしました。')
  return redirect('/')

@app.route('/register', methods=['GET', 'POST'])
def register():
  if request.method == 'GET':
    return render_template('register.html')
  
  sid = request.form['sid']
  pw = request.form['password']
  error = None

  if not sid:
    error = '学籍番号を入力してください'
  elif not pw:
    error = 'パスワードを入力してください'
  elif Student.query.filter_by(sid=sid).first() is not None:
    error = '登録済みです。<a href="/login">ログインはこちら</a>'
  
  if error is None:
    db.session.add(Student(sid=sid, password_hash=bcrypt.hash(pw)))
    db.session.commit()

    session.clear()
    session['sid'] = sid
    flash('登録に成功しました。')
    return redirect(url_for('/'))

  flash(error)
  # return render_template('register.html')
  return render_template('touroku.html')

# @app.route('')


# メニュー一覧
@app.route("/menu")
def menu():
  products = Product.query.all()
  return render_template("menu.html", products=products)


# メニューの個別ページ
@app.route("/menu/<id>")
def product(id):
  product = Product.query.get(id)
  return render_template("product.html", product=product)

# マイページ
@app.route("/profile")
# @jwt_required()
def profile():
  sid = get_jwt_identity()
  user = Student.query.filter_by(sid=sid).fetchone()
  
  if not Student:
    flash('ユーザーが見つかりません')
    return redirect('index')

  return render_template("mypage.html", user=user)
  # return render_template("profile.html", user=user)

# 出費を見られるページ
@app.route("/profile/expense")
# @jwt_required()
def expense():
  sid = get_jwt_identity()
  user = Student.query.filter_by(sid=sid).fetchone()

  if not Student:
    flash('ユーザーが見つかりません')
    return redirect('index')

  # return render_template("expense.html", user=user)
  return render_template("syokuhi.html", user=user)

##### API

# @app.route("/api/menu/update")

# @app.route("/api/profile/edit", )

@app.route("/api/dummy/get")
def get():
  return { data: 'hogehoge' }

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8085)