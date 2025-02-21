# Tomcat和JDK对应关系

## 一、Tomcat和JDK的对应关系基础



## 二、Tomcat SpringBoot JDK
1. 在有的项目中，JDK1.8 + Tomcat 8 | Tomcat 9的组合能够正常运行，但是JDK1.8 + Tomcat 10却完全不能运行。
   - 现象：
   - 目前发现的问题是，应该更改Maven的pom文件，某些SpringBoot的jar不能支持Tomcat10，通常
2. 

<!--JDK8-->
<dependency>
     <groupId>javax.servlet</groupId>
     <artifactId>javax.servlet-api</artifactId>
     <version>3.0.1</version>
     <scope>provided</scope>
 </dependency>



<!--JDK21-->
<dependency>
    <groupId>javax</groupId>
    <artifactId>javaee-api</artifactId>
    <version>8.0.1</version>
</dependency>