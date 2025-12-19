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

## 类型提示

### 必需的类型提示
- **所有函数签名**必须包含参数和返回值类型提示
- **公共 API** 必须完整标注
- **类属性**应在类定义或 `__init__` 中标注

### 现代类型提示（Python 3.9+）
- 优先使用内置类型：`list`、`dict`、`tuple`、`set`（而非 `typing.List` 等）
- 使用 `|` 表示联合类型（Python 3.10+）：`str | None` 而非 `Optional[str]`
- 使用 `X | Y` 而非 `Union[X, Y]`

## 文档字符串

### Docstring 规范
- 使用三引号 `"""` 包裹文档字符串
- 公共函数、类、模块必须有 docstring
- 简短描述在首行，详细说明空一行后继续
- 使用 Google 风格或 NumPy 风格（项目保持一致）
- 必须包含 Args、Returns、Raises 等关键部分（如适用）

## 错误处理

### 异常处理最佳实践
- 捕获具体的异常类型，避免使用裸露的 `except:`
- 使用 `raise` 重新抛出异常，或使用 `raise ... from ...` 保留异常链
- 自定义异常应继承自内置异常类
- 记录异常信息以便调试

## 代码组织

### 函数和方法
- 函数应保持简短（通常不超过 50 行）
- 一个函数只做一件事（单一职责原则）
- 避免过多参数（超过 5 个考虑使用配置对象）
- 使用早返回（early return）减少嵌套

### 类设计
- 遵循单一职责原则
- 使用 `@dataclass` 简化数据类（Python 3.7+）
- 使用 `@property` 封装计算属性
- 魔术方法使用要克制，优先使用显式方法

## 现代 Python 特性

### 使用上下文管理器
- 文件操作、数据库连接等资源管理必须使用 `with` 语句
- 可使用 `contextlib.contextmanager` 装饰器创建自定义上下文管理器

### 使用推导式和生成器
- 优先使用列表推导、字典推导、集合推导代替循环
- 大数据集使用生成器表达式节省内存

### 使用 pathlib 处理路径
- 使用 `pathlib.Path` 而非字符串拼接路径
- 使用 `/` 运算符组合路径

## 测试

### 测试规范
- 测试文件命名：`test_*.py` 或 `*_test.py`
- 测试函数命名：`test_<功能描述>`，描述性强
- 使用 pytest fixtures 共享测试数据
- 遵循 AAA 模式：Arrange（准备）、Act（执行）、Assert（断言）
- 每个测试只验证一个行为或场景

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
- 优先考虑算法复杂度而非微优化

## 安全性

### 安全最佳实践
- 不要在代码中硬编码密码、API 密钥等敏感信息
- 使用环境变量或配置文件管理敏感数据（.env 文件不要提交到版本控制）
- 验证和清理所有外部输入
- 使用参数化查询防止 SQL 注入
- 使用 `secrets` 模块生成安全的随机数和令牌
