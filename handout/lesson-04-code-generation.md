# 第4课：让Agent写代码 -- 结构化代码生成工作流

> **对应原文：** 第6-7章（代码生成工作流 / 写作系统的演进）
> **课程难度：** 中级
> **课时：** 3小时

---

## 预习建议（30分钟）

请在课前完成以下预习，为课堂学习做好准备：

1. **阅读材料（15分钟）：** 阅读原文第6章"代码生成工作流"全文，重点关注Skill系统的目录结构和SKILL.md的内容规范。
2. **动手准备（10分钟）：** 确保本地Python环境已安装以下依赖：
   ```bash
   pip install fastapi uvicorn sqlalchemy pydantic python-jose passlib bcrypt pytest httpx
   ```
3. **思考问题（5分钟）：** 你有没有直接让ChatGPT/Claude"帮我写一个XXX系统"的经历？生成的代码质量如何？你觉得问题出在哪里？

---

## 本课知识地图

```
第4课：结构化代码生成工作流
│
├── 模块4.1 无约束代码生成的问题
│   └── 缺乏结构 → 质量不稳定 → 难以维护 → 无法复现
│
├── 模块4.2 Skill系统架构
│   └── 目录结构 → SKILL.md六要素 → 模板机制
│
├── 模块4.3 代码生成工作流详解
│   └── 意图分析 → 技能选择 → 架构设计 → 代码生成 → 自动验证 → 迭代优化
│
├── 模块4.4 完整案例 -- FastAPI用户管理API
│   └── 需求分析 → 7个文件的完整生成过程
│
├── 模块4.5 测试驱动生成
│   └── pytest fixture → TestClient → 数据库覆盖 → 依赖注入mock
│
└── 模块4.6 写作Skill系统
    └── 技术博客写作规范 → 五阶段写作流程
```

---

## 模块4.1：无约束代码生成的问题

### 学习目标

完成本模块后，你应能够：

1. 列举"直接让AI写代码"存在的四个核心问题，并用具体场景说明每个问题
2. 解释为什么"约束"反而能提升AI代码生成的质量和一致性

### 正文

#### 最初的代码生成方式

回顾原文第6章开头所描述的场景：

```
用户：帮我写一个Python函数，计算斐波那契数列
AI：好的，这是代码...
```

对于简单任务，这种方式没有问题。但当需求复杂度上升时，问题就暴露了。

#### 四个核心问题

**问题一：缺乏结构**

当你说"帮我写一个用户管理系统"，AI可能把所有代码写在一个文件里，也可能拆成10个文件。不同次生成的结果，结构可能完全不同。这就像让10个人各自独立盖房子，你无法预期任何一栋的户型。

**问题二：质量不稳定**

同一个需求，今天生成的代码可能考虑了异常处理和类型注解，明天生成的就没有。AI的输出受上下文、随机性等多因素影响，没有一套标准来保证最低质量线。

**问题三：难以维护**

AI生成的代码没有统一的命名规范、注释规范和测试覆盖要求。三个月后你回来看这段代码，可能比看别人的代码还费劲。

**问题四：无法复现**

"上次你帮我生成那段代码效果很好，再来一次" -- 你几乎不可能得到相同质量的输出，因为没有记录"上次是怎么做的"。

#### 核心洞察："约束即自由"

这个发现促使OpenClaw团队开发了Skill系统。核心理念是：**给AI施加明确的结构化约束，反而能释放它的生产力**。这就像软件工程中的设计模式 -- 表面上是限制，实际上是最佳实践的沉淀。

> **[知识补给站] Prompt Engineering在代码生成中的核心原则**
>
> 好的代码生成Prompt需要三个要素：
> - **系统提示词（System Prompt）：** 定义AI的角色和行为规范，如"你是一个严格遵循PEP 8的Python开发者"
> - **Few-shot示例：** 给出1-2个"输入-输出"的完整示例，让AI理解期望的代码风格
> - **输出格式约束：** 明确要求输出的结构，如"每个文件必须包含：文件头注释、类型注解、docstring"
>
> 这三个要素正是Skill系统试图系统化解决的问题。

### 课后自测

1. **以下哪项不是无约束代码生成的典型问题？**
   - A. 生成的代码结构不一致
   - B. AI无法理解编程语言语法
   - C. 相同需求多次生成的质量差异大
   - D. 缺少统一的测试覆盖要求

   **答案：** B。现代LLM对主流编程语言的语法理解能力很强，语法错误已经很少见。核心问题在于"软"质量（结构、规范、一致性），而非"硬"语法。

2. **"约束即自由"这个理念在代码生成中的具体含义是什么？请用一句话解释。**

   **答案：** 给AI施加明确的结构化约束（如文件组织规范、输出格式要求、测试覆盖标准），使其输出质量更稳定、更可预期，最终提升而非限制了生产效率。

---

## 模块4.2：Skill系统架构

### 学习目标

完成本模块后，你应能够：

1. 画出Skill系统的目录结构，并解释每个组成部分的作用
2. 编写一个包含六要素的SKILL.md文件
3. 解释模板机制如何保证代码生成的一致性

### 正文

#### Skill的目录结构

