#!/usr/bin/expect

set timeout 3

set sudo_pass [lindex $argv 0]
set sudo_name [lindex $argv 1]

spawn su $sudo_name
expect {
  "*密码*" {
    send "$sudo_pass\r"
    exp_continue
  }
}

set timeout 30

send "sudo ipa-client-install --uninstall -U \r"
expect {
  "*密码*" {
    send "$sudo_pass\r"
    exp_continue
  }
}
