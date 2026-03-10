# 第5课（选修/进阶）：实战案例 -- AI驱动的量化交易系统

> **对应原文：** 第5章（量化交易系统的开发）
> **课程难度：** 高级
> **课时：** 3小时

---

## 预习建议（30分钟）

请在课前完成以下预习，为课堂学习做好准备：

1. **阅读材料（15分钟）：** 阅读原文第5章"量化交易系统的开发"，重点关注系统架构图和风险管理模块。不必深究每个技术指标的数学公式，课堂上会讲解。
2. **动手准备（10分钟）：** 确保本地Python环境已安装以下依赖：
   ```bash
   pip install pandas numpy scikit-learn ccxt streamlit plotly joblib
   ```
3. **思考问题（5分钟）：** 如果你要构建一个"自动执行操作"的AI系统（不限于交易，可以是自动发邮件、自动部署等），你最担心什么？在完全自动化和完全手动之间，如何找到平衡点？

---

## 本课知识地图

```
第5课：AI驱动的量化交易系统
│
├── 模块5.1 量化交易系统架构
│   └── 四层模型：数据层 → 策略层 → 执行层 → 监控层
│
├── 模块5.2 数据获取与特征工程
│   └── BinanceDataFetcher → SQLite缓存 → 12个技术指标
│
├── 模块5.3 ML策略
│   └── 标签定义 → RandomForest训练 → 置信度过滤 → 信号预测
│
├── 模块5.4 网格策略
│   └── 等比网格计算 → 挂单逻辑 → 成交回调 → 重平衡
│
├── 模块5.5 风险管理（本课核心）
│   └── RiskLimits → 六重安全检查 → 熔断机制 → 风险评分
│
└── 模块5.6 实时监控Dashboard
    └── Streamlit + Plotly → 账户/策略/风险/K线/交易记录
```

---

## 模块5.1：量化交易系统架构

### 学习目标

完成本模块后，你应能够：

1. 画出量化交易系统的四层架构图，说明每层的职责和组件
2. 解释数据层、策略层、执行层、监控层之间的数据流向
3. 将这种分层架构思想迁移到其他AI自动化系统

### 正文

#### 项目背景

2024年2月，OpenClaw团队开始开发一个生产级的量化交易系统。核心需求包括：

- 币安现货交易（ETH/USDT）
- ML驱动的交易信号
- 网格策略作为补充
- 严格的风险管理
- 实时监控和报警

这不是一个简单的"帮我写个交易脚本"任务，而是一个完整的、生产级别的系统。

> **[知识补给站] 交易领域基本术语表**
>
> | 术语 | 含义 |
> |------|------|
> | K线（Candlestick） | 一段时间内的开盘价、收盘价、最高价、最低价的图形表示 |
> | 开盘/收盘/最高/最低（OHLC） | Open/High/Low/Close，K线的四个基本价格 |
> | RSI（相对强弱指数） | 衡量价格变动速度和幅度的指标，0-100，>70超买，<30超卖 |
> | MACD（指数平滑移动平均线） | 短期均线与长期均线的差值，用于判断趋势方向和强度 |
> | 布林带（Bollinger Bands） | 基于移动平均线和标准差构建的通道，价格触碰上下轨有回归倾向 |
> | 回撤（Drawdown） | 从账户最高点到最低点的跌幅，衡量风险的关键指标 |
> | 滑点（Slippage） | 预期成交价格与实际成交价格的差异 |
> | 熔断（Circuit Breaker） | 当损失达到阈值时自动停止交易的保护机制 |

#### 四层架构

```
┌─────────────────────────────────────────────────────────┐
│                  量化交易系统架构                         │
├─────────────────────────────────────────────────────────┤
│  数据层                                                  │
│  - 币安API（价格、账户、订单）                            │
│  - 本地数据缓存（SQLite）                                │
│  - 特征存储                                              │
├─────────────────────────────────────────────────────────┤
│  策略层                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ ML策略      │  │ 网格策略    │  │ 风控模块    │     │
│  │ （随机森林）│  │ （动态挂单）│  │ （熔断机制）│     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
├─────────────────────────────────────────────────────────┤
│  执行层                                                  │
│  - 订单管理                                              │
│  - 仓位跟踪                                              │
│  - 滑点控制                                              │
├─────────────────────────────────────────────────────────┤
│  监控层                                                  │
│  - 实时盈亏                                              │
│  - 策略性能                                              │
│  - 异常报警                                              │
└─────────────────────────────────────────────────────────┘
```

#### 各层职责详解

| 层级 | 职责 | 核心组件 | 对外接口 |
|------|------|---------|---------|
| 数据层 | 获取和存储市场数据 | BinanceDataFetcher, SQLite | 向策略层提供DataFrame |
| 策略层 | 分析数据、生成交易信号 | MLTradingStrategy, GridTradingStrategy, RiskManager | 向执行层输出信号 |
| 执行层 | 执行下单、管理仓位 | OrderManager, PositionTracker | 接收信号，返回成交结果 |
| 监控层 | 实时展示、异常报警 | TradingDashboard, AlertSystem | 接收全部组件的状态数据 |

**关键设计原则：** 每层只与相邻层交互。数据层不知道策略逻辑，策略层不知道下单细节。这种分层隔离使得替换任何一层（如更换交易所、更换策略算法）都不影响其他层。

### 课后自测

1. **如果要将交易系统的策略层从"ML策略+网格策略"替换为"规则策略+动量策略"，需要修改哪些层的代码？**

   **答案：** 只需要修改策略层。数据层的数据获取和特征计算不受影响，执行层的下单逻辑不受影响，监控层只要策略层的输出接口不变就不受影响。这正是分层架构的价值。

2. **这种四层架构思想可以应用到哪些非交易场景？请举一个例子并对应四层。**

   **答案：** 例如"AI自动化内容发布系统"：数据层（爬取热点话题、素材库），策略层（选题算法、内容生成、质量检查），执行层（发布到各平台、定时排期），监控层（阅读量监控、异常内容报警）。

---

## 模块5.2：数据获取与特征工程

### 学习目标

完成本模块后，你应能够：

