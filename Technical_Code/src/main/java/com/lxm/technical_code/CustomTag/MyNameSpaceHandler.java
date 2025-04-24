package com.lxm.technical_code.CustomTag;

import org.springframework.beans.factory.xml.NamespaceHandlerSupport;

public class MyNameSpaceHandler extends NamespaceHandlerSupport {

    public void init() {
        // 表示接受以user开头的自定义标签
        registerBeanDefinitionParser("user", new UserBeanDefinitionParser());
    }

}
