# 第2课课件：一个模型不够用 -- 多模型调度与智能路由

> 课件脚本 | 对应讲义：lesson-02-model-routing.md | 对应讲课稿：lesson-02-script.md
> 总页数：31页 | 建议时长：3小时

---

<!-- Page 1 -->
## [COVER] Slide 2-0a

# AI Agent系统工程实战

### 第2课：一个模型不够用
### -- 多模型调度与智能路由

对应原文：第3章 | 难度：中级 | 时长：3小时

---

<!-- Page 2 -->
## [TOC] Slide 2-0b

### 今天的旅程

| 模块 | 主题 | 时间 |
|------|------|------|
| 2.1 | LLM能力矩阵 | 0:00-0:35 |
| 2.2 | 路由系统设计 | 0:35-0:50 |
| 2.3 | 动态模型选择 | 0:50-1:15 |
| -- | 休息 | 1:15-1:25 |
| -- | 练习1：实现ModelRouter | 1:25-1:55 |
| 2.4 | 性能监控体系 | 1:55-2:25 |
| 2.5 | 成本优化实战 | 2:10-2:25 |
| -- | 练习2 + 总结 | 2:25-3:00 |

---

<!-- Page 3 -->
## [DIAGRAM] Slide 2-1a

### 模块 2.1 -- 同一问题，四个模型的表现

```
问题："用Python实现一个LRU缓存"

GPT-4o-mini   | 0.8秒  | 代码正确，无注释      | $0.0002
Claude Sonnet | 2.5秒  | 高质量，类型标注完整   | $0.015
Kimi K2.5     | 3.0秒  | 不错，中文注释好       | $0.010
Gemini Pro    | 4.0秒  | 全面，含场景分析       | $0.020
```

> 没有"最好的模型"，只有"最适合当前任务的模型"

---

<!-- Page 4 -->
## [QUESTION] Slide 2-1b

> 对应讲课稿 [互动]：如果你是架构师，你会选哪个模型作为唯一模型？

# 你会选哪个模型处理所有请求？

**正确答案：你不应该只选一个。**

"你好" 也用Claude --> 花$0.015等2.5秒

复杂架构设计用mini --> 质量不够

---

<!-- Page 5 -->
## [TABLE] Slide 2-1c

### LLM能力矩阵

| 维度 | Kimi K2.5 | GPT-4o-mini | Claude Sonnet | Gemini Pro |
|------|-----------|-------------|---------------|------------|
| 定位 | 全能主力 | 飞毛腿 | 代码大师 | 图书馆员 |
| 上下文 | 128K | 128K | 200K | 2M |
| 强项 | 推理/中文 | 速度/低价 | 代码/调试 | 长文档 |
| 延迟 | 2-4秒 | 0.5-1秒 | 2-3秒 | 3-5秒 |

---

<!-- Page 6 -->
## [DIAGRAM] Slide 2-1d

### 成本计算公式

```
单次调用成本 =
    (input_tokens / 1000) x input_price
  + (output_tokens / 1000) x output_price

示例（1000输入 + 500输出 tokens）：
  GPT-4o     = $0.0025 + $0.005  = $0.0075
  GPT-4o-mini = $0.00015 + $0.0003 = $0.00045

价格差距：约 17 倍
```

---

<!-- Page 7 -->
## [QUESTION] Slide 2-1e

> 对应讲课稿 [互动]：80%简单请求从GPT-4切到mini，一个月省多少？

# 算一笔账

每天1000个请求，80%是简单问答

把这80%从GPT-4切到mini模型

**一个月能省多少钱？**

---

<!-- Page 8 -->
## [DIAGRAM] Slide 2-1f

### 模型选择的"不可能三角"

```
        质量 (Quality)
           /\
          /  \
         /    \         不可能三角
        / 理想  \        （需要取舍）
       /  区域   \
      /____________\
   成本 (Cost) --- 速度 (Speed)
```

- 高质量 + 高速度 = 高成本
- 高质量 + 低成本 = 低速度
- 高速度 + 低成本 = 质量折中

> 智能路由 = 为每个任务找到最优平衡点

---

<!-- Page 9 -->
## [CONCEPT] Slide 2-2a

### 模块 2.2 -- 路由系统设计

# 路由核心 = YAML配置文件

改配置就改行为，不用改代码

两部分：**模型定义** + **路由规则**

---

<!-- Page 10 -->
## [CODE] Slide 2-2b

### 路由配置YAML -- 模型定义

```yaml
models:
  primary:
    id: "moonshot/kimi-k2.5"
    context_window: 128000
    strengths: [reasoning, coding, chinese]   # <-- 重点

  fast:
    id: "openai/gpt-4o-mini"
    context_window: 128000
    strengths: [speed, cost_efficient]        # <-- 重点

  coding:
    id: "anthropic/claude-3-5-sonnet-20241022"
    context_window: 200000
    strengths: [code_generation, debugging]
```