Skill系统的核心设计是：**将代码生成的最佳实践封装成可复用的"技能包"**。每个Skill是一个独立的目录，包含定义文件、模板和辅助脚本。

```yaml
# Skill系统的目录结构
skills/
├── coding-agent/              # 通用编码技能
│   ├── SKILL.md               # 技能定义和使用指南（核心文件）
│   ├── templates/             # 代码模板（提供结构骨架）
│   └── scripts/               # 辅助脚本（自动化验证等）
├── test-driven-development/   # 测试驱动开发技能
│   ├── SKILL.md
│   └── examples/              # 示例项目（参考实现）
└── systematic-debugging/      # 系统化调试技能
    ├── SKILL.md
    └── patterns/              # 调试模式库
```

每个Skill就像一本"操作手册"，告诉AI（和人类开发者）：面对某类任务时，应该按什么步骤、什么标准来执行。

#### SKILL.md的六要素

SKILL.md是整个Skill系统的灵魂。它必须包含以下六个要素：

```markdown
# coding-agent SKILL.md

## 适用场景
# 要素1：明确"什么时候用这个Skill"
- 构建新功能或应用
- 审查PR
- 重构大型代码库
- 需要迭代探索的编码任务

## 输入要求
# 要素2：定义"需要提供什么信息"
- 功能需求描述（必须）
- 技术栈限制（可选）
- 性能要求（可选）
- 现有代码上下文（如有）

## 输出格式
# 要素3：规定"输出长什么样"
每个文件必须包含：
- 文件头注释（用途、作者、日期）
- 类型注解
- 文档字符串
- 关键逻辑的注释

## 工作流程
# 要素4：规定"按什么步骤执行"
1. **分析需求** - 理解用户意图，澄清模糊点
2. **设计架构** - 确定模块划分和接口
3. **编写测试** - 先写测试，定义期望行为
4. **实现代码** - 编写满足测试的代码
5. **验证运行** - 执行测试，确保通过
6. **代码审查** - 检查质量、性能、安全性

## 示例
# 要素5：给出"做得好是什么样的"
（见模块4.4的完整案例）

## 常见陷阱
# 要素6：提醒"容易犯什么错"
- 不要跳过测试直接写实现
- 不要把所有逻辑放在一个文件中
- 不要忽略错误处理和边界条件
```

#### 六要素的设计逻辑

这六个要素的排列不是随意的，它们构成了一个完整的"认知闭环"：

| 要素 | 回答的问题 | 类比 |
|------|-----------|------|
| 适用场景 | 什么时候用？ | 药品说明书的"适应症" |
| 输入要求 | 需要什么原料？ | 菜谱的"食材清单" |
| 输出格式 | 产出长什么样？ | 合同的"交付标准" |
| 工作流程 | 按什么步骤做？ | 施工的"工序流程" |
| 示例 | 做好是什么样？ | 样板间 |
| 常见陷阱 | 容易错在哪里？ | 前人踩过的坑 |

> **[知识补给站] YAML格式快速参考**
>
> Skill系统的配置大量使用YAML格式。以下是YAML的核心语法要点：
>
> ```yaml
> # 基本键值对
> name: "coding-agent"
> version: 1.0
>
> # 列表（两种写法）
> skills:
>   - coding
>   - testing
>   - debugging
> # 或者：skills: [coding, testing, debugging]
>
> # 嵌套结构
> output:
>   format: markdown
>   sections:
>     - title
>     - content
>
> # 多行字符串
> description: |
>   这是一段多行描述，
>   每行会保留换行符。
> ```
>
> 核心规则：**用缩进表示层级**（必须用空格，不能用Tab），**冒号后必须有空格**。

### 课后自测

1. **SKILL.md的六要素中，哪个要素对保证输出质量的一致性贡献最大？为什么？**

   **答案：** "输出格式"要素贡献最大。它直接定义了"什么是合格的输出"，相当于设定了质量基线。无论AI的创造性如何发挥，只要输出满足格式要求（文件头注释、类型注解、docstring、关键注释），最低质量就有保障。

2. **如果你要为"数据库迁移"任务设计一个Skill，"常见陷阱"部分应该包含哪些内容？列举至少3项。**

   **答案：** 参考答案包括：(1) 忘记备份数据就执行迁移；(2) 没有编写回滚脚本（down migration）；(3) 在生产环境直接执行未经测试的迁移；(4) 大表增加列时没有考虑锁表问题；(5) 忽略外键约束导致数据不一致。

---

## 模块4.3：代码生成工作流详解

### 学习目标

完成本模块后，你应能够：

1. 画出代码生成六步工作流的完整流程图，标注每一步的输入、输出和判断标准
2. 解释每一步可能出现的异常情况及其处理方式
3. 说明为什么"自动验证"步骤是不可省略的

### 正文

#### 六步工作流总览

以下是从"用户请求"到"可运行代码"的完整工作流：

