# Spock单元测试书写


## 一、只有一个参数的方法，使用`_`占位
1. java方法
   ```java
    @VisibleForTesting
    private int getNum() {
        return 5;
    }
   ```
2. 单元测试
   ```groovy
    @Unroll
    def 'getSumTest'() {
        given: ""
            def testObj = new TestObj()
        when: ""
            def res = testObj.getSum()
        then: ""
            res == 5 == result
        where: ""
         _ || result
         _ || true
    }
   ```

## 二、为私有方法添加`@VisibleForTesting`并不能保证方法的可见性，还是要用`protected`来保证提权
1. 主方法
   ```java
    import com.google.common.annotations.VisibleForTesting;
   
    @VisibleForTesting
    private int getSum1(int a, int b) {
        return a + b;
    }
    
    @VisibleForTesting
    protected int getSum2(int a, int b, int c) {
        return a + b + c;
    }
   ```
2. 单元测试
   ```groovy
    def 'getSum1Test'() {
        when: ""
        // 无效
        testObj.getSum1(1, 2)
    }
    
    def 'getSum2Test'() {
        when: ""
        // 有效，因为可见
        testObj.getSum2(1, 2, 3)
    }
   ```
3. 注意事项
   1. `@VisibleForTesting`注解不能实现提权，它只是用来告诉程序员们这个方法是被迫可见的。
   2. 实际上要通过`protected & public`来实现
   
## 三、模拟同一个类中其他方法的返回值
1. 主方法
   ```java
    public class RoomNumberUtil {
   
        private RoomNumberUtil() {}

        @VisibleForTesting
        protected Integer getRoomNumber(String roomNumber) {
            return getNumber() + Integer.valueOf(roomNumber.trim());
        }

        @VisibleForTesting
        protected Integer getNumber() {
            return 0;
        }
    }
   ```
2. 单元测试
   ```java 
    def roomNumberUtil = new RoomNumberUtil()
    def spy = Spy(roomNumberUtil)

    // 使用同一个对象 spy 能够 mock 的案例
    // mock spy & 使用 spy 调用
    @Unroll
    def "getRoomNumberTest"() {
        given: ""
        this.spy.getNumber() >> 2

        when: ""
        def res = this.spy.getRoomNumber(input)

        then: ""
        res == ans

        where: ""
        input || ans
        "0"   || 2
    }
   ```
3. 注意事项：
   1. 注意mock的方法都要可见，至少都是`protected`
   2. 注意mock的对象必须是spy对象，也就是`Spy(testObj)`
   3. 注意调用方法的对象必须是spy对象，也就是`Spy(testObj)`



// //Generated with love by TestMe :) Please report issues and submit feature requests at: http://weirddev.com/forum#!/testme

