# 大模型算法技术总纲（AI补全版）


## 一、嵌入层相关
1. Token Embedding（词元嵌入）
    - 将离散的 token（词/子词）映射到连续的稠密向量空间，是语言模型理解文本的入口
    - 常用方法：
        - Word2Vec（Skip-gram / CBOW）：基于上下文的静态词向量训练方法
        - GloVe：基于全局词共现矩阵分解的词向量方法
        - FastText：引入子词（subword）信息的词向量，能处理 OOV（词表外）词
    - 在大模型中，词嵌入矩阵通常与语言模型头（LM Head）权重共享（Weight Tying），减少参数量并提升效果
    - 嵌入维度设计：嵌入维度 `d_model` 通常随模型规模增大而增大（如 GPT-3 175B 为 12288，LLaMA 7B 为 4096）。对于典型的 decoder-only 架构，参数量与维度近似满足 `N ≈ 12 × L × d²`（L 为层数），即 `d ≈ √(N / (12L))`
2. Subword Tokenization（子词分词）
    - BPE（Byte Pair Encoding）：从字符级别开始，迭代合并最高频的相邻 token 对，最终得到子词词表
    - WordPiece：类似 BPE，但合并依据是互信息最大化的语言模型似然增益
    - SentencePiece / Unigram LM：基于单语言模型损失，以 EM 算法迭代剪枝词表；不依赖空格分割，天然支持多语言
    - 主流大模型使用的分词器：GPT 系列用 BPE，BERT 用 WordPiece，LLaMA 用 SentencePiece（BPE）
    - 词表大小选择：通常为 32K~256K，词表过大导致嵌入层参数量膨胀和 softmax 开销，过小则增加序列长度和计算量
3. 其他嵌入技术
    - 相对位置偏置（T5 Bias / ALiBi）：不在输入层加位置编码，而是在注意力分数计算时加上与位置差相关的偏置
    - Ngram Embedding（如 Google 的 ngram 特征）：在传统 NLP 中用于捕捉短语级别的语义
    - Embedding Dropout：对嵌入向量施加 Dropout（通常 `p = 0.1`），是微调阶段常用的正则化手段


## 二、位置编码相关
1. 正余弦编码（Sinusoidal Positional Encoding）
    - 出自 `Attention Is All You Need`，使用固定频率的正弦和余弦函数生成位置编码
    - 公式：
      $$
      PE_{(pos, 2i)} = \sin\left(\frac{pos}{10000^{2i/d_{\text{model}}}}\right), \quad
      PE_{(pos, 2i+1)} = \cos\left(\frac{pos}{10000^{2i/d_{\text{model}}}}\right)
      $$
    - 优点：不需要学习参数，且能外推到比训练时更长的序列
    - 缺点：位置编码与词嵌入相加，可能干扰语义信息；对序列长度的外推能力仍然有限
2. 可学习的位置编码（Learnable Positional Encoding）
    - 将位置编码作为一个可训练的参数矩阵 `[max_seq_len, d_model]`，随模型一起训练
    - 代表模型：BERT、GPT-2、GPT-3
    - 优点：灵活，模型可以自行学习适合任务的位置表示
    - 缺点：`max_seq_len` 固定，无法外推到更长的序列（需要插值或微调）
3. 旋转位置编码（Rotary Position Embedding, RoPE）
    - 论文：RoFormer（https://arxiv.org/pdf/2104.09864v2）
    - 核心思想：对 query 和 key 向量施加旋转矩阵变换，使得注意力分数自然包含相对位置信息
    - 数学表达：将 `(q, k)` 视为复数，在复平面上按位置角度旋转：
      $$
      f_q(x_m, m) = (W_q x_m) e^{im\theta}, \quad
      f_k(x_n, n) = (W_k x_n) e^{in\theta}
      $$
    - 关键性质：
        - 内积仅依赖于相对位置 `m-n`（旋转矩阵的乘法具有群结构）
        - 支持序列长度的外推（位置间距离越远，内积自然衰减）
        - 在 LLaMA、Mistral、Qwen、Gemma 等主流大模型中广泛采用
    - 改进方案进一步提升了 RoPE 的长序列外推能力

4. ALiBi（Attention with Linear Biases）
    - 核心思想：不在输入层添加位置编码，而是直接在注意力分数上施加与 token 距离成线性比例的惩罚偏置
    - 公式：`Attention(Q, K, V) = softmax(QK^T / √d + m · [-|i-j|]) · V`
        - 其中 `m` 为每层不同的斜率系数（head-specific slope），随着 head 索引增加按几何级数递减
    - 优势：训练序列长度短，推理时可平滑外推到极长序列（如 2048 → 8192），无额外参数
    - 代表模型：BlenderBot、GPT-3 的某些变体
    - 局限：线性偏置对外推能力的提升有限，已被 RoPE + 扩展方案取代

5. 长上下文扩展技术
    - Position Interpolation（PI，位置插值）：将 RoPE 的旋转频率按比例缩放，使得 `[0, L_new]` 映射到 `[0, L_old]`
        - 公式：`f'_q(x_m, m) = f_q(x_m, m · L_old / L_new)`
        - 优势：只需很少的微调即可将上下文从 2K 扩展到 32K+
    - NTK-aware RoPE：通过调整 RoPE 的基频（base frequency），保留高频分辨率的同时扩展低频的周期
        - 将 `θ_i = 10000^{-2i/d}` 修改为 `θ_i = (α · 10000)^{-2i/d}`，其中 `α` 为缩放因子
        - 优势：无需微调即可直接外推到更长序列
    - YaRN（Yet another RoPE extensioN）：结合 PI 和 NTK-aware，引入 ramp 函数在高低频之间平滑过渡，并通过 `temperature` 调整注意力分布
    - YaRN 适配（DeepSeek-V2 的 128K 上下文方案）：在 YaRN 基础上针对 MLA 架构调整缩放参数和 ramp 策略，实现单次训练支持 128K 上下文


