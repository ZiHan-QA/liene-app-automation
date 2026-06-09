# Liene Photo APP UI 自动化框架

## 目录结构
```
liene-app-automation/
├── capabilities/       # 设备能力配置
│   ├── android.yaml
│   └── ios.yaml
├── pages/              # Page Object 层
│   ├── base_page.py    # 基类，封装常用操作
│   └── home_page.py    # 首页
├── tests/
│   ├── smoke/          # P0 冒烟用例
│   └── regression/     # 回归用例
├── ai_assert/          # AI 视觉断言
│   ├── vision_client.py
│   └── prompts/
├── reports/            # Allure 报告输出
├── conftest.py         # pytest fixture
├── pytest.ini
└── requirements.txt
```

## 使用步骤

### 1. 安装依赖
pip3 install -r requirements.txt

### 2. 启动 Appium Server（另开终端）
appium

### 3. 运行冒烟测试
pytest -m smoke

### 4. 运行回归测试
pytest -m regression

### 5. 生成 Allure 报告
pytest -m smoke --alluredir=reports/allure-results
allure serve reports/allure-results

## 配置说明
- capabilities/android.yaml：修改 udid 为你的设备序列号（多设备时必填）
- capabilities/ios.yaml：修改 bundle_id、udid、xcode_org_id
- ai_assert/vision_client.py：设置环境变量 DEEPSEEK_API_KEY
