#!/bin/bash

echo "即将执行目录复制: dependent/`arch` hyldap-client/opt/hyldap_client/dependent/"
cp -r dependent/`arch` hyldap-client/opt/hyldap_client/dependent/
no=$(date '+%Y%m%d')

dpkg -b hyldap-client hyldap_${no}_`arch`.deb

rm -rf hyldap-client/opt/hyldap_client/dependent/`arch`
echo "目录删除完成:hyldap-client/opt/hyldap_client/dependent/`arch`"