## 三、模型宏观架构
1. MoE 模型与稠密模型
    - 稠密模型（Dense Model）：每个 token 经过所有 Transformer 层的全部参数计算，参数量和计算量直接挂钩
    - MoE（Mixture of Experts, 混合专家模型）：
        - 每个 FFN 层替换为多个"专家"子网络，由门控网络（Router）选择 Top-K 个专家激活
        - 代表模型：Mixtral 8×7B（每层 8 个专家，每 token 激活 2 个）、DeepSeek-V2、Qwen2-MoE
        - 优势：在相同总参数量下，单 token 计算量远低于稠密模型，推理效率更高
        - 挑战：负载均衡（专家坍缩）、通信开销、训练稳定性
    - MoE 的负载均衡损失：
      $$
      \mathcal{L}_{\text{balance}} = \alpha \cdot N \sum_{i=1}^{N} f_i \cdot P_i
      $$
      其中 `f_i` 是分配给第 `i` 个专家的 token 比例，`P_i` 是门控网络分配给第 `i` 个专家的平均概率
    - DeepSeek MoE 创新：采用细粒度专家分割 + 共享专家设计，将标准 FFN 拆分为更细粒度的专家并保留一个共享专家处理通用知识，提升专家利用率
    - Router 策略对比：
        - Top-2 Router（Mixtral）：简单有效，每 token 激活 2 个专家
        - Top-1 Router（Switch Transformer）：计算效率最高，但负载更难均衡
        - Expert Choice（EC）：由专家选择 token 而非 token 选择专家，天然实现完美负载均衡

2. 编码器架构、解码器架构、编码器-解码器架构
    - 编码器架构（Encoder-Only）：
        - 双向注意力（Bidirectional Attention），每个 token 能看到所有位置的上下文
        - 代表模型：BERT、RoBERTa、ALBERT
        - 适用场景：文本分类、序列标注、句子对匹配等自然语言理解任务
    - 解码器架构（Decoder-Only）：
        - 因果注意力（Causal / Autoregressive Attention），每个 token 只能看到当前位置及之前的 token
        - 代表模型：GPT 系列、LLaMA、Qwen、Mistral
        - 适用场景：文本生成、对话、代码生成等自回归生成任务
        - 目前的主流趋势：几乎所有前沿大模型（GPT-4、Claude、Gemini）均采用 Decoder-Only 架构
    - 编码器-解码器架构（Encoder-Decoder）：
        - 编码器（双向注意力）对输入序列编码，解码器（交叉注意力 + 因果注意力）逐步生成输出
        - 代表模型：T5、BART、UL2
        - 适用场景：机器翻译、文本摘要、语音识别等序列到序列的生成任务

3. 注意力替代架构：State Space Models（SSM）
    - 背景：Transformer 的 `O(n²)` 注意力复杂度成为长序列推理的瓶颈，SSM 以 `O(n)` 复杂度实现序列建模
    - Mamba（Selective State Space Model）：
        - 核心创新：将 SSM 的参数（∆, A, B, C）改为输入相关的选择机制，使模型能根据输入内容"记住"或"忽略"信息
        - 架构：无需注意力，仅有 SSM 层 + 门控 MLP，线性复杂度 `O(n)`
        - 优势：在长序列（如 100K+）推理时吞吐量大幅超越 Transformer
        - 局限：硬件亲和性不如注意力（需要特殊的 CUDA kernel 实现并行扫描）
    - Mamba-2：
        - 将 SSM 重新形式化为结构化状态空间对偶性（SSD），统一了 SSM 和注意力机制的理论框架
        - 使用更大的 head 维度（从 16 → 64），提升了硬件利用率
    - RWKV（Receptance Weighted Key Value）：
        - 将 Transformer 与 RNN 的优势结合：训练时用 Transformer 模式（并行），推理时用 RNN 模式（逐 token O(1) 状态更新）
        - 核心机制：WKV 算子实现了类似注意力但具有线性复杂度的 token 交互
    - xLSTM：
        - 将 LSTM 升级为现代化版本，引入两种变体：sLSTM（标量记忆 + 记忆混合）和 mLSTM（矩阵记忆，可并行化），配合指数门控和归一化策略
        - 在同等参数量下可与 Transformer / Mamba 竞争

4. DeepSeek Multi-Head Latent Attention（MLA）
    - 问题：标准 MHA/GQA 在推理时 KV Cache 仍占用大量显存
    - 核心思想：对 KV 进行低秩压缩（映射到低维潜在空间），推理时仅需缓存压缩后的潜在向量
    - 公式：`k = W_{UK} · (W_{DK} · h)`，`v = W_{UV} · (W_{DV} · h)`，其中 `W_{DK}`、`W_{DV}` 为降维投影，`W_{UK}`、`W_{UV}` 为升维投影
    - 效果：KV Cache 量减少到 GQA 的约 1/4 ~ 1/8，且模型质量不降反升（通过增加压缩维度补偿信息损失）
    - 代表模型：DeepSeek-V2 / V3

5. 思维链的产生（Chain-of-Thought, CoT）
    - 定义：通过在提示中展示多步推理过程，引导模型在生成答案前先生成中间推理步骤
    - Few-shot CoT：在 prompt 中提供若干包含推理过程的示例
    - Zero-shot CoT：直接使用 "Let's think step by step" 等触发词诱导模型推理
    - CoT 的关键发现：
        - 模型参数量需达到约 100B 以上才会涌现可靠的 CoT 能力
        - CoT 能显著提升数学、逻辑、符号推理等复杂任务的准确率
        - CoT 的推理链越长，模型越容易产生中间错误累积
    - 变体方法：
        - Self-Consistency：多次采样 CoT 路径，投票选择最一致的答案
        - Tree-of-Thought（ToT）：将推理过程组织为树形搜索，允许回溯和分支
        - Graph-of-Thought（GoT）：更灵活的有向图推理结构
        - Chain-of-Thought with Self-Verification：模型在推理后自我校验中间步骤


## 四、注意力机制优化
1. MHA、MQA、GQA
    - MHA（Multi-Head Attention）：Transformer 原始注意力方案，多头注意力机制
        - 将 query、key、value 分别拆分为 `h` 个头，每个头独立计算注意力后拼接
        - 参数量和计算量均为标准的 `O(n^2)` 复杂度
    - MQA（Multi-Query Attention）：多查询注意力机制
        - 所有 query 头共享同一组 key 和 value（仅有 1 组 key/value），大幅减少 KV 缓存和显存占用
        - 论文：https://arxiv.org/pdf/1911.02150
        - 在推理时 KV cache 量减少到 MHA 的 `1/h`，适合大模型的推理加速
        - 代价：模型质量略有下降（由于 key/value 表示能力减弱）
    - GQA（Grouped-Query Attention）：分组查询注意力机制
        - MHA 和 MQA 的折中方案：将 query 头分为 `G` 组，每组共享一组 key/value
        - 论文：https://arxiv.org/pdf/2305.13245
        - 当 `G = h` 时退化为 MHA，当 `G = 1` 时退化为 MQA
        - LLaMA 2-70B、LLaMA 3、Gemma 等模型采用 GQA，在质量和推理效率间取得平衡
        - 典型配置：`h=32, G=8`（每组 4 个 query 头共享 1 组 key/value）

