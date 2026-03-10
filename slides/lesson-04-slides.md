# 第4课课件：让Agent写代码 -- 结构化代码生成工作流

> 课件脚本 | 对应讲义：lesson-04-code-generation.md | 对应讲课稿：lesson-04-script.md
> 总页数：36页 | 建议时长：3小时

---

<!-- Page 1 -->
## [COVER] Slide 4-0a

# AI Agent系统工程实战

### 第4课：让Agent写代码
### -- 结构化代码生成工作流

对应原文：第6-7章 | 难度：中级 | 时长：3小时

---

<!-- Page 2 -->
## [TOC] Slide 4-0b

### 今天的旅程

| 模块 | 主题 | 时间 |
|------|------|------|
| 4.1 | 无约束代码生成的问题 | 0:00-0:15 |
| 4.2 | Skill系统架构 | 0:15-0:45 |
| 4.3 | 代码生成六步工作流 | 0:45-1:15 |
| -- | 休息 | 1:15-1:25 |
| 4.4 | 完整案例：FastAPI用户管理API | 1:25-1:55 |
| -- | 练习：编写SKILL.md + 生成代码骨架 | 1:55-2:25 |
| 4.5-4.6 | 测试生成与写作系统 | 2:25-2:45 |
| -- | 总结 | 2:45-3:00 |

---

<!-- Page 3 -->
## [QUESTION] Slide 4-1a

> 对应讲课稿 [互动]：你有没有直接让AI"帮我写一个XXX系统"的经历？结果如何？

# 你让AI写过代码吗？

"帮我写一个用户管理系统"

生成的代码你敢直接上线吗？

来，有过这种经历的举个手。

---

<!-- Page 4 -->
## [CONCEPT] Slide 4-1b

### 模块 4.1 -- 无约束代码生成的问题

# 直接让AI写代码 = 碰运气

四个核心问题：

**缺乏结构 → 质量不稳定 → 难以维护 → 无法复现**

---

<!-- Page 5 -->
## [TABLE] Slide 4-1c

### 四个核心问题

| 问题 | 具体表现 |
|------|---------|
| 缺乏结构 | 同一需求，每次生成的文件组织完全不同 |
| 质量不稳定 | 今天有异常处理，明天就没有 |
| 难以维护 | 无统一命名规范、注释规范、测试覆盖 |
| 无法复现 | "上次生成的很好，再来一次" -- 做不到 |

---

<!-- Page 6 -->
## [QUESTION] Slide 4-1d

> 对应讲课稿 [互动]：这些问题的根源是什么？是AI能力不够吗？

# 问题出在哪里？

- A. AI不懂编程语言语法
- B. AI没有统一的输出标准
- C. 需要更大的模型

**答案：B。AI语法能力很强，缺的是"约束"。**

---

<!-- Page 7 -->
## [CONCEPT] Slide 4-1e

# 核心洞察：约束即自由

给AI施加**结构化约束**

反而能**释放**它的生产力

> 就像设计模式 -- 表面是限制，实际是最佳实践的沉淀

---

<!-- Page 8 -->
## [TRANSITION] Slide 4-1to2

# 如何给AI施加"结构化约束"？

答案：**Skill系统**

将代码生成的最佳实践封装为可复用的"技能包"

---

<!-- Page 9 -->
## [CONCEPT] Slide 4-2a

### 模块 4.2 -- Skill系统架构

# 每个Skill = 一本"操作手册"

告诉AI：面对某类任务时

按**什么步骤**、**什么标准**来执行

---

<!-- Page 10 -->
## [DIAGRAM] Slide 4-2b

### Skill系统目录结构

```
skills/
├── coding-agent/              # 通用编码技能
│   ├── SKILL.md               # 技能定义（核心文件）
│   ├── templates/             # 代码模板（结构骨架）
│   └── scripts/               # 辅助脚本（自动验证）
│
├── test-driven-development/   # 测试驱动开发
│   ├── SKILL.md
│   └── examples/              # 示例项目
│
└── systematic-debugging/      # 系统化调试
    ├── SKILL.md
    └── patterns/              # 调试模式库
```

> 三个组件：SKILL.md（灵魂）+ templates（骨架）+ scripts（自动化）

---

<!-- Page 11 -->
## [CONCEPT] Slide 4-2c

# SKILL.md = Skill系统的灵魂

必须包含**六个要素**

每个要素回答一个关键问题

---

