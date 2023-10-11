import subprocess
import http.server
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import _thread
import time
import os
import base64

def get_ldap_user():
	"""
    获取当前登录的LDAP用户信息
    """
	try:
        # 检测是否为ldap登录的用户
        # 使用klist命令检测，只要是ldap或ad信任登录的用户均可以验证
		klist = subprocess.check_output(["klist"])
		print("klist验证结果="+str(klist,encoding="utf-8"))

        # 获取当前登录的用户
		whoami = subprocess.check_output(["whoami"])
		uname= str(whoami,encoding="utf-8").strip()
		print("当前登录用户="+uname)
		if "@" in uname:
			item = uname.split("@")

			rs = {
            	"success": True,
            	"upn": uname,
	    		"name": item[0],
				"type": "ldap"
			}
			b64 = base64.b64encode(json.dumps(rs).encode("ascii"))
			return b64 
		else:
			rs = {
            	"success": True,
            	"upn": uname,
	    		"name": uname,
				"type": "ldap"
			}
			b64 = base64.b64encode(json.dumps(rs).encode("ascii"))
			return b64

	except Exception as e:
		print("程序出现异常或当前登录用户不是有效的LDAP用户:"+str(e))
    
	rs = {
        "success": True,
        "name": str(subprocess.check_output(["whoami"]),"utf-8").strip(),
		"type": "native"
	}
	b64 = base64.b64encode(json.dumps(rs).encode("ascii"))
	return b64

class Resquest(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin','*')
        self.end_headers()

        user = get_ldap_user()
        self.wfile.write(user)
 
def delay_task():
    time.sleep(6)
    os._exit(0)

if __name__ == '__main__':
    _thread.start_new_thread(delay_task,())
    server = HTTPServer(('localhost', 8888), Resquest)
    server.serve_forever()
