# -*- coding: utf-8 -*-
"""
POM 页面对象层 —— 工作创作（功能列表页）。

个人身份登录后，顶部导航「工作创作」进入本页，页面以卡片形式
列出 8 个创作/申报功能入口：

    职称申报：政策解读 / 项目方向挖掘 / 立项报告生成 / 项目方案生成
    专利工具：技术交底书生成 / 权利要求书生成 / 专利说明书生成 / 查找相似专利

本类负责：从个人首页进入工作创作页、按名称点击功能卡片进入对应功能页。
"""
import logging
import time

import allure
from selenium.webdriver.common.by import By

from page.base_page import BasePage

logger = logging.getLogger(__name__)


class WorkCreationPage(BasePage):
    """工作创作页：8 个创作/申报功能的入口列表。"""

    name = "工作创作页"

    # 顶部导航入口（个人身份）
    nav_entry = (
        By.XPATH,
        '//button[contains(@class,"header-nav-link") and normalize-space(.)="工作创作"]',
    )
    # 工作创作页独有特征文案（用于等待页面加载完成）
    MARK = "职称申报"

    def _feature_card(self, name):
        """功能卡片标题（h3）定位。"""
        return (By.XPATH, f'//h3[normalize-space(.)="{name}"]')

    @allure.step("进入工作创作页")
    def enter(self):
        """从个人身份首页点击顶部导航，进入工作创作页。

        :return: self（便于链式调用）
        """
        self.click(self.nav_entry)
        self.wait_body_text(self.MARK)
        # Vue SPA 异步挂载：功能卡片虽已可见，但点击事件可能尚未绑定，稍等片刻再点
        time.sleep(2)
        return self

    @allure.step("打开功能模块")
    def open_feature(self, case, retries=6):
        """点击某个功能卡片，进入对应功能页。

        Vue SPA 异步挂载，卡片点击事件绑定存在延迟，首次点击可能不生效，
        故点击后校验是否已离开工作创作页，未跳转则重试（最多 retries 次）。

        :param case: 功能数据字典（含 name 等字段，来自 data/work_creation.yaml）
        :param retries: 最大重试次数
        :return: WorkFeaturePage 实例
        """
        name = case["name"]
        card = self._feature_card(name)
        for _ in range(retries):
            try:
                self.click(card)
            except Exception:
                pass
            time.sleep(1)
            if "workcreation" not in self.driver.current_url.lower():
                break
        from page.work_feature_page import WorkFeaturePage
        return WorkFeaturePage(self.driver, case)

    @allure.step("判断功能入口是否展示")
    def is_feature_visible(self, name):
        """判断某个功能卡片是否在页面可见。"""
        return self.is_exist(self._feature_card(name))