<!-- Page 12 -->
## [DIAGRAM] Slide 4-2d

### SKILL.md六要素

```
+------------------+     +------------------+
| ① 适用场景       |     | ② 输入要求       |
| "什么时候用？"   |     | "需要什么原料？" |
+--------+---------+     +--------+---------+
         |                        |
         v                        v
+------------------+     +------------------+
| ③ 输出格式       |     | ④ 工作流程       |
| "产出什么样？"   |     | "按什么步骤？"   |
+--------+---------+     +--------+---------+
         |                        |
         v                        v
+------------------+     +------------------+
| ⑤ 示例           |     | ⑥ 常见陷阱       |
| "做好是什么样？" |     | "容易错在哪？"   |
+------------------+     +------------------+
```

> 六要素构成一个完整的"认知闭环"

---

<!-- Page 13 -->
## [TABLE] Slide 4-2e

### 六要素类比

| 要素 | 回答的问题 | 类比 |
|------|-----------|------|
| 适用场景 | 什么时候用？ | 药品说明书的"适应症" |
| 输入要求 | 需要什么原料？ | 菜谱的"食材清单" |
| 输出格式 | 产出长什么样？ | 合同的"交付标准" |
| 工作流程 | 按什么步骤做？ | 施工的"工序流程" |
| 示例 | 做好是什么样？ | 样板间 |
| 常见陷阱 | 容易错在哪？ | 前人踩过的坑 |

---

<!-- Page 14 -->
## [CODE] Slide 4-2f

### SKILL.md示例 -- 适用场景 + 输入要求

```markdown
# coding-agent SKILL.md

## 适用场景
- 构建新功能或应用
- 审查PR
- 重构大型代码库                       # <-- 重点

## 输入要求
- 功能需求描述（必须）
- 技术栈限制（可选）
- 性能要求（可选）
- 现有代码上下文（如有）               # <-- 重点
```

---

<!-- Page 15 -->
## [CODE] Slide 4-2g

### SKILL.md示例 -- 输出格式 + 工作流程

```markdown
## 输出格式
每个文件必须包含：
- 文件头注释（用途、作者、日期）
- 类型注解
- 文档字符串                           # <-- 重点
- 关键逻辑的注释

## 工作流程
1. 分析需求 - 理解意图，澄清模糊点
2. 设计架构 - 模块划分和接口
3. 编写测试 - 先写测试，定义期望      # <-- 重点
4. 实现代码 - 满足测试
5. 验证运行 - 执行测试
6. 代码审查 - 质量、性能、安全
```

---

<!-- Page 16 -->
## [QUESTION] Slide 4-2h

> 对应讲课稿 [互动]：六要素中哪个对输出质量一致性贡献最大？

# 哪个要素最重要？

六要素：适用场景 / 输入要求 / **输出格式** / 工作流程 / 示例 / 常见陷阱

**答案：输出格式。**

它直接定义了"什么是合格的输出"
= 质量基线

---

<!-- Page 17 -->
## [TRANSITION] Slide 4-2to3

# 有了Skill系统

从"用户请求"到"可运行代码"

需要经过**六步工作流**

---

<!-- Page 18 -->
## [DIAGRAM] Slide 4-3a

### 模块 4.3 -- 代码生成六步工作流

```
用户请求
    |
    v
[Step 1: 意图分析] --> 任务类型、复杂度、技术栈
    |
    v
[Step 2: 技能选择] --> 匹配的Skill名称和配置
    |
    v
[Step 3: 架构设计] --> 模块划分、接口定义
    |
    v
[Step 4: 代码生成] --> 完整代码文件集
    |
    v
[Step 5: 自动验证] --> 语法/类型/测试检查
    |  不通过 --> 回到Step 4
    v
[Step 6: 迭代优化] --> 最终代码 + 说明文档
```

---

<!-- Page 19 -->
## [TABLE] Slide 4-3b

### 每一步的输入输出

| 步骤 | 输入 | 输出 | 判断标准 |
|------|------|------|---------|
| 意图分析 | 自然语言描述 | 结构化任务 | 需求是否明确？ |
| 技能选择 | 任务类型 | Skill配置 | 有无匹配Skill？ |
| 架构设计 | 需求+Skill | 模块+接口 | 单一职责？低耦合？ |
| 代码生成 | 架构+模板 | 代码文件集 | 符合输出格式？ |
| 自动验证 | 生成的代码 | 验证报告 | 全部检查通过？ |
| 迭代优化 | 代码+报告 | 最终代码 | 达到质量标准？ |

