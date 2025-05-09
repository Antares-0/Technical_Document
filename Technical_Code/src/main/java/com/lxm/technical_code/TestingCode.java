package com.lxm.technical_code;

import java.util.ArrayList;

/**
 * @Author: liuxianming
 * @Date: 2025/05/09 16:05:40
 */
public class TestingCode {
    public static void main(String[] args) {
        ArrayList list = new ArrayList();
        list.add("a");
        list.add('a');
        list.add(new TestingCode());
        for (int i = 0; i < list.size(); i++) {
            System.out.println(list.get(i));
        }
    }
}
