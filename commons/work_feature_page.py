# -*- coding: utf-8 -*-
"""
POM 页面对象层 —— 工作创作各功能页（通用）。

8 个功能页面结构相似：页面标题 + 表单 + 提交按钮，提交后跳转到详情页
并异步生成 AI 结果（"生成中..."），生成完成后展示结果内容与
「内容由 AI生成，仅供参考，请仔细甄别」免责声明。

各功能差异（标题、提交按钮、URL 关键字、表单字段、成功标志）由外部数据
（data/work_creation.yaml）传入，本类按数据驱动的 fill 配置完成填写、
提交、等待生成、结果断言，实现"数据与代码分离"。
"""
import logging
import re
import time

import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

from commons.base_page import BasePage

logger = logging.getLogger(__name__)


class WorkFeaturePage(BasePage):
    """工作创作功能页通用页面对象。"""

    name = "工作创作功能页"

    # 通用定位
    _alert = (By.XPATH, '//*[@role="alert"]')

    def __init__(self, driver, case):
        """构造方法。

        :param driver: 浏览器驱动
        :param case: 单个功能的数据字典（来自 data/work_creation.yaml 的 features 列表项）
        """
        self.case = case
        self.feature_name = case["name"]
        self.url_keyword = case["url_keyword"]
        self.submit_button = case.get("submit_button") or ""
        self.result_hint = case.get("result_hint") or ""
        self.name = self.feature_name  # 覆盖基类 name，便于报告区分
        super().__init__(driver)

    # ==================== 提交 ====================

    def _button(self, text):
        return (By.XPATH, f'//button[normalize-space(.)="{text}"]')

    @allure.step("点击提交按钮")
    def click_submit(self, label=None):
        """点击提交/生成按钮。

        :param label: 按钮文案，缺省用 case 里的 submit_button
        """
        label = label or self.submit_button
        if not label:
            return self
        self.click(self._button(label))
        return self

    @allure.step("JS 点击按钮")
    def click_js_button(self, text):
        """用 JS 强制点击按钮（绕过遮挡/可见性校验）。"""
        el = self.driver.find_element(*self._button(text))
        self.driver.execute_script("arguments[0].click()", el)
        return self

    # ==================== 填写 ====================

    @allure.step("填写所有文本域")
    def fill_textareas(self, text):
        """向页面所有 textarea 填写内容（覆盖单/多文本域两类表单）。"""
        for el in self.driver.find_elements(By.TAG_NAME, "textarea"):
            el.clear()
            el.send_keys(text)
        return self

    @allure.step("按占位符填写输入框")
    def fill_input(self, placeholder, text):
        """按 placeholder 定位输入框并填写（直接 send_keys，兼容 Vue 响应式）。"""
        el = self.driver.find_element(By.XPATH, f'//input[@placeholder="{placeholder}"]')
        el.send_keys(text)
        return self

    @allure.step("按序号填写数字输入框")
    def fill_number(self, index, text):
        """按序号填写数字输入框（直接 send_keys）。"""
        els = self.driver.find_elements(By.XPATH, "//input[@type='number']")
        els[index].send_keys(text)
        return self

    @allure.step("选择下拉框选项")
    def select_level(self, text):
        """选择页面第一个 <select> 下拉框的选项（项目方向挖掘的项目级别）。"""
        sel = self.driver.find_element(By.XPATH, "//select")
        Select(sel).select_by_visible_text(text)
        return self

    @allure.step("填写起止日期")
    def fill_dates(self, start, end):
        """填写起止时间（原生 input[type=date]）。

        Chrome 的 date 输入框在 zh-CN 下不接受 send_keys 直接填 ISO 字符串，
        需点击后分段输入：年 → 方向键 → 月 → 方向键 → 日。
        """
        dates = self.driver.find_elements(By.XPATH, "//input[@type='date']")
        for el, val in zip(dates[:2], [start, end]):
            self._type_date(el, val)
        return self

    def _type_date(self, el, value):
        """分段键入日期，value 形如 'YYYY-MM-DD'。"""
        year, month, day = value.split("-")
        el.click()
        el.send_keys(year)
        el.send_keys(Keys.ARROW_RIGHT)
        el.send_keys(month)
        el.send_keys(Keys.ARROW_RIGHT)
        el.send_keys(day)

    @allure.step("选择单选（主持/参与）")
    def click_radio(self, index=0):
        """JS 点击第 index 个 radio（原生 radio 可能被样式遮挡）。"""
        radios = self.driver.find_elements(By.XPATH, "//input[@type='radio']")
        if radios:
            self.driver.execute_script("arguments[0].click()", radios[index])
        return self

    @allure.step("选择政策文件")
    def select_policy_file(self):
        """政策解读：点击搜索框展开文件列表，选择第一个政策文件。

        选中文件后页面会自动跳转到该政策的解读结果页。
        """
        self.driver.find_element(By.XPATH, '//input[@placeholder="请选择政策文件"]').click()
        time.sleep(2)
        row = self.driver.find_element(
            By.XPATH,
            '//div[contains(@class,"cursor-pointer") and contains(@class,"min-h-10") '
            'and contains(normalize-space(.),".docx")]',
        )
        row.click()
        return self

    @allure.step("导入知识库文件")
    def import_knowledge_base_file(self):
        """打开「导入知识库」弹窗，选择第一个文件并导入（用于需参考文件的功能）。"""
        self.click(self._button("导入知识库"))
        time.sleep(3)
        row = self.driver.find_element(
            By.XPATH,
            "//*[contains(@class,'cursor-pointer') and "
            "(contains(normalize-space(.),'.pdf') or contains(normalize-space(.),'.docx'))]",
        )
        row.click()
        time.sleep(1)
        btn = self.driver.find_element(
            By.XPATH, "//button[starts-with(normalize-space(.),'导入(')]"
        )
        self.driver.execute_script("arguments[0].click()", btn)
        time.sleep(3)
        return self

    @allure.step("按配置填写表单")
    def fill_form(self, fill):
        """按 YAML 里的 fill 配置分发到对应填写方法。

        支持的键：
          description   —— 文本域内容（技术描述/方案摘要/项目描述等）
          policy_file   —— 选择政策文件（政策解读）
          import_kb_file—— 导入知识库文件（项目方向挖掘）
          project_name  —— 项目名称
          amount        —— 项目金额（第一个数字框）
          people        —— 项目人数（第二个数字框）
          unit          —— 立项单位
          work_unit     —— 工作经历所在单位
          work_position —— 工作经历岗位
          start_date/end_date —— 起止日期
        """
        if not fill:
            return self
        if fill.get("description"):
            self.fill_textareas(fill["description"])
        if fill.get("policy_file"):
            self.select_policy_file()
        # select 下拉框先填：其 change 事件会触发 Vue 响应式，可能重置后续已填字段
        if fill.get("select_level"):
            self.select_level(fill["select_level"])
        if fill.get("project_name"):
            self.fill_input("请输入项目名称", fill["project_name"])
        if fill.get("amount"):
            self.fill_number(0, fill["amount"])
        if fill.get("people"):
            self.fill_number(1, fill["people"])
        if fill.get("start_date") and fill.get("end_date"):
            self.fill_dates(fill["start_date"], fill["end_date"])
        if fill.get("unit"):
            self.fill_input("请输入立项单位", fill["unit"])
        if fill.get("work_unit"):
            self.fill_input("请输入单位名称", fill["work_unit"])
        if fill.get("work_position"):
            self.fill_input("请输入岗位名称", fill["work_position"])
        if fill.get("template"):
            self.click(self._button(fill["template"]))
        if fill.get("budget"):
            self.fill_number(0, fill["budget"])
        # 导入知识库文件放到最后：其弹窗关闭后可能重置表单状态
        if fill.get("import_kb_file"):
            self.import_knowledge_base_file()
        return self

    # ==================== 断言辅助 ====================

    @allure.step("获取校验提示")
    def get_toast(self, timeout=8):
        """轮询所有 role=alert 元素，返回第一个有文本的提示。"""
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            for el in self.driver.find_elements(*self._alert):
                text = (el.text or "").strip()
                if text:
                    return text
            time.sleep(0.3)
        return None

    def has_validation_toast(self, timeout=8):
        return self.get_toast(timeout) is not None

    @allure.step("判断是否已进入生成详情页")
    def is_detail_page(self):
        """判断当前 URL 是否为详情页（形如 /technical/12113，含数字 id 段）。"""
        return bool(re.search(rf"/{re.escape(self.url_keyword)}/\d+", self.driver.current_url))

    @allure.step("等待生成完成")
    def wait_generated(self, timeout=240):
        """等待 AI 生成完成：'生成中'消失（连续两次，处理多阶段生成闪烁）且结果已渲染。

        结果以 case 的 result_hint（或通用「AI生成」免责声明）为准，
        忽略"内容由 AI生成"与"内容由AI生成"之间的空格差异。

        :param timeout: 最长等待秒数
        :return: True 表示生成完成且结果已出现
        """
        marker = (self.result_hint or "AI生成").replace(" ", "")
        end = time.monotonic() + timeout
        gone_streak = 0
        while time.monotonic() < end:
            body = self.body_text().replace(" ", "")
            generating = "生成中" in body or "正在" in body
            if not generating and marker in body:
                gone_streak += 1
                if gone_streak >= 2:
                    return True
            else:
                gone_streak = 0
            time.sleep(5)
        return False

    @allure.step("断言结果内容")
    def has_text(self, text):
        """判断页面正文是否包含指定文本（忽略空格差异）。"""
        return text.replace(" ", "") in self.body_text().replace(" ", "")

    # ==================== 内部工具 ====================

    def _js_set_input_value(self, el, value):
        """JS 设置输入框值并派发 input/change 事件，触发 Vue 响应式更新。"""
        self.driver.execute_script(
            "var setter = Object.getOwnPropertyDescriptor("
            "window.HTMLInputElement.prototype, 'value').set;"
            "setter.call(arguments[0], arguments[1]);"
            "arguments[0].dispatchEvent(new InputEvent('input', {bubbles: true, inputType: 'insertText', data: arguments[1]}));"
            "arguments[0].dispatchEvent(new Event('change', {bubbles: true}));",
            el,
            value,
        )