1. 使用ccxt库从币安获取K线数据，并实现SQLite缓存策略
2. 计算至少5种常用技术指标（MA、RSI、MACD、布林带、波动率）
3. 解释每个技术指标的含义及其在交易决策中的作用

### 正文

#### BinanceDataFetcher完整实现

```python
# data_fetcher.py - 数据获取与特征工程
# 职责：从币安获取K线数据，计算技术指标特征
# 核心设计：先查本地缓存，缓存不足时才请求交易所API
# 这样做的好处：(1)减少API调用频率 (2)加快回测速度 (3)避免触发限流
import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sqlite3

class BinanceDataFetcher:
    def __init__(self, api_key: str, api_secret: str):
        # ccxt是一个统一的加密货币交易所API库
        # 支持100+交易所，用同一套接口调用不同交易所
        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,   # 自动限流，防止被交易所封IP
            'options': {
                'defaultType': 'spot'  # 使用现货交易，不是期货
            }
        })
        self.db_path = "trading_data.db"
        self._init_db()

    def _init_db(self):
        """初始化SQLite数据库 -- 用作本地数据缓存
        为什么用SQLite而不是直接存CSV？
        1. 支持增量更新（只下载新数据）
        2. 支持按时间范围高效查询
        3. 事务保证数据一致性
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # K线数据表：存储历史价格
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS klines (
                timestamp INTEGER PRIMARY KEY,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume REAL,
                timeframe TEXT
            )
        ''')

        # 交易记录表：存储实际成交
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER,
                symbol TEXT,
                side TEXT,
                amount REAL,
                price REAL,
                order_id TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def fetch_ohlcv(self, symbol: str = 'ETH/USDT',
                    timeframe: str = '4h',
                    limit: int = 500) -> pd.DataFrame:
        """获取K线数据
        优先使用本地缓存，不足时从交易所补充
        """
        # 先检查本地缓存
        cached_data = self._get_cached_data(symbol, timeframe, limit)
        if len(cached_data) >= limit * 0.9:  # 90%数据可用就直接返回
            return cached_data

        # 从交易所获取增量数据
        since = None
        if len(cached_data) > 0:
            since = int(cached_data['timestamp'].max()) + 1

        ohlcv = self.exchange.fetch_ohlcv(
            symbol, timeframe, since=since, limit=limit
        )

        df = pd.DataFrame(
            ohlcv,
            columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
        )
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['timeframe'] = timeframe

        # 合并缓存和新数据，去重后保存
        combined = pd.concat([cached_data, df]).drop_duplicates('timestamp')
        self._save_to_db(combined, symbol, timeframe)

        return combined.tail(limit)

    def _calculate_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算技术指标特征 -- 这是特征工程的核心
        每个指标都是从价格/成交量中提取的"信号"，
        组合在一起帮助ML模型判断市场状态
        """

        # ========== 价格变动特征 ==========
        # 不同时间窗口的收益率，捕捉短中长期趋势
        df['returns_1'] = df['close'].pct_change(1)    # 1周期收益率
        df['returns_4'] = df['close'].pct_change(4)    # 4周期收益率
        df['returns_12'] = df['close'].pct_change(12)  # 12周期收益率

        # ========== 移动平均线（MA） ==========
        # MA是最基础的趋势指标：价格在MA上方 = 上升趋势
        # 计算多个周期的MA和价格与MA的偏离度
        for period in [5, 10, 20, 30, 60]:
            df[f'ma_{period}'] = df['close'].rolling(period).mean()
            # 偏离度 = (当前价 - MA) / MA，正值=高于均线，负值=低于均线
            df[f'close_ma{period}_dist'] = (
                (df['close'] - df[f'ma_{period}']) / df[f'ma_{period}']
            )

        # ========== RSI（相对强弱指数） ==========
        # RSI范围0-100：>70超买（可能回调），<30超卖（可能反弹）
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))

        # ========== MACD ==========
        # MACD = 快线(12) - 慢线(26)，信号线 = MACD的9周期均线
        # MACD柱状图 > 0 表示上升动量，< 0 表示下降动量
        exp1 = df['close'].ewm(span=12).mean()  # 12周期指数移动平均
        exp2 = df['close'].ewm(span=26).mean()  # 26周期指数移动平均
        df['macd'] = exp1 - exp2
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        df['macd_hist'] = df['macd'] - df['macd_signal']

        # ========== 布林带（Bollinger Bands） ==========
        # 上轨 = MA20 + 2*标准差，下轨 = MA20 - 2*标准差
        # bb_position表示当前价格在布林带中的位置（0=下轨，1=上轨）
        df['bb_middle'] = df['close'].rolling(20).mean()
        bb_std = df['close'].rolling(20).std()
        df['bb_upper'] = df['bb_middle'] + 2 * bb_std
        df['bb_lower'] = df['bb_middle'] - 2 * bb_std
        df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])

        # ========== 波动率 ==========
        # 年化波动率 = 日收益率标准差 * sqrt(365)
        # 高波动率 = 高风险高机会，低波动率 = 市场平静
        df['volatility'] = df['returns_1'].rolling(20).std() * np.sqrt(365)

        # ========== 成交量特征 ==========
        # 成交量比率：当前成交量 / 10周期平均成交量
        # > 1 表示放量（市场活跃），< 1 表示缩量（市场冷清）
        df['volume_ma_10'] = df['volume'].rolling(10).mean()
        df['volume_ratio_10'] = df['volume'] / df['volume_ma_10']

        # ========== K线形态特征 ==========
        # body：实体大小，反映多空博弈激烈程度
        # upper_shadow/lower_shadow：上下影线，反映价格被拒绝的位置
        df['body'] = abs(df['close'] - df['open']) / df['open']
        df['upper_shadow'] = (
            (df['high'] - df[['close', 'open']].max(axis=1)) / df['open']
        )
        df['lower_shadow'] = (
            (df[['close', 'open']].min(axis=1) - df['low']) / df['open']
        )

        return df
```

#### 技术指标汇总

