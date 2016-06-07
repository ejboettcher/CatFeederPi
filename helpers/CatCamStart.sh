#!/bin/bash
#

sudo fuser -k 8082/tcp

#askubuntu.com/question/428713/create-a-screen-session-with-a-bash-using-contab

screen -dmS CatScreen  /usr/local/bin/Startcv3Flask.sh