```
用户请求
    │
    ▼
┌──────────────┐
│ Step 1       │ 输入：用户的自然语言描述
│ 意图分析     │ 输出：任务类型、复杂度评级、技术栈
│              │ 判断：需求是否明确？不明确则追问
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Step 2       │ 输入：任务类型和复杂度
│ 技能选择     │ 输出：选中的Skill名称和配置
│              │ 判断：是否有匹配的Skill？无则用通用Skill
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Step 3       │ 输入：需求 + Skill规范
│ 架构设计     │ 输出：模块划分、接口定义、数据流图
│              │ 判断：架构是否合理？（单一职责、低耦合）
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Step 4       │ 输入：架构设计 + Skill模板
│ 代码生成     │ 输出：完整的代码文件集
│              │ 判断：是否符合Skill的输出格式要求
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Step 5       │ 输入：生成的代码
│ 自动验证     │ 输出：验证报告（语法、类型、测试结果）
│              │ 判断：所有检查是否通过？
└──────┬───────┘
       │ 不通过则回到Step 4
       ▼
┌──────────────┐
│ Step 6       │ 输入：验证通过的代码 + 验证报告
│ 迭代优化     │ 输出：最终代码 + 说明文档
│              │ 判断：是否达到质量标准？
└──────┬───────┘
       │
       ▼
  输出代码 + 说明文档
```

#### 每一步的详细说明

**Step 1：意图分析**

这一步的核心是将模糊的用户请求转化为结构化的任务描述。

```python
# 意图分析的伪代码示例
# 输入："帮我创建一个用户管理的REST API，使用FastAPI，包含JWT认证"
# 分析结果：
intent_analysis = {
    "task_type": "new_application",       # 任务类型：新建应用
    "complexity": "medium",               # 复杂度：中等
    "tech_stack": ["FastAPI", "SQLAlchemy", "JWT"],  # 技术栈
    "requirements": [
        "用户CRUD操作",                    # 功能需求
        "JWT认证和授权",
        "数据持久化"
    ],
    "unclear_points": []                  # 没有模糊点，无需追问
}
```

**Step 2：技能选择**

根据任务类型选择最匹配的Skill。在本例中，"新建应用"任务匹配`coding-agent`技能。

**Step 3：架构设计**

这一步是质量的分水岭。好的架构设计意味着模块职责清晰、接口定义明确。原文中的FastAPI案例设计了以下模块划分：

```
项目结构：
├── main.py          # 应用入口：初始化FastAPI应用、注册路由
├── models.py        # 数据模型：SQLAlchemy ORM定义
├── schemas.py       # 接口模型：Pydantic请求/响应模型
├── auth.py          # 认证逻辑：JWT生成/验证、密码哈希
├── crud.py          # 数据操作：数据库读写封装
├── routers/
│   └── users.py     # 用户路由：REST API端点定义
└── tests/
    └── test_users.py # 测试文件：接口测试用例
```

**Step 4：代码生成**

按照Skill规范和架构设计逐文件生成代码。具体代码见模块4.4。

**Step 5：自动验证**

这是最容易被跳过、也最不应被跳过的步骤。自动验证包括三个层次：

| 验证层次 | 工具 | 检查内容 |
|---------|------|---------|
| 语法检查 | `python -m py_compile` | 代码是否有语法错误 |
| 类型检查 | `mypy`（可选） | 类型注解是否正确 |
| 测试运行 | `pytest` | 功能是否符合预期 |

**Step 6：迭代优化**

如果Step 5发现问题，回到Step 4修复代码，然后再次验证。这个循环通常1-3轮即可收敛。

#### 异常处理

每一步都可能出现异常，以下是常见情况和处理方式：

| 步骤 | 异常情况 | 处理方式 |
|------|---------|---------|
| 意图分析 | 需求模糊或矛盾 | 列出具体的澄清问题，要求用户补充 |
| 技能选择 | 没有匹配的Skill | 使用通用coding-agent Skill |
| 架构设计 | 需求超出单个服务范围 | 建议拆分为多个独立任务 |
| 代码生成 | 上下文窗口不足 | 分文件逐个生成 |
| 自动验证 | 测试失败 | 分析失败原因，回到Step 4修复 |
| 迭代优化 | 3轮仍未收敛 | 标记问题，请求人工介入 |

### 课后自测

1. **在六步工作流中，如果跳过Step 5（自动验证），最可能导致什么后果？**

   **答案：** 最可能导致生成的代码包含运行时错误或逻辑缺陷，但在交付时无法被发现。用户拿到的代码看起来"完整"，但实际运行时才暴露问题。自动验证是代码生成质量的最后一道防线。

2. **Step 3（架构设计）中"单一职责"原则在FastAPI项目中如何体现？请举例说明。**

   **答案：** models.py只负责定义数据库表结构（ORM映射），schemas.py只负责定义API的请求/响应数据格式（Pydantic模型），auth.py只负责认证逻辑（JWT生成和验证）。每个文件只关注一个职责，修改数据库结构不需要改认证逻辑，修改API格式不需要改数据库模型。

---

## 模块4.4：完整案例 -- FastAPI用户管理API

### 学习目标

完成本模块后，你应能够：

1. 追踪一个从"用户请求"到"7个可运行文件"的完整代码生成过程
2. 解释每个文件的职责和文件间的依赖关系
3. 独立实现一个类似结构的FastAPI项目

### 正文

#### 用户请求

