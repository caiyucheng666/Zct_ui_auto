# -*- coding: utf-8 -*-
"""
企业身份测试用例。

场景：账号密码登录 → 选择企业身份（浙江深佳科技有限公司）→ 进入企业身份首页。
"""
import allure
import pytest

from commons.config import ACCOUNT
from commons.login_page import LoginPage


@allure.epic("职策佳平台")
@allure.feature("身份登录")
@allure.story("企业身份登录")
class TestEnterprise:
    """企业身份相关测试集。"""

    @pytest.mark.enterprise
    @allure.title("选择企业身份登录进入企业中心")
    @pytest.mark.skip(reason="临时跳过，待补充新的用例")
    def test_enterprise_identity_login(self, driver, screenshot_on_end):
        """登录后选择企业身份，应进入企业身份首页。"""
        home = (
            LoginPage(driver)
            .open()
            .login_password(ACCOUNT["mobile"], ACCOUNT["password"])
            .select_enterprise()
        )

        assert home.is_enterprise_home(), "应进入企业身份首页"
