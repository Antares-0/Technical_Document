# MySQL数据库一些架构问题



## 一、MySQL为什么不能提供高并发？
1. 锁机制 ：MySQL在查询的时候会加锁，不论是行锁或者是表锁，会出现大量的阻塞和等待，影响系统的并发能力
2. 事务隔离级别：MySQL支持不同的事务隔离级别，不同的隔离级别下能够承担的请求量也是不一样的
3. 通信机制：MySQL需要通过TCP三次握手建立通信，这也是会使用一部分时间的
4. 硬件限制：计算资源有限，要交互磁盘

## 二、MySQL支持高并发操作的一些策略（索引、缓存、分库分表、读写分离）
1. 采用一些索引，加速查询，减少等待和锁表
2. 加缓存，拒绝请求直接查询MySQL
3. 读写分离：读请求给Salve，写请求给Master，主从之间使用同步机制  
   ![](./fig/MySQLMS.png)
4. 数据归档：因为大部分的业务具有热尾效应，可以将之前的历史数据保存到另外的一张表，这样来降低数据库的表容量，从而提高查询性能；成本小，比常提的分库分表具有更优秀的效果，而且不容易产生分布式问题
5. 分库分表：分片查询，一个数据库实例撑不住，就将并发请求分散到多个实例中
   1. 数据库大，就分表
   2. 并发高，就分库，多加一些MySQL实例


## 三、MySQL存在一些大表问题



## 四、解决方案



## 五、MySQL和ES的数据同步问题



## 六、跨页问题


## 七、MySQL的死锁问题
1. MySQL为什么会出现死锁？`select * from order_info where id = 212358736 for update`
   - 资源竞争：事务A对记录X加锁，事务B对记录Y加锁，随后两者同时请求对方已经加锁的记录
   - 申请锁的顺序不一致：事务A先申请1再申请2，事务B先申请2再申请1
   - 锁升级：MySQL中的锁分为共享锁和排他锁，如果是两个线程分别拥有共享锁，其中一个线程的锁面临升级的问题时，会与持有共享锁的另一个线程发生冲突，导致死锁
2. 怎样避免MySQL出现死锁？
   - 调整事务的执行顺序
   - 优化索引和查询
   - 用较低的隔离级别
   - 避免大事务

## 八、MySQL的隔离级别




## 九、MySQL


参考资料
1. https://cloud.tencent.com/developer/article/1683394