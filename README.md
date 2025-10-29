# 中国身份证验证系统

基于图像处理的中国身份证号码自动识别与验证系统。

## 功能特性

- **图像上传**: 支持多种图像格式（PNG、JPG、JPEG、BMP、TIFF）
- **OCR 处理**: 双重 OCR 支持（Pytesseract + EasyOCR 备用）
- **图像预处理**: 高级 OpenCV 预处理（灰度化、降噪、阈值处理）
- **身份证号提取**: 自动提取 18 位中国身份证号码
- **验证功能**: 完整的验证包括：
  - 长度检查（18位字符）
  - 地址码验证（前6位）
  - 出生日期验证（YYYYMMDD 格式）
  - 顺序码验证（3位）
  - 校验码验证（中国身份证算法）
- **结果导出**: 将结果保存到带时间戳的 CSV 文件
- **用户友好界面**: 简洁的 Tkinter 界面，带有可视化反馈

## 系统要求

### 系统需求

- Python 3.7+
- Tesseract OCR（用于 pytesseract）

### Python 依赖

```bash
pip install -r requirements.txt
```

所需包：
- opencv-python
- pytesseract
- Pillow
- easyocr（可选，用作备用）

### 安装 Tesseract OCR

#### Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-chi-sim  # 简体中文
```

#### macOS:
```bash
brew install tesseract
brew install tesseract-lang  # 中文支持
```

#### Windows:
1. 从以下地址下载安装程序：https://github.com/UB-Mannheim/tesseract/wiki
2. 安装并添加到 PATH
3. 如需要，在代码中设置 tesseract 路径：
   ```python
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```

## 安装步骤

1. 克隆或下载本仓库

2. 安装 Python 依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. 安装 Tesseract OCR（见上文）

4. 运行应用程序：
   ```bash
   python id_card_verifier.py
   ```

## 使用方法

1. **上传图像**: 点击"上传身份证图片"选择身份证图像

2. **识别并验证**: 点击"识别并验证"处理图像：
   - 使用 OpenCV 预处理图像
   - OCR 从图像中提取文本
   - 使用正则表达式提取 18 位身份证号码
   - 使用中国身份证验证算法验证号码

3. **查看结果**:
   - 提取的身份证号码显示在顶部文本框中
   - 验证结果显示验证状态
   - 状态栏显示当前操作状态

4. **保存结果**: 点击"保存结果"导出到 `results.csv`

5. **清空**: 点击"清空"重置界面

## 中国身份证格式

中国身份证号码为 18 位字符：
- **第 1-6 位**: 地址码（行政区划）
- **第 7-14 位**: 出生日期（YYYYMMDD）
- **第 15-17 位**: 顺序码（奇数=男，偶数=女）
- **第 18 位**: 校验码（使用加权算法计算）

### 校验码算法

最后一位按以下方式计算：

1. 将前 17 位数字分别乘以权重：
   ```
   [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
   ```

2. 对所有乘积求和

3. 对 11 取模

4. 将结果映射到校验码：
   ```
   ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
   ```

## 示例身份证号码

用于测试目的（这些是带有正确校验码的有效测试身份证号）：

**有效格式：**
- 11010519491231002X（北京，1949年）
- 440524198001010013（广东，1980年）
- 510102198901010017（四川，1989年）

## 文件结构

```
ID Card Numbers Verification System/
│
├── id_card_verifier.py      # 主应用程序
├── requirements.txt          # Python 依赖
├── README.md                 # 本文件
└── results.csv              # 保存结果后生成
```

## 故障排除

### OCR 无法工作

**问题**: "没有可用的 OCR 库"
- **解决方案**: 安装 pytesseract 或 easyocr
  ```bash
  pip install pytesseract easyocr
  ```

**问题**: 找不到 Tesseract
- **解决方案**: 安装 Tesseract OCR 并确保其在 PATH 中

### OCR 准确度低

**问题**: 身份证号码提取不正确
- **解决方案**:
  - 确保图像清晰且光线充足
  - 身份证号码应清晰可见
  - 尝试不同的图像格式
  - 在代码中调整预处理参数

### 图像无法显示

**问题**: 图像上传成功但未显示
- **解决方案**: 检查图像格式是否受支持
- 确保已安装 Pillow：`pip install Pillow`

## 技术细节

### 图像预处理流程

1. **灰度转换**: 简化为单通道
2. **降噪**: 使用 fastNlMeansDenoising 去除噪声
3. **自适应阈值处理**: 二值化转换以获得更好的 OCR 效果

### OCR 策略

- **主要**: Pytesseract（更快，适合清晰图像）
- **备用**: EasyOCR（更准确，较慢）
- 针对数字和 'X' 字符优化配置

### 验证逻辑

应用程序执行全面验证：
1. 格式检查（18位字符）
2. 地址码验证（数字，6位）
3. 日期验证（有效的 YYYYMMDD）
4. 顺序码检查（数字，3位）
5. 校验码验证（加权算法）

## CSV 输出格式

`results.csv` 文件包含：
- `filename`: 上传图像的名称
- `extracted_id`: 提取的身份证号码
- `verification_status`: 有效/无效
- `timestamp`: 执行验证的时间

## 许可证

本项目仅用于教育目的。

## 贡献

欢迎提交问题或拉取请求以进行改进。
