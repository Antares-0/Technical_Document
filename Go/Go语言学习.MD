# Go语言学习（Java程序员视角）


## 一、Go语言核心优势及环境配置
1. 核心优势
   1. go语言的核心优势就是高并发场景
      - 使用go开发的各种应用比如：Docker、k8s、TiDB、InfluxDB 
      - 使用C++开发的应用比如：MySQL、MongoDB 
      - 使用Java开发的应用比如：Hadoop、Spring
   2. 编译型语言、解释型语言
      - 编译型语言：通过预编译转变为机器码，性能较高，Java、Go、C++
      - 解释型语言：逐行解释代码，性能较低，Python、JavaScript
   3. java是值传递，而不是引用传递；go也是值传递，而不是引用传递
      - 值传递：调用函数的时候，将传输的对象复制一份给新函数
      - 引用传递：调用函数的时候，将传输的对象直接给新函数
2. 环境配置
   1. 去[链接](https://go.dev/dl/)下载go的开发包，相当于JDK，安装后使用`go version`确认
   2. 在goland中配置该go开发包
3. Go语言的运行
   - 运行main.go文件
     ```bash
     # 方式一 直接运行
     go run main.go
     # 方式二 两步运行
     go build main.go # 会生成main可执行文件 
     ./main # 直接执行
     ```
   - 【main.go文件的package必须是main】运行报错：`The 'main' file has the non-main package or does not contain the 'main' func`
     ```txt
     go语言的main方法的头，package必须是main，这点跟Java不同，需要注意
     package main
     
     import (
         "fmt"
     )
     ```

## 二、Go语言特性语法
1. go语言的大括号必须与上一个语句在同一行
   ```go
   // right
   for i := 1; i < 10; i++ {
       // inner
   }
   // wrong
   for i := 1; i < 10; i++ 
   {
       // inner
   } 
   ```
2. 一些常用API
   1. 标准输入
      ```go
      // 标准输入
      import "os"
      import "bufio"
      import "fmt"
      func main() {
		  input := bufio.NewScanner(os.Stdin)
          for input.Scan() {
              fmt.Printf(input.Text())
          }
      }
      ```
   2. switch可以没有操作数，相当于多个`if`的直接堆叠
      ```go
      func switchTest(x int) {
          switch {
              case x > 0:
                  return +1
              case x < 0:
                  return -1
              default:
                  return 0
          }
      }
      ```
3. 编程约定（程序结构）：
   - 如果一个实体在函数中声明，它只在函数局部有效。如果声明在函数外，它将对包里面的所有源文件可见。实体的第一个字母的大小写决定其可见性是否跨包。
      ```go
      // fmt.Printf方法，首字母大写，表示包外可见
      ```
   - 包名本身总是由小写字母构成
     ```go
     // fmt包，本身是小写的
     ```
   - 短变量声明：`name := expression`
     - 短变量声明对应的是完整变量声明
       ```go
       // 完整变量声明
       var myValue int = 2
       // 短变量声明
       myValue := 2
       ```
     - 短变量声明不需要声明所有在左边的变量，如果有的变量已经赋值了，那就相当于覆盖
       ```go
       // 第一次声明
       in, err := os.Open(inFileUrl)
       // 第二次，声明out同时覆盖err
       out, err := os.Create(createFileUrl)
       ```
     - 短变量声明最少声明一个新变量，否则编译不通过，这种情况可以直接使用赋值来实现
       ```go
       // 第一次声明
       f, err := os.Open(inFileUrl)
       // 第二次，声明out同时覆盖err
       f, err := os.Create(createFileUrl) // 编译失败
       f, err = os.Create(createFileUrl)
       ```
   - <font color='yellow'>指针（Java程序员知识盲区）：指针的值是一个变量的地址</font>
     - 使用指针的意义在于，可以不知道变量名的情况下间接读取或者更新变量的值
     - 指针家族nameSpace
       ```go
       // & 取地址操作符
       x := 2
       pointer := &x // 获取了x的指针，并命名为pointer
       // pointer的类型是 (* int)，叫做整型指针
       pointerValue := *pointer 
       ```
     - 指针类型的零值是`nil`，也就是说当一个指针类型的变量没有赋值的时候，它的值是`nil`
       ```go
       // pointer的默认值是nil
       var pointer *int
       // 所以判断指针有没有指向一个对象，可以通过 pointer != nil 来确定
       ```
     - 指针是可以比较的，当两个指针指向同一个对象或都是`nil`的时候，相等
       ```go
       var x, y int
       fmt.Println(&x == &y, &x == nil) // false true
       ```
     - 函数返回局部变量的地址是非常安全的
       ```go
       func f() *int {
           x := 2
		   return &x
       }
       ```
   - `new`函数
     - 注意：`new`函数返回的是地址
       ```go
       p := new(int)
       fmt.Println(*p) // 0
       *p = 2
       fmt.Println(*p) // 2
       ```
     - `new`函数只是一种简便写法，方便直接创建一个类型为Type的对象
     - `new`是一个函数，不是一个预设的关键字，所以可以创建名称为`new`的变量
       ```go
       func delta(old, new int) int {
           return new - old
       }
       ```
   - 交换变量
     ```go
     a := 1
     b := 2
     a, b = b, a
     ```
   - 空标识符
     ```go
     // for循环
     // 第一个是index，第二个是具体的值
     // 不需要index的时候也可以写成index, _
     for _, name := range os.Args[1:] {
         // inner
     }
     // 返回值
     _, err = io.Copy(dts, src)
     ```
   - 在任何比较中，第一个操作数和第二个操作数必须是可以赋值的才可以
   - 类型声明：类型声明声明一个新的命名类型，它和某个已有类型使用同样的底层类型，只是一个别名的作用，防止混淆
     - 别名功能
       ```go
       type myType float64
       func getMyType(x myType) {
           return myType(0.66 + 0.88)
       }
       ```
     - 支持计算
       ```go
       myValue := myType(0.9) + myType(0.8)
       ```
   - go的变量声明是可以重名的，这一点与Java部分类似
     - 变量可见性问题1：if中的变量对应着else中也可见
       ```go
       if f, err := os.Open(fname); err != nil {
           return err
       } else {
           // 注意，f和err在这里是可见的！！
           f.Stat()
       }
       ```
     - 变量可见性问题2：一个隐藏的bug
       - go语言环境下，这个问题是这样的：局部变量pwd没有被使用，全局变量也没有被赋值，因为init函数的pwd与全局的pwd是两个变量
         ```go
         var pwd string
         func init() {
             pwd, err := os.Getwd() // 编译错误，程序发现了没有使用的cwd变量
             if err != nil {
                 log.Fatalf("... %v", err)
             }
             // 如果多了下面这行日志，问题就会非常隐蔽了，这时候编译不会报错，因为后面使用到了pwd
             // log.Printf("%s", pwd)
         }
         // 出现问题的原因在于，init函数内部定义了自己的cwd，当init方法内部需要检查cwd有没有用到的时候，编译器报错
         ```
       - go语言环境下，修复这个问题的简单办法：
         ```go
         var pwd string
         func init() {
             var err error
             // 注意到这里是赋值语句，不是声明语句，这样全局变量就被赋值了
             pwd, err = os.Getwd()
             if err != nil {
                 log.Fatalf("%v", err)
             }
         }
         ```
       - java语言环境下，这个问题是这样的
         ```java
         public class student {
             private String name;
             public Student(String name) {
                 // 错误
                 name = name;
                 // 应当是 this.name = name;
             }
         }
         ```
     
4. 常用数据结构及算法题的使用
   - 
5. 项目中使用的特殊注意事项



## 三、Go语言开发工具包
1. Go mod是什么？
   1. go mod是go官方推出的包管理工具，用于管理项目依赖，相当于java的maven和gradle
   2. go mod生成了两个文件
      1. go.mod 用于记录依赖
      2. go.sum 用于校验文件
   3. go mod对应的老版本是GOPATH
      - GOPATH配置模式：选择一个目录作为Go的工作空间，并使得GOPATH环境变量指向它
   4. Go mod常用命令：
      ```bash
      
      # 自动下载依赖
      go mod tidy
      ```
   5. 
2. 


## 四、Go底层原理
1. 编译顺序和初始化顺序
   - 编译器会按照文件名的Unicode代码点顺序（字典序）来处理同一个包下的多个go文件
   - 但是变量初始化和`init()`函数的指定顺序由依赖关系和文件顺序共同决定
   - 包的初始化按照程序中导入的顺序来执行，依赖顺序优先
   - 初始化过程是从下到上的，main包最后初始化
2. 当编译器遇到一个名字的引用是，将从最内层的封闭词法块到全局寻找其声明
3. 

参考资料：
1. 解决goland无法解析git类引入的问题：https://blog.csdn.net/qq_38018994/article/details/125745076
2. 
