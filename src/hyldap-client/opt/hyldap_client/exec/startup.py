import json
import os
import subprocess
import time
import getpass
import platform
from config import *
from common import *

print("hyldap开机启动服务开始运行")

value = read_config("startup")
print("开机任务配置="+str(value))
if value == "join_domain":

    try:
        line = ['curl','-X','POST',ADMIN_SYS_URL+'/public_service/client/echo','-H','Content-Type: application/json','-d','{"hostname":"'+get_hostname()+'","domain":"'+DOMAIN+'","clientVersion":"'+CLIENT_VERSION+'","arch":"'+platform.uname().machine+'","sysVersion":"'+get_sys_version()+'","user":"'+getpass.getuser()+'","sysName":"'+get_osname()+'","ip":"'+get_host_ip()+'"}']
        print("即将向服务器汇报安装状态：line=",line)
        start_report_result = subprocess.check_output(line)
        start_report_result = str(start_report_result,encoding="utf8")
        print("汇报数据成功，response=",start_report_result)
    except Exception as e:
        print("向平台端发送心跳时遇到错误："+str(e))
    
    try:
        print("即将开始更新配置")
        write_config({"startup":"complete"})
        print("配置更新完成")
    except Exception as e:
        print("更新配置文件时出现错误："+str(e))

    join_rs = subprocess.check_output("/usr/bin/expect /opt/hyldap_client/exec/shell/join_domain.sh "+get_hostname()+" "+SUDO_USER_PASSWD, shell=True)
    join_rs = str(join_rs,"utf8")
    print(join_rs)
else:
    print("无可执行的开机任务")

print("hyldap开机启动服务运行结束")