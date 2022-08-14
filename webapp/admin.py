from webapp import db, app
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from webapp.models import *
from flask_admin import BaseView, expose
from flask_login import logout_user, current_user
from flask import redirect
import utils


class AuthenticatedAdmin(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role.__eq__(Role.Administrator)


class View_Sach(AuthenticatedAdmin):
    can_view_details = True
    can_edit = True
    can_delete = True
    can_export = True
    column_exclude_list = ['hinhanh']
    column_filters = ['tensach', 'giaban']
    column_searchable_list = ['tensach', 'idtheloai']
    column_labels = {
        'tensach': 'Tên Sách',
        'mota': 'Mô Tả',
        'hinhanh': 'Hình Ảnh',
        'giaban': 'Giá Bán',
        'soluong': 'Số lượng',
        'tacgia': 'Tác Giả',
        'active': 'Còn Kinh Doanh',
        'theloai': 'Thể loại',
        'ngaylap': "Ngày Lập"
    }
    form_excluded_columns = ['chitiethoadon', 'chitietdathang', 'comments', 'chitietphieunhap']


class View_TheLoai(AuthenticatedAdmin):
    can_edit = True
    can_view_details = True
    column_labels = {
        'tentheloai': 'Thể Loại',
    }
    form_excluded_columns = ['rsach']


class View_HoaDon(AuthenticatedAdmin):
    can_create = True
    can_edit = True
    can_view_details = True
    can_delete = True
    can_export = True
    column_filters = ['id_hoadon', 'tonggia']
    column_labels = {
        'Sach': 'Mã sách',
        'Hoadon': 'Mã hóa đơn',
        'soluong': 'Số lượng',
        'dongia': 'Đơn giá',
        'tonggia': 'Tổng giá'
    }


class View_DatHang(AuthenticatedAdmin):
    can_create = False
    can_view_details = True
    can_delete = True
    can_edit = False
    can_export = True
    column_filters = ['id_dathang', 'tonggia']
    column_labels = {
        'Sach': 'Mã sách',
        'Dathang': 'Mã đặt hàng',
        'soluong': 'Số lượng',
        'dongia': 'Đơn giá',
        'tonggia': 'Tổng giá'
    }

class ViewUser(AuthenticatedAdmin):
    can_export = True
    can_delete = True
    can_view_details = True
    can_create = True
    can_edit = True
    column_labels = {
        'ten': 'Tên',
        'username': 'Username',
        'password': 'Password',
        'hinhanh': 'Avatar',
        'sodienthoai': 'Số điện thoại',
        'diachi': 'Địa chỉ',
        'email': 'Email',
        'ngaylap': 'Ngày tạo',
        'role': 'Phân quyền'
    }
    form_excluded_columns = ['hoadon', 'dathang', 'comments', 'phieunhap']


class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()

        return redirect('/admin')

    def is_accessible(self):
        return current_user.is_authenticated


class StatsView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/stats.html', stats=utils.sach_stats())

    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == Role.Administrator


class MyAdminIndexView(AdminIndexView):
    @expose("/")
    def index(self):

        return self.render("admin/index.html", stats=utils.category_stats())


admin = Admin(app=app, name='Quản Lí Thư Viện', template_mode='bootstrap4', index_view=MyAdminIndexView())
admin.add_view(View_Sach(Sach, db.session, name='Sách'))
admin.add_view(View_TheLoai(TheLoai, db.session, name='Thể loại'))
admin.add_view(View_DatHang(ChiTietDatHang, db.session, name='Đơn đặt hàng'))
admin.add_view(View_HoaDon(ChiTietHoaDon, db.session, name='Hóa đơn'))
admin.add_view(ViewUser(User, db.session, name='Người dùng'))
admin.add_view(StatsView(name='Thống kê báo cáo'))
admin.add_view(LogoutView(name="Đăng xuất"))
