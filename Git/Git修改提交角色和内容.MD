# Git修改提交角色和内容

## 一、git修改<font color='yellow'>历史</font>某一次提交
1. 基本流程
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
2. 


## 


参考文档
1. https://blog.csdn.net/weixin_43553153/article/details/134636003