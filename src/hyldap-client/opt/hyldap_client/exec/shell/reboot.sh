#!/usr/bin/expect

set timeout 3

set password [lindex $argv 0]
set username [lindex $argv 1]

spawn su $username
expect {
  "*密码*" {
    send "$password\r"
    exp_continue
  }
}

send "sudo reboot \r"
expect {
  "*密码*" {
    send "$password\r"
    exp_continue
  }
}
