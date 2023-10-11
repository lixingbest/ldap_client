import json
import os
import subprocess
import time
import getpass
import platform
from config import *
from common import *

print("hyldap已启动用户登录脚本")

try:

    userinfo = get_username()
    uname = userinfo.get("name")
    utype = userinfo.get("type")
    # 仅在域用户登录时才上报
    if utype == "ldap" or utype == "ad":
        line = ['curl','-X','POST',ADMIN_SYS_URL+'/public_service/client/echo','-H','Content-Type: application/json','-d','{"hostname":"'+get_hostname()+'","domain":"'+DOMAIN+'","clientVersion":"'+CLIENT_VERSION+'","sysArch":"'+platform.uname().machine+'","sysVersion":"'+get_sys_version()+'","uid":"'+uname+'","sysName":"'+get_osname()+'","ip":"'+get_host_ip()+'","mac":"'+get_mac_addr()+'"}']
        print("即将向服务器汇报安装状态：line=",line)
        start_report_result = subprocess.check_output(line)
        start_report_result = str(start_report_result,encoding="utf8")
        print("汇报数据成功，response=",start_report_result)
except Exception as e:
    print("向平台端发送心跳时遇到错误："+str(e))

try:
    # 加载主机登录限制
    load_login_limit(DOMAIN,uname)
except Exception as e:
    print("向平台端发送心跳时遇到错误："+str(e))

print("hyldap用户登录脚本执行完毕")