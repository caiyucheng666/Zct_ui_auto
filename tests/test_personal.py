# -*- coding: utf-8 -*-
"""
个人身份测试用例。

场景：账号密码登录 → 选择"个人身份登录" → 进入个人身份首页。
"""
import allure
import pytest

from utils.config import ACCOUNT
from page.login_page import LoginPage


@allure.epic("职策佳平台")
@allure.feature("身份登录")
@allure.story("个人身份登录")
class TestPersonal:
    """个人身份相关测试集。"""

    @pytest.mark.personal
    @allure.title("选择个人身份登录进入个人中心")
    def test_personal_identity_login(self, driver, screenshot_on_end):
        """登录后选择个人身份，应进入个人身份首页。"""
        home = (
            LoginPage(driver)
            .open()
            .login_password(ACCOUNT["mobile"], ACCOUNT["password"])
            .select_personal()
        )

        assert home.is_personal_home(), "应进入个人身份首页"
