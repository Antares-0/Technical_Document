package com.lxm.technical_code.ThreadLocal;

public class MyThreadLocalTest {
    public static void main(String[] args) {
        ThreadLocal<String> threadLocal = new ThreadLocal<>();
        threadLocal.set("test");

        new Thread(() -> {
            String s = threadLocal.get();
            System.out.println(s + Thread.currentThread().getName());
        }, "tha").start();
        System.out.println(threadLocal.get());
    }
}
