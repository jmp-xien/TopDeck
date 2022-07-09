# TopDeck is provided under the Mozilla Public License Version 2.0
# All other included code and work is provided under their respective License
# 
# TopDeck written by jmp_xien:
# github.com/jmp_xien


import os, subprocess, crypt, ast, time
from werkzeug.utils import secure_filename
from flask import session, request, flash, url_for, \
    redirect, render_template, Markup, escape
from simplepam import authenticate
from flask_bcrypt import Bcrypt
from topdeck import app, db
from topdeck.models import User, Container, Server, \
    Containerservice, Containeruser
from topdeck.forms import *
from topdeck.process import *


page = {
    "intro": "Main Page",
    "editrc": "Edit RC Config",
    "editperi": "Edit Periodic",
    "contadd": "Add Container",
    "contstate": "Container State",
    "contconfig": "Container Config",
    "contuseradm": "Container Users",
    "contupdate": "Edit Container",
    "contservice": "Edit Services",
    "contsvclist": "List Services",
    "contsvcmod": "Modify Service",
    "contuser": "Edit Users",
    "serverconf": "Configure Server",
    "serverreset": "Reset Server",
    "serveradmin": "Server Cluster",
    "useradd": "Add New User",
    "userupdate": "Edit User",
    "contshell": "Container Shell"
}


class User_Proc:
    def __init__(self, username=None):
        self.user = User.query.filter_by(username=username).first()

    def add_user(self, form):
        bcry = Bcrypt()
        username = form.username.data.strip()
        password = form.password.data.strip()
        email =  form.email.data.strip()
        admin =  form.admin.data.strip()
        pwhash  = bcry.generate_password_hash(password).decode('utf-8')
        newuser = User(
            username,
            pwhash,
            email,
            admin,
        )
        db.session.add(newuser)
        db.session.commit()

    def update_user(self, updatepw, udata):
        user = User.query.get(udata.uid.data)
        user.email = udata.email.data.strip()
        user.admin = udata.admin.data.strip()
        inpw = udata.password.data.strip()
        if updatepw:
            bcry = Bcrypt()
            pwhash = bcry.generate_password_hash(inpw).decode('utf-8')
            user.password = pwhash
        db.session.commit()

    def delete_user(self, uid):
        user = User.query.get(uid)
        db.session.delete(user)
        db.session.commit()
        return True

    def verify_user_dup(self, uid, inuname):
        user = User.query.get(uid)
        newuser = User.query.filter_by(username=inuname).first()
        if newuser:
            if user.id == newuser.id:
                return False
            else:
                return True
        else:
            return False

    def getuser_by_uid(self, uid):
        self.user = User.query.get(uid)
        return self.user

    def getuser_by_uname(self, username):
        self.user = User.query.filter_by(username=username).first()
        return self.user

    def auth_user(self, username, password):
        user = User.query.filter_by(username=username).first()
        bcry = Bcrypt()
        if user:
            pw_match = bcry.check_password_hash(user.password, password)
            if pw_match:
                return True
            else:
                return False
        return False

    def user_admin(self):
        isadmin = self.user.admin
        if isadmin == "Yes":
            return True
        else:
            return False