> "帮我创建一个用户管理的REST API，使用FastAPI，包含JWT认证"

这是一个典型的中等复杂度任务。下面我们按照六步工作流，完整走一遍代码生成过程。

> **[知识补给站] FastAPI核心概念快速入门**
>
> FastAPI是一个现代Python Web框架，核心概念包括：
>
> ```python
> from fastapi import FastAPI, Depends
> from pydantic import BaseModel
>
> app = FastAPI()
>
> # 1. 路由装饰器：定义API端点
> @app.get("/users/{user_id}")    # GET请求，路径参数
> def get_user(user_id: int):     # 自动类型转换和验证
>     return {"user_id": user_id}
>
> # 2. Pydantic模型验证：自动验证请求体
> class UserCreate(BaseModel):
>     email: str
>     password: str
>
> @app.post("/users/")
> def create_user(user: UserCreate):  # 自动解析和验证JSON请求体
>     return {"email": user.email}
>
> # 3. 依赖注入Depends：复用公共逻辑
> def get_db():
>     db = SessionLocal()
>     try:
>         yield db
>     finally:
>         db.close()
>
> @app.get("/items/")
> def read_items(db: Session = Depends(get_db)):  # 自动注入数据库会话
>     return db.query(Item).all()
> ```
>
> 三个要点：**路由装饰器**绑定URL和函数，**Pydantic模型**自动验证数据，**Depends**实现依赖注入。

#### 文件1：数据模型（models.py）

```python
# models.py - 数据库模型定义
# 职责：定义数据库表结构，使用SQLAlchemy ORM
# 依赖：database模块（提供Base基类）
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"

    # 主键和索引：id是自增主键，email建立唯一索引
    # 为什么email要加unique和index？
    # unique保证不会有重复注册，index加速按邮箱查询（登录时需要）
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)

    # 密码存储：只存哈希值，永远不存明文
    # 这是安全设计的基本原则，即使数据库泄露，密码也不会暴露
    hashed_password = Column(String, nullable=False)

    # 状态字段：控制用户是否可用，软删除比硬删除更安全
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    # 时间戳：使用数据库级别的默认值（func.now()）
    # 为什么用server_default而不是default？
    # server_default在数据库层面设置，即使绕过ORM直接操作数据库也能生效
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

#### 文件2：接口模型（schemas.py）

```python
# schemas.py - Pydantic请求/响应模型
# 职责：定义API的数据契约，自动验证输入、格式化输出
# 为什么models.py和schemas.py要分开？
# models.py面向数据库（内部），schemas.py面向API（外部）
# 它们的字段可能不同：比如密码在schemas中是明文，在models中是哈希值
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    """用户基础模型 -- 所有用户模型的共同字段"""
    email: EmailStr          # EmailStr会自动验证邮箱格式
    is_active: bool = True

class UserCreate(UserBase):
    """创建用户时的请求体 -- 比基础模型多一个password字段"""
    password: str            # 注意：这里是明文密码，只在创建时接收
                             # 永远不会在响应中返回

class UserResponse(UserBase):
    """返回给客户端的用户信息 -- 不包含密码"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True  # 允许从ORM对象自动转换
        # 原来叫orm_mode = True（Pydantic v1），v2改名为from_attributes

class Token(BaseModel):
    """JWT令牌响应"""
    access_token: str
    token_type: str = "bearer"
```

#### 文件3：认证逻辑（auth.py）

```python
# auth.py - JWT认证模块
# 职责：密码哈希、JWT令牌生成与验证
# 这是整个系统的安全核心，需要特别注意以下几点：
# 1. SECRET_KEY必须从环境变量读取，绝不能硬编码
# 2. 密码哈希使用bcrypt，这是目前公认最安全的方案之一
# 3. JWT令牌要设置过期时间，避免永久有效的安全风险
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import Optional

# 生产环境必须从环境变量读取，此处为教学演示
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 密码上下文：使用bcrypt算法
# 为什么选bcrypt而不是SHA256？
# bcrypt专门为密码哈希设计，内置了"盐"（salt）和"慢哈希"机制
# "慢"是优点：让暴力破解变得极其耗时
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码：将用户输入的明文与数据库中的哈希值比较"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """生成密码哈希：每次调用都会生成不同的哈希值（因为盐不同）"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """生成JWT令牌
    data通常包含用户标识（如email）
    令牌结构：header.payload.signature
    payload中包含用户数据和过期时间
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    # jwt.encode会用SECRET_KEY对payload签名
    # 任何人都能解码payload看到内容，但只有知道SECRET_KEY才能伪造
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

#### 文件4：数据操作（crud.py）

```python
# crud.py - 数据库CRUD操作
# 职责：封装所有数据库读写逻辑
# 为什么要单独一层？而不是直接在路由中操作数据库？
# 1. 路由层只负责HTTP请求/响应，不关心数据怎么存取
# 2. CRUD层可以被多个路由复用（如admin路由和普通用户路由）
# 3. 更容易编写单元测试（只测数据逻辑，不需要启动HTTP服务）
from sqlalchemy.orm import Session
from models import User
from schemas import UserCreate
from auth import get_password_hash

def get_user_by_email(db: Session, email: str):
    """根据邮箱查询用户 -- 登录验证和重复检查都会用到"""
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate):
    """创建新用户
    注意：password -> hashed_password的转换在这里完成
    调用者传入明文密码，存储层负责哈希处理
    """
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)       # 添加到会话
    db.commit()           # 提交事务
    db.refresh(db_user)   # 刷新对象（获取数据库生成的id和时间戳）
    return db_user
```

