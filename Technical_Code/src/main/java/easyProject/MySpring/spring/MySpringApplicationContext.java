package easyProject.MySpring.spring;


import easyProject.MySpring.service.MyPostProcessor;
import org.springframework.util.StringUtils;

import java.beans.Introspector;
import java.io.File;
import java.lang.reflect.Field;
import java.lang.reflect.InvocationTargetException;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ConcurrentHashMap;

public class MySpringApplicationContext {

    private Class configClass;

    // beanDefinition记录
    private ConcurrentHashMap<String, BeanDefinition> beanDefinitionMap = new ConcurrentHashMap<>();

    // 单例池
    private ConcurrentHashMap<String, Object> singletonCache = new ConcurrentHashMap<>();

    // 处理器
    private List<BeanPostProcessor> beanPostProcessorList = new ArrayList<>();


    public MySpringApplicationContext(Class clazz) {
        this.configClass = clazz;

        // 扫描
        if (clazz.isAnnotationPresent(ComponentScan.class)) {
            ComponentScan componentScan = (ComponentScan) clazz.getAnnotation(ComponentScan.class);
            // 需要扫描的路径
            String path = componentScan.value();
            path = path.replace(".", "/");
            ClassLoader classLoader = MySpringApplicationContext.class.getClassLoader();
            String file = classLoader.getResource(path).getFile();
            File filePath = new File(file);
            if (filePath.isDirectory()) {
                File[] files = filePath.listFiles();
                for (File f : files) {
                    String absolutePath = f.getAbsolutePath();
                    // 如果是class结尾
                    if (absolutePath.endsWith(".class")) {
                        try {
                            // 写死了
                            String className = absolutePath.substring(absolutePath.indexOf("easyProject"), absolutePath.indexOf(".class"));
                            Class<?> aClass = classLoader.loadClass(className.replace("/", "."));
                            if (aClass.isAnnotationPresent(Component.class)) {
                                // 如果是processor
                                // isAssignableFrom：判断参数类型是不是本类型的实现
                                // instanceOf不适用
                                if (BeanPostProcessor.class.isAssignableFrom(aClass)) {
                                    beanPostProcessorList.add((BeanPostProcessor) aClass.newInstance());
                                }
                                String beanName = aClass.getAnnotation(Component.class).value();
                                if (StringUtils.isEmpty(beanName)) {
                                    // 首字母小写方法
                                    beanName = Introspector.decapitalize(aClass.getSimpleName());
                                }
                                BeanDefinition beanDefinition = new BeanDefinition();
                                // 需要使用Spring加载
                                if (aClass.isAnnotationPresent(Scope.class)) {
                                    beanDefinition.setScope(aClass.getAnnotation(Scope.class).value());
                                    beanDefinition.setType(aClass);
                                } else {
                                    beanDefinition.setScope("singleton");
                                    beanDefinition.setType(aClass);
                                }
                                beanDefinitionMap.put(beanName, beanDefinition);
                            }
                        } catch (Exception e) {

                        }

                    }

                }
            }

        }

        // 实例化单例bean
        for (String beanName : beanDefinitionMap.keySet()) {
            BeanDefinition beanDefinition = beanDefinitionMap.get(beanName);
            if ("singleton".equals(beanDefinition.getScope())) {
                Object o = createBean(beanName, beanDefinition);
                singletonCache.put(beanName, o);
            }
        }
    }

    private Object createBean(String beanName, BeanDefinition beanDefinition) {
        Class type = beanDefinition.getType();
        Object o = null;
        try {
            o = type.getConstructor().newInstance();

            // getFields只能访问到公有的字段
            // getDeclaredFields可以访问到全部的私有字段
            Field[] fields = type.getDeclaredFields();
            for (Field field : fields) {
                if (field.isAnnotationPresent(Autowired.class)) {
                    field.setAccessible(true);
                    // 实现自动注入
                    // filed instance object
                    field.set(o, getBean(field.getName()));
                }
            }

            // 实现了这个接口，就setBeanName
            if (o instanceof BeanNameAware) {
                ((BeanNameAware) o).setBeanName(beanName);
            }

            // 遍历处理器
            for (BeanPostProcessor postProcessor : beanPostProcessorList) {
                o = postProcessor.beforeInitialization(beanName, o);
            }

            // 初始化
            if (o instanceof InitializingBean) {
                ((InitializingBean) o).afterPropertiesSet();
            }

            for (BeanPostProcessor postProcessor : beanPostProcessorList) {
                o = postProcessor.afterInitialization(beanName, o);
            }


        } catch (InstantiationException e) {
            throw new RuntimeException(e);
        } catch (IllegalAccessException e) {
            throw new RuntimeException(e);
        } catch (InvocationTargetException e) {
            throw new RuntimeException(e);
        } catch (NoSuchMethodException e) {
            throw new RuntimeException(e);
        }
        return o;
    }

    public Object getBean(String beanName) {
        BeanDefinition beanDefinition = beanDefinitionMap.get(beanName);
        if (beanDefinition == null) {
            throw new NullPointerException("no beanDefinition found");
        }
        String scope = beanDefinition.getScope();
        if ("singleton".equals(scope)) {
            Object o = singletonCache.get(beanName);
            if (o == null) {
                Object bean = createBean(beanName, beanDefinition);
                singletonCache.put(beanName, bean);
                return bean;
            }
            return o;
        } else {
            return createBean(beanName, beanDefinition);
        }
    }


}
