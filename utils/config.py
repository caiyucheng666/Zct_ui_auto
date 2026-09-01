# -*- coding: utf-8 -*-
"""
全局配置模块。

集中管理项目用到的常量，好处是：环境或账号变化时只改这里，
页面对象和测试用例无需改动。

内容包括：
1. 被测系统地址 BASE_URL
2. 浏览器驱动 chromedriver 路径
3. 登录账号（该账号同时绑定了"个人身份"与"企业身份"）
4. 数据文件目录

账号安全：手机号与密码**不写入仓库**，通过环境变量注入。
支持在项目根目录放一个 .env 文件（KEY=VALUE 每行一条，已被 .gitignore
忽略），或直接在系统环境变量里设置。两者取其一，缺一即报错提示。
"""
import os

# 项目根目录（config.py 位于 utils/ 下，上一级即项目根）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 被测系统地址
BASE_URL = "https://zct.aisjkj.com/"

# chromedriver 路径（放在项目根目录，保证项目自包含、可移植）
CHROMEDRIVER_PATH = os.path.join(BASE_DIR, "chromedriver.exe")

# 静默执行开关：设为 1/true/yes/on 时 Chrome 以 headless 模式运行（不弹浏览器窗口），
# 供 Jenkins 定时任务使用；本地手动调试建议保持关闭以便观察界面。
HEADLESS = os.environ.get("HEADLESS", "").strip().lower() in ("1", "true", "yes", "on")


def _load_dotenv():
    """读取项目根目录 .env 文件（KEY=VALUE 每行一条，忽略空行与 # 注释）。

    仅在系统环境变量未设置时兜底填充，不覆盖已有的系统变量。
    """
    env_path = os.path.join(BASE_DIR, ".env")
    if not os.path.exists(env_path):
        return
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key, value = key.strip(), value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


_load_dotenv()


def _env(name):
    """读取环境变量；缺失时给出明确引导（避免凭据误入库后难排查）。"""
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(
            f"缺少环境变量 {name}。为避免测试凭据入库，账号改为环境变量注入，"
            f"请在项目根目录创建 .env 文件（参考 .env.example）填写后重试，"
            f"或直接设置系统环境变量 {name}。"
        )
    return value


# 登录账号（一个账号同时绑定个人身份与企业身份，登录后需二次选择身份）
ACCOUNT = {
    "mobile": _env("ZCT_PHONE"),
    "password": _env("ZCT_PASSWORD"),
}

# 登录成功后会弹出"请选择登录身份"，这里定义两种身份的入口文案
IDENTITY_PERSONAL = "个人身份登录"
IDENTITY_ENTERPRISE = "浙江深佳科技有限公司"

# 数据文件目录
DATA_DIR = os.path.join(BASE_DIR, "data")
