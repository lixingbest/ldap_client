#!/bin/bash

# 注意：
# 之所以没有使用 echo 输出，是因为当控制台登录后会看到内容，不太友好。

# 复制自启动文件，用于自动执行策略
if [ "`whoami`" != "uer" ] && [ "`whoami`" != "jn4300" ]  && [ "`whoami`" != "user" ] && [ "`whoami`" != "root" ];then 
    mkdir -p ~/.config/autostart/
    cp -r /opt/hyldap_client/settings/autostart/ ~/.config/
    sed -i "s|HOMEDIR|"$HOME"|g" ~/.config/autostart/hyldap.desktop

    mkdir -p ~/.local/share/applications/
    cp -r /opt/hyldap_client/settings/hyldap.desktop  ~/.local/share/applications/
    cp -u /opt/hyldap_client/settings/mimeapps.list  ~/.config/ 
    cp ~/.config/mimeapps.list ~/.config/mimeapps.list.bak
    sed -i "s|\[Added Associations\]|x-scheme-handler/hyldap=hyldap.desktop\n\[Added Associations\]|g" ~/.config/mimeapps.list
    update-desktop-database ~/.local/share/applications
fi

/usr/bin/bash  /opt/hyldap_client/exec/shell/copy_desktop_icon.sh &