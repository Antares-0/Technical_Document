# MySQL锁

## 一、临键锁的退化
1. 
2. 



## 二、行锁分类
- Record Lock：记录锁，仅仅锁定一条记录
  - S锁：共享锁，<font color='yellow'>只有Record Lock才有S和X的区分</font>
  - X锁：排他锁，<font color='yellow'>只有Record Lock才有S和X的区分</font>
  - S锁和X锁的区分为了解决多个事务之间的并发和数据一致性的兼容问题，退而求其次实现的一种读写分离方案
- Gap Lock：间隙锁，锁定一个范围，不包含记录本身
  - Gap Lock本身没有S和X锁的区分，Gap Lock判断数据能不能共享与读写没有直接关系，主要取决于区间是否重叠
- Next-Key Lock：临键锁，Record Lock + Gap Lock的组合，锁定记录本身并且锁定一个范围


