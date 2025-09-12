# Charles抓包

## 一、软件概况
1. 去官网下载[1]
2. 软件基本原理：Charles相当于一层代理，所有的请求都是通过通过Charles转发给服务器的，因此可以在软件上获取所有的流量
3. Charles可以篡改请求，也可以篡改响应
4. 破解版见[5] 
5. 目前5.0.1版本的license_key是：`b03793ace3586d03ed`

## 二、抓包HTTP
1. 抓包移动端手机
   - Charles配置：安装证书、配置拦截规则
     - 安装证书
     - 配置拦截规则：`Proxy --> SSL Proxying Settings`，配置代理的拦截对象`host`和`port`，一般配置成`*.443`，代表代理`HTTPS`的请求
     - 配置暴露给手机的端口：`Proxy --> Proxy Settings`，勾选`Enable transparent HTTP proxying`，一般默认是`8888`
     - 目前就已经完成了，接受`8888`端口的信息用于交给Charles拦截，过滤出`HTTPS`的请求，监听所有主机的`HTTPS 443端口`的请求
   - 手机配置
     - 打开Charles的`Help --> SSL Proxying --> install Charles Root Certificate on a Mobile Device or Remote Browser`
     - 打开WIFI配置，开启代理，配置上本手机的所有请求都将打给代理的`ip + port`
2. 导出请求至postman
   - 使用filter过滤请求
   - 右键请求，获取cUrl副本，使用Postman的导入功能

## 三、Map功能



## 四、Rewrite功能


参考资料
1. 官网下载地址：https://www.charlesproxy.com/
2. 抓包详细教程[推荐]：https://blog.csdn.net/only____one/article/details/147902788
3. 将Charles的请求导出到Postman：https://zhuanlan.zhihu.com/p/713603800
4. 完整教程：https://blog.csdn.net/qq_15283475/article/details/127838576
5. 破解教程：https://www.cnblogs.com/neozheng/p/18960535