2. 线性注意力机制、稀疏注意力机制
    - 线性注意力机制 Linformer
        - 线性注意力机制：计算注意力机制的计算复杂度是 `O(k * n)`，能够大幅度降低计算注意力机制的时间复杂度
        - 实现的数学原理：论文中对大部分注意力矩阵进行了谱分析，认为大部分注意力矩阵是低秩的，大部分的奇异值很小，信息集中在前面 `k` 个主成分上
        - 实现方案：直接对每个注意力矩阵做奇异值分解不现实，于是增加了两个可学习的线性层，把 K、V 在"序列长度"维度从 `n` 压缩到 `k`，于是新增加了两个线性层 `E_i` 和 `F_i`，将原来的维度进行压缩
          $$
          \begin{aligned}
          \overline{\text{head}}_i &= \text{Attention}(QW_i^Q, E_iKW_i^K, F_iVW_i^V) \\
          &= \underbrace{\text{softmax}\left( \frac{QW_i^Q (E_iKW_i^K)^T}{\sqrt{d_k}} \right)}_{\bar{P}:n \times k} \cdot \underbrace{F_iVW_i^V}_{k \times d},
          \end{aligned}
          $$

          | 矩阵名称 | 原矩阵维度参数 | 现矩阵维度参数 |
                 |:------:|:---------------------------------:|:---------------------------------:|
          | Q矩阵  | `[batch_size, seq_len, d_model]`  | `[batch_size, seq_len, d_model]`  |
          | K矩阵  | `[batch_size, seq_len, d_model]`  | `[batch_size, k, d_model]`        |
          | V矩阵  | `[batch_size, seq_len, d_model]`  | `[batch_size, k, d_model]`        |
        - 简单描述：增加了一个线性层对 K 和 V 矩阵进行压缩，但是 Q 矩阵不处理，也就是 `n` 个词元去查询 `k` 个待关注的对象，本质上是减少了关注的范围

    - 稀疏注意力机制 Sparse Transformers
        - 稠密自注意力机制：之前各种模型 Transformer 和 GPT 的注意力机制都是计算当前词元和其他所有词元之间的相关性，计算相关性的矩阵是"满"的，也就是稠密注意力机制
            - 每次计算注意力，需要计算当前元素和之前所有元素之间的关系，也就是至少 `n^2` 的复杂度计算，在超长上下文序列下，计算成本太高了
            - 研究人员在研究图片注意力机制时发现，注意力机制本身就是"有限"的，并不是稠密的注意力，每一个像素点在不同层训练时关注的内容不一样
            - 既然本来就不是全都注意，那是不是可以削弱注意力机制，用部分注意力代替全部，以节省算力？基于这种思想，诞生了稀疏注意力机制的思路
        - 稀疏自注意力机制：GPT-3 不再使用当前词元计算和其他所有词元之间的相关性，以此在能够保证训练效果的基础上适当降低训练成本
            - 设计思想：降低注意力关注的范围，正如 Transformer 论文展望的那样，计算"部分"注意力机制以适配更长的上下文场景
            - 稀疏自注意力机制设计原则：保证在固定次跳跃后，能够关注到全部应该关注的内容
            - 二重分解注意力机制：
                - 跨步注意力机制：只关注最近的 `k` 个、从当前开始的每 `k` 个都加上关注；通过这种设计，能够保证在当前节点之间的所有节点，最短在 2 步都能达到
                - 固定步长注意力机制：只关注最近的 `x % k` 个、每 `x % k = 0` 的位置都加上关注；通过这种设计，能够保证在当前节点之间的所有节点，最短在 2 步都能达到
            - 两种注意力机制使用方法：
                - 多层交替使用：在神经网络的不同层中交替使用分解过的注意力机制
                - 单头复合使用：在神经网络中的某一层或某一头同时应用双重分解注意力机制

3. FlashAttention
    - 核心问题：标准注意力计算需要将完整的 `S = QK^T` 矩阵（`n × n`）写入 HBM，产生大量显存读写开销
    - FlashAttention（v1）：通过 tiling（分块） 和 kernel fusion（核融合），在不将完整注意力矩阵写入 HBM 的前提下，在 SRAM 中分块计算精确注意力
        - 前向过程：将 Q、K、V 分块，在 SRAM 中逐一加载并计算分块 softmax
        - 使用 online softmax 技巧（分两趟扫描）保证数值精度
        - 加速比：HBM 读写从 `O(n^2)` 降低到 `O(n^2 / M)`（M 为 SRAM 大小）
    - FlashAttention（v2）：
        - 减少非矩阵运算操作（如 rescaling），减少 CUDA kernel launch 次数
        - 在计算分块注意力时不对 mask 做条件判断，使用 warp-level 优化
        - 相比 v1 约 2 倍加速
    - FlashAttention（v3 / FA3）：
        - 利用 Hopper 架构的 Tensor Core 和异步拷贝指令（TMA），进一步减少同步开销
        - 在 FP8 精度下实现更高的计算吞吐
    - FlashAttention 变体：
        - FlashDecoding：针对长序列推理场景优化，将 Q 分块并行计算，避免 Key 过长时的缓存压力
        - PageAttention / vLLM：将 KV cache 分页管理，解决推理时的显存碎片和缓存管理问题

4. 其他注意力优化
    - Sliding Window Attention（滑动窗口注意力）：如 Mistral、LongFormer，只在固定大小的局部窗口内计算注意力，复杂度 `O(n × w)`（w 为窗口大小）
    - Dilated Attention（空洞注意力）：在滑动窗口中引入空洞步长，增大有效感受野


