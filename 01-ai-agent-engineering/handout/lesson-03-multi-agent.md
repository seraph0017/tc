# 第3课：从独行侠到团队 -- 多Agent架构设计与实现

> **对应原文：** 第4章（多Agent架构的诞生）
> **课程难度：** 中高级
> **课时：** 3小时

---

## 预习建议（30分钟）

请在课前完成以下预习：

1. **阅读材料（15分钟）：** 阅读原文第4章"多Agent架构的诞生"全文，重点关注OpenClaw的三层架构图和Agent配置YAML。尝试理解每个Agent的职责划分逻辑。
2. **概念准备（10分钟）：** 如果你不熟悉Redis，请浏览Redis官网的"Introduction to Redis"页面（https://redis.io/docs/about/），了解Redis是什么以及Pub/Sub模式的基本概念。
3. **思考问题（5分钟）：** 如果你是一家公司的CTO，你会让一个全栈工程师同时负责前端、后端、运维、QA，还是组建专业团队？为什么？这个决策和多Agent架构有什么共通之处？

---

## 本课知识地图

```
第3课：多Agent架构设计与实现
│
├── 模块3.1 单Agent瓶颈分析
│   └── 上下文竞争 → 领域干扰 → 并行限制 → 单点故障
│
├── 模块3.2 多Agent架构设计
│   └── 主Agent + 专业Agent集群 + 共享基础设施
│
├── 模块3.3 Agent定义规范
│   └── YAML配置结构 → 字段详解 → 设计原则
│
├── 模块3.4 通信机制实现
│   └── AgentMessage → AgentBus → Redis Pub/Sub → 消息持久化
│
├── 模块3.5 任务编排器
│   └── Task生命周期 → 依赖图 → 技能匹配 → 负载均衡
│
└── 模块3.6 记忆同步
    └── AgentMemorySync → MEMORY.md同步 → 每日记忆 → QMD索引
```

---

## 模块3.1：单Agent瓶颈分析

### 学习目标

完成本模块后，你应能够：

1. 列举单Agent架构在功能扩展时面临的四个核心瓶颈
2. 用具体示例解释"上下文窗口竞争"和"领域干扰"的含义
3. 解释为什么这些瓶颈无法仅通过增强单个Agent的能力来解决

### 正文

#### 当一个Agent要做所有事

回顾前两课，我们已经给Agent装备了强大的记忆系统和智能路由能力。但随着功能不断增加——量化交易、代码开发、内容创作、项目管理——单一Agent开始"窒息"。

**瓶颈1：上下文窗口竞争**

每个LLM都有上下文窗口限制（如128K tokens）。当Agent需要同时处理量化交易策略和前端代码开发时，交易相关的系统提示词、历史记录、策略文档会和代码相关的上下文争夺有限的窗口空间。

```
单Agent的上下文窗口（128K tokens）：
┌─────────────────────────────────────────┐
│ 系统提示词 (2K)                          │
│ 交易策略上下文 (30K)                      │
│ 代码开发上下文 (30K)                      │
│ 写作项目上下文 (20K)                      │
│ 项目管理上下文 (15K)                      │
│ 对话历史 (20K)                           │
│ 剩余空间: 11K ← 几乎没有余量              │
└─────────────────────────────────────────┘
```

结果：每个领域只能分到一小部分上下文，Agent在所有领域都只能给出"及格"的回答。

**瓶颈2：领域干扰**

不同领域的知识和指令会互相干扰。一个被训练为"严谨的量化交易分析师"的提示词和"创意的内容写手"的提示词是矛盾的。

```
系统提示词冲突示例：
"你是一个严谨的量化分析师，只基于数据做出判断，避免主观推测。"
   vs
"你是一个富有创意的内容写手，大胆发挥想象力，用生动的语言吸引读者。"
```

当两组指令共存于一个Agent中，它的行为变得不可预测——有时过于保守，有时过于奔放。

**瓶颈3：并行限制**

单一Agent一次只能处理一个任务。当用户要求"同时执行交易策略回测和前端代码重构"时，Agent只能串行执行，效率低下。

**瓶颈4：单点故障**

一个Agent的一个错误可能影响所有功能。例如，量化交易模块出现bug导致Agent崩溃，连最简单的聊天功能都无法使用。

#### 四大瓶颈的本质

这四个瓶颈指向同一个根本问题：**单Agent架构违反了软件工程的"单一职责原则"（Single Responsibility Principle）。**

就像一家公司不会让一个人同时担任CEO、CTO、财务总监和前台接待，AI系统也需要将不同的职责分配给不同的Agent。

### 自测题

**1.（选择题）以下哪个不是单Agent架构的核心瓶颈？**

A. 上下文窗口竞争
B. 模型训练数据不足
C. 领域干扰
D. 单点故障

**答案：** B。模型训练数据不足是模型本身的问题，不是单Agent架构的问题。即使有一个完美的模型，单Agent架构仍然面临上下文竞争、领域干扰和单点故障的挑战。

**2.（简答题）请用"餐厅"的类比解释单Agent瓶颈和多Agent架构的区别。**

**参考答案：** 单Agent架构类似于一个人同时担任厨师、服务员、收银员和清洁工的餐厅。这个人即使能力很强，在客人多的时候也会手忙脚乱：做菜的时候不能点单（并行限制），做甜点的手法影响了做川菜的口味（领域干扰），一旦他生病整个餐厅就停业了（单点故障）。多Agent架构则是一个有专业分工的餐厅团队：主厨负责出品，服务员负责接待，收银员负责结账——每个人做自己最擅长的事，效率和质量都更高。

---

## 模块3.2：多Agent架构设计

### 学习目标

完成本模块后，你应能够：

1. 画出OpenClaw的三层多Agent架构图，并解释每一层的职责
2. 说明"主Agent + 专业Agent集群 + 共享基础设施"的设计意图
3. 解释共享基础设施层的四个组件各自的作用

### 正文

#### OpenClaw架构总览

OpenClaw采用了一个清晰的三层架构：

```
┌─────────────────────────────────────────────────────────┐
│                     OpenClaw 架构                        │
├─────────────────────────────────────────────────────────┤
│  第一层：主Agent (Friday)                                │
│  - 用户交互的唯一入口                                    │
│  - 任务分发与协调中心                                    │
│  - 记忆管理与同步                                        │
│  - 类比：公司CEO / 项目经理                               │
├─────────────────────────────────────────────────────────┤
│  第二层：专业Agent集群                                    │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │
│  │ 桑丘    │ │ 参孙    │ │ 建筑师  │ │ PM      │       │
│  │(trading)│ │(learning)│ │(arch)   │ │(pm)     │       │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘       │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐                   │
│  │ 前端    │ │ 后端    │ │ QA      │                   │
│  │(frontend)│ │(backend)│ │(qa)     │                   │
│  └─────────┘ └─────────┘ └─────────┘                   │
│  - 每个Agent有独立的workspace和技能集                    │
│  - 类比：各部门专家                                      │
├─────────────────────────────────────────────────────────┤
│  第三层：共享基础设施                                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │ 向量记忆 │ │ 消息总线 │ │ 定时调度 │ │ 配置管理 │   │
│  │  (QMD)   │ │  (Bus)   │ │  (Cron)  │ │ (Config) │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
│  - 所有Agent共享的公共服务                               │
│  - 类比：公司的IT基础设施                                │
└─────────────────────────────────────────────────────────┘
```

