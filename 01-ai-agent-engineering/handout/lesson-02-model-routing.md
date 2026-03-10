# 第2课：一个模型不够用 -- 多模型调度与智能路由

> **对应原文：** 第3章（多模型调度策略）
> **课程难度：** 中级
> **课时：** 3小时

---

## 预习建议（30分钟）

请在课前完成以下预习：

1. **阅读材料（15分钟）：** 阅读原文第3章"多模型调度策略"全文，重点关注模型路由的YAML配置和ModelRouter的select_model()方法。
2. **体验差异（10分钟）：** 如果你有多个LLM的API访问权限，尝试用同一个问题分别问GPT-4和一个轻量模型（如GPT-4o-mini），对比回答质量和响应速度。
3. **思考问题（5分钟）：** 如果一个AI系统要同时处理客服问答、代码调试和文档摘要三类任务，用同一个模型处理所有任务合理吗？为什么？

---

## 本课知识地图

```
第2课：多模型调度与智能路由
│
├── 模块2.1 LLM能力矩阵
│   └── 各模型特点 → 上下文窗口 → 强项 → 定价对比
│
├── 模块2.2 路由系统设计
│   └── YAML配置规范 → 正则匹配规则 → 优先级机制
│
├── 模块2.3 动态模型选择
│   └── ModelRouter实现 → 复杂度估计 → 容量检查
│
├── 模块2.4 性能监控体系
│   └── ModelPerformanceMonitor → 指标采集 → 统计分析 → 自动推荐
│
└── 模块2.5 成本优化实战
    └── 实际效果数据 → 成本计算 → ROI分析
```

---

## 模块2.1：LLM能力矩阵

### 学习目标

完成本模块后，你应能够：

1. 列举至少四种主流LLM的核心能力差异（上下文窗口、强项领域、定价、延迟）
2. 解释为什么单一模型无法满足所有AI Agent场景的需求
3. 根据给定的任务需求，初步判断应该使用哪类模型

### 正文

#### 为什么需要多个模型？

在第1课中，ClawBot只使用一个模型——GPT-4。这在功能简单时没有问题，但随着Agent承担的任务越来越多样化，单一模型的局限性开始显现：

| 问题 | 具体表现 |
|------|---------|
| **成本浪费** | 用户说"你好"，系统也调用GPT-4，花费$0.03，而一个小模型只需$0.0001 |
| **速度瓶颈** | 简单问题也要等3-5秒的GPT-4响应，用户体验差 |
| **能力错配** | GPT-4擅长推理，但代码生成不如Claude；长文档分析不如Gemini |
| **单点故障** | GPT-4 API出故障时，整个系统瘫痪 |

核心认知：**没有"最好的模型"，只有"最适合当前任务的模型"。**

#### 主流LLM能力对比

以下是OpenClaw系统实际使用的四类模型及其特点：

| 维度 | Kimi K2.5 (主力) | GPT-4o-mini (快速) | Claude 3.5 Sonnet (代码) | Gemini 1.5 Pro (长文档) |
|------|------------------|-------------------|------------------------|----------------------|
| **上下文窗口** | 128K tokens | 128K tokens | 200K tokens | 2M tokens |
| **核心强项** | 推理、中文、编程 | 速度快、成本低 | 代码生成、调试 | 超长文档分析 |
| **典型延迟** | 2-4秒 | 0.5-1秒 | 2-3秒 | 3-5秒 |
| **适用场景** | 复杂分析、架构设计 | 简单问答、分类 | 写代码、debug | 总结100页PDF |

> **[知识补给站] LLM定价与成本计算**
>
> LLM的定价通常按token计费，分为输入（input）和输出（output）两部分。
>
> **单次调用成本计算公式：**
> ```
> 成本 = (input_tokens / 1000) × input_price + (output_tokens / 1000) × output_price
> ```
>
> **示例：** 用GPT-4o处理一个1000 token输入、500 token输出的请求：
> - 成本 = (1000/1000) × $0.0025 + (500/1000) × $0.01 = $0.0025 + $0.005 = **$0.0075**
>
> 同样的请求用GPT-4o-mini：
> - 成本 = (1000/1000) × $0.00015 + (500/1000) × $0.0006 = $0.00015 + $0.0003 = **$0.00045**
>
> **价格差距：约17倍。** 如果80%的请求是简单问答，把这部分路由到mini模型，整体成本可以降低60%以上。
>
> **注意：** LLM定价变化频繁，以上数据仅供参考。实际使用时请查阅各服务商的最新定价页面。

#### 模型选择的三个关键维度

选择模型时，需要在三个维度之间权衡：

```
        质量 (Quality)
           /\
          /  \
         /    \          "不可能三角"
        /  理想  \        （实际中需要取舍）
       /   区域   \
      /____________\
   成本 (Cost) --- 速度 (Speed)
```

- **高质量 + 高速度 = 高成本**（如GPT-4 Turbo）
- **高质量 + 低成本 = 低速度**（如使用本地部署的大模型）
- **高速度 + 低成本 = 质量折中**（如GPT-4o-mini）

**智能路由的目标就是：为每个任务在这三个维度上找到最优平衡点。**

### 自测题

**1.（选择题）以下哪个场景最适合使用GPT-4o-mini而非Claude 3.5 Sonnet？**

