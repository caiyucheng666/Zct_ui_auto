# -*- coding: utf-8 -*-
"""
登录功能测试用例（数据驱动：数据来自 data/login_data.yaml）。

覆盖场景：
1. 正确账号密码登录 → 弹出"请选择登录身份"弹窗
2. 密码错误 → toast 提示"登录失败，账号密码不正确"
3. 密码为空 → 登录按钮禁用（前端校验）
4. 未登录访问受保护页面 → 跳回首页并自动弹出登录弹窗（看不到受保护内容）
5. 退出登录后登录态失效 → 再访问受保护页面被引导登录
"""
import allure
import pytest
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils.config import ACCOUNT, BASE_URL
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
        params.append(pytest.param(
            d,
            id = d["name"]
        ))
    return params


@allure.epic("职策佳平台")
@allure.feature("登录功能")
class TestLogin:
    """登录功能测试集。"""

    @allure.story("密码登录成功")
    @pytest.mark.login
    @pytest.mark.parametrize(
        "case",
        _with_account(_login_data["login_success"], real_password=True),
    )
    def test_login_success(self, driver, screenshot_on_end, case:dict):
        """正确账号密码登录后，应弹出身份选择弹窗。"""
        page = LoginPage(driver).open().login_password(case["mobile"], case["password"])

        # 断言：弹出"请选择登录身份"弹窗，且标题正确
        assert page.identity_dialog_visible(), "登录成功后应弹出身份选择弹窗"
        assert page.get_identity_title() == case["expect_title"]

    @allure.story("密码登录失败")
    @pytest.mark.login
    @pytest.mark.parametrize(
        "case",
        _with_account(_login_data["login_fail"]),
    )
    def test_login_fail(self, driver, screenshot_on_end, case:dict):
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

    @allure.story("未登录访问受保护页面")
    @allure.title("未登录直接访问受保护页面应引导登录")
    @pytest.mark.login
    def test_unauth_access_protected_page(self, driver, screenshot_on_end):
        """未登录直接访问受保护页面（企业工作创作），应被引导到登录，看不到受保护内容。"""
        page = LoginPage(driver)
        driver.get(BASE_URL + "/company/enterprise/WorkCreation")
        # 站点行为：未登录访问受保护路由 → 跳回首页并自动弹出登录弹窗，
        # 以「手机号输入框出现」作为登录弹窗已弹出的判定锚点
        WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located(page.phone_input)
        )
        body = page.body_text()
        assert "职称申报" not in body, "未登录不应看到受保护的工作创作内容"
        assert any(
            el.is_displayed() for el in driver.find_elements(*page.login_entry)
        ), "未登录访问受保护页应出现登录入口"

    @allure.story("退出后登录态失效")
    @allure.title("退出登录后访问受保护页面应引导登录")
    @pytest.mark.login
    def test_logout_invalidates_session(self, driver, screenshot_on_end):
        """登录 → 退出登录 → 再访问受保护页面，应被引导到登录（登录态已失效）。"""
        home = (
            LoginPage(driver)
            .open()
            .login_password(ACCOUNT["mobile"], ACCOUNT["password"])
            .select_personal()
        )
        # 退出登录：点右上角用户菜单 → 点「退出登录」（cookie 中的 token 被清除）
        home.logout()
        # 退出后再访问受保护页面，应再次被引导登录
        driver.get(BASE_URL + "/company/enterprise/WorkCreation")
        WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located(LoginPage.phone_input)
        )
        body = home.body_text()
        assert "职称申报" not in body, "退出后不应看到受保护的工作创作内容"
        assert any(
            el.is_displayed() for el in driver.find_elements(*LoginPage.login_entry)
        ), "退出后应回到未登录态"
