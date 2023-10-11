import os
import re
import socket
import subprocess
import time
import uuid
import platform
import getpass
import json
import base64
import sys
from config import *

print("------------------开始安装------------------")
print("命令行参数="+str(sys.argv))
hostname_arg = None
if len(sys.argv) == 2:
    hostname_arg = sys.argv[1]
    print("hostname参数="+hostname_arg)

print("即将启动hyldap client安装程序，等待3秒继续...")
time.sleep(3)

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
    

def get_avli_hostname():
    """
    生成有效的hostname
    """

    # 如果命令行已传递参数，则使用
    if hostname_arg:
        print("使用参数中传递的hostname："+hostname_arg)
        return hostname_arg

    # 判断已有的hostname是否可以继续使用
    curr_hostname = socket.gethostname()
    if "."+DOMAIN in curr_hostname:

        # 判断是否包含特殊字符
        short_name = curr_hostname.replace("."+DOMAIN,"")  # 需要移除域名后再判断
        _char = "~!@#$%^&*()+=_<>?/,.[]{}"
        result=True
        for c in _char:
            if c in short_name:
                result = False
                break;
        if result:

            # 判断是否包含大写字母
            if curr_hostname.islower():
                print("当前主机名"+curr_hostname+"可用，继续使用此主机名")
                return curr_hostname
            else:
                print("当前主机名"+curr_hostname+"符合域名规范，且无特殊符号，但是包含大写字母，即将自动转为小写并使用")
                return curr_hostname.lower()
  

    # 都不符合则使用随机名称
    hostname = str(uuid.uuid1())[:6]
    new_hostname = "".join(hostname.split("-"))+"."+DOMAIN
    print("已生成新的hostname："+new_hostname)

    # 检测新hostname的可用性
    dig_result = subprocess.check_output(["dig","@"+DOMAIN_SERVER_IP, "+short", new_hostname])
    dig_result = str(dig_result,encoding="utf8").strip()
    if dig_result: # 如果存在，则会返回ip，因为len=0时表示不存在
        print("hostname检测不通过，因为dns中已存在此名称，dig结果="+new_hostname)
        return get_avli_hostname()
    else:
        print("hostname检测通过")
        return new_hostname


# 如果是更改主机名，则跳过一些步骤
if not hostname_arg:

    # 系统兼容性检测
    print("开始检测系统兼容性")
    print("支持的系统列表：",COMPATIBILITY_VERSION)
    version = subprocess.check_output("cat /etc/.kyinfo | grep milestone=",shell=True)
    version = str(version,encoding="utf8").strip().replace("milestone=","")
    print("您的系统版本：",version)
    if version in COMPATIBILITY_VERSION:
        print("系统兼容性检测结果：通过")
    else:
        print("系统兼容性检测结果：不通过")
        print("注意：您正在未经测试过的系统版本上运行此软件，可能存在兼容性问题，此安装程序仍将继续安装，如安装失败请联系技术支持人员！")



# 设置hostname
print("准备设置hostname")
hostname = get_avli_hostname()
os.system("hostnamectl set-hostname "+hostname)
os.system("hostname "+hostname)
print("hostname设置完成:"+hostname)


# 向服务器汇报安装状态
try:
    line = ['curl','-X','POST',ADMIN_SYS_URL+'/public_service/client/beginInstall','-H','Content-Type: application/json','-d','{"hostname":"'+hostname+'","domain":"'+DOMAIN+'","clientVersion":"'+CLIENT_VERSION+'","arch":"'+platform.uname().machine+'","sysVersion":"'+version+'","user":"'+getpass.getuser()+'","sysName":"'+get_osname()+'","ip":"'+get_host_ip()+'","step":0}']
    print("即将向服务器汇报安装状态：line=",line)
    start_report_result = subprocess.check_output(line)
    start_report_result = str(start_report_result,encoding="utf8")
    print("汇报数据成功，response=",start_report_result)
    install_id = json.loads(start_report_result).get("data")
    print("install_id=",install_id)
except Exception as e:
    print("向服务器汇报状态时遇到错误：",e)



# 禁用/etc/resolv.conf自动更新
print("准备更新/etc/resolv.conf")
os.system('echo "[main]\ndns=none" > /etc/NetworkManager/conf.d/hyldap-dns.conf')

file = open("/etc/resolv.conf","r")
lines = file.readlines()
file.close()
print("原始/etc/resolv.conf内容：")
print(lines)

if "nameserver "+DOMAIN_SERVER_IP+"\n" not in lines:
    new_resolv = []
    for l in lines:
        if l.startswith("option"):
            new_resolv.append(l.replace("rotate"," "))
        elif len(new_resolv)>0 and new_resolv[-1].startswith("option"):
            new_resolv.append("nameserver "+DOMAIN_SERVER_IP+"\n")
        else:
            new_resolv.append(l)

    print("新的/etc/resolv.conf内容已生成：")
    print(new_resolv)

    print("即将更新到/etc/resolv.conf")
    os.system("mv /etc/resolv.conf  /etc/resolv.conf.hyldap.bak")
    new_file = open("/etc/resolv.conf","w")
    new_file.writelines(new_resolv)
    new_file.close()
    print("/etc/resolv.conf更新完成")