A. 用户要求调试一段复杂的Python代码
B. 用户问"今天星期几"
C. 用户要求分析一段代码的架构设计
D. 用户要求重构一个200行的类

**答案：** B。"今天星期几"是一个极其简单的问题，不需要复杂推理或代码能力。使用mini模型既快又便宜，质量不会有明显下降。其他三个场景都涉及代码能力，更适合Claude 3.5 Sonnet。

**2.（简答题）请解释为什么"没有最好的模型，只有最适合当前任务的模型"这个观点成立。**

**参考答案：** 每个LLM都有不同的训练目标、架构和优化方向。Claude擅长代码是因为Anthropic在代码数据上做了大量优化；Gemini擅长长文档是因为其架构支持2M token的上下文窗口。如果所有任务都用最强的模型（如GPT-4），虽然质量有保障，但成本、速度和可用性都会受影响。智能路由通过任务分类，让每个任务使用"刚好够用"的模型，实现资源利用的最优化。

---

## 模块2.2：路由系统设计

### 学习目标

完成本模块后，你应能够：

1. 阅读和编写模型路由的YAML配置文件，理解每个字段的含义
2. 解释正则匹配在路由规则中的工作方式
3. 说明路由优先级机制的设计逻辑

### 正文

#### 路由配置的YAML规范

OpenClaw的模型路由配置是一个清晰的YAML文件，分为两部分：模型定义和路由规则。

```yaml
# ~/.openclaw/config/models.yml
# 模型路由配置文件
# 这个文件是整个调度系统的"大脑"——修改它就能改变系统的路由行为

# === 第一部分：模型定义 ===
# 每个模型有一个别名（key），包含模型ID、上下文窗口和能力标签
models:
  primary:
    id: "moonshot/kimi-k2.5"
    context_window: 128000
    strengths: [reasoning, coding, chinese]
    # 主力模型：综合能力强，中文优化好
    # 用于复杂分析、架构设计等需要深度推理的任务

  fast:
    id: "openai/gpt-4o-mini"
    context_window: 128000
    strengths: [speed, cost_efficient]
    # 快速模型：延迟低、成本低
    # 用于简单问答、分类、格式转换等轻量任务

  coding:
    id: "anthropic/claude-3-5-sonnet-20241022"
    context_window: 200000
    strengths: [code_generation, debugging]
    # 代码模型：代码生成和调试能力最强
    # 用于编程相关的所有任务

  long_context:
    id: "google/gemini-1.5-pro"
    context_window: 2000000
    strengths: [long_context, document_analysis]
    # 长文档模型：超大上下文窗口
    # 用于长文档分析、大型代码库理解

# === 第二部分：路由规则 ===
# 按优先级排列，先匹配到的规则先执行
# pattern字段使用正则表达式语法
routing:
  - pattern: "代码|编程|debug|报错"
    model: coding
    priority: 1
    # 优先级最高：代码相关的请求优先路由到Claude
    # 正则解读："代码"或"编程"或"debug"或"报错"

  - pattern: "总结|摘要|分析文档"
    model: long_context
    priority: 2
    # 文档分析类请求路由到Gemini

  - pattern: "快速|简单|是/否"
    model: fast
    priority: 3
    # 明确表示简单需求的请求路由到mini模型

  default: primary
  # 兜底规则：没有匹配到任何模式的请求使用主力模型
```

> **[知识补给站] 正则表达式基础回顾**
>
> 路由规则中的`pattern`字段使用Python正则表达式。以下是本课涉及的核心语法：
>
> | 语法 | 含义 | 示例 |
> |------|------|------|
> | `|` | 或（匹配任一） | `"代码|编程"` 匹配"代码"或"编程" |
> | `.` | 任意单个字符 | `"bug."` 匹配"bugs""bugx"等 |
> | `*` | 前一个字符重复0次或多次 | `"代码.*优化"` 匹配"代码优化""代码性能优化"等 |
> | `+` | 前一个字符重复1次或多次 | `"\d+"` 匹配一个或多个数字 |
> | `\b` | 单词边界 | `"\bAPI\b"` 匹配独立的"API"，不匹配"APIs" |
> | `{n,m}` | 前一个字符重复n到m次 | `.{0,30}` 匹配0到30个任意字符 |
>
> **在Python中使用：**
> ```python
> import re
> # re.search(pattern, text) 返回第一个匹配，或None
> if re.search(r"代码|编程|debug", "帮我debug这段代码"):
>     print("匹配成功")  # 会执行
> ```

#### 路由规则的设计原则

设计路由规则时需要遵循几个关键原则：

**原则1：高优先级规则应更具体**

```yaml
# 好的设计：具体规则优先
- pattern: "Python.*报错|traceback|异常"   # 非常具体的代码问题
  model: coding
  priority: 1

- pattern: "代码|编程"                      # 一般性的代码需求
  model: coding
  priority: 2
```

**原则2：兜底规则不可省略**

没有兜底规则的系统在遇到未预见的请求时会报错。`default: primary` 确保所有请求都能得到处理。

**原则3：规则数量要克制**

过多的路由规则会导致维护困难和规则冲突。OpenClaw的生产配置只有3条规则加1个默认值——简单但有效。

### 自测题

