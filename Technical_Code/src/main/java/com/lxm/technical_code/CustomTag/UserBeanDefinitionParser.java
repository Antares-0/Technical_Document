package com.lxm.technical_code.CustomTag;

import org.mockito.internal.util.StringUtil;
import org.springframework.beans.factory.support.BeanDefinitionBuilder;
import org.springframework.beans.factory.xml.AbstractSingleBeanDefinitionParser;
import org.springframework.util.StringUtils;
import org.w3c.dom.Element;

/**
 * Spring的自定义标签
 */
public class UserBeanDefinitionParser extends AbstractSingleBeanDefinitionParser {
    protected Class getBeanClass(Element element) {
        return User.class;
    }

    protected void doParse(Element element, BeanDefinitionBuilder beanDefinitionBuilder) {
        String userName = element.getAttribute("userName");
        String email = element.getAttribute("email");
        if (!StringUtils.isEmpty(userName)) {
            beanDefinitionBuilder.addPropertyValue("userName", userName);
        }
        if (!StringUtils.isEmpty(email)) {
            beanDefinitionBuilder.addPropertyValue("email", email);
        }
    }

}
