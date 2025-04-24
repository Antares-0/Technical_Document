# Spring的bean属性


## 一、Bean的属性（BeanDefinitionParserDelegate.parseBeanDefinitionAttributes中进行了加载）
1. abstract属性与parent属性
2. scope属性
3. lazy-init属性
4. autowire属性
5. depends-on属性

<property>：用于设置bean的属性值。它可以用于注入基本类型、引用类型或其他属性。通过指定属性名称和对应的值，可以将值注入到bean的相应属性中。

<constructor-arg>：用于设置构造函数参数的值。当创建bean时，可以通过指定构造函数参数的值来实例化bean对象。可以使用索引或参数名称指定构造函数的参数位置，并将相应的值注入到构造函数中。

<description>：用于给bean或其属性提供描述信息。该标签可以用于为bean或属性添加注释或描述，以提供更好的文档和可读性。

<lookup-method>：用于在子类中重写父类的bean方法。当使用Spring的基于配置的AOP时，该标签允许子类通过返回不同的实例来重写父类的方法。

<meta>：用于指定bean的元数据。元数据可以包括键值对、注释或其他自定义标记，用于描述bean的特性和行为。

<qualifier>：用于标识具有相同类型的多个bean的唯一性。当存在多个同一类型的bean时，可以使用该标签为每个bean设置一个唯一的标识符，以便在注入时进行精确的匹配。

<replaced-method>：用于在运行时替换bean中的方法。可以通过指定要替换的方法名称和相应的新实现来替换bean中的现有方法。







参考资料：
1. https://cloud.tencent.com/developer/article/1432387