## 五、稳定梯度传播的策略
1. 归一化位置——Pre-Norm、Post-Norm
    - Post-Norm（原始 Transformer 方案）：
        - 归一化放在残差连接之后：`output = LayerNorm(x + Sublayer(x))`
        - 优点：理论上界清晰，原始 Transformer 证明有效
        - 缺点：在深层网络中容易出现梯度爆炸，需要 warmup 学习率调度
    - Pre-Norm（当前主流方案）：
        - 归一化放在残差连接之前：`output = x + Sublayer(LayerNorm(x))`
        - 优点：训练更稳定，对深层网络和较大学习率更鲁棒，无需 warmup 也可收敛
        - 缺点：残差路径直接将输入相加，可能会削弱归一化的效果
        - 代表模型：GPT-3、LLaMA、Mistral、PaLM
    - Sandwich-Norm（夹层归一化）：
        - 在子层前后都做归一化：`output = LayerNorm(x + Sublayer(LayerNorm(x)))`
        - 用于 T5 等模型，兼顾稳定性和表达力

2. 归一化策略——BatchNorm、LayerNorm、RMSNorm
    - BatchNorm（批归一化）：
        - 在 batch 维度上对每个特征做归一化：`μ_B, σ²_B` 基于当前 batch 计算
        - 训练时使用 mini-batch 统计量，推理时使用全局运行均值/方差
        - 在 CV 领域效果显著，但在 NLP 中表现不佳（序列长度变长导致统计量不稳定）
        - 不适用于 RNN / Transformer（序列长度不一，batch 间统计量差异大）
    - LayerNorm（层归一化）：
        - 在特征维度上对每个样本独立做归一化：`μ_L, σ²_L` 基于当前 token 的所有特征计算
        - 公式：
          $$
          \text{LayerNorm}(x) = \frac{x - \mu}{\sqrt{\sigma^2 + \epsilon}} \cdot \gamma + \beta
          $$
        - 优势：不受 batch size 影响，适合变长序列；Transformer 的标准归一化方法
    - RMSNorm（均方根归一化）：
        - LayerNorm 的简化版本，只对均方根做归一化，不做均值平移：
          $$
          \text{RMSNorm}(x) = \frac{x}{\sqrt{\frac{1}{d}\sum_{i=1}^{d} x_i^2 + \epsilon}} \cdot \gamma
          $$
        - 优势：省去了均值计算，约节省 30%~40% 的归一化计算量
        - 代表模型：LLaMA、Gemma、Mistral 均采用 RMSNorm

3. 激活函数——ReLU、SwiGLU、GeLU
    - ReLU（Rectified Linear Unit）：
        - `ReLU(x) = max(0, x)`
        - 优势：计算简单，稀疏激活，缓解梯度消失
        - 劣势：Dead ReLU 问题，输出均值不为零
    - GeLU（Gaussian Error Linear Unit）：
        - `GeLU(x) = x · Φ(x)`，其中 Φ 为标准正态分布的累积分布函数
        - 近似实现：`GeLU(x) ≈ 0.5x(1 + tanh(√(2/π)(x + 0.044715x³)))`
        - 优势：比 ReLU 更平滑，BERT、GPT-3 等经典模型采用
    - SwiGLU（Swish-Gated Linear Unit）：
        - 结合 Swish 激活和门控线性单元：`SwiGLU(x) = Swish(xW_g) ⊗ (xW_u)`
        - Swish 函数：`Swish(x) = x · σ(βx)`（β 可学习或固定为 1）
        - 优势：在相同参数量下比 ReLU/GeLU 效果更好，但增加了额外的线性投影
        - 代表模型：LLaMA 2/3、PaLM、Gemini 均采用 SwiGLU
    - 其他激活函数：
        - GLU 变体：ReGLU（ReLU + GLU）、GeGLU（GeLU + GLU）
        - SwiGLU 与 GLU 的参数量关系：标准 SwiGLU 的中间维度为 `8/3 d`（约为 2.67 倍），而非标准 FFN 的 4 倍

4. 初始化方法与残差缩放
    - DeepNet 初始化（Microsoft，用于 1000 层 Transformer）：
        - 在残差连接中引入缩放因子 `α`，使信号可以在超深层网络中稳定传播
        - 公式：`output = x + α · Sublayer(LayerNorm(x))`，其中 `α ≈ 1/√(2·num_layers)`
        - 效果：可稳定训练 1000 层 Transformer，无需 warmup
    - QK-Norm：
        - 对 Query 和 Key 的 head 输出做 LayerNorm 或 RMSNorm，防止注意力 logit 方差过大
        - 公式：`Attention = softmax(QK-Norm(Q) · QK-Norm(K)^T / √d)`
        - 代表模型：PaLM、Gemini、LLaMA 3（部分层）
        - 效果：提高大学习率下的训练稳定性，减少注意力熵坍塌
    - z-loss（PaLM）：
        - 在 softmax logit 上添加辅助损失，惩罚 logit 的绝对值过大
        - 公式：`L_z = 1e-4 · log(Σ exp(z_i))²`，施加在 final logits 上
        - 效果：防止 logit 极端增长，稳定训练
    - Gradient Clipping（梯度裁剪）：
        - 当梯度范数超过阈值时缩放到阈值，防止梯度爆炸
        - 公式：`g = g · min(1, clip_value / ||g||)`
        - 大模型典型值：`clip_value = 1.0`（LLaMA）、`clip_value = 0.3`（PaLM）

5. Gradient Checkpointing（梯度检查点）
    - 在前向传播中丢弃中间激活值，反向传播时重新计算，以计算换显存
    - 可节省约 50%~80% 的激活显存，增加约 20%~30% 的计算开销
    - 在单 GPU 显存受限的大模型训练中广泛使用

6. 通信优化：分布式训练策略
    - ZeRO（Zero Redundancy Optimizer）：
        - ZeRO-1：仅分片优化器状态（Adam 状态的 12N 字节在 G 卡间均分）
        - ZeRO-2：分片优化器状态 + 梯度
        - ZeRO-3：分片优化器状态 + 梯度 + 模型参数，每卡显存占用降为约 16N/G 字节（G 为 GPU 数量），但通信量相应增加
    - FSDP（Fully Sharded Data Parallel）：PyTorch 的原生实现，功能上等价于 ZeRO-3
    - Tensor Parallelism（张量并行）：在 GPU 间拆分单个层的参数矩阵（如按列拆分 QKV），适合单机多卡
    - Pipeline Parallelism（流水线并行）：按层切分模型到不同 GPU，每 GPU 计算一部分层，减少跨机通信


