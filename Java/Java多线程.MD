# Java多线程


## 一、synchronized关键字
1. synchronized使用规则：
   - 修饰实例方法（非静态方法）：作用于当前的实例对象
   - 修饰静态方法：作用于当前的类对象，加锁
   - 修饰代码块：指定加锁对象，对给定对象加锁，进入同步代码前要获得当前类对象的锁  
   `synchronized加在一个static方法上，是对这个类进行加锁；synchronized加在一个普通方法上，是对新建出来的这个对象加锁。`
2. synchronized关键字的底层原理
   - JVM中，对象在内存中的布局分为3块区域，对象头（存储一些数据）、实例数据、对齐填充（仅仅为了字节对齐）
   - 对象头大小一般是两个字节，如果是数组对象是三个字节；
     - Mark Word：存储对象的hashCode、锁信息或分代年龄或GC标志等信息；这个标志是可变的
       ```txt
       无锁状态：30bit（对象HashCode）      +  2bit锁标志位（01）
       偏向锁：  23bit 线程ID + 2bit Epoch + 4bit 对象分代年龄 + 1bit 是否是偏向锁 + 2bit 锁标志位（01）
       轻量级锁：25bit 指向栈中锁记录的指针   +  2bit锁标志位（01）
       重量级锁：25bit 指向互斥量的指针      +  2bit锁标志位（10）
       GC标记：  30bit空                  +  2bit锁标志位（11）
       ```
     - Class Metadata Address：类型指针指向对象的类元数据，JVM通过这个指针确定该对象是哪个类的实例。
   - JVM中每个对象都存在一个相对应的监视器Monitor（也叫管程），Monitor的底层实现上是通过C++编写的ObjectMonitor来实现的，这个对象有三个关键结构：
     - count：记录进入锁的次数
     - WaitSet：处于等待状态的线程集合
     - EntryList：处于等待锁Block状态的线程，会被加入到该列表  
     ![monitor](./fig/synchronized01.png)
   - synchronized同步到类上的形式
     - 通过monitorEnter和monitorExit指令实现对监视器的访问
   - synchronized同步到方法上的底层原理
     - 通过标识该方法是同步方法（ACC_SYNCHRONIZED）来实现每次调用时先访问监视器monitor
   - synchronized的可重入性：
3. JVM对synchronized的优化
   - synchronized的锁优化主要基于统计学原理，在大部分情况下锁的对象往往只被一个线程享有，根本不存在并发问题，基于统计学数据为了提高效率，有了如下的优化方案
   - 【优化一】synchronized具有四种状态：无锁、偏向锁、轻量级锁和重量级锁；升级是单向的
     - 无锁：没有线程访问对象的时候，是无锁状态
     - 偏向锁：“大部分情况下都是一个线程多次访问一个锁对象”，当只有一个线程在访问对象的时候，是偏向锁的状态，为了降低同一个线程获取锁的代价而引入偏向锁。
     - 轻量级锁：“对绝大部分的锁，在整个同步周期内不存在竞争”，换句话说，在同一时间同时访问一个锁的情况不常见，适用于“线程交替执行”的场景
     - 自旋锁：“大多情况下线程持有锁的时间都不会太长”，在锁膨胀到重量级锁之前，会要求其他线程进行自旋，如果自旋结束后可以获得锁，那就获取也就没有必要膨胀到重量级锁了。
     - 重量级锁：monitor监视器的应用
   - 【优化二】synchronized的锁消除
     - 在某些场景下锁不可能生效，JVM会自动消除锁，比如：
       ```java
         public void add(String str1, String str2) {
             // 这个stringBuffer就属于不可能被共享的对象，JVM会自动消除内部的锁
             // 不会出现多个线程同时访问这个变量
             StringBuffer stringBuffer = new StringBuffer();
             stringBuffer.append(str1).append(str2);
         }
       ```





## 二、线程回收的流程





## 三、自己实现一个线程池