#### 三层架构的设计意图

**第一层：主Agent（Friday）-- 统一入口**

Friday是用户接触的唯一Agent。用户不需要知道后面有多少个专业Agent，也不需要手动选择应该和谁对话。这遵循了"门面模式（Facade Pattern）"的设计理念——提供一个简单的接口，隐藏系统内部的复杂性。

Friday的三个核心职责：
1. **用户交互：** 接收用户请求，返回最终结果
2. **任务分发：** 分析请求内容，决定交给哪个专业Agent处理
3. **记忆同步：** 确保各Agent之间的记忆一致

**第二层：专业Agent集群 -- 各司其职**

每个专业Agent有明确的领域、独立的工作空间和专属的技能集。这解决了模块3.1中的所有瓶颈：

| 瓶颈 | 多Agent如何解决 |
|------|----------------|
| 上下文竞争 | 每个Agent只加载自己领域的上下文 |
| 领域干扰 | 每个Agent有独立的系统提示词 |
| 并行限制 | 不同Agent可以并行处理不同任务 |
| 单点故障 | 一个Agent故障不影响其他Agent |

**第三层：共享基础设施 -- 公共服务**

| 组件 | 作用 | 为什么共享而不是每个Agent各自拥有 |
|------|------|------------------------------|
| QMD（向量记忆） | 全局知识检索 | 避免知识孤岛，一个Agent的经验可以被其他Agent利用 |
| 消息总线（Bus） | Agent间通信 | 统一通信协议，避免点对点连接的复杂性（N个Agent需要N*(N-1)/2个连接） |
| 定时调度（Cron） | 定时任务管理 | 避免多个Agent各自维护定时任务导致的时间冲突和资源浪费 |
| 配置管理（Config） | 统一配置中心 | 一处修改，全局生效——避免配置不一致 |

### 自测题

**1.（选择题）OpenClaw为什么选择让Friday作为用户交互的唯一入口，而不是让用户直接和专业Agent对话？**

A. 因为Friday的模型能力最强
B. 为了简化用户体验——用户不需要了解内部架构，就像你不需要知道酒店厨房有几个厨师
C. 因为其他Agent不具备对话能力
D. 这只是一个临时设计，最终目标是让用户直接和专业Agent对话

**答案：** B。这是门面模式的应用。用户只需要和Friday交流，由Friday决定将任务分发给谁。这降低了用户的认知负担，也使得内部架构的调整（增减Agent、改变职责划分）不会影响用户体验。

**2.（简答题）在什么情况下你会选择不共享基础设施，而是让每个Agent拥有独立的记忆系统？请给出至少一个合理的场景。**

**参考答案：** 当Agent处理高度敏感且需要隔离的数据时。例如，在金融机构中，交易Agent和合规Agent的记忆可能需要严格隔离——交易策略属于核心商业机密，不应该被合规Agent的搜索检索到。又如在医疗系统中，处理不同患者数据的Agent应该有独立的记忆空间以满足隐私法规（如HIPAA）要求。

---

## 模块3.3：Agent定义规范

### 学习目标

完成本模块后，你应能够：

1. 阅读并理解Agent配置YAML文件中每个字段的含义和设计考量
2. 为一个新的领域Agent编写完整的YAML配置
3. 解释`responsibilities`和`skills`的区别

### 正文

#### 完整的Agent配置YAML

以下是OpenClaw系统中所有Agent的配置定义：

```yaml
# ~/.openclaw/config/agents.yml
# Agent集群配置文件
# 每个Agent的定义包含六个关键字段：name/role/workspace/model/responsibilities/skills

agents:
  friday:
    name: "星期五"               # 人类可读的名称
    role: "主助手"               # 角色定位（决定系统提示词的基调）
    workspace: "~/.openclaw/workspace"  # 独立工作空间路径
    model: "moonshot/kimi-k2.5"  # 使用的LLM模型
    responsibilities:            # 职责列表（定义"这个Agent应该做什么"）
      - 用户交互
      - 任务分发
      - 记忆同步
      - 定时任务协调
    # 注意：Friday没有skills字段
    # 原因：Friday是协调者，不直接执行专业任务

  trading:
    name: "桑丘"
    role: "量化交易助手"
    workspace: "~/.openclaw/workspace-trading"
    # 每个Agent有独立的workspace，确保文件和数据隔离
    # workspace路径包含agent名称，便于管理
    model: "moonshot/kimi-k2.5"
    responsibilities:
      - 加密货币量化策略
      - 预测市场套利
      - 风险管理
      - 交易监控
    skills:                      # 技能列表（定义"这个Agent能调用什么工具"）
      - binance-pro              # 币安交易API封装
      - polymarket-analysis      # Polymarket数据分析
      - polymarket-arbitrage     # Polymarket套利策略
    # skills vs responsibilities的区别：
    # responsibilities是"做什么"——描述Agent的职责范围
    # skills是"用什么"——定义Agent可调用的具体工具/能力

  learning:
    name: "参孙"
    role: "Polymarket学习助手"
    workspace: "~/.openclaw/workspace-polymarket"
    model: "moonshot/kimi-k2.5"
    responsibilities:
      - 预测市场分析
      - 策略学习
      - 交易模式提取

  architect:
    name: "建筑师"
    role: "系统架构师"
    workspace: "~/.openclaw/workspace-architect"
    model: "anthropic/claude-3-5-sonnet"
    # 建筑师使用Claude而非Kimi
    # 原因：架构设计和代码审查需要强大的代码理解能力
    # 这体现了"给Agent匹配最适合的模型"的原则（第2课内容）
    responsibilities:
      - 系统设计
      - 技术选型
      - 架构评审

  frontend:
    name: "前端"
    role: "前端开发"
    workspace: "~/.openclaw/workspace-frontend"
    model: "anthropic/claude-3-5-sonnet"
    responsibilities:
      - React/Next.js开发
      - UI组件实现
      - 性能优化

  backend:
    name: "后端"
    role: "后端开发"
    workspace: "~/.openclaw/workspace-backend"
    model: "anthropic/claude-3-5-sonnet"
    responsibilities:
      - API开发
      - 数据库设计
      - 服务架构

  pm:
    name: "PM"
    role: "产品经理"
    workspace: "~/.openclaw/workspace-pm"
    model: "moonshot/kimi-k2.5"
    responsibilities:
      - 需求分析
      - 项目规划
      - 进度跟踪

  qa:
    name: "QA"
    role: "测试工程师"
    workspace: "~/.openclaw/workspace-qa"
    model: "anthropic/claude-3-5-sonnet"
    responsibilities:
      - 测试用例设计
      - 自动化测试
      - Bug追踪
```

#### 配置设计的六个关键字段

| 字段 | 含义 | 设计考量 |
|------|------|---------|
| **name** | Agent的人类可读名称 | 便于在日志、监控和用户交互中识别 |
| **role** | 角色定位 | 直接影响系统提示词——"你是一个{role}"会成为所有对话的基调 |
| **workspace** | 独立工作空间 | 文件和数据隔离，防止Agent间互相覆盖文件 |
| **model** | 使用的LLM | 不同Agent使用不同模型，体现了第2课的路由思想 |
| **responsibilities** | 职责列表 | 用于任务分发时的匹配——Friday根据responsibilities决定将任务交给谁 |
| **skills** | 可调用的技能 | 用于任务编排时的能力匹配——判断Agent能否胜任某个具体任务 |

