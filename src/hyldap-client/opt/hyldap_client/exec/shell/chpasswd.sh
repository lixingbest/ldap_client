#!/usr/bin/expect

set timeout 6

set oldpasswd [lindex $argv 0]
set newpasswd [lindex $argv 1]

spawn passwd
expect {
  "当前*密码：" {
    send "$oldpasswd\r"
    exp_continue
  }
  "Current*Password:" {
    send "$oldpasswd\r"
    exp_continue
  }
  "新的*密码：" {
    send "$newpasswd\r"
    exp_continue
  }
  "重新输入新的*密码：" {
    send "$newpasswd\r"
    exp_continue
  }
}