class Server_Proc:
    def __init__(self):
        self.server = Server.query.first()

    def add_server(self, config):
        hostname = config.hostname.data.strip()
        daship = config.daship.data.strip()
        dashport = config.dashport.data.strip()
        basedir = config.basedir.data.strip()
        logdir = config.logdir.data.strip()
        contdir = config.contdir.data.strip()
        domain = config.domain.data.strip()
        upd_serv_conf = Server(
            hostname,
            daship,
            dashport,
            basedir,
            logdir,
            contdir,
            domain
        )
        db.session.add(upd_serv_conf)
        db.session.commit()
        return True

    def update_serv_conf(self, config, sid=None):
        if not sid:
            sid = 1
        srv = Server.query.get(sid)
        srv.daship  = config.daship.data.strip()
        srv.dashport = config.dashport.data.strip()
        srv.basedir = config.basedir.data.strip()
        srv.logdir  = config.logdir.data.strip()
        srv.contdir = config.contdir.data.strip()
        srv.dnsip   = config.dnsip.data.strip()
        srv.domain  = config.domain.data.strip()
        db.session.commit()
        contli  = []
        allcont = Container.query.all()
        for c in allcont:
            contli.append(c.hostname)
        proc_update_serv_config(config, contli)
        return True

    def edit_server(self, config, sid):
        srv = Server.query.get(sid)
        srv.hostname  = config.hostname.data.strip()
        srv.daship  = config.daship.data.strip()
        srv.dashport  = config.dashport.data.strip()
        db.session.commit()
        return True

    def remove_server(self, sid):
        if sid == 1 or sid == "1":
            return False
        server = Server.query.get(sid)
        db.session.delete(server)
        db.session.commit()
        return True

    def reset_gunicorn(self):
        proc_reset_gunicorn()
        return True


class Container_Proc:
    def __init__(self, cname=None):
        self.cont = Container.query.filter_by(hostname=cname).first()

    def cont_by_cid(self, cid):
        self.cont = Container.query.get(cid)
        return self.cont

    def cont_by_name(self, cname):
        self.cont = Container.query.filter_by(hostname=cname).first()
        return self.cont

    def new_container(self, config):
        hostname  = config.hostname.data.strip()
        ipaddress = config.ipaddress.data.strip()
        ethernet  = config.ethernet.data.strip()
        options = config.options.data.strip()
        state = 'stopped'
        newcont = Container(
            hostname,
            ipaddress,
            ethernet,
            options,
            state,
        )
        proc_new_cont(config)
        db.session.add(newcont)
        db.session.commit()

    def update_container(self, config):
        cont = Container.query.get(config.cid.data)
        old_name = cont.hostname
        new_name = config.hostname.data.strip()
        cont.hostname  = config.hostname.data.strip()
        cont.ipaddress = config.ipaddress.data.strip()
        cont.ethernet  = config.ethernet.data.strip()
        cont.options = config.options.data.strip()
        db.session.commit()
        update_name = True
        if new_name == old_name:
            update_name = False
        proc_update_cont(update_name, new_name, old_name)
        # reset and update files
        self.update_conf_files()

    def delete_cont(self, cid):
        cont = Container.query.get(cid)
        cname = cont.hostname
        proc_delete_cont(cname)
        db.session.delete(cont)
        db.session.commit()
        self.update_conf_files()

    def update_conf_files(self):
        allcont = self.all_container()
        for cn in allcont:
            proc_create_conf(cn.hostname, cn.ipaddress, cn.ethernet, cn.options)
        proc_config_files()

    def cont_state_update(self, service, cname):
        cont = self.cont_by_name(cname)
        cont_run = ' one' + service + ' '
        oscmd1 = 'service jail ' + cont_run + cname
        print(oscmd1)
        proc1 = subprocess.run(oscmd1, shell=True)
        # Start services in container, if enabled
        if service == "start" or service == "restart":
            cid = cont.id
            allsvc = Containerservice.query.filter_by(contid=cid).all()
            for s in allsvc:
                if s.contsvcstatus == 'enabled':
                    cntsvc = s.contservice
                    svcmod = proc_cont_svc_modify('enable', cname, cntsvc)
            cont.state = "running"
        else:
            cont.state = "stopped"
        # update container state
        db.session.commit()
        return True

    def verify_cont_dup(self, cid, cnewname):
        cont = Container.query.get(cid)
        newcont = Container.query.filter_by(hostname=cnewname).first()
        if newcont:
            if cont.id == newcont.id:
                return False
            else:
                return True
        else:
            return False

    def all_container(self):
        self.allcont = Container.query.all()
        return self.allcont

    def container_service(self, svcid):
        self.contsvc = Containerservice.query.get(svcid)
        return self.contsvc

    def cont_running_state(self, cid):
        contsta = Container.query.get(cid)
        if contsta.state == "running":
            return True
        else:
            return False

    def cont_srvc_install(self, icontid, indata):
        if not self.cont_running_state(icontid):
            return False
        contsvc = indata.contservice.data
        csvcsta = 'installed'
        cidlist = []
        # svc already installed
        contid = str(icontid)
        svc = Containerservice.query.filter_by(contservice=contsvc).all()
        if svc:
            for s in svc:
                cidlist.append(str(s.contid))
            print("Container ID list", cidlist)
            if contid in cidlist:
                print(f'Container already has service "{ contsvc }" installed')
                return False
        cont = Container.query.get(contid)
        proc_cont_svc_install(cont.hostname, contsvc)
        # change shell conf
        if contsvc == "shellinabox":
            proc_sh_config(cont.hostname)
        newcontsvc = Containerservice(
            contsvc,
            csvcsta,
            contid,
        )
        db.session.add(newcontsvc)
        db.session.commit()
        return True

    def cont_svc_modify(self, option, cohname, svcid):
        cont = self.cont_by_name(cohname)
        if not self.cont_running_state(cont.id):
            return 'NOTRUN'
        contsvc = Containerservice.query.get(svcid)
        svcname = contsvc.contservice
        svcmod = proc_cont_svc_modify(option, cohname, svcname)
        # svcmod = True
        if not svcmod:
            return 'NOTRCD'
        if option == "enable":
            contsvc.contsvcstatus = 'enabled'
        elif option == "disable":
            contsvc.contsvcstatus = 'disabled'
        elif option == "uninst":
            db.session.delete(contsvc)
        db.session.commit()
        return 'OK'

    def cont_user_modify(self, contid, indata):
        if not self.cont_running_state(contid):
            return False
        cuid   = indata.cuid.data
        cuser  = indata.contuser.data
        usrstat = indata.contusrstat.data
        cuserpw = indata.contuserpwd.data
        coption = indata.contoption.data
        cont = Container.query.get(contid)
        cname = cont.hostname
        umod = proc_cont_user_modify(coption, cname, cuser, cuserpw)
        if coption == "add":
            newuser = Containeruser(
                cuser,
                usrstat,
                contid,
            )
            db.session.add(newuser)
            db.session.commit()
            print("new user added to container")
        elif coption == "delete":
            puser = Containeruser.query.get(cuid)
            db.session.delete(puser)
            db.session.commit()
            cuserpw = 'None'
            print("user deleted from container")
        elif coption == "reset":
            print("reset user password in container")


