package easyProject.MySpring.service;

import easyProject.MySpring.spring.*;

@Component("myService")
@Scope("singleton")
//@Scope("prototype")
public class MyService implements BeanNameAware, InitializingBean, MyInterface {

    @Autowired
    private MyInnerService myInnerService;

    private String beanName;

    public MyService() {

    }

    @Override
    public void test() {
        System.out.println(myInnerService);
    }

    @Override
    public void setBeanName(String beanName) {
        this.beanName = beanName;
    }

    @Override
    public void afterPropertiesSet() {
        System.out.println("afterPropertiesSet");
    }
}
