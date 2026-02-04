# Git提交格式规范

## 一、git提交规范
1. git在提交代码的时候需要填写message，该部分可以指定固定格式
2. 目前相对普遍使用的是`Angular`规范，该规范的基本内容如下：
   - 基本格式：`[type(optinal scope):description] [optional body] [optional footer(s)]`
   - type字段：【必填】表明本次提交的类型
   - scope字段：【可选】可选内容，表明本次修改的代码位置
   - description字段：【必填】本次修改的具体描述
   - body字段：【可选】正文
   - footer字段：【可选】脚注
3. type字段的可选值
   - feat：新实现的功能
   - fix：修复bug
   - style：修改了代码的格式（换行空格等）
   - docs：修改了md文件或者其他描述性文件
   - refactor：重构代码，不影响现有的功能
   - test：新增测试用例
   - perf：提升性能
   - chore：不在上述修改范围的其他修改
4. scope字段的可选值：视图层、控制层、docs、config, plugin
5. description字段的可选值：简单说明修改的内容
6. body字段：进一步说明修改的具体内容是什么
7. footer字段：脚注
8. 示例：`feat(登陆相关):实现登陆校验` 或 `fix(类型转换):解决NPE`

## 二、Idea工具
可以使用Git Commit Template插件方便快速生成git信息


参考文档：
1. https://www.conventionalcommits.org/zh-hans/v1.0.0/#%e7%ba%a6%e5%ae%9a%e5%bc%8f%e6%8f%90%e4%ba%a4%e8%a7%84%e8%8c%83
2. https://juejin.cn/post/7126022242508472351
