#!/usr/bin/expect

set timeout 3

set password [lindex $argv 0]
set username [lindex $argv 1]
set ldap_ip [lindex $argv 2]

spawn su user
expect {
  "*密码*" {
    send "$password\r"
    exp_continue
  }
}

send "sudo timedatectl set-timezone 'Asia/Shanghai'\r"
expect {
  "*密码*" {
    send "$password\r"
    exp_continue
  }
}

send "sudo ntpdate $ldap_ip\r"
expect {
  "*密码*" {
    send "$password\r"
    exp_continue
  }
}

send "sudo hwclock -w\r"
expect {
  "*密码*" {
    send "$password\r"
    exp_continue
  }
}
