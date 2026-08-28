# -*- coding: utf-8 -*-
"""
POM 元素的底层基类（Base Page）。

作用：为各个页面对象（Page Object）提供统一的基础操作能力，
页面对象继承本类后即可复用这些方法，避免重复编写 Selenium 定位/交互代码。

提供的通用能力：
1. 接收 driver 对象（构造时传入）
2. 实例化显式等待对象 WebDriverWait
3. 元素定位（带显式等待）
4. 常见交互：点击、输入、获取文本
5. 强制操作：JS 点击（绕过可见/可点击校验）
6. 元素存在性 / 页面文本断言辅助
"""
import logging
from asyncio import timeout

import allure
from allure_commons.types import AttachmentType
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

logger = logging.getLogger(__name__)


class BasePage:
    """所有页面对象的基类，封装通用的元素定位与交互方法。"""

    name = "基类"  # 类名标识，便于日志/报告区分

    def __init__(self, driver):
        """构造方法：接收 driver 并初始化显式等待对象。

        :param driver: 已启动的浏览器驱动（WebDriver 实例）
        """
        self.driver: WebDriver = driver        # 保存浏览器驱动，供后续定位/操作使用
        self.wait = WebDriverWait(driver, 10)  # 显式等待对象，最长等 10 秒
        # 实例化页面对象时，往测试报告里"附加"一张当前页面截图
        allure.attach(
            driver.get_screenshot_as_png(),
            name="POM实例化:" + self.name,
            attachment_type=AttachmentType.PNG,
        )
        logger.info(f"POM实例化: {self.driver.current_url}")

    @allure.step("元素定位")
    def find_element(self, locator):
        """定位单个元素（自带显式等待，直到元素可见）。

        :param locator: 定位元组，形如 (By.XPATH, '//div')
        :return: 定位到的 WebElement
        """
        logger.info(f"正在定位元素: {locator}")
        el = self.wait.until(EC.visibility_of_element_located(locator))
        logger.info(f"找到元素: {el.tag_name}: {str(el.text)[:20]}")
        return el

    @allure.step("点击元素")
    def click(self, locator):
        """点击元素（自带显式等待，直到元素可见且可点击）。

        :param locator: 定位元组，形如 (By.XPATH, '//button')
        """
        logger.info(f"正在点击元素: {locator}")
        el = self.wait.until(EC.element_to_be_clickable(locator))
        el.click()

    @allure.step("强制点击")
    def click_js(self, locator):
        """强制点击：跳过显式等待与可点击校验，用 JS 硬点。

        适用于被遮挡、隐藏或常规 click 点击不到的元素。
        :param locator: 定位元组，形如 (By.XPATH, '//button')
        """
        logger.info(f"正在强制点击元素: {locator}")
        el = self.driver.find_element(*locator)
        self.driver.execute_script("arguments[0].click()", el)

    @allure.step("输入内容")
    def send_keys(self, locator, text):
        """向输入框输入内容（先清空再输入）。

        :param locator: 定位元组，形如 (By.XPATH, '//input')
        :param text: 要输入的内容
        """
        logger.info(f"正在输入内容: {locator}, {text}")
        el = self.find_element(locator)
        el.clear()              # 先清空输入框原有内容
        el.send_keys(text)      # 再输入新内容

    @allure.step("获取文本")
    def get_text(self, locator):
        """获取元素的可见文本（自带显式等待，直到元素可见）。

        :param locator: 定位元组
        :return: 元素文本内容
        """
        el = self.find_element(locator)
        return el.text

    @allure.step("判断元素是否存在")
    def is_exist(self, locator, timeout=5):
        """判断元素是否在指定时间内出现（可见）。

        :param locator: 定位元组
        :param timeout: 最长等待秒数
        :return: True 表示元素出现，False 表示超时未出现
        """
        try:
            # wait  = WebDriverWait(self.driver, timeout)
            # wait.until(EC.visibility_of_element_located(locator))
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except Exception:
            return False

    @allure.step("等待页面出现指定文本")
    def wait_body_text(self, text, timeout=10):
        """等待页面 body 中出现指定文本（常用于等待登录后页面加载完成）。

        :param text: 目标文本
        :param timeout: 最长等待秒数
        :return: self（便于链式调用）
        """
        WebDriverWait(self.driver, timeout).until(
            # 找<body>
            lambda d: text in d.find_element(By.TAG_NAME, "body").text
        )

    @allure.step("获取页面正文文本")
    def body_text(self):
        """返回当前页面 body 的完整可见文本。"""
        return self.driver.find_element(By.TAG_NAME, "body").text