#### 设计原则

**原则1：Agent数量要克制**

不要为每个小功能都创建一个Agent。OpenClaw经过多次迭代，从最初的3个Agent扩展到8个——每次增加都是因为出现了明确的、无法由现有Agent承担的需求。

**原则2：模型选择要匹配**

代码类Agent统一使用Claude（代码能力最强），分析和交互类Agent使用Kimi（中文推理强，成本适中）。不要给所有Agent都用最贵的模型。

**原则3：职责边界要清晰**

如果两个Agent的responsibilities有超过30%的重叠，说明它们应该合并，或者重新划分职责边界。

> **[知识补给站] Enum和dataclass在系统设计中的最佳实践**
>
> 在后续的代码中，你会频繁看到`Enum`和`@dataclass`的使用。它们在系统设计中扮演重要角色：
>
> ```python
> from enum import Enum
> from dataclasses import dataclass
>
> # Enum：用于定义有限的、固定的状态集合
> # 好处：IDE自动补全、防止拼写错误、代码可读性强
> class TaskStatus(Enum):
>     PENDING = "pending"     # 而非直接用字符串 "pending"
>     ASSIGNED = "assigned"   # 如果写错成 "assinged" 编译器不会报错
>     RUNNING = "running"     # 但 TaskStatus.ASSINGED 会立即报错
>     COMPLETED = "completed"
>     FAILED = "failed"
>
> # dataclass：用于定义结构化数据
> # 好处：自动生成__init__、__repr__，字段类型明确
> @dataclass
> class Task:
>     id: str
>     status: TaskStatus  # 类型标注使用Enum
>     description: str
>
> # 使用示例
> task = Task(id="t1", status=TaskStatus.PENDING, description="写代码")
> if task.status == TaskStatus.PENDING:  # 类型安全的比较
>     print("任务待分配")
> ```

### 自测题

**1.（选择题）OpenClaw系统中，architect Agent使用Claude而非Kimi的主要原因是什么？**

A. Claude更便宜
B. Claude的架构设计和代码审查能力更强
C. Kimi不支持英文
D. 这是随机选择的

**答案：** B。architect Agent的核心职责是系统设计和架构评审，这些任务高度依赖代码理解能力。Claude 3.5 Sonnet在代码相关任务上的表现优于其他模型（这是第2课LLM能力矩阵中的结论）。

**2.（简答题）如果你需要为OpenClaw添加一个"数据分析师"Agent，请写出它的完整YAML配置，并解释你的模型选择理由。**

**参考答案：**
```yaml
data_analyst:
  name: "分析师"
  role: "数据分析师"
  workspace: "~/.openclaw/workspace-analyst"
  model: "google/gemini-1.5-pro"
  responsibilities:
    - 数据探索与清洗
    - 统计分析与可视化
    - 报告生成
  skills:
    - pandas-analysis
    - plotly-visualization
    - sql-query
```
选择Gemini 1.5 Pro的理由：数据分析经常需要处理大量数据和长文档（如CSV文件、数据字典），Gemini的2M token上下文窗口能够一次性处理大型数据集的描述和分析需求。

---

## 模块3.4：通信机制实现

### 学习目标

完成本模块后，你应能够：

1. 解释Agent间通信为什么选择发布-订阅模式而非点对点模式
2. 阅读并理解AgentBus的完整实现，说明send、broadcast、subscribe三个方法的工作原理
3. 解释消息持久化的设计目的——为什么消息既要通过Pub/Sub实时发送，又要存入列表

### 正文

#### 通信模式的选择

> **[知识补给站] 消息队列核心模式对比**
>
> Agent间通信有两种基本模式：
>
> **点对点模式（Point-to-Point）：**
> ```
> Agent A ──────> Agent B
> Agent A ──────> Agent C
> Agent B ──────> Agent C
> ```
> - 每对Agent之间需要一条专用连接
> - N个Agent需要N*(N-1)/2条连接
> - 8个Agent = 28条连接——管理复杂
>
> **发布-订阅模式（Pub/Sub）：**
> ```
> Agent A ──┐
> Agent B ──┤──> 消息总线 ──┤──> Agent A
> Agent C ──┘              ├──> Agent B
>                          └──> Agent C
> ```
> - 所有Agent只连接消息总线
> - N个Agent只需N条连接
> - 8个Agent = 8条连接——简单清晰
>
> OpenClaw选择了Pub/Sub模式，使用Redis作为消息中间件。

> **[知识补给站] Redis Pub/Sub基础**
>
> Redis是一个高性能的内存数据存储，除了键值存储外，还提供了Pub/Sub（发布/订阅）消息功能。
>
> **安装与启动：**
> ```bash
> # macOS
> brew install redis
> redis-server
>
> # Python客户端
> pip install redis
> ```
>
> **核心概念：**
> - **Channel（频道）：** 消息的传输管道，类似于广播电台的频率
> - **Publish（发布）：** 向某个频道发送消息
> - **Subscribe（订阅）：** 监听某个频道的消息
>
> ```python
> import redis
>
> r = redis.Redis(host='localhost', port=6379)
>
> # 发布者
> r.publish('agent:trading', '{"type": "task", "content": "执行回测"}')
>
> # 订阅者（通常在另一个进程/线程中运行）
> pubsub = r.pubsub()
> pubsub.subscribe('agent:trading')
> for message in pubsub.listen():
>     if message['type'] == 'message':
>         print(f"收到消息: {message['data']}")
> ```

#### AgentMessage数据结构与AgentBus实现

