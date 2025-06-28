import json
from typing import Any, Union, Optional

def json_to_markdown(
    data: Union[str, dict, list], 
    title: str = "Data", 
    force_table: bool = False,
    force_structure: bool = False
) -> str:
    """
    将JSON数据转换为Markdown格式（统一函数）
    
    Args:
        data: JSON数据（字符串、字典或列表）
        title: 标题
        force_table: 强制使用表格格式（仅对列表有效）
        force_structure: 强制使用结构化格式
    
    Returns:
        str: Markdown格式的字符串
    """
    
    # 解析JSON字符串
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError as e:
            return f"❌ **JSON解析错误**: {str(e)}"
    
    # 根据数据类型和参数选择转换方式
    if isinstance(data, list):
        if force_structure:
            return _convert_to_structure(data, title)
        elif force_table or _is_suitable_for_table(data):
            return _convert_to_table(data, title)
        else:
            return _convert_to_structure(data, title)
    else:
        return _convert_to_structure(data, title)

def _is_suitable_for_table(data: list) -> bool:
    """判断列表数据是否适合转换为表格"""
    if not data or len(data) < 2:
        return False
    
    # 检查是否所有元素都是字典
    if not all(isinstance(item, dict) for item in data):
        return False
    
    # 检查是否有共同的键
    all_keys = [set(item.keys()) for item in data if isinstance(item, dict)]
    if not all_keys:
        return False
    
    # 计算键的重叠度
    common_keys = set.intersection(*all_keys)
    total_unique_keys = set.union(*all_keys)
    
    # 如果共同键占比超过60%，适合表格格式
    overlap_ratio = len(common_keys) / len(total_unique_keys) if total_unique_keys else 0
    return overlap_ratio > 0.6

def _convert_to_table(data: list, title: str) -> str:
    """转换为表格格式"""
    if not data:
        return f"# {title}\n\n*(空数据)*"
    
    # 获取所有键
    all_keys = set()
    for item in data:
        if isinstance(item, dict):
            all_keys.update(item.keys())
    
    if not all_keys:
        return f"# {title}\n\n*(没有找到有效的对象)*"
    
    # 排序列名
    columns = sorted(all_keys)
    
    # 构建表格
    lines = [f"# {title}\n"]
    
    # 表头
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join(["---"] * len(columns)) + " |"
    
    lines.extend([header, separator])
    
    # 表格数据
    for item in data:
        if isinstance(item, dict):
            row_values = []
            for col in columns:
                value = item.get(col, "")
                formatted_value = _format_table_value(value)
                row_values.append(formatted_value)
            
            row = "| " + " | ".join(row_values) + " |"
            lines.append(row)
    
    return "\n".join(lines)

def _convert_to_structure(data: Any, title: str, indent_level: int = 0) -> str:
    """转换为结构化格式"""
    lines = []
    
    # 添加标题（仅在顶级调用时）
    if indent_level == 0:
        lines.append(f"# {title}\n")
    
    content = _format_structure_value(data, indent_level)
    lines.append(content)
    
    return "\n".join(lines)

def _format_structure_value(value: Any, indent_level: int = 0) -> str:
    """格式化值为结构化Markdown"""
    indent = "  " * indent_level
    
    if isinstance(value, dict):
        if not value:
            return "*(空对象)*"
        
        result = []
        for key, val in value.items():
            if isinstance(val, (dict, list)) and val:
                result.append(f"{indent}- **{key}**:")
                result.append(_format_structure_value(val, indent_level + 1))
            else:
                formatted_val = _format_simple_value(val)
                result.append(f"{indent}- **{key}**: {formatted_val}")
        return "\n".join(result)
    
    elif isinstance(value, list):
        if not value:
            return "*(空数组)*"
        
        result = []
        for i, item in enumerate(value):
            if isinstance(item, (dict, list)):
                result.append(f"{indent}{i + 1}. ")
                result.append(_format_structure_value(item, indent_level + 1))
            else:
                formatted_item = _format_simple_value(item)
                result.append(f"{indent}{i + 1}. {formatted_item}")
        return "\n".join(result)
    
    else:
        return _format_simple_value(value)

def _format_simple_value(value: Any) -> str:
    """格式化简单值"""
    if value is None:
        return "*null*"
    elif isinstance(value, bool):
        return f"**{str(value).lower()}**"
    elif isinstance(value, str):
        if not value:
            return "*(空字符串)*"
        # 处理多行字符串
        elif '\n' in value:
            return f"```\n{value}\n```"
        # 处理URL
        elif value.startswith(('http://', 'https://')):
            return f"[{value}]({value})"
        # 处理邮箱
        elif '@' in value and '.' in value.split('@')[-1]:
            return f"[{value}](mailto:{value})"
        else:
            return f"`{value}`"
    elif isinstance(value, (int, float)):
        return f"`{value}`"
    else:
        return f"`{str(value)}`"

