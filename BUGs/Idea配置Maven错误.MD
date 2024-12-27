# Idea配置Maven错误

## 问题描述
```txt
"LATEST" or "RELEASE" for the Parent POM are currently being deprecated.
```
某些maven文件中的坐标中的版本写的是RELEASE，之前的maven会自动定位，但是新版的maven为了防止冲突就避免了。
正常的解决方案应该是更改version变为某一具体版本，但是某些pom文件并不是开发能够直接修改的，因此还是尽可能改变自己的配置。

## 解决方案
更换maven版本，该文档中写的是3.3.9可以支持（已经确认支持）。已经确认3.9.9、3.6.3不支持。

## 思考
1. JDK的版本、Maven的版本都会影响开发
2. maven的插件也会升级迭代，用最新的确实容易出问题


参考资料：
1. https://youtrack.jetbrains.com/issue/IDEA-350957/When-parent-poms-version-is-RELEASE-maven-import-failed