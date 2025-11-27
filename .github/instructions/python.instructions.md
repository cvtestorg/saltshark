---
applyTo: '**/*.py'
---

# Python 3 开发编码规范

## 代码风格

### 格式化
- 使用 **Ruff** 进行代码格式化，运行 `ruff format .`
- 行长度限制为 88 字符（Ruff 默认，与 Black 兼容）
- 使用 4 个空格缩进，不使用制表符
- 文件末尾保留一个空行

### 命名约定
- **类名**: 使用 `PascalCase`（如 `DataProcessor`、`UserService`）
- **函数/方法**: 使用 `snake_case`（如 `process_data`、`get_user_by_id`）
- **常量**: 使用 `UPPER_SNAKE_CASE`（如 `MAX_RETRY_COUNT`、`DEFAULT_TIMEOUT`）
- **变量**: 使用 `snake_case`（如 `user_name`、`total_count`）
- **私有成员**: 以单下划线开头（如 `_internal_method`、`_cache`）
- **模块**: 使用小写字母和下划线（如 `data_utils.py`、`http_client.py`）

### 导入语句
- 导入顺序：标准库 → 第三方库 → 本地模块，每组之间空一行
- 使用绝对导入，避免相对导入（除非在包内部）
- 每个导入独占一行（避免 `import os, sys`）
- 使用 `from typing import` 导入类型提示

```python
# 正确示例
import os
import sys
from pathlib import Path

import requests
from fastapi import FastAPI

from myapp.models import User
from myapp.utils import logger
```

## 类型提示

### 必需的类型提示
- **所有函数签名**必须包含参数和返回值类型提示
- **公共 API** 必须完整标注
- **类属性**应在类定义或 `__init__` 中标注

```python
from typing import Optional, List, Dict, Any

def process_users(
    users: List[Dict[str, Any]],
    max_count: int,
    filter_active: bool = True
) -> List[str]:
    """处理用户列表并返回用户名列表"""
    return [u["name"] for u in users[:max_count] if filter_active]

class DataProcessor:
    cache: Dict[str, Any]
    max_size: int
    
    def __init__(self, max_size: int = 100) -> None:
        self.cache = {}
        self.max_size = max_size
```

### 现代类型提示（Python 3.9+）
- 优先使用内置类型：`list`、`dict`、`tuple`、`set`（而非 `typing.List` 等）
- 使用 `|` 表示联合类型（Python 3.10+）：`str | None` 而非 `Optional[str]`
- 使用 `X | Y` 而非 `Union[X, Y]`

```python
# Python 3.10+ 推荐写法
def get_user(user_id: int) -> dict[str, Any] | None:
    """获取用户信息"""
    pass

def merge_lists(a: list[str], b: list[str]) -> list[str]:
    """合并两个列表"""
    return a + b
```

## 文档字符串

### Docstring 规范
- 使用三引号 `"""` 包裹文档字符串
- 公共函数、类、模块必须有 docstring
- 简短描述在首行，详细说明空一行后继续
- 使用 Google 风格或 NumPy 风格（项目保持一致）

```python
def calculate_discount(price: float, discount_rate: float) -> float:
    """计算折扣后的价格
    
    Args:
        price: 原始价格
        discount_rate: 折扣率（0.0 到 1.0 之间）
    
    Returns:
        折扣后的价格
        
    Raises:
        ValueError: 当折扣率不在有效范围内时
    """
    if not 0.0 <= discount_rate <= 1.0:
        raise ValueError("折扣率必须在 0.0 到 1.0 之间")
    return price * (1 - discount_rate)
```

## 错误处理

### 异常处理最佳实践
- 捕获具体的异常类型，避免使用裸露的 `except:`
- 使用 `raise` 重新抛出异常，或使用 `raise ... from ...` 保留异常链
- 自定义异常应继承自内置异常类

```python
# 推荐写法
try:
    result = process_data(data)
except ValueError as e:
    logger.error(f"数据处理失败: {e}")
    raise ProcessingError("无法处理数据") from e
except KeyError as e:
    logger.warning(f"缺少必需的键: {e}")
    return default_value

# 自定义异常
class ProcessingError(Exception):
    """数据处理相关的异常"""
    pass
```

## 代码组织