def _format_table_value(value: Any) -> str:
    """格式化表格中的值"""
    if value is None:
        return ""
    elif isinstance(value, bool):
        return str(value).lower()
    elif isinstance(value, (dict, list)):
        # 复杂对象转为JSON字符串
        json_str = json.dumps(value, ensure_ascii=False, separators=(',', ':'))
        return json_str.replace("|", "\\|")
    elif isinstance(value, str):
        # 转义管道符和换行符
        return value.replace("|", "\\|").replace("\n", "<br>")
    else:
        return str(value).replace("|", "\\|")

def test_json_to_markdown():
    """完整的测试函数"""
    print("🧪 开始测试 JSON 转 Markdown 函数")
    print("=" * 80)
    
    # 测试用例1: 适合表格的数据
    print("\n📊 测试1: 适合表格的员工数据")
    print("-" * 40)
    table_data = [
        {"姓名": "张三", "年龄": 30, "城市": "北京", "邮箱": "zhang@example.com", "活跃": True},
        {"姓名": "李四", "年龄": 25, "城市": "上海", "邮箱": "li@example.com", "活跃": False},
        {"姓名": "王五", "年龄": 35, "城市": "广州", "邮箱": "wang@example.com", "活跃": True}
    ]
    result1 = json_to_markdown(table_data, "员工信息表")
    print(result1)
    
    # 测试用例2: 复杂嵌套数据
    print("\n🏗️ 测试2: 复杂嵌套的用户配置")
    print("-" * 40)
    complex_data = {
        "用户ID": "user_001",
        "用户名": "张三",
        "网站": "https://example.com",
        "个人配置": {
            "主题": "dark",
            "语言": "zh-CN",
            "通知": True,
            "隐私设置": {
                "公开邮箱": False,
                "显示在线状态": True
            }
        },
        "项目列表": [
            {
                "名称": "电商网站",
                "状态": "完成",
                "描述": "这是一个\n多行描述\n的项目",
                "技术栈": ["React", "Node.js", "MongoDB"]
            },
            {
                "名称": "移动应用",
                "状态": "进行中",
                "进度": 75.5
            }
        ],
        "备注": None,
        "创建时间": "2024-01-15T10:30:00Z"
    }
    result2 = json_to_markdown(complex_data, "用户详细信息")
    print(result2)
    
    # 测试用例3: JSON字符串输入
    print("\n📝 测试3: JSON字符串输入")
    print("-" * 40)
    json_string = '''{
        "产品": "智能手表",
        "价格": 1299.99,
        "库存": 50,
        "规格": {
            "屏幕": "1.4英寸AMOLED",
            "电池": "7天续航",
            "防水": "IP68"
        },
        "颜色选项": ["黑色", "白色", "玫瑰金"],
        "可用": true
    }'''
    result3 = json_to_markdown(json_string, "产品信息")
    print(result3)
    
    # 测试用例4: 强制表格格式
    print("\n📋 测试4: 强制表格格式")
    print("-" * 40)
    mixed_data = [
        {"产品": "笔记本电脑", "价格": 5999, "品牌": "Apple"},
        {"产品": "鼠标", "价格": 299, "品牌": "Logitech", "无线": True},
        {"产品": "键盘", "价格": 899, "品牌": "Cherry", "机械": True}
    ]
    result4 = json_to_markdown(mixed_data, "产品列表", force_table=True)
    print(result4)
    
    # 测试用例5: 强制结构化格式
    print("\n🌳 测试5: 强制结构化格式")
    print("-" * 40)
    result5 = json_to_markdown(table_data, "员工信息(结构化)", force_structure=True)
    print(result5)
    
    # 测试用例6: 边界情况
    print("\n⚠️ 测试6: 边界情况")
    print("-" * 40)
    
    # 空数据
    print("6.1 空列表:")
    result6_1 = json_to_markdown([], "空数据")
    print(result6_1)
    
    print("\n6.2 空字典:")
    result6_2 = json_to_markdown({}, "空对象")
    print(result6_2)
    
    print("\n6.3 无效JSON字符串:")
    result6_3 = json_to_markdown('{"invalid": json}', "错误JSON")
    print(result6_3)
    
    print("\n6.4 简单列表:")
    simple_list = ["苹果", "香蕉", "橙子"]
    result6_4 = json_to_markdown(simple_list, "水果列表")
    print(result6_4)
    
    # 测试用例7: 特殊字符处理
    print("\n🔤 测试7: 特殊字符处理")
    print("-" * 40)
    special_data = [
        {"名称": "测试|管道符", "描述": "包含\n换行符\n的文本", "链接": "https://github.com"},
        {"名称": "特殊字符", "描述": "包含 `代码` 和 **粗体**", "邮箱": "test@example.com"}
    ]
    result7 = json_to_markdown(special_data, "特殊字符测试")
    print(result7)
    
    print("\n✅ 所有测试完成!")
    print("=" * 80)

if __name__ == "__main__":
    test_json_to_markdown() 