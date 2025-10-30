# 아이콘 제거 스크립트

파일이 너무 커서 모든 아이콘을 자동으로 제거하기 어렵습니다.

## 제거해야 할 아이콘

스크립트로 일괄 제거하거나, Python 코드로 처리할 수 있습니다.

```python
import re

with open('src/web/streamlit_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# emoji 제거 (유니코드 범위)
content = re.sub(r'[^\w\s\[\]().,;:\'"<>={}]+', lambda m: '' if ord(m.group()) > 126 else m.group(), content)

with open('src/web/streamlit_app.py', 'w', encoding='utf-8') as f:
    f.write(content)
```

또는 수동으로 주요 섹션만 수정하는 것이 더 안전할 수 있습니다.


