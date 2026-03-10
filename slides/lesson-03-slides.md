# 第3课课件：从独行侠到团队 -- 多Agent架构设计与实现

> 课件脚本 | 对应讲义：lesson-03-multi-agent.md | 对应讲课稿：lesson-03-script.md
> 总页数：35页 | 建议时长：3小时

---

<!-- Page 1 -->
## [COVER] Slide 3-0a

# AI Agent系统工程实战

### 第3课：从独行侠到团队
### -- 多Agent架构设计与实现

对应原文：第4章 | 难度：中高级 | 时长：3小时

---

<!-- Page 2 -->
## [TOC] Slide 3-0b

### 今天的旅程

| 模块 | 主题 | 时间 |
|------|------|------|
| 3.1 | 单Agent瓶颈分析 | 0:00-0:25 |
| 3.2 | 多Agent架构设计 | 0:25-0:50 |
| 3.3 | Agent定义规范 | 0:45-1:00 |
| 3.4 | 通信机制实现 | 1:00-1:15 |
| -- | 休息 | 1:15-1:25 |
| 3.5 | 任务编排器 | 1:25-2:00 |
| -- | 练习：实现TaskOrchestrator | 2:00-2:35 |
| 3.6 | 记忆同步 | 2:35-2:50 |
| -- | 总结 | 2:50-3:00 |

---

<!-- Page 3 -->
## [QUESTION] Slide 3-1a

> 对应讲课稿 [互动]：你会让一个全栈工程师同时负责前端、后端、运维、QA吗？

# 你会怎么做？

如果你是CTO，你会让一个全栈工程师
**同时负责前端、后端、运维、QA和产品经理吗？**

当然不会 --> 你会组建专业团队。

---

<!-- Page 4 -->
## [CONCEPT] Slide 3-1b

### 模块 3.1 -- 单Agent瓶颈分析

# "全能选手"的崩溃

一个Agent同时做量化交易 + 写代码 + 写文章 + 管项目

就像一个人同时当厨师、服务员、收银员和清洁工

---

<!-- Page 5 -->
## [DIAGRAM] Slide 3-1c

### 上下文窗口被挤占

```
单Agent的上下文窗口（128K tokens）：
+-------------------------------------------+
| 系统提示词 (2K)                            |
| 交易策略上下文 (30K)                        |
| 代码开发上下文 (30K)                        |
| 写作项目上下文 (20K)                        |
| 项目管理上下文 (15K)                        |
| 对话历史 (20K)                             |
| 剩余空间: 11K  <-- 几乎没有余量             |
+-------------------------------------------+
```

---

<!-- Page 6 -->
## [TABLE] Slide 3-1d

### 四大瓶颈

| 瓶颈 | 具体表现 |
|------|---------|
| 上下文竞争 | 多领域知识争夺有限窗口空间 |
| 领域干扰 | "严谨分析师"与"创意写手"人设打架 |
| 并行限制 | 同一时间只能处理一个任务 |
| 单点故障 | 一个模块出错，整个Agent崩溃 |

> 本质：违反了**单一职责原则**

---

<!-- Page 7 -->
## [QUESTION] Slide 3-1e

> 对应讲课稿 [互动]：哪个瓶颈是增加上下文窗口也解决不了的？

# 哪个瓶颈无法靠增大窗口解决？

四个瓶颈：上下文竞争 / 领域干扰 / 并行限制 / 单点故障

**答案：领域干扰。**

即使窗口无限大，
"严谨分析师"和"创意写手"的冲突依然存在。

---

<!-- Page 8 -->
## [TRANSITION] Slide 3-1to2

# 解决方案

把一个"全能但平庸"的Agent

拆分成多个"专精且高效"的Agent

--> **多Agent架构**

---

<!-- Page 9 -->
## [DIAGRAM] Slide 3-2a

### 模块 3.2 -- OpenClaw三层架构

