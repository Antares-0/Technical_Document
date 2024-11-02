# Java的SPI机制

## 一、SPI是什么
1. SPI（Service Provider Interface，服务发现接口），是JDK内置的一种服务提供发现机制，可以用来启用框架扩展和替换组件，主要是被框架的开发人员使用。
2. SPI用于实现框架或库的扩展点，允许在运行时动态地插入或更换组件实现。它提供了一个框架来发现和加载服务实现，使得软件模块能够灵活地选择和使用不同的服务提供商。SPI鼓励松耦合的设计，因为服务的消费者不需要直接依赖于具体的服务实现。有没有想到面向对象的某个设计原则，SOLID中的 O 开闭原则，对扩展开放对修改关闭。Java允许服务提供者，按照SPI给定的规则实现自己的服务，而Java应用使用通过SPI规则提供的服务时无需进行额外的配置，并且可以随时替换服务，也无需修改业务代码。
3. SPI和API的区别
   1. SPI，调用方对实现方进行限制，实现方必须实现调用者要求的接口（在本案例中是Search.java），并将自己的实现配置放在`META-INF/services/easyProject.SPI.Search`文件中，在文件中指明自己的接口位置
   2. API，实现方对调用方进行限制，调用方必须修改自己的代码以适配外部的API，比如要使用外部的A服务，必须在调用方的代码中写A.RTPCall()，这对于调用方的封装不利。
   3. 总结来说，API是调用适配实现，SPI是实现适配调用
   


## 二、SPI怎样使用
1. 使用ServiceLoader.load方法，加载某一个接口类型的class。
   ```java
    package easyProject.SPI;
    import java.util.ServiceLoader;
    public class SPITest {
        public static void main(String[] args) {
            // Search 是一个接口
            ServiceLoader<Search> serviceLoader = ServiceLoader.load(Search.class);
            for (Search search : serviceLoader) {
                System.out.println(search.searchDoc("myWord"));
            }
        }
    }
   ```
   ```java
    public interface Search {
        String searchDoc(String keyWord);
    }
   ```
2. 



## 三、SPI的案例分析
1. MySQL的




参考资料
1. https://blog.csdn.net/qq_37883866/article/details/139000021
2. https://zhuanlan.zhihu.com/p/28909673