@app.route("/contshell/<cohname>", methods=['GET', 'POST'])
def contshell(cohname):
    if "username" in session:
        username = escape(session["username"])
    else:
        return redirect(url_for('login'))
    cp = Container_Proc()
    cont = cp.cont_by_name(cohname)
    form = ShellInstallForm(request.form)
    pageid="contshell"
    pageli=page[pageid]
    if request.method == 'POST':
        serv = form.contservice.data
        inst = cp.cont_srvc_install(cont.id, form)
        if inst:
            svc = Containerservice.query.filter_by(contservice='shellinabox',contid=cont.id).first()
            if svc:
                print("Found service:", svc)
                mod = cp.cont_svc_modify('enable', cohname, svc.id)
                if mod == 'OK':
                    flash(f'INFO: added web terminal to container { cohname }.', 'success')
            else:
                flash(f'ERROR: web shell not active in { cohname }, try via service admin.', 'error')
        else:
            flash(f'ERROR: web terminal already installed or failed in container { cohname }.', 'error')
        return redirect(url_for('contconfig'))
    return render_template("contshell.html", username=username, pageid=pageid, pageli=pageli, form=form, cont=cont)


@app.route('/contuser/<cohname>/<contid>', methods=['GET', 'POST'])
def contuser(cohname, contid):
    if "username" in session:
        username = escape(session["username"])
    else:
        return redirect(url_for('login'))
    form = ContUserForm(request.form)
    pageid = "contuser"
    pageli = page[pageid]
    cousers = Containeruser.query.filter_by(contid=contid).all()
    contq  = Container.query.filter_by(hostname=cohname).first()
    if request.method == 'POST':
        cuser = form.contuser.data
        copt  = form.contoption.data
        if not copt == "delete":
            pwd1 = str(form.contuserpwd.data)
            pwd2 = str(form.contuserpwd_conf.data)
            if not pwd1 == pwd2:
                flash('Error: passwords do not match, please retry.', 'error')
                return redirect('/contuser/' + cohname + '/' + contid)
            if not (pwd1 or pwd2):
                flash('Error: blank passwords, user access not updated.', 'error')
                return redirect('/contuser/' + cohname + '/' + contid)
        cp = Container_Proc()
        mod = cp.cont_user_modify(contid, form)
        flash(f'INFO: success, {copt} user "{ cuser }" for container: { cohname }.', 'success')
        return redirect(url_for('contuseradm'))
    return render_template('contuser.html', cousers=cousers, contq=contq, username=username, form=form, pageli=pageli)