## 六、模型泛化能力提高
1. Dropout 随机失活
    - 训练时以概率 `p` 随机将神经元输出置零，防止神经元之间的共适应（co-adaptation）
    - 推理时按 `1-p` 缩放输出（或使用 inverted dropout，训练时缩放，推理时不变）
    - Dropout 在大模型中的使用：
        - GPT-3 等纯解码器模型通常不使用 Dropout（参数量大，过拟合不显著）
        - BERT 等编码器模型在微调时仍会使用 Dropout（通常 `p = 0.1`）
        - 在 Attention Dropout 中，对注意力权重矩阵施加 Dropout，防止注意力分布过拟合
    - 变体方法：
        - Stochastic Depth（随机深度）：训练时随机跳过整个子层（Dropout 在层级别）
        - DropConnect：随机失活权重而非神经元输出

2. 退火算法（Learning Rate Annealing / Schedule）
    - 在训练过程中动态调整学习率，平衡前期快速收敛和后期精细搜索
    - Warmup + Cosine Decay（预热 + 余弦退火）（GPT-3、LLaMA 等大模型标配）：
        - 前 `W` 步（通常为总步数的 1%~5%）从 0 线性增长到最大学习率 `η_max`
        - 之后按余弦曲线从 `η_max` 衰减到 `η_min`（通常为 0 或 `η_max × 0.1`）
        - 公式：`η_t = η_min + 0.5(η_max - η_min)(1 + cos(π(t - W)/(T - W)))`
    - Inverse Square Root Decay：`η_t = η_0 / √(max(t, W))`，用于 T5 等模型
    - Warmup + Exponential Decay：预热后按指数衰减，用于一些中小规模模型
    - 循环学习率（Cyclical LR）：学习率在区间内周期振荡，帮助跳出局部最优
    - Warmup-Stable-Decay（WSD）：预热后保持恒定学习率，最后阶段快速衰减到 0（如 LLaMA 2 的部分训练阶段）

3. AdamW 优化器
    - Adam（Adaptive Moment Estimation）：
        - 结合 Momentum（一阶矩）和 RMSProp（二阶矩）的梯度自适应优化器
        - 更新公式：
            - `m_t = β₁·m_{t-1} + (1-β₁)·g_t`（动量的指数滑动平均）
            - `v_t = β₂·v_{t-1} + (1-β₂)·g_t²`（梯度平方的指数滑动平均）
            - `θ_{t+1} = θ_t - η · m̂_t / (√v̂_t + ε)`（修正偏差后更新参数）
    - Adam 的问题：L2 正则化与自适应学习率耦合，导致正则化效果不理想
    - AdamW（Adam with Decoupled Weight Decay）：
        - 将 weight decay 从梯度更新中解耦，在参数更新后单独执行：
            - `θ_{t+1} = θ_t - η · m̂_t / (√v̂_t + ε) - η · λ · θ_t`
        - 优势：weight decay 不受自适应学习率影响，正则化效果更稳定
        - 大模型标配优化器：AdamW 是当前绝大多数大模型训练的首选优化器
    - AdamW 的典型超参：`β₁ = 0.9`, `β₂ = 0.95`, `ε = 1e-8`, `weight_decay = 0.1`
    - 其他优化器：
        - Adafactor：对二阶矩估计做低秩分解，节省显存（T5 使用）
        - LION（EvoLved Sign Momentum）：仅使用一阶矩的符号更新，显著节省显存
        - Sophia：基于 Hessian 对角估计的自适应优化器，在大模型上可达到 AdamW 的 2 倍速度

4. 标签平滑（Label Smoothing）
    - 将 one-hot 标签分布替换为平滑分布：`y' = (1 - ε)·y_onehot + ε/K`（K 为类别数）
    - 效果：防止模型对训练标签过度自信，提升泛化能力
    - 典型值：`ε = 0.1`（Transformer 原始配置）

5. 数据增强与数据筛选
    - 文本数据增强：回译（Back Translation）、Span Masking、Token Dropout、MixUp（在表示空间混合样本）
    - 数据质量筛选（在大模型预训练中比数量更关键）：
        - Perplexity 过滤：用已有模型评估数据困惑度，过滤低质量数据
        - MinHash / LSH 去重：检测并移除重复或近似重复文档
        - 分类器过滤：训练质量分类器（如 fastText）筛选高质数据
        - Heuristic 过滤：基于长度、特殊字符比例、语言模型得分等手工规则
    - 课程学习（Curriculum Learning）：训练初期使用简单、高质量数据，后期引入更难、更多样的数据


## 七、大模型推理优化
1. KV Cache 技术
    - 在自回归推理中，每次生成一个 token 时，缓存前面所有 token 的 Key 和 Value 矩阵，避免重复计算
    - 对于 MHA，KV Cache 占用显存为 `2 × batch_size × seq_len × d_model × num_layers × 2 bytes`（FP16）
    - 优化方向：
        - Multi-Query / Grouped-Query Attention：减少 KV Cache 的头数
        - KV Cache 量化：将 KV Cache 从 FP16 量化到 INT8 或 FP8
        - KV Cache 淘汰策略（Eviction）：如 H2O（Heavy Hitter Oracle）、Scissorhands、StreamingLLM 等，丢弃不重要的 KV 条目
        - 共享 Prompt KV Cache：在批处理中复用相同的 system prompt 的 KV Cache（前缀缓存）
        - MLA（Multi-Head Latent Attention）：将 KV 压缩到低维潜在空间，缓存量可减少 70%~85%

2. PagedAttention 与 vLLM
    - 核心问题：KV Cache 在显存中以连续块存储，碎片化严重，且无法动态共享
    - PagedAttention：借鉴操作系统的虚拟内存分页思想，将 KV Cache 划分为固定大小的"块"（page/block）
        - 每个 page 存储固定数量 token（如 16 个）的 KV 向量
        - 通过页表（page table）实现逻辑连续到物理连续的映射
    - vLLM 优势：
        - 接近零碎片：按需分配 page，显存利用率从 40%~60% 提升到 95%+
        - Copy-on-Write（写时复制）：多个 beam 共享相同 prefix 的 KV page 直到分叉
        - 高吞吐批处理：支持数千个序列并行推理
    - 框架：vLLM 已成为大模型推理部署的事实标准框架之一

3. 前缀缓存（Prefix Caching）
    - 将 system prompt 或用户输入前缀的 KV Cache 缓存在内存/显存中
    - 同一前缀被复用时可跳过预填充（prefill）阶段，直接进入解码（decode）阶段
    - 应用场景：多轮对话（历史消息）、批量推理（相同 prompt 模板）
    - 实现方案：vLLM 的 Automatic Prefix Caching、SGLang 的 RadixAttention

