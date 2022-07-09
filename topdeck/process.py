# TopDeck is provided under the Mozilla Public License Version 2.0
# All other included code and work is provided under their respective License
# 
# TopDeck written by jmp_xien:
# github.com/jmp_xien

import subprocess, os
from jinja2 import Environment, FileSystemLoader
from fnmatch import fnmatch


# GLOBAL
jail_cnf = '/etc/jail.conf'
jail_dir = '/usr/jails'
config_dir = 'config'
cont_config = 'td_cont.conf'
base_config = 'base.conf'
jail_config = 'jail.conf'
container_dir = 'container'
template_dir  = 'template'

cont_dir = jail_dir + '/' + container_dir + '/'
conf_dir = jail_dir + '/' + config_dir + '/'


# Processes Modules
def get_ethernet(seltype):
    oscmd = '/sbin/ifconfig | grep flags | cut -d":" -f1'
    proc = subprocess.run(oscmd, shell=True, stdout=subprocess.PIPE)
    os_eth = proc.stdout.decode("utf-8").rstrip("\n")
    ethlist = os_eth.split('\n')
    eth_cl = []
    for e in ethlist:
        if e != "lo0":
            eth_cl.append(e)
    eth_cl.append("lo0")
    ethlist = []
    ethhtml = []
    for eth in eth_cl:
        ethline = (eth, f"Ethernet : {eth}")
        ethlist.append(ethline)
        ethhtml.append(eth)
    if seltype == "Form":
        return ethlist
    else:
        return ethhtml


def proc_update_serv_config(config, contli):
    # base_config = 'base.conf'
    tdp_ctl = 'tdctl.csh'
    tdp_tpl = 'tdctl.csh.j2'
    srv_tpl = 'base.conf.j2'
    dns_tpl = 'resolv.conf.j2'
    dns_cnf = 'resolv.conf'

    env = Environment(loader=FileSystemLoader('./', encoding='utf8'))
    tdp_conf_tmpl = env.get_template(tdp_tpl)
    srv_conf_tmpl = env.get_template(srv_tpl)
    dns_conf_tmpl = env.get_template(dns_tpl)

    td_tpl_data = tdp_conf_tmpl.render(
        log_dir = config.logdir.data.strip(),
        daship  = config.daship.data.strip(),
        dashport = config.dashport.data.strip(),
    )
    sc_tpl_data  = srv_conf_tmpl.render(
        root_dir = config.basedir.data.strip(),
        log_dir  = config.logdir.data.strip(),
        cont_dir = config.contdir.data.strip(),
        domain = config.domain.data.strip(),
    )
    dn_tpl_data = dns_conf_tmpl.render(
        dns_serv = config.dnsip.data.strip()
    )
    # to save the results
    with open(tdp_ctl, "w") as tf:
        tf.write(td_tpl_data)
    with open(base_config, "w") as cf:
        cf.write(sc_tpl_data)
    with open(dns_cnf, "w") as df:
        df.write(dn_tpl_data)
    base_fi = conf_dir + base_config
    oscmd1 = 'cp ' + base_config + ' ' + base_fi
    subprocess.run(oscmd1, shell=True)
    for cn in contli:
        fipath = cont_dir + cn + '/etc/'
        oscmd2 = 'cp ' + dns_cnf + ' ' + fipath
        subprocess.run(oscmd2, shell=True)
    proc_config_files()


def proc_reset_gunicorn():
    gupath = '/usr/venv/pyvenv/bin/'
    oscmd1 = './tdctl.csh stop'
    proc1 = subprocess.run(oscmd1, shell=True)
    oscmd2 = './tdctl.csh start'
    proc2 = subprocess.run(oscmd2, shell=True)
    return True


def proc_config_files():
    bs_cnf_file = conf_dir + base_config
    td_cnf_file = conf_dir + cont_config
    jl_cnf_file = conf_dir + jail_config
    oscmd1 = 'cat ' + bs_cnf_file + ' > ' + jl_cnf_file
    oscmd2 = 'cat ' + td_cnf_file + ' >> ' + jl_cnf_file
    oscmd3 = 'cp ' + jl_cnf_file + ' ' + jail_cnf
    proc1 = subprocess.run(oscmd1, shell=True)
    proc2 = subprocess.run(oscmd2, shell=True)
    proc3 = subprocess.run(oscmd3, shell=True)
    return True


def proc_create_conf(hname, ip, eth, opts):
    host_conf = jail_dir + '/' + config_dir + '/' + hname + '.tdc'
    td_conf   = jail_dir + '/' + config_dir + '/' + cont_config
    if opts == "" or opts == None:
        opts = "# empty options"
    hdata = (hname + ' {\n'
        + '    ip4.addr = "' + ip + '";\n'
        + '    interface = ' + eth + ';\n'
        + '    ' + opts + ';\n'
        + '}\n\n')
    with open(host_conf, 'w') as hf:
        hf.write(hdata)
    with open(td_conf, 'a') as td:
        td.write(hdata)
    return True


