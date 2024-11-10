# Java多线程


## 一、synchronized关键字
1. synchronized加在一个static方法上，是对这个类进行加锁；synchronized加在一个普通方法上，是对新建出来的这个对象加锁
2. synchronized关键字的底层原理





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




## 六、volatile关键字
1. 






