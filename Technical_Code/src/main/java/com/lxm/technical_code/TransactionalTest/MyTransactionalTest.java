package com.lxm.technical_code.TransactionalTest;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.transaction.PlatformTransactionManager;
import org.springframework.transaction.support.TransactionTemplate;

public class MyTransactionalTest {

    @Autowired
    PlatformTransactionManager transactionManager;

    public static void main(String[] args) {

    }
}
