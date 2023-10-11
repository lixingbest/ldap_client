from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import subprocess
import os
import socket
from tkinter import simpledialog
import urllib.request
import urllib.parse
import json
import hashlib
import time
import _thread
import datetime
from config import *
import configparser
import uuid
import platform
import time

def date_str_2_timestamp(datestr,pattern):
    """
    将日期字符串转换为时间戳
    """
    obj = datetime.datetime.strptime(datestr,pattern)
    return obj.timestamp()


def load_login_limit(domain,uname):
    """
    加载登录限制
    """
    try:
        resp = http_request("/public_service/strategySettings/get_login_time_limit?domain="+DOMAIN+"&uid="+uname)
        data = json.loads(resp).get("data")
        print("登录时间限制内容",str(data))

        if data:
            login_date_begin = data.get("loginDateBegin")
            login_date_begin_ts = date_str_2_timestamp(login_date_begin,"%Y-%m-%d %H:%M:%S")
            login_date_end = data.get("loginDateEnd")
            login_date_end_ts = date_str_2_timestamp(login_date_end,"%Y-%m-%d %H:%M:%S")

            login_time_begin = data.get("loginTimeBegin")
            login_time_end = data.get("loginTimeEnd")
            print("解析后的时间为：",login_date_begin,login_date_end,login_time_begin,login_time_end)

            # 获取是否将被退出的用户
            whoami = subprocess.check_output(["whoami"])
            whoami = str(whoami,"utf8").strip()
            print("是否将被退出的用户为：",whoami)

            # 判断日期是否在允许范围内
            if time.time() < login_date_begin_ts or time.time() > login_date_end_ts:
                messagebox.showwarning("提示", "您("+uname+")无法在此时段内登录终端：不在日期范围内。\n\n被允许的登录时段为："+login_date_begin.replace("00:00:00","")+"至"+login_date_end.replace("00:00:00","")+"的每天"+login_time_begin+"至"+login_time_end+"。\n\n系统即将自动退出。")
                subprocess.check_output(["/usr/bin/expect", "/opt/hyldap_client/exec/shell/force_logout.sh", SUDO_USER_PASSWD,SUDO_USER_NAME,whoami])
            
            # 判断是否是否在允许范围内
            now_time = datetime.datetime.now().time()
            login_time_begin_array = login_time_begin.split(":")
            login_time_end_array = login_time_end.split(":")
            start_time = datetime.time(int(login_time_begin_array[0]),int(login_time_begin_array[1]))
            end_time = datetime.time(int(login_time_end_array[0]),int(login_time_end_array[1]))
            if now_time < start_time or now_time > end_time:
                messagebox.showwarning("提示", "您("+uname+")无法在此时段内登录终端：不在时间范围内。\n\n被允许的登录时段为："+login_date_begin.replace("00:00:00","")+"至"+login_date_end.replace("00:00:00","")+"的每天"+login_time_begin+"至"+login_time_end+"。\n\n系统即将自动退出。")
                subprocess.check_output(["/usr/bin/expect", "/opt/hyldap_client/exec/shell/force_logout.sh", SUDO_USER_PASSWD,SUDO_USER_NAME,whoami])
        else:
            print("该用户无登录时间限制配置！")
    except Exception as e:
        print("执行登录时间限制出现问题：",str(e))

