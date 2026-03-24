# Attention Is All You Need
# 只需要注意力机制

**Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Łukasz Kaiser, Illia Polosukhin**
Google Brain

---

## Abstract
The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely.

目前主流的序列转换模型都基于包含编码器和解码器的复杂循环神经网络或卷积神经网络。表现最好的模型同样通过注意力机制连接编码器与解码器。我们提出一种新颖简洁的网络架构 Transformer，完全基于注意力机制，不再使用循环和卷积结构。

Experiments on two machine translation tasks show these models to be superior in quality while being more parallelizable and requiring significantly less time to train. Our model achieves 28.4 BLEU on the WMT 2014 English-to-German translation task, improving over the existing best results, including ensembles, by over 2 BLEU. On the WMT 2014 English-to-French translation task, our model establishes a new single-model state-of-the-art BLEU score of 41.8 after training for 3.5 days on eight GPUs, a small fraction of the training costs of the best models from the literature.

在两个机器翻译任务上的实验表明，这类模型不仅质量更优，而且并行度更高、训练耗时显著更少。我们的模型在 WMT 2014 英德翻译任务上达到 28.4 BLEU，超过包括集成模型在内的现有最佳结果 2 个 BLEU 以上。在 WMT 2014 英法翻译任务上，我们的模型在 8 块 GPU 上训练 3.5 天后达到 41.8 BLEU 的单模型最优结果，训练成本仅为文献中最优模型的一小部分。

We show that the Transformer generalizes well to other tasks by applying it successfully to English constituency parsing both with large and limited training data.

我们还将 Transformer 成功应用于英文句法成分分析任务，证明它在大量和有限训练数据下都能很好地泛化到其他任务。

---

## 1 Introduction
Recurrent neural networks, long short-term memory and gated recurrent neural networks in particular, have been firmly established as state of the art approaches in sequence modeling and transduction problems such as language modeling and machine translation. Numerous efforts have since continued to push the boundaries of recurrent language models and encoder-decoder architectures further.

循环神经网络，尤其是长短期记忆 LSTM 和门控循环网络 GRU，已经成为序列建模与序列转换任务（如语言模型、机器翻译）的公认最优方法。此后大量工作不断推进循环语言模型与编码器-解码器架构的边界。

Recurrent models typically factor computation along the symbol positions of the input and output sequences. Aligning the positions to steps in computation time, they generate a sequence of hidden states \(h_t\), as a function of the previous hidden state \(h_{t-1}\) and the input for position \(t\). This inherently sequential nature precludes parallelization within training examples, which becomes critical at longer sequence lengths, as memory constraints limit batching across examples. Recent work has achieved significant improvements in computational efficiency through factorization tricks and conditional computation, while also improving model performance in the case of the latter. The fundamental constraint of sequential computation, however, remains.

循环模型通常沿着输入与输出序列的符号位置分解计算。将位置与计算时间步对齐，它们通过前一时刻隐状态 \(h_{t-1}\) 和位置 \(t\) 的输入生成隐状态序列 \(h_t\)。这种固有的串行性阻碍了训练样本内部的并行化，在序列较长时问题尤为突出，因为内存限制会限制跨样本批处理。近期工作通过因式分解技巧和条件计算显著提升计算效率，后者同时提升了模型性能。但串行计算的根本限制依然存在。

Attention mechanisms have become an integral part of compelling sequence modeling and transduction models in various tasks, allowing modeling of dependencies without regard to their distance in the input or output sequences. In all but a few cases, however, such attention mechanisms are used in conjunction with a recurrent network.

注意力机制已经成为各类序列建模与转换模型的核心组件，能够在不考虑输入/输出序列中位置距离的情况下建模依赖关系。但除少数情况外，这类注意力机制都与循环网络结合使用。

In this work we propose the Transformer, a model architecture eschewing recurrence and instead relying entirely on an attention mechanism to draw global dependencies between input and output. The Transformer allows for significantly more parallelization and can reach a new state of the art in translation quality after being trained for as little as twelve hours on eight P100 GPUs.