@app.route('/contsvcmod/<option>/<cohname>/<csvcid>', methods=['GET', 'POST'])
def contsvcmod(option, cohname, csvcid):
    if "username" in session:
        username = escape(session["username"])
    else:
        return redirect(url_for('login'))
    cp = Container_Proc()
    cnt = cp.container_service(csvcid)
    csn = cnt.contservice
    mod = cp.cont_svc_modify(option, cohname, csvcid)
    if mod == 'NOTRUN':
        flash(f'ERROR: { cohname } not "running", unable to "{ option }" service { csn }.', 'error')
    elif mod == 'NOTRCD':
        flash(f'ERROR: rc.d file for service { csn } not found, unable to "{ option }" .', 'error')
    else:
        flash(f'INFO: service { csn } modified to { option } in { cohname }.', 'success')
    return redirect(url_for('contservice'))


@app.route('/contsvclist/<cohname>/<contid>', methods=['GET', 'POST'])
def contsvclist(cohname, contid):
    if "username" in session:
        username = escape(session["username"])
    else:
        return redirect(url_for('login'))
    pageid = "contsvclist"
    pageli = page[pageid]
    form = ContServiceForm(request.form)
    cosrvces = Containerservice.query.filter_by(contid=contid).all()
    contq = Container.query.filter_by(hostname=cohname).first()
    if request.method == 'POST':
        serv = form.contservice.data
        cp = Container_Proc()
        inst = cp.cont_srvc_install(contid, form)
        if inst:
            flash(f'INFO: added service { serv } to container { cohname }.', 'success')
        else:
            flash(f'ERROR: service "{ serv }" not added, verify if installed in container { cohname }.', 'error')
        return redirect('/contsvclist/'+cohname+'/'+contid)
    return render_template('contsvclist.html', cosrvces=cosrvces, contq=contq, username=username, form=form, pageli=pageli)


# Begin Authentication For Panel Pages
@app.route("/")
def home():
    if "username" in session:
        username = escape(session["username"])
        pageid="intro"
        pageli=page[pageid]
        return render_template("index.html", username=username, pageid=pageid, pageli=pageli)
    return redirect(url_for('login'))


@app.route("/serverrem/<servname>/<hostid>", methods=['GET', 'POST'])
def serverrem(servname, hostid):
    if "username" in session:
        username = escape(session["username"])
    else:
        return redirect(url_for('login'))
    # Remove
    sp = Server_Proc()
    remsrv = sp.remove_server(hostid)
    flash(f'INFO: server { servname } removed from admin cluster', 'success')
    return redirect(url_for('serveradmin'))

@app.route("/serveredit/<servname>/<hostid>", methods=['GET', 'POST'])
def serveredit(servname, hostid):
    if "username" in session:
        username = escape(session["username"])
    else:
        return redirect(url_for('login'))
    # Remove
    sp = Server_Proc()
    edsrv = sp.edit_server(hostid)
    flash(f'INFO: server { servname } removed from admin cluster', 'success')
    return redirect(url_for('serveradmin'))