else:
    print("/etc/resolv.conf中已包含目标dns，无需更新")


# 在hostname中注册ldap server的地址
print("准备在hosts中注册ldap server的地址")
f = open("/etc/hosts","r")
hostcontent = f.read()
f.close()
if not DOMAIN_SERVER in hostcontent:
    f = open("/etc/hosts", "a")
    # 注意一定要在前面加上\n,否则文件最后一行不是空行的话会导致添加的记录无效
    f.write("\n\n"+DOMAIN_SERVER_IP+"   "+DOMAIN_SERVER+"\n")
    f.close()
    print("/etc/hosts更新完成")
else:
    print("/etc/hosts无需更新，因为配置已存在")

# 配置lightdm.conf文件
exist = os.path.exists("/etc/lightdm/lightdm.conf")
print("是否存在/etc/lightdm/lightdm.conf文件:",exist)
if exist:
    # 判断文件内容是否包含f
    f = open("/etc/lightdm/lightdm.conf", "r")
    content = f.read()
    f.close()
    print("文件内容:", content)

    if not "greeter-show-manual-login" in content:
        f = open("/etc/lightdm/lightdm.conf","a")
        f.write("greeter-show-manual-login=true")
        f.close()
        print("greeter-show-manual-login=true追加完成")
    else:
        print("配置文件已存在选项greeter-show-manual-login，无需配置！")
else:
    f = open("/etc/lightdm/lightdm.conf","w")
    f.writelines([
        "[SeatDefaults]\n",
        "greeter-show-manual-login=true\n"
    ])
    f.close()
    print("/etc/lightdm/lightdm.conf文件创建完成")

# 更新动态链接库文件
print("即将复制 libndr.so.1 到 libndr.so.0")
exist_so0 = os.path.exists("/usr/lib/x86_64-linux-gnu/libndr.so.0")
exist_so1 = os.path.exists("/usr/lib/x86_64-linux-gnu/libndr.so.1")
if not exist_so0 and exist_so1:
    os.system("cp /usr/lib/x86_64-linux-gnu/libndr.so.1  /usr/lib/x86_64-linux-gnu/libndr.so.0")
    print("复制 libndr.so.1 完成")
elif not exist_so0 and not exist_so1:
    print("错误：没有找到libndr.so0和libndr.so1，sssd服务可能无法工作，请确认您的系统版本！")
else:
    print("libndr.so1检测正常，无需处理")


# 卸载旧版本ipaclient
print("开始卸载旧版本ipaclient")
os.system("ipa-client-install --uninstall -U")
print("旧版本ipaclient卸载完成")

# 如果是更改主机名，则跳过一些步骤
if not hostname_arg:
    # 禁用现有apt源
    print("禁用现有apt源")
    os.system("mv /etc/apt/sources.list /etc/apt/sources.list.backup")
    print("禁用apt源完成")

    # 更新apt源，使得自定义apt本地源生效
    print("更新apt源，使得自定义apt本地源生效")
    os.system("apt-get update")
    print("apt更新完成")

    

    # 安装 freeipa
    print("开始安装")
    print("检查环境变量：DEBIAN_FRONTEND=")
    os.system("echo $DEBIAN_FRONTEND")
    os.system("apt-get install -y freeipa-client sssd-tools")

    # 安装依赖
    print("即将安装第三方依赖")
    try:
        os.system("apt-get install -y python3-tk")
        os.system("apt-get install -y expect")
        os.system("apt-get install -y ntpdate")
    except Exception as e:
        print("安装第三方软件包时出现异常")
    print("第三方依赖安装完成")

    # 启用现有源
    print("启用现有源")
    os.system("mv /etc/apt/sources.list.backup /etc/apt/sources.list")
    os.system("rm -rf /etc/apt/sources.list.d/hyldap_client.list")
    os.system("apt-get update")
    print("启用现有源完成")


# NTP时间同步，时间差异太大会导致ldap的登录失败
# ntpdate在海关仓库中包含
try:
    os.system('timedatectl set-timezone "Asia/Shanghai"') 
    os.system("ntpdate  " + DOMAIN_SERVER_IP)
    os.system("hwclock -w") 
    time_out = subprocess.check_output(["timedatectl","status"])
    print("NTP同步完成，并已写入硬件时间， timedatectl status结果：" + str(time_out,"utf8"))
except Exception as e:
    print("同步时间时出现错误（ntp server="+DOMAIN_SERVER_IP+"）") 


# 配置 nsswitch.conf
print("即将变更nsswitch.conf")

nsswitch = open("/etc/nsswitch.conf", "r")
nsswitch_content = nsswitch.read()
nsswitch.close()
print("/etc/nsswitch.conf 文件内容:", nsswitch_content)

# 只有在不存在配置项时候才更新
re_passwd = re.compile(r'passwd:.*files.*sss')
if not re_passwd.search(nsswitch_content):
    os.system("sed -i 's/passwd:\s*files/passwd:  files  sss/g' /etc/nsswitch.conf")