4. 投机解码（Speculative Decoding）
    - 用一个小模型（草稿模型）快速生成候选 token，大模型（目标模型）并行验证
    - 在不改变生成质量的前提下，实现 2~3 倍的推理加速
    - 变体：
        - Medusa：在目标模型上添加多个并行的"草稿头"，不需要额外的小模型
        - Lookahead Decoding：使用 Jacobi 迭代并行生成多个 token
        - Self-Speculative Decoding：跳过目标模型的部分层作为草稿模型
        - Eagle / Eagle-2：基于特征层预测的投机解码，利用目标模型的 hidden state 训练草稿头，达到更高接受率

5. 模型量化（Quantization）
    - GPTQ：基于 Hessian 矩阵的后训练量化，对权重做逐层 4-bit 或 3-bit 量化
    - AWQ：激活感知的权重量化，保护对输出敏感的通道不被量化
    - GGUF / llama.cpp：在 CPU/边缘设备上运行的量化推理方案（支持 Q2_K 到 Q8_0 多种级别）
    - FP8 训练与推理：NVIDIA H100 原生支持 FP8 计算，可大幅减少显存占用并提升吞吐

6. 连续批处理（Continuous Batching）
    - 传统批处理：必须等所有序列生成完毕才能退出批次，导致 GPU 利用率不均
    - 连续批处理：每完成一条序列即释放其占用的 KV Cache 并插入新序列，最大化 GPU 利用率
    - 由 ORCA 系统提出，vLLM / TensorRT-LLM / TGI 等推理框架均已支持

7. 推理并行策略
    - Tensor Parallelism（张量并行）：在 GPU 间拆分单层参数矩阵（如按列拆分 QKV 权重），all-reduce 汇聚结果
        - 适用于单机多卡，通信量 `O(d²)`，对 NVLink 等高速互联依赖强
    - Pipeline Parallelism（流水线并行）：按层切分模型到不同 GPU，每 GPU 计算完整层，通过微批次（micro-batch）隐藏通信延迟
        - 跨多机互联时更高效，但存在流水线气泡（pipeline bubble）问题
    - TP + PP + DP 三维并行：Megatron-LM 提出的 3D 并行策略，TP 在节点内、PP 在节点间、DP 跨节点同步
    - 专家并行（Expert Parallelism，EP）：MoE 模型的特有并行，每个专家放置在不同 GPU，all-to-all 通信分发 token


## 八、大模型高效微调技术
1. 混合精度微调（Mixed Precision Training）
    - FP16 混合精度：
        - 前向和反向计算使用 FP16，权重和优化器状态使用 FP32
        - 使用 Loss Scaling 防止梯度下溢
        - 可节省约 50% 显存，加速约 2~3 倍
    - BF16 混合精度：
        - BF16 保留与 FP32 相同的指数位（8 位），动态范围与 FP32 相同
        - 不需要 Loss Scaling，训练更稳定，成为当前大模型训练的主流精度
    - FP8 混合精度（H100 及以上）：
        - 前向使用 FP8（E4M3），反向梯度使用 FP8（E5M2），权重更新使用 FP16/BF16
        - 进一步减少显存占用和通信量

2. 低秩分解——LoRA 与 QLoRA
    - LoRA（Low-Rank Adaptation）：
        - 冻结原始权重，在旁路插入低秩矩阵 `A ∈ ℝ^{d×r}`, `B ∈ ℝ^{r×d}`（`r ≪ d`）
        - 前向计算：`h = W₀x + BAx`，只优化 `A` 和 `B`
        - 优势：
            - 可插拔设计，不同任务可切换不同的 LoRA 权重，基座模型不变
            - 单卡即可微调 7B~13B 模型
            - 推理时可将 LoRA 权重合并到原权重中，零额外推理延迟
        - 超参：`r`（秩，通常 8~64）、`α`（缩放因子，通常 16~32）、`dropout`
    - QLoRA（Quantized LoRA）：
        - 在 LoRA 基础上将基座模型权重量化到 4-bit（NF4 数据类型）
        - 引入双重量化（Double Quantization）对量化常数进一步量化
        - 使用 Paged Optimizer 管理梯度溢出
        - 效果：65B 模型可在单张 48GB GPU 上微调，效果接近全量微调
    - DoRA（Weight-Decomposed Low-Rank Adaptation）：
        - 将权重分解为方向和幅度，仅对方向部分使用 LoRA 学习
        - 比 LoRA 更接近全量微调的学习模式
    - AdaLoRA：根据各参数的重要性自适应地分配 LoRA 秩，不重要维度自动缩减，重要维度分配更多容量

3. Prompt Tuning 与 Prefix Tuning
    - Prompt Tuning：在输入层前添加可学习的 soft prompt（连续向量），仅优化这些 prompt 向量
    - Prefix Tuning：在每一层 Transformer 的 key 和 value 前添加可学习的 prefix 向量
    - P-Tuning v2：在每一层都添加可学习的 prompt 参数，效果接近全量微调

4. Adapter 系列
    - 在 Transformer 层中插入 bottleneck 结构的 Adapter 层（降维→非线性→升维）
    - 早期方法（Adapter 在 LayerNorm 之后），后期简化（Adapter 直接插入残差连接后）
    - AdapterFusion：多个 Adapter 组合使用，共享基座模型参数

5. 其他轻量化微调方法
    - IA³（Infused Adapter by Inhibiting and Amplifying Inner Activations）：
        - 对 key、value、FFN 的中间激活分别乘以可学习的缩放向量 `l_k`、`l_v`、`l_ff`
        - 参数量极少（仅为 LoRA 的百分之一），适合快速适配
    - BitFit：仅微调模型所有 bias 参数（约 0.1% 参数），其他全部冻结
        - 效果：在中小规模任务上可达到接近全量微调的准确率
    - （IA）³ 与 BitFit 对比：参数量极少，但模型容量有限，适用于简单适配任务；LoRA 在复杂任务上更优

6. 指令微调（Instruction Tuning）
    - 核心思想：将各类 NLP 任务统一格式化为"指令 + 输入 + 输出"的形式，在此格式化的数据上微调模型
    - Flan 系列（Flan-T5、Flan-PaLM）：收集 1800+ 任务，转化为指令格式，显著提升零样本泛化能力
    - 数据构建策略：
        - 模板多样化：同一任务使用多种指令表述方式，增强指令跟随能力
        - 任务平衡：采样时对不同规模的任务进行加权，防止高频任务主导
        - 难度混合：混合简单任务（分类）和复杂任务（推理、代码）
    - 与对齐的关系：指令微调是 RLHF/DPO 之前的必要阶段，提供基础的任务遵循能力


