# 一些面试题驱动的Spring架构


## 一、Spring的@Transactional注解
1. @Transactional注解基本功能：提供对某一个方法的“事务性”补偿，如果某一个方法内的逻辑全部执行完毕，就正常退出，否则回滚。
   - 可以作用在类上：该类所有的public方法都配置相同的事务属性信息。
   - 可以作用在接口上：不推荐，如果标注在接口上并配置了Spring AOP使用CGlib进行了动态代理，就会导致@Transactional注解失效
   - 可以作用在方法上：最常用的模式
2. Spring事务的传播机制
   - Spring框架的事务传播行为定义了如何在方法调用时处理事务，这主要涉及到多个事务方法相互调用时的情况。
   - Spring支持以下七种传播行为： 
     - REQUIRED（默认）：如果当前存在事务，则加入该事务；如果没有，则创建一个新的事务。 
     - SUPPORTS：如果当前存在事务，则加入该事务；如果没有，则以非事务方式执行。 
     - MANDATORY：使用当前事务，如果没有则抛出异常。 
     - REQUIRES_NEW：创建一个新的事务，如果当前存在事务，则挂起当前事务。 
     - NOT_SUPPORTED：以非事务方式执行操作，如果当前存在事务，则挂起当前事务。 
     - NEVER：以非事务方式执行，如果当前存在事务，则抛出异常。 
     - NESTED：如果当前存在事务，则在嵌套事务内执行；否则，类似于REQUIRED。
3. @Transactional注解的属性
   - rollbackFor：用于指定能够触发事务回滚的异常类型，可以指定多个异常类型。
   - isolation：事务的隔离级别
     - Isolation.DEFAULT：使用底层数据库默认的隔离级别
     - Isolation.READ_UNCOMMITTED：读未提交
     - Isolation.READ_COMMITTED：读已提交
     - Isolation.REPEATABLE_READ：可重复读
     - Isolation.SERIALIZABLE：串行化
   - propagation：表示事务的传播行为，可配置项参考上面
4. 使用编程式事务（目前用的已经很少了）：参考`src/main/java/com/lxm/technical_code/TransactionalTest/CodingTransactionalTest.java`
5. @Transactional的失效
   - 方法必须是public的，否则该注解会失效（Spring硬性规定，主要是代理逻辑）
   - @Transactional的propagation属性配置错误（某些特殊的配置，不会产生事务）
   - rollbackFor属性配置错误（某些没有捕获的异常，不会被回滚）
   - 方法调用嵌套错误：同一个类中方法调用，导致@Transactional失效
     - 问题说明：
       ```java
       public class MyTest {
           @Autowired
           UserService userService;
           
           @RequestMapping("/test")
           public void test(){
               innerTest();
           }
       
           // 这个注解会失效，因为这个方法的调用没有用到AOP
           // 只有当事务方法被当前类以外的代码调用时，才会由Spring生成的代理对象来管理
           // 因此这个案例中，没有用AOP代理的对象进行代码执行，因此也就不会被回滚
           @Transactional(rollbackFor = Exception.class)
           public void innerTest() {
               try {
                   User user = new User();
                   userService.insert(user);
               } catch (Exception e) {
                   throw e;
               }
           }
       }
       ```
     - 问题解决：
       - AopContext.currentProxy()获得当前代理对象，强制走AOP
         ```java
         public class MyTest {
             @Autowired
             UserService userService;
             
             @RequestMapping("/test")
             public void test() {
                 // 强行走AOP
                 ((TestController) AopContext.currentProxy()).innerTest();
             }
             
             @Transactional(rollbackFor = Exception.class)
             public void innerTest() {
                 try {
                     User user = new User();
                     userService.insert(user);
                 } catch (Exception e) {
                     throw e;
                 }
             }
         }
         ```
       - 写到另一个类中，使用Autowired调用
       - 通过其他方式获取Spring的Bean对象，比如ApplicationContext
   - 如果数据库的引擎不支持事务，将导致该注解根本性失效
6. @Transactional注解的实现原理



## 二、Java的IOC怎么实现的
1. 




## 三、Java的AOP怎么实现的
1. Java的AOP有两种实现模式，JDK动态代理和CGLib代理
2. 


