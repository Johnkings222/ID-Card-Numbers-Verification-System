# 快速入门指南

## 安装

1. **安装系统依赖（Tesseract OCR）**:

   **Ubuntu/Debian:**
   ```bash
   sudo apt-get update
   sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim
   ```

   **macOS:**
   ```bash
   brew install tesseract tesseract-lang
   ```

2. **安装 Python 依赖**:
   ```bash
   pip install -r requirements.txt
   ```

3. **运行应用程序**:
   ```bash
   python id_card_verifier.py
   ```

## 测试验证逻辑

运行测试脚本以验证一切正常工作：

```bash
python test_verifier.py
```

预期输出：所有测试通过！

## 使用应用程序

### 步骤 1：上传图像
- 点击"上传身份证图片"
- 选择一张中国身份证图像（PNG、JPG 等）
- 图像将显示在左侧

### 步骤 2：识别并验证
- 点击"识别并验证"
- 观察状态栏显示进度：
  - "处理中..."
  - "预处理图片中..."
  - "提取文本中..."
  - "验证身份证号码..."
- 结果显示在右侧

### 步骤 3：查看结果
系统显示：
- **提取的身份证号码**：图像中找到的 18 位身份证号
- **验证结果**：
  - 身份证号码有效（如果所有检查都通过）
  - 身份证号码无效（附带具体原因）
- **状态栏**：显示当前状态

### 步骤 4：保存结果（可选）
- 点击"保存结果"
- 数据将追加到 `results.csv`
- 包括：文件名、身份证号码、状态、时间戳

### 步骤 5：清空（重新开始）
- 点击"清空"
- 重置整个界面
- 准备处理下一张身份证

## 测试身份证号码

在没有实际身份证图像的情况下，可以使用这些进行测试：

**有效身份证号：**
- `11010519491231002X`（北京，1949年）
- `440524198001010013`（广东，1980年）
- `510102198901010017`（四川，1989年）

**无效身份证号（用于测试错误处理）：**
- `11010519491231002Y`（校验码错误）
- `110105194913310020`（月份无效：13）
- `11010519491232002X`（日期无效：32）

## 创建测试图像

为 OCR 创建测试图像：

1. 创建一个带有身份证号文本的简单图像
2. 使用清晰、可读的字体（例如 Arial，20-24pt）
3. 白色背景、黑色文字效果最好
4. 仅包含 18 位数字

使用 ImageMagick 的示例：
```bash
convert -size 600x100 xc:white -font Arial -pointsize 32 \
  -fill black -gravity center -annotate +0+0 "11010519491231002X" \
  test_id.png
```

或使用 Python PIL：
```python
from PIL import Image, ImageDraw, ImageFont

img = Image.new('RGB', (600, 100), color='white')
draw = ImageDraw.ImageDraw(img)
draw.text((50, 30), "11010519491231002X", fill='black')
img.save('test_id.png')
```

## 故障排除

### 没有可用的 OCR 库
```bash
pip install pytesseract easyocr
```

### 找不到 Tesseract
```bash
# 检查是否已安装
tesseract --version

# 如果未找到，安装它（Ubuntu）
sudo apt-get install tesseract-ocr
```

### OCR 准确度低
- 确保图像清晰且分辨率高
- 身份证号码应清晰可见
- 光线充足，无眩光
- 正面拍摄（不倾斜）

### GUI 未出现
- 确保已安装 tkinter（通常随 Python 一起提供）
- 在 Linux 上，您可能需要：`sudo apt-get install python3-tk`

## 验证什么？

系统检查：

1. **长度**：必须恰好为 18 位字符
2. **地址码**：前 6 位（必须为数字）
3. **出生日期**：第 7-14 位（有效的 YYYYMMDD 格式）
4. **顺序码**：第 15-17 位（必须为数字）
5. **校验码**：第 18 位（使用加权算法计算）

所有检查都必须通过才能获得有效结果。

## 输出文件

- `results.csv` - 保存结果时创建
- 包含：文件名、提取的身份证号、验证状态、时间戳

## 需要帮助？

请参阅完整的 [README.md](README.md) 了解详细文档。