```
+-------------------------------------------------------+
| 第一层：主Agent (Friday)                                |
| - 用户交互的唯一入口（门面模式）                          |
| - 任务分发与协调 / 记忆同步                              |
+-------------------------------------------------------+
| 第二层：专业Agent集群                                    |
| [桑丘]    [参孙]    [建筑师]  [PM]                      |
| trading   learning  arch      pm                       |
| [前端]    [后端]    [QA]                                |
| frontend  backend   qa                                 |
+-------------------------------------------------------+
| 第三层：共享基础设施                                     |
| [QMD记忆] [消息总线] [定时调度] [配置管理]                |
+-------------------------------------------------------+
```

---

<!-- Page 10 -->
## [CONCEPT] Slide 3-2b

### Friday -- 门面模式

# 用户只需要跟Friday对话

Friday = 公司前台

- 接收请求 --> 分发给专业Agent
- 返回结果 --> 隐藏内部复杂性
- 同步记忆 --> 确保团队信息一致

> 用户不需要知道后面有多少个Agent

---

<!-- Page 11 -->
## [TABLE] Slide 3-2c

### 四大瓶颈如何被解决

| 瓶颈 | 多Agent如何解决 |
|------|----------------|
| 上下文竞争 | 每个Agent只加载自己领域的上下文 |
| 领域干扰 | 每个Agent有独立的系统提示词 |
| 并行限制 | 不同Agent可以并行处理不同任务 |
| 单点故障 | 一个Agent故障不影响其他Agent |

---

<!-- Page 12 -->
## [QUESTION] Slide 3-2d

> 对应讲课稿 [互动]：共享基础设施为什么要共享？8个Agent点对点要多少条连接？

# 为什么基础设施要共享？

如果不共享消息总线，8个Agent之间

**点对点连接 = 8 x 7 / 2 = 28条**

共享消息总线 --> **只需8条**

---

<!-- Page 13 -->
## [TABLE] Slide 3-2e

### 共享 vs 独立

| 组件 | 共享原因 |
|------|---------|
| QMD记忆 | 避免知识孤岛，经验全局可用 |
| 消息总线 | N条连接 vs N*(N-1)/2条 |
| 定时调度 | 避免时间冲突和资源浪费 |
| 配置管理 | 一处修改，全局生效 |

---

<!-- Page 14 -->
## [CONCEPT] Slide 3-3a

### 模块 3.3 -- Agent定义规范

# 六个关键配置字段

| 字段 | 作用 |
|------|------|
| **name** | 人类可读名称（日志/监控用） |
| **role** | 角色定位（决定系统提示词基调） |
| **workspace** | 独立工作空间（文件隔离） |
| **model** | 使用的LLM（匹配任务类型） |
| **responsibilities** | 做什么（任务分发依据） |
| **skills** | 用什么（能力匹配依据） |

---

<!-- Page 15 -->
## [CODE] Slide 3-3b

### Agent配置YAML示例

```yaml
agents:
  friday:
    name: "星期五"
    role: "主助手"                          # <-- 重点
    workspace: "~/.openclaw/workspace"
    model: "moonshot/kimi-k2.5"
    responsibilities:
      - 用户交互
      - 任务分发
      - 记忆同步

  trading:
    name: "桑丘"
    role: "量化交易助手"                     # <-- 重点
    workspace: "~/.openclaw/workspace-trading"
    model: "moonshot/kimi-k2.5"
```

---

<!-- Page 16 -->
## [QUESTION] Slide 3-3c

> 对应讲课稿 [互动]：responsibilities和skills有什么区别？

# responsibilities vs skills

**桑丘(trading)的配置：**

- responsibilities: 加密货币量化策略 / 风险管理 / 交易监控
- skills: binance-pro / polymarket-analysis

**区别是什么？**

responsibilities = "做什么"（职责范围）
skills = "用什么"（具体工具）

---

<!-- Page 17 -->
## [CONCEPT] Slide 3-3d

### Agent设计三原则

1. **数量要克制**
   - 从3个起步，按需扩展到8个

2. **模型选择要匹配**
   - 代码Agent --> Claude / 分析Agent --> Kimi

3. **职责边界要清晰**
   - 两个Agent的responsibilities重叠>30% --> 合并或重划

---

