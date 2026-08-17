# -*- coding: utf-8 -*-
"""
一键运行入口。

执行：python run.py
1. 运行 pytest 测试（Allure 原始结果输出到 ./temps）
2. 用 Allure 命令行把 ./temps 生成 HTML 报告到 ./reports
"""
import os

import pytest

if __name__ == "__main__":
    # 运行测试（-vs 及 alluredir 参数已在 pytest.ini 中配置）
    pytest.main()

    # 生成 Allure 报告
    os.system("allure generate ./temps -o ./reports --clean")
    print("Allure 报告已生成：./reports/index.html")
