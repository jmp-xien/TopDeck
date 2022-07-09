# TopDeck is provided under the Mozilla Public License Version 2.0
# All other included code and work is provided under their respective License
# 
# TopDeck written by jmp_xien:
# github.com/jmp_xien

from sqlalchemy import Integer, ForeignKey, String, Text, Boolean, Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from topdeck import db


class Server(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(64), nullable=False)
    daship   = db.Column(db.String(32), nullable=False)
    dashport = db.Column(db.String(8), nullable=False)
    basedir = db.Column(db.String(128), nullable=False)
    logdir  = db.Column(db.String(128), nullable=False)
    contdir = db.Column(db.String(128), nullable=False)
    dnsip = db.Column(db.String(32), nullable=False)
    domain  = db.Column(db.String(128), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Server(id='{self.id}', hostname='{self.hostname}', daship='{self.daship}', dashport='{self.dashport}', \
                basedir='{self.basedir}', logdir='{self.logdir}', contdir='{self.contdir}', \
                dnsip='{self.dnsip}', domain='{self.domain}')"

    def __init__(self, hostname, daship, dashport, basedir, logdir, contdir, dnsip, domain):
        self.hostname = hostname
        self.daship = daship
        self.dashport = dashport
        self.basedir = basedir
        self.logdir = logdir
        self.contdir = contdir
        self.dnsip = dnsip
        self.domain = domain      


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128))
    admin = db.Column(db.String(8), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"User(id='{self.id}', username='{self.username}', password='{self.password}', email='{self.email}', admin='{self.admin}')"

    def __init__(self, username, password, email, admin):
        self.username = username
        self.password = password
        self.email = email
        self.admin = admin


class Container(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(64), nullable=False)
    ipaddress = db.Column(db.String(24), nullable=False)
    ethernet = db.Column(db.String(16), nullable=False)
    options = db.Column(db.String(255))
    state = db.Column(db.String(24))    
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    contuser = db.relationship("Containeruser", cascade="all, delete", passive_deletes=True, backref=db.backref("container", lazy=True))
    contservice = db.relationship("Containerservice", cascade="all, delete", passive_deletes=True, backref=db.backref("container", lazy=True))

    def __repr__(self):
        return f"Container(id='{self.id}', hostname='{self.hostname}', ipaddress='{self.ipaddress}', ethernet='{self.ethernet}', options='{self.options}', state='{self.state}')"

    def __init__(self, hostname, ipaddress, ethernet, options, state):
        self.hostname = hostname
        self.ipaddress = ipaddress
        self.ethernet = ethernet
        self.options = options
        self.state = state


class Containeruser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contuser = db.Column(db.String(64), nullable=False)
    usrstatus = db.Column(db.String(64), nullable=False)
    date  = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    contid = db.Column(db.Integer, db.ForeignKey("container.id", ondelete='CASCADE'), nullable=False)

    def __repr__(self):
        return f"Containeruser(id='{self.id}', contuser='{self.contuser}', usrstatus='{self.usrstatus}', contid='{self.contid}')"

    def __init__(self, contuser, usrstatus, contid):
        self.contuser = contuser
        self.usrstatus = usrstatus
        self.contid = contid


class Containerservice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contservice = db.Column(db.String(64), nullable=False)
    contsvcstatus = db.Column(db.String(64), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    contid = db.Column(db.Integer, db.ForeignKey("container.id", ondelete='CASCADE'), nullable=False)

    def __repr__(self):
        return f"Containerservice(id='{self.id}', contservice='{self.contservice}', contsvcstatus='{self.contsvcstatus}', contid='{self.contid}')"

    def __init__(self, contservice, contsvcstatus, contid):
        self.contservice = contservice
        self.contsvcstatus = contsvcstatus
        self.contid = contid
