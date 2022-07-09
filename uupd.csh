#!/bin/csh

set userid = $1
set passwd = $2 

echo $passwd | pw usermod $userid -h0

