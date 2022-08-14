import hashlib
import math
from webapp import app, login
import utils
from flask import request, render_template, url_for, session, jsonify
from webapp.admin import *
from flask_login import login_user, login_required, current_user
import cloudinary.uploader


@login.user_loader
def load_user(user_id):
    return utils.get_user_by_id(user_id=user_id)


@app.route('/admin-login', methods=['POST'])
def admin_login():
    username = request.form.get('username')
    password = request.form.get('psw')

    user = utils.check_login(username=username, password=password, role=Role.Administrator)
    if user:
        login_user(user=user)

    return redirect('/admin')


@app.route("/")
def home():
    kw = request.args.get('keyword')
    type = utils.load_TheLoai()
    type_id = request.args.get('theloai_id')
    tl = utils.get_id_theloai(type_id=type_id)
    books = utils.load_Sach(type_id=type_id, kw=kw)

    return render_template('index.html', theloai=type, sach=books, tl=tl, type_id=type_id)


@app.route("/<int:sach_id>")
def detail(sach_id):
    sach = utils.get_id_sach(sach_id)
    theloai = utils.load_TheLoai()
    tl = utils.get_id_theloai(sach_id)
    counter = utils.count_comments(sach_id=sach_id)

    return render_template('chitietsach.html', sach=sach, theloai=theloai, tl=tl,
                           pages=math.ceil(counter/app.config['COMMENT_SIZE']))


@app.route("/customer-login", methods=["GET", "POST"])
def login_kh():
    err_msg = ''
    if request.method == "POST":
        username = request.form.get('username')
        psw = request.form.get('psw')

        kh = utils.check_login(username=username, password=psw)
        if kh:
            login_user(user=kh)
            if 'sach_id' in request.args:
                return redirect(url_for(request.args.get('next', 'home'), sach_id=request.args['sach_id']))
            return redirect(url_for(request.args.get('next', 'home')))
        else:
            err_msg = "Username hoặc Password không đúng!!!"

    return render_template("login.html", err_msg=err_msg)


@app.route("/customer-signup", methods=["GET", "POST"])
def signup_kh():
    err_msg = ''
    if request.method == "POST":
        name = request.form.get("name")
        username = request.form.get("user")
        img = request.files.get("avatar")
        email = request.form.get("email")
        telephone = request.form.get("telephone")
        address = request.form.get("address")
        psw = request.form.get("psw")
        psw_repeat = request.form.get("psw-repeat")
        avatar_path = None

        sdt_exists = User.query.filter_by(sodienthoai=telephone).first()
        username_exists = User.query.filter_by(username=username).first()
        email_exists = User.query.filter_by(email=email).first()

        if sdt_exists:
            err_msg = 'Số điện thoại đã tồn tại!'
        elif username_exists:
            err_msg = 'Tên đăng đã tồn tại!'
        elif psw != psw_repeat:
            err_msg = 'Mật khẩu không khớp!'
        elif len(psw) < 4:
            err_msg = 'Mật khẩu quá ngắn'
        elif email_exists:
            err_msg = 'Email đã tồn tại!'
        else:
            if img:
                res = cloudinary.uploader.upload(img)
                avatar_path = res['secure_url']

            new_user = User(ten=name, username=username, hinhanh=avatar_path, sodienthoai=telephone, email=email,
                                diachi=address, password=str(hashlib.md5(psw.strip().encode('utf8')).hexdigest()))

            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login_kh'))

    return render_template("signin.html", err_msg=err_msg)


@app.route('/customer-logout')
def kh_logout():
    logout_user()
    return redirect(url_for('home'))


@login.user_loader
def user_load(user_id):
    return utils.get_user_by_id(user_id=user_id)


@app.route('/api/comments', methods=['post'])
@login_required
def add_comment():
    data = request.json
    if data.get('content'):
        content = data.get('content')
        sach_id = data.get('sach_id')
        try:
            c = utils.add_comment(content=content, sach_id=sach_id)
        except:
            return {'status': 404, 'err_msg': 'Website bị lỗi !!'}

        return {'status': 201, 'comment': {
            'id': c.id,
            'content': c.content,
            'created_date': str(c.created_date),
            'user': {
                'id': c.user.id,
                'username': c.user.username,
                'hinhanh': c.user.hinhanh
            }
        }}
    else:
        return {'status': 404, 'err_msg': 'Nhập comment!!!!'}


@app.route('/api/sach/<int:sach_id>/comments')
def get_comments(sach_id):
    page = request.args.get('page', 1)
    comments = utils.get_comments(sach_id=sach_id, page=int(page))

    results = []
    for c in comments:
        results.append({
            'id': c.id,
            'content': c.content,
            'created_date': str(c.created_date),
            'user': {
                'id': c.user.id,
                'username': c.user.username,
                'hinhanh': c.user.hinhanh
            }
        })

    return jsonify(results)


@app.route('/api/add-cart', methods=['post'])
@login_required
def add_to_cart():
    data = request.json
    id = str(data.get('id'))
    name = data.get('name')
    price = data.get('price')

    cart = session.get('cart')
    if not cart:
        cart = {}

    if id in cart:
        cart[id]['quantity'] = cart[id]['quantity'] + 1
    else:
        cart[id] = {
            'id': id,
            'name': name,
            'price': price,
            'quantity': 1
        }

    session['cart'] = cart

    return jsonify(utils.count_cart(cart))


@app.route('/cart')
@login_required
def cart():
    theloai = utils.load_TheLoai()
    return render_template('cart.html', stats=utils.count_cart(session.get('cart')), theloai=theloai)


@app.route('/api/update-cart', methods=['put'])
def update_cart():
    data = request.json
    id = str(data.get('id'))
    quantity = data.get('quantity')

    cart = session.get('cart')
    if cart and id in cart:
        cart[id]['quantity'] = quantity
        session['cart'] = cart

    return jsonify(utils.count_cart(cart))


@app.route('/api/delete-cart/<sach_id>', methods=['delete'])
def delete_cart(sach_id):
    cart = session.get('cart')

    if cart and sach_id in cart:
        del cart[sach_id]
        session['cart'] = cart

    return jsonify(utils.count_cart(cart))


@app.context_processor
def common_response():
    return {
        'cart_stats': utils.count_cart(session.get('cart'))
    }


@app.route('/api/pay', methods=['post'])
@login_required
def pay():
    try:
        utils.add_receipt(session.get('cart'))
        del session['cart']
    except:
        return jsonify({'code': 400})

    return jsonify({'code': 200})


@app.route('/api/order', methods=['post'])
@login_required
def order():
    try:
        utils.add_order(session.get('cart'))
        del session['cart']
    except:
        return jsonify({'code': 400})

    return jsonify({'code': 200})


if __name__ == '__main__':
    db.create_all()

    app.run(debug=True)