```python
# agent_messaging.py
# Agent间通信系统：基于Redis Pub/Sub的消息总线
# 核心设计：每个Agent有一个专属频道（channel），消息通过频道进行路由
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import redis

@dataclass
class AgentMessage:
    """Agent间消息的标准格式

    所有Agent间的通信都使用这个统一的消息结构。
    统一格式的好处：任何Agent都能解析其他Agent的消息，
    无需为每对Agent组合定义专用的消息格式。
    """
    id: str               # 消息唯一标识（UUID）
    from_agent: str        # 发送方Agent的ID
    to_agent: str          # 接收方Agent的ID
    message_type: str      # 消息类型：task/response/broadcast/heartbeat
    content: Dict          # 消息正文（灵活的字典结构）
    timestamp: datetime    # 发送时间
    priority: int = 1      # 优先级：1=高, 2=普通, 3=低

class AgentBus:
    """Agent消息总线

    提供三个核心能力：
    1. send()：点对点发送消息
    2. broadcast()：广播消息给所有Agent
    3. subscribe()：订阅消息并注册回调函数
    """

    def __init__(self):
        # 连接到本地Redis实例
        # 生产环境中这里会配置为Redis集群地址
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        self.subscribers = {}

    def send(self, msg: AgentMessage) -> bool:
        """发送消息到指定Agent

        设计亮点：消息同时通过两个通道发送
        1. Pub/Sub频道：实时推送（如果接收方在线，立即收到）
        2. Redis列表：持久化存储（如果接收方离线，上线后可以从列表中读取）

        这解决了一个关键问题：如果Agent暂时离线，它上线后不会错过任何消息。
        """
        channel = f"agent:{msg.to_agent}"

        message_data = {
            'id': msg.id,
            'from': msg.from_agent,
            'type': msg.message_type,
            'content': msg.content,
            'timestamp': msg.timestamp.isoformat(),
            'priority': msg.priority
        }

        # 通道1：Pub/Sub实时推送
        self.redis_client.publish(channel, json.dumps(message_data))

        # 通道2：持久化到Agent的收件箱列表
        # lpush将消息插入到列表头部，最新消息在最前面
        self.redis_client.lpush(
            f"agent:{msg.to_agent}:inbox",
            json.dumps(message_data)
        )

        return True

    def broadcast(self, from_agent: str, content: Dict,
                  exclude: List[str] = None):
        """广播消息给所有Agent

        使用场景：
        - 系统级公告（如"配置已更新，请重新加载"）
        - 全局事件通知（如"QMD索引已更新"）
        - 心跳检测（Friday定期广播，确认各Agent存活）

        Args:
            from_agent: 发送方Agent ID
            content: 广播内容
            exclude: 排除的Agent列表（通常排除发送方自己）
        """
        exclude = exclude or []

        for agent_id in self._get_all_agents():
            if agent_id not in exclude:
                msg = AgentMessage(
                    id=self._generate_id(),
                    from_agent=from_agent,
                    to_agent=agent_id,
                    message_type='broadcast',
                    content=content,
                    timestamp=datetime.now()
                )
                self.send(msg)

    def subscribe(self, agent_id: str, callback):
        """订阅消息并注册回调函数

        当有新消息到达时，callback函数会被自动调用。
        监听在独立的daemon线程中运行，不会阻塞主线程。

        Args:
            agent_id: 要订阅的Agent ID（即监听哪个Agent的频道）
            callback: 收到消息时调用的函数，接收一个dict参数
        """
        pubsub = self.redis_client.pubsub()
        pubsub.subscribe(f"agent:{agent_id}")

        self.subscribers[agent_id] = pubsub

        # 在独立线程中运行消息监听循环
        import threading
        thread = threading.Thread(
            target=self._listen_messages,
            args=(agent_id, pubsub, callback)
        )
        # daemon=True：主线程退出时，监听线程自动终止
        # 如果设为False，即使主程序退出，监听线程也会继续运行
        thread.daemon = True
        thread.start()

    def _listen_messages(self, agent_id: str, pubsub, callback):
        """消息监听循环（在独立线程中运行）

        这是一个无限循环，持续监听指定频道的消息。
        当收到非控制消息（type='message'）时，解析JSON并调用回调函数。
        """
        for message in pubsub.listen():
            if message['type'] == 'message':
                data = json.loads(message['data'])
                callback(data)

    def _get_all_agents(self) -> List[str]:
        """获取所有已注册Agent的ID列表"""
        # 实际实现中从配置文件读取
        return ['friday', 'trading', 'learning', 'architect',
                'frontend', 'backend', 'pm', 'qa']

    def _generate_id(self) -> str:
        """生成唯一消息ID"""
        import uuid
        return str(uuid.uuid4())
```

> **[知识补给站] Python threading基础**
>
> AgentBus的subscribe方法使用了Python线程来实现异步消息监听。以下是关键概念：
>
> ```python
> import threading
>
> # 创建线程
> thread = threading.Thread(target=my_function, args=(arg1, arg2))
>
> # daemon线程：主线程退出时自动终止
> thread.daemon = True  # 必须在start()之前设置
>
> # 启动线程
> thread.start()
> ```
>
> **daemon vs non-daemon线程：**
> - `daemon=True`：后台线程，主程序退出时自动终止。适用于监听、日志等辅助任务。
> - `daemon=False`（默认）：前台线程，主程序必须等待所有前台线程结束才能退出。适用于必须完成的任务。
>
> **线程安全基本概念：**
> - 多个线程同时读写同一个变量可能导致数据不一致
> - AgentBus中，Redis本身是线程安全的（每个操作是原子的），因此不需要额外的锁
> - 如果使用内存中的dict代替Redis，就需要使用`threading.Lock()`来保护共享数据

#### 消息类型与使用场景

| 消息类型 | 方向 | 场景示例 |
|---------|------|---------|
| `task` | Friday -> 专业Agent | "请执行ETH/USDT交易策略回测" |
| `response` | 专业Agent -> Friday | "回测完成，胜率65%，最大回撤12%" |
| `broadcast` | 任何Agent -> 所有Agent | "配置文件已更新，请重新加载" |
| `heartbeat` | Friday -> 所有Agent | "状态检查：请报告当前负载" |

### 自测题

**1.（选择题）AgentBus的send方法为什么同时使用Pub/Sub和Redis列表两种方式发送消息？**

A. Pub/Sub速度更快，列表更安全——双重保障
B. Pub/Sub实现实时推送（在线时立即收到），列表实现离线存储（Agent重启后不会丢失消息）
C. Pub/Sub用于广播，列表用于点对点
D. 这是Redis的技术限制，必须两种方式都使用

**答案：** B。Pub/Sub的特点是"即发即忘"——如果接收方不在线，消息就丢失了。Redis列表提供持久化存储，Agent上线后可以从inbox列表中读取遗漏的消息。两者结合实现了"实时 + 可靠"的消息传递。

**2.（简答题）如果要为AgentBus添加消息优先级处理能力（高优先级消息优先处理），你会如何修改设计？**

**参考答案：** 可以使用Redis的有序集合（Sorted Set）替代列表作为收件箱。将消息的priority作为score，读取时按score排序（ZRANGEBYSCORE），高优先级（score=1）的消息先被处理。具体修改：(1) 将`lpush`改为`zadd`，score使用priority值；(2) 读取时使用`zrangebyscore`按priority从低到高（1最高）获取消息；(3) 处理完成后使用`zrem`删除已处理的消息。

---

## 模块3.5：任务编排器

### 学习目标

完成本模块后，你应能够：

1. 描述Task的完整生命周期：PENDING -> ASSIGNED -> RUNNING -> COMPLETED/FAILED
2. 解释任务编排器的三个核心算法：依赖检查、技能匹配（match_ratio > 0.5）、负载均衡排序
3. 实现一个简化版的TaskOrchestrator，支持任务创建、自动分配和依赖触发

### 正文

#### Task生命周期

```
                   ┌─────────────────────────────────────────┐
                   │           Task 生命周期                   │
                   │                                         │
     create_task() │   PENDING ──────> ASSIGNED ──────> RUNNING
                   │      │               │                │
                   │      │               │           ┌────┴────┐
                   │      │               │           │         │
                   │      │               │      COMPLETED   FAILED
                   │      │               │           │
                   │      └───────────────┘           │
                   │      (依赖未完成时等待)             │
                   │                            (触发依赖任务)
                   └─────────────────────────────────────────┘
```

- **PENDING：** 任务已创建，等待分配。如果有未完成的依赖任务，会一直停留在此状态。
- **ASSIGNED：** 已找到合适的Agent，任务已发送给该Agent。
- **RUNNING：** Agent已开始执行任务。
- **COMPLETED：** 任务成功完成。此时会检查是否有其他任务依赖此任务，如果有，触发它们的分配流程。
- **FAILED：** 任务执行失败。可以设置重试策略或标记为永久失败。

#### TaskOrchestrator完整实现