## 四、线程池
1. 线程池执行任务的过程
   1. 提交一个新的任务到线程池，线程池会检查正在运行的线程数是否少于 corePoolSize（核心线程数），如果不足，则创建一个新线程来执行任务。  
      <font color='yellow'>当线程数小于核心线程数时，即使现有的线程空闲，线程池也会优先创建新线程来处理任务，而不是直接交给现有的线程处理。</font>
   2. 如果正在运行的线程数大于或等于 corePoolSize，则将任务加入到队列中。
   3. 如果无法将任务加入到队列（队列已满），则在满足条件的情况下创建 maximumPoolSize（最大线程数）大小的额外线程来处理任务。
   4. 如果创建了最大数量的线程且队列已满，则执行拒绝策略（RejectedExecutionHandler），如默认的策略是抛出 RejectedExecutionException 异常。
2. 当核心线程数配置为0的时候会发生什么？
   1. 结论：当线程池的核心线程数设置为0时，任务仍然会被丢入任务队列。如果当前工作线程数量为0，<font color='yellow'>线程池会创建非核心线程来执行任务</font>。
   2. 源码：
   ```java
   public void execute(Runnable command) {
      if (command == null)
          throw new NullPointerException();
      int c = ctl.get();
      // 如果当前工作线程的线程数量少于核心线程数目，不管这个线程是不是空闲的，都要创建新的线程工作
      if (workerCountOf(c) < corePoolSize) {
          if (addWorker(command, true))
              return;
          c = ctl.get();
      }
      if (isRunning(c) && workQueue.offer(command)) {
          int recheck = ctl.get();
          if (! isRunning(recheck) && remove(command))
              reject(command);
          // 如果新的目前工作线程数为0，新建一个非核心线程来执行
          else if (workerCountOf(recheck) == 0)
              // addWorker的第二个参数表示是否是核心线程
              addWorker(null, false);
      }
      else if (!addWorker(command, false))
          reject(command);
   }
   ```
   3. 扩展：如果核心线程和非核心线程数都为0，会报错——参数不合法异常。
   ```java
   public ThreadPoolExecutor(int corePoolSize,
                              int maximumPoolSize,
                              long keepAliveTime,
                              TimeUnit unit,
                              BlockingQueue<Runnable> workQueue,
                              ThreadFactory threadFactory,
                              RejectedExecutionHandler handler) {
        if (corePoolSize < 0 ||
            maximumPoolSize <= 0 || // 最大线程数 == 0，抛出异常
            maximumPoolSize < corePoolSize ||
            keepAliveTime < 0)
            // 抛出异常
            throw new IllegalArgumentException();
        if (workQueue == null || threadFactory == null || handler == null)
            throw new NullPointerException();
        this.acc = System.getSecurityManager() == null ?
                null :
                AccessController.getContext();
        this.corePoolSize = corePoolSize;
        this.maximumPoolSize = maximumPoolSize;
        this.workQueue = workQueue;
        this.keepAliveTime = unit.toNanos(keepAliveTime);
        this.threadFactory = threadFactory;
        this.handler = handler;
   }
   ```
3. 线程池的核心参数
   1. corePoolSize——线程池核心线程数  
      也可以理解为线程池维护的最小线程数量，核心线程创建后不会被回收。大于核心线程数的线程，在空闲时间超过 keepAliveTime 后会被回收；
   2. maximumPoolSize——线程池最大线程数  
      线程池允许创建的最大线程数；（包括核心线程池数量），也就是非核心线程+核心线程数量总和。
   3. keepAliveTime——非核心线程线程存活时间  
      当一个可被回收的线程的空闲时间大于 keepAliveTime ，就会被回收。
   4. TimeUnit——时间单位  
      参数keepAliveTime的时间单位。
   5. BlockingQueue——阻塞工作队列  
      阻塞队列不要使用默认值，默认的`new LinkedBlockingQueue()`相当于将队列长度设置为`Integer.MAX_VALUE`，也就是说线程池中的工作线程将永远稳定在核心线程数这个水平上，任务量增加的时候响应时间会陡增。  
      它用于存储等待执行的任务，如果有一些任务需要被执行，但是当前核心线程数以满且全部都在运行时期，则将当前任务存储在阻塞工作队列中，等核心线程执行完后，队列中的任务会进行分配执行。它仅仅用来存放被 execute() 方法提交的Runnable任务。工作队列实现了BlockingQueue接口。
   6. ThreadFactory——线程工厂  
      用于创建线程，以及自定义线程名称，需要实现ThreadFactory接口；
   7. RejectedExecutionHandler——拒绝策略