#### 文件5：用户路由（routers/users.py）

```python
# routers/users.py - 用户相关API路由
# 职责：定义用户相关的HTTP端点
# 设计原则：路由函数应该尽量"薄" -- 只做参数解析、调用业务逻辑、返回响应
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from schemas import UserCreate, UserResponse
from crud import create_user, get_user_by_email
from auth import get_current_user  # 依赖注入：自动验证JWT并返回当前用户

router = APIRouter(prefix="/users", tags=["users"])
# prefix="/users"：所有路由自动加上/users前缀
# tags=["users"]：在API文档中分组显示

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_new_user(user: UserCreate, db: Session = Depends(get_db)):
    """创建新用户
    FastAPI自动完成：
    1. 解析请求体JSON -> UserCreate对象（包括邮箱格式验证）
    2. 注入数据库会话（Depends(get_db)）
    3. 将返回值按UserResponse格式序列化（自动过滤掉密码字段）
    """
    # 检查邮箱是否已注册 -- 这是业务规则，放在路由层处理
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    return create_user(db=db, user=user)

@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息
    Depends(get_current_user)会自动：
    1. 从请求头提取Bearer token
    2. 验证JWT签名和过期时间
    3. 从数据库查询对应用户
    4. 如果任何步骤失败，自动返回401错误
    """
    return current_user
```

#### 文件6：主应用（main.py）

```python
# main.py - 应用入口
# 职责：初始化FastAPI应用，注册所有中间件和路由
# 这个文件应该尽量简洁，只做"组装"工作
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import users, auth

# 创建数据库表（开发环境用，生产环境应使用Alembic迁移）
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="User Management API",
    description="A RESTful API for user management with JWT authentication",
    version="1.0.0"
)

# CORS中间件：控制跨域访问
# 生产环境不应该使用allow_origins=["*"]，应指定具体的前端域名
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # 开发环境允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由模块
app.include_router(auth.router)   # /auth/token 等认证相关路由
app.include_router(users.router)  # /users/ 等用户相关路由

@app.get("/health")
def health_check():
    """健康检查端点 -- 运维监控用，返回固定响应即可"""
    return {"status": "healthy"}
```

#### 文件间的依赖关系

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

关键设计原则：**依赖方向单一**。路由层依赖业务层（crud/auth），业务层依赖模型层（models/schemas），反过来的依赖绝不允许出现。

### 课后自测

1. **为什么schemas.py中的UserResponse不包含password字段？这体现了什么安全原则？**

   **答案：** UserResponse是API的响应模型，直接返回给客户端。如果包含password字段（即使是哈希值），也会增加信息泄露风险。这体现了"最小暴露原则"（Principle of Least Exposure）：只返回客户端需要的信息，不多也不少。

2. **在crud.py的create_user函数中，db.refresh(db_user)的作用是什么？如果不调用会怎样？**

   **答案：** `db.refresh(db_user)`从数据库重新加载该对象的最新数据。`db.commit()`之后，数据库生成的字段（如auto-increment的id、server_default的created_at）已经写入数据库，但Python对象中这些字段仍然是None。refresh让ORM对象与数据库同步，这样返回的UserResponse才能包含正确的id和created_at。

---

## 模块4.5：测试驱动生成

### 学习目标

完成本模块后，你应能够：

1. 解释为什么代码生成工作流中"先写测试"比"先写实现"更有效
2. 使用pytest的fixture机制管理测试数据库
3. 使用FastAPI的TestClient和依赖注入覆盖编写接口测试

### 正文

#### 为什么要"测试驱动"代码生成

在传统TDD中，测试是写给人看的需求规约。在AI代码生成中，测试还扮演了一个更重要的角色：**自动验证生成结果的正确性**。

没有测试的代码生成，就像没有检验的工厂 -- 你只能在客户投诉时才知道产品有问题。

> **[知识补给站] pytest基础用法**
>
> ```python
> # pytest的核心用法
>
> # 1. 基本断言
> def test_addition():
>     assert 1 + 1 == 2
>     assert "hello".upper() == "HELLO"
>
> # 2. fixture：测试的"准备工作"
> import pytest
>
> @pytest.fixture
> def sample_user():
>     """每个使用此fixture的测试函数都会获得一个全新的user对象"""
>     return {"email": "test@example.com", "password": "secret"}
>
> def test_user_email(sample_user):
>     assert "@" in sample_user["email"]
>
> # 3. 参数化测试：一个测试函数覆盖多组数据
> @pytest.mark.parametrize("email,valid", [
>     ("user@example.com", True),
>     ("invalid-email", False),
>     ("", False),
> ])
> def test_email_validation(email, valid):
>     result = is_valid_email(email)
>     assert result == valid
> ```
>
> 核心概念：**assert**做断言，**fixture**做准备，**parametrize**做参数化。

