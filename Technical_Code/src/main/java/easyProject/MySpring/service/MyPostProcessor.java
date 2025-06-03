package easyProject.MySpring.service;

import easyProject.MySpring.spring.BeanPostProcessor;
import easyProject.MySpring.spring.Component;

import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;

@Component
public class MyPostProcessor implements BeanPostProcessor {

    @Override
    public Object beforeInitialization(String beanName, Object instance) {
        if ("myService".equals(beanName)) {
            System.out.println("beforeInitialization" + beanName + instance);
        }
        return instance;
    }

    @Override
    public Object afterInitialization(String beanName, Object instance) {
        // AOP可以在这里实现
        if ("myService".equals(beanName)) {
            System.out.println("afterInitialization" + beanName + instance);
            // Proxy.newProxyInstance的逻辑
            // client调用代理对象的时候，调用proxy对象，proxy对象将请求转发给InvocationHandler
            return Proxy.newProxyInstance(this.getClass().getClassLoader(), instance.getClass().getInterfaces(), new InvocationHandler() {
                @Override
                public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
                    System.out.println("代理逻辑");
                    return method.invoke(instance, args);
                }
            });
        }

        return instance;
    }
}
