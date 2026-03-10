# 第1课课件：从聊天机器人到智能助手 -- AI Agent的记忆觉醒

> 课件脚本 | 对应讲义：lesson-01-memory-system.md | 对应讲课稿：lesson-01-script.md
> 总页数：32页 | 建议时长：3小时

---

<!-- Page 1 -->
## [COVER] Slide 1-0a

# AI Agent系统工程实战

### 第1课：从聊天机器人到智能助手
### -- AI Agent的记忆觉醒

对应原文：第1-2章 | 难度：中级 | 时长：3小时

---

<!-- Page 2 -->
## [TOC] Slide 1-0b

### 今天的旅程

| 模块 | 主题 | 时间 |
|------|------|------|
| 1.1 | ChatBot基本结构与记忆局限 | 0:00-0:50 |
| 1.2 | 向量数据库基础 | 0:35-1:10 |
| -- | 练习1 + 休息 | 0:50-1:20 |
| 1.3 | 四层记忆架构设计 | 1:20-1:50 |
| 1.4 | 记忆自动收敛 | 1:50-2:20 |
| 1.5 | QMD向量记忆系统 | 2:00-2:20 |
| -- | 练习2 + 总结 | 2:20-3:00 |

---

<!-- Page 3 -->
## [QUESTION] Slide 1-1a

> 对应讲课稿 [互动]：平时用ChatGPT或Claude时，有没有遇到它忘记之前信息的情况？

# 你的AI助手"失忆"过吗？

用ChatGPT或Claude时，有没有遇到
**你说了一个重要信息，下次聊天它完全不记得？**

来，遇到过的举个手。

---

<!-- Page 4 -->
## [CONCEPT] Slide 1-1b

### 模块 1.1 -- ChatBot的基本结构

# ClawBot v1：一切的起点

核心工作流四步走：

**记忆加载 -> 上下文构建 -> API调用 -> 记忆保存**

---

<!-- Page 5 -->
## [DIAGRAM] Slide 1-1c

### ClawBot v1 数据流

```
用户消息
   |
   v
[加载 memory.json] --> 全部历史对话
   |
   v
[构建 messages 列表] --> system + history[-20:] + 当前消息
   |
   v
[调用 GPT-4 API]
   |
   v
[保存到 memory.json] --> 只保留最近20轮
   |
   v
返回回复
```

> 关键瓶颈：`history[-20:]` 一刀切丢弃旧信息

---

<!-- Page 6 -->
## [CODE] Slide 1-1d

### ClawBot v1 核心代码

```python
def chat(self, user_id: str, message: str) -> str:
    history = self.conversations.get(user_id, [])

    messages = [
        {"role": "system", "content": "你是一个有用的AI助手。"}
    ] + history + [
        {"role": "user", "content": message}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4", messages=messages
    )

    self.conversations[user_id] = history[-20:]  # <-- 重点
    self._save_memory()
```

---

<!-- Page 7 -->
## [QUESTION] Slide 1-1e

> 对应讲课稿 [互动]：这个设计最大的问题是什么？

# ClawBot v1 最大的问题是什么？

- A. 20轮太少，改成200轮
- B. 不区分重要性，一刀切丢弃
- C. 应该用数据库替代JSON文件

思考30秒...

---

<!-- Page 8 -->
## [TABLE] Slide 1-1f

### JSON存储的四大缺陷

| 缺陷 | 具体表现 |
|------|---------|
| 无法跨会话检索 | 超过20轮永久丢失 |
| 没有语义理解 | "API密钥" 搜不到 "API key" |
| 文件膨胀 | 所有用户数据挤在一个JSON里 |
| 无法区分重要性 | 闲聊和关键信息混在一起 |

---

<!-- Page 9 -->
## [CONCEPT] Slide 1-1g

# 对话记录 ≠ 记忆

- **对话记录** = 按时间排列的流水账
- **记忆** = 经过理解、筛选、组织的知识

> AI Agent与ChatBot的本质区别在于"记忆的质量"

---

<!-- Page 10 -->
## [TRANSITION] Slide 1-1to2

# 如何让AI理解语义？

"API密钥" 和 "API key" 是同一回事

关键词匹配做不到 --> 我们需要**向量Embedding**

---

<!-- Page 11 -->
## [CONCEPT] Slide 1-2a

### 模块 1.2 -- 向量数据库基础

# 向量Embedding

把文本映射到高维数字空间

**语义相近的文本，在空间中距离更近**

---

<!-- Page 12 -->
## [DIAGRAM] Slide 1-2b

### Embedding的直觉理解

```
        女王 (0.9, 0.8)
         *
        /
       / "国王 - 男人 + 女人 ≈ 女王"
      /
     * 国王 (0.8, 0.2)
    /         * 女人 (0.3, 0.7)
   /         /
  * 男人 (0.2, 0.1)
```

