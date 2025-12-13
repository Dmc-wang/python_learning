# 数据模型与类型提示

from pydantic import BaseModel, HttpUrl, field_validator
from datetime import datetime
from typing import Optional

class PageTutle(BaseModel):
    """
    Pydantic数据模型：自动校验和序列化
    知识点：类型注解、数据校验
    """
    url: HttpUrl
    title: str
    status_code: int
    error_msg: Optional[str] = None
    fetch_at: datetime = datetime.now()

    @field_validator('title')
    @classmethod
    def title_must_not_be_too_long(cls, v: str) -> str:
        """自定义校验：标题长度限制"""
        if len(v) > 500:
            return v[:500] + "..."
        return v

    @field_validator('status_code')
    @classmethod
    def status_code_must_be_valid(cls, v: int) -> int:
        """验证状态码范围"""
        if v < 0 or v > 599:
            raise ValueError("Tnvalid HTTP status code")
        return v

    class Config:
        # Pydantic配置
        json_schema_extra = {
            "example":{
                "url": "https://example.com",
                "title": "Example Domain",
                "status_code": 200
            }
        }

if __name__ == '__main__':
    # 正确数据
    good = PageTutle(url = "https://baidu.com", title = "百度", status_code = 200)
    print(good.model_dump())

    # 错误数据（会抛出ValidationError）
    try:
        bad = PageTutle(url = "not-a-url", title = "Test", status_code = 999)
    except Exception as e:
        print(f"✓ 成功捕获校验错误: {type(e).__name__}")