---

<!-- Page 11 -->
## [CODE] Slide 2-2c

### 路由配置YAML -- 路由规则

```yaml
routing:
  - pattern: "代码|编程|debug|报错"    # <-- 重点
    model: coding
    priority: 1                        # 最高优先级

  - pattern: "总结|摘要|分析文档"
    model: long_context
    priority: 2

  - pattern: "快速|简单|是/否"
    model: fast
    priority: 3

  default: primary                     # <-- 重点
```

---

<!-- Page 12 -->
## [QUESTION] Slide 2-2d

> 对应讲课稿 [互动]：输入"帮我总结这段代码的功能"匹配到哪条规则？

# "帮我总结这段代码的功能"

匹配到哪个模型？

- A. coding（包含"代码"，priority 1）
- B. long_context（包含"总结"，priority 2）
- C. primary（兜底）

---

<!-- Page 13 -->
## [CONCEPT] Slide 2-2e

### 路由规则三原则

1. **高优先级规则更具体**
   - "Python.*报错|traceback" (priority 1)
   - "代码|编程" (priority 2)

2. **兜底规则不可省略**
   - `default: primary` 确保所有请求有处理

3. **规则数量要克制**
   - 生产配置：3条规则 + 1个默认值

---

<!-- Page 14 -->
## [CONCEPT] Slide 2-3a

### 模块 2.3 -- 动态模型选择

# select_model() 三层递进逻辑

**第1层：** 正则规则匹配（人工经验）

**第2层：** 上下文长度（>100K --> Gemini）

**第3层：** 复杂度估计（算法判断）

---

<!-- Page 15 -->
## [DIAGRAM] Slide 2-3b

### 决策流程 -- "帮我debug这段代码"

```
输入：query="帮我debug这段代码", context=5000

[第1层] 正则匹配
  "代码|编程|debug|报错" --> 命中 "debug"
  model = "coding"

[容量检查] coding上下文200K
  5000 < 200K x 0.8 = 160K --> 通过

--> 返回 "coding" (Claude 3.5 Sonnet)
```

---

<!-- Page 16 -->
## [DIAGRAM] Slide 2-3c

### 决策流程 -- "你好"

```
输入：query="你好", context=100

[第1层] 正则匹配 --> 无命中

[第2层] 上下文检查
  100 < 100K --> 不触发

[第3层] 复杂度估计
  length: 2/1000 = 0.002
  code_blocks: 0
  technical_terms: 0
  reasoning: 0
  总分: 0.002 < 0.3

--> 返回 "fast" (GPT-4o-mini)
```

---

<!-- Page 17 -->
## [CODE] Slide 2-3d

### _estimate_complexity() 四因子评分

```python
def _estimate_complexity(self, query: str) -> float:
    factors = {
        'length': min(len(query) / 1000, 1.0),
        'code_blocks': len(
            re.findall(r'```', query)) * 0.2,    # <-- 重点
        'technical_terms': len(re.findall(
            r'\b(API|架构|算法|模型|数据库)\b', query
        )) * 0.1,
        'reasoning_indicators': len(re.findall(
            r'\b(为什么|如何|分析|比较|优化)\b', query
        )) * 0.15,                                # <-- 重点
    }
    return min(sum(factors.values()), 1.0)