**1.（选择题）在上面的YAML配置中，如果用户输入"帮我总结这段代码的功能"，会匹配到哪个模型？**

A. coding（因为包含"代码"）
B. long_context（因为包含"总结"）
C. primary（兜底规则）
D. 无法确定，取决于运行时状态

**答案：** A。路由规则按优先级排序，`priority: 1`的规则先检查。"帮我总结这段代码的功能"包含"代码"，匹配第一条规则（pattern: "代码|编程|debug|报错"），因此路由到coding模型。虽然也包含"总结"（匹配第二条规则），但第一条优先级更高。

**2.（简答题）如果你需要添加一条路由规则，将"翻译"相关的请求路由到一个多语言模型（multilingual），请写出这条YAML规则，并说明你会设置什么优先级以及为什么。**

**参考答案：**
```yaml
- pattern: "翻译|translate|英译中|中译英"
  model: multilingual
  priority: 2
```
设置优先级为2（或3），因为翻译任务的紧急性通常低于代码调试（priority 1），但高于简单问答。同时，如果用户说"帮我翻译这段代码的注释"，我们可能希望它匹配到coding模型而非multilingual——所以翻译规则的优先级应低于代码规则。

---

## 模块2.3：动态模型选择

### 学习目标

完成本模块后，你应能够：

1. 阅读并理解ModelRouter的完整实现，解释select_model()的三层选择逻辑
2. 实现复杂度估计算法（_estimate_complexity），理解其多因子评分设计
3. 解释容量检查（_check_capacity）中"留20%余量"的工程考量

### 正文

#### ModelRouter完整实现

路由器是将YAML配置转化为运行时决策的核心组件。它的select_model()方法实现了三层递进的选择逻辑：

```python
# model_router.py
# 模型路由器：根据查询内容自动选择最合适的LLM
# 这是多模型调度系统的核心组件
import re
from typing import Optional
from dataclasses import dataclass

@dataclass
class ModelConfig:
    """模型配置数据类

    使用dataclass而非普通dict，有三个好处：
    1. 字段有明确的类型标注，IDE能提供自动补全
    2. 自动生成__init__、__repr__等方法，减少样板代码
    3. 不可变性（可选），防止运行时意外修改配置
    """
    id: str                    # 模型标识符，如 "openai/gpt-4o-mini"
    context_window: int        # 最大上下文长度（tokens）
    cost_per_1k_input: float   # 每1000输入token的成本（美元）
    cost_per_1k_output: float  # 每1000输出token的成本（美元）
    avg_latency_ms: int        # 平均响应延迟（毫秒）

class ModelRouter:
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.models = self._init_models()

    def select_model(self, query: str, context_length: int = 0) -> str:
        """根据查询内容选择最合适的模型

        三层选择逻辑（按优先级递减）：
        1. 规则匹配：查询文本匹配到预定义的正则模式
        2. 上下文长度：超长上下文自动路由到长文档模型
        3. 复杂度估计：基于查询特征评估复杂度，选择对应级别的模型

        Args:
            query: 用户的查询文本
            context_length: 当前对话的上下文长度（tokens）

        Returns:
            选中的模型别名（如 "coding", "fast", "primary"）
        """
        # === 第一层：基于规则匹配 ===
        # 最高优先级，因为规则是人工定义的，体现了领域经验
        for rule in self.config['routing']:
            if re.search(rule['pattern'], query, re.IGNORECASE):
                model_id = rule['model']
                # 匹配到规则后还要检查容量——如果目标模型处理不了这么长的上下文，
                # 就跳过这条规则，继续检查下一条
                if self._check_capacity(model_id, context_length):
                    return model_id

        # === 第二层：基于上下文长度 ===
        # 超过100K tokens的上下文，只有Gemini能处理
        # 这一层独立于规则匹配，是一个硬性约束
        if context_length > 100000:
            return 'long_context'

        # === 第三层：基于复杂度估计 ===
        # 没有匹配到规则，且上下文不长时，用算法估计查询的复杂度
        complexity = self._estimate_complexity(query)
        if complexity > 0.8:
            # 高复杂度：使用主力模型（推理能力最强）
            return 'primary'
        elif complexity < 0.3:
            # 低复杂度：使用快速模型（成本最低）
            return 'fast'

        # 兜底：中等复杂度使用默认模型
        return self.config['default']

    def _estimate_complexity(self, query: str) -> float:
        """估计查询复杂度 (0-1)

        这是一个基于启发式规则的多因子评分模型。
        没有用ML来做复杂度估计，因为：
        1. 启发式规则足够有效（覆盖80%+的场景）
        2. 不引入额外的模型调用成本
        3. 运行速度快（微秒级），不增加路由延迟

        评分因子：
        - 查询长度：长查询通常更复杂
        - 代码块数量：包含代码的查询通常需要更强的理解能力
        - 技术术语密度：技术词汇多说明问题专业度高
        - 推理指示词：需要分析、比较、优化的查询更复杂
        """
        factors = {
            # 长度因子：查询超过1000字符时达到满分1.0
            'length': min(len(query) / 1000, 1.0),
            # 代码块因子：每个代码块标记（```）贡献0.2分
            'code_blocks': len(re.findall(r'```', query)) * 0.2,
            # 技术术语因子：每个技术关键词贡献0.1分
            'technical_terms': len(re.findall(
                r'\b(API|架构|算法|模型|数据库)\b', query
            )) * 0.1,
            # 推理指示因子：每个推理类关键词贡献0.15分
            'reasoning_indicators': len(re.findall(
                r'\b(为什么|如何|分析|比较|优化)\b', query
            )) * 0.15,
        }

        # 总分上限为1.0
        return min(sum(factors.values()), 1.0)

    def _check_capacity(self, model_id: str, context_length: int) -> bool:
        """检查模型是否能处理该上下文长度

        为什么留20%余量？
        1. 模型输出也需要token空间（输入占满就无法生成回复）
        2. 系统提示词（system prompt）会占用一部分上下文
        3. 安全余量防止因token计数误差导致的溢出
        """
        model = self.models.get(model_id)
        if not model:
            return False

        # 使用80%作为有效容量上限
        return context_length < model.context_window * 0.8

    def _load_config(self, config_path: str) -> dict:
        """加载YAML配置文件"""
        import yaml
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    def _init_models(self) -> dict:
        """初始化模型配置对象"""
        models = {}
        for name, config in self.config.get('models', {}).items():
            models[name] = ModelConfig(
                id=config['id'],
                context_window=config['context_window'],
                cost_per_1k_input=config.get('cost_per_1k_input', 0.01),
                cost_per_1k_output=config.get('cost_per_1k_output', 0.03),
                avg_latency_ms=config.get('avg_latency_ms', 2000)
            )
        return models
