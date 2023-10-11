#!/usr/bin/expect

set timeout 3

set password [lindex $argv 0]
set username [lindex $argv 1]
set target_uname [lindex $argv 2]

spawn su $username
expect {
  "*密码*" {
    send "$password\r"
    exp_continue
  }
}

send "sudo pkill -KILL -u  $target_uname\r"
expect {
  "*密码*" {
    send "$password\r"
    exp_continue
  }
}
