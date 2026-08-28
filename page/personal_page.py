# -*- coding: utf-8 -*-
"""
POM 页面对象层 —— 个人身份首页。

个人身份登录后的落地页：标题为"职策佳官网 - 职业评测与申报辅助平台"，
URL 带 siteMode=c，页面展示职业评测、政策雷达、申报档案等个人服务。
"""
import logging
from email.quoprimime import body_check

import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from page.base_page import BasePage

logger = logging.getLogger(__name__)


class PersonalHomePage(BasePage):
    """个人身份首页（登录并选择"个人身份登录"后的落地页）。"""

    name = "个人身份首页"

    # 个人模式 URL 标识
    SITE_MODE = "siteMode=c"
    # 个人模式独有特征文案（企业模式下不出现）
    MARK = "职业评测"

    @allure.step("断言已进入个人身份首页")
    def is_personal_home(self):
        """校验当前页面是否为个人身份首页。

        判定规则（同时满足）：
        1. URL 携带 siteMode=c（个人模式）
        2. 页面出现"职业评测"（个人身份独有服务入口）

        :return: True 表示判定通过，False 表示不通过
        """
        # 等待个人身份独有内容渲染完成，避免 SPA 异步导航导致断言过早
        self.wait_body_text(self.MARK)
        body = self.body_text()
        return (
            self.SITE_MODE in self.driver.current_url
            and self.MARK in body
        )

    # 右上角用户菜单触发点（头像+用户名区域；含头像 img，区别于「职策点充值」入口）
    _user_trigger = (
        By.XPATH,

        '//div[contains(@class,"cursor-pointer") and contains(@class,"rounded-lg") '
        'and .//img and contains(@class,"space-x-2")]',
    )
    # 用户菜单里的「退出登录」按钮
    _logout_btn = (By.XPATH, '//button[normalize-space(.)="退出登录"]')

    @allure.step("退出登录")
    def logout(self):
        """退出登录：点击右上角用户菜单 → 点击「退出登录」。

        退出后 cookie 中的 token 等被清除（isLoggedIn=no），
        右上角重新出现「登录/注册」入口（据此判断登录态已失效）。
        """
        self.click_js(self._user_trigger)
        self.wait.until(EC.visibility_of_element_located(self._logout_btn))
        self.click_js(self._logout_btn)
        self.wait.until(
            lambda d: any(
                el.is_displayed()
                for el in d.find_elements(
                    By.XPATH, '//button[contains(@class,"login-register-btn")]'
                )
            )
        )
        return self
