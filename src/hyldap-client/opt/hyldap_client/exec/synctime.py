import json
import os
import subprocess
import time
import getpass
import platform
from config import *
from common import *

print("即将开始时间同步")

sync_rs = subprocess.check_output("/bin/expect /opt/hyldap_client/exec/shell/synctime.sh "+SUDO_USER_PASSWD+" "+SUDO_USER_NAME+" "+DOMAIN_SERVER_IP,shell=True)
sync_rs = str(sync_rs,"utf8")
print("时间同步结果：",sync_rs)

print("时间同步完成")