## 九、基于人类反馈的强化学习
1. RLHF（Reinforcement Learning from Human Feedback）
    - 整体流程分为三个阶段：
        - SFT（Supervised Fine-Tuning）：在高质量的人类标注数据上对预训练模型进行有监督微调
        - Reward Model（奖励模型）训练：
            - 使用同一 prompt 由 SFT 模型生成多个候选回答
            - 标注员对回答进行排序（而非打分），训练一个奖励模型来预测人类偏好
            - 损失函数为 Bradley-Terry 排序损失：
              $$
              \mathcal{L}_{R} = -\mathbb{E}_{(x, y_w, y_l)}[\log \sigma(r(x, y_w) - r(x, y_l))]
              $$
        - PPO（Proximal Policy Optimization）微调：
            - 以奖励模型的得分为奖励信号，使用 PPO 算法强化学习优化策略模型
            - 损失函数包含三部分：
                - 策略梯度损失（最大化奖励）
                - KL 散度惩罚（防止策略偏离 SFT 模型太远）
                - PPO 裁剪（确保更新步长稳定）
            - 同时引入参考模型（frozen SFT 模型）计算 KL 散度

2. DPO（Direct Preference Optimization）
    - 直接利用偏好对优化策略，无需显式训练奖励模型
    - 核心思想：将 RLHF 中的奖励函数隐式表示为策略模型的对数似然比
    - 损失函数：
      $$
      \mathcal{L}_{DPO} = -\mathbb{E}_{(x, y_w, y_l)}[\log \sigma(\beta \log \frac{\pi_\theta(y_w|x)}{\pi_{ref}(y_w|x)} - \beta \log \frac{\pi_\theta(y_l|x)}{\pi_{ref}(y_l|x)})]
      $$
    - 优势：训练过程简化，不再需要 PPO 的四模型并行（策略、参考、奖励、价值网络）
    - DPO 相比 RLHF 的局限：
        - 对偏好数据质量更敏感
        - 在某些场景下不如 PPO + Reward Model 稳定

3. 其他对齐技术
    - KTO（Kahneman-Tversky Optimization）：仅需要"好/坏"的二分类标签，不需要配对偏好数据
    - IPO（Identity Preference Optimization）：在 DPO 基础上引入正则化项，减少过拟合
    - ORPO（Odds Ratio Preference Optimization）：在 SFT 阶段直接加入偏好对齐损失，不需要单独的对齐阶段
    - RRHF（Rank Responses to align Human Feedback）：将偏好学习建模为排序问题
    - Rejection Sampling：从策略中采样多个回答，选择奖励最高的作为监督信号进行 SFT（如 InstructGPT 使用的方法之一）

4. Constitutional AI（宪法 AI，Anthropic）
    - 动机：RLHF 需要大量昂贵的人工偏好标注，且难以覆盖所有对齐维度
    - 方法：
        1. 监督阶段：给定初始回答，模型根据一组"宪法原则"（如"不要输出有害内容"）进行自我修订，在修订后的数据上微调
        2. RL 阶段：使用 AI 生成的偏好数据（基于宪法原则判断）训练奖励模型，再做 RL 微调
    - 效果：
        - 大幅减少人工标注量（仅需定义宪法原则）
        - 模型在有用性（helpfulness）和无害性（harmlessness）之间取得更好的平衡
        - Claude 系列模型的核心对齐方法

5. RLAIF（Reinforcement Learning from AI Feedback）
    - 使用 LLM（如 GPT-4）替代人类标注员生成偏好对比数据
    - Self-Rewarding：模型自身同时充当生成器和奖励模型，在迭代中自我提升
    - 成本远低于人工标注，但在对抗性和安全性数据上仍有局限

6. GRPO（Group Relative Policy Optimization，DeepSeek-R1）
    - 核心思想：去掉 PPO 中的价值网络（critic）和参考模型，对同一 prompt 采样多个响应分组估计优势
    - 优势计算：`A_i = (r_i - mean(r_group)) / std(r_group)`，基于组内相对表现而非绝对奖励
    - 效果：
        - 大幅减少显存占用（无需价值网络和参考模型）
        - 在 DeepSeek-R1 系列模型中验证有效
    - 扩展：GRPO + CoT 冷启动——先用少量 CoT 数据微调，再用 GRPO 强化学习优化推理过程

7. 奖励模型过优化（Reward Hacking）与缓解
    - Reward Hacking：策略模型学会利用奖励模型的漏洞获得高分（如回复变长、重复无关的安全措辞）
    - 常见缓解手段：
        - KL 散度惩罚：PPO 中的标准做法，约束策略与 SFT 模型的距离
        - 奖励模型集成：使用多个奖励模型投票，减少单一模型被攻破的风险
        - 偏好数据多样性：确保奖励训练数据覆盖广泛场景
        - 在线奖励收集：定期用当前策略生成新数据重新训练奖励模型

8. 迭代式对齐（Iterative Alignment）
    - 单一轮次的 RLHF 通常不够，需要多轮迭代：
        1. SFT → 奖励模型训练 → PPO
        2. 用 PPO 后的模型采样新数据，重新训练奖励模型
        3. 在新奖励模型上再次做 PPO
    - GPT-4 / Claude 等产品级模型均经历了多轮迭代式对齐
    - 在线 vs 离线：在线对齐（采样当前策略的最新数据）通常优于离线（使用固定数据集）


## 十、模型缩放定律
1. Scaling Laws（缩放定律）
    - 核心发现（Kaplan et al., 2020）：
        - 模型性能与参数量 N、数据量 D、计算量 C 之间存在幂律关系
        - 在其他条件不变时，三者越大越好，且相互之间可转换
        - 测试损失 L 与各因素的关系近似：
            - `L(N) ≈ (N_c / N)^{α_N} + L_∞`（α_N ≈ 0.076）
            - `L(D) ≈ (D_c / D)^{α_D} + L_∞`（α_D ≈ 0.095）
            - `L(C) ≈ (C_c / C)^{α_C} + L_∞`（α_C ≈ 0.050）
    - 实践建议：在计算预算有限时，应在模型和数据上按比例投入资源，而非只放大模型