#### 完整的测试代码

以下是原文中FastAPI用户管理API的测试文件，逐段解读：

```python
# tests/test_users.py - 用户接口测试
# 核心策略：使用内存数据库隔离测试环境，避免污染开发/生产数据
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database import Base, get_db

# 测试数据库配置
# 为什么用sqlite:///:memory:（内存数据库）？
# 1. 速度快：不需要磁盘IO
# 2. 隔离性：每次测试都是全新的数据库
# 3. 无残留：测试结束自动清除，不会留下脏数据
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite多线程需要此配置
    poolclass=StaticPool,  # 内存数据库必须用StaticPool，否则每次连接都是新数据库
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """替换生产数据库会话为测试数据库会话
    这是FastAPI依赖注入的强大之处：
    不修改任何业务代码，只替换依赖，就能切换到测试环境
    """
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# 关键：用测试数据库覆盖生产数据库的依赖
app.dependency_overrides[get_db] = override_get_db

# TestClient模拟HTTP客户端，无需真正启动服务器
client = TestClient(app)

@pytest.fixture(scope="function")
def setup_db():
    """每个测试函数前创建表，测试后删除表
    scope="function"意味着每个测试函数都有独立的数据库状态
    这保证了测试之间的完全隔离
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_create_user(setup_db):
    """测试正常创建用户"""
    response = client.post(
        "/users/",
        json={"email": "test@example.com", "password": "testpassword"}
    )
    assert response.status_code == 201      # 验证状态码
    data = response.json()
    assert data["email"] == "test@example.com"  # 验证返回数据
    assert "id" in data                     # 验证id已生成
    # 注意：response中不应包含password字段

def test_create_duplicate_user(setup_db):
    """测试重复邮箱注册 -- 验证业务规则"""
    # 先创建一个用户
    client.post(
        "/users/",
        json={"email": "test@example.com", "password": "testpassword"}
    )

    # 尝试用相同邮箱再次注册
    response = client.post(
        "/users/",
        json={"email": "test@example.com", "password": "testpassword"}
    )
    assert response.status_code == 400              # 期望返回400错误
    assert "already registered" in response.json()["detail"]

def test_login(setup_db):
    """测试登录流程 -- 验证JWT令牌生成"""
    # 先创建用户
    client.post(
        "/users/",
        json={"email": "test@example.com", "password": "testpassword"}
    )

    # 登录获取令牌
    response = client.post(
        "/auth/token",
        data={"username": "test@example.com", "password": "testpassword"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()     # 验证返回了令牌
```

#### 测试设计的核心原则

| 原则 | 在本例中的体现 |
|------|-------------|
| 独立性 | 每个测试有独立的数据库（setup_db fixture） |
| 可重复性 | 内存数据库保证每次运行结果一致 |
| 覆盖正常路径和异常路径 | test_create_user（正常）+ test_create_duplicate_user（异常） |
| 验证行为而非实现 | 检查HTTP状态码和响应内容，不检查内部函数调用 |

### 课后自测

1. **为什么测试数据库使用StaticPool连接池？如果不用会怎样？**

   **答案：** SQLite内存数据库的特性是：每个连接看到的是独立的数据库。如果使用默认连接池，不同请求可能获得不同的连接，导致一个请求写入的数据在另一个请求中看不到。StaticPool确保所有请求共享同一个连接，从而共享同一个内存数据库。

2. **`app.dependency_overrides[get_db] = override_get_db` 这行代码体现了什么设计模式？它的好处是什么？**

   **答案：** 这体现了"依赖注入"（Dependency Injection）模式。好处是：(1) 测试不需要修改任何业务代码，只需要替换依赖即可切换环境；(2) 同一套业务代码可以在不同环境（开发、测试、生产）运行，只需要提供不同的依赖实现。

---

## 模块4.6：写作Skill系统

### 学习目标

完成本模块后，你应能够：

1. 描述写作Skill系统的输入输出规范
2. 画出五阶段写作流程并解释每个阶段的作用
3. 将代码生成Skill的设计理念迁移到非代码领域（如写作、数据分析）

### 正文

#### 从代码到写作：Skill系统的通用性

Skill系统不仅适用于代码生成。原文第7章展示了如何将同样的理念应用到写作领域。这证明了一个重要观点：**结构化的工作流适用于任何需要AI高质量输出的场景**。

#### 写作Skill的目录结构

```
skills/
├── technical-blog-writing/    # 技术博客写作
├── copywriting/               # 营销文案
├── docx/                      # Word文档生成
├── pdf/                       # PDF处理
├── pptx/                      # 演示文稿
└── xlsx/                      # 电子表格
```

#### 技术博客写作Skill的输入输出规范

```yaml
# technical-blog-writing Skill规范
# 这个YAML定义了"技术博客写作"的完整契约

input:
  # 必需参数
  - topic: string              # 文章主题
  - target_audience: "beginner" | "intermediate" | "advanced"  # 目标读者
  - word_count: number         # 目标字数

  # 可选参数
  - code_examples: boolean     # 是否包含代码示例
  - include_diagrams: boolean  # 是否包含图表

output:
  format: markdown             # 输出格式
  sections:                    # 输出结构（必须包含这7个部分）
    - title                    # 标题
    - tldr                     # 一句话摘要
    - problem                  # 问题背景
    - solution                 # 解决方案
    - results                  # 效果展示
    - trade-offs               # 利弊权衡
    - conclusion               # 结论
```

