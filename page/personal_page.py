# -*- coding: utf-8 -*-
"""
POM 页面对象层 —— 个人身份首页。

个人身份登录后的落地页：标题为"职策佳官网 - 职业评测与申报辅助平台"，
URL 带 siteMode=c，页面展示职业评测、政策雷达、申报档案等个人服务。
"""
import logging

import allure
from selenium.webdriver.common.by import By

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

        判定规则（三者同时满足）：
        1. 页面出现登录用户名"蔡雨承"（说明已登录成功）
        2. URL 携带 siteMode=c（个人模式）
        3. 页面出现"职业评测"（个人身份独有服务入口）

        :return: True 表示判定通过，False 表示不通过
        """
        # 先等待页面加载出用户名，避免断言过早
        self.wait_body_text("蔡雨承")
        body = self.body_text()
        return (
            self.SITE_MODE in self.driver.current_url
            and self.MARK in body
            and "蔡雨承" in body
        )
