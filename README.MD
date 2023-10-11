# LDAP客户端

## 添加新的依赖（参考：https://unix.stackexchange.com/questions/87130/how-to-quickly-create-a-local-apt-repository-for-random-packages-using-a-debian）
- 清空apt的缓存目录：
  sudo rm -rf /var/cache/apt/archives/*
- 安装需要的软件：
  sudo apt-get install xxx
- 生成 package
  进入依赖包的目录下执行：
  dpkg-scanpackages . | gzip > Packages.gz

## 依赖安装
apt-get install python3-tk
pips install pillow

## 不同平台下打包
- 更改 /DEBIAN/control 中的架构名称
- 更改 /etc/apt/sources.list.d/hyldap_client.list 下的库加载路径

## 不同域（控）下打包
- 更改 /opt/installer.py 中的域控配置

## 打包新版本
- 更改 /DEBIAN/control 中的版本号
- 更改 /opt/hyldap_client/application.py 中的版本号和发布日期

## 常见问题
- 安装后发现非管理员用户打不开系统图标：
  请确认是否在deb源代码中的py文件有正确的权限，否则会导致其他用户无法打开此文件。可以直接复制正确的文件，然后替换内容即可解决此问题。