这里有一个重要的设计决策：**输出的sections是固定的**。这看似限制了灵活性，但实际上保证了每篇文章都覆盖读者最关心的内容（问题是什么、怎么解决的、效果如何、有什么取舍）。

#### 五阶段写作流程

以原文本身的写作为例，展示完整的流程：

```
阶段1：需求分析
- 主题：ClawBot到OpenClaw的演进历程
- 长度：3万字
- 风格：技术回忆录 + 架构文档
- 关键要素：代码示例、配置文件、真实数据

阶段2：大纲生成
1. 起点 -- 简单ClawBot
2. 记忆系统的演进
3. 多模型调度
4. 多Agent架构
5. 量化交易系统
6. 代码生成工作流
7. 写作系统本身

阶段3：内容生成（逐章节）
- 每个章节包含：
  - 背景/动机（"为什么做"）
  - 架构设计（"怎么设计"）
  - 核心代码（"怎么实现"）
  - 实际效果（"效果如何"）
  - 经验教训（"学到什么"）

阶段4：代码验证
- 所有代码片段语法检查
- 配置文件格式验证
- 数据一致性检查

阶段5：格式优化
- Markdown格式统一
- 代码高亮
- 表格对齐
- 层级结构优化
```

#### 代码Skill vs 写作Skill：共性与差异

| 维度 | 代码Skill | 写作Skill |
|------|----------|----------|
| 输入 | 功能需求、技术栈 | 主题、目标读者、字数 |
| 输出 | 可运行的代码文件 | 结构化的文档 |
| 验证方式 | 语法检查 + 测试运行 | 格式检查 + 内容一致性 |
| 迭代焦点 | 修复bug、优化性能 | 调整结构、润色表达 |
| 共性 | 都需要明确的输入规范、固定的输出结构、可执行的工作流程 |

#### 核心启示

Skill系统的本质是**将隐性知识显性化**：

- 一个资深开发者"知道"好代码应该什么样 -- 通过coding-agent Skill显性化
- 一个优秀作者"知道"好文章应该什么结构 -- 通过writing Skill显性化

显性化之后，AI就能按照这些标准执行，输出质量从"看运气"变成"有保障"。

### 课后自测

1. **写作Skill的输出sections为什么是固定的7个部分？如果允许AI自由决定文章结构，可能出现什么问题？**

   **答案：** 固定的7个部分保证了内容的完整性和一致性。如果允许自由结构，AI可能会：(1) 遗漏"trade-offs"部分，使文章缺乏客观性；(2) 跳过"problem"部分，让读者不知道为什么要看这篇文章；(3) 每次生成的结构都不同，读者无法形成阅读预期。固定结构就是写作领域的"设计模式"。

2. **如果你要把Skill系统的理念应用到"产品需求文档（PRD）生成"场景，输入和输出应该如何定义？**

   **答案：** 输入至少包括：product_name（产品名）、problem_statement（问题描述）、target_users（目标用户群）、priority（优先级）。输出的sections至少包括：背景与目的、目标用户画像、需求列表（功能/非功能）、用户故事、验收标准、技术约束、排期建议。

---

## 练习

### 练习06：设计并实现一个数据分析Skill

**难度：** 中级
**时间：** 30分钟
**对应教学目标：** 能设计并实现一个SKILL.md规范；理解Skill系统的通用性

#### Part A：编写SKILL.md（15分钟）

**题目描述：**

为"数据分析报告生成"场景编写一个完整的SKILL.md。该Skill的功能是：接收一个CSV数据文件，根据指定的分析维度，自动生成Markdown格式的分析报告。

**要求：**

1. 必须包含SKILL.md的六要素（适用场景、输入要求、输出格式、工作流程、示例、常见陷阱）
2. 输入参数至少包含：data_source_path（数据源路径）、analysis_dimensions（分析维度列表）、output_format（输出格式）
3. 输出格式必须定义报告的结构（至少5个section）
4. 工作流程至少定义6个步骤

**骨架代码（请补充标注 `# TODO` 的部分）：**

```markdown
# data-analysis-report SKILL.md

## 适用场景
# TODO: 列出至少3个适用场景

## 输入要求
# TODO: 定义至少5个输入参数（含类型和是否必需）

## 输出格式
format: markdown
sections:
  # TODO: 定义报告的结构（至少5个section，每个标注用途）

## 工作流程
# TODO: 定义6个步骤，每步标注输入和输出

## 示例
# TODO: 给出一个"销售数据分析"的输入输出示例

## 常见陷阱
# TODO: 列出至少3个常见陷阱
```

#### Part B：实现数据分析脚本骨架（15分钟）

**题目描述：**

基于Part A中你编写的SKILL.md，实现一个数据分析脚本的骨架代码。

**测试数据文件（sales_data.csv）：**

