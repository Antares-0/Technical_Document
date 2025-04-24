package com.lxm.technical_code.TransactionalTest;

import com.lxm.technical_code.TransactionalTest.Service.UserService;
import org.junit.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.transaction.PlatformTransactionManager;
import org.springframework.transaction.TransactionStatus;
import org.springframework.transaction.support.DefaultTransactionDefinition;
import org.springframework.transaction.support.TransactionCallback;
import org.springframework.transaction.support.TransactionTemplate;

/**
 * 编程式事务
 */
@SpringBootTest
public class CodingTransactionalTest {

    @Autowired
    PlatformTransactionManager platformTransactionManager;

    @Autowired
    private TransactionTemplate transactionTemplate;

    @Autowired
    UserService userService;

    @Test
    public void transactionManagerTest() {
        // 事务基础信息 超时时间、隔离级别、传播属性等
        DefaultTransactionDefinition defaultTransactionDefinition = new DefaultTransactionDefinition(); // 定义事务属性
        // 设置传播行为属性，默认事务级别。当前无事务则新建事务，已有事务则加入事务。
        defaultTransactionDefinition.setPropagationBehavior(DefaultTransactionDefinition.PROPAGATION_REQUIRED);
        // 获得事务状态
        TransactionStatus status = platformTransactionManager.getTransaction(defaultTransactionDefinition);
        try {
            User user = new User();
            user.setName("张三");
            // 事务操作
            // 数据库操作
            userService.insertUser(user);
            // 手动设置异常
            int i = 1 / 0;
            // 事务提交
            platformTransactionManager.commit(status);// 提交事务
        } catch (Exception e) {
            // 事务提交
            platformTransactionManager.rollback(status);
            System.out.println("已经回滚了");
        }
    }

    @Test
    public void transactionTemplateTest() {
        Object execute = transactionTemplate.execute(new TransactionCallback() {
            /**
             * @param transactionStatus 事务运行状态信息 是否是新事务、是否已被标记为回滚等
             * @return
             */
            @Override
            public Object doInTransaction(TransactionStatus transactionStatus) {
                try {
                    User user = new User();
                    user.setName("张三");
                    userService.insertUser(user);
                    // 手动设置异常
                    int i = 1 / 0;
                    return "成功";
                } catch (Exception e) {
                    System.out.println("捕捉异常！");
                    transactionStatus.setRollbackOnly();
                    return "失败";
                }
            }
        });
    }

}



