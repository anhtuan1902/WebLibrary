from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, Boolean, Enum
from datetime import datetime
from enum import Enum as UserEnum
from sqlalchemy.orm import relationship, backref
from webapp import db


class BaseModel(db.Model):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)


class Sach(BaseModel):
    __tablename__ = 'sach'

    tensach = Column(String(80), nullable=False)
    idtheloai = Column(Integer, ForeignKey('theloai.id'), nullable=False)
    hinhanh = Column(String(150), nullable=True)
    mota = Column(String(900))
    tacgia = Column(String(50), nullable=False)
    giaban = Column(Float, default=0)
    soluong = Column(Integer, default=0)
    active = Column(Boolean, default=True)
    ngaytao = Column(Date, default=datetime.now().today())
    chitiethoadon = relationship('ChiTietHoaDon', backref='sach', lazy=True)
    chitietdathang = relationship('ChiTietDatHang', backref='sach', lazy=True)
    chitietphieunhap = relationship('ChiTietPhieuNhap', backref='sach', lazy=True)
    comments = relationship('Comment', backref='sach', lazy=True)

    def __str__(self):
        return self.tensach


class TheLoai(BaseModel):
    __tablename__ = 'theloai'

    tentheloai = Column(String(50), nullable=False)
    rsach = relationship('Sach', backref='theloai', lazy=True)

    def __str__(self):
        return self.tentheloai


class Role(UserEnum):
    Administrator = 1
    Customer = 2


class User(BaseModel, UserMixin):
    __tablename__ = 'user'

    ten = Column(String(100), nullable=False)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(250), nullable=False)
    hinhanh = Column(String(100))
    sodienthoai = Column(Integer, nullable=False, unique=True)
    diachi = Column(String(250), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    active = Column(Boolean, default=True)
    ngaylap = Column(Date, default=datetime.now())
    role = Column(Enum(Role), default=Role.Customer)
    comments = relationship('Comment', backref='user', lazy=True)
    hoadon = relationship('HoaDon', backref='user', lazy=True)
    dathang = relationship('DatHang', backref='user', lazy=True)
    phieunhap = relationship('PhieuNhap', backref='user', lazy=True)

    def __str__(self):
        return self.ten


class PhieuNhap(BaseModel):
    __tablename__ = 'phieunhap'

    ngaytao = Column(Date, default=datetime.now())
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    chitiet = relationship('ChiTietPhieuNhap', backref='phieunhap', lazy=True)


class ChiTietPhieuNhap(db.Model):
    __tablename__ = 'chitietphieunhap'

    id_sach = Column(Integer, ForeignKey('sach.id'), primary_key=True)
    id_phieunhap = Column(Integer, ForeignKey('phieunhap.id'), primary_key=True)
    soluong = Column(Integer, default=0)
    dongia = Column(Float, default=0)
    tonggia = Column(Float, default=dongia * soluong)


class HoaDon(BaseModel):
    ngaylap = Column(Date, default=datetime.now())
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    chitiet = relationship('ChiTietHoaDon', backref='hoadon', lazy=True)


class ChiTietHoaDon(db.Model):
    id_sach = Column(Integer, ForeignKey(Sach.id), nullable=False, primary_key=True)
    id_hoadon = Column(Integer, ForeignKey(HoaDon.id), nullable=False, primary_key=True)
    soluong = Column(Integer, default=0)
    dongia = Column(Float, default=0)
    tonggia = Column(Float, default=dongia * soluong)


class DatHang(BaseModel):
    ngaytao = Column(Date, default=datetime.now())
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    chitiet = relationship('ChiTietDatHang', backref='dathang', lazy=True)


class ChiTietDatHang(db.Model):
    id_dathang = Column(Integer, ForeignKey(DatHang.id), nullable=False, primary_key=True)
    id_sach = Column(Integer, ForeignKey(Sach.id), nullable=False, primary_key=True)
    soluong = Column(Integer, default=0)
    dongia = Column(Float, default=0)
    tonggia = Column(Float, default=dongia * soluong)


class Comment(BaseModel):
    content = Column(String(255), nullable=False)
    sach_id = Column(Integer, ForeignKey(Sach.id), nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    created_date = Column(Date, default=datetime.now())

    def __str__(self):
        return self.content