```csv
date,product,region,quantity,revenue
2026-01-01,Widget A,North,100,5000
2026-01-01,Widget B,South,80,6400
2026-01-02,Widget A,North,120,6000
2026-01-02,Widget B,South,90,7200
2026-01-03,Widget A,East,150,7500
2026-01-03,Widget B,West,70,5600
2026-01-04,Widget A,North,110,5500
2026-01-04,Widget B,East,95,7600
```

**骨架代码（请补充标注 `# TODO` 的部分）：**

```python
# data_analysis.py - 数据分析报告生成器
import pandas as pd
from typing import List, Dict

class DataAnalysisReport:
    def __init__(self, data_path: str, dimensions: List[str]):
        self.data_path = data_path
        self.dimensions = dimensions
        self.df = None
        self.stats = {}

    def load_data(self) -> pd.DataFrame:
        """Step 1：加载并验证数据"""
        # TODO: 读取CSV文件
        # TODO: 验证dimensions中的列是否存在
        # TODO: 返回DataFrame
        pass

    def compute_basic_stats(self) -> Dict:
        """Step 2：计算基本统计量"""
        # TODO: 计算数值列的 count, mean, std, min, max
        # TODO: 将结果存入self.stats
        pass

    def compute_dimension_analysis(self, dimension: str) -> Dict:
        """Step 3：按指定维度分组分析"""
        # TODO: 按dimension列分组
        # TODO: 计算每组的sum和mean
        # TODO: 找出最大和最小的组
        pass

    def generate_report(self) -> str:
        """Step 4：生成Markdown报告"""
        # TODO: 组装报告标题
        # TODO: 组装数据概览section
        # TODO: 组装各维度分析section
        # TODO: 组装结论section
        # TODO: 返回完整的Markdown字符串
        pass

# 使用示例
if __name__ == "__main__":
    report = DataAnalysisReport(
        data_path="sales_data.csv",
        dimensions=["product", "region"]
    )
    report.load_data()
    report.compute_basic_stats()
    markdown = report.generate_report()
    print(markdown)
```

**期望输出（报告结构示例）：**

```markdown
# 数据分析报告

## 1. 数据概览
- 数据量：8条记录
- 时间范围：2026-01-01 ~ 2026-01-04
- 数值列统计：quantity均值101.9，revenue均值6350.0

## 2. 按product分析
- Widget A：总销量480，总收入$24,000
- Widget B：总销量335，总收入$26,800
- 最高收入产品：Widget B

## 3. 按region分析
- North：总销量330，总收入$16,500
- South：总销量170，总收入$13,600
- ...

## 4. 结论
（自动生成的关键发现）
```

**评分维度：**

| 维度 | 权重 | 标准 |
|------|------|------|
| SKILL.md完整性 | 30% | 六要素齐全，每个要素内容合理 |
| 代码结构 | 25% | 方法划分清晰，职责单一 |
| 功能正确性 | 25% | 能正确读取CSV、计算统计量、生成报告 |
| 代码规范 | 20% | 类型注解、docstring、错误处理 |

---

## 本课知识总结

### 核心概念回顾

| 概念 | 一句话定义 |
|------|-----------|
| Skill系统 | 将AI代码生成的最佳实践封装为可复用的"技能包"，包含SKILL.md定义文件、模板和脚本 |
| SKILL.md | Skill的核心定义文件，包含六要素：适用场景、输入要求、输出格式、工作流程、示例、常见陷阱 |
| 六步工作流 | 意图分析 -> 技能选择 -> 架构设计 -> 代码生成 -> 自动验证 -> 迭代优化 |
| 测试驱动生成 | 先定义测试用例作为验收标准，再生成满足测试的代码，确保输出质量可验证 |
| 约束即自由 | 结构化约束不是限制AI能力，而是通过明确标准来保证输出质量的稳定性 |

### 关键结论

1. **无约束的AI代码生成存在结构不一致、质量不稳定、难以维护、无法复现四大问题**，这些问题随着项目复杂度增加而加剧。
2. **Skill系统通过六要素的标准化定义**，将代码生成从"碰运气"变成"有章法"。其中"输出格式"要素对质量一致性贡献最大。
3. **六步工作流中"自动验证"是不可省略的步骤**，它是代码质量的最后一道防线。测试驱动的生成方法让验证自动化成为可能。
4. **Skill系统具有通用性**，从代码生成到写作、数据分析等任何需要AI结构化输出的场景，都可以应用同样的设计理念。

---

## 扩展阅读

1. **FastAPI官方文档：** https://fastapi.tiangolo.com/ -- 本课案例使用的Web框架，推荐阅读Tutorial部分
2. **pytest官方文档：** https://docs.pytest.org/ -- Python最流行的测试框架，推荐阅读fixture章节
3. **Prompt Engineering Guide：** https://www.promptingguide.ai/ -- 系统学习Prompt工程的在线资源
4. **Python-jose库：** https://github.com/mpdavis/python-jose -- JWT在Python中的实现，了解令牌机制
5. **SQLAlchemy ORM教程：** https://docs.sqlalchemy.org/en/20/tutorial/ -- 数据库ORM层的深入学习
