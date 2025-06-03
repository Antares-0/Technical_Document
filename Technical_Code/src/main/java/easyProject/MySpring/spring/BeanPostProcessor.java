package easyProject.MySpring.spring;

public interface BeanPostProcessor {

    Object beforeInitialization(String beanName, Object instance);

    Object afterInitialization(String beanName, Object instance);

}