| 指标 | 公式/计算方法 | 取值范围 | 交易含义 |
|------|-------------|---------|---------|
| MA（移动平均） | N周期收盘价平均值 | 与价格同量纲 | 价格在MA上方=上升趋势 |
| RSI | 100 - 100/(1+RS)，RS=平均涨幅/平均跌幅 | 0-100 | >70超买，<30超卖 |
| MACD | EMA(12) - EMA(26) | 正负均可 | 柱状图>0=上升动量 |
| 布林带 | MA20 +/- 2*STD(20) | 与价格同量纲 | 触碰上下轨有回归倾向 |
| 波动率 | STD(returns) * sqrt(365) | 0-1+ | 高=风险高机会大 |
| 成交量比 | 当前量/MA(量,10) | 0-inf | >1放量，<1缩量 |

### 课后自测

1. **为什么fetch_ohlcv方法先检查本地缓存？直接每次从API获取不行吗？**

   **答案：** 直接从API获取有三个问题：(1) 交易所有API调用频率限制，频繁调用会被封IP；(2) 历史数据不会变化，重复下载浪费带宽；(3) 回测时需要大量历史数据，每次从网络获取速度很慢。本地缓存策略实现了"新数据在线获取，旧数据离线读取"的最优方案。

2. **RSI为什么用14作为默认计算周期？**

   **答案：** 14是RSI发明者J. Welles Wilder在1978年推荐的默认值。它在灵敏度和稳定性之间取得了较好的平衡。周期太短（如7）会产生过多噪音信号，周期太长（如28）会反应迟钝。实际使用中也可以根据交易频率调整。

---

## 模块5.3：ML策略

### 学习目标

完成本模块后，你应能够：

1. 解释ML策略中"标签定义"的逻辑（上涨>1.5%=1，震荡=0，下跌>1.5%=-1）
2. 说明为什么使用TimeSeriesSplit而不是普通的train_test_split
3. 解释置信度阈值0.6的设定依据

### 正文

> **[知识补给站] RandomForestClassifier的直觉解释**
>
> 随机森林可以类比为"专家委员会投票"：
> - 200棵决策树 = 200位专家
> - 每棵树只看到部分数据和部分特征（防止死记硬背）
> - 最终预测 = 多数投票结果
> - 置信度 = 投票的一致程度（如180/200投买入，置信度=90%）
>
> 为什么"多数投票"比"一位专家"更可靠？
> - 单棵决策树容易过拟合（对训练数据记忆太好，对新数据预测差）
> - 多棵树的错误会互相抵消（除非大部分树都犯同样的错）
> - 这就是"集成学习"的核心思想

#### MLTradingStrategy完整实现

```python
# ml_strategy.py - ML交易策略
# 核心思路：用历史技术指标预测未来价格变动方向
# 将预测问题建模为三分类：上涨(1) / 震荡(0) / 下跌(-1)
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.metrics import accuracy_score, classification_report
import joblib
import pandas as pd
import numpy as np
import os
from datetime import datetime
from typing import Tuple, Optional

class MLTradingStrategy:
    def __init__(self, model_path: Optional[str] = None):
        self.model = None
        self.feature_cols = None
        self.model_path = model_path
        # 置信度阈值：只有当模型"非常确定"时才执行交易
        # 0.6意味着至少60%的决策树投了同一个票
        # 为什么不用0.5？因为0.5只比随机猜测好一点点，风险太大
        self.confidence_threshold = 0.6

        if model_path and os.path.exists(model_path):
            self.load_model(model_path)

    def prepare_data(self, df: pd.DataFrame,
                     lookahead_periods: int = 4) -> Tuple[pd.DataFrame, pd.Series]:
        """准备训练数据
        关键设计：标签定义直接决定了策略的交易风格
        """

        # 计算未来收益作为标签
        # lookahead_periods=4 表示预测未来4个周期（4h K线 = 16小时）的方向
        df['future_return'] = df['close'].shift(-lookahead_periods) / df['close'] - 1

        # 三分类标签定义：
        # 上涨(1)：未来涨幅 > 1.5%
        # 震荡(0)：涨跌幅在 [-1.5%, 1.5%] 之间
        # 下跌(-1)：未来跌幅 > 1.5%
        # 为什么用1.5%而不是0%？
        # 因为实际交易有手续费和滑点（约0.1%-0.3%），
        # 涨0.5%的交易扣完费用可能还是亏的，所以需要一个"缓冲区"
        df['label'] = 0
        df.loc[df['future_return'] > 0.015, 'label'] = 1
        df.loc[df['future_return'] < -0.015, 'label'] = -1

        # 选择特征列：排除目标列和原始价格列
        feature_cols = [col for col in df.columns if col not in
                       ['timestamp', 'open', 'high', 'low', 'close', 'volume',
                        'future_return', 'label', 'timeframe']]

        df_clean = df.dropna()

        X = df_clean[feature_cols]
        y = df_clean['label']

        self.feature_cols = feature_cols

        return X, y

    def train(self, df: pd.DataFrame,
              test_size: float = 0.2) -> dict:
        """训练模型"""

        X, y = self.prepare_data(df)

        # 时间序列分割：只用过去的数据预测未来
        # 绝对不能用随机分割（random split）！
        # 为什么？因为时间序列有先后关系，如果用未来数据训练，
        # 就等于"开卷考试"，准确率虚高但实盘必亏
        split_idx = int(len(X) * (1 - test_size))
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

        # 随机森林参数选择理由：
        self.model = RandomForestClassifier(
            n_estimators=200,      # 200棵树：足够多以稳定结果，不至于太慢
            max_depth=10,          # 最大深度10：防止过拟合（树太深会记住噪音）
            min_samples_split=20,  # 最少20个样本才分裂：避免对少量数据过度拟合
            min_samples_leaf=10,   # 叶子节点最少10个样本：保证预测的统计意义
            random_state=42,       # 固定随机种子：保证可复现
            n_jobs=-1              # 使用所有CPU核心并行训练
        )

        self.model.fit(X_train, y_train)

        # 评估
        train_pred = self.model.predict(X_train)
        test_pred = self.model.predict(X_test)

        train_acc = accuracy_score(y_train, train_pred)
        test_acc = accuracy_score(y_test, test_pred)

        # 特征重要性分析：哪些指标对预测最有用？
        importance = pd.DataFrame({
            'feature': self.feature_cols,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)

        metrics = {
            'train_accuracy': train_acc,
            'test_accuracy': test_acc,
            'feature_importance': importance.head(10).to_dict(),
            'samples_train': len(X_train),
            'samples_test': len(X_test)
        }

        return metrics

    def predict(self, current_features: pd.Series) -> dict:
        """预测当前信号"""

        if self.model is None:
            raise ValueError("Model not trained or loaded")

        X = current_features[self.feature_cols].values.reshape(1, -1)

        # 获取每个类别的概率
        proba = self.model.predict_proba(X)[0]
        prediction = self.model.predict(X)[0]

        action_map = {1: 'BUY', 0: 'HOLD', -1: 'SELL'}
        action = action_map[prediction]

        # 置信度 = 预测类别的投票比例
        confidence = proba[self.model.classes_.tolist().index(prediction)]

        return {
            'action': action,
            'confidence': confidence,
            'probabilities': {
                action_map[c]: p
                for c, p in zip(self.model.classes_, proba)
            },
            # 只有置信度达标且不是HOLD时才实际执行交易
            'should_execute': confidence >= self.confidence_threshold and action != 'HOLD'
        }

    def save_model(self, path: str):
        """保存模型到磁盘"""
        joblib.dump({
            'model': self.model,
            'feature_cols': self.feature_cols,
            'confidence_threshold': self.confidence_threshold
        }, path)

    def load_model(self, path: str):
        """从磁盘加载模型"""
        data = joblib.load(path)
        self.model = data['model']
        self.feature_cols = data['feature_cols']
        self.confidence_threshold = data.get('confidence_threshold', 0.6)
```

