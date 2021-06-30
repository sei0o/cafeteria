import os

from flask import Flask, render_template, request, flash, url_for, session, redirect
from flask_sqlalchemy import SQLAlchemy
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
  expense = db.Column(db.Integer, nullable=False, default=0)

  def authenticate(self, pw):
    return bcrypt.verify(pw, self.password_hash)

#### Helpers

def current_user():
  if session['sid']:
    return Student.query.filter_by(sid=session['sid']).first()
  return None

##### Routes

# メニュー一覧
@app.route("/")
def index():
  products = Product.query.all()
  return render_template("index.html", products=products)

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
  return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
  if request.method == 'GET':
    # return render_template('register.html')
    return render_template('touroku.html')
  
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
    db.session.add(Student(sid=sid, password_hash=bcrypt.hash(pw), expense=0))
    db.session.commit()

    session.clear()
    session['sid'] = sid
    flash('登録に成功しました。')
    return redirect(url_for('index'))

  flash(error)
  # return render_template('register.html')
  return render_template('touroku.html')

# メニューの個別ページ
@app.route("/menu/<id>")
def product(id):
  product = Product.query.get(id)
  return render_template("menu.html", product=product)

# 「食べた」処理
@app.route("/menu/<id>/tabeta", methods=["POST"])
def tabeta(id):
  product = Product.query.get(id)
  student = current_user()

  expense_total = expense_total + product.price
  student.expense = expense_total

  db.session.add(student)
  db.session.commit()

  return redirect("/menu/" + id)

@app.route("/menu/<id>/out_of_stock", methods=["POST"])
def out_of_stock(id):
  product = Product.query.get(id)
  
  if request.form['out_of_stock'] == 1:
    #売り切れ
    product.out_of_stock = True                        
  else:
    #在庫あり
    product.out_of_stock = False
                  
  db.session.add(product)
  db.session.commit()
                  
  return redirect("/menu/" + id)

# マイページ
@app.route("/profile")
def profile():
  user = current_user()
  
  if not user:
    flash('ユーザーが見つかりません')
    return redirect('index')

  return render_template("mypage.html", user=user)
  # return render_template("profile.html", user=user)

# 出費を見られるページ
@app.route("/profile/expense")
def expense():
  user = current_user()

  if not user:
    flash('ユーザーが見つかりません')
    return redirect('index')

  # return render_template("expense.html", user=user)
  return render_template("syokuhi.html", student=student)

##### API

@app.route("/api/dummy/get")
def get():
  return { data: 'hogehoge' }

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8085)
