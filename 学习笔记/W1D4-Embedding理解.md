# W1D4 Embedding 理解

## 今日目标

今天只抓住一条主线：Embedding 是把文本变成向量，让机器可以用“距离/相似度”比较语义。

学完后你应该能说清楚：

1. Embedding 和普通关键词搜索的区别。
2. 为什么语义搜索要先把文档和查询都转成向量。
3. 余弦相似度如何用于找“最相关”的内容。
4. 为什么真实项目里通常会把 Embedding 存进向量数据库。

## 对应课程

- 主课程：`08-building-search-applications`
- 概念预习：`02-exploring-and-comparing-different-llms` 中的 Embedding 小节
- 扩展关联：`15-rag-and-vector-databases`

## 核心概念

### 1. 什么是 Embedding

Embedding 是文本的数字表示。比如一句话会被模型转换成一个长向量：

```text
"What are Jupyter Notebooks?" -> [0.012, -0.034, 0.88, ...]
```

向量不是给人读的，而是给程序计算的。它把“含义接近”的文本放到向量空间里更接近的位置。

### 2. 关键词搜索 vs 语义搜索

关键词搜索更像“字符串匹配”：

```text
query: car
match: car, cars, car insurance
```

语义搜索更像“意思匹配”：

```text
query: my dream car
match: ideal vehicle, buying a car, choosing an automobile
```

### 3. Embedding 搜索流程

1. 把资料切成片段。
2. 为每个片段生成 Embedding。
3. 把片段和向量保存成索引。
4. 用户输入 query。
5. 为 query 生成 Embedding。
6. 计算 query 向量和每个片段向量的相似度。
7. 返回分数最高的 Top K 结果。

### 4. 余弦相似度

余弦相似度比较两个向量方向是否接近。越接近 `1`，语义越相似；越接近 `0`，关系越弱。

## 今天的动手任务

先运行本地离线脚本，理解搜索管线：

```powershell
python .\08-building-search-applications\python\local_embedding_demo.py "what are jupyter notebooks"
```

再打开 Jupyter Notebook 学官方课程：

```text
08-building-search-applications/python/oai-assignment.ipynb
08-building-search-applications/python/aoai-assignment.ipynb
```

如果没有配置 API Key，先阅读和运行不需要 API 的单元；需要真实 Embedding API 的单元会等配置完成后再跑。

## 今日验收

用自己的话回答：

1. Embedding 为什么适合做语义搜索？
2. 向量数据库解决了什么问题？
3. RAG 为什么离不开 Embedding？