<!-- Page 18 -->
## [CONCEPT] Slide 3-4a

### 模块 3.4 -- 通信机制

# 发布订阅 vs 点对点

```
点对点：8个Agent = 28条连接（管理噩梦）

发布订阅：8个Agent = 8条连接（清爽）
```

OpenClaw选择 **Pub/Sub**，使用 **Redis** 作为消息中间件

---

<!-- Page 19 -->
## [DIAGRAM] Slide 3-4b

### 发布订阅架构

```
Agent A --+
Agent B --+--> [Redis 消息总线] --+--> Agent A
Agent C --+                      +--> Agent B
          ...                    +--> Agent C
                                 ...
```

- 每个Agent只连消息总线
- 加新Agent只需新增1条连接
- 频道隔离：agent:trading / agent:frontend / ...

---

<!-- Page 20 -->
## [DIAGRAM] Slide 3-4c

### send()的双通道设计

```
AgentBus.send(msg)
    |
    +--> 通道1: Redis Pub/Sub
    |    实时推送（在线立即收到）
    |
    +--> 通道2: Redis 列表 (lpush)
         持久化存储（离线不丢消息）
```

> 类比：微信消息 = 实时推送 + 服务器存储

---

<!-- Page 21 -->
## [QUESTION] Slide 3-4d

> 对应讲课稿 [互动]：为什么要用两个通道？一个不行吗？

# 为什么send()用两个通道？

**Pub/Sub特性："即发即忘"**

接收方不在线 --> 消息丢失

Redis列表 = "收件箱"

Agent重启后从收件箱读取遗漏消息

---

<!-- Page 22 -->
## [TABLE] Slide 3-4e

### 四种消息类型

| 类型 | 方向 | 场景 |
|------|------|------|
| task | Friday --> 专业Agent | "执行ETH回测" |
| response | 专业Agent --> Friday | "回测完成，胜率65%" |
| broadcast | 任何 --> 所有Agent | "配置已更新" |
| heartbeat | Friday --> 所有Agent | "请报告当前负载" |

---

<!-- Page 23 -->
## [CONCEPT] Slide 3-5a

### 模块 3.5 -- 任务编排器

# Task生命周期

```
PENDING --> ASSIGNED --> RUNNING --> COMPLETED
                                 \-> FAILED
```

- PENDING：等待分配（依赖未完成时等待）
- ASSIGNED：已找到Agent
- COMPLETED：完成后触发依赖任务

---

<!-- Page 24 -->
## [DIAGRAM] Slide 3-5b

### Task完整生命周期

```
 create_task()
      |
      v
   PENDING ---------> ASSIGNED ---------> RUNNING
      |                  |                    |
      |                  |               +----+----+
      |                  |               |         |
      +------------------+          COMPLETED   FAILED
      (依赖未完成时等待)        (触发依赖任务)
```

---

<!-- Page 25 -->
## [DIAGRAM] Slide 3-5c

### 技能匹配算法

```
匹配度 = 匹配的技能数 / 需要的技能数

示例：任务需要 [data_fetching, data_cleaning]

  data_agent:  [data_fetching, data_cleaning, sql]
               匹配 2/2 = 1.0  <-- 最佳

  ml_agent:    [model_training, feature_eng, data_cleaning]
               匹配 1/2 = 0.5  <-- 刚好达标

  report_agent: [visualization, report_gen, data_cleaning]
               匹配 1/2 = 0.5

过滤：匹配度 > 0.5
排序：匹配度降序 --> 负载升序
```

---

<!-- Page 26 -->
## [QUESTION] Slide 3-5d

> 对应讲课稿 [互动]：Agent A匹配度0.8负载3，Agent B匹配度0.6负载1，选谁？

# 选谁？

- Agent A：匹配度 0.8，负载 3个任务
- Agent B：匹配度 0.6，负载 1个任务

**答案：选A。**

匹配度是第一排序条件（0.8 > 0.6）

> 能力匹配优先于负载均衡

---

<!-- Page 27 -->
## [DIAGRAM] Slide 3-5e

### 依赖触发流程

