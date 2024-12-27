from flask import Flask
from urllib.parse import quote
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import cloudinary
from payos import PayOS
from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = '^%^&%^(*^^^&&*^(*^^&$%&*&*%^&$&$%$$$$#$%^'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/flight_management?charset=utf8mb4" % quote('1234')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

# Configuration
# cloudinary.config(
#     cloud_name = "dcztds1is",
#     api_key = "893276997459282",
#     api_secret = "ewju58qrKhZ1zi7k7rTVvQ2LpuE", # Click 'View API Keys' above to copy your API secret
#     secure=True
# )

cloudinary.config(
    cloud_name="demfjaknk",
    api_key="675115286763916",
    api_secret="YmFNxxs4iZTU5pv-qrBFpldsgMw",  # Click 'View API Keys' above to copy your API secret
    secure=True
)
db = SQLAlchemy(app)
login = LoginManager(app)


#payment
client_id = "81e41fb0-7275-423b-9df7-b5e28b0192e0"
api_key = "8b5ec400-8eb1-4741-a897-79147beb13b9"
checksum_key = "52a4971e74888cb9b20243ae0905f19bf6f7b90a3adddc312463332af7247966"
payos = PayOS(client_id, api_key, checksum_key)


#mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'httranggg@gmail.com'
app.config['MAIL_PASSWORD'] = 'tjob qmtx xtst jcas'
mail = Mail(app)