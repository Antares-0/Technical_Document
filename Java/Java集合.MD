# Java集合

## 一、HashMap
1. HashMap中为什么不能使用基本数据类型？Java的容器类是通过泛型实现的，泛型实现是基于Object类型的，而基本类型不是对象，所以不能直接存放在容器类中。
2. HashMap在多线程动态扩容时出现的问题——死循环指针问题
   
3. 



## 二、TreeMap
1. TreeMap的底层是红黑树，



## 三、ConcurrentHashMap（HashMap的线程安全版本之一）
1. 是HashMap的支持并发的版本，是`Collections.synchronizedMap(Map<K,V> m)`的优化版本。下面是`Collections.synchronizedMap`的使用
    ```java
        public static void main(String[] args) {
            Map<Integer, String> map = new HashMap<>();
            map.put(1, "a");
            Map<Integer, String> integerStringMap = Collections.synchronizedMap(map);
            System.out.println(integerStringMap.size());
        }
    ```
2. ConcurrentHashMap在理想情况下可以支持16个线程的并发写操作
3. ConcurrentHashMap的高效并发机制是通过以下三个方面保证的：
   1. 锁分段
      
   2. HashEntry的不变性、Volatile的内存可见性、加锁重读机制
   
   3. 加锁不加锁两种方案控制跨段的安全性

## 四、HashMap的线程安全版本之二：





参考资料：
1. ConcurrentHashMap：https://blog.csdn.net/qq_24903931/article/details/82850170