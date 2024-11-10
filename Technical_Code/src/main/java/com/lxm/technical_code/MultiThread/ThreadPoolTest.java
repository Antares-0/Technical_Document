package com.lxm.technical_code.MultiThread;

import java.util.concurrent.*;

public class ThreadPoolTest {
    public static void main(String[] args) {
        // 查看源码可以发现，这种情况下设置最大线程数为0，会报错
        // ThreadPoolExecutor threadPoolExecutor = new ThreadPoolExecutor(0, 0, 200, TimeUnit.MILLISECONDS, new LinkedBlockingQueue<>(10));
        // Exception in thread "main" java.lang.IllegalArgumentException
        //	at java.util.concurrent.ThreadPoolExecutor.<init>(ThreadPoolExecutor.java:1314)
        //	at java.util.concurrent.ThreadPoolExecutor.<init>(ThreadPoolExecutor.java:1202)
        //	at com.lxm.technical_code.MultiThread.ThreadPoolTest.main(ThreadPoolTest.java:8)
        ThreadPoolExecutor threadPoolExecutor = new ThreadPoolExecutor(0, 5, 200, TimeUnit.MILLISECONDS, new LinkedBlockingQueue<>(10));
        threadPoolExecutor.execute(() -> {
            System.out.println("hello");
        });
        // 输出hello，还是创建了非核心线程进行处理
    }
}