### 课后自测

1. **为什么时间序列数据不能使用随机分割（random split）来划分训练集和测试集？**

   **答案：** 随机分割会导致"数据泄露"（Data Leakage）：未来的数据点可能被分到训练集中，等于用未来信息预测未来。在实盘中，你只能用历史数据做决策，不可能知道明天的价格。TimeSeriesSplit保证训练集永远在测试集之前，模拟真实的时间顺序。

2. **如果模型的训练准确率是85%但测试准确率只有52%，这说明什么问题？应该如何改进？**

   **答案：** 这说明模型严重过拟合 -- 它记住了训练数据的噪音而非真正的规律。改进方法包括：(1) 减小max_depth限制树的复杂度；(2) 增大min_samples_split和min_samples_leaf防止过度分裂；(3) 减少特征数量，只保留重要性最高的特征；(4) 增加训练数据量。

---

## 模块5.4：网格策略

### 学习目标

完成本模块后，你应能够：

1. 解释网格策略的基本原理：在固定价格区间内低买高卖
2. 说明等比网格与等差网格的区别及各自的适用场景
3. 描述"买单成交后在上方挂卖单"的重平衡逻辑

### 正文

#### 网格策略的核心思想

网格策略的逻辑很简单：**在一个价格区间内画出若干条水平线（网格），在每条线上同时挂买单和卖单。价格下跌时自动买入，价格上涨时自动卖出。**

它不预测方向，而是利用"价格会在区间内波动"这个假设来赚取差价。

#### GridTradingStrategy完整实现

```python
# grid_strategy.py - 网格交易策略
# 核心思路：在价格区间内设置多个买卖网格，利用波动赚取差价
# 不依赖方向预测，只需要价格在区间内波动就能获利
from typing import List, Dict, Optional
from dataclasses import dataclass
import numpy as np

@dataclass
class GridLevel:
    """单个网格层级的状态"""
    price: float
    buy_order_id: Optional[str] = None
    sell_order_id: Optional[str] = None
    executed_buy: bool = False
    executed_sell: bool = False

class GridTradingStrategy:
    def __init__(self,
                 upper_price: float,      # 网格上界
                 lower_price: float,      # 网格下界
                 grid_count: int = 10,    # 网格数量
                 investment: float = 1000): # 总投资额
        self.upper_price = upper_price
        self.lower_price = lower_price
        self.grid_count = grid_count
        self.investment = investment

        # 计算网格价格
        self.grids = self._calculate_grids()
        self.grid_size = (upper_price - lower_price) / grid_count

        # 状态跟踪
        self.active_orders = {}
        self.total_profit = 0.0
        self.trade_count = 0

    def _calculate_grids(self) -> List[float]:
        """计算网格价格
        使用等比数列而非等差数列
        为什么？因为等比数列在低价区网格更密：
        - 等差：1000, 1100, 1200, 1300...（间距固定100）
        - 等比：1000, 1072, 1149, 1232...（间距递增）
        低价区网格更密 = 低价时买得更频繁 = 平均成本更低
        """
        ratio = (self.upper_price / self.lower_price) ** (1 / self.grid_count)
        grids = [self.lower_price * (ratio ** i) for i in range(self.grid_count + 1)]
        return sorted(grids)

    def get_orders_to_place(self, current_price: float,
                           current_position: float) -> Dict:
        """获取需要挂的订单"""
        orders = {'buy': [], 'sell': []}

        current_grid_idx = self._find_grid_index(current_price)

        for i, grid_price in enumerate(self.grids):
            # 当前价格下方的网格 → 挂买单
            if grid_price < current_price * 0.995:  # 留0.5%缓冲防止频繁触发
                grid_investment = self.investment / self.grid_count
                orders['buy'].append({
                    'price': grid_price,
                    'amount': grid_investment / grid_price,
                    'grid_index': i
                })

            # 当前价格上方的网格 → 挂卖单（前提是有持仓可卖）
            if grid_price > current_price * 1.005 and current_position > 0:
                orders['sell'].append({
                    'price': grid_price,
                    'amount': self.investment / self.grid_count / grid_price,
                    'grid_index': i
                })

        return orders

    def on_order_filled(self, order_type: str, price: float,
                       amount: float, grid_index: int):
        """订单成交回调 -- 这是网格策略的核心循环"""
        self.trade_count += 1

        # 卖单成交时计算已实现利润
        if order_type == 'sell':
            buy_price = self.grids[grid_index - 1] if grid_index > 0 else price * 0.95
            profit = (price - buy_price) * amount
            self.total_profit += profit

        # 重新平衡：成交后在相反方向补单
        return self._rebalance_grid(grid_index, order_type)

    def _rebalance_grid(self, filled_grid: int, filled_type: str) -> Dict:
        """重新平衡网格订单
        核心逻辑：买单成交后在上方挂卖单，卖单成交后在下方挂买单
        这样形成"买低卖高"的循环
        """
        new_orders = []

        if filled_type == 'buy':
            # 买单成交 → 在上方一个网格挂卖单
            if filled_grid < len(self.grids) - 1:
                sell_price = self.grids[filled_grid + 1]
                new_orders.append({
                    'type': 'sell',
                    'price': sell_price,
                    'grid_index': filled_grid + 1
                })

        elif filled_type == 'sell':
            # 卖单成交 → 在下方一个网格挂买单
            if filled_grid > 0:
                buy_price = self.grids[filled_grid - 1]
                new_orders.append({
                    'type': 'buy',
                    'price': buy_price,
                    'grid_index': filled_grid - 1
                })

        return {'new_orders': new_orders}

    def get_status(self) -> Dict:
        """获取策略状态"""
        return {
            'total_profit': self.total_profit,
            'trade_count': self.trade_count,
            'avg_profit_per_trade': (
                self.total_profit / self.trade_count if self.trade_count > 0 else 0
            ),
            'grid_range': f"{self.lower_price:.2f} - {self.upper_price:.2f}",
            'grid_count': self.grid_count
        }
```

