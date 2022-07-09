# TopDeck is provided under the Mozilla Public License Version 2.0
# All other included code and work is provided under their respective License
# 
# TopDeck written by jmp_xien:
# github.com/jmp_xien

from flask import Flask
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy


# Get TopDeck config variables
conf = {}
conffile = 'topdeck.conf'
with open(conffile, 'r') as cnf:
    entry = cnf.readlines()
for l in entry:
    key, val = l.strip().split(":")
    conf[key] = val

# Setup TopDeck app environment 
app = Flask(__name__)
app.config['SECRET_KEY'] = "ztIx3p07gk6h9haf"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)
app.config['MAX_CONTENT_LENGTH'] = 4*1024*1024
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://'+conf["Username"]+':'+conf["Password"]+'@localhost/topdeck'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from topdeck import routes
