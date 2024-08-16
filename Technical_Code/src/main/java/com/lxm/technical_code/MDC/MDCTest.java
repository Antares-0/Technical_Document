package com.lxm.technical_code.MDC;


import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;

/**
 * @Author : Liu Xianming
 * @Date: 2024-08-16
 * @Description: 该类用于测试slf4j中的MDC的使用
 */
public class MDCTest {

    private static final Logger log = LoggerFactory.getLogger(MDCTest.class);

    public static void main(String[] args) {
        log.info("MDCTest");
        MDC.put("myTestKey", "myTestValue");
        System.out.println(MDC.get("myTestKey"));
        System.out.println(args.length);
    }

}
