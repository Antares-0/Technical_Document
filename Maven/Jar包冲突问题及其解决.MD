# Jar包冲突问题及其解决

## 一、Maven引入不同版本Jar包的基本方式
1. Maven依赖原则
   1. 路径优先原则
      相同名称不同版本的Jar包，路径短的先引入
   2. 先声明优先原则
      在路径长度一致的时候，在pom文件中先出现的版本会被引入
   3. 子pom中的依赖优先于父pom中的依赖
2. Maven的多级缓存机制
   1. maven的多级缓存机制主要配置在maven的settings.xml文件中
   2. 多级缓存主要包括：本地缓存 + 远程镜像仓库
   3. 在本地没有相关的配置的时候，会出现向远程镜像仓库请求获取Jar包的行为；远程仓库包括自己配置的中央仓库和maven官方的中央仓库。
   4. 简单来说，目前的maven缓存机制可以概括为三级缓存机制
      ```
      本地仓库
      远程自定义仓库（比如公司内部的某些Jar配置）
      远程中央仓库（maven官方的兜底仓库）
      ```
   

## 二、Jar包冲突可能会引起的Exception
1. 简单易懂的Exception
   1. NoClassDefFoundError，存粹的Jar包冲突问题
   2. ClassNotFoundException，存粹的Jar包冲突问题
2. 不容易发现的Exception「积累中」
   1. 外表上是java.lang.ArrayStoreException: sun.reflect.annotation.TypeNotPresentExceptionProxy，但是实际上还是Jar包的冲突问题


## 三、解决Jar包冲突
1. 安装maven helper插件，使用dependency Analyzer，进行分析
2. 尽量选择直接冲突的Jar包进行排除，而不要排除上一级的包。
   例如，目前的依赖关系是 A -- B -- C，C包冲突了，尽量在B中排除C，而不是在A中排除B
3. 去官方的[maven仓库](https://mvnrepository.com/)，看版本之间的映射关系，尽量选择项目中已经存在过的其他版本的包进行依赖，可以解决一些问题，在引入Jar包指定版本的时候可以参考
4. 一种极端的做法是，A包冲突了，在项目文件中涉及到该包的所有文件全部排除，然后在下面单独直接指定一个A包。
