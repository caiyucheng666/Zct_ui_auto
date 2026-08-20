# -*- coding: utf-8 -*-
"""
POM 核心层 —— 登录页页面对象。

从内容上看：与真实登录页保持一致（登录入口、账号密码输入框、登录按钮、
身份选择弹窗、错误提示 toast）。

从结构上看：承上启下 —— 继承 BasePage，为测试用例提供自动化操作；
"选择身份"后返回对应的首页页面对象（个人/企业），形成页面流转。
"""
import logging
import time

import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from page.base_page import BasePage
from utils.config import BASE_URL, IDENTITY_ENTERPRISE, IDENTITY_PERSONAL

logger = logging.getLogger(__name__)


class LoginPage(BasePage):
    """登录页：账号密码登录 + 身份二次选择。"""

    name = "登录页"

    # 首页右上角"登录/注册"入口（PC/移动端各一个，需点可见的那个）
    login_entry = (By.XPATH, '//button[contains(@class,"login-register-btn")]')
    # 登录表单
    phone_input = (By.XPATH, '//input[@placeholder="请输入手机号"]')
    password_input = (By.XPATH, '//input[@placeholder="请输入密码"]')
    submit_btn = (By.XPATH, '//button[@type="submit"]')
    # 身份选择弹窗
    identity_title = (By.XPATH, '//h3[normalize-space(.)="请选择登录身份"]')
    personal_option = (By.XPATH, f'//h4[normalize-space(.)="{IDENTITY_PERSONAL}"]')
    enterprise_option = (By.XPATH, f'//h4[normalize-space(.)="{IDENTITY_ENTERPRISE}"]')
    # 错误提示 toast（语义化的 role=alert）
    toast = (By.XPATH, '//*[@role="alert"]')

    @allure.step("打开首页并点开登录弹窗")
    def open(self):
        """访问系统首页，并点击"登录/注册"打开登录弹窗。

        登录入口可能被临时角标/遮罩拦截导致点击"看似成功"而弹窗未打开，
        故以「手机号输入框是否出现」判定弹窗已打开，未打开则重试点击。
        :return: self（便于链式调用）
        """
        self.driver.get(BASE_URL)
        # 等待登录入口渲染出来（SPA 页面在 driver.get 返回后才异步渲染）
        self.wait.until(
            lambda d: any(el.is_displayed() for el in d.find_elements(*self.login_entry))
        )
        # SPA（Vue）异步挂载：元素虽已可见，但点击事件可能尚未绑定，稍等片刻再点
        time.sleep(2)
        # 首页有 PC 端与移动端两个登录入口，只点可见的那个；
        # 直到登录弹窗内的手机号输入框出现才返回（最多约 25s）
        deadline = time.monotonic() + 25
        while time.monotonic() < deadline:
            if self.driver.find_elements(*self.phone_input):
                return self
            try:
                for el in self.driver.find_elements(*self.login_entry):
                    if el.is_displayed():
                        el.click()
                        break
            except Exception:
                pass
            time.sleep(1.5)
        return self

    @allure.step("填写登录表单")
    def fill_form(self, mobile, password):
        """只填写手机号与密码，不点击登录（供"校验按钮禁用"等场景使用）。

        登录弹窗为 SPA 异步渲染，偶发首次加载较慢（>10s），先显式等待手机号输入框
        出现（最长 30s），避免偶发超时误报为用例失败。

        :param mobile: 手机号
        :param password: 密码
        :return: self（便于链式调用）
        """
        WebDriverWait(self.driver, 30).until(
            EC.visibility_of_element_located(self.phone_input)
        )
        self.send_keys(self.phone_input, mobile)
        self.send_keys(self.password_input, password)
        return self

    @allure.step("输入账号密码并登录")
    def login_password(self, mobile, password):
        """输入手机号与密码，点击登录按钮。

        :param mobile: 手机号
        :param password: 密码
        :return: self（便于链式调用）
        """
        self.fill_form(mobile, password)
        self.click(self.submit_btn)  # 登录按钮在账号密码填写完整后才会变为可点击
        return self

    @allure.step("选择个人身份登录")
    def select_personal(self):
        """点击"个人身份登录"，进入个人身份首页。

        :return: PersonalHomePage 实例
        """
        self.click(self.personal_option)
        from page.personal_page import PersonalHomePage
        return PersonalHomePage(self.driver)

    @allure.step("选择企业身份登录")
    def select_enterprise(self):
        """点击企业名称（如"浙江深佳科技有限公司"），进入企业身份首页。

        :return: EnterpriseHomePage 实例
        """
        self.click(self.enterprise_option)
        from page.enterprise_page import EnterpriseHomePage
        return EnterpriseHomePage(self.driver)

    @allure.step("获取身份选择弹窗标题")
    def get_identity_title(self):
        """返回身份选择弹窗的标题文本（如"请选择登录身份"）。"""
        return self.get_text(self.identity_title)

    @allure.step("判断身份选择弹窗是否出现")
    def identity_dialog_visible(self):
        """判断登录成功后是否弹出"请选择登录身份"弹窗。"""
        return self.is_exist(self.identity_title)

    @allure.step("获取登录错误提示")
    def get_login_toast(self, timeout=8):
        """返回登录失败的 toast 提示文本（如"登录失败，账号密码不正确"）。

        注意：页面里 role="alert" 的元素可能不止一个（存在隐藏的空占位 span），
        所以这里不依赖 find_element 的可见性等待，而是轮询所有 alert，
        返回第一个有文本内容的那个。

        :param timeout: 最长等待秒数
        :return: toast 文本
        """
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            for el in self.driver.find_elements(*self.toast):
                text = (el.text or "").strip()
                if text:
                    return text
            time.sleep(0.3)
        raise TimeoutError("未捕获到登录错误提示 toast")

    @allure.step("判断登录按钮是否禁用")
    def submit_disabled(self):
        """判断登录按钮当前是否处于禁用状态（前端未通过校验时禁用）。

        :return: True 表示禁用
        """
        return self.driver.find_element(*self.submit_btn).get_attribute("disabled") is not None