```

> **[知识补给站] Python dataclass装饰器**
>
> `@dataclass`是Python 3.7引入的装饰器，用于简化数据类的定义。
>
> ```python
> from dataclasses import dataclass
>
> # 不用dataclass：需要手动写__init__和__repr__
> class ModelConfigOld:
>     def __init__(self, id, context_window, cost):
>         self.id = id
>         self.context_window = context_window
>         self.cost = cost
>
>     def __repr__(self):
>         return f"ModelConfigOld(id={self.id}, ...)"
>
> # 用dataclass：自动生成__init__、__repr__、__eq__等方法
> @dataclass
> class ModelConfig:
>     id: str
>     context_window: int
>     cost: float
>
> # 使用方式完全一样
> config = ModelConfig(id="gpt-4", context_window=128000, cost=0.03)
> print(config)  # ModelConfig(id='gpt-4', context_window=128000, cost=0.03)
> ```
>
> **在系统设计中的最佳实践：**
> - 配置类、消息类等"纯数据"结构用`@dataclass`
> - 需要复杂逻辑的类（如Router、Monitor）用普通class
> - 如果数据不应被修改，使用`@dataclass(frozen=True)`

#### select_model()的决策流程图

```
输入：query="帮我debug这段代码", context_length=5000
    │
    ▼
[第一层] 正则规则匹配
    │ pattern="代码|编程|debug|报错"
    │ re.search("代码|编程|debug|报错", "帮我debug这段代码") → 匹配！
    │ model_id = "coding"
    │
    ▼
[容量检查] _check_capacity("coding", 5000)
    │ coding模型上下文窗口 = 200,000
    │ 5000 < 200,000 × 0.8 = 160,000 → 通过！
    │
    ▼
返回 "coding" ← 最终选择Claude 3.5 Sonnet
```

```
输入：query="你好", context_length=100
    │
    ▼
[第一层] 正则规则匹配 → 无匹配
    │
    ▼
[第二层] 上下文长度检查
    │ 100 < 100,000 → 不触发
    │
    ▼
[第三层] 复杂度估计
    │ _estimate_complexity("你好")
    │   length: min(2/1000, 1.0) = 0.002
    │   code_blocks: 0
    │   technical_terms: 0
    │   reasoning_indicators: 0
    │   总分: 0.002 → 低于0.3
    │
    ▼
返回 "fast" ← 最终选择GPT-4o-mini
```

### 自测题

**1.（选择题）在_estimate_complexity()中，查询"为什么数据库的API响应变慢了"的复杂度分数大约是多少？**

A. 0.002（极低）
B. 0.15（偏低）
C. 0.35（中等）
D. 0.85（很高）

**答案：** C。分析：length = min(16/1000, 1.0) = 0.016；code_blocks = 0；technical_terms = "API" + "数据库" = 2 × 0.1 = 0.2；reasoning_indicators = "为什么" = 1 × 0.15 = 0.15。总分 = 0.016 + 0 + 0.2 + 0.15 = 0.366，约0.35，属于中等复杂度。

**2.（简答题）为什么_check_capacity()使用80%而不是100%作为容量上限？如果设置为100%会出什么问题？**

**参考答案：** 三个原因：(1) 输入填满上下文窗口后，模型没有空间生成输出；(2) 系统提示词（system prompt）需要占用一部分上下文空间，通常有几百到上千token；(3) token计数不是精确的——不同的tokenizer可能产生不同的计数结果，留20%余量防止因计数误差导致API调用失败。如果设为100%，最可能出现的问题是API返回"上下文超限"错误。

**3.（选择题）如果一个查询同时匹配了priority=1和priority=2的规则，系统会选择哪个？**

A. 两个都执行，取结果更好的那个
B. 选择priority=1的规则（先匹配先执行）
C. 随机选择
D. 抛出异常

**答案：** B。路由规则在配置文件中按优先级排列，代码中的for循环按顺序遍历，第一个匹配的规则就会被采用（前提是通过容量检查）。

---

## 模块2.4：性能监控体系

### 学习目标

完成本模块后，你应能够：

1. 解释模型性能监控的五个核心指标（调用次数、成功率、平均延迟、P95延迟、总成本）
2. 阅读并理解ModelPerformanceMonitor的实现，说明其数据采集和统计分析逻辑
3. 设计自动推荐策略——什么条件下应该建议切换模型

### 正文

#### 为什么需要模型性能监控？

路由系统上线后，你需要回答几个关键问题：
- 每个模型被调用了多少次？（路由规则是否合理？）
- 成功率如何？（是否有模型频繁出错？）
- 延迟表现如何？（用户体验是否达标？）
- 成本分布如何？（预算是否可控？）

性能监控系统持续收集这些数据，提供数据驱动的决策支持。

#### ModelPerformanceMonitor完整实现

```python
# model_monitor.py
# 模型性能监控器：持续跟踪每个模型的表现指标
# 这是路由优化的数据基础——没有监控就无法知道路由策略是否有效
from datetime import datetime, timedelta
from typing import Optional
import json
from collections import defaultdict

