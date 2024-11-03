# MySQL字符串与数值匹配的自动转换机制

## 一、字符串与数字的自动转换
1. 【类型一】当MySQL遇到字符串和数字相比较的时候，会自动把**字符串**转换为**数字**。
   ```sql
   select * from students where name = 123
   ## 相当于
   select * from students where cast(name as int) = 123
   ```
   如果`name`列加了索引，这种情况会导致索引失效，因为转换会发生在索引列上，将`name`列的字符串转换为数字，导致索引失效。
2. 【类型二】当MySQL遇到字符串和数字相比较的时候，会自动把**字符串**转换为**数字**。
   ```sql
   select * from students where age = '123'
   ## 相当于
   select * from students where age = cast('123' as int)
   ```
   如果`age`列加了索引，这种情况不会导致索引失效，因为转换没有发生在索引列上。



参考资料
1. https://zhuanlan.zhihu.com/p/635230263