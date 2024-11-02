package easyProject.MultiThread;


import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.locks.LockSupport;

public class MyLockSupport {

    private static AtomicInteger num = new AtomicInteger(0);

    public static void main(String[] args) throws InterruptedException {
        Thread t1 = new Thread(() -> {
            while (true) {
                System.out.println(num + "----" + Thread.currentThread().getName());
                num.incrementAndGet();
                LockSupport.park();
            }
        }, "t1");

        Thread t2 = new Thread(() -> {
            while (true) {
                System.out.println(num + "----" + Thread.currentThread().getName());
                num.incrementAndGet();
                LockSupport.unpark(t1);
            }
        }, "t2");

        Thread t3 = new Thread(() -> {
            while (true) {

            }
        }, "t3");

        t1.start();
        Thread.sleep(20);
        t2.start();
        Thread.sleep(20);
        t3.start();
        Thread.sleep(20);

    }
}
