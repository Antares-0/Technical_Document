# Java的Optional书写机制

## 一、Optional对象
1. Optional的作用：减少判空的代码
2. Optional对象的创建：
   ```java
   Optional<String> empty = Optional.empty;
   // 注意，of里面的不能是null
   Optional<Book> book = Optional.of(new Book());
   Optional<Book> bookCanBeNull = Optional.ofNullable(null);
   ```
3. Optional对象的计算：
   ```java
   Optional<Book> book = Optional.ofNullable(null);
   // 判断是不是空值 isPresent
   boolean isPresent = book.isPresent();
   // 如果不是空值怎么处理，使用ifPresent传入消费者
   book.ifPresent(it -> System.out.println(it));
   book.ifPresent(System.out::println);
   // 使用orElse处理Optional为空的情况
   Book love = book.orElse(new Book("love", 1));
   // 过滤值
   Optional<Book> remain = book.filter(it -> it.getName().length() > 2);
   // 转换值
   Optional<Integer> values = book.map(Book::getValue);
   ```





参考文章：
1. https://javabetter.cn/java8/optional.html#_02%E3%80%81optional-%E6%98%AF%E5%A6%82%E4%BD%95%E8%A7%A3%E5%86%B3%E8%BF%99%E4%B8%AA%E9%97%AE%E9%A2%98%E7%9A%84