def get_strategy():
	"""
	获取并执行策略
	"""
	username_obj = get_username()
	username = None
	print("当前登录用户为："+str(username_obj))
	home_dir = os.path.expanduser("~")

	if username_obj.get("type") != "native":

		if username_obj.get("type") == "ldap" or username_obj.get("type") == "ad":
			username = username_obj.get("name")
			posi = username.index("@")
			if posi > 0:
				username = username[0:posi]

		hostname = get_hostname()
		print("当前主机名为:"+hostname)

		print("开始拉取组策略")
		encoded = urllib.parse.urlencode({"domainName":DOMAIN,"hostname":hostname,"hostIP":None,"uid":username,"sysName":get_osname(),"sysVersion":get_sys_version(),"sysArch":platform.uname().machine})
		resp = subprocess.check_output(["curl", ADMIN_SYS_URL+"/public_service/strategySettings/execute?"+encoded])
		resp = str(resp,encoding="utf-8")
		print("组策略接口响应内容："+resp)
		respObj = json.loads(resp)
		if respObj["success"]:
			personalise_shell = respObj.get("data").get("personalise_shell")
			print("shell脚本为:"+personalise_shell)

			if personalise_shell == "" or len(personalise_shell) == 0:
				print("没有发现可执行的脚本！")
			else:
				_path = home_dir+"/.hyldap/"
				if not os.path.exists(_path):
					os.makedirs(_path,0o777)
				file = open(_path+"/hyldap-strategysettings.sh","w")
				file.write(personalise_shell)
				file.close()
				
				os.system("chmod u+wx "+home_dir+"/.hyldap/hyldap-strategysettings.sh")
				subprocess.call(["/bin/bash",home_dir+"/.hyldap/hyldap-strategysettings.sh"])
				os.system('echo "`date +%s`" > '+home_dir+'/.hyldap/last_update_time')
		else:
			print("request error")

	else:
		print("当前登录用户为本地用户，不支持组策略！")


def get_mac_addr():
    macaddr = uuid.UUID(int = uuid.getnode()).hex[-12:]
    return ":".join([macaddr[i:i+2] for i in range(0,11,2)])

def get_sys_version():
    """
    获取系统版本号
    """
    version = subprocess.check_output("cat /etc/.kyinfo | grep milestone=",shell=True)
    version = str(version,encoding="utf8").strip().replace("milestone=","").replace("\r","")
    return version

def get_osname():
    """
    获取系统版本
    """
    try:
        ver = subprocess.check_output("cat /etc/os-release",shell=True)
        ver = str(ver,"utf8").split("\n")[1].replace('"','').split("=")[1]
        return ver
    except Exception as e:
        return ""

