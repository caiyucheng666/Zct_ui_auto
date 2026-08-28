# -*- coding: utf-8 -*-
"""
POM 页面对象层 —— 企业身份首页。

企业身份登录后的落地页：标题为"浙江深佳科技有限公司"，
页面展示企业 Talent HR 智能体、企业工作创作、企业知识库、招聘管理等，
导航出现"企业工作创作 / 企业知识管理"。
"""
import logging

import allure
from selenium.webdriver.common.by import By

from page.base_page import BasePage

logger = logging.getLogger(__name__)


class EnterpriseHomePage(BasePage):
    """企业身份首页（登录并选择企业身份后的落地页）。"""

    name = "企业身份首页"

    # 企业模式独有特征文案（个人模式下不出现）
    MARK = "我的企业协作入口"

    @allure.step("断言已进入企业身份首页")
    def is_enterprise_home(self):
        """校验当前页面是否为企业身份首页。

        判定规则（同时满足）：
        1. 页面出现"我的企业协作入口"（企业身份独有入口）
        2. 导航出现"企业工作创作"（企业模式导航）

        :return: True 表示判定通过，False 表示不通过
        """
        # 等待企业身份独有内容渲染完成，避免 SPA 异步导航导致断言过早
        self.wait_body_text(self.MARK)
        body = self.body_text()
        return (
            self.MARK in body
            and "企业工作创作" in body
        )