```

---

<!-- Page 18 -->
## [QUESTION] Slide 2-3e

> 对应讲课稿 [互动]："为什么数据库的API响应变慢了？"复杂度是多少？

# 计算复杂度

"为什么数据库的API响应变慢了？"

- length = 16/1000 = 0.016
- code_blocks = 0
- technical_terms = "数据库" + "API" = 0.2
- reasoning = "为什么" = 0.15

**总分 = 0.366（中等复杂度）**

---

<!-- Page 19 -->
## [CONCEPT] Slide 2-3f

### _check_capacity() -- 为什么留20%余量

# 容量检查：context < window x 0.8

三个原因：

1. 输入填满 --> 没空间生成输出
2. 系统提示词也占空间
3. Token计数不精确，留安全余量

> 磁盘用到90%就该报警，不是等到100%

---

<!-- Page 20 -->
## [EXERCISE] Slide 2-3g

### 练习1：实现完整的ModelRouter类

- **时间：** 30分钟
- **实现：** select_model() / _estimate_complexity() / _check_capacity()
- **测试：** 5个场景全部通过
- **文件：** exercise_03_model_router.py
- **参考：** 讲义模块2.3 ModelRouter完整代码

---

<!-- Page 21 -->
## [CONCEPT] Slide 2-4a

### 模块 2.4 -- 性能监控体系

# 没有监控就没有优化

路由上线后必须回答：

- 每个模型被调用了多少次？
- 成功率如何？延迟表现？
- 成本分布在预算内吗？

---

<!-- Page 22 -->
## [TABLE] Slide 2-4b

### 五个核心监控指标

| 指标 | 含义 | 健康阈值 |
|------|------|---------|
| total_calls | 总调用次数 | 关注分布是否合理 |
| success_rate | 成功率 | >= 95% |
| avg_latency | 平均延迟 | 依模型而异 |
| **p95_latency** | P95延迟 | < 10,000ms |
| total_cost | 总成本 | 月预算内 |

---

<!-- Page 23 -->
## [QUESTION] Slide 2-4c

> 对应讲课稿 [互动]：为什么P95比平均延迟更有参考价值？

# P95 vs 平均延迟

100个请求：99个1秒，1个30秒

- 平均延迟 = 1.29秒（看起来还行）
- P95延迟 = 1秒（95%用户真实体验）

**P95排除极端异常，反映真实用户体验**

---

<!-- Page 24 -->
## [CODE] Slide 2-4d

### P95延迟计算

```python
def get_model_stats(self, model_id: str, days: int = 7):
    entries = self._get_recent_entries(model_id, days)

    latencies = [e['latency_ms'] for e in entries]

    return {
        'total_calls': len(entries),
        'success_rate': sum(successes) / len(successes),
        'avg_latency_ms': sum(latencies) / len(latencies),
        'p95_latency_ms': sorted(latencies)[   # <-- 重点
            int(len(latencies) * 0.95)
        ],
        'total_cost': sum(costs),
    }
```

---

<!-- Page 25 -->
## [DIAGRAM] Slide 2-4e

### 自动推荐策略

```
遍历所有模型的最近7天数据
     |
     v
[检查成功率]
  < 95%? --> "建议检查 API 稳定性或重试逻辑"
     |
     v
[检查P95延迟]
  > 10秒? --> "考虑降级或切换模型"
     |
     v
  无异常 --> 无推荐（系统健康）
```

---

<!-- Page 26 -->
## [TABLE] Slide 2-5a

### 模块 2.5 -- 实际运行效果

| 场景 | 自动选择模型 | 延迟 | 成本 |
|------|-------------|------|------|
| "你好" | gpt-4o-mini | 800ms | $0.0001 |
| "帮我debug代码" | claude-sonnet | 2500ms | $0.015 |
| "总结100页PDF" | gemini-pro | 5000ms | $0.05 |
| "设计分布式架构" | kimi-k2.5 | 3500ms | $0.025 |

---

<!-- Page 27 -->
## [TABLE] Slide 2-5b

### 成本对比：有路由 vs 无路由

| 场景 | 路由后成本 | 全用主力 | 节省 |
|------|----------|---------|------|
| "你好" | $0.0001 | $0.005 | **98%** |
| "debug代码" | $0.015 | $0.025 | 40% |
| "总结PDF" | $0.05 | $0.10 | 50% |
| "架构设计" | $0.025 | $0.025 | 0% |

**综合效果：成本降低~60%，响应速度提升~40%**

---

<!-- Page 28 -->
## [CONCEPT] Slide 2-5c

### 成本优化四原则

1. **识别"杀鸡用牛刀"** -- 50-70%请求是简单的
2. **先粗后细** -- 3-5条规则覆盖80%场景
3. **监控驱动优化** -- 用数据说话，不凭感觉
4. **保留兜底** -- 最强模型作为默认选项

---

<!-- Page 29 -->
## [EXERCISE] Slide 2-5d

### 练习2：为混合场景设计路由规则

- **时间：** 25分钟（小组讨论）
- **场景：** 客服300次/天 + 内容创作50次/天 + 数据分析30次/天
- **约束：** 月预算 $500
- **产出：** YAML配置 + 成本估算
- **文件：** exercise_04_routing_design.yml

---

<!-- Page 30 -->
## [SUMMARY] Slide 2-6a

### 第2课核心总结

1. **没有最好的模型** -- 只有最适合当前任务的模型
2. **简单规则最有效** -- 3条正则 + 1个默认值 = 成本降低60%
3. **复杂度估计不需要AI** -- 启发式多因子评分够用
4. **监控是优化的基础** -- 没有P95数据就没有优化方向
5. **容量检查是安全网** -- 留20%余量防止溢出

---

<!-- Page 31 -->
## [TRANSITION] Slide 2-next

# 下节课预告

模型路由解决了"用什么模型"

但一个Agent同时做交易、写代码、写文章...
上下文窗口被挤占，提示词互相干扰

**第3课：多Agent架构设计与实现**

> 难度升级：中级 --> 中高级
> 建议预习Redis Pub/Sub基础
