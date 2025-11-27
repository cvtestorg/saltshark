# Python 项目开发核心原则

## 核心开发理念

### 1. 测试驱动开发（TDD）是强制要求

**所有功能开发必须遵循 TDD 流程：**

#### Red-Green-Refactor 循环
1. **Red（红）**: 先编写失败的测试
   - 在编写任何生产代码之前，必须先写测试
   - 测试应该清晰描述预期行为
   - 运行测试，确认它失败（证明测试有效）

2. **Green（绿）**: 编写最简代码使测试通过
   - 实现满足测试的最小代码
   - 不要过度设计或添加未测试的功能
   - 运行测试，确认全部通过

3. **Refactor（重构）**: 优化代码质量
   - 重构代码以提高可读性和可维护性
   - 消除重复，改善设计
   - 确保测试仍然通过

#### TDD 实践规则
```python
# ❌ 错误：直接编写实现代码
def calculate_total(items: list[dict]) -> float:
    return sum(item['price'] * item['quantity'] for item in items)

# ✅ 正确：先编写测试
def test_calculate_total_with_multiple_items():
    """测试计算多个商品的总价"""
    items = [
        {'price': 10.0, 'quantity': 2},
        {'price': 5.0, 'quantity': 3}
    ]
    assert calculate_total(items) == 35.0

def test_calculate_total_with_empty_list():
    """测试空列表返回0"""
    assert calculate_total([]) == 0.0

# 然后再实现功能
def calculate_total(items: list[dict]) -> float:
    """计算商品总价"""
    return sum(item['price'] * item['quantity'] for item in items)
```

#### 测试覆盖率要求
- **最低覆盖率**: 80%（强制）
- **目标覆盖率**: 90%+
- **关键路径覆盖率**: 100%（核心业务逻辑）
- 每次提交前必须运行 `pytest --cov` 检查覆盖率

### 2. Python 之禅（The Zen of Python）

遵循 PEP 20 的核心原则：

```
Beautiful is better than ugly.
Explicit is better than implicit.
Simple is better than complex.
Complex is better than complicated.
Flat is better than nested.
Sparse is better than dense.
Readability counts.
```

**实践要点：**
- **美观优于丑陋**: 代码应该赏心悦目，格式化工具不能替代良好的代码结构
- **明确优于隐晦**: 避免魔法方法和隐式行为，代码意图应该一目了然
- **简单优于复杂**: 优先选择简单的解决方案，避免过度工程
- **扁平优于嵌套**: 减少嵌套层级，使用早返回（early return）
- **可读性很重要**: 代码是写给人看的，优先考虑可读性而非简洁性

### 3. SOLID 原则

#### S - 单一职责原则（Single Responsibility Principle）
- 每个类、函数只负责一件事
- 修改的理由只有一个

```python
# ❌ 违反 SRP：一个类做太多事
class User:
    def save_to_database(self): ...
    def send_email(self): ...
    def generate_report(self): ...

# ✅ 遵循 SRP：职责分离
class User:
    """用户实体"""
    pass

class UserRepository:
    """用户数据持久化"""
    def save(self, user: User): ...

class EmailService:
    """邮件发送服务"""
    def send_to_user(self, user: User): ...

class ReportGenerator:
    """报告生成器"""
    def generate_user_report(self, user: User): ...
```

#### O - 开闭原则（Open/Closed Principle）
- 对扩展开放，对修改封闭
- 使用抽象和多态实现扩展

```python
from abc import ABC, abstractmethod

class PaymentProcessor(ABC):
    """支付处理器抽象基类"""
    @abstractmethod
    def process(self, amount: float) -> bool:
        pass

class CreditCardProcessor(PaymentProcessor):
    """信用卡支付"""
    def process(self, amount: float) -> bool:
        # 信用卡支付逻辑
        return True

class PayPalProcessor(PaymentProcessor):
    """PayPal 支付"""
    def process(self, amount: float) -> bool:
        # PayPal 支付逻辑
        return True
```

#### L - 里氏替换原则（Liskov Substitution Principle）
- 子类必须能够替换父类
- 子类不应该改变父类的行为契约

#### I - 接口隔离原则（Interface Segregation Principle）
- 客户端不应依赖它不使用的接口
- 使用多个专用接口而非单一通用接口

#### D - 依赖倒置原则（Dependency Inversion Principle）
- 依赖抽象而非具体实现
- 高层模块不应依赖低层模块

```python
# ✅ 依赖注入示例
class UserService:
    def __init__(self, repository: UserRepository, email_service: EmailService):
        self.repository = repository
        self.email_service = email_service
    
    def register_user(self, user_data: dict) -> User:
        user = User(**user_data)
        self.repository.save(user)
        self.email_service.send_welcome_email(user)
        return user
```

### 4. DRY 原则（Don't Repeat Yourself）

