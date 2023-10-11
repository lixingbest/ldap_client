#!/usr/bin/expect

set timeout 3

set hostname [lindex $argv 0]
set sudo_pass [lindex $argv 1]
set sudo_name [lindex $argv 2]

spawn su $sudo_name
expect {
  "*密码*" {
    send "$sudo_pass\r"
    exp_continue
  }
}

# 注意超时时间需要设置为-1，否则按照时间太长expect会自动终止
set timeout 600

send "sudo /bin/python3 /opt/hyldap_client/exec/installer.py $hostname \r"
expect {
  "*密码*" {
    send "$sudo_pass\r"
    exp_continue
  }
}