### 函数和方法
- 函数应保持简短（通常不超过 50 行）
- 一个函数只做一件事
- 避免过多参数（超过 5 个考虑使用配置对象）
- 使用早返回（early return）减少嵌套

```python
def validate_user(user: dict[str, Any]) -> bool:
    """验证用户数据"""
    if not user.get("name"):
        return False
    if not user.get("email"):
        return False
    if user.get("age", 0) < 18:
        return False
    return True
```

### 类设计
- 遵循单一职责原则
- 使用 `@dataclass` 简化数据类（Python 3.7+）
- 使用 `@property` 封装计算属性
- 魔术方法使用要克制，优先使用显式方法

```python
from dataclasses import dataclass

@dataclass
class User:
    """用户数据类"""
    id: int
    name: str
    email: str
    age: int = 0
    
    @property
    def is_adult(self) -> bool:
        """判断是否成年"""
        return self.age >= 18
```

## 现代 Python 特性

### 使用上下文管理器
```python
# 推荐：使用 with 语句
with open("data.txt", "r") as f:
    data = f.read()

# 自定义上下文管理器
from contextlib import contextmanager

@contextmanager
def database_connection(db_url: str):
    conn = connect(db_url)
    try:
        yield conn
    finally:
        conn.close()
```

### 使用推导式和生成器
```python
# 列表推导
active_users = [u for u in users if u.is_active]

# 字典推导
user_map = {u.id: u.name for u in users}

# 生成器表达式（节省内存）
total = sum(len(line) for line in file)
```

### 使用 pathlib 处理路径
```python
from pathlib import Path

# 推荐：使用 pathlib
data_dir = Path("data")
config_file = data_dir / "config.json"

if config_file.exists():
    content = config_file.read_text()
```

## 测试

### 测试规范
- 测试文件命名：`test_*.py` 或 `*_test.py`
- 测试函数命名：`test_<功能描述>`，描述性强
- 使用 pytest fixtures 共享测试数据
- 遵循 AAA 模式：Arrange（准备）、Act（执行）、Assert（断言）

```python
import pytest
from myapp.services import UserService

@pytest.fixture
def user_service():
    """创建用户服务实例"""
    return UserService(db_url="sqlite:///:memory:")

def test_create_user_success(user_service):
    """测试成功创建用户"""
    # Arrange
    user_data = {"name": "张三", "email": "zhang@example.com"}
    
    # Act
    user = user_service.create_user(user_data)
    
    # Assert
    assert user.name == "张三"
    assert user.email == "zhang@example.com"
```

## 代码质量检查

### 提交前检查清单
```bash
# 1. 格式化代码
ruff format .

# 2. 运行 linter
ruff check .

# 3. 类型检查
mypy .

# 4. 运行测试
pytest

# 5. 检查覆盖率
pytest --cov
```

### 常见 Ruff 规则
- 移除未使用的导入和变量
- 使用 f-string 而非 `%` 或 `.format()`
- 避免可变默认参数（如 `def func(x=[]):`）
- 使用 `is` 比较 `None`：`if x is None:` 而非 `if x == None:`

## 性能考虑

### 优化建议
- 使用 `collections` 模块的专用数据结构（`defaultdict`、`Counter`、`deque`）
- 大量字符串拼接使用 `"".join()` 而非 `+`
- 使用集合 `set` 进行成员检查（`O(1)` vs 列表的 `O(n)`）
- 缓存重复计算结果（使用 `@lru_cache`）

```python
from functools import lru_cache
from collections import defaultdict

@lru_cache(maxsize=128)
def fibonacci(n: int) -> int:
    """计算斐波那契数（带缓存）"""
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

# 使用 defaultdict 避免检查键是否存在
word_count: defaultdict[str, int] = defaultdict(int)
for word in words:
    word_count[word] += 1
```

## 安全性

### 安全最佳实践
- 不要在代码中硬编码密码、API 密钥等敏感信息
- 使用环境变量或配置文件管理敏感数据
- 验证和清理所有外部输入
- 使用参数化查询防止 SQL 注入

```python
import os
from pathlib import Path

# 推荐：从环境变量读取敏感信息
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY 环境变量未设置")

# 使用 .env 文件（不要提交到版本控制）
from dotenv import load_dotenv
load_dotenv()
```