- **消除重复**: 相同的逻辑不应出现在多个地方
- **抽象提取**: 将重复代码提取为函数、类或模块
- **配置驱动**: 使用配置文件而非硬编码重复的值

```python
# ❌ 重复代码
def calculate_price_with_tax_usa(price: float) -> float:
    return price * 1.07

def calculate_price_with_tax_canada(price: float) -> float:
    return price * 1.13

# ✅ DRY 原则
def calculate_price_with_tax(price: float, tax_rate: float) -> float:
    """计算含税价格"""
    return price * (1 + tax_rate)

# 配置文件
TAX_RATES = {
    'USA': 0.07,
    'CANADA': 0.13,
}
```

### 5. YAGNI 原则（You Aren't Gonna Need It）

- **不要过度设计**: 只实现当前需要的功能
- **延迟决策**: 在需要时再添加功能，而非提前预测
- **保持简单**: 避免"万一以后需要"的代码

```python
# ❌ 过度设计
class User:
    def __init__(self):
        self.cache = {}  # 可能以后需要缓存？
        self.logger = Logger()  # 可能需要日志？
        self.metrics = MetricsCollector()  # 可能需要监控？

# ✅ YAGNI：只实现需要的
class User:
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email
```

### 6. 类型安全

- **强制类型提示**: 所有函数必须有完整的类型标注
- **运行 mypy**: 提交前必须通过静态类型检查
- **使用 Protocol**: 定义接口而非依赖具体类型

```python
from typing import Protocol

class Drawable(Protocol):
    """可绘制对象协议"""
    def draw(self) -> None: ...

def render(obj: Drawable) -> None:
    """渲染可绘制对象"""
    obj.draw()
```

### 7. 防御性编程

- **验证输入**: 永远不要信任外部输入
- **早失败**: 在问题发生时立即抛出异常
- **明确异常**: 使用具体的异常类型，提供清晰的错误信息

```python
def divide(a: float, b: float) -> float:
    """安全的除法运算"""
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("参数必须是数字类型")
    
    if b == 0:
        raise ValueError("除数不能为零")
    
    return a / b
```

### 8. 文档驱动开发

- **API 先行**: 在实现前编写接口文档
- **完整 Docstring**: 所有公共 API 必须有详细文档
- **示例代码**: 文档中包含使用示例

```python
def fetch_user_data(
    user_id: int,
    include_profile: bool = False,
    timeout: float = 30.0
) -> dict[str, Any]:
    """获取用户数据
    
    从数据库获取指定用户的数据，可选择性地包含详细资料。
    
    Args:
        user_id: 用户唯一标识符，必须为正整数
        include_profile: 是否包含用户详细资料，默认为 False
        timeout: 请求超时时间（秒），默认 30 秒
    
    Returns:
        包含用户数据的字典，至少包含以下键：
        - id: 用户ID
        - name: 用户名
        - email: 邮箱地址
        如果 include_profile=True，还包含：
        - profile: 用户详细资料字典
    
    Raises:
        ValueError: 当 user_id 不是正整数时
        UserNotFoundError: 当用户不存在时
        DatabaseError: 当数据库连接失败时
        TimeoutError: 当请求超时时
    
    Example:
        >>> user = fetch_user_data(123, include_profile=True)
        >>> print(user['name'])
        'John Doe'
    """
    if user_id <= 0:
        raise ValueError("user_id 必须是正整数")
    # 实现...
```

## 代码审查标准

所有代码合并前必须满足：

1. ✅ 所有测试通过（`pytest`）
2. ✅ 测试覆盖率 ≥ 80%（`pytest --cov`）
3. ✅ 无代码风格问题（`ruff check .`）
4. ✅ 代码已格式化（`ruff format .`）
5. ✅ 通过类型检查（`mypy .`）
6. ✅ 所有公共 API 有文档
7. ✅ 遵循 TDD 流程（测试先行）
8. ✅ 遵循 SOLID 原则
9. ✅ 无重复代码（DRY）
10. ✅ 无过度设计（YAGNI）

## 提交前检查清单

```bash
#!/bin/bash
# pre-commit 检查脚本

echo "🧪 运行测试..."
pytest || exit 1

echo "📊 检查覆盖率..."
pytest --cov --cov-fail-under=80 || exit 1

echo "🎨 格式化代码..."
ruff format .

echo "🔍 代码检查..."
ruff check . || exit 1

echo "🔬 类型检查..."
mypy . || exit 1

echo "✅ 所有检查通过！"
```

## 违反原则的处理

- **代码审查拒绝**: 不符合原则的代码不能合并
- **重构要求**: 必须按照原则进行重构
- **教育优先**: 帮助团队理解和应用这些原则

---

**记住**: 这些原则不是束缚，而是保证代码质量、可维护性和团队协作的基础。当有疑问时，优先考虑可读性和可测试性。