---

<!-- Page 20 -->
## [CODE] Slide 4-3c

### Step 1：意图分析示例

```python
# 输入："帮我创建一个用户管理的REST API，
#        使用FastAPI，包含JWT认证"

intent_analysis = {
    "task_type": "new_application",        # <-- 重点
    "complexity": "medium",
    "tech_stack": ["FastAPI", "SQLAlchemy", "JWT"],
    "requirements": [
        "用户CRUD操作",
        "JWT认证和授权",
        "数据持久化"
    ],
    "unclear_points": []                   # <-- 重点
}
```

---

<!-- Page 21 -->
## [DIAGRAM] Slide 4-3d

### Step 5：自动验证三层次

```
生成的代码
    |
    v
[第1层] 语法检查: python -m py_compile
    |  通过
    v
[第2层] 类型检查: mypy（可选）
    |  通过
    v
[第3层] 测试运行: pytest               <-- 最关键
    |
    +-- 通过 --> Step 6
    +-- 失败 --> 回到 Step 4（通常1-3轮收敛）
```

> 自动验证 = 代码质量的**最后一道防线**

---

<!-- Page 22 -->
## [QUESTION] Slide 4-3e

> 对应讲课稿 [互动]：如果跳过Step 5自动验证，最可能发生什么？

# 跳过自动验证会怎样？

代码看起来"完整"

实际运行时才暴露问题

**没有检验的工厂 = 客户投诉时才知道产品有问题**

---

<!-- Page 23 -->
## [TABLE] Slide 4-3f

### 异常处理速查表

| 步骤 | 异常情况 | 处理方式 |
|------|---------|---------|
| 意图分析 | 需求模糊 | 列出澄清问题，要求补充 |
| 技能选择 | 无匹配Skill | 用通用coding-agent |
| 架构设计 | 超出单服务范围 | 建议拆分为多个任务 |
| 代码生成 | 上下文窗口不足 | 分文件逐个生成 |
| 自动验证 | 测试失败 | 回到Step 4修复 |
| 迭代优化 | 3轮未收敛 | 标记问题，人工介入 |

---

<!-- Page 24 -->
## [TRANSITION] Slide 4-3to4

# 理论讲完了

接下来用一个完整案例走一遍

**"帮我创建一个用户管理的REST API，使用FastAPI，包含JWT认证"**

从需求到7个可运行文件

---

<!-- Page 25 -->
## [DIAGRAM] Slide 4-4a

### 模块 4.4 -- FastAPI案例：7个文件架构

```
项目结构：
├── main.py          # 应用入口：初始化+注册路由
├── models.py        # 数据模型：SQLAlchemy ORM
├── schemas.py       # 接口模型：Pydantic请求/响应
├── auth.py          # 认证逻辑：JWT生成/验证
├── crud.py          # 数据操作：数据库读写封装
├── routers/
│   └── users.py     # 用户路由：REST API端点
└── tests/
    └── test_users.py # 测试文件：接口测试用例
```

> 每个文件只关注一个职责 = **单一职责原则**

---

<!-- Page 26 -->
## [DIAGRAM] Slide 4-4b

### 文件依赖关系图

```
main.py ──────────────┐
    │                 │
    ├── routers/      │
    │   ├── users.py ─┼── schemas.py
    │   └── auth.py   │       │
    │                 │       │
    └── database.py ──┘   models.py
                              │
                          auth.py ── crud.py
```

关键原则：**依赖方向单一**

路由层 --> 业务层 --> 模型层

反向依赖**绝不允许**

---

<!-- Page 27 -->
## [CODE] Slide 4-4c

### models.py -- 数据模型

```python
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True,    # <-- 重点
                   nullable=False)
    hashed_password = Column(String, nullable=False)   # <-- 重点
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now())
```

> email加unique+index：防重复注册 + 加速登录查询
> 只存hashed_password：即使数据库泄露，密码也不暴露

---

<!-- Page 28 -->
## [CODE] Slide 4-4d

### schemas.py -- 接口模型

```python
class UserCreate(UserBase):
    """创建用户请求体"""
    password: str          # 明文密码，只在创建时接收  # <-- 重点

class UserResponse(UserBase):
    """返回给客户端的用户信息"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True                        # <-- 重点
```

> models.py面向数据库（内部），schemas.py面向API（外部）
> UserResponse**不包含password** = 最小暴露原则