class ModelPerformanceMonitor:
    def __init__(self):
        self.metrics_file = "model_metrics.json"
        # 使用defaultdict(list)：访问不存在的key时自动创建空列表
        # 这避免了每次record_call时检查key是否存在
        self.metrics = self._load_metrics()

    def record_call(self, model_id: str, latency_ms: int,
                    input_tokens: int, output_tokens: int,
                    success: bool, task_type: str):
        """记录每次模型调用的指标

        这个方法应该在每次LLM调用完成后立即调用。
        它不做任何分析，只负责原始数据的采集和持久化。
        分析由get_model_stats()按需执行。

        Args:
            model_id: 模型别名（如 "coding", "fast"）
            latency_ms: 本次调用的响应时间（毫秒）
            input_tokens: 输入token数
            output_tokens: 输出token数
            success: 调用是否成功
            task_type: 任务类型（如 "code_debug", "qa", "summary"）
        """
        entry = {
            'timestamp': datetime.now().isoformat(),
            'latency_ms': latency_ms,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'success': success,
            'task_type': task_type,
            # 计算本次调用的成本（单位：美元）
            'cost': self._calculate_cost(model_id, input_tokens, output_tokens)
        }

        self.metrics[model_id].append(entry)
        self._save_metrics()

    def get_model_stats(self, model_id: str, days: int = 7) -> dict:
        """获取指定模型在最近N天的统计信息

        统计指标包括：
        - total_calls: 总调用次数
        - success_rate: 成功率（0-1）
        - avg_latency_ms: 平均延迟
        - p95_latency_ms: P95延迟（95%的请求在此延迟内完成）
        - total_cost: 总成本
        - avg_cost_per_call: 单次平均成本

        为什么用P95而不是最大延迟？
        最大延迟容易被个别异常值（如网络抖动）影响，
        P95更能反映"绝大多数用户"的真实体验。
        """
        entries = self._get_recent_entries(model_id, days)

        if not entries:
            return {}

        latencies = [e['latency_ms'] for e in entries]
        costs = [e['cost'] for e in entries]
        successes = [e['success'] for e in entries]

        return {
            'total_calls': len(entries),
            'success_rate': sum(successes) / len(successes),
            'avg_latency_ms': sum(latencies) / len(latencies),
            # P95计算：对延迟排序后取第95%位置的值
            'p95_latency_ms': sorted(latencies)[int(len(latencies) * 0.95)],
            'total_cost': sum(costs),
            'avg_cost_per_call': sum(costs) / len(costs)
        }

    def recommend_model_switch(self) -> Optional[str]:
        """基于性能数据自动推荐模型调整

        这是监控系统的"智能"部分：不只是展示数据，
        还主动发现问题并给出建议。

        当前检查两个维度：
        1. 成功率低于95%：可能是模型服务不稳定
        2. P95延迟超过10秒：用户体验已经不可接受

        Returns:
            推荐文本，或None（无需调整时）
        """
        recommendations = []

        for model_id in self.metrics:
            stats = self.get_model_stats(model_id, days=7)

            if not stats:
                continue

            # 成功率过低
            if stats['success_rate'] < 0.95:
                recommendations.append(
                    f"{model_id}: 成功率仅{stats['success_rate']:.1%}，建议检查"
                )

            # 延迟过高
            if stats['p95_latency_ms'] > 10000:
                recommendations.append(
                    f"{model_id}: P95延迟{stats['p95_latency_ms']}ms，考虑降级"
                )

        return "\n".join(recommendations) if recommendations else None

    def _calculate_cost(self, model_id: str, input_tokens: int,
                        output_tokens: int) -> float:
        """计算单次调用成本

        成本 = 输入成本 + 输出成本
             = (input_tokens/1000 * input_price) + (output_tokens/1000 * output_price)
        """
        # 模型定价表（每1000 tokens，单位美元）
        pricing = {
            'primary': {'input': 0.01, 'output': 0.03},
            'fast': {'input': 0.00015, 'output': 0.0006},
            'coding': {'input': 0.003, 'output': 0.015},
            'long_context': {'input': 0.00125, 'output': 0.005},
        }

        price = pricing.get(model_id, pricing['primary'])
        return (input_tokens / 1000 * price['input'] +
                output_tokens / 1000 * price['output'])

    def _load_metrics(self) -> defaultdict:
        """加载历史指标数据"""
        try:
            with open(self.metrics_file, 'r') as f:
                data = json.load(f)
                return defaultdict(list, data)
        except FileNotFoundError:
            return defaultdict(list)

    def _save_metrics(self):
        """持久化指标数据"""
        with open(self.metrics_file, 'w') as f:
            json.dump(dict(self.metrics), f, indent=2)

    def _get_recent_entries(self, model_id: str, days: int) -> list:
        """获取指定模型最近N天的调用记录"""
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        return [
            e for e in self.metrics.get(model_id, [])
            if e['timestamp'] >= cutoff
        ]
