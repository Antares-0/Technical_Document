# Spock单元测试中遇到的BUGs

## 一、Spock单元测试中的BUGs
1. BUG1
   - BUG信息：`To create a new mock, the existing static mock registration must be deregistered`
   - BUG含义：某一个静态类的mock在多行测试中被多次引用
   - 解决方案：将静态类的Mock语句放在方法的given语句内，而且将多行测试拆分为一个一个的子方法进行测试
   - 参考文档：https://github.com/mockito/mockito/issues/2754





