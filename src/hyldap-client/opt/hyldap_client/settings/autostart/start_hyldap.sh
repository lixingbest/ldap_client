#!/bin/bash

mkdir -p ~/.hyldap/

# 用户登录脚本
/usr/bin/python3 /opt/hyldap_client/exec/startup_session.py

/bin/python3 /opt/hyldap_client/exec/strategy.py > ~/.config/autostart/strategy_logging.log