## 四、三级缓存循环依赖



## 五、Spring自定义标签的使用
1. 使用原则
   ```txt
   1.创建需要扩展的组件
   2.定义XSD文件描述组件内容
   3.创建一个文件，实现BeanDefinitionParser接口，用来解析XSD文件中的定义和组件定义
   4.创建Handler文件，扩展字NamespaceHandlerSupport,目的是将组件注册到Spring容器
   5.编写Spring.handlers和Spring.schemas文件
   ```
2. 具体实例参考`src/main/java/com/lxm/technical_code/CustomTag`及《Spring源码深度解析》第四章
3. 因此某些Spring插件的原理也就显而易见了，通过Spring提供的自定义标签加载机制，来实现某些定制化逻辑。


## 六、Spring默认的bean是单例的还是原型的？Spring怎样创建对象？
1. 默认是单例模式`singleton`
2. Spring创建对象的基本流程（xml--beanDefinition--创建对象）
   - 从Xml文档中解析对象的基本定义
   - 将对象基本定义封装到beanDefinition中
   - 创建Bean对象，需要找到合适的 构造器 + 对应的参数(参考Spring源码中寻找构造器的部分)，并调用反射创建对象
3. 


## 七、Spring中常用的设计模式包括哪些？
1. 


## 八、Spring框架的设计思想
### （一）Spring框架设计：扫描注解 -- 从xml中加载定义到BeanDefinition中 -- 根据bd创建对象
1. Spring扫描组件
   - 扫描的是编译后的class文件
   - 扫描到所有带Spring组件的注解，挨个进行加载
2. Spring加载对象beanDefinition
   - 为什么不直接创建对象，要用beanDefinition承接对象？
     - 不确定是不是单例的对象，如果是单例的，每次从单例池中获取就可以
     - 不是单例的，每次都创建一个新的对象
3. Spring根据beanDefinition获取bean
   - 寻找构造器创建对象
     - 构造器匹配
     - 构造对象并实现依赖注入
   - 数据记录：
     - beanDefinition池：根据beanName获取对应的beanDefinition，根据beanDefinition创建对象
     - singleton池：用于记录创建好的单例对象
4. Spring创建对象 & AOP等
   - 依赖注入后实现各种初始化逻辑，准备bean
   - AOP需要创建各种代理，JDK动态代理或者CGLib动态代理

 
### （二）Spring的bean生命周期：实例化 -- 属性注入 -- 初始化 -- ready -- 销毁
【个人理解：属性注入完成后，对JVM层面来说，这个对象已经基本可用；对业务层面上，需要继续进行初始化】
1. 实例化：调用构造器创建对象
   - Spring中涉及到怎样匹配构造器，找到合适的构造器
2. 属性注入：依赖注入
3. Aware回调：
   - BeanNameAware回调：主要是用来设置beanName的
   - BeanFactoryAware回调：主要是用来设置BeanFactory的，BeanFactory是用来获取对象的特殊Factory
   - ApplicationContextAware回调：类似BeanFactoryAware，提供的功能更强大
4. 后处理器处理（初始化之前）：`BeanPostProcessor#postProcessBeforeInitialization`
5. 自定义初始化
   - `@PostConstruct`
   - `InitializingBean#afterPropertiesSet`
   - `init-method`
6. 后处理器处理（初始化之后）：`BeanPostProcessor#postProcessAfterInitialization`
7. Bean准备完成（如果有AOP，需要创建代理对象，将代理对象用于被业务调用）
8. 销毁前处理`@PreDestroy`
9. 销毁处理
   - `DisposableBean#destroy`
   - `destroy-method`






参考资料
1. Spring事务：https://blog.csdn.net/qq_57581439/article/details/132086303
2. Spring事务：https://blog.csdn.net/minghao0508/article/details/124374637
3. @Transactional的失效：https://blog.csdn.net/qq_57581439/article/details/132086303
4. Spring自定义标签的使用：《Spring源码深度解析》第四章
5. JDK动态代理：https://blog.csdn.net/m0_64231944/article/details/134602559
6. 手写Spring源码视频：https://www.bilibili.com/video/BV1tR4y1F75R
7. 