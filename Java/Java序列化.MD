# Java序列化

## 一、Java序列化Serializable接口（序列化 = 对象转字节数组）
1. Serializable接口代表可以序列化，表示某个实现了这个接口的类可以被转换成字节数组，便于储存和传输——实现了该接口后，一方面可以将对象保存到文件中，然后再从文件中读出来；另一方面，可以在网络中传输这个对象。
2. Serializable接口的底层实际上是空的，这个接口下没有任何方法或字段。
3. Serializable接口的作用是“标识”，告诉JVM这个类可以被序列化，具体的序列化过程实际上是JVM实现的。


## 二、Serializable接口的实现
1. 源码
    ```java
     // 序列化方法
     public final void writeObject(Object obj) throws IOException {
         if (enableOverride) {
             writeObjectOverride(obj);
             return;
         }
         try {
             // 序列化主方法
             writeObject0(obj, false);
         } catch (IOException ex) {
             if (depth == 0) {
                 writeFatalException(ex);
             }
             throw ex;
         }
     }
   
     // 序列化方法
     private void writeObject0(Object obj, boolean unshared) throws IOException {
         boolean oldMode = bout.setBlockDataMode(false);
         depth++;
         try {
             // .... 无关源码省略
             // 检查对象的类型，如果是字符串、数组、枚举或者实现了Serializable接口，那就可以正常序列化
             if (obj instanceof String) {
                 writeString((String) obj, unshared);
             } else if (cl.isArray()) {
                 writeArray(obj, desc, unshared);
             } else if (obj instanceof Enum) {
                 writeEnum((Enum<?>) obj, desc, unshared);
             // 如果实现了序列化接口，那就可以调用 writeOrdinaryObject 方法实例化
             } else if (obj instanceof Serializable) {
                 writeOrdinaryObject(obj, desc, unshared);
             } else {
                 // 抛异常
                 if (extendedDebugInfo) {
                     throw new NotSerializableException(
                         cl.getName() + "\n" + debugInfoStack.toString());
                 } else {
                     throw new NotSerializableException(cl.getName());
                 }
             }
         } finally {
             depth--;
             bout.setBlockDataMode(oldMode);
         }
     }
    ```
2. 序列化的底层：使用的是ObjectOutputStream.defaultWriteFields方法进行序列化的实现，本质上就是文件的写入
3. 反序列化的底层：
4. 序列化ID：private static final long serialVersionUID = 362498820763181265L;  
   序列化ID的是决定java对象能否反序列化成功的重要因子，在反序列化时，Java虚拟机会把字节流中的serialVersionUID与被序列化类中的serialVersionUID做比较，相同就可以正常反序列化，否则抛出异常。
5. 反序列化是否成功的因素目前包括如下：序列化因子、类路径、功能代码是否一致。









参考资料：
1. https://blog.csdn.net/weixin_44209555/article/details/107837108
2. https://blog.csdn.net/demo_yo/article/details/139704145

