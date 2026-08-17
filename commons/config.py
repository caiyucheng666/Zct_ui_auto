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
"""
import os

# 项目根目录（config.py 位于 commons/ 下，上一级即项目根）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 被测系统地址
BASE_URL = "https://zct.aisjkj.com/"

# chromedriver 路径（放在项目根目录，保证项目自包含、可移植）
CHROMEDRIVER_PATH = os.path.join(BASE_DIR, "chromedriver.exe")

# 登录账号（一个账号同时绑定个人身份与企业身份，登录后需二次选择身份）
ACCOUNT = {
    "mobile": "13142886588",
    "password": "cyc02918",
}

# 登录成功后会弹出"请选择登录身份"，这里定义两种身份的入口文案
IDENTITY_PERSONAL = "个人身份登录"
IDENTITY_ENTERPRISE = "浙江深佳科技有限公司"

# 数据文件目录
DATA_DIR = os.path.join(BASE_DIR, "data")
