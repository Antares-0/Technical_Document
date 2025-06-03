package easyProject.MySpring.service;

import easyProject.MySpring.spring.Autowired;
import easyProject.MySpring.spring.Component;
import easyProject.MySpring.spring.Scope;

@Component("myService")
@Scope("singleton")
//@Scope("prototype")
public class MyService {

    @Autowired
    private MyInnerService myInnerService;

    public MyService() {

    }

    public void test() {
        System.out.println(myInnerService);
    }

    public MyInnerService getMyInnerService() {
        return myInnerService;
    }

    public void setMyInnerService(MyInnerService myInnerService) {
        this.myInnerService = myInnerService;
    }
}