### 课后自测

1. **网格策略在什么市场条件下表现最好？什么条件下会亏损？**

   **答案：** 网格策略在**震荡行情**（价格在区间内来回波动）中表现最好，因为每次波动都能触发买卖赚取差价。在**单边趋势行情**中表现最差：如果价格一直上涨，所有买单都无法成交，错失机会；如果价格一直下跌，所有买单都成交但卖单无法成交，造成浮亏。极端情况下，价格跌破下界，所有网格的买单都成交，产生严重亏损。

2. **等比网格相比等差网格的优势是什么？在什么场景下等差网格更好？**

   **答案：** 等比网格在低价区网格更密，高价区更稀疏。优势是：低价时买入更频繁，降低了平均持仓成本。等差网格在每个价位的交易量相同，适合价格波动幅度固定的场景（如波动率稳定的股指）。

---

## 模块5.5：风险管理（本课核心）

### 学习目标

完成本模块后，你应能够：

1. 设计一套包含多重安全检查的风险管理规则
2. 实现熔断机制并解释其触发条件和恢复逻辑
3. 计算综合风险评分（0-100分），并解释各分项的权重设定依据
4. 将量化交易的风控原则迁移到其他AI自动化系统

### 正文

#### 为什么风险管理是本课核心

风险管理模块的设计原则**适用于任何AI自动化系统**，不仅是交易：

| 交易系统的风控 | 其他AI自动化系统的类比 |
|-------------|---------------------|
| 最大持仓限制 | API调用的速率限制 |
| 日亏损上限 | 每日错误操作次数上限 |
| 熔断机制 | 异常检测后自动暂停 |
| 风险评分 | 系统健康度评分 |
| 交易间隔限制 | 操作频率限制（防止误操作） |

掌握这些原则后，你可以为任何自动化系统设计安全防线。

#### RiskManager完整实现

```python
# risk_manager.py - 风险管理模块
# 设计哲学："先建防线再建功能"
# 任何自动执行操作的系统都需要回答：什么情况下应该停下来？
from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

@dataclass
class RiskLimits:
    """风控限制参数 -- 五项核心限制"""
    max_position_value: float = 1000   # 最大持仓价值（美元）
    max_daily_loss: float = 100        # 最大日亏损（美元）
    max_drawdown_pct: float = 0.10     # 最大回撤（10%）
    max_trades_per_day: int = 5        # 每日最大交易次数
    min_order_interval_minutes: int = 30  # 最小下单间隔（分钟）

class RiskManager:
    def __init__(self, limits: RiskLimits = None):
        self.limits = limits or RiskLimits()
        self.daily_stats = self._load_daily_stats()
        self.trade_history = []
        self.circuit_breaker_triggered = False

    def check_trade_allowed(self,
                           action: str,
                           current_position: float,
                           position_value: float,
                           account_value: float) -> Dict:
        """六重安全检查 -- 每一笔交易都必须通过全部检查
        检查顺序有讲究：最严重的（熔断）最先检查，
        因为一旦熔断，后面的检查都不需要做了
        """

        reasons = []

        # 第1重：检查熔断状态（最高优先级）
        # 熔断一旦触发，当天所有交易都停止
        if self.circuit_breaker_triggered:
            return {
                'allowed': False,
                'reason': '熔断已触发，今日停止交易'
            }

        # 第2重：检查持仓限制
        # 防止单一资产占比过大
        if action == 'BUY' and position_value >= self.limits.max_position_value:
            reasons.append(f'持仓价值已达上限 ${self.limits.max_position_value}')

        # 第3重：检查日亏损（可触发熔断）
        # 这是最重要的防线之一：一天亏太多就停手
        daily_pnl = self._calculate_daily_pnl()
        if daily_pnl <= -self.limits.max_daily_loss:
            self._trigger_circuit_breaker()
            return {
                'allowed': False,
                'reason': f'日亏损已达上限 ${self.limits.max_daily_loss}，触发熔断'
            }

        # 第4重：检查交易次数
        # 防止过度交易（频繁交易 = 高手续费 + 低质量决策）
        today_trades = self._count_today_trades()
        if today_trades >= self.limits.max_trades_per_day:
            reasons.append(f'今日交易次数已达上限 {self.limits.max_trades_per_day}')

        # 第5重：检查下单间隔
        # 防止短时间内连续下单（情绪化交易的典型特征）
        last_trade_time = self._get_last_trade_time()
        if last_trade_time:
            minutes_since = (datetime.now() - last_trade_time).total_seconds() / 60
            if minutes_since < self.limits.min_order_interval_minutes:
                reasons.append(
                    f'距离上次交易仅{minutes_since:.1f}分钟，'
                    f'需等待{self.limits.min_order_interval_minutes}分钟'
                )

        # 第6重：检查回撤（可触发熔断）
        # 账户从最高点回撤超过阈值，说明策略可能失效
        drawdown = self._calculate_drawdown(account_value)
        if drawdown > self.limits.max_drawdown_pct:
            self._trigger_circuit_breaker()
            return {
                'allowed': False,
                'reason': (
                    f'回撤已达{drawdown:.1%}，超过限制'
                    f'{self.limits.max_drawdown_pct:.1%}，触发熔断'
                )
            }

        if reasons:
            return {
                'allowed': False,
                'reason': '; '.join(reasons)
            }

        return {
            'allowed': True,
            'reason': None
        }

    def record_trade(self, trade: Dict):
        """记录交易"""
        trade['timestamp'] = datetime.now().isoformat()
        self.trade_history.append(trade)
        self._save_daily_stats()

    def _trigger_circuit_breaker(self):
        """触发熔断 -- 这是最后的安全阀
        一旦触发：
        1. 设置熔断标志（当天不可逆）
        2. 记录触发时间
        3. 发送报警通知
        """
        self.circuit_breaker_triggered = True
        self.daily_stats['circuit_breaker_triggered'] = True
        self.daily_stats['circuit_breaker_time'] = datetime.now().isoformat()
        self._save_daily_stats()
        self._send_alert('熔断触发', '交易已暂停，请检查账户状态')

    def get_risk_report(self) -> Dict:
        """获取风险报告"""
        return {
            'daily_pnl': self._calculate_daily_pnl(),
            'drawdown': self._calculate_drawdown(),
            'today_trades': self._count_today_trades(),
            'circuit_breaker': self.circuit_breaker_triggered,
            'position_utilization': self._get_position_utilization(),
            'risk_score': self._calculate_risk_score()
        }

    def _calculate_risk_score(self) -> float:
        """计算综合风险评分（0-100，越高越危险）
        评分权重设计理由：
        - 回撤（40分）：最能反映策略是否失效
        - 日亏损（30分）：反映当天的交易质量
        - 交易频率（20分）：频繁交易通常意味着策略不稳定
        - 持仓占比（10分）：集中持仓增加风险但影响较小
        """
        score = 0

        # 回撤贡献（0-40分）
        drawdown = self._calculate_drawdown()
        score += min(drawdown / self.limits.max_drawdown_pct * 40, 40)

        # 日亏损贡献（0-30分）
        daily_pnl = self._calculate_daily_pnl()
        if daily_pnl < 0:
            score += min(abs(daily_pnl) / self.limits.max_daily_loss * 30, 30)

        # 交易频率贡献（0-20分）
        trade_ratio = self._count_today_trades() / self.limits.max_trades_per_day
        score += trade_ratio * 20

        # 持仓贡献（0-10分）
        position_util = self._get_position_utilization()
        score += position_util * 10

        return min(score, 100)
```

