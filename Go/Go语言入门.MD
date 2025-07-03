# Go语言入门（Java程序员视角）


## 一、Go语言核心优势及环境配置
1. 核心优势
   1. go语言的核心优势就是高并发场景
      - 使用go开发的各种应用比如：Docker、k8s、TiDB、InfluxDB 
      - 使用C++开发的应用比如：MySQL、MongoDB 
      - 使用Java开发的应用比如：Hadoop、Spring
   2. 编译型语言、解释型语言
      - 编译型语言：通过预编译转变为机器码，性能较高，Java、Go、C++
      - 解释型语言：逐行解释代码，性能较低，Python、JavaScript
   3. 
2. 环境配置
   1. 去[链接](https://go.dev/dl/)下载go的开发包，相当于JDK，安装后使用`go version`确认
   2. 在goland中配置该go开发包
3. Go语言的运行
   1. 运行main.go文件
      ```bash
      # 方式一 直接运行
      go run main.go
      # 方式二 两步运行
      go build main.go # 会生成main可执行文件 
      ./main # 直接执行
      ```
   2. 
   
4. 



## 二、Go语言特性语法
1. 



## 三、Go语言开发工具包
1. Go mod是什么？
   1. go mod是go官方推出的包管理工具，用于管理项目依赖，相当于java的maven和gradle
   2. go mod生成了两个文件
      1. go.mod 用于记录依赖
      2. go.sum 用于校验文件
   3. go mod对应的老版本是GOPATH
      - GOPATH配置模式：选择一个目录作为Go的工作空间，并使得GOPATH环境变量指向它
   4. Go mod常用命令：
      ```bash
      
      # 自动下载依赖
      go mod tidy
      ```
   5. 
2. 


参考资料：
1. 解决goland无法解析git类引入的问题：https://blog.csdn.net/qq_38018994/article/details/125745076
2. 
