#!/usr/bin/expect

set timeout 3

set hostname [lindex $argv 0]
set password [lindex $argv 1]
set username [lindex $argv 2]

spawn su $username
expect {
  "*密码*" {
    send "$password\r"
    exp_continue
  }
}

send "sudo hostnamectl set-hostname $hostname \r"
expect {
  "*密码*" {
    send "$password\r"
    exp_continue
  }
}

# 临时变更主机名
send "sudo hostname $hostname"
expect {
  "*密码*" {
    send "$sudo_pass\r"
    exp_continue
  }
}