# 只有在不存在配置项时候才更新
re_group = re.compile(r'group:.*files.*sss')
if not re_group.search(nsswitch_content):
    os.system("sed -i 's/group:\s*files/group:  files  sss/g' /etc/nsswitch.conf")

cmd_line = "ipa-client-install --mkhomedir --enable-dns-updates --no-ntp -p admin --password "+DOMAIN_ADMIN_PASSWD+" --domain "+DOMAIN+" --server "+DOMAIN_SERVER+" --force-join --debug --unattended"
print("开始配置freeipa："+cmd_line)
os.system(cmd_line)

# 启用 mkhomedir
print("即将启用mkhomedir")
os.system("rm -rf /usr/share/pam-configs/mkhomedir")
os.system('echo "Name: activate mkhomedir" >> /usr/share/pam-configs/mkhomedir')
os.system('echo "Default: yes" >> /usr/share/pam-configs/mkhomedir')
os.system('echo "Priority: 900" >> /usr/share/pam-configs/mkhomedir')
os.system('echo "Session-Type: Additional" >> /usr/share/pam-configs/mkhomedir')
os.system('echo "Session:" >> /usr/share/pam-configs/mkhomedir')
os.system('echo "required pam_mkhomedir.so umask=0022 skel=/etc/skel" >> /usr/share/pam-configs/mkhomedir')
os.system("pam-auth-update --enable mkhomedir")
print("启用mkhomedir完成")

# 更新krb5配置内容
print("即将更新krb5配置文件")
os.system("sed -i 's/dns_lookup_realm = false/dns_lookup_realm = true/' /etc/krb5.conf")
os.system("sed -i 's/dns_lookup_kdc = false/dns_lookup_kdc = true/' /etc/krb5.conf")
print("krb5配置文件更新完成，最新内容：")
os.system("cat /etc/krb5.conf")

# 更新/etc/sssd/sssd.conf
# 修复AD用户登录后由于默认shell环境错误导致的诸多问题
print("即将更新/etc/sssd/sssd.conf")
os.system("sed -i 's/\[sssd\]/default_shell=\/bin\/bash \\n\\n[sssd]/g' /etc/sssd/sssd.conf")
print("/etc/sssd/sssd.conf中已更新default_shell")

# 重启sssd
try:
    print("即将重启sssd")
    os.system("systemctl restart sssd")
    print("sssd重启完成")
except Exception as e:
    print("启动sssd服务时遇到错误：",e)

# 清空sssd缓存
try:
    print("即将清理sssd缓存")
    os.system("/sbin/sssctl cache-remove -o -p -s -r")
    print("sssd缓存清理完成")
except Exception as e:
    print("清空sssd缓存时出现错误："+str(e))

# 添加开机启动
try:
    print("即将安装系统启动服务")
    systemd_rs = subprocess.check_output("/usr/bin/systemctl enable /etc/systemd/system/hyldapclient.service",shell=True)
    systemd_rs = str(systemd_rs,"utf8")
    print("已安装系统启动服务：",systemd_rs)
except Exception as e:
    print("添加开机启动服务时遇到错误：",e)

try:
    print("即将添加时间同步任务")

    # 检测时间同步任务是否已添加
    print("检测crontab是否已添加时间同步任务")
    crontab = subprocess.check_output("crontab -l",shell=True)
    crontab = str(crontab,"utf8")
    print("crontab内容：",crontab)

    if "synctime.py" not in crontab:
        print("crontab中未添加时间同步任务，即将添加")
        os.system('crontab -l > conf && echo "*/1 * * * *     /bin/python3 /opt/hyldap_client/exec/synctime.py" >> conf && crontab conf && rm -rf conf')
        print("时间同步任务添加成功")
    else:
        print("crontab中已添加时间同步任务，跳过")
except Exception as e:
    print("添加时间同步任务失败："+str(e))

# 向服务器汇报安装状态
try:
    is_success = 0  # 是否安装成功的标志，0成功，1失败
    # 判断freeipa client是否安装成功，判断依据：是否存在sssd配置文件
    exist = os.path.exists("/etc/sssd/sssd.conf")
    if not exist:
        is_success = 1
        print("糟糕,ldap服务没有安装成功")

    if install_id:
        line = ['curl','-X','POST',ADMIN_SYS_URL+'/public_service/client/endInstall','-H','id:'+str(install_id),'-H','result:'+str(is_success),'-F','file=@/opt/hyldap_client/install.upload']
        print("即将向服务器汇报安装状态：line=",line)
        os.system("cp /opt/hyldap_client/install.log /opt/hyldap_client/install.upload")
        end_report_result = subprocess.check_output(line)
        end_report_result = str(end_report_result,encoding="utf8")
        os.remove("/opt/hyldap_client/install.upload")
        print("汇报数据成功，response=",end_report_result)
    else:
        print("没有找到install_id，可能时安装时beginInstall请求没有发送成功！")
except Exception as e :
    print("向服务器汇报信息时遇到错误：",e)


print("------------------安装程序执行结束------------------")
# os.system("reboot")