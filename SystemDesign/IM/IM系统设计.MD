# IM系统设计

## 一、IM系统
1. IM系统，即instant messaging system，即时消息系统
2. 已知产品包括，微信WeChat和电报Telegram，也包括WhatsApp


## 二、IM系统设计思路（参考system-design）
1. 需求分析 Requirements
   1. 功能需求：支持私聊、群聊和文件分享
   2. 技术需求：低延迟且高可用、稳定且有效
   3. 扩展功能：消息发送、送达、已读记录；显示最后登陆时间；推送新消息的通知
2. 估算与限制条件 Estimation and Constraints
   1. 消息体量估算：日活 * 每人发消息的数量，其中 x% 的消息是多媒体消息
   2. 存储估算：每条文本消息 x Byte，多媒体消息图片平均每张 y Byte
   3. 带宽估算：存储成本 / 时间
3. 数据模型设计 Data model design

   ![系统设计](./fig/IMSystem.png)
   1. 数据依赖设计
      1. users_groups表：记录群组和用户的映射关系
      2. users表：记录用户基础信息
      3. users_chats表：记录用户有哪些会话
      4. chats表：记录会话的基本信息，群聊、单聊和临时会话都算作一种会话，会话与消息强相关
      5. messages表：记录消息
      6. groups表：记录群组基本信息
   2. 技术选型
      1. 常用数据库：MySQL、Redis
      2. 不常用的数据库：TiDB、postgresql、Apache Cassandra、memcache
4. 接口设计 API design
   1. 获取会话列表
   2. 获取会话内容
   3. 发送消息
   4. 退出会话、加入会话
5. 高级设计 High-level design
   1. 微服务架构设计：
      1. 服务分类：用户服务、会话服务、通知服务、在线状态服务、媒体服务
      2. 内部服务调用 & 服务发现
   2. 实时消息设计
      1. 拉取消息模型：类似长轮训，定期请求服务器是否有新信息
      2. 推送消息模型：客户端和设备之间建立长链接，例如web socket甚至是sse
      3. 拉取消息模型会造成更多的资源浪费，因为请求会疯狂涌入服务，而大部分时间获取的消息都是空的；推送消息模型会更好
   3. 最后登陆时间
      1. 设备终端每隔一段时间进行上报（类似ping命令），结合redis和memcache的user对应的key，占用空间更小
      2. 跟踪用户最后一次操作，用作最近登陆时间，也可以实现该功能
   4. 通知功能
6. 细节设计 Detailed design
7. 瓶颈问题分析与解决 Identify and resolve bottlenecks



## 三、IM系统设计实战（参考某互联网公司设计实现）
1. 架构设计
   1. 
2. 


参考资料：
1. system-design：https://github.com/karanpratapsingh/system-design?tab=readme-ov-file#whatsapp