#### 六重安全检查流程图

```
交易信号到达
    │
    ▼
[1. 熔断检查] ──── 已触发 ──→ 拒绝，今日停止
    │ 未触发
    ▼
[2. 持仓检查] ──── 超限 ────→ 记录原因
    │ 未超限
    ▼
[3. 日亏损检查] ── 超限 ────→ 触发熔断，拒绝
    │ 未超限
    ▼
[4. 交易次数检查] ─ 超限 ────→ 记录原因
    │ 未超限
    ▼
[5. 下单间隔检查] ─ 太频繁 ──→ 记录原因
    │ 间隔足够
    ▼
[6. 回撤检查] ──── 超限 ────→ 触发熔断，拒绝
    │ 未超限
    ▼
  全部通过？
  ├── 有原因 → 拒绝（返回所有原因）
  └── 无原因 → 允许交易
```

#### 风险管理的通用设计原则

这些原则适用于**任何AI自动化系统**，不仅是交易：

1. **先建防线再建功能：** 在实现自动化功能之前，先设计好"什么情况下停止"
2. **多重检查，层层设防：** 不要依赖单一检查点，每一层都可能失效
3. **熔断不可逆（或需手动恢复）：** 防止系统在异常状态下反复尝试
4. **监控比策略更重要：** 策略可以赔钱，但监控保证你知道在赔钱
5. **量化风险：** 用分数（0-100）而非"高/中/低"来衡量风险，便于设置自动化阈值

### 课后自测

1. **为什么日亏损检查和回撤检查都能触发熔断，而持仓检查和交易次数检查不会？**

   **答案：** 日亏损和回撤反映的是"资金安全"问题 -- 一旦触发说明当天策略可能存在系统性问题，继续交易只会扩大损失。持仓和交易次数反映的是"操作规范"问题 -- 超限只意味着当前这笔交易不应执行，但不意味着整个系统出了问题。熔断是"紧急刹车"，只在关乎资金安全时使用。

2. **风险评分中，回撤权重（40分）为什么高于日亏损权重（30分）？**

   **答案：** 回撤衡量的是"从高点到低点的最大跌幅"，反映的是策略的系统性风险（长期表现恶化）。日亏损只衡量"今天一天"的表现，可能是短期波动。回撤持续扩大意味着策略可能已经失效，比单日亏损更值得警惕，因此权重更高。

3. **如果要为一个"AI自动发送营销邮件"系统设计风控规则，你会设计哪些检查？**

   **答案：** 参考答案：(1) 每日发送总量上限（防止垃圾邮件）；(2) 单用户发送频率限制（防止骚扰）；(3) 退订率监控 -- 退订率>5%时暂停（防止品牌损害）；(4) 内容异常检测 -- AI生成的邮件包含敏感词时拦截；(5) 熔断机制 -- 投诉率达标时停止所有发送。

---

## 模块5.6：实时监控Dashboard

### 学习目标

完成本模块后，你应能够：

1. 使用Streamlit构建一个包含多个指标卡片的监控页面
2. 使用Plotly创建K线图并标记交易信号
3. 解释监控Dashboard各组件的设计意图

### 正文

