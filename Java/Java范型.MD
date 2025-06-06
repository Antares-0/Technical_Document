# Java范型

## 一、Java范型的存在意义
1. 范型的引入使得参数的类型可以像变量一样传入方法，它提供了一种扩展能力，更符合面向对象开发的软件编程宗旨。
2. 当具体的数据类型确定后，泛型又提供了一种类型安全检测机制，只有数据类型相匹配的变量才能正常的赋值，否则编译器就不通过。所以说，泛型一定程度上提高了软件的安全性，防止出现低级的失误。
3. 泛型提高了程序代码的可读性。在定义泛型阶段（类、接口、方法）或者对象实例化阶段，由于 <类型参数> 需要在代码中显式地编写，所以程序员能够快速猜测出代码所要操作的数据类型，提高了代码可读性。

## 二、Java范型
1. 泛型，即“参数化类型”。一提到参数，最熟悉的就是定义方法时有形参列表，普通方法的形参列表中，每个形参的数据类型是确定的，而变量是一个参数。在调用普通方法时需要传入对应形参数据类型的变量（实参），若传入的实参与形参定义的数据类型不匹配，则会报错。
2. 那参数化类型是什么？以方法的定义为例，在方法定义时，将方法签名中的形参的**数据类型**也设置为参数，在调用该方法时再从外部传入一个具体的数据类型和变量。
3. 泛型的本质是为了<font color='yellow'>将类型参数化</font>， 也就是说在泛型使用过程中，数据类型被设置为一个参数，在使用时再从外部传入一个数据类型；而一旦传入了具体的数据类型后，传入变量（实参）的数据类型如果不匹配，编译器就会直接报错。这种参数化类型可以用在类、接口和方法中，分别被称为泛型类、泛型接口、泛型方法。

## 三、Java范型的实现原理
1. 范型擦除：java在编译器检查对象的类型是否符合范型要求，但是在运行过程中会将所有的类型统一擦除为Object类型；
   - 范型信息仅仅会存在于编译阶段
   - 不是所有的范型擦除都会擦除至Object类型，当指定了super、extends等标识的时候不会擦除至Object
   - 既然都范型擦除了，运行时怎么获取范型的具体类型？虽然实行了范型擦除，JVM还是记录了每个对象的真实类型，当需要的时候会从JVM中取出
   ```txt
   List<String> strList = new ArrayList<>();
   1. 编译期，编译器会校验放入list中的数据类型，不符合要求会报错
   2. 编译期检查完毕后，会自动实现范型擦除，将范型的类型转换为Object或其他，JVM会记录下数据的具体类型(String)
   3. 运行期需要操作对象的时候，JVM会自动根据记录的数据类型实现数据转换，将Object转换为String
   ```
2. 向上转型：`ArrayList<Number> numberList = new ArrayList<Integer>();`是不被允许的
   1. 基础信息：Integer是Number的子类，Float也是Number的子类
   2. 如果允许这种转型，那么从代码的角度，numberList能够放入Float对象，因为Float对象符合Number的限制；那么取数据的时候怎么将Float对象转换为Integer呢？这就导致了新的问题，因此就不能这么做
   3. `Pair<Integer>`不是`Pair<Number>`的子类，Integer是Number的子类
3. 为了实现向上转型，范型通配符由此产生
   1. 上界通配符extends，下界通配符super
   2. 虽然`Pair<Integer>`和`Pair<Number>`之间不存在继承关系，但是引入上界通配符的概念后，我们便可以在逻辑上将`Pair<? extends Number>`看做是`Pair<Integer>`的父类，但实质上它们之间没有继承关系
      ```java
        ArrayList<Number> list01 = new ArrayList<Integer>(); // 编译错误
		ArrayList<? extends Number> list02 = new ArrayList<Integer>(); // 编译正确
      ```
   3. 





参考文档
1. 范型相关：https://blog.csdn.net/weixin_45395059/article/details/126006369
2. 
