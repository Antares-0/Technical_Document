package easyProject.MySpring.service;

import easyProject.MySpring.spring.MySpringApplicationContext;

public class MyTest {

    public static void main(String[] args) {

        MySpringApplicationContext mySpringApplicationContext = new MySpringApplicationContext(AppConfig.class);

        MyInterface myInterface = (MyInterface) mySpringApplicationContext.getBean("myService");
        myInterface.test();

    }


}
