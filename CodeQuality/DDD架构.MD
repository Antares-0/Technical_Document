# DDD架构

## 一、DDD架构相关
1. DDD（Domain-Driven Design）架构，领域驱动设计。
2. 敏捷实践中的重构、测试驱动设计及持续集成可以对付各种混乱问题。重构——保持行为不变的代码改善清除了不协调的局部设计，测试驱动设计确保对系统的更改不会导致系统丢失或破坏现有功能，持续集成则为团队提供了同一代码库。

## 二、COLA架构——DDD的具体实践
1. COLA架构：是DDD范式的一种实现
2. COLA架构的目录结构
   - Adapter层：程序入口，相当于MVC中的controller；具体可以包含以下几种
     - RPC接口调用：通过RPC实现
     - 硬件调用：wireless设备调用
     - 前端调用：前端的页面展示等
     - MQ：消息队列的消息接收可以算作Adapter或者Application
   - Application层：主要负责获取输入，组装上下文，参数校验，调用领域层做业务处理，如果需要的话，发送消息通知等。层次是开放的，应用层也可以绕过领域层，直接访问基础实施层；
   - Domain层：主要是封装了核心业务逻辑，并通过领域服务（Domain Service）和领域对象（Domain Entity）的方法对App层提供业务实体和业务逻辑计算。领域是应用的核心，不依赖任何其他层次；
   - Infrastructure层：主要负责技术细节问题的处理，比如数据库的CRUD、搜索引擎、文件系统、分布式服务的RPC等。此外，领域防腐的重任也落在这里，外部依赖需要通过gateway的转义处理，才能被上面的Application层和Domain层使用。
3. COLA项目架构的基本样式
   
   ![COLA](./fig/COLA.png)

   |       层次       |     包名      |            功能             | 是否必须 |
   |:--------------:|:-----------:|:-------------------------:|:----:|
   |    Adapter     |     web     |         处理前端相关的请求         |  否   |
   |    Adapter     |     rpc     |       处理rpc框架相关的请求        |  否   |
   |    Adapter     |  wireless   |         处理硬件相关请求          |  否   |
   |                |             |                           |      | 
   |  Application   |  executor   | 处理request，包括command和query |  是   |
   |  Application   |  consumer   |        处理外部message        |  否   |
   |  Application   |  scheduler  |          处理定时任务           |  否   |
   |                |             |                           |      |
   |     Domain     |    model    |           领域模型            |  否   |
   |     Domain     |   ability   |   领域能力，包括DomainService    |  否   |
   |     Domain     |   gateway   |         领域网关，解耦利器         |  是   |
   |                |             |                           |      |
   | Infrastructure | gatewayImpl |           网关实现            |  是   |
   | Infrastructure |   mapper    |           数据库映射           |  否   |
   | Infrastructure |   config    |           配置信息            |  否   |
   |                |             |                           |      |
   |   Client SDK   |     api     |        服务对外透出的API         |  是   |
   |   Client SDK   |     dto     |         服务对外的DTO          |  是   |







参考文档：
1. DDD架构【美团技术团队】：https://tech.meituan.com/2017/12/22/ddd-in-practice.html
2. DDD架构：https://blog.csdn.net/qq_41889508/article/details/124907312
3. COLA架构：https://zhuanlan.zhihu.com/p/656764423
4. COLA架构：https://www.cnblogs.com/makai/p/14240924.html