@app.route("/serveradmin", methods=['GET', 'POST'])
def serveradmin():
    if "username" in session:
        username = escape(session["username"])
    else:
        return redirect(url_for('login'))
    hosts = Server.query.all()
    form = ServerConf(request.form)
    pageid="serveradmin"
    pageli=page[pageid]
    if request.method == 'POST':
        sp = Server_Proc()
        sp.add_server(form)
        flash(f'INFO: new server added to cluster', 'success')
        return redirect(url_for('serveradmin'))
    return render_template("serveradmin.html", form=form, username=username, hosts=hosts, pageid=pageid, pageli=pageli)


@app.route("/contstate")
def contstate():
    if "username" in session:
        username = escape(session["username"])
    else:
        return redirect(url_for('login'))
    hosts = Container.query.all()
    form = ContServiceState(request.form)
    pageid="contstate"
    pageli=page[pageid]
    return render_template("contstate.html", form=form, username=username, hosts=hosts, pageid=pageid, pageli=pageli)


@app.route('/statemod/<service>/<inhname>', methods=['GET', 'POST'])
def statemod(service, inhname):
    if "username" in session:
        username = escape(session["username"])
    else:
        return redirect(url_for('login'))
    cname = inhname
    csp  = Container_Proc(inhname)
    cndel = csp.cont_state_update(service, cname)
    flash(f'INFO: service state "{ service }" applied to container: { cname }', 'success')
    return redirect(url_for('contstate'))


@app.route('/contadd', methods=['GET', 'POST'])
def contadd():
    if "username" in session:
        username = escape(session["username"])
    else:
        return redirect(url_for('login'))
    form = ContainerConf(request.form)
    pageid="contadd"
    pageli=page[pageid]
    if request.method == 'POST':
        cname = form.hostname.data
        nc = Container_Proc(cname)
        cnt_exists = nc.cont
        if cnt_exists:
            flash(f'ERROR: container with name "{ cname }" already exists', 'error')
            return redirect(url_for('home'))
        nc.new_container(form)
        flash(f'INFO: created new container: "{ cname }"', 'success')
        return redirect(url_for('home'))
    return render_template("contadd.html", form=form, username=username, pageid=pageid, pageli=pageli)


@app.route('/contupdate', methods=['GET', 'POST'])
def contupdate():
    if "username" in session:
        username = escape(session["username"])
    else:
        return redirect(url_for('login'))
    hosts = Container.query.all()
    form = ContUpdateConf(request.form)
    eths = get_ethernet("html")
    pageid="contupdate"
    pageli=page[pageid]
    if request.method == 'POST':
        cnt_nname = form.hostname.data
        cnt_id = form.cid.data
        cup = Container_Proc()
        cn_exists = cup.verify_cont_dup(cnt_id, cnt_nname)
        if cn_exists:
            flash(f'ERROR: container with name "{ cnt_nname }" already exists', 'error')
            return redirect(url_for('contupdate'))
        cup.update_container(form)
        flash(f'INFO: updated container: "{ cnt_nname }"', 'success')
        return redirect(url_for('contupdate'))
    return render_template("contupdate.html", form=form, eths=eths, username=username, hosts=hosts, pageid=pageid, pageli=pageli)


@app.route('/editrc/<cohname>', methods=['GET', 'POST'])
def editrc(cohname):
    if "username" in session:
        username = escape(session["username"])
    else:
        return redirect(url_for('login'))
    rcfile = '/usr/jails/container/' + cohname + '/etc/rc.conf'
    if os.path.exists(rcfile):
        with open(rcfile, 'r') as rf:
            filines = rf.read()
    else:
        flash(f'ERROR: file rc.conf not in container { cohname }.', 'error')
        return redirect(url_for('contconfig'))
    form = UpdateRCconf(request.form)
    form.rccfdata.data = filines
    pageid="editrc"
    pageli=page[pageid]
    if request.method == 'POST':
        indata = request.form['rccfdata']
        with open(rcfile, 'w') as nf:
            for d in indata:
                nf.write(str(d))
        # Content done
        flash(f'INFO: updated rc.conf file for container { cohname }.', 'success')
        return redirect(url_for('contconfig'))
    return render_template('editrc.html', hname=cohname, username=username, form=form, pageli=pageli)