> **[知识补给站] Streamlit和Plotly基础用法**
>
> **Streamlit** 是一个用纯Python构建Web应用的框架：
> ```python
> import streamlit as st
>
> # 指标卡片
> st.metric(label="账户总值", value="$10,000", delta="$150")
>
> # 多列布局
> col1, col2 = st.columns(2)
> with col1:
>     st.write("左侧内容")
> with col2:
>     st.write("右侧内容")
>
> # 显示图表
> st.plotly_chart(fig, use_container_width=True)
> ```
>
> **Plotly** 是一个交互式图表库：
> ```python
> import plotly.graph_objects as go
> from plotly.subplots import make_subplots
>
> # K线图
> fig = go.Figure(go.Candlestick(
>     x=dates, open=opens, high=highs, low=lows, close=closes
> ))
>
> # 仪表盘
> fig = go.Figure(go.Indicator(
>     mode="gauge+number",
>     value=75,
>     gauge={'axis': {'range': [0, 100]}}
> ))
>
> # 子图
> fig = make_subplots(rows=2, cols=1, shared_xaxes=True)
> ```

#### TradingDashboard完整实现

```python
# dashboard.py - 量化交易实时监控Dashboard
# 运行方式：streamlit run dashboard.py
# 职责：将各组件的状态数据可视化展示
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sqlite3
from datetime import datetime, timedelta

class TradingDashboard:
    def __init__(self):
        st.set_page_config(
            page_title="量化交易监控",
            page_icon="chart_with_upwards_trend",
            layout="wide"           # 宽屏布局，充分利用屏幕
        )

    def run(self):
        """运行Dashboard"""
        st.title("量化交易实时监控")

        self._render_sidebar()

        # 三列布局：账户 | 策略 | 风险
        col1, col2, col3 = st.columns(3)

        with col1:
            self._render_account_summary()

        with col2:
            self._render_strategy_status()

        with col3:
            self._render_risk_metrics()

        st.markdown("---")
        self._render_price_chart()

        st.markdown("---")
        self._render_trade_history()

    def _render_account_summary(self):
        """账户概览 -- 三个核心指标"""
        st.subheader("账户概览")

        account = self._get_account_data()

        # st.metric自带delta显示，绿涨红跌
        st.metric(
            label="账户总值",
            value=f"${account['total_value']:.2f}",
            delta=f"${account['daily_pnl']:.2f}"
        )
        st.metric(
            label="USDT余额",
            value=f"${account['usdt_balance']:.2f}"
        )
        st.metric(
            label="ETH持仓",
            value=f"{account['eth_amount']:.4f}",
            delta=f"${account['eth_value']:.2f}"
        )

    def _render_strategy_status(self):
        """策略状态 -- ML策略和网格策略的实时数据"""
        st.subheader("策略状态")

        ml_status = self._get_ml_strategy_status()
        st.markdown(f"""
        **ML策略**
        - 今日信号: {ml_status['signals_today']}
        - 执行交易: {ml_status['executed_trades']}
        - 模型版本: {ml_status['model_version']}
        """)

        grid_status = self._get_grid_strategy_status()
        st.markdown(f"""
        **网格策略**
        - 运行状态: {'运行中' if grid_status['active'] else '暂停'}
        - 今日成交: {grid_status['trades_today']}
        - 累计利润: ${grid_status['total_profit']:.2f}
        """)

    def _render_risk_metrics(self):
        """风险监控 -- 风险评分仪表盘 + 详细指标"""
        st.subheader("风险监控")

        risk = self._get_risk_data()

        # 风险评分仪表盘：绿(0-30) / 黄(30-70) / 红(70-100)
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=risk['risk_score'],
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "风险评分"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 30], 'color': "green"},
                    {'range': [30, 70], 'color': "yellow"},
                    {'range': [70, 100], 'color': "red"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 70       # 70分以上红色警戒线
                }
            }
        ))
        fig.update_layout(height=200)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown(f"""
        - 今日盈亏: ${risk['daily_pnl']:.2f}
        - 最大回撤: {risk['drawdown']:.2%}
        - 熔断状态: {'已触发' if risk['circuit_breaker'] else '正常'}
        """)

    def _render_price_chart(self):
        """价格图表 -- K线 + 交易信号 + 成交量"""
        st.subheader("价格走势与信号")

        df = self._get_price_data(hours=48)

        # 创建双行子图：上方K线，下方成交量
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.7, 0.3]
        )

        # K线图
        fig.add_trace(
            go.Candlestick(
                x=df['timestamp'],
                open=df['open'], high=df['high'],
                low=df['low'], close=df['close'],
                name='ETH/USDT'
            ),
            row=1, col=1
        )

        # 标记买卖信号
        signals = self._get_signals()
        buy_signals = signals[signals['action'] == 'BUY']
        sell_signals = signals[signals['action'] == 'SELL']

        fig.add_trace(
            go.Scatter(
                x=buy_signals['timestamp'], y=buy_signals['price'],
                mode='markers',
                marker=dict(color='green', size=10, symbol='triangle-up'),
                name='买入信号'
            ),
            row=1, col=1
        )

        fig.add_trace(
            go.Scatter(
                x=sell_signals['timestamp'], y=sell_signals['price'],
                mode='markers',
                marker=dict(color='red', size=10, symbol='triangle-down'),
                name='卖出信号'
            ),
            row=1, col=1
        )

        # 成交量柱状图
        fig.add_trace(
            go.Bar(
                x=df['timestamp'], y=df['volume'],
                name='成交量', marker_color='blue'
            ),
            row=2, col=1
        )

        fig.update_layout(
            height=600,
            showlegend=True,
            xaxis_rangeslider_visible=False
        )

        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    dashboard = TradingDashboard()
    dashboard.run()
```

### 课后自测

1. **为什么风险评分仪表盘的阈值设在70分而不是50分？**

   **答案：** 50分意味着一半的风险容量已经用完，但还有缓冲空间，不需要立即报警。70分意味着风险已经进入危险区域，接近触发熔断的水平（如回撤接近上限、日亏损接近上限），此时需要引起高度关注。设在70分是为了给人工干预留出时间窗口。

2. **K线图上标记交易信号有什么实际用途？**

   **答案：** (1) 事后复盘：直观看到买卖点是否合理；(2) 策略调优：发现"在下跌趋势中频繁买入"等系统性问题；(3) 异常检测：如果信号集中在某个时间段，可能说明数据或策略有异常。

