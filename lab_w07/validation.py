# Kim Duy Vương
# 20237410
"""Kiểm tra đầu vào dùng chung, không phụ thuộc loại thiết bị."""


def require_text(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} phải là chuỗi không rỗng.")
    return value.strip()


def require_percentage(value: int, field_name: str) -> int:
    # bool là lớp con của int trong Python, nhưng không phải mức pin hợp lệ.
    if type(value) is not int or not 0 <= value <= 100:
        raise ValueError(f"{field_name} phải là số nguyên từ 0 đến 100.")
    return value