@app.route('/editperi/<cohname>', methods=['GET', 'POST'])
def editperi(cohname):
    if "username" in session:
        username = escape(session["username"])
    else:
        return redirect(url_for('login'))
    perifile = '/usr/jails/container/' + cohname + '/etc/periodic.conf'
    if os.path.exists(perifile):
        with open(perifile, 'r') as rf:
            filines = rf.read()
    else:
        flash(f'ERROR: file periodic.conf not in container { cohname }.', 'error')
        return redirect(url_for('contconfig'))
    form = UpdatePeriConf(request.form)
    form.peridata.data = filines
    pageid="editperi"
    pageli=page[pageid]
    if request.method == 'POST':
        indata = request.form['peridata']
        with open(perifile, 'w') as nf:
            for d in indata:
                nf.write(str(d))
        # Content done
        flash(f'INFO: updated periodic.conf file for container { cohname }.', 'success')
        return redirect(url_for('contconfig'))
    return render_template('editperi.html', hname=cohname, username=username, form=form, pageli=pageli)


@app.route('/contuseradm')
def contuseradm():
    if "username" in session:
        username = escape(session["username"])
    else:
        return redirect(url_for('login'))
    hosts = Container.query.all()
    pageid="contuseradm"
    pageli=page[pageid]
    return render_template("contuseradm.html", username=username, hosts=hosts, pageid=pageid, pageli=pageli)


@app.route('/contconfig')
def contconfig():
    if "username" in session:
        username = escape(session["username"])
    else:
        return redirect(url_for('login'))
    hosts = Container.query.all()
    pageid="contconfig"
    pageli=page[pageid]
    return render_template("contconfig.html", username=username, hosts=hosts, pageid=pageid, pageli=pageli)


@app.route('/contservice')
def contservice():
    if "username" in session:
        username = escape(session["username"])
    else:
        return redirect(url_for('login'))
    hosts = Container.query.all()
    pageid="contservice"
    pageli=page[pageid]
    return render_template("contservice.html", username=username, hosts=hosts, pageid=pageid, pageli=pageli)


@app.route('/contdel/<inhname>', methods=['GET', 'POST'])
def contdel(inhname):
    if "username" in session:
        username = escape(session["username"])
    else:
        return redirect(url_for('login'))
    cname = inhname
    cdp = Container_Proc(inhname)
    cst = cdp.cont.state
    if cst == "running":
        flash(f'ERROR: "{ cname }" must be stopped before deleting', 'error')
        return redirect(url_for('contupdate'))
    cdel = cdp.delete_cont(cdp.cont.id)
    flash(f'INFO: deleted container: "{ cname }"', 'success')
    return redirect(url_for('contupdate'))


@app.route('/serverconf', methods=['GET', 'POST'])
def serverconf():
    if "username" in session:
        username = escape(session["username"])
    else:
        flash('ERROR: Please log-in to access TopDeck admin system.', 'error')
        return redirect(url_for('login'))
    markup_user = Markup.unescape(username)
    # isadmin = ua.user_admin()
    # if not isadmin:
    #     flash('ERROR: Must be Admin to add user to TopDeck admin system.', 'error')
    #     return redirect(url_for('home'))
    form = ServerConf(request.form)
    server = Server.query.get(1)
    pageid="serverconf"
    pageli=page[pageid]
    if request.method == 'POST':
        sp = Server_Proc()
        sp.update_serv_conf(form)
        flash(f'INFO: server configuration updated', 'success')
        return redirect(url_for('home'))
    return render_template("serverconf.html", form=form, server=server, username=username, pageid=pageid, pageli=pageli)