```

#### 五个核心监控指标

| 指标 | 含义 | 健康阈值 | 异常处置 |
|------|------|---------|---------|
| **total_calls** | 总调用次数 | 无绝对标准 | 某模型调用量骤降可能说明路由规则有误 |
| **success_rate** | 成功率 | >= 95% | 低于95%需检查API稳定性或重试逻辑 |
| **avg_latency_ms** | 平均延迟 | 依模型而异 | fast模型超过2秒需排查 |
| **p95_latency_ms** | P95延迟 | < 10,000ms | 超过10秒需考虑降级或切换模型 |
| **total_cost** | 总成本 | 月预算内 | 超预算时增加fast模型的使用比例 |

### 自测题

**1.（选择题）为什么推荐用P95延迟而非平均延迟来评估用户体验？**

A. P95更容易计算
B. P95排除了最慢的5%异常请求的影响，更真实地反映绝大多数用户的体验
C. 平均延迟没有任何参考价值
D. P95是行业标准，没有技术原因

**答案：** B。平均延迟容易被少数极端值拉高（比如一次网络超时导致30秒延迟），使平均值失真。P95表示95%的请求在此延迟内完成，既排除了极端异常，又涵盖了绝大多数用户的真实体验。

**2.（简答题）如果监控数据显示coding模型的成功率为92%，P95延迟为8500ms，你会给出什么建议？请说明推理过程。**

**参考答案：** 两个指标都需关注但严重程度不同。成功率92%低于95%阈值，说明约8%的代码相关请求失败，需要立即排查原因（常见原因：API限流、模型服务不稳定、输入超长）。短期措施：添加重试逻辑（retry 1-2次）。P95延迟8500ms虽然偏高但未超过10秒阈值，暂不需要紧急处理，但应持续观察趋势。如果两个指标同时恶化，建议考虑将部分代码任务降级到primary模型作为备选。

---

## 模块2.5：成本优化实战

### 学习目标

完成本模块后，你应能够：

1. 阅读并解释OpenClaw系统的实际运行效果数据
2. 计算不同路由策略下的成本差异
3. 解释"平均成本降低60%，响应速度提升40%"这一结论的来源

### 正文

#### 实际运行效果数据

以下是OpenClaw多模型路由系统上线后的真实运行数据：

| 场景 | 自动选择的模型 | 延迟 | 单次成本 | 路由依据 |
|------|--------------|------|---------|---------|
| "你好" | gpt-4o-mini | 800ms | $0.0001 | 复杂度=0.002 → fast |
| "帮我debug这段Python代码" | claude-3.5-sonnet | 2500ms | $0.015 | 规则匹配"debug" → coding |
| "总结这篇100页PDF" | gemini-1.5-pro | 5000ms | $0.05 | 规则匹配"总结" + 长上下文 → long_context |
| "设计一个分布式系统架构" | kimi-k2.5 | 3500ms | $0.025 | 复杂度=0.85 → primary |

#### 成本对比分析

**如果不使用路由，所有请求都用主力模型（kimi-k2.5）：**

| 场景 | 实际成本 | 主力模型成本 | 节省 |
|------|---------|-------------|------|
| "你好" | $0.0001 | $0.005 | 98% |
| "debug代码" | $0.015 | $0.025 | 40% |
| "总结PDF" | $0.05 | $0.10 | 50% |
| "架构设计" | $0.025 | $0.025 | 0% |

**综合效果：**

假设日常请求的分布比例为：简单问答60%、代码相关20%、文档分析10%、复杂分析10%。

- **无路由的月成本：** 假设每天100次请求
  - 60 × $0.005 + 20 × $0.025 + 10 × $0.10 + 10 × $0.025 = $2.05/天
  - 月成本 ≈ **$61.5**

- **有路由的月成本：**
  - 60 × $0.0001 + 20 × $0.015 + 10 × $0.05 + 10 × $0.025 = $1.056/天
  - 月成本 ≈ **$31.7**

- **节省：** 约48%（实际运行中由于请求分布和模型选择的精确度，节省比例可达60%）

同时，由于60%的简单请求使用了fast模型（800ms vs 3500ms），**加权平均响应速度提升约40%。**

#### 成本优化的核心原则

1. **识别"杀鸡用牛刀"的场景。** 大多数AI系统中，50-70%的请求是简单的，不需要最强的模型。
2. **先粗后细。** 先用3-5条简单规则覆盖80%的场景，再根据监控数据微调。
3. **监控驱动优化。** 不要凭感觉调整路由规则，让数据说话。
4. **保留兜底。** 永远有一个"最强模型"作为默认选项，确保不会因为路由错误导致任务失败。

### 自测题

**1.（选择题）在上述成本对比中，哪类请求通过路由获得了最大的成本节省？**

A. 代码调试（40%）
B. 简单问答（98%）
C. 文档分析（50%）
D. 架构设计（0%）

**答案：** B。简单问答占比最大（60%），且单次成本从$0.005降到$0.0001，节省98%。这是路由系统最大的价值所在——把大量低复杂度请求从昂贵模型转移到廉价模型。

**2.（简答题）如果你的月预算只有$500，需要支撑每天500次请求（其中70%是简单问答），你会如何设计路由策略来控制成本？**

**参考答案：** 月预算$500，30天约$16.7/天，需支撑500次请求。关键策略：(1) 70%的简单问答（350次）使用GPT-4o-mini，成本350 × $0.0001 = $0.035/天；(2) 剩余30%（150次）中，根据任务类型分配——代码任务用Claude（约$0.015/次），文档任务用Gemini（约$0.05/次），复杂分析用主力模型（约$0.025/次）；(3) 假设150次中代码60次、文档30次、复杂分析60次，成本 = 60×$0.015 + 30×$0.05 + 60×$0.025 = $0.9 + $1.5 + $1.5 = $3.9/天；(4) 日总成本 ≈ $3.94，月成本 ≈ $118，远在$500预算内。如果需要进一步控制成本，可以将部分代码任务降级到primary模型。

---

## 练习设计

### 练习1（编码，30分钟）：实现完整的ModelRouter类

**题目描述：**

实现一个ModelRouter类，包含`select_model()`、`_estimate_complexity()`和`_check_capacity()`三个核心方法。使用提供的YAML配置文件和5个测试查询验证路由正确性。

**配置文件（直接在代码中定义）：**

```python
# exercise_03_model_router.py
import re
from dataclasses import dataclass
from typing import Optional