在本文中，我们提出 Transformer：一种完全摒弃循环、仅依靠注意力机制建模输入与输出全局依赖的架构。Transformer 支持高度并行化，仅需在 8 块 P100 GPU 上训练 12 小时，就能在翻译质量上达到新的最优水平。

---

## 2 Background
The goal of reducing sequential computation also forms the foundation of the Extended Neural GPU, ByteNet and ConvS2S, all of which use convolutional neural networks as basic building block, computing hidden representations in parallel for all input and output positions. In these models, the number of operations required to relate signals from two arbitrary input or output positions grows in distance between positions, linearly for ConvS2S and logarithmically for ByteNet. This makes it more difficult to learn dependencies between distant positions. In the Transformer this is reduced to a constant number of operations, albeit at the cost of reduced effective resolution due to averaging attention-weighted positions, an effect we counteract with Multi-Head Attention as described in section 3.2.

减少串行计算的目标同样是 Extended Neural GPU、ByteNet 和 ConvS2S 的基础，它们都使用卷积神经网络作为基本模块，对所有输入/输出位置并行计算隐表示。在这些模型中，关联两个任意位置信号所需的操作数随距离增长：ConvS2S 是线性增长，ByteNet 是对数增长。这使得学习远距离依赖更加困难。
在 Transformer 中，这一操作数被降为常数，尽管会因注意力加权平均导致有效分辨率下降，我们通过 3.2 节的多头注意力抵消这一影响。

Self-attention, sometimes called intra-attention is an attention mechanism relating different positions of a single sequence in order to compute a representation of the sequence. Self-attention has been used successfully in a variety of tasks including reading comprehension, abstractive summarization, textual entailment and learning task-independent sentence representations.

自注意力（有时称内部注意力）是一种关联单个序列不同位置以计算序列表示的注意力机制。它已被成功用于阅读理解、摘要生成、文本蕴含和与任务无关的句子表示学习等多个任务。

End-to-end memory networks are based on a recurrent attention mechanism instead of sequence-aligned recurrence and have been shown to perform well on simple-language question answering and language modeling tasks.

端到端记忆网络基于循环注意力机制而非按序列对齐的循环，在简单语言问答和语言模型任务上表现良好。

To the best of our knowledge, however, the Transformer is the first transduction model relying entirely on self-attention to compute representations of its input and output without using sequence-aligned RNNs or convolution. In the following sections we describe the Transformer, motivate self-attention and demonstrate its superiority.

据我们所知，Transformer 是首个完全依靠自注意力计算输入输出表示、不使用序列对齐 RNN 或卷积的转换模型。后续章节我们将介绍 Transformer、阐述自注意力动机并证明其优越性。

---

## 3 Model Architecture
Most competitive neural sequence transduction models have an encoder-decoder structure. Here, the encoder maps an input sequence of symbol representations \((x_1, ..., x_n)\) to a sequence of continuous representations \(z = (z_1, ..., z_n)\). Given \(z\), the decoder then generates an output sequence \((y_1, ..., y_m)\) of symbols one element at a time. At each step the model is auto-regressive, consuming the previously generated symbols as additional input when generating the next.

多数高性能序列转换模型采用编码器-解码器结构。其中，编码器将符号表示输入序列 \((x_1,...,x_n)\) 映射为连续表示序列 \(z=(z_1,...,z_n)\)。给定 \(z\)，解码器逐一生成符号输出序列 \((y_1,...,y_m)\)。每一步模型都是自回归的，生成下一个符号时将先前生成的符号作为附加输入。

The Transformer follows this overall architecture using stacked self-attention and point-wise, fully connected layers for both the encoder and decoder, shown in the left and right halves of Figure 1, respectively.

Transformer 沿用这一整体架构，对编码器和解码器均使用堆叠的自注意力与逐点全连接层，分别如图 1 左右半部分所示。

### 3.1 Encoder and Decoder Stacks

