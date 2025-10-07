# Go语言学习（Java程序员视角）




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
   
   - 将一个整数值转换为字符串，值按照文字符号类型解读
     ```go
     fmt.Println(string(65)) // "A"
     // 非法
     fmt.Println(string(1111111165)) // �
     ```
   - 无类型常量：有些常量在声明是是无类型的，它维持了较高的精度（方便在后续可以转换），具体类型包括6种
   - Go的数据类型分为4大类
     - 基础类型：数字、字符串、布尔类型
       - 整数：int8、int16、int32、int64、uint8、uint16、uint32、uint64、int、uint
       - 浮点数：float32、float64
       - 复数：complex64、complex128（内部分别是两个float32、float64组成实部和虚部）
       - 布尔值：true、false，无法被转换为数值
       - 字符串：string
     - 聚合类型：数组、slice、map、结构体
       - 数组：长度不可变，`[2]int`与`[3]int`是不同的数组，同长度同类型的数组可以进行直接比较（比较的是里面元素的内容是否相等），go中的数组是值传递
       - slice：`[]int`长度可变的，底层数据结构用到了数组，不能比较
       - map：
       - 结构体：
     - 引用类型：指针、slice、map、函数、通道channel
     - 接口类型
     
4. 常用数据结构及算法题的使用
   - 常用集合
     - 数组（固定长度的slice）：`var arr [3]int`
     - slice：`var arr []int`，`make([]int, len, cap)`
   - 标准模版
     - math包
       - `math.Exp(x)`：自然底数e的x次方
       - `math.NaN`：作为一种信号值，与任何值的比较都是不相等，包括其自身
     - 
   - 输入输出
     - 字符串处理
       - 字符串获取字符，直接使用`[]`获取就可以
         ```go
         s := "hello world"
         fmt.Println(s[5:7])
         ```
       - 字符串比较：go的字符串可以直接按照字典序比较，使用`>`和`<`和`==`等
       - 字符串内部不可变，字符串内部的值无法修改`s[0] = 'a'`无法赋值
     - strings包：搜索、替换、比较、修整、切分与连接字符串
     - bytes包：
       - `bytes.Buffer`类似Java的`StringBuilder`
         ```go
         var buf bytes.Buffer 
         buf.writeByte('[')
         buf.writeString("a,b")
         buf.writeByte(']')
         ```
       - 其他常用api
         - `func Contains(s, subslice []byte) bool`
         - `func Conut(s, sep[] byte) int`
         - `func Fields(s []byte) [][]byte`
         - `func HasPrefix(s, prefix []byte) bool`
         - `func Join(s [][]byte, sep []byte) []byte`
     - strconv包
       - 整数与数字转换
         ```go
         strconv.Itoa() // Integer to ASCII
         strconv.Atoi() // ASCII to Integer
         strconv.ParseInt("123", 10, 64) // 将字符串转换成10进制的int64
         ```
       - 数字与整数转换
     - unicode包：`IsDigit`、`IsLetter`、`IsUpper`、`IsLower`
5. 项目中使用的特殊注意事项
   - `fmt.Printf()`可以使用`%[1]`这种形式重复使用某一个变量
     ```go
     import "fmt"

     const (
         str1 = "string1"
         str2 = "string2"
     )
     
     func main() {
         fmt.Printf("第一个字符串：%v，第一个字符串第二遍%[1]v，第二个字符串第一遍%v", str1, str2)
         // 第一个字符串：string1，第一个字符串第二遍string1， 第二个字符串第一遍string2
     }
     ```
   - go项目的结构
     ```txt
     | ---- goProject
                 | ---- src
                         | ---- go_code 
                                    | ---- project01
                                               | ---- main
                                                        | ---- hello.go
                                               | ---- package
     ```
     - 所有的go文件都必须归属于一个包
   - 
6. 



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
2. 当编译器遇到一个名字的引用时，将从最内层的封闭词法块到全局寻找其声明
3. Go语言的子串生成，是借助原字符串的，所以子串生成挺高效的
   ```go
   s := "hello_world"
   hello := s[:5]
   world := s[7:]
   // 底层原理上，s是底层唯一的真实数据结构
   // hello是将头指针指向h，len=5
   // world是将头指针指向w，len=5
   //  h e l l o _ w o r l d
   //  ^           ^
   //  |           |---- world len:5
   //  |---- s len:12
   //  |---- hello len:5
   ```

