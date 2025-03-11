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

## 二、为私有方法添加`@VisibleForTesting`保证方法的可见性
1. 主方法
   ```java
    @VisibleForTesting
    private int getSum(int a, int b) {
        return a + b;
    }
   ```
2. 单元测试
   ```groovy
    def 'getSumTest'() {
        // 正常写就好了
    }
   ```
   
