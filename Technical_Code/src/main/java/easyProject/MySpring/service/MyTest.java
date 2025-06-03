package easyProject.MySpring.service;

import easyProject.MySpring.spring.MySpringApplicationContext;

public class MyTest {

    public static void main(String[] args) {

        MySpringApplicationContext mySpringApplicationContext = new MySpringApplicationContext(AppConfig.class);

        MyService myService = (MyService) mySpringApplicationContext.getBean("myService");
        myService.test();

    }


}