4. 线程池的参数配置需要考虑哪些因素？
   1. 业务类型是IO密集型还是CPU密集型？——决定核心线程数的配置  
      1. 对于IO密集型，可以配置核心线程数为`CPU核心数目的2倍或者更多`
      2. 对于CPU密集型，一般是`CPU核数 + 1`
   2. 资源上限——决定最大线程数  
      资源的上限决定了最大线程数的配置
   3. 业务类型——决定存活时间、拒绝策略  
      业务是快速响应类型，一般会配置的存活时间比较短  
      拒绝策略也可以根据响应的做出配置  
   4. 资源有限场景——决定阻塞队列的配置  
      资源有限的场景，可以使用有大小的阻塞队列，保证资源不被耗尽  

## 五、ReentrantLock可重入锁
1. ReentrantLock的使用是显式的，因此照比synchronized的使用更加灵活。
   1. 
2. AQS抽象式队列同步器
   
3. 



## 六、volatile关键字
1. volatile是Java虚拟机提供的轻量级的同步机制。  
   volatile关键字有如下两个作用：
   - 保证被volatile修饰的共享变量对所有线程总数可见的，也就是当一个线程修改了一个被volatile修饰共享变量的值，新值总可以被其他线程立即得知。 
   - 禁止指令重排序优化。
2. JMM是怎样保证volatile的可见性呢？在写一个volatile变量的时候，JMM会把线程对应的工作内存中的共享变量值刷新到主内存中，当读取一个volatile变量时，JMM会把该线程中对应的工作线程置为无效，那么该线程将只能从主内存中重新读取共享变量。
3. JMM是怎样保证volatile禁止重排优化的呢？volatile关键字另一个作用就是禁止指令重排优化，从而避免多线程环境下程序出现乱序执行的现象。   
   内存屏障，又称内存栅栏，是一个CPU指令，它的作用有两个，一是保证特定操作的执行顺序，二是保证某些变量的内存可见性（利用该特性实现volatile的内存可见性）。   
   由于编译器和处理器都能执行指令重排优化。如果在指令间插入一条Memory Barrier则会告诉编译器和CPU，不管什么指令都不能和这条Memory Barrier指令重排序，也就是说通过插入内存屏障禁止在内存屏障前后的指令执行重排序优化。  
   Memory Barrier的另外一个作用是强制刷出各种CPU的缓存数据，因此任何CPU上的线程都能读取到这些数据的最新版本。总之，volatile变量正是通过内存屏障实现其在内存中的语义，即可见性和禁止重排优化。   
4. volatile的关键应用（单例模式）：
   ```java
    public static DoubleCheckLock {
        // 使用 volatile 禁止指令重排
        private volatile static DoubleCheckLock instance;
    
        public static DoubleCheckLock getInstance() {
            // 第一次检测
            if (instance == null){
                // 同步
                synchronized (DoubleCheckLock.class) {
                    if (instance == null) {
                        // 多线程环境下可能会出现问题的地方
                        // 正常创建对象分配空间的流程是：
                        // memory = allocate();  // 1.分配对象内存空间
                        // instance(memory);     // 2.初始化对象
                        // instance = memory;    // 3.设置instance指向刚分配的内存地址，此时instance != null
                        // 出现重排：
                        // memory = allocate();  // 1.分配对象内存空间
                        // instance = memory;    // 3.设置instance指向刚分配的内存地址，此时instance != null，但是对象还没有初始化完成！
                        // instance(memory);     // 2.初始化对象
                        // 重排的情况下，对象还没有被初始化就已经返回了
                        instance = new DoubleCheckLock();
                    }
                }
            }
            return instance;
        }
    }
   ```
5. volatile关键字的总结：
   - 编译器在编译对volatile关键字修饰的变量进行读写的时候，会在指令中插入内存屏障
   - 内存屏障保证了每次写数据后，可以将数据直接刷到主内存中；同时内存屏障保证了禁止重排序
6. 扩展：volatile关键字的内存屏障类型（LoadStore、StoreStore、StoreLoad、LoadLoad）


## 七、CAS操作
1. 【注意】CAS操作是原子的，因为在CPU层面提供了操作原语，保证对数据Compare and Swap是原子性操作。




参考资料：
1. volatile关键字的内存屏障类型：https://blog.csdn.net/q1372302825/article/details/139282172
2. synchronized关键字：https://blog.csdn.net/javazejian/article/details/72828483
3. 
