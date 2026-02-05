# 大模型部署（Docker + ollama）

## 一、大模型部署基础背景
1. 软件层面：使用了Docker和ollama
2. 硬件层面：一台包含4张A30显卡的Linux机器

## 二、周边知识——ollama
1. ollama介绍：ollama是一个强大的本地推理大模型平台，旨在简化模型的本地部署、管理和推理工作流。它允许用户在本地机器上拉取、管理、运行大模型，并提供多种访问方式，包括本地CLI、HTTP接口以及通过OpenAI客户端的集成。
2. ollama的核心功能包括：
   1. 本地模型管理：ollama支持从官方模型库或自定义模型库拉取预训练模型，并在本地保存和加载。它支持各种流行的模型格式（如 ONNX、PyTorch、TensorFlow）。
   2. 高效推理：通过 GPU/CPU 的加速，ollama 提供高效的模型推理，适合本地化应用或需要控制数据隐私的场景。
   3. 多种接口访问：ollama 支持命令行（CLI）、HTTP 接口访问推理服务，并通过 OpenAI 客户端实现更广泛的集成。
   4. 环境变量配置：通过灵活的环境变量，用户可以自定义推理设备（GPU/CPU）、缓存路径、并发数、日志级别等。
3. 简而言之，ollama是一个能够部署模型，并对外暴露接口实现模型访问的大模型平台，高效集成了大模型相关的使用功能；使用方式类似docker。
4. ollama使用：
   1. 使用docker部署
   ```bash
   docker pull ollama/ollama
   # 默认拉取最新版本的ollama
   ```
   2. docker启动ollama
   ```bash
   # docker run -d --gpus=all -e OLLAMA_KEEP_ALIVE=-1 -e OLLAMA_NUM_PARALLEL=4 -e OLLAMA_FLASH_ATTENTION=1 -p 11434:11434 --name ollama docker.io/ollama/ollama:latest
   docker run -d \ 
   --gpus=all \
   -e OLLAMA_KEEP_ALIVE=-1 \
   -e OLLAMA_NUM_PARALLEL=4 \
   -e OLLAMA_FLASH_ATTENTION=1 \
   -p 11434:11434 \
   --name ollama-vincent \
   docker.io/ollama/ollama
   # -d 标识 后台运行容器（守护进程模式）
   # --gpus=all：向容器暴露宿主机的所有GPU设备
   # -e开头的是设置容器内的环境变量，用于定制ollama的运行规则
   # OLLAMA_KEEP_ALIVE：设置模型常驻内存，不会因为空闲超时被释放
   # OLLAMA_NUM_PARALLEL：设置ollama最大并行推理数为4，允许同时处理4个推理请求，适合多用户/多场景调用，避免单请求阻塞
   # OLLAMA_FLASH_ATTENTION：启用FlashAttention注意力机制（1开启，0关闭），这是大模型的核心优化，能大幅降低GPU显存占用、提升推理速度
   # -p 标识 端口映射p1:p2，将宿主机的p1端口映射到容器中的p2端口
   # --name 标志 设置容器名称
   ```
   3. 使用docker进入ollama
   ```bash
   docker exec -it [镜像id] bash
   ```
   4. 使用ollama拉取模型
   ```bash
   # 在ollama的官网上model一栏，寻找合适的模型，并拉取
   # 拉取llama2模型的13b版本
   ollama pull llama2:13b
   ```
   5. 运行ollama的llama2模型
   ```bash
   # 运行ollama模型
   ollama run llama2:13b
   ```
   6. 进入模型，开始对话
   ```bash
   >>> who are you
   I am LLaMA, an AI assistant developed by Meta AI that can understand and respond to human input in a conversational manner. I am here to help answer any questions you may have or provide information on a wide range of topics. Is there something specific you would like to know or discuss?
   ```
   7. ollama也支持远程调用方式使用模型资源
   ```bash
   # ollama提供远程方式直接调用并使用模型：
   curl http://宿主机ip地址:11434/api/chat -d '{"model": "llama2:13b","messages": [{"role": "user", "content": "帮我计算1加1"}]}'
   ```
5. 其他注意事项
   1. ollama不支持多卡并行计算，因此四张A30显卡只能分别发挥作用，不能同时对一个模型生效

## 三、周边知识——模型大小与显卡性能
1. 基础知识
   1. Model Size：模型参数量，1B代表10亿参数量；1T代表1万亿参数量
   2. VRAM Size：显存大小
2. 显存大小与模型参数关系

    | Model Size |   VRAM   |
    |:----------:|:--------:|
    |    1.5B    |    4G    |
    |     7B     |    8G    |
    |    14B     |   16G    |
3. 常用显卡的显存大小

    | graphics card | VRAM |
    |:-------------:|:----:|
    |     A30       | 24G  |
4. 



参考资料
1. ollama官方网址：https://docs.ollama.com/
2. ollama介绍：https://blog.csdn.net/bluesocks152/article/details/145683901
3. 
4. 