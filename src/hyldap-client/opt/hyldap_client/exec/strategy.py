import time
from config import *
from common import *

#加载策略执行周期
resp = http_request("/public_service/strategySettings/get_interval")
STRATEGY_PERIOD = int(json.loads(resp).get("data").get("value"))
print("策略执行周期：",str(STRATEGY_PERIOD))

while True:
	# 不能因为错误而终止循环
	try:
		print("准时拉取最新策略")
		get_strategy()
		print("最新策略执行完成")
		time.sleep(STRATEGY_PERIOD*60)
	except Exception as e:
		print("执行组策略时出现错误："+str(e))
		time.sleep(STRATEGY_PERIOD*60)