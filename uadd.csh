#!/bin/csh

set userid = $1
set passwd = $2 

echo $passwd | pw useradd $userid -g wheel -c "Cont User" -s csh -m -h0

