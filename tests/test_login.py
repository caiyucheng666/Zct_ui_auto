# -*- coding: utf-8 -*-
"""
登录功能测试用例（数据驱动：数据来自 data/login_data.yaml）。

覆盖场景：
1. 正确账号密码登录 → 弹出"请选择登录身份"弹窗
2. 密码错误 → toast 提示"登录失败，账号密码不正确"
3. 密码为空 → 登录按钮禁用（前端校验）
"""
import allure
import pytest

from utils.config import ACCOUNT
from page.login_page import LoginPage
from utils.read_yaml import read_yaml

# 从 YAML 读取登录用例数据
_login_data = read_yaml("login_data.yaml")


def _with_account(cases, real_password=False):
    """把 YAML 用例与账号数据合并：手机号一律注入 ACCOUNT（环境变量）；
    登录成功场景的密码也用真实账号密码，其余场景保留 YAML 里的错误/空密码。
    """
    params = []
    for c in cases:
        d = dict(c)
        d["mobile"] = ACCOUNT["mobile"]
        if real_password:
            d["password"] = ACCOUNT["password"]
        params.append(pytest.param(d, id=d["name"]))
    return params


@allure.epic("职策佳平台")
@allure.feature("登录功能")
class TestLogin:
    """登录功能测试集。"""

    @allure.story("密码登录成功")
    @pytest.mark.login
    @pytest.mark.skip(reason="临时跳过，待补充新的用例")
    @pytest.mark.parametrize(
        "case",
        _with_account(_login_data["login_success"], real_password=True),
    )
    def test_login_success(self, driver, screenshot_on_end, case):
        """正确账号密码登录后，应弹出身份选择弹窗。"""
        page = LoginPage(driver).open().login_password(case["mobile"], case["password"])

        # 断言：弹出"请选择登录身份"弹窗，且标题正确
        assert page.identity_dialog_visible(), "登录成功后应弹出身份选择弹窗"
        assert page.get_identity_title() == case["expect_title"]

    @allure.story("密码登录失败")
    @pytest.mark.login
    @pytest.mark.skip(reason="临时跳过，待补充新的用例")
    @pytest.mark.parametrize(
        "case",
        _with_account(_login_data["login_fail"]),
    )
    def test_login_fail(self, driver, screenshot_on_end, case):
        """密码错误 / 密码为空时的校验提示。"""
        page = LoginPage(driver).open()

        if case.get("expect_toast"):
            # 密码错误：填写并点击登录，断言 toast 提示文案
            page.login_password(case["mobile"], case["password"])
            assert page.get_login_toast() == case["expect_toast"]
        elif case.get("expect_disabled"):
            # 密码为空：只填写表单不点击，断言登录按钮禁用
            page.fill_form(case["mobile"], case["password"])
            assert page.submit_disabled(), "密码为空时登录按钮应处于禁用状态"