def get_host_ip():
    """
    获取当前主机的ip
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        return ip
    finally:
        s.close()

def write_config(item):
    """
    写入配置
    参数示例：{"name":"tom"}
    """
    config = configparser.ConfigParser()
    config["default"] = item
    with open("/opt/hyldap_client/config.ini","w") as configfile:
        config.write(configfile)

def read_config(key):
    """
    读取配置
    """
    try:
        config = configparser.ConfigParser()
        config.read("/opt/hyldap_client/config.ini")
        return config["default"][key]
    except Exception as e:
        print("读取配置时遇到错误：",str(e))
        return None

# write_config({"startup":"None"})
# print(read_config("startup"))

def show_validate_window(func):
    """
    显示管理员认证窗口并验证
    """

    def admin_validate():

        username = admin_name_val.get()
        password = admin_passwd_val.get()
        if not username or not password:
            messagebox.showwarning("提示", "请输入完整的管理员账号！")
            return

        resp = http_request(
            "/public_service/client/validateAdmin?username="+username+"&password="+md5(password.encode("utf8")))
        if resp:
            resp_obj = json.loads(resp)
            if not resp_obj.get("success"):
                messagebox.showwarning("账号错误", "输入的账号验证不通过，请检查！")
            else:
                validate_window.destroy()
                func()

    validate_window = Toplevel()
    validate_window["background"] = "#d7d7d7"
    validate_window.title("请输入管理员账号")
    validate_window.geometry("290x160")
    validate_window.resizable(False, False)
    if os.path.exists("/opt/hyldap_client/exec/assets/logo.png"):
        validate_window.iconphoto(False, PhotoImage(
            file="/opt/hyldap_client/exec/assets/logo.png"))

    admin_name_label = ttk.Label(
        validate_window, text="用户名：")
    admin_name_label.grid(row=1, column=1, sticky=W,
                          padx=(20, 0), pady=(14, 0))
    admin_name_val = StringVar()
    admin_name_ipt = ttk.Entry(
        validate_window, width=22, textvariable=admin_name_val)
    admin_name_ipt.grid(row=1, column=2, sticky=W, padx=(20, 0), pady=(14, 0))

    admin_passwd_label = ttk.Label(
        validate_window, text="密码：")
    admin_passwd_label.grid(row=2, column=1, sticky=W,
                            padx=(20, 0), pady=(14, 0))
    admin_passwd_val = StringVar()
    admin_passwd_ipt = ttk.Entry(
        validate_window, show="*", width=22, textvariable=admin_passwd_val)
    admin_passwd_ipt.grid(row=2, column=2, sticky=W,
                          padx=(20, 0), pady=(14, 0))

    admin_valite_btn = ttk.Button(
        validate_window, text="验证", command=admin_validate)
    admin_valite_btn.grid(row=3, column=1, columnspan=2,
                          sticky=E, padx=(14, 0), pady=(14, 0))


def process_on(title,parent_win):
    """
    显示加载窗口
    """
    global process_window
    process_window = Toplevel()
    process_window["background"] = "#d7d7d7"
    process_window.title(title)
    process_window.resizable(False, False)
    if os.path.exists("/opt/hyldap_client/exec/assets/logo.png"):
        process_window.iconphoto(False, PhotoImage(
            file="/opt/hyldap_client/exec/assets/logo.png"))
    bar = ttk.Progressbar(process_window, orient='horizontal',
                          mode='indeterminate', length=300)
    bar.grid(row=1, column=1, padx=(10, 10), pady=(10, 10))
    bar.start()

    parent_win.withdraw()


def process_off(parent_win):
    """
    隐藏加载窗口
    """
    global process_window

    if process_window:
        process_window.destroy()
    
    parent_win.deiconify()

def clear_invalid_host():
    """
    清理无用的host
    """
    resp = http_request("/public_service/client/clearInvalidHost?domain="+DOMAIN)
    resp_obj = json.loads(resp)
    print(resp_obj)

def get_user_pwd_expir():
    """
    获取当前用户的
    """

    userinfo = get_username()
    uname = userinfo.get("name")
    short_uname = uname
    if uname.index("@") > -1:
        short_uname = uname[0:uname.index("@")]

    resp = http_request("/public_service/client/getUserPwdExpirDate?domain="+DOMAIN+"&uid="+short_uname)
    resp_obj = json.loads(resp)
    expir_time = resp_obj.get("data")[2].get("result").get("krbpasswordexpiration")[0].get("__datetime__")
    expir_time_obj = datetime.datetime.strptime(expir_time, '%Y%m%d%H%M%SZ')
    expir_time_fmt = expir_time_obj.strftime("%Y-%m-%d %H:%M:%S")
    interval = expir_time_obj - datetime.datetime.now()

    return expir_time_fmt,interval

def is_in_domain():
    """
    判断是否已入域
    """
    try:
        subprocess.check_output("id admin@"+DOMAIN, shell=True)
        return True
    except Exception as e:
        return False

def get_hostname():
    """
    获取主机名
    """
    return socket.gethostname()


def md5(text):
    """
    计算md5指纹
    """
    m = hashlib.md5()
    m.update(text)
    return m.hexdigest()


def http_request(uri):
    """
    发送http请求
    """
    try:
        f = urllib.request.urlopen(ADMIN_SYS_URL+uri)
        resp = f.read().decode('utf-8')
        return resp
    except Exception as e:
        messagebox.showerror("错误", "同LDAP平台通信时遇到错误，请检查网络或LDAP平台可用性，明细："+str(e))
        return None

def get_username():
    """
    获取当前用户名
    """
    try:
        name = subprocess.check_output(["klist"])
        name = str(name, encoding="utf8").split("\n")[
            1].strip().split(":")[1].strip().lower()
    except Exception as e:
        name = subprocess.check_output(["whoami"])
        name = str(name, encoding="utf8").strip()

    if "@" not in name:
        return {
            "type": "native",
            "name": name
        }
    else:
        if "intrab.com" in name:
            return {
                "type": "ldap",
                "name": name
            }
        elif "hgtest.com" in name:
            return {
                "type": "ad",
                "name": name
            }
        else:
            return {
                "type": "unknow",
                "name": name
            }
