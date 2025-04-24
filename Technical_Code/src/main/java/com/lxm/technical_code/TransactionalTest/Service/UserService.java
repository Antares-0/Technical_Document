package com.lxm.technical_code.TransactionalTest.Service;

import com.alibaba.fastjson2.JSON;
import com.lxm.technical_code.TransactionalTest.User;
import org.springframework.stereotype.Service;

/**
 * 模拟数据库Service层
 */
@Service
public class UserService {

    public void insertUser(User user) {
        System.out.println("插入User：" + JSON.toJSONString(user));
    }

}