# 模拟的配置数据（等效于YAML配置文件）
CONFIG = {
    'models': {
        'primary': {'id': 'kimi-k2.5', 'context_window': 128000},
        'fast': {'id': 'gpt-4o-mini', 'context_window': 128000},
        'coding': {'id': 'claude-3.5-sonnet', 'context_window': 200000},
        'long_context': {'id': 'gemini-1.5-pro', 'context_window': 2000000},
    },
    'routing': [
        {'pattern': r'代码|编程|debug|报错|bug', 'model': 'coding', 'priority': 1},
        {'pattern': r'总结|摘要|分析文档', 'model': 'long_context', 'priority': 2},
        {'pattern': r'快速|简单|是否', 'model': 'fast', 'priority': 3},
    ],
    'default': 'primary'
}

@dataclass
class ModelConfig:
    id: str
    context_window: int

class ModelRouter:
    def __init__(self, config: dict):
        self.config = config
        self.models = {
            name: ModelConfig(id=cfg['id'], context_window=cfg['context_window'])
            for name, cfg in config['models'].items()
        }

    def select_model(self, query: str, context_length: int = 0) -> str:
        """根据查询选择最合适的模型

        三层逻辑：
        1. 规则匹配（检查容量后返回）
        2. 上下文长度（>100K时选择long_context）
        3. 复杂度估计（>0.8用primary，<0.3用fast，其余用default）
        """
        # TODO 1: 实现规则匹配逻辑
        ______

        # TODO 2: 实现上下文长度检查
        ______

        # TODO 3: 实现复杂度估计逻辑
        ______

        return self.config['default']

    def _estimate_complexity(self, query: str) -> float:
        """估计查询复杂度 (0-1)

        四个评分因子：
        - length: min(len(query)/1000, 1.0)
        - code_blocks: 代码块标记数 × 0.2
        - technical_terms: 技术词汇数 × 0.1
        - reasoning_indicators: 推理词汇数 × 0.15
        """
        # TODO 4: 实现复杂度估计
        ______

    def _check_capacity(self, model_id: str, context_length: int) -> bool:
        """检查模型是否有足够的上下文容量（留20%余量）"""
        # TODO 5: 实现容量检查
        ______


# ===== 测试用例 =====
if __name__ == "__main__":
    router = ModelRouter(CONFIG)

    # 测试1：代码任务 -> coding模型
    result = router.select_model("帮我debug这段Python代码")
    assert result == "coding", f"测试1失败：期望coding，实际{result}"
    print("测试1通过：代码任务 -> coding")

    # 测试2：简单问答 -> fast模型
    result = router.select_model("你好")
    assert result == "fast", f"测试2失败：期望fast，实际{result}"
    print("测试2通过：简单问答 -> fast")

    # 测试3：文档摘要 -> long_context模型
    result = router.select_model("请总结这篇文章的要点")
    assert result == "long_context", f"测试3失败：期望long_context，实际{result}"
    print("测试3通过：文档摘要 -> long_context")

    # 测试4：复杂分析 -> primary模型
    result = router.select_model(
        "为什么这个分布式数据库的API架构在高并发场景下性能会下降？请分析可能的瓶颈并给出优化建议。"
    )
    assert result == "primary", f"测试4失败：期望primary，实际{result}"
    print("测试4通过：复杂分析 -> primary")

    # 测试5：超长上下文 -> long_context模型
    result = router.select_model("分析一下这个问题", context_length=150000)
    assert result == "long_context", f"测试5失败：期望long_context，实际{result}"
    print("测试5通过：超长上下文 -> long_context")

    print("\n所有测试通过！")
