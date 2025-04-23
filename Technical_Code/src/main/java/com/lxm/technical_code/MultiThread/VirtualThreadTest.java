package com.lxm.technical_code.MultiThread;

/**
 * @Author: liuxianming
 * @Date: 2025/04/23 17:33:26
 */
public class VirtualThreadTest {

    public static void main(String[] args) {
        Thread.startVirtualThread(new Runnable() {
            @Override
            public void run() {
                int a = 1;
                int b = 2;
                int c = 3;
                System.out.println(a + b + c);
            }
        }).start();
    }


}
