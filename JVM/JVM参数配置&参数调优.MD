# JVM参数配置 & JVM参数调优

## 一、各个参数的含义
1. -Xmx：最大堆大小 ｜ -Xms：最小堆大小，堆初始大小
   1. -Xmx默认是物理内存的1/64，-Xms默认是物理内存的1/4。
   2. 目前相对广泛的说法是，-Xmx和-Xms设置为一样的大小，可以避免频繁申请内存，避免导致系统不稳定。
   3. 也有[说法表示](https://blog.csdn.net/Truong/article/details/71126868)，java的垃圾回收器在内存使用达到-Xms的时候才会开始垃圾回收，如果两个值一样，那就意味着当java使用完所有的内存才会进行垃圾回收，内存就会一直不停的涨。
   4. 整合了[网上的说法](https://hello.blog.csdn.net/article/details/108462684)，目前了解到的设置为一致的好处和坏处如下：
      ```text
         好处：JVM在扩大或者缩小内存的时候，会导致应用停顿，为降低延迟同时避免每次垃圾回收完成后jvm重新分配内存，两个值设定为相等的。
         坏处：JVM只会在到达-Xms才会开始垃圾回收，因此内存始终在增长；而且内存越大，JVM进行一次GC的时间就会越久
         综合来说，针对高吞吐量服务（对应的反义词是低时延服务），并不在乎偶尔的停顿；针对低延迟服务，需要保证每次的垃圾回收都尽可能短来保证低时延。
         因此针对高吞吐量服务，或对内存性能要求较高的应用，如12306抢票、秒杀、缓存服务、MQ服务等，可以配置一样的-Xms和-Xmx
      ```
   5. 某互联网中厂技术实战
      1. 如果配置-Xms等于-Xmx
         - 配小了会浪费内存且容易导致JVM OOM
         - 配大了会引发Docker events OOM（容器占用的内存太大导致被操作系统杀死），还不利于资源共享，对系统性能提升极其有限；
           - Docker events OOM：容器占用的内存太大导致容器被操作系统杀死，因此提示我们不能占用太多的操作系统空间
           - 如果一个物理机上有两个Docker容器，都设置一样的-Xms和-Xmx（8G），就导致这两个容器永远都捏着8G内存不放手，造成了资源浪费
      2. Java应用的JVM占用包括哪些方面？
         - 内存占用 = Java Heap(Xmx) + Native Memory 
         - Native Memory中主要包括
           - JNI调用，也就是Native Stack，例如jdbc，gzip
           - 线程占用内存(Xss)
           - DirectByteBuffer，常说的Java堆外
             - DirectByteBuffer‌是Java NIO（New I/O）中的一个关键类，用于在Java程序中高效地使用堆外内存。堆外内存不受Java虚拟机（JVM）的垃圾回收机制管理，因此可以避免因频繁垃圾回收导致的性能下降。DirectByteBuffer通过直接映射到操作系统的内存，减少了数据在Java堆内存和操作系统之间的拷贝开销，特别适用于高性能的I/O操作，如网络编程和文件I/O
           - 管理java heap的状态数据(用于GC)
           - other...
      3. Docker内的Java应用出现Docker events OOM可以从以下方面入手：（以4G容器实例为例，正常情况Xmx3G，Native Memory正常需要300M）
         - Xmx设置错误,heap大于3.7G时，整体占用超过4G ———— 处理的方法是设置合理 -Xmx -Xms -Xmn
         - 线程数持续增加，线程占用内存超过1G，整体超过4G ———— 处理的方式是检查代码
         - DirectByteBuffer超过1G，整体占用超过4G ———— 建议查看堆外预留内存是否设置合理，如果不合理可以通过调整JVM配置来解决
Native Stack内存占用过大超过1G,例如gzip流未close，整体超过4G，处理的方式是检查代码
2. -XX:ZUncommit：ZGC垃圾回收算法是否向操作系统归还内存
   1. 从JDK13开始ZGC收集器就已经支持归还内存，默认是true，也就是归还；



## 二、参数配置一键解决方案
1. 支付宝平台提供了页面可供一键生成参数配置，[JVM参数配置](https://render.alipay.com/p/s/jvm-generate/JvmGenerate)。【仅支持到JDK8】
2. HeapDump平台提供了页面可供一键生成参数配置，[JVM参数配置](https://opts.share.heapdump.cn/result/generate/1zqgg)。【仅支持到JDK8】