```

**期望输出：**

```
测试1通过：代码任务 -> coding
测试2通过：简单问答 -> fast
测试3通过：文档摘要 -> long_context
测试4通过：复杂分析 -> primary
测试5通过：超长上下文 -> long_context

所有测试通过！
```

**评分维度：**
- select_model()的三层逻辑正确实现（35%）
- _estimate_complexity()的四因子评分正确（25%）
- _check_capacity()正确实现20%余量逻辑（15%）
- 所有5个测试用例通过（15%）
- 代码风格和注释（10%）

---

### 练习2（设计，25分钟）：为混合场景设计模型路由规则

**题目描述：**

你的公司要开发一个AI助手，需要同时支持三类业务：
- **客服问答：** 回答用户关于产品的问题（每天约300次）
- **内容创作：** 撰写营销文案和社交媒体帖子（每天约50次）
- **数据分析：** 分析销售数据并生成报告（每天约30次）

要求在**月预算$500以内**完成路由规则设计。

**骨架配置（需要你填写）：**

```yaml
# exercise_04_routing_design.yml
# 混合场景模型路由配置

models:
  # TODO 1: 定义至少3个模型，包含id、context_window和用途说明
  ______

routing:
  # TODO 2: 设计至少3条路由规则，使用正则模式匹配
  # 要求：客服问答尽量使用低成本模型
  ______

default: ______
# TODO 3: 选择合理的默认模型

# === 成本估算 ===
# TODO 4: 基于每天的请求分布，估算月成本
# 客服问答: 300次/天 × 模型成本 = ?
# 内容创作: 50次/天 × 模型成本 = ?
# 数据分析: 30次/天 × 模型成本 = ?
# 日总成本: ?
# 月总成本: ?
# 是否在$500预算内: ?
```

**评分维度：**
- 模型选择合理，覆盖三类业务需求（25%）
- 路由规则设计合理，正则模式准确（25%）
- 成本估算完整且在预算内（25%）
- 设计说明清晰，解释了每个决策的理由（15%）
- 考虑了边界情况（如某个模型不可用时的降级策略）（10%）

---

## 本课知识总结

### 核心概念回顾

| 概念 | 定义 | 关键代码/配置 |
|------|------|-------------|
| **LLM能力矩阵** | 不同模型在上下文、速度、成本、强项上的差异对比 | YAML models配置 |
| **路由规则** | 基于正则匹配的请求-模型映射规则 | `routing: [{pattern, model, priority}]` |
| **动态模型选择** | 三层递进的选择逻辑：规则 > 上下文 > 复杂度 | `ModelRouter.select_model()` |
| **复杂度估计** | 基于多因子评分的查询复杂度评估（0-1） | `_estimate_complexity()` |
| **性能监控** | 持续跟踪模型的调用量、成功率、延迟和成本 | `ModelPerformanceMonitor` |
| **P95延迟** | 95%的请求在此延迟内完成 | `sorted(latencies)[int(len(latencies) * 0.95)]` |

### 核心结论

1. **没有"最好的模型"，只有"最适合当前任务的模型"。** 智能路由的价值在于为每个任务找到质量-成本-速度的最优平衡。
2. **简单的规则往往最有效。** OpenClaw的生产系统只用了3条正则规则加1个默认值，就实现了60%的成本降低。
3. **复杂度估计不需要AI。** 基于启发式规则的多因子评分足够有效，避免了引入额外模型调用的成本。
4. **监控是路由优化的基础。** 没有性能数据，就无法知道路由策略是否合理。
5. **容量检查是安全网。** 即使规则匹配成功，也要检查目标模型能否处理当前的上下文长度。

---

## 扩展阅读与资源推荐

1. **OpenAI定价页面：** https://openai.com/pricing —— 最新的GPT系列模型定价
2. **Anthropic API文档：** https://docs.anthropic.com/ —— Claude模型的能力说明和最佳实践
3. **LMSys Chatbot Arena：** https://chat.lmsys.org/ —— LLM模型的众包评测排行榜，直观对比各模型表现
4. **Python正则表达式文档：** https://docs.python.org/3/library/re.html —— 完整的正则语法参考
5. **《Prompt Engineering Guide》：** https://www.promptingguide.ai/ —— 不同模型的提示词优化技巧
6. **dataclasses文档：** https://docs.python.org/3/library/dataclasses.html —— Python dataclass的完整用法

---

> **下节课预告：** 多模型路由解决了"用什么模型"的问题，但当系统需要同时处理量化交易、代码开发、内容创作等多个领域的任务时，一个Agent即使有了最好的模型也会力不从心——上下文窗口被各种领域知识挤占，不同领域的提示词互相干扰。第3课将探讨**多Agent架构设计与实现**，教你如何将一个"全能但平庸"的Agent拆分成多个"专精且高效"的Agent团队。
