package com.lxm.technical_code.CustomTag;


import org.springframework.context.ApplicationContext;
import org.springframework.context.support.ClassPathXmlApplicationContext;

public class TestCustomTag {
    public static void main(String[] args) {
        ApplicationContext applicationContext = new ClassPathXmlApplicationContext("test.xml");
        User user = (User) applicationContext.getBean("testbean");
        System.out.println(user.getUserName() + "----" + user.getEmail());
    }
}
