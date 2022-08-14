from webapp import app
from webapp.models import *
import hashlib
from sqlalchemy import func
from flask_login import current_user


def get_id_sach(sach_id):
    return Sach.query.get(sach_id)


def get_id_theloai(type_id):
    theloai = TheLoai.query.filter(TheLoai.id.__eq__(type_id))

    return theloai.all()


def get_user_by_id(user_id):
    return User.query.get(user_id)


def get_user_by_role(user_role):
    return User.query.get(user_role)


def load_TheLoai():
    return TheLoai.query.all()


def load_Sach(type_id=None, kw=None):
    sach = Sach.query.filter(Sach.active.__eq__(True))

    if type_id:
        sach = sach.filter(Sach.idtheloai.__eq__(type_id))

    if kw:
        sach = sach.filter(Sach.tensach.contains(kw))

    return sach.all()


def check_login(username, password, role=Role.Customer):
    if username and password:
        password = str(hashlib.md5(password.strip().encode('utf8')).hexdigest())

        return User.query.filter(User.username.__eq__(username.strip()), User.password.__eq__(password),
                                 User.role.__eq__(role)).first()


def add_comment(content, sach_id):
    c = Comment(content=content, sach_id=sach_id, user_id=current_user.id)

    db.session.add(c)
    db.session.commit()

    return c


def get_comments(sach_id, page=1):
    page_size = app.config['COMMENT_SIZE']
    start = (page - 1) * page_size

    return Comment.query.filter(Comment.sach_id.__eq__(sach_id))\
        .order_by(-Comment.id).slice(start, start + page_size).all()


def count_comments(sach_id):
    return Comment.query.filter(Comment.sach_id.__eq__(sach_id)).count()


def count_cart(cart):
    total_quantity, total_amount = 0, 0

    if cart:
        for c in cart.values():
            total_quantity += c['quantity']
            total_amount += c['price'] * c['quantity']

    return {
        'total_quantity': total_quantity,
        'total_amount': total_amount
    }


def add_receipt(cart):
    if cart:
        hoadon = HoaDon(user=current_user)
        db.session.add(hoadon)

        for c in cart.values():
            d = ChiTietHoaDon(id_sach=c['id'],
                              hoadon=hoadon,
                              soluong=c['quantity'],
                              dongia=c['price'])
            db.session.add(d)

        db.session.commit()


def add_order(cart):
    if cart:
        dathang = DatHang(user=current_user)
        db.session.add(dathang)

        for c in cart.values():
            d = ChiTietDatHang(dathang=dathang,
                              id_sach=c['id'],
                              soluong=c['quantity'],
                              dongia=c['price'])
            db.session.add(d)

        db.session.commit()


def category_stats():
    """
    Select c.id, c.name, count(p.id)
    From TheLoai c, Sach p
    Where c.id = p.TheLoai_id
    group by c.id, c.name
    """

    # return TheLoai.query.join(Sach, Sach.idtheloai.__eq__(TheLoai.id), isouter=True).add_columns(func.count(Sach.id))\
    #     .group_by(TheLoai.id, TheLoai.tentheloai).all()

    return db.session.query(TheLoai.id, TheLoai.tentheloai, func.count(Sach.id))\
        .join(Sach, TheLoai.id.__eq__(Sach.idtheloai), isouter=True).group_by(TheLoai.id, TheLoai.tentheloai).all()


def sach_stats(kw=None, from_date=None, to_date=None):
    p = db.session.query(Sach.id, Sach.tensach, func.sum(ChiTietHoaDon.soluong*ChiTietHoaDon.dongia))\
        .join(ChiTietHoaDon, ChiTietHoaDon.id_sach.__eq__(Sach.id), isouter=True)\
        .group_by(Sach.id, Sach.tensach).all()

    return p