@app.route('/serverreset', methods=['GET', 'POST'])
def serverreset():
    if "username" in session:
        username = escape(session["username"])
    else:
        flash('ERROR: Please log-in to access TopDeck admin system.', 'error')
        return redirect(url_for('login'))
    markup_user = Markup.unescape(username)
    pageid="serverreset"
    pageli=page[pageid]
    if request.method == 'POST':
        sp = Server_Proc()
        # Reset gunicorn
        flash(f'INFO: TopDeck service reset', 'success')
        return redirect(url_for('serverreset'))
    return render_template("serverreset.html", username=username, pageid=pageid, pageli=pageli)


@app.route('/useradd', methods=['GET', 'POST'])
def useradd():
    if "username" in session:
        username = escape(session["username"])
    else:
        flash('ERROR: Please log-in to access TopDeck admin system.', 'error')
        return redirect(url_for('login'))

    markup_user = Markup.unescape(username)
    ua = User_Proc(markup_user)
    isadmin = ua.user_admin()
    if not isadmin:
        flash('ERROR: Must be Admin to add user to TopDeck admin system.', 'error')
        return redirect(url_for('home'))

    form = UserAdd(request.form)
    pageid="useradd"
    pageli=page[pageid]
    if request.method == 'POST':
        new_user = form.username.data
        nu = User_Proc()
        name_exists = nu.getuser_by_uname(new_user)
        if name_exists:
            flash(f'ERROR: user login name "{ new_user }" already exists', 'error')
            return redirect(url_for('home'))
        nu.add_user(form)
        flash(f'INFO: user name "{ new_user }" added to system', 'success')
        return redirect(url_for('home'))
    return render_template("useradd.html", form=form, username=username, pageid=pageid, pageli=pageli)


@app.route('/userupdate', methods=['GET', 'POST'])
def userupdate():
    if "username" in session:
        username = escape(session["username"])
    else:
        return redirect(url_for('login'))
    allusers = User.query.all()
    form = UserUpdate(request.form)
    pageid="userupdate"
    pageli=page[pageid]
    if request.method == 'POST':
        upd_username = form.username.data
        pw = form.password.data
        pw_conf = form.password_confirm.data
        pwupdate = False
        if not (pw == "" or pw == None):
            pwupdate = True
        if not pw == pw_conf:
            flash(f'ERROR: password entries do not match', 'error')
            return redirect(url_for('userupdate'))
        uup = User_Proc(upd_username)
        uup.update_user(pwupdate, form)
        if pwupdate:
            flash(f'INFO: account and password updated for: { upd_username }', 'success')
        else:
            flash(f'INFO: only account information updated for: { upd_username }', 'success')
        return redirect(url_for('userupdate'))
    return render_template("userupdate.html", form=form, username=username, users=allusers, pageid=pageid, pageli=pageli)


@app.route('/userdel/<del_user>', methods=['GET', 'POST'])
def userdel(del_user):
    if "username" in session:
        username = escape(session["username"])
    else:
        return redirect(url_for('login'))
    if del_user == "admin":
        flash(f'Error: not allowed to delete user: { del_user }', 'error')
        return redirect(url_for('userupdate'))
    dup = User_Proc(del_user)
    du = dup.delete_user(du.id)
    flash(f'INFO: user deleted: { del_user }', 'success')
    return redirect(url_for('userupdate'))


@app.route("/modal")
def modal():
    # Test modal pop-up
    return render_template("modal.html")


@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    flash('INFO: Logged-out of TopDeck Admin Panel.', 'error')
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST':
        username = form.username.data
        password = form.password.data
        ua = User_Proc()
        auth = ua.auth_user(username, password)
        if auth:
            session["username"] = username
            # log.info(f'User logged-in: {username}')
            # session.permanent = True
            return redirect(url_for('home'))
        else:
            flash('ERROR: Invalid username or password', 'error')
    return render_template("login.html", form=form)