2. Chinchilla 缩放定律（Compute-Optimal Scaling）
    - Hoffmann et al. (2022) 通过更系统的实验发现：之前 Scaling Laws 高估了参数量的重要性
    - 核心结论：对于给定的计算预算 C，存在最优的参数量 N 和 token 量 D 配比，其关系为：
        - 最优 token-参数比：`D/N ≈ 20`（每参数约 20 个 token）
        - 即参数量每翻倍，训练数据量也应翻倍，保持约 20:1 的 token-参数比
    - 推导：由 `C ≈ 6ND` 和 `D ≈ 20N` 可得 `N ≈ √(C/120)`、`D ≈ √(10C/3)`
    - 实际意义：许多大模型（如 GPT-3 175B 仅训练 300B token，token-参数比 < 2）属于严重"欠训练"
    - Chinchilla 模型：70B 参数，训练 1.4T token（恰好约 20:1），在同计算量下性能远超 175B GPT-3

3. 大模型训练的实践缩放公式
    - 计算量估算：`C ≈ 6ND`（其中 N 为参数量，D 为 token 数）
    - 示例：训练一个 7B 模型在 2T token 上，所需计算量约为 `6 × 7e9 × 2e12 ≈ 8.4e22 FLOPs`
    - FLOPS 利用率（MFU）：模型的实际计算吞吐与理论峰值吞吐之比
        - 当前 GPU 训练大模型时 MFU 一般在 40%~60%
    - 损失预测：基于 Scaling Laws 可在小规模实验中预测大模型的最终损失

4. Beyond Scaling Laws
    - Emergent Abilities（涌现能力）：当模型规模超过某个阈值时，突然出现小模型不具备的能力（如 CoT、上下文学习）
    - 数据质量 > 数据数量：最近研究表明，高质量数据的选择比单纯增加数据量更重要
    - 小模型蒸馏：利用大模型生成的数据训练小模型，可在极低成本下获得接近大模型的能力
    - Scaling Law for MoE：MoE 模型的缩放行为与稠密模型有所不同，专家数量的增加带来次线性收益

5. 数据缩放定律（Data Scaling Laws）
    - 对于固定模型大小，性能随数据量增加按幂律提升，但边际收益递减
    - 数据质量幂律：高质量数据的缩放指数（α_D）高于低质量数据，意味着在优质数据上投入更多算力回报率更高
    - 去重与缩放：数据去重（Deduplication）可有效提升缩放斜率，相当于在每个 token 上获得更多"有效信息"

6. 推理时计算缩放（Inference-Time Compute Scaling）
    - 背景：传统 Scaling Laws 关注训练阶段，o1 系列模型揭示了推理阶段也可通过增加计算量提升性能
    - Test-Time Compute Scaling：
        - 扩展思路（思维预算，thinking budget）：通过延长 CoT 推理链、增加采样次数、扩展搜索空间来提升模型能力
        - Scaling Pattern：不同难度的问题需要不同的"推理预算"
    - 搜索策略：
        - 并行搜索（Self-Consistency、Best-of-N）：增加采样数量，性能与 log(N) 成正比
        - 顺序搜索（ToT、MCTS）：在推理过程中动态分配计算资源，对复杂推理任务更高效
        - 混合策略（如 o1 的隐式 CoT）：训练模型自动决定何时"深度思考"、何时快速回答
    - Verifier Scaling：使用验证器（reward model / PRM）评估中间步骤，验证器的性能也遵循缩放定律

7. 多模态缩放定律
    - 多模态模型（如 GPT-4V、Gemini、LLaVA）表现出与纯文本模型不同的缩放行为
    - 模态对齐缩放：视觉与文本编码器之间的对齐质量随数据量增大而提升
    - 数据混合比：图像-文本对与纯文本数据的最优比例随模型规模变化，大模型通常需要更高比例的图像数据
    - 分辨率缩放：高分辨率输入带来更好的视觉理解，但计算成本更高，需要在高分辨率与计算量间平衡


----- 
参考资料汇总
1. 旋转位置编码(RoPE)：https://arxiv.org/pdf/2104.09864v2
2. 线性注意力机制(Linformer)：https://arxiv.org/pdf/2006.04768
3. 稀疏注意力机制(Sparse Transformers)：https://arxiv.org/pdf/1904.10509
4. 多查询注意力机制(MQA)：https://arxiv.org/pdf/1911.02150
5. 分组查询注意力机制(GQA)：https://arxiv.org/pdf/2305.13245
6. FlashAttention：https://arxiv.org/pdf/2205.14135
7. FlashAttention v2：https://arxiv.org/pdf/2307.08691
8. AdamW：https://arxiv.org/pdf/1711.05101
9. LoRA：https://arxiv.org/pdf/2106.09685
10. QLoRA：https://arxiv.org/pdf/2305.14314
11. InstructGPT / RLHF：https://arxiv.org/pdf/2203.02155
12. DPO：https://arxiv.org/pdf/2305.18290
13. Scaling Laws(Kaplan)：https://arxiv.org/pdf/2001.08361
14. Chinchilla Scaling Law：https://arxiv.org/pdf/2203.15556
15. SwiGLU：https://arxiv.org/pdf/2002.05202
16. MoE (GShard)：https://arxiv.org/pdf/2006.16668
17. Pre-Norm vs Post-Norm：https://arxiv.org/pdf/2002.04745
18. Chain-of-Thought：https://arxiv.org/pdf/2201.11903
19. ALiBi：https://arxiv.org/pdf/2108.12409
20. YaRN：https://arxiv.org/pdf/2309.00071
21. Mamba：https://arxiv.org/pdf/2312.00752
22. RWKV：https://arxiv.org/pdf/2305.13048
23. DeepSeek-V2 MLA：https://arxiv.org/pdf/2405.04434
24. PagedAttention / vLLM：https://arxiv.org/pdf/2309.06180
25. Speculative Decoding：https://arxiv.org/pdf/2211.17192
26. Constitutional AI：https://arxiv.org/pdf/2212.08073
27. DeepSeek-R1 / GRPO：https://arxiv.org/pdf/2501.12948
28. DoRA：https://arxiv.org/pdf/2402.09353
29. IA³：https://arxiv.org/pdf/2205.05638
30. BitFit：https://arxiv.org/pdf/2206.04769
31. xLSTM：https://arxiv.org/pdf/2405.04517
32. DeepNet：https://arxiv.org/pdf/2203.00555
33. DeepSeek-R1 / 推理时计算扩展：https://arxiv.org/pdf/2501.12948