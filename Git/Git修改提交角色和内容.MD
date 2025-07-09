# Git修改提交角色和内容

## 一、git修改提交
1. <font color='yellow'>历史</font>某一次提交的修改基本流程
   ```bash
    git log # 查看git提交的历史
    git rebase -i <commit hash>^ # 将git的head切换
    ###### ----- 此时文件会显示出一个文档 ----- ##### 
    # 将 pick 更改为 edit, 保存 
    ###### ----- -------------------- ----- ##### 
    git commit --amend -author "liuxianming@example.com" # 更改提交所属人
    git commit --amend -m "正确的提交" # 更改提交的信息message
    git rebase --continue # 恢复至最初的头节点
   ```
2. <font color='yellow'>当前</font>提交的修改基本流程
   ```bash
    git commit --amend -m "new message" # 修改提交信息
    git commit --amend --author="liuxianming@example.com>" # 修改作者信息
   ```

## 二、git配置提交角色信息
1. 全局配置 - 基本流程
   ```bash
    git config --global user.name 'liuxianming' # 修改提交人name
    git config --global user.email 'liuxianming@example.com' # 修改提交人的email，在公司中通常根据email来确定是不是内部人员
    git config user.email # 校验修改是否成功
    git config user.name # 校验是否修改成功
   ```
2. 项目配置 - 基本流程
   ```bash
    git config user.name "liuxianming" # 修改提交人name
    git config user.email "3016226031@tju.edu.cn" # 修改提交人的email
   ```
3. 项目配置与全局配置的基本关系
   1. git支持多级配置
      - system系统级（安装路径/etc/gitconfig）： 系统级配置文件，对系统中所有用户都普遍适用的配置。使用 git config --system读写的就是这个文件。
      - global用户级（C:/Users/用户名/.gitconfig）： 用户级配置文件，用户目录下的配置文件只适用于该用户。使用 git config --global读写的就是这个文件。
      - local项目级（某仓库的本地路径/.git/config）： 项目级配置文件，当前项目的 git仓库目录中的配置文件（也就是工作目录中的 .git/config 文件）,这里的配置仅仅针对当前项目有效。使用 git config --local或 省略 local参数，读写的就是这个文件。
      - worktree工作区级： 工作区级配置，此配置仅仅针对当前工作区有效。使用 git config --worktree进行配置。
      - 每一个级别的配置都会覆盖上层的相同配置，所以 .git/config 里的配置会覆盖 /etc/gitconfig 中的同名变量。
   2. 优先级：` worktree > local > global > system `
   


参考文档
1. https://blog.csdn.net/weixin_43553153/article/details/134636003
2. https://blog.csdn.net/MPengYu/article/details/129462027