```python
# task_orchestrator.py
# 任务编排器：管理任务的创建、分配、执行和完成
# 这是多Agent系统的"调度中心"——决定什么任务交给什么Agent
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import uuid

class TaskStatus(Enum):
    """任务状态枚举

    使用Enum而非字符串的好处：
    1. 防止拼写错误（TaskStatus.PENING会报错，"pening"不会）
    2. IDE自动补全
    3. 可以用 == 安全比较
    """
    PENDING = "pending"
    ASSIGNED = "assigned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Task:
    """任务数据结构

    每个任务包含：描述、所需技能、分配信息、状态、时间、依赖关系和结果。
    """
    id: str
    description: str
    required_skills: List[str]      # 完成此任务需要的技能列表
    assigned_agent: Optional[str]   # 被分配的Agent ID（未分配时为None）
    status: TaskStatus
    created_at: datetime
    deadline: Optional[datetime]    # 截止时间（可选）
    dependencies: List[str]         # 依赖的其他任务ID列表
    result: Optional[Dict] = None   # 任务执行结果（完成后填充）

class TaskOrchestrator:
    """任务编排器

    核心职责：
    1. 创建任务并尝试自动分配
    2. 根据技能匹配和负载均衡找到最佳Agent
    3. 处理任务完成后的依赖触发
    """

    def __init__(self, agent_config: Dict):
        """初始化编排器

        Args:
            agent_config: Agent配置字典，结构与agents.yml一致
        """
        self.agents = agent_config
        self.tasks = {}            # 所有任务的存储 {task_id: Task}
        self.agent_bus = AgentBus()

    def create_task(self, description: str,
                    required_skills: List[str],
                    deadline: Optional[datetime] = None,
                    dependencies: List[str] = None) -> str:
        """创建新任务并尝试自动分配

        工作流程：
        1. 生成唯一ID和Task对象
        2. 存入任务字典
        3. 调用_try_assign_task尝试自动分配

        如果有依赖任务未完成，任务会停留在PENDING状态，
        等依赖完成后再触发分配（在handle_task_completion中实现）。
        """
        task_id = str(uuid.uuid4())
        task = Task(
            id=task_id,
            description=description,
            required_skills=required_skills,
            assigned_agent=None,
            status=TaskStatus.PENDING,
            created_at=datetime.now(),
            deadline=deadline,
            dependencies=dependencies or []
        )

        self.tasks[task_id] = task

        # 立即尝试分配——如果依赖未完成，_try_assign_task会直接返回
        self._try_assign_task(task)

        return task_id

    def _try_assign_task(self, task: Task):
        """尝试为任务分配Agent

        分配前需要通过两个检查：
        1. 依赖检查：所有依赖的任务必须已完成
        2. Agent匹配：至少有一个Agent的技能匹配度>50%

        如果两个检查都通过，将任务分配给最佳Agent并发送消息。
        """
        # === 检查1：依赖是否全部完成 ===
        for dep_id in task.dependencies:
            dep_task = self.tasks.get(dep_id)
            # 如果依赖任务不存在或未完成，暂不分配
            if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                return

        # === 检查2：寻找合适的Agent ===
        best_agent = self._find_best_agent(task.required_skills)

        if best_agent:
            task.assigned_agent = best_agent
            task.status = TaskStatus.ASSIGNED

            # 通过消息总线发送任务给Agent
            msg = AgentMessage(
                id=str(uuid.uuid4()),
                from_agent="orchestrator",
                to_agent=best_agent,
                message_type="task",
                content={
                    'task_id': task.id,
                    'description': task.description,
                    'deadline': task.deadline.isoformat() if task.deadline else None
                },
                timestamp=datetime.now(),
                # 优先级判断：截止时间在24小时内的任务标记为高优先级
                priority=1 if task.deadline and (task.deadline - datetime.now()).days < 1 else 2
            )

            self.agent_bus.send(msg)

    def _find_best_agent(self, required_skills: List[str]) -> Optional[str]:
        """根据技能需求找到最佳Agent

        匹配算法：
        1. 计算每个Agent的技能匹配度 = 匹配的技能数 / 需要的技能数
        2. 过滤：匹配度必须 > 50%（至少一半技能匹配）
        3. 排序：先按匹配度降序，再按负载升序
        4. 返回排序后的第一个Agent

        为什么阈值是50%而不是100%？
        - 100%太严格：很难找到完全匹配的Agent
        - 50%是合理的折中：Agent至少具备一半以上的所需技能
        - 不足的技能可以由Agent的通用能力弥补
        """
        candidates = []

        for agent_id, config in self.agents.items():
            agent_skills = config.get('skills', [])
            # 没有skills字段的Agent（如Friday）不参与任务分配
            if not agent_skills and required_skills:
                continue

            # 计算技能匹配度
            match_count = sum(1 for skill in required_skills
                            if skill in agent_skills)
            match_ratio = match_count / len(required_skills) if required_skills else 0

            if match_ratio > 0.5:
                # 获取Agent当前负载（正在执行的任务数）
                load = self._get_agent_load(agent_id)
                candidates.append((agent_id, match_ratio, load))

        if not candidates:
            return None

        # 排序策略：匹配度优先（降序），匹配度相同时负载低的优先（升序）
        # -x[1] 使匹配度降序，x[2] 使负载升序
        candidates.sort(key=lambda x: (-x[1], x[2]))

        return candidates[0][0]

    def handle_task_completion(self, task_id: str, result: Dict):
        """处理任务完成

        当一个任务完成时，需要做两件事：
        1. 更新任务状态和结果
        2. 检查是否有其他任务依赖此任务——如果有，触发它们的分配流程

        这实现了"任务链"的自动推进：
        Task A完成 -> 检测到Task B依赖A -> 尝试分配Task B
        """
        task = self.tasks.get(task_id)
        if not task:
            return

        task.status = TaskStatus.COMPLETED
        task.result = result

        # 遍历所有任务，找到依赖此任务的PENDING任务
        for t in self.tasks.values():
            if task_id in t.dependencies and t.status == TaskStatus.PENDING:
                # 重新尝试分配——此时依赖可能已经全部满足
                self._try_assign_task(t)

    def get_system_status(self) -> Dict:
        """获取系统状态概览

        返回各状态的任务数量和每个Agent的当前负载。
        这为监控和管理提供数据支持。
        """
        status = {
            'total_tasks': len(self.tasks),
            'pending': sum(1 for t in self.tasks.values()
                         if t.status == TaskStatus.PENDING),
            'running': sum(1 for t in self.tasks.values()
                         if t.status == TaskStatus.RUNNING),
            'completed': sum(1 for t in self.tasks.values()
                            if t.status == TaskStatus.COMPLETED),
            'failed': sum(1 for t in self.tasks.values()
                         if t.status == TaskStatus.FAILED),
            'agent_loads': {agent_id: self._get_agent_load(agent_id)
                          for agent_id in self.agents}
        }

        return status

    def _get_agent_load(self, agent_id: str) -> int:
        """获取Agent当前负载（正在执行的任务数）"""
        return sum(
            1 for t in self.tasks.values()
            if t.assigned_agent == agent_id
            and t.status in (TaskStatus.ASSIGNED, TaskStatus.RUNNING)
        )
```

#### 依赖图示例

