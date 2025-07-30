# Java的反射机制

## 一、反射是什么
1. 反射是指java在程序运行时动态加载并获取类的详细信息，从而操作类或者对象的属性和方法。本质是JVM得到class对象之后，再通过class对象进行反编译，从而得到对象的各种信息。
2. Java属于先编译再运行的语言，程序中对象的类型在编译期间就定下来了，但程序再运行时可能需要动态加载某些类，于是相当于JVM留下了一个后门。

## 二、反射的优点和缺点
1. 优点：在编译后依然可以动态地加载一些类并创建对象，保证了灵活性。
2. 缺点：一方面，反射需要一定的系统资源；另一方面，反射越过了一个特殊的权限检查，因此会导致安全问题

## 三、反射的原理
1. 正常加载一个类的流程：
    1. 执行new对象的时候，JVM加载.class文件
    2. JVM去本地磁盘中加载文件到JVM内存中
    3. 文件加载到内存之后，JVM会自动创建一个class对象，一个类只会产生一个class对象
    4. 根据.class文件创建对象等
2. 反射加载一个类或创建新的对象
    1. JVM去某一指定位置加载.class文件，可能是网络可能是某个包的目录下
    2. JVM去本地磁盘中加载文件到JVM内存中
    3. 文件加载到内存之后，JVM会自动创建一个class对象，一个类只会产生一个class对象
    4. 根据.class文件创建对象等

## 四、反射的真实使用案例
1. 反编译：.class-->.java
2. 通过反射机制访问java对象的属性，方法，构造方法等
3. 当我们在使用IDE,比如IDEA时，当我们输入一个对象或者类，并想调用他的属性和方法时，一按点号，编译器就会自动列出他的属性或者方法，这里就是用到反射。
4. 反射最重要的用途就是开发各种通用框架。比如很多框架（Spring）都是配置化的（比如通过XML文件配置Bean），为了保证框架的通用性，他们可能需要根据配置文件加载不同的类或者对象，调用不同的方法，这个时候就必须使用到反射了，运行时动态加载需要的加载的对象。

## 五、反射的使用
1. 获取class对象的方法`Class.forName("");`
   ```java
   // 方式一
   Student A = new Student();
   Class studentClass = A.getClass();
   // 方式二
   Class studentClass = Student.class;
   // 方式三（比较常用）
   Class studentClass = Class.forName("com.lxm.Student"); 
   ```
2. 判断是不是某个类型`Class.isInstance()`
3. 反射创建对象`class.newInstance()`
4. 反射填充字段`class.getField()`
   ```java
   // 获取class
   Class stuClass = Class.forName("com.lxm.Student");
   // 加载反射对象的相关字段，getFields只能获取公用的字段
   Field[] fieldArray = stuClass.getFields();
   for (Field f : fieldArray) {
       System.out.println(f);
   }
   fieldArray = stuClass.getDeclaredFields();
   for (Field f : fieldArray) {
       System.out.println(f);
   }
   // 获取name这个字段
   Field field = stuClass.getField("name");
   // 创建对象
   Object obj = stuClass.getConstructor().newInstance(); // 产生Student对象 --> Student stu = new Student();
   // 为字段设置值，方式：Field.set(对象,值)
   field.set(obj, "刘德华"); //为Student对象中的name属性赋值 --> stu.name = "刘德华"
   // 验证
   Student stu = (Student)obj;
   System.out.println("验证姓名：" + stu.name);
   ```
5. 反射调用方法`class.getMethod(方法名称, .class).invoke(实例对象, 参数)`
6. 反射获取对象上的信息




参考资料
1. https://blog.csdn.net/a745233700