#### Encoder
The encoder is composed of a stack of \(N=6\) identical layers. Each layer has two sub-layers. The first is a multi-head self-attention mechanism, and the second is a simple, position-wise fully connected feed-forward network. We employ a residual connection around each of the two sub-layers, followed by layer normalization.

编码器由 \(N=6\) 个完全相同的层堆叠而成。每层包含两个子层：第一层是多头自注意力，第二层是简单的逐位置前馈全连接网络。我们在每个子层外部使用残差连接，随后进行层归一化。

That is, the output of each sub-layer is \(\text{LayerNorm}(x + \text{Sublayer}(x))\), where \(\text{Sublayer}(x)\) is the function implemented by the sub-layer itself. To facilitate these residual connections, all sub-layers in the model, as well as the embedding layers, produce outputs of dimension \(d_{\text{model}}=512\).

即每个子层的输出为：
\[
\text{LayerNorm}(x + \text{Sublayer}(x))
\]
为方便残差连接，模型中所有子层与嵌入层的输出维度均为 \(d_{\text{model}}=512\)。

#### Decoder
The decoder is also composed of a stack of \(N=6\) identical layers. In addition to the two sub-layers in each encoder layer, the decoder inserts a third sub-layer, which performs multi-head attention over the output of the encoder stack. Similar to the encoder, we employ residual connections around each of the sub-layers, followed by layer normalization.

解码器同样由 \(N=6\) 个相同层堆叠而成。除编码器每层的两个子层外，解码器插入第三个子层，对编码器堆叠的输出执行多头注意力。与编码器类似，每个子层外部使用残差连接，随后层归一化。

We also modify the self-attention sub-layer in the decoder stack to prevent positions from attending to subsequent positions. This masking, combined with fact that the output embeddings are offset by one position, ensures that the predictions for position \(i\) can depend only on the known outputs at positions less than \(i\).

我们还修改了解码器堆叠中的自注意力子层，禁止位置关注后续位置。这种掩码机制，配合输出嵌入偏移一个位置，确保对位置 \(i\) 的预测仅依赖小于 \(i\) 的已知输出。

### 3.2 Attention
An attention function can be described as mapping a query and a set of key-value pairs to an output, where the query, keys, values, and output are all vectors. The output is computed as a weighted sum of the values, where the weight assigned to each value is computed by a compatibility function of the query with the corresponding key.

注意力函数可描述为：将一个查询（query）和一组键值对（key-value）映射为输出。查询、键、值与输出均为向量。输出是值的加权和，分配给每个值的权重由查询与对应键的兼容函数计算。

#### 3.2.1 Scaled Dot-Product Attention
We call our particular attention "Scaled Dot-Product Attention". The input consists of queries and keys of dimension \(d_k\), and values of dimension \(d_v\). We compute the dot products of the query with all keys, divide each by \(\sqrt{d_k}\), and apply a softmax function to obtain the weights on the values.

我们的注意力称为缩放点积注意力。输入包含维度为 \(d_k\) 的查询和键，以及维度为 \(d_v\) 的值。我们计算查询与所有键的点积，每个除以 \(\sqrt{d_k}\)，再用 softmax 得到值的权重。

