#根据关键字参数构造用户信息（考察 kwargs）
def build_user_profile(**kwargs) -> dict:
    """Build a user profile dict using keyword arguments."""
    return kwargs

# 示例1：基础用法
profile1 = build_user_profile(name="张三", age=25, city="北京")
print(profile1)

# 示例2：灵活添加字段
profile2 = build_user_profile(email="lisi@example.com", verified=True)
print(profile2)

# 示例3：动态传参
data = {"phone": "123456", "gender": "男"}
profile3 = build_user_profile(**data)  # 解包字典
print(profile3)