- 语义相近 --> 距离近
- 同义词自动聚拢："API密钥" ≈ "API key" ≈ "访问令牌"

---

<!-- Page 13 -->
## [QUESTION] Slide 1-2c

> 对应讲课稿 [互动]：搜索"交易所密钥"能找到"我的币安API key是abc123"吗？

# 搜索"交易所密钥"

能找到内容为
**"我的币安API key是abc123"** 的记忆吗？

为什么能？

---

<!-- Page 14 -->
## [DIAGRAM] Slide 1-2d

### 余弦相似度

```
公式：cosine(A, B) = (A . B) / (|A| x |B|)

结果范围：-1 到 1（实际 0 到 1）

示例：
  cosine("API密钥", "API key")    ≈ 0.92  高度相似
  cosine("API密钥", "天气预报")    ≈ 0.05  几乎无关
```

值越接近 1 --> 语义越相似

---

<!-- Page 15 -->
## [CODE] Slide 1-2e

### VectorMemory -- add() 方法

```python
class VectorMemory:
    def __init__(self, collection_name="clawbot_memory"):
        self.encoder = SentenceTransformer(
            'all-MiniLM-L6-v2'                 # <-- 重点
        )
        self.client = chromadb.Client(Settings(
            persist_directory="./chroma_db"
        ))
        self.collection = self.client.get_or_create_collection(
            name=collection_name
        )

    def add(self, text: str, metadata: dict = None):
        embedding = self.encoder.encode(text).tolist()  # <-- 重点
        self.collection.add(
            embeddings=[embedding], documents=[text],
            metadatas=[metadata or {}], ids=[doc_id]
        )
```

---

<!-- Page 16 -->
## [CODE] Slide 1-2f

### VectorMemory -- search() 方法

```python
def search(self, query: str, n_results: int = 5):
    query_embedding = self.encoder.encode(query).tolist()

    results = self.collection.query(       # <-- 重点
        query_embeddings=[query_embedding],
        n_results=n_results
    )

    return results['documents'][0]
```

搜索"API key" --> 找到"API密钥"（相似度 ≈ 0.92）

---

<!-- Page 17 -->
## [TABLE] Slide 1-2g

### JSON存储 vs 向量存储

| 能力 | JSON（之前） | 向量（之后） |
|------|------------|------------|
| 语义理解 | "API密钥" ≠ "API key" | "API密钥" ≈ "API key" |
| 跨会话检索 | 只搜最近20轮 | 搜索所有历史 |
| 关联发现 | 无 | 自动关联相似记忆 |
| 存储效率 | 全量加载 | 按需检索 |

---

<!-- Page 18 -->
## [EXERCISE] Slide 1-2h

### 练习1：基于ChromaDB实现VectorMemory类

- **时间：** 20分钟
- **目标：** 实现 add() 和 search() 方法
- **验证：** "API密钥"和"API key"能互相检索
- **文件：** exercise_01_vector_memory.py
- **参考：** 讲义模块1.2 VectorMemory完整代码

---

<!-- Page 19 -->
## [TRANSITION] Slide 1-2to3

# 新问题出现了

所有记忆被**平等对待**

"用户喜欢喝咖啡" 与 "用户的银行密码"
被同等存储和检索

--> 我们需要**记忆分层**

---

<!-- Page 20 -->
## [CONCEPT] Slide 1-3a

### 模块 1.3 -- 四层记忆架构

# 不是所有记忆都同等重要

人类记忆也分层：
- 正在读的这段话 = 工作记忆
- 今天午饭吃了什么 = 短期记忆
- 你的名字 = 长期记忆
- 你的专业知识 = 知识体系

---

<!-- Page 21 -->
## [DIAGRAM] Slide 1-3b

### 四层记忆架构图

```
Layer 1: 工作记忆    | 当前对话上下文 | 内存      | 会话结束清除
---------------------------------------------------------------------
Layer 2: 短期记忆    | 今日对话记录   | MD文件    | 数天到数周
---------------------------------------------------------------------
Layer 3: 长期记忆    | 重要事实/偏好  | MEMORY.md | 永久
                     |               | + 向量DB  |
---------------------------------------------------------------------
Layer 4: 知识库      | 领域知识/技能  | 结构化    | 永久
                     |               | 文档+索引 | 定期更新
```

> 检索优先级：L1 > L2 > L3 > L4

---

<!-- Page 22 -->
## [QUESTION] Slide 1-3c

> 对应讲课稿 [互动]：设计一个客服AI Agent，四层记忆分别放什么内容？

# 设计客服AI Agent的记忆

四层分别应该放什么内容？

给大家30秒想一想...

---

<!-- Page 23 -->
## [DIAGRAM] Slide 1-3d

