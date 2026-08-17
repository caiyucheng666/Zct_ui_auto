# -*- coding: utf-8 -*-
"""
企业工作创作功能测试用例（数据驱动：数据来自 data/work_creation.yaml）。

覆盖场景（8 个功能模块）：
1. 工作创作页入口 —— 列出全部 8 个功能入口
2. 功能页导航    —— 点击卡片进入对应功能页（URL + 标题断言）
3. 必填校验      —— 空表单提交出现校验提示（alert）
4. 完整生成流程  —— 填写表单 → 提交 → 等待 AI 生成完成 → 断言结果内容（消耗职策点）
"""
import allure
import pytest

from commons.config import ACCOUNT
from commons.login_page import LoginPage
from commons.read_yaml import read_yaml
from commons.work_creation_page import WorkCreationPage

# 从 YAML 读取工作创作用例数据
_data = read_yaml("work_creation.yaml")
feature_names = _data["feature_names"]
features = _data["features"]


def _full_generation_params():
    """构造完整生成用例的参数列表。

    - 带 skip_reason 的功能：打 skip（已验证通过，日常不重复消耗职策点）
    - 带 xfail_reason 的功能：打 xfail（表单填写后仍不触发，待人工排查）
    """
    params = []
    for c in features:
        marks = []
        if c.get("skip_reason"):
            marks.append(pytest.mark.skip(reason=c["skip_reason"]))
        if c.get("xfail_reason"):
            marks.append(pytest.mark.xfail(reason=c["xfail_reason"], strict=False))
        params.append(pytest.param(c, id=c["name"], marks=marks))
    return params


def _login_to_work_creation(driver):
    """登录个人身份并进入工作创作页。

    :param driver: 浏览器驱动
    :return: WorkCreationPage 实例
    """
    (
        LoginPage(driver)
        .open()
        .login_password(ACCOUNT["mobile"], ACCOUNT["password"])
        .select_personal()
    )
    return WorkCreationPage(driver).enter()


@allure.epic("职策佳平台")
@allure.feature("企业工作创作")
@pytest.mark.work_creation
class TestWorkCreation:
    """企业工作创作功能测试集。"""

    @allure.story("工作创作页入口")
    @allure.title("工作创作页展示全部功能入口")
    def test_work_creation_lists_all_features(self, driver, screenshot_on_end):
        """工作创作页应列出全部 8 个功能入口。"""
        page = _login_to_work_creation(driver)
        body = page.body_text()
        for name in feature_names:
            assert name in body, f"工作创作页应展示功能入口：{name}"

    @allure.story("功能页导航")
    @allure.title("进入功能页：{case[name]}")
    @pytest.mark.parametrize("case", features, ids=lambda c: c["name"])
    def test_feature_navigation(self, driver, screenshot_on_end, case):
        """点击功能卡片后，应跳转到对应功能页（URL + 标题）。"""
        page = _login_to_work_creation(driver).open_feature(case)

        assert case["url_keyword"] in driver.current_url, (
            f"应跳转到「{case['name']}」页，实际 URL：{driver.current_url}"
        )
        assert case["name"] in page.body_text(), f"页面应展示标题「{case['name']}」"

    @allure.story("必填校验")
    @allure.title("空表单提交校验：{case[name]}")
    @pytest.mark.parametrize("case", features, ids=lambda c: c["name"])
    def test_feature_required_validation(self, driver, screenshot_on_end, case):
        """空表单直接提交，应出现校验提示（alert）且不进入生成页。"""
        page = _login_to_work_creation(driver).open_feature(case)
        page.click_submit(case["submit_button"])

        assert page.has_validation_toast(), f"「{case['name']}」空提交应出现校验提示"

    @allure.story("完整生成流程")
    @allure.title("完整生成：{case[name]}")
    @pytest.mark.parametrize("case", _full_generation_params(), ids=lambda c: c["name"])
    def test_feature_full_generation(self, driver, screenshot_on_end, case):
        """填写表单 → 提交 → 等待 AI 生成完成 → 断言结果内容（消耗职策点）。"""
        page = _login_to_work_creation(driver).open_feature(case)

        # 1. 按数据配置填写表单
        page.fill_form(case.get("fill"))
        # 2. 提交（政策解读选文件即触发，无需再点提交）
        if not case.get("no_submit_on_generate"):
            page.click_submit(case["submit_button"])
        # 2.1 多步向导（如立项报告）：填写第二步并再次提交
        step2 = (case.get("fill") or {}).get("step2")
        if step2:
            page.fill_form(step2)
            page.click_submit(case["submit_button"])

        # 3. 等待生成完成（"生成中"消失 且 进入详情页）
        assert page.wait_generated(), (
            f"「{case['name']}」未在预期时间内生成完成，当前 URL：{driver.current_url}"
        )

        # 4. 断言结果内容
        assert page.has_text(case["result_hint"]), (
            f"「{case['name']}」生成结果中应包含「{case['result_hint']}」"
        )
