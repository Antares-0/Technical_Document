package com.lxm.technical_code.Optional;

import java.util.Optional;

public class MyOptionalTest {

    public static void main(String[] args) {
        // 创建空对象
        Optional<String> empty = Optional.empty();
        Optional<String> key = Optional.of("key");
        Optional<Book> book = Optional.of(new Book());
        // 判断是不是空值
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
    }


    static class Book {

        private String name;

        private int value;

        public String getName() {
            return name;
        }

        public void setName(String name) {
            this.name = name;
        }

        public int getValue() {
            return value;
        }

        public void setValue(int value) {
            this.value = value;
        }

        public Book() {
        }

        public Book(String name, int value) {
            this.name = name;
            this.value = value;
        }
    }
}
