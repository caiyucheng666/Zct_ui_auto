# -*- coding: utf-8 -*-
"""
pytest 公共夹具（fixture）定义。

1. driver           —— 每个用例一个全新的浏览器（保证用例间隔离）
2. screenshot_on_end—— 用例结束时自动截图并附加到 Allure 报告

用法：测试用例函数签名里声明 driver、screenshot_on_end 即可自动注入。
"""
import allure
import pytest
from allure_commons.types import AttachmentType
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from commons.config import CHROMEDRIVER_PATH


@pytest.fixture(scope="function")
def driver():
    """启动 Chrome 浏览器，用例结束后自动关闭。

    每个用例独立一个浏览器实例，互不影响，保证用例可重复执行。
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    # 规避网站对自动化浏览器的检测
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=options)
    driver.implicitly_wait(3)

    yield driver

    driver.quit()


@pytest.fixture(scope="function")
def screenshot_on_end(driver):
    """用例结束时自动截图，附加到 Allure 报告，便于失败排查。"""
    yield
    try:
        allure.attach(
            driver.get_screenshot_as_png(),
            name="用例结束截图",
            attachment_type=AttachmentType.PNG,
        )
    except Exception as e:
        print(f"截图失败: {e}")