### 四层协作检索流程

```
用户问："我之前让你监控的Polymarket市场现在怎样？"

步骤1 --> 工作记忆：当前对话无相关上下文
步骤2 --> 短期记忆：今日无相关记录
步骤3 --> 长期记忆：找到 "启动Polymarket套利监控"
步骤4 --> 知识库：找到 "价格监控脚本每小时扫描"

--> 综合回复（融合多层信息）
```

---

<!-- Page 24 -->
## [CONCEPT] Slide 1-4a

### 模块 1.4 -- 记忆自动收敛

# 记忆收敛 = 大脑的"睡眠整理"

短期记忆如何"提升"到长期记忆？

灵感来源：人类睡眠中的记忆巩固

**自动扫描 --> 正则提取 --> 判断重要性 --> 写入长期记忆**

---

<!-- Page 25 -->
## [CODE] Slide 1-4b

### MemoryConsolidator 关键逻辑

```python
self.patterns = {
    'account_info': r'(账户|余额|资金).{0,30}(\$?\d+)',  # <-- 重点
    'decision': r'(决定|决策|选择).{0,50}(使用|采用)',
    'milestone': r'(完成|启动|部署).{0,30}(项目|系统)',
    'error': r'(错误|失败|问题|修复).{0,50}',
}

def should_promote_to_longterm(self, event):
    if event['type'] == 'account_info':
        if float(amounts[0]) > 100:       # <-- 重点
            return True
    if event['type'] == 'milestone':
        return True                        # <-- 重点
    return False
```

---

<!-- Page 26 -->
## [QUESTION] Slide 1-4c

> 对应讲课稿 [互动]：为什么错误类型没有自动提升规则？

# 为什么"错误"类事件没有自动提升？

错误那么重要，不应该全部记住吗？

提示：想想 error 模式匹配的范围有多广...

---

<!-- Page 27 -->
## [TABLE] Slide 1-4d

### 正则 vs LLM 做收敛判断

| 维度 | 正则匹配 | LLM判断 |
|------|---------|---------|
| 运行成本 | 接近零 | $0.01-0.05/次 |
| 运行速度 | 毫秒级 | 秒级 |
| 可预测性 | 确定性输出 | 每次可能不同 |
| 适用频率 | 每小时 | 每天 |

> 收敛器每天运行多次，正则是成本最优解

---

<!-- Page 28 -->
## [CONCEPT] Slide 1-5a

### 模块 1.5 -- QMD向量记忆系统

# 混合搜索：BM25 + 向量 + RRF

- **BM25：** 精确关键词匹配（如 "E1001"）
- **向量：** 语义理解（如 "交易所密钥"）
- **RRF：** 融合两者排名，取两者之长

---

<!-- Page 29 -->
## [DIAGRAM] Slide 1-5b

### RRF融合算法

```
公式：RRF_score(d) = sum( 1 / (k + rank + 1) )    k=60

文档A：BM25排名第1 + 向量排名第3
  = 1/61 + 1/63 = 0.03226

文档C：BM25排名第2 + 向量排名第2
  = 1/62 + 1/62 = 0.03226

文档D：仅BM25排名第1，向量搜索没出现
  = 1/61 = 0.01639  <-- 远低于双路出现的文档
```

> RRF奖励"在多个排名中都表现稳定"的文档

---

<!-- Page 30 -->
## [QUESTION] Slide 1-5c

> 对应讲课稿 [互动]：RRF为什么不直接把两个搜索的分数加起来？

# RRF为什么用排名而不是分数融合？

BM25分数和余弦相似度的量级完全不同

直接相加会怎样？

---

<!-- Page 31 -->
## [EXERCISE] Slide 1-5d

### 练习2：实现记忆收敛器

- **时间：** 25分钟
- **目标：** 从日志中提取关键事件并判断是否提升
- **规则：** 金额>$500 / 所有里程碑 / "严重"错误
- **文件：** exercise_02_memory_consolidator.py
- **参考：** 讲义模块1.4 MemoryConsolidator完整代码

---

<!-- Page 32 -->
## [SUMMARY] Slide 1-6a

### 第1课核心总结

1. AI Agent与ChatBot的区别 = **记忆的质量**
2. 向量Embedding让AI理解 "API密钥" ≈ "API key"
3. 记忆必须**分层管理**（工作/短期/长期/知识库）
4. 记忆收敛 = 自动从短期提取关键信息到长期
5. 混合搜索（BM25 + 向量 + RRF）比单一搜索更可靠

---

<!-- Page 33 -->
## [TRANSITION] Slide 1-next

# 下节课预告

记忆解决了"Agent知道什么"

但当Agent要同时处理代码、问答、文档...

应该用**哪个模型**？

**第2课：多模型调度与智能路由**
