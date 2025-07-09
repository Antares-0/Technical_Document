# Docker常用命令


## 一、Docker基础命令
1. 查看Docker镜像
   ```bash
   docker images
   ```
2. 进入容器内部
   ```bash
   docker exec -it [容器ID] bash
   ```
3. docker打标签
   ```bash
   docker tag [id] my_halo:0.0.2
   ```
4. docker查看正在运行的镜像
   ```bash
   docker ps
   ```

## 二、Docker-compose命令
1. 安装Docker-compose：注意docker-compose与docker要有对应的版本
   ```bash
   # 安装docker
   sudo dnf install docker-ce-24.0.6 docker-ce-cli-24.0.6 containerd.io
   # 安装docker-compose
   sudo curl -SL https://github.com/docker/compose/releases/download/v2.20.3/docker-compose-linux-x86_64 -o /usr/local/lib/docker/cli-plugins/docker-compose
   # 验证docker和docker-compose版本
   docker compose version
   docker --verison
   ```
2. 创建docker-compose.yaml文档
3. 运行：
   ```bash
   # 添加权限
   sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
   # 执行命令 (-d 在后台运行)
   docker-compose up -d
   ```
4. docker-compose服务管理
   - 查看运行中的容器和服务
     ```bash
     docker-compose ps
     ```
   - 停止和移除服务
     ```bash
     docker-compose stop
     ```

