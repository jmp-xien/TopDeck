#!/bin/csh

set suser = `id -u`
if ($suser != 0) then
    echo ERROR: TopDeck remove must be ran as super user.
    exit(1)
endif

sleep 2
echo ">>> CAUTION: trying to remove TopDeck panel <<<"
echo -n "Type 'yes' to continue or hit enter key to cancel: "
set remresp = $<

set upresp = `echo "$remresp" | tr '[A-Z]' '[a-z]'`
if ($upresp != "yes" ) then
    echo Canceling TopDeck panel removal.
    exit(1)
endif
echo Begin removal of TopDeck panel...
sleep 1

set startdir = `pwd`
set jl_bsdir = "/usr/jails"

set rootmnt = `zfs list | egrep 'ROOT.*/$' | cut -d'/' -f1`
set rootzfs = `zfs list | egrep 'ROOT.*/$' | cut -d'/' -f2`

./tdctl.csh stop
sleep 1
mysql -e "drop database topdeck;"

cd /usr/
rm -fr flask/*
rm -fr venv/*
rm -fr jails/*
sleep 1
chflags -R noschg jails
rm -fr jails/*

cd $startdir
if ("$rootzfs" == "ROOT" ) then

    echo ">>> CAUTION: About to destroy mounts: usr/flask, usr/venv, and usr/jails <<<"
    echo -n "Type 'yes' to allow or hit enter key to cancel: "
    set desreps = $<

    set updes = `echo "$desreps" | tr '[A-Z]' '[a-z]'`
    if ($updes != "yes" ) then
        echo Ignoring TopDeck mount removal
    else
        echo Begin removal of TopDeck mounts...
        sleep 1
        # ZFS
        zfs destroy $rootmnt/usr/jails
        zfs destroy $rootmnt/usr/flask
        zfs destroy $rootmnt/usr/venv
        echo "Removed TopDeck mounts..."
        sleep 1
    endif
endif

echo "Completed removal of TopDeck panel!"
