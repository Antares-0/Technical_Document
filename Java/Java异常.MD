# Java异常

## 一、Java异常的基本结构
1. Java中所有不正常类都继承于Throwable类，它主要包括两个大类，一个是Error类，另一个是Exception类。
   ```txt
   Throwable
      | ------ Error，错误
                  | ------ VirtualMachineError，虚拟机错误
                  | ------ ThreadDeath，线程死锁
      | ------ Exception，异常
                  | ------ IOException、SQLException，受检异常
                  | ------ RunTimeException，运行时异常，非受检异常
                                  | ------ NullPointerExcepion，空指针异常
                                  | ------ ArrayIndexOutOfBoundsException，越界异常
                                  | ------ ClassCastException，类型转换异常
                                  | ------ ArithmeticException，算术异常
   ```
2. 异常链：每次抛异常的时候，都是将捕获的异常封装进一个新的异常中并重新抛出的异常处理方式，这样可以保证最原始的异常信息不被丢失。


## 二、Java异常的处理，finally中代码执行与return的关系
1. 基础情况：
   - 不存在异常，try - finally
   - 存在异常，try - catch - finally
2. 带return：
   - finally中的代码肯定会被执行
   - try和catch中有return，finally中没有return：finally中的代码会被执行，但是要看返回对象是不是引用类型，try和catch中的return的含义是确定了返回对象的一份copy的地址
     - 非引用类型，return过程中就确定了返回什么值
       ```java
       public static int testBasic() {
           int i = 1; 
           try {
               i++;
               System.out.println("try block, i = " + i);
               return i;
           } catch (Exception e) {
               i++;
               System.out.println("catch block i = " + i);
               return i;
           } finally {
               i = 10;
               System.out.println("finally block i = " + i);
           }
       }
       // try block, i = 2
       // finally block i = 10
       // return test i = 2
       ```
     - 引用类型，finally中的代码执行完毕会影响返回值
       ```java
       public static List<Object> testWrap(){
           List<Object> list = new ArrayList<>();
           try{
               list.add("try");
               System.out.println("try block");
               return list;
           } catch (Exception e) {
               list.add("catch");
               System.out.println("catch block");
               return list;
           } finally {
               list.add("finally");
               System.out.println("finally block ");
           }
       }
       // try block
       // finally block
       // return test i = [try, finally]
       ```
   - finally中包含return，会直接返回finally中的return值，并屏蔽掉try-catch中的异常


       


## 三、throw和throws关键字
1. `throw`是一个动作，代表抛出异常
2. `throws`是一个声明，代表声明可能抛出的异常类型

## 四、自定义异常
1. 基本原则：
   - 所有的异常必须继承Throwable类
   - 如果想写一个检查性异常类，则需要继承Exception类
   - 如果想写一个运行时异常类，则需要继承RunTimeException类
2. 案例
   ```txt
   可以参考 src/main/java/easyProject/ExceptionTest 下面的解决方案
   ```

