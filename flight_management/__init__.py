from flask import Flask
from urllib.parse import quote
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager



app = Flask(__name__)
app.secret_key = '^%^&%^(*^^^&&*^(*^^&$%&*&*%^&$&$%$$$$#$%^'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/flight_management?charset=utf8mb4" % quote('1234')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

# CẤU HÌNH QUY ĐỊNH
app.config['THOI_GIAN_BAY_TOI_THIEU'] = 30 #MINUTE
app.config['SO_SAN_BAY_TRUNG_GIAN_TOI_DA'] = 2
app.config['THOI_GIAN_DUNG_TOI_THIEU'] = 20 #MINUTE
app.config['THOI_GIAN_DUNG_TOI_DA'] = 30 #MINUTE
app.config['THOI_GIAN_BAN_VE'] = 4 #HOUR
app.config['THOI_GIAN_DAT_VE'] = 12 #HOUR
app.config['SO_LUONG_HANG_VE'] = 2
app.config['SO_LUONG_SAN_BAY'] = 10

# CẤU HÌNH CHUNG
app.config["VERTICAL_MAX"]= 3


db = SQLAlchemy(app)
login = LoginManager(app)