```
任务A: "获取ETH价格数据"         任务B: "计算技术指标"
   (无依赖)                        (依赖: A)
      │                              │
      ▼                              ▼
   trading Agent                  等待A完成...
   执行中...                        │
      │                              │
      ▼ 完成！                       │
   handle_task_completion(A)         │
      └──> 检测到B依赖A ────────────>│
                                     ▼
                                  _try_assign_task(B)
                                  依赖检查通过 -> 分配给trading
```

> **[知识补给站] 分布式系统中的"最终一致性"**
>
> 在多Agent系统中，不同Agent可能在不同时刻看到不同的系统状态。例如，Friday刚把一个任务标记为"已分配"，但trading Agent还没收到消息。这就是分布式系统中常见的"一致性"问题。
>
> **类比：快递系统**
> 你在网上查到"包裹已发出"，但快递员可能还没拿到包裹——物流信息和实际状态之间有延迟。这种"暂时的不一致但最终会一致"的状态就是**最终一致性（Eventual Consistency）**。
>
> 在OpenClaw中，通过以下机制保障最终一致性：
> - 消息持久化（Redis列表）确保消息不丢失
> - 任务状态有明确的生命周期（PENDING -> ASSIGNED -> ...），不会跳跃
> - 定期的状态同步（heartbeat广播）检测不一致并修复

### 自测题

**1.（选择题）_find_best_agent()中，如果Agent A的匹配度是0.8、负载是3个任务，Agent B的匹配度是0.6、负载是1个任务，系统会选择谁？**

A. Agent A（匹配度更高）
B. Agent B（负载更低）
C. 随机选择
D. 两个都不选（因为负载太高）

**答案：** A。排序规则是"先按匹配度降序，再按负载升序"。匹配度是第一优先级：A(0.8) > B(0.6)，因此选择A。只有在匹配度相同时，才会考虑负载。这体现了"能力匹配优于负载均衡"的设计理念——把任务交给最擅长的Agent比交给最闲的Agent更重要。

**2.（简答题）请描述当Task C依赖Task A和Task B时，系统如何保证Task C在A和B都完成后才被分配？**

**参考答案：** Task C创建时设置`dependencies=["task_a_id", "task_b_id"]`。创建后立即调用`_try_assign_task(C)`，此时A和B都未完成，依赖检查不通过，C停留在PENDING状态。当A完成时，`handle_task_completion(A)`遍历所有任务，找到依赖A的C，尝试分配——但此时B还未完成，依赖检查仍然不通过，C继续等待。当B也完成时，`handle_task_completion(B)`再次找到C并尝试分配——此时A和B都是COMPLETED，依赖检查通过，C被成功分配给匹配度最高的Agent。

**3.（选择题）handle_task_completion()方法中，为什么要遍历所有任务而不是只遍历"已知的依赖方"？**

A. 因为代码写得不好，应该优化
B. 因为Task对象中只存储了"我依赖谁"（dependencies），而没有存储"谁依赖我"（dependents），所以需要反向查找
C. 因为需要更新所有任务的状态
D. 因为广播机制要求通知所有任务

**答案：** B。当前数据结构中，Task只记录了正向依赖关系（我依赖哪些任务），没有记录反向依赖（哪些任务依赖我）。如果性能成为瓶颈（任务数量很大时），可以增加一个反向索引：`dependents: Dict[str, List[str]]`，在创建任务时同时建立反向关系，避免全量遍历。

---

## 模块3.6：记忆同步

### 学习目标

完成本模块后，你应能够：

1. 解释为什么多Agent系统需要记忆同步机制
2. 阅读并理解AgentMemorySync的实现，说明其三种同步内容（MEMORY.md、每日记忆、学习记录）
3. 描述QMD索引更新在记忆同步中的作用

### 正文

#### 为什么需要记忆同步？

每个Agent有独立的workspace和记忆文件。如果没有同步机制，会出现以下问题：

- trading Agent发现了一个重要的市场模式，但architect Agent在设计监控系统时无法获取这个信息
- frontend Agent修复了一个UI bug的经验，但QA Agent无法在后续测试中利用这个经验
- Friday作为用户交互入口，无法全面了解各专业Agent的工作进展

记忆同步确保了：**每个Agent的经验和知识能够被整个系统共享。**

#### AgentMemorySync完整实现

```python
# memory_sync.py
# Agent间记忆同步系统
# 核心功能：将所有Agent的记忆文件同步到统一存储位置，
# 并更新QMD向量索引使其可被全局搜索
import os
import shutil
from datetime import datetime
from typing import List

class AgentMemorySync:
    """Agent间记忆同步系统

    同步三类内容：
    1. 长期记忆（MEMORY.md）：Agent的核心知识和经验
    2. 每日记忆（memory/YYYY-MM-DD.md）：日常工作记录
    3. 学习记录（.learnings/*.md）：执行任务过程中积累的教训

    同步策略：基于文件修改时间的增量同步
    只复制"源文件更新时间晚于目标文件"的文件，避免不必要的IO操作
    """

    def __init__(self):
        self.agents = [
            'friday', 'trading', 'learning', 'architect',
            'frontend', 'backend', 'pm', 'qa'
        ]
        self.base_path = "~/.openclaw"
        # 同步目标：统一的记忆存储位置
        self.openviking_path = "~/.openviking/memory/long_term/core"

    def sync_all(self):
        """同步所有Agent的记忆

        这个方法通常由定时任务每天调用一次。
        遍历所有Agent，依次同步每个Agent的三类记忆文件，
        最后更新QMD向量索引。
        """
        print("同步所有 Agent 记忆到 OpenViking...")

        for agent in self.agents:
            self._sync_agent_memory(agent)

        # 所有Agent同步完成后，更新向量索引
        # 这确保新同步的内容可以被QMD搜索到
        self._update_qmd_index()

        print("所有 Agent 记忆同步完成！")

    def _sync_agent_memory(self, agent_id: str):
        """同步单个Agent的所有记忆

        按优先级同步三类内容：
        1. MEMORY.md（最重要，包含核心经验）
        2. 每日记忆文件（工作记录）
        3. 学习记录（执行任务中的教训）
        """
        agent_workspace = f"{self.base_path}/workspace-{agent_id}"

        # === 同步长期记忆 ===
        memory_src = f"{agent_workspace}/MEMORY.md"
        memory_dst = f"{self.openviking_path}/{agent_id}_MEMORY.md"

        if os.path.exists(memory_src):
            if self._file_changed(memory_src, memory_dst):
                shutil.copy2(memory_src, memory_dst)
                # copy2保留文件的修改时间等元数据
                print(f"  {agent_id}: MEMORY.md 已同步")
            else:
                print(f"  {agent_id}: MEMORY.md 无变化，跳过")

        # === 同步每日记忆 ===
        self._sync_daily_memories(agent_id, agent_workspace)

        # === 同步学习记录 ===
        self._sync_learnings(agent_id, agent_workspace)

    def _sync_daily_memories(self, agent_id: str, workspace: str):
        """同步每日记忆文件

        只同步2026年之后的文件（历史文件假设已经同步过）。
        使用文件修改时间判断是否需要更新。
        """
        daily_src = f"{workspace}/memory"
        daily_dst = f"{self.openviking_path}/{agent_id}_daily"

        if not os.path.exists(daily_src):
            return

        os.makedirs(daily_dst, exist_ok=True)

        for filename in os.listdir(daily_src):
            # 只处理2026年之后的Markdown文件
            if filename.endswith('.md') and filename.startswith('2026-'):
                src_file = f"{daily_src}/{filename}"
                dst_file = f"{daily_dst}/{filename}"

                # 增量同步：只在源文件比目标文件新时才复制
                if not os.path.exists(dst_file) or \
                   os.path.getmtime(src_file) > os.path.getmtime(dst_file):
                    shutil.copy2(src_file, dst_file)
                    print(f"  同步每日记忆: {agent_id}/{filename}")

    def _sync_learnings(self, agent_id: str, workspace: str):
        """同步学习记录

        学习记录是Agent在执行任务过程中积累的经验和教训。
        例如：trading Agent发现"在高波动率市场中，网格间距应加大20%"
        这些经验对其他Agent也可能有参考价值。
        """
        learnings_src = f"{workspace}/.learnings"
        learnings_dst = f"{self.openviking_path}/{agent_id}_learnings"

        if not os.path.exists(learnings_src):
            return

        os.makedirs(learnings_dst, exist_ok=True)

        for filename in os.listdir(learnings_src):
            if filename.endswith('.md'):
                src_file = f"{learnings_src}/{filename}"
                dst_file = f"{learnings_dst}/{filename}"

                if self._file_changed(src_file, dst_file):
                    shutil.copy2(src_file, dst_file)

    def _file_changed(self, src: str, dst: str) -> bool:
        """检查源文件是否比目标文件更新

        基于文件修改时间的简单判断：
        - 如果目标文件不存在 -> 需要同步
        - 如果源文件的修改时间晚于目标文件 -> 需要同步
        """
        if not os.path.exists(dst):
            return True

        return os.path.getmtime(src) > os.path.getmtime(dst)

    def _update_qmd_index(self):
        """更新QMD向量索引

        同步完文件后，需要让QMD重新索引这些文件，
        这样新的记忆内容才能通过语义搜索被检索到。

        这是记忆同步的"最后一公里"：文件同步了但索引没更新，
        等于新内容对搜索系统来说是不可见的。
        """
        import subprocess
        result = subprocess.run(
            ['qmd', 'update'],
            capture_output=True,
            text=True
        )
        print(result.stdout)
```