---

## 练习

### 练习07：为RiskManager添加"连续亏损保护"规则

**难度：** 中高级
**时间：** 25分钟
**对应教学目标：** 能设计并实现风险管理规则；理解风控在AI自动化中的通用价值

#### 题目描述

为RiskManager添加一条新的风控规则 -- "连续亏损保护"：

- 当连续3笔交易亏损时，自动将下一笔交易的最大仓位降低50%
- 当连续5笔交易亏损时，触发熔断
- 连续亏损后如果出现一笔盈利，计数器重置为0

#### 骨架代码

```python
# 在RiskManager类中添加以下方法

def _check_consecutive_losses(self) -> Dict:
    """检查连续亏损情况

    Returns:
        {
            'consecutive_losses': int,  # 当前连续亏损次数
            'action': str,              # 'normal' | 'reduce_position' | 'circuit_break'
            'position_multiplier': float # 仓位调整系数（1.0=正常, 0.5=减半）
        }
    """
    # TODO: 从self.trade_history中获取最近的交易记录
    # TODO: 从最新一笔开始往回数，统计连续亏损次数
    # TODO: 根据连续亏损次数返回对应的action
    pass

def check_trade_allowed_v2(self,
                           action: str,
                           current_position: float,
                           position_value: float,
                           account_value: float) -> Dict:
    """升级版交易检查 -- 在原有六重检查基础上增加连续亏损检查"""
    # TODO: 先调用原有的check_trade_allowed
    # TODO: 如果原有检查通过，再检查连续亏损
    # TODO: 如果连续亏损>=3，修改返回结果中的最大仓位
    # TODO: 如果连续亏损>=5，触发熔断
    pass
```

#### 测试用例

```python
def test_consecutive_losses():
    rm = RiskManager(RiskLimits())

    # 测试1：无亏损 -- 正常交易
    result = rm._check_consecutive_losses()
    assert result['consecutive_losses'] == 0
    assert result['action'] == 'normal'
    assert result['position_multiplier'] == 1.0

    # 测试2：连续3笔亏损 -- 仓位减半
    rm.trade_history = [
        {'pnl': -10, 'timestamp': '2026-01-01T10:00:00'},
        {'pnl': -15, 'timestamp': '2026-01-01T11:00:00'},
        {'pnl': -8, 'timestamp': '2026-01-01T12:00:00'},
    ]
    result = rm._check_consecutive_losses()
    assert result['consecutive_losses'] == 3
    assert result['action'] == 'reduce_position'
    assert result['position_multiplier'] == 0.5

    # 测试3：连续5笔亏损 -- 触发熔断
    rm.trade_history = [
        {'pnl': -10}, {'pnl': -15}, {'pnl': -8},
        {'pnl': -12}, {'pnl': -20},
    ]
    result = rm._check_consecutive_losses()
    assert result['consecutive_losses'] == 5
    assert result['action'] == 'circuit_break'

    # 测试4：3笔亏损后1笔盈利 -- 计数器重置
    rm.trade_history = [
        {'pnl': -10}, {'pnl': -15}, {'pnl': -8},
        {'pnl': 25},  # 盈利，重置计数
    ]
    result = rm._check_consecutive_losses()
    assert result['consecutive_losses'] == 0
    assert result['action'] == 'normal'
```

#### 期望输出

```
test_consecutive_losses: 4/4 tests passed
- 无亏损时正常交易 [PASS]
- 3连亏时仓位减半 [PASS]
- 5连亏时触发熔断 [PASS]
- 亏损后盈利重置计数 [PASS]
```

#### 评分维度

| 维度 | 权重 | 标准 |
|------|------|------|
| 逻辑正确性 | 40% | 4个测试用例全部通过 |
| 代码集成 | 25% | 能正确集成到check_trade_allowed_v2中 |
| 边界处理 | 20% | 空交易记录、全盈利、混合盈亏等边界情况 |
| 代码规范 | 15% | 类型注解、docstring、注释清晰 |

---

## 本课知识总结

### 核心概念回顾

| 概念 | 一句话定义 |
|------|-----------|
| 四层架构 | 数据层-策略层-执行层-监控层，每层只与相邻层交互，便于独立替换 |
| 特征工程 | 从原始价格和成交量中计算技术指标，为ML模型提供输入 |
| ML策略 | 用随机森林将技术指标映射为买/持/卖信号，置信度>0.6才执行 |
| 网格策略 | 在固定价格区间内设置多个网格，利用波动自动低买高卖 |
| 六重安全检查 | 熔断->持仓->日亏损->交易次数->下单间隔->回撤，层层防线 |
| 风险评分 | 0-100分量化风险，回撤(40)+日亏(30)+频率(20)+持仓(10) |

### 关键结论

1. **分层架构是管理复杂系统的基本方法**。四层架构使得策略、数据、执行、监控各自独立演进，降低了系统的整体复杂度。
2. **ML策略不是"黑盒预测"，而是"概率决策"**。通过置信度阈值和标签缓冲区（1.5%），将不确定性控制在可接受范围内。
3. **风险管理的设计原则具有通用性**。六重安全检查、熔断机制、风险评分等概念可以迁移到任何AI自动化系统。
4. **监控比策略更重要**。策略可以亏钱，但没有监控就无法知道在亏钱。Dashboard是系统的"仪表盘"，不是可选的装饰。

---

## 扩展阅读

1. **ccxt官方文档：** https://docs.ccxt.com/ -- 统一加密货币交易所API库，支持100+交易所
2. **scikit-learn随机森林文档：** https://scikit-learn.org/stable/modules/ensemble.html#forests-of-randomized-trees
3. **Streamlit官方文档：** https://docs.streamlit.io/ -- 用Python快速构建数据应用
4. **Plotly Python文档：** https://plotly.com/python/ -- 交互式图表库
5. **Investopedia RSI解释：** https://www.investopedia.com/terms/r/rsi.asp -- 技术指标的通俗解释
6. **关于网格策略的深度分析：** 搜索"Grid Trading Strategy Explained"了解更多网格策略的变体和优化方法