In practice, we compute the attention function on a set of queries simultaneously, packed together into a matrix \(Q\). The keys and values are also packed together into matrices \(K\) and \(V\). We compute the matrix of outputs as:
\[
\text{Attention}(Q,K,V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V
\]

实际使用时，我们将一组查询并行打包为矩阵 \(Q\)，键和值分别打包为 \(K\) 和 \(V\)，输出矩阵计算为：
\[
\text{Attention}(Q,K,V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V
\]

The two most commonly used attention functions are additive attention, and dot-product (multiplicative) attention. Dot-product attention is identical to our algorithm, except for the scaling factor \(\frac{1}{\sqrt{d_k}}\). Additive attention computes the compatibility function using a feed-forward network with a single hidden layer. While the two are similar in theoretical complexity, dot-product attention is much faster and more space-efficient in practice, since it can be implemented using highly optimized matrix multiplication code.

最常用的两种注意力是加性注意力和点积（乘法）注意力。点积注意力与我们的算法几乎一致，只差缩放因子 \(\frac{1}{\sqrt{d_k}}\)。加性注意力使用单隐层前馈网络计算兼容函数。二者理论复杂度相近，但点积注意力速度更快、空间效率更高，可使用高度优化的矩阵乘法实现。

While for small values of \(d_k\) the two mechanisms perform similarly, additive attention outperforms dot product attention without scaling for larger values of \(d_k\). We suspect that for large values of \(d_k\), the dot products grow large in magnitude, pushing the softmax function into regions where it has extremely small gradients. To counteract this effect, we scale the dot products by \(\frac{1}{\sqrt{d_k}}\).

当 \(d_k\) 较小时二者表现相近；但 \(d_k\) 较大时，不加缩放的点积注意力效果劣于加性注意力。我们推测原因是：\(d_k\) 大时点积幅值过大，使 softmax 进入梯度极小的饱和区。为抵消该效应，我们用 \(\frac{1}{\sqrt{d_k}}\) 缩放点积。

#### 3.2.2 Multi-Head Attention
Instead of performing a single attention function with \(d_{\text{model}}\)-dimensional keys, values and queries, we find it beneficial to linearly project the queries, keys and values \(h\) times with different, learned linear projections to \(d_k\), \(d_k\) and \(d_v\) dimensions, respectively.

与其对 \(d_{\text{model}}\) 维的键、值、查询执行单次注意力，我们发现更有益的做法是：使用不同的可学习线性投影，将查询、键、值分别投影 \(h\) 次到 \(d_k, d_k, d_v\) 维度。

On each of these projected versions of queries, keys and values we then perform the attention function in parallel, yielding \(d_v\)-dimensional output values. These are concatenated and once again projected, resulting in the final values.

在每组投影后的查询、键、值上并行执行注意力函数，得到 \(d_v\) 维输出值。将它们拼接后再次投影，得到最终值。

Multi-head attention allows the model to jointly attend to information from different representation subspaces at different positions. With a single attention head, averaging inhibits this.
\[
\text{MultiHead}(Q,K,V) = \text{Concat}(\text{head}_1,...,\text{head}_h)W^O
\]
where \(\text{head}_i = \text{Attention}(QW_i^Q, KW_i^K, VW_i^V)\)

多头注意力允许模型在不同位置联合关注来自不同表示子空间的信息。单头注意力的平均操作会抑制这一能力。
\[
\text{MultiHead}(Q,K,V) = \text{Concat}(\text{head}_1,...,\text{head}_h)W^O
\]
其中 \(\text{head}_i = \text{Attention}(QW_i^Q, KW_i^K, VW_i^V)\)

In this work we employ \(h=8\) parallel attention layers, or heads. For each of these we use \(d_k=d_v=d_{\text{model}}/h=64\). Due to the reduced dimension of each head, the total computational cost is similar to that of single-head attention with full dimensionality.

本文使用 \(h=8\) 个并行注意力层（头）。每个头使用 \(d_k=d_v=d_{\text{model}}/h=64\)。由于每个头维度降低，总计算成本与全维度单头注意力相近。

#### 3.2.3 Applications of Attention in our Model
The Transformer uses multi-head attention in three different ways:

Transformer 在三种不同场景使用多头注意力：

1. **Encoder-decoder attention**
   Queries come from the previous decoder layer, and memory keys and values come from the output of the encoder. This allows every position in the decoder to attend over all positions in the input sequence.

**编码器-解码器注意力**
查询来自前一个解码器层，存储的键和值来自编码器输出。这使得解码器每个位置都能关注输入序列所有位置。

2. **Encoder self-attention**
   In an encoder layer, all keys, values and queries come from the output of the previous layer in the encoder. Each position in the encoder can attend to all positions in the previous layer of the encoder.

**编码器自注意力**
编码器层中，所有查询、键、值都来自编码器前一层输出。编码器每个位置都能关注前一层所有位置。

3. **Decoder self-attention**
   Each position in the decoder can attend to all positions in the decoder up to and including that position. We prevent leftward information flow in the decoder by masking out (setting to \(-\infty\)) all values in the input of the softmax which correspond to illegal connections.

**解码器自注意力**
解码器每个位置可关注到该位置及之前的所有位置。我们通过将 softmax 输入中非法连接位置设为 \(-\infty\) 进行掩码，禁止解码器信息向左流动。

### 3.3 Position-wise Feed-Forward Networks
In addition to attention sub-layers, each of the layers in our encoder and decoder contains a fully connected feed-forward network, which is applied to each position separately and identically. This consists of two linear transformations with a ReLU activation in between.

除注意力子层外，编码器和解码器的每层都包含逐位置前馈网络，对每个位置独立且相同地应用。它由两个线性变换和中间的 ReLU 激活组成。

\[
\text{FFN}(x) = \max(0, xW_1 + b_1)W_2 + b_2
\]

While the linear transformations are the same across different positions, they use different parameters from layer to layer. Another way of describing this is as two convolutions with kernel size 1. The dimensionality of input and output is \(d_{\text{model}}=512\), and the inner layer has dimensionality \(d_{ff}=2048\).

线性变换在不同位置共享，但层与层之间参数不同。也可描述为两个核大小为 1 的卷积。输入输出维度为 \(d_{\text{model}}=512\)，内层维度 \(d_{ff}=2048\)。

### 3.4 Embeddings and Softmax
Similarly to other sequence transduction models, we use learned embeddings to convert the input tokens and output tokens to vectors of dimension \(d_{\text{model}}\). We also use the usual linear transformation and softmax function to convert the decoder output to predicted next-token probabilities.

与其他序列转换模型类似，我们使用可学习嵌入将输入/输出标记转为 \(d_{\text{model}}\) 维向量。使用线性变换与 softmax 将解码器输出转为下一个标记的预测概率。

In our model, we share the same weight matrix between the two embedding layers and the pre-softmax linear transformation. In the embedding layers, we multiply those weights by \(\sqrt{d_{\text{model}}}\).

在我们的模型中，两个嵌入层与 softmax 前的线性变换共享同一权重矩阵。在嵌入层，我们将权重乘以 \(\sqrt{d_{\text{model}}}\)。

### 3.5 Positional Encoding
Since our model contains no recurrence and no convolution, in order for the model to make use of the order of the sequence, we must inject some information about the relative or absolute position of the tokens in the sequence.

由于模型不含循环与卷积，为使模型利用序列顺序信息，必须向序列中注入标记的相对或绝对位置信息。

To this end, we add "positional encodings" to the input embeddings at the bottoms of the encoder and decoder stacks. The positional encodings have the same dimension \(d_{\text{model}}\) as the embeddings, so that the two can be summed. There are many choices of positional encodings, learned and fixed.

为此，我们在编码器和解码器堆叠底部，向输入嵌入添加位置编码。位置编码与嵌入维度同为 \(d_{\text{model}}\)，可直接相加。位置编码有多种选择：可学习的或固定的。

In this work, we use sine and cosine functions of different frequencies:
\[
\text{PE}_{(pos,2i)} = \sin(pos / 10000^{2i/d_{\text{model}}})
\]
\[
\text{PE}_{(pos,2i+1)} = \cos(pos / 10000^{2i/d_{\text{model}}})
\]

本文使用不同频率的正弦和余弦函数：
\[
\text{PE}_{(pos,2i)} = \sin(pos / 10000^{2i/d_{\text{model}}})
\]
\[
\text{PE}_{(pos,2i+1)} = \cos(pos / 10000^{2i/d_{\text{model}}})
\]

where \(pos\) is the position and \(i\) is the dimension. That is, each dimension of the positional encoding corresponds to a sinusoid. The wavelengths form a geometric progression from \(2\pi\) to \(10000 \cdot 2\pi\). We chose this function because we hypothesized it would allow the model to easily learn to attend by relative positions, since for any fixed offset \(k\), \(\text{PE}_{pos+k}\) can be represented as a linear function of \(\text{PE}_{pos}\).

其中 \(pos\) 为位置，\(i\) 为维度。位置编码的每一维对应一个正弦曲线，波长从 \(2\pi\) 到 \(10000\cdot 2\pi\) 等比数列。我们选择该函数是因为假设它能让模型轻松学习相对位置注意力：对任意固定偏移 \(k\)，\(\text{PE}_{pos+k}\) 可表示为 \(\text{PE}_{pos}\) 的线性函数。

In addition, we apply dropout to the sums of the embeddings and the positional encodings in both the encoder and decoder stacks. For the base model, we use a rate of \(P_{drop}=0.1\).

此外，我们在编码器和解码器堆叠中，对嵌入与位置编码之和施加 dropout。基础模型使用 \(P_{drop}=0.1\)。

---

## 4 Why Self-Attention
In this section we compare various aspects of self-attention layers to recurrent and convolutional layers commonly used for mapping one variable-length sequence of symbol representations \((x_1,...,x_n)\) to another sequence \((z_1,...,z_n)\).

本节将自注意力层与循环/卷积层从多方面对比，它们都用于将变长符号表示序列 \((x_1,...,x_n)\) 映射为另一序列 \((z_1,...,z_n)\)。

We are motivated to use self-attention for three reasons:

我们使用自注意力主要出于三点动机：

1. Computational Complexity
2. Amount of computation that can be parallelized
3. Path length between long-range dependencies in the network

1. 计算复杂度
2. 可并行计算量
3. 网络中远距离依赖的路径长度

Table 1 compares the three layer types based on total computational complexity per layer, minimum number of operations required to relate two arbitrary positions, and maximum path length between two positions.

表 1 对比了三种层类型：每层总计算复杂度、关联两个任意位置所需最小操作数、两位置间最大路径长度。

For \(n\) equal to the sequence length, and \(d\) the representation dimension, a self-attention layer is faster than a recurrent layer when \(n < d\), which is the case in most machine translation tasks with state-of-the-art models.

当序列长度 \(n <\) 表示维度 \(d\) 时，自注意力层比循环层更快，这正是多数最优机器翻译模型的情况。

---

## 5 Training

### 5.1 Training Data and Batching
We trained on the standard WMT 2014 English-German dataset consisting of about 4.5 million sentence pairs. Sentences were encoded using a shared byte-pair encoding (BPE) vocabulary of 37000 tokens. For English-French we used the larger WMT 2014 English-French dataset consisting of 36M sentences and split tokens into a 32000 word-piece vocabulary.

我们在标准 WMT 2014 英德数据集（约 450 万句对）上训练。句子使用共享的 37000 标记 BPE 词汇编码。英法翻译使用更大的 WMT 2014 英法数据集（3600 万句），切分为 32000 词片词汇。

### 5.2 Hardware and Schedule
We trained our models on one machine with 8 NVIDIA P100 GPUs. For our base models using the hyperparameters described throughout the paper, each training step took about 0.4 seconds. We trained the base models for a total of 100,000 steps or 12 hours. For our big model, step time was 1.0 seconds. The big models were trained for 300,000 steps (3.5 days).

我们在一台 8 卡 NVIDIA P100 机器上训练。基础模型按本文超参数，每步约 0.4 秒，共训练 10 万步（12 小时）。大模型每步 1.0 秒，训练 30 万步（3.5 天）。

### 5.3 Optimizer
We use the Adam optimizer with \(\beta_1=0.9\), \(\beta_2=0.98\) and \(\epsilon=10^{-9}\). We vary the learning rate over the course of training, according to the formula:
\[
\text{lr} = d_{\text{model}}^{-0.5} \cdot \min(\text{step\_num}^{-0.5}, \text{step\_num} \cdot \text{warmup\_steps}^{-1.5})
\]

使用 Adam 优化器，\(\beta_1=0.9\)，\(\beta_2=0.98\)，\(\epsilon=10^{-9}\)。学习率随训练变化：
\[
\text{lr} = d_{\text{model}}^{-0.5} \cdot \min(\text{step\_num}^{-0.5}, \text{step\_num} \cdot \text{warmup\_steps}^{-1.5})
\]

This corresponds to increasing the learning rate linearly for the first warmup_steps training steps, and decreasing it thereafter proportionally to the inverse square root of the step number. We used warmup_steps=4000.

即前 warmup_steps 步线性增加学习率，之后按步数平方根倒数衰减。本文 warmup_steps=4000。

### 5.4 Regularization
We employ three types of regularization:

使用三种正则化：

1. **Residual Dropout**
   We apply dropout to the output of each sub-layer, before it is added to the sub-layer input and normalized. In addition, we apply dropout to the sums of the embeddings and positional encodings in both encoder and decoder stacks. For the base model, we use a rate of 0.1.

**残差 Dropout**
在每个子层输出加入残差并归一化前施加 dropout。同时对编码器和解码器的嵌入+位置编码施加 dropout。基础模型率为 0.1。

2. **Label Smoothing**
   During training, we employed label smoothing of value \(\epsilon_{ls}=0.1\). This hurts perplexity, as the model learns to be more unsure, but improves accuracy and BLEU score.

**标签平滑**
训练时使用 \(\epsilon_{ls}=0.1\) 的标签平滑。这会提高困惑度（模型更不确定），但提升准确率与 BLEU。

---

## 6 Results

### 6.1 Machine Translation
On the WMT 2014 English-to-German translation task, the Transformer big model achieves a BLEU score of 28.4, which improves over all previously reported models by at least 2.0 BLEU.

在 WMT 2014 英德翻译任务上，Transformer 大模型达到 28.4 BLEU，超过所有已有模型至少 2.0 BLEU。

On the WMT 2014 English-to-French translation task, our big model achieves a BLEU score of 41.8, which outperforms all previously published single models.

在 WMT 2014 英法翻译任务上，大模型达到 41.8 BLEU，超过所有已发表单模型。

### 6.2 Model Variations
By varying the hyperparameters we measured the sensitivity of our model’s performance. We also found that the Transformer generalizes well to other tasks such as English constituency parsing.

通过改变超参数，我们测量了模型性能的敏感度。同时发现 Transformer 能很好泛化到其他任务，如英文句法分析。

---

## 7 Conclusion
Recurrence was the dominant approach in the best performing sequence transduction models. We have presented the Transformer, the first sequence transduction model based entirely on attention, replacing the recurrent layers most commonly used in encoder-decoder architectures with multi-headed self-attention.

循环曾是最优序列转换模型的主流方案。我们提出 Transformer，首个完全基于注意力的序列转换模型，用多头自注意力替代编码器-解码器中最常用的循环层。

For translation tasks, the Transformer can be trained significantly faster than architectures based on recurrent or convolutional layers. On WMT 2014 English-to-German and English-to-French translation tasks, we outperform the state of the art by a large margin.

对于翻译任务，Transformer 训练速度远快于循环/卷积架构。在 WMT 2014 英德、英法任务上，我们大幅超越当前最优结果。

We are excited about the future of attention-based models and plan to apply them to other tasks. We plan to extend the Transformer to problems involving input and output modalities other than text and to investigate local, restricted attention mechanisms to efficiently handle large inputs and outputs such as images, audio and video. Making generation less sequential is another research goal of ours.

我们对基于注意力的模型前景感到兴奋，并计划将其应用于其他任务。计划将 Transformer 扩展到文本以外的输入输出模态，研究局部受限注意力以高效处理图像、音频、视频等大规模输入输出。降低生成过程的串行性也是我们的研究目标。