```
Task A: "获取ETH数据" (无依赖) --> 立即分配
Task B: "计算指标" (依赖A) --> PENDING等待

A执行完成
    |
    v
handle_task_completion(A)
    |
    v
遍历所有PENDING任务
发现B依赖A --> _try_assign_task(B)
    |
    v
依赖检查通过 --> B被分配
```

---

<!-- Page 28 -->
## [CODE] Slide 3-5f

### handle_task_completion 核心逻辑

```python
def handle_task_completion(self, task_id: str, result: Dict):
    task = self.tasks.get(task_id)
    if not task:
        return

    task.status = TaskStatus.COMPLETED        # <-- 重点
    task.result = result

    for t in self.tasks.values():
        if task_id in t.dependencies \
           and t.status == TaskStatus.PENDING: # <-- 重点
            self._try_assign_task(t)
```

---

<!-- Page 29 -->
## [EXERCISE] Slide 3-5g

### 练习：实现简化版TaskOrchestrator

- **时间：** 35分钟
- **四个TODO：** create_task / _try_assign_task / _find_best_agent / handle_task_completion
- **测试场景：** 3个Agent + 4个有依赖关系的任务
- **验证：** 无依赖分配 / 依赖等待 / 依赖触发 / 多重依赖
- **文件：** exercise_05_task_orchestrator.py

---

<!-- Page 30 -->
## [CONCEPT] Slide 3-6a

### 模块 3.6 -- 记忆同步

# 没有同步 = 知识孤岛

桑丘发现"ETH月底波动率增30%"
写在自己的MEMORY.md里

建筑师设计监控系统时 --> **完全不知道这个信息**

---

<!-- Page 31 -->
## [DIAGRAM] Slide 3-6b

### 记忆同步数据流

```
各Agent独立工作空间          统一存储           搜索服务
+------------------+     +-----------+     +------+
| friday/          |     |           |     |      |
|   MEMORY.md      |-+   | openviking|---->| QMD  |
|   memory/*.md    | |   |   /core/  |     |      |
+------------------+ |   |           |     | 全局 |
| trading/         |-+-->| friday_   |     | 语义 |
|   MEMORY.md      | |   | MEMORY.md |     | 搜索 |
+------------------+ |   | trading_  |     |      |
| architect/       |-+   | MEMORY.md |     |      |
|   MEMORY.md      |     |           |     |      |
+------------------+     +-----------+     +------+
   各自积累经验          文件同步+索引更新     全局可搜索
```

---

<!-- Page 32 -->
## [QUESTION] Slide 3-6c

> 对应讲课稿 [互动]：为什么不做实时同步？

# 为什么不实时同步？

Agent每写一条记忆就立即同步？

**成本太高。**

桑丘交易时每秒产生日志
每次触发文件复制 + QMD索引重建

> 每天一次批量同步 = 效率与新鲜度的平衡

---

<!-- Page 33 -->
## [CONCEPT] Slide 3-6d

### 同步设计要点

1. **增量同步** -- 只同步修改时间更新的文件
2. **定时执行** -- 每天运行一次
3. **最后一步：qmd update** -- 更新向量索引

> 文件同步了但索引没更新 = 新内容对搜索不可见

---

<!-- Page 34 -->
## [SUMMARY] Slide 3-7a

### 第3课核心总结

1. 单Agent瓶颈的本质 = **违反单一职责原则**
2. 三层架构：主Agent + 专业Agent集群 + 共享基础设施
3. 通信用**Pub/Sub + 持久化**双通道保证不丢消息
4. 任务分配：**技能匹配优先于负载均衡**（阈值>0.5）
5. 记忆同步是多Agent系统的"隐藏英雄"

---

<!-- Page 35 -->
## [TRANSITION] Slide 3-next

# 下节课预告

三大基础设施已完成：
记忆系统（第1课）+ 模型路由（第2课）+ 多Agent架构（第3课）

接下来进入应用层：

**第4课：让Agent写代码 -- 结构化代码生成工作流**

> 一句需求 --> 6步工作流 --> 7个完整代码文件
> 难度回到"中级"