---

<!-- Page 29 -->
## [QUESTION] Slide 4-4e

> 对应讲课稿 [互动]：为什么models.py和schemas.py要分开？不能用同一个类吗？

# 为什么要分两个模型文件？

- models.py = 面向数据库（存的是哈希密码）
- schemas.py = 面向API（接收的是明文密码）

**字段不同、用途不同、安全要求不同**

合在一起 = 耦合 = 改一处影响全局

---

<!-- Page 30 -->
## [EXERCISE] Slide 4-4f

### 练习：设计SKILL.md + 生成代码骨架

- **时间：** 30分钟（Part A 15分钟 + Part B 15分钟）
- **Part A：** 为"数据分析报告生成"编写SKILL.md（六要素齐全）
- **Part B：** 基于SKILL.md生成数据分析脚本骨架（pandas读CSV + 统计 + Markdown报告）
- **测试数据：** sales_data.csv（8条记录）
- **参考：** 讲义练习06完整描述

---

<!-- Page 31 -->
## [CONCEPT] Slide 4-5a

### 模块 4.5 -- 测试驱动生成

# 测试 = 自动验收标准

传统TDD：测试写给人看

AI代码生成：测试还用于**自动验证生成结果**

> 没有测试的代码生成 = 没有检验的工厂

---

<!-- Page 32 -->
## [CODE] Slide 4-5b

### 测试文件关键片段 -- test_users.py

```python
def test_create_user(client):
    response = client.post("/users/", json={
        "email": "test@example.com",
        "password": "secret123"
    })
    assert response.status_code == 200          # <-- 重点
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "password" not in data               # <-- 重点

def test_duplicate_email(client):
    # 第一次创建成功
    client.post("/users/", json={...})
    # 第二次应该失败
    response = client.post("/users/", json={...})
    assert response.status_code == 400          # <-- 重点
```

> 三个设计点：状态码验证 / 返回字段检查 / 边界情况覆盖

---

<!-- Page 33 -->
## [CODE] Slide 4-5c

### 写作Skill -- 五阶段工作流

```python
writing_workflow = {
    "stages": [
        "1. 大纲生成",    # 结构化标题层级
        "2. 段落展开",    # 逐段填充内容
        "3. 一致性检查",  # 术语/格式统一     # <-- 重点
        "4. 可读性优化",  # 句式/过渡/节奏
        "5. 格式输出",    # Markdown/PDF/DOCX
    ],
    "quality_gates": {
        "max_paragraph_length": 200,  # 字
        "min_heading_depth": 2,
        "required_sections": ["摘要", "正文", "参考"],
    }
}
```

> 写作Skill与代码Skill的**共性**：明确输入 + 固定结构 + 可验证输出

---

<!-- Page 34 -->
## [TABLE] Slide 4-5d

### 代码Skill vs 写作Skill

| 维度 | 代码Skill | 写作Skill |
|------|----------|----------|
| 输入 | 功能需求、技术栈 | 主题、目标读者、字数 |
| 输出 | 可运行的代码文件 | 结构化的文档 |
| 验证 | 语法检查 + 测试运行 | 格式检查 + 内容一致性 |
| 迭代 | 修复bug、优化性能 | 调整结构、润色表达 |
| **共性** | **都需要：明确的输入规范 + 固定的输出结构 + 可执行的工作流** |

> Skill系统的本质 = **将隐性知识显性化**

---

<!-- Page 35 -->
## [SUMMARY] Slide 4-6a

### 第4课核心总结

1. 无约束代码生成有四大问题：**结构/质量/维护/复现**
2. Skill系统 = 将最佳实践封装为"技能包"（SKILL.md六要素）
3. 六步工作流：**意图分析→技能选择→架构设计→代码生成→自动验证→迭代优化**
4. 自动验证是**不可省略**的步骤（质量最后防线）
5. Skill系统具有通用性：代码、写作、数据分析...

> **设计哲学：约束即自由**

---

<!-- Page 36 -->
## [TRANSITION] Slide 4-next

# 下节课预告

前4课搭建了完整的Agent基础设施：
记忆（第1课）+ 路由（第2课）+ 多Agent（第3课）+ 代码生成（第4课）

接下来进入最硬核的实战案例：

**第5课：AI驱动的量化交易系统（选修/进阶）**

> 难度升级：中级 --> 高级
> 重点：风险管理 -- 任何AI自动化系统都需要的"安全网"