#### 记忆同步的完整数据流

```
各Agent独立工作空间              统一存储             搜索服务
┌──────────────────┐          ┌──────────┐        ┌──────┐
│ friday/           │ ──sync──>│          │        │      │
│   MEMORY.md       │          │ openviking│──index──>│ QMD  │
│   memory/*.md     │          │   /core/  │        │      │
│   .learnings/*.md │          │          │        │      │
├──────────────────┤          │ friday_  │        │      │
│ trading/          │ ──sync──>│ MEMORY.md│        │ 全局 │
│   MEMORY.md       │          │ trading_ │        │ 语义 │
│   memory/*.md     │          │ MEMORY.md│        │ 搜索 │
├──────────────────┤          │ ...      │        │      │
│ architect/        │ ──sync──>│          │        │      │
│   MEMORY.md       │          │          │        │      │
└──────────────────┘          └──────────┘        └──────┘
     每个Agent                   文件同步            索引更新
     独立积累经验                 集中存储            可被搜索
```

### 自测题

**1.（选择题）为什么记忆同步后需要调用`_update_qmd_index()`？**

A. 因为QMD在文件同步时会自动检测变化
B. 因为文件同步只是把文件复制到了统一位置，但QMD的向量索引还是旧的——不更新索引，新内容无法被语义搜索找到
C. 因为QMD需要清除旧的索引
D. 因为这是一个安全检查步骤

**答案：** B。QMD的搜索依赖向量索引，而向量索引不会因为底层文件变化自动更新。必须显式调用`qmd update`重建索引，新同步的记忆内容才能出现在搜索结果中。

**2.（简答题）如果同步频率从每天一次改为实时同步（每次Agent写入记忆文件就立即同步），会有什么优缺点？**

**参考答案：**
优点：(1) 记忆的"新鲜度"大幅提升，Agent刚产生的经验几乎立即可被其他Agent检索；(2) 减少了不一致窗口期。
缺点：(1) IO开销大幅增加——每次文件写入都触发网络传输和QMD索引重建；(2) QMD索引频繁重建会影响搜索性能；(3) 如果Agent高频写入（如trading Agent每秒产生交易日志），同步开销可能成为瓶颈。折中方案：可以使用"批量延迟同步"——检测到文件变化后，等待30秒再执行同步，将多次变化合并为一次同步操作。

---

## 练习设计

### 练习（35分钟）：实现简化版TaskOrchestrator

**题目描述：**

实现一个简化版的TaskOrchestrator，支持以下功能：
- `create_task()`：创建任务并尝试自动分配
- `_find_best_agent()`：基于技能匹配度找到最佳Agent（匹配度>50%）
- `handle_task_completion()`：标记完成并触发依赖任务

测试场景：3个Agent、4个有依赖关系的任务，验证分配和依赖触发逻辑。

**骨架代码：**