def proc_delete_cont(hname):
    container = cont_dir + hname
    cont_conf = conf_dir + hname + '.tdc'
    td_cnf_file = conf_dir + cont_config
    oscmd1 = 'rm -fr ' + container
    oscmd2 = 'rm -f ' + cont_conf
    oscmd3 = 'echo "" > ' + td_cnf_file
    proc1 = subprocess.run(oscmd1, shell=True)
    proc2 = subprocess.run(oscmd2, shell=True)
    proc3 = subprocess.run(oscmd3, shell=True)


def proc_update_cont(update_name, new_name, old_name):
    old_cnf = conf_dir + old_name + '.tdc'
    td_cnf_file = conf_dir + cont_config

    if update_name:
        ohn = cont_dir + old_name
        nhn = cont_dir + new_name
        oscmd1 = 'rm -f ' + old_cnf
        oscmd2 = 'mv ' + ohn + ' ' + nhn
        proc1 = subprocess.run(oscmd1, shell=True)
        proc2 = subprocess.run(oscmd2, shell=True)
    oscmd3 = 'echo "" > ' + td_cnf_file
    proc3  = subprocess.run(oscmd3, shell=True)


def proc_new_cont(config):
    hostname  = config.hostname.data.strip()
    ipaddress = config.ipaddress.data.strip()
    ethernet  = config.ethernet.data.strip()
    options = config.options.data.strip()
    # host file
    proc_create_conf(hostname, ipaddress, ethernet, options)
    bs_templ = jail_dir + '/' + template_dir + '/'
    new_cont = jail_dir + '/' + container_dir + '/' + hostname
    oscmd4 = 'mkdir ' + new_cont
    oscmd5 = 'cp -a ' + bs_templ + ' ' + new_cont
    proc4 = subprocess.run(oscmd4, shell=True)
    proc5 = subprocess.run(oscmd5, shell=True)
    # conf
    proc_config_files()
    return True


def proc_sh_config(contname):
    cmd1 = 'cp ' + jail_dir + '/template/usr/local/scripts/shellinaboxd'
    cmd2 = ' /usr/jails/container/' + contname
    cmd3 = '/usr/local/etc/rc.d/'
    cmd = cmd1 + cmd2 + cmd3
    proc = subprocess.run(cmd, shell=True)
    print(f'installed shell config in container { contname }')
    return True


def proc_cont_svc_install(contname, svc):
    cmd1 = 'jexec ' + contname
    cmd2 = ' pkg install -y ' + svc
    cmd = cmd1 + cmd2
    proc = subprocess.run(cmd, shell=True)
    print(f'Service { svc } installed in container { contname }')
    return True


def proc_cont_svc_modify(option, cohname, svcname):
    uninst = False
    rcpath1 = '/usr/jails/container/' + cohname
    rcpath2 = '/usr/local/etc/rc.d/'
    rcdpath = rcpath1 + rcpath2
    svcctlfi = rcdpath + svcname
    svcnamed = svcname + 'd'
    svcdpath = rcdpath + svcnamed
    svcfwild = svcname + '*'

    svcfi = os.path.exists(svcctlfi)
    if not svcfi:
        svcd = os.path.exists(svcdpath)
        if not svcd:
            cnt = 0
            for f in os.listdir(rcdpath):
                if fnmatch(f, svcfwild):
                    cnt += 1
                    tmpfi = f
            if cnt == 1:
                svcname = tmpfi
            else:
                print("Service or Service-d file not found.")
                return False
        else:
            svcname = svcnamed
            print("Service-d file OK")
    else:
        print("Service file OK")

    cmd1 = 'jexec ' + cohname
    if option == "enable":
        cmd2 = ' service ' + svcname + ' onestart'
    elif option == "disable":
        cmd2 = ' service ' + svcname + ' onestop'
    elif option == "uninst":
        uninst = True
        cmd2 = ' service ' + svcname + ' onestop'
    cmd = cmd1 + cmd2
    print("Executing command:", cmd)
    proc1 = subprocess.run(cmd, shell=True)
    if uninst:
        cmd3 = ' pkg remove -y ' + svcname
        cmd = cmd1 + cmd3
        proc2 = subprocess.run(cmd, shell=True)
    print(f'Service { svcname } state updated in container { cohname }')
    return True


def proc_cont_user_modify(uoption, hname, user, password):
    cmd1 = 'jexec ' + hname
    if uoption == "add":
        cmd2 = ' /usr/local/scripts/uadd.csh ' + user + ' ' + password
        cmd  = cmd1 + cmd2
    elif uoption == "delete":
        cmd2 = ' pw userdel -n '+ user + ' -r'
        cmd = cmd1 + cmd2
    elif uoption == "reset":
        cmd2 = ' /usr/local/scripts/uupd.csh ' + user + ' ' + password
        cmd = cmd1 + cmd2
    proc = subprocess.run(cmd, shell=True)
    print("Container user process completed")
    return True


def proc_get_rc_conf_file(rcfile):
    pass


