package com.lxm.technical_code.TransactionalTest;

import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@SpringBootTest
public class MyTransactionalTest {

    private static Integer age;

    private static String name;

    public static void init(){
        age = 0;
        name = "liu";
    }


    public static void main(String[] args) {
        init();
        new MyTransactionalTest().update();
        System.out.println(age);
        System.out.println(name);
    }

    // 注解失效
    @Transactional(rollbackFor = Exception.class)
    public void update(){
        age = 1;
        int p = 1 / 0;
        name = "myName";
    }
}