```python
# exercise_05_task_orchestrator.py
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

class TaskStatus(Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    COMPLETED = "completed"

@dataclass
class Task:
    id: str
    description: str
    required_skills: List[str]
    assigned_agent: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    dependencies: List[str] = field(default_factory=list)
    result: Optional[Dict] = None

class SimpleOrchestrator:
    def __init__(self, agents: Dict):
        """初始化编排器

        Args:
            agents: Agent配置字典
            格式: {"agent_id": {"skills": ["skill1", "skill2"], ...}, ...}
        """
        self.agents = agents
        self.tasks: Dict[str, Task] = {}
        self._task_counter = 0

    def create_task(self, description: str,
                    required_skills: List[str],
                    dependencies: List[str] = None) -> str:
        """创建任务并尝试自动分配

        TODO 1: 完成以下步骤：
        1. 生成任务ID（使用 self._next_id()）
        2. 创建Task对象
        3. 存入self.tasks
        4. 调用_try_assign_task尝试分配
        5. 返回任务ID
        """
        ______

    def _try_assign_task(self, task: Task):
        """尝试分配任务

        TODO 2: 完成以下步骤：
        1. 检查所有依赖是否已完成（COMPLETED）
        2. 如果依赖未全部完成，直接返回（不分配）
        3. 调用_find_best_agent找到最佳Agent
        4. 如果找到，更新task的assigned_agent和status
        """
        ______

    def _find_best_agent(self, required_skills: List[str]) -> Optional[str]:
        """找到最佳Agent

        TODO 3: 完成以下步骤：
        1. 遍历所有Agent
        2. 计算技能匹配度 = 匹配技能数 / 需要技能数
        3. 过滤匹配度 > 0.5 的Agent
        4. 按匹配度降序排列
        5. 返回第一个Agent的ID（或None）
        """
        ______

    def handle_task_completion(self, task_id: str, result: Dict = None):
        """处理任务完成

        TODO 4: 完成以下步骤：
        1. 获取任务并标记为COMPLETED
        2. 保存result
        3. 遍历所有PENDING任务，找到依赖此任务的
        4. 对每个找到的任务调用_try_assign_task
        """
        ______

    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """获取任务状态"""
        task = self.tasks.get(task_id)
        return task.status if task else None

    def _next_id(self) -> str:
        """生成递增的任务ID"""
        self._task_counter += 1
        return f"task_{self._task_counter}"


# ===== 测试用例 =====
if __name__ == "__main__":
    # 定义3个Agent
    agents = {
        "data_agent": {
            "skills": ["data_fetching", "data_cleaning", "sql"]
        },
        "ml_agent": {
            "skills": ["model_training", "feature_engineering", "data_cleaning"]
        },
        "report_agent": {
            "skills": ["visualization", "report_generation", "data_cleaning"]
        }
    }

    orchestrator = SimpleOrchestrator(agents)

    # === 测试1：创建无依赖任务并自动分配 ===
    task_a = orchestrator.create_task(
        description="获取并清洗交易数据",
        required_skills=["data_fetching", "data_cleaning"]
    )
    assert orchestrator.get_task_status(task_a) == TaskStatus.ASSIGNED, \
        f"测试1失败：无依赖任务应被自动分配，实际状态={orchestrator.get_task_status(task_a)}"
    assert orchestrator.tasks[task_a].assigned_agent == "data_agent", \
        f"测试1失败：应分配给data_agent，实际分配给{orchestrator.tasks[task_a].assigned_agent}"
    print("测试1通过：无依赖任务自动分配给data_agent")

    # === 测试2：创建有依赖的任务 ===
    task_b = orchestrator.create_task(
        description="训练ML模型",
        required_skills=["model_training", "feature_engineering"],
        dependencies=[task_a]  # 依赖task_a
    )
    assert orchestrator.get_task_status(task_b) == TaskStatus.PENDING, \
        f"测试2失败：有未完成依赖的任务应保持PENDING，实际状态={orchestrator.get_task_status(task_b)}"
    print("测试2通过：有依赖的任务保持PENDING")

    # === 测试3：完成依赖任务后触发分配 ===
    orchestrator.handle_task_completion(task_a, result={"rows": 10000})
    assert orchestrator.get_task_status(task_a) == TaskStatus.COMPLETED, \
        "测试3失败：task_a应标记为COMPLETED"
    assert orchestrator.get_task_status(task_b) == TaskStatus.ASSIGNED, \
        f"测试3失败：task_a完成后task_b应被自动分配，实际状态={orchestrator.get_task_status(task_b)}"
    assert orchestrator.tasks[task_b].assigned_agent == "ml_agent", \
        f"测试3失败：task_b应分配给ml_agent，实际分配给{orchestrator.tasks[task_b].assigned_agent}"
    print("测试3通过：依赖完成后自动触发分配")

    # === 测试4：多重依赖 ===
    task_c = orchestrator.create_task(
        description="生成分析报告",
        required_skills=["visualization", "report_generation"],
        dependencies=[task_a, task_b]  # 依赖task_a和task_b
    )
    # task_a已完成，但task_b未完成
    assert orchestrator.get_task_status(task_c) == TaskStatus.PENDING, \
        "测试4a失败：task_b未完成时task_c应保持PENDING"
    print("测试4a通过：多重依赖中有一个未完成，任务保持PENDING")

    # 完成task_b
    orchestrator.handle_task_completion(task_b, result={"accuracy": 0.85})
    assert orchestrator.get_task_status(task_c) == TaskStatus.ASSIGNED, \
        f"测试4b失败：所有依赖完成后task_c应被分配，实际状态={orchestrator.get_task_status(task_c)}"
    assert orchestrator.tasks[task_c].assigned_agent == "report_agent", \
        f"测试4b失败：task_c应分配给report_agent"
    print("测试4b通过：所有依赖完成后自动分配")

    print("\n所有测试通过！")
```

**期望输出：**

```
测试1通过：无依赖任务自动分配给data_agent
测试2通过：有依赖的任务保持PENDING
测试3通过：依赖完成后自动触发分配
测试4a通过：多重依赖中有一个未完成，任务保持PENDING
测试4b通过：所有依赖完成后自动分配

所有测试通过！
```

**评分维度：**
- create_task()正确创建任务并尝试自动分配（20%）
- _try_assign_task()正确实现依赖检查（20%）
- _find_best_agent()正确实现技能匹配度计算和排序（25%）
- handle_task_completion()正确触发依赖任务的分配（20%）
- 所有4组测试用例通过（10%）
- 代码风格和注释（5%）

---

## 本课知识总结

### 核心概念回顾

| 概念 | 定义 | 关键代码/配置 |
|------|------|-------------|
| **单Agent瓶颈** | 上下文竞争、领域干扰、并行限制、单点故障 | 设计分析，无对应代码 |
| **三层架构** | 主Agent + 专业Agent集群 + 共享基础设施 | 架构图 |
| **Agent配置** | YAML格式定义Agent的name/role/workspace/model/responsibilities/skills | `agents.yml` |
| **消息总线** | 基于Redis Pub/Sub的Agent间通信机制 | `AgentBus.send/broadcast/subscribe` |
| **任务编排** | 创建 -> 依赖检查 -> 技能匹配 -> 负载均衡 -> 分配 | `TaskOrchestrator` |
| **技能匹配** | match_ratio = 匹配技能数 / 需求技能数，阈值 > 0.5 | `_find_best_agent()` |
| **依赖触发** | 任务完成时检查并触发依赖此任务的其他任务 | `handle_task_completion()` |
| **记忆同步** | 将各Agent的记忆文件同步到统一存储并更新QMD索引 | `AgentMemorySync.sync_all()` |

### 核心结论

1. **单Agent架构的瓶颈本质上是"单一职责原则"的违背。** 当一个Agent承担过多领域的职责时，上下文竞争和领域干扰是不可避免的。
2. **多Agent架构的关键在于"分工而不分裂"。** 专业Agent各司其职，但通过消息总线、共享记忆和任务编排紧密协作。
3. **消息的"实时推送 + 持久化存储"双通道设计解决了离线消息丢失问题。** 这是分布式系统中常见的可靠性保障模式。
4. **技能匹配度 > 50%的阈值是实用性和灵活性的平衡。** 过高的阈值（如100%）会导致很多任务无法分配，过低则可能把任务交给不胜任的Agent。
5. **记忆同步是多Agent系统的"隐藏英雄"。** 没有同步机制，多Agent系统就是一组互不相知的个体，而非一个协作的团队。

---

## 扩展阅读与资源推荐

1. **Redis官方文档 - Pub/Sub：** https://redis.io/docs/interact/pubsub/ —— Redis发布/订阅模式的完整说明
2. **Python threading文档：** https://docs.python.org/3/library/threading.html —— 线程编程的完整参考
3. **《Designing Data-Intensive Applications》：** Martin Kleppmann著，分布式系统设计的经典教材，特别是"一致性与共识"章节
4. **LangChain Multi-Agent文档：** https://python.langchain.com/docs/modules/agents/ —— 另一种多Agent框架的实现思路，可供对比学习
5. **《Enterprise Integration Patterns》：** Gregor Hohpe著，消息传递和集成模式的百科全书，消息总线、路由、过滤等模式都有详细讲解
6. **AutoGen项目：** https://github.com/microsoft/autogen —— 微软的多Agent对话框架，展示了另一种Agent协作的实现方式

---

> **下节课预告：** 我们已经构建了记忆系统（第1课）、模型路由（第2课）和多Agent架构（第3课）——这是AI Agent系统的三大基础设施。第4课将进入应用层面：**如何让Agent写出高质量的代码？** 我们将学习Skill系统的设计理念和结构化代码生成工作流，从"无约束的代码生成"进化到"有规范、可复现、质量稳定"的代码生成。
