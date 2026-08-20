# -*- coding: utf-8 -*-
"""
POM 页面对象层 —— 知识库页。

个人身份登录后，顶部导航「知识库」进入本页（URL: /knowledgBase/mine?siteMode=c）。
页面结构（已实测校准）：
- 根页：文件夹卡片网格（未分类/项目材料/获奖情况/资质证书…），卡片含更多菜单；
- 点击文件夹卡片进入文件夹视图：文件卡片网格（h3 为文件名，含处理中/处理完成徽标），
  每个文件卡片右上角有更多按钮（下拉菜单含「删除」「移动」）；
- 上传：点「上传」打开「个人文件上传」弹窗，隐藏 input[type=file] 随弹窗渲染，
  选文件后点「完成」上传（成功 toast「成功上传 N 个文件」），默认归入未分类；
- 搜索：根页提示「搜索文件夹…」过滤文件夹卡片；文件夹内提示「搜索知识…」过滤文件卡片；
- 删除：文件卡片更多按钮 →「删除」菜单项 → 触发浏览器原生 alert 确认。

定位说明：
- 入口：优先按 class + 文案"知识库"定位，失败回退到绝对路径 nav/button[3]
- 菜单项：按 role="menuitem" + 文案定位（避免 reka-ui 动态 vnode id）
"""
import logging
import time

import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from page.base_page import BasePage

logger = logging.getLogger(__name__)


class KnowledgeBasePage(BasePage):
    """知识库页：进入 / 列表 / 上传 / 搜索 / 删除。"""

    name = "知识库页"

    # 顶部导航入口（个人首页）
    nav_entry = (
        By.XPATH,
        '//button[contains(@class,"header-nav-link") and normalize-space(.)="知识库"]',
    )
    # 兜底：用户提供的绝对路径入口
    nav_entry_fallback = (
        By.XPATH,
        '//*[@id="__nuxt"]/div/div/div/div[1]/div/div[1]/nav/button[3]',
    )

    # 搜索框：根页提示"搜索文件夹..."、文件夹内提示"搜索知识..."，统一按包含"搜索"定位
    search_input = (By.XPATH, '//input[contains(@placeholder,"搜索")]')

    # 上传（"个人文件上传"弹窗，隐藏 input[type=file] 随弹窗渲染）
    upload_btn = (By.XPATH, '//button[normalize-space(.)="上传"]')
    file_input = (By.XPATH, '//input[@type="file"]')
    done_btn = (By.XPATH, '//button[normalize-space(.)="完成"]')
    cancel_btn = (By.XPATH, '//button[normalize-space(.)="取消"]')

    # 删除菜单项（文件卡片更多按钮展开后）
    delete_btn = (
        By.XPATH,
        '//*[@role="menuitem" and contains(normalize-space(.),"删除")]',
    )

    # 文件夹视图标志（进入文件夹后出现"返回文件夹"按钮）
    back_btn = (By.XPATH, '//button[normalize-space(.)="返回文件夹"]')

    # 校验提示（role=alert，与登录/工作创作一致）
    _alert = (By.XPATH, '//*[@role="alert"]')

    # 空状态文案
    _EMPTY_KEYS = ("未找到匹配的文件夹", "未找到", "暂无", "没有找到", "无结果", "为空")

    # 打开 reka-ui 下拉菜单：仅 JS .click() 只派发 click 事件，reka 在 pointerdown 触发，
    # 故派发完整的指针/鼠标事件序列（绕过遮罩拦截，且兼容下拉的 pointerdown 监听）
    _OPEN_MENU_JS = (
        "var el=arguments[0];"
        "el.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,cancelable:true,"
        "pointerId:1,pointerType:'mouse',view:window}));"
        "['mousedown','pointerup','mouseup','click'].forEach(function(t){"
        "el.dispatchEvent(new MouseEvent(t,{bubbles:true,cancelable:true,view:window}));});"
    )

    def __init__(self, driver, url_keyword="knowledgBase"):
        self.url_keyword = url_keyword
        super().__init__(driver)

    # ==================== 进入与断言 ====================

    @allure.step("进入知识库页")
    def enter(self):
        """从个人身份首页点击顶部导航进入知识库页。

        导航按钮上偶发叠加橙色角标（如未读提示）会拦截普通点击的中心点，用 JS
        强制点击绕过，与打开文件夹的处理一致。
        """
        target = self.nav_entry if self.is_exist(self.nav_entry, timeout=5) else self.nav_entry_fallback
        self.click_js(target)
        self.wait.until(lambda d: self.url_keyword in d.current_url)
        time.sleep(1)
        return self

    @allure.step("断言已进入知识库页")
    def is_kb_page(self):
        """URL 含路由关键字 且 页面出现特征文案。"""
        return self.url_keyword in self.driver.current_url and self.has_text("知识库")

    # ==================== 上传 ====================

    @allure.step("打开上传弹窗")
    def open_upload(self):
        """点击「上传」并等待弹窗内的隐藏文件输入框渲染。

        知识库页为 SPA，页面会异步重渲染：普通 click 在定位与点击之间的瞬间可能
        因按钮被替换而抛 stale 引用异常。隐藏的 file input 只随弹窗进入 DOM（弹窗
        未开时不存在），故以「文件输入框是否存在于 DOM」判定弹窗是否已打开；
        已打开则直接返回、不再点击，避免遮罩拦截误关弹窗。
        """
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            if self.driver.find_elements(*self.file_input):
                return self
            try:
                self.click(self.upload_btn)
            except Exception:
                pass
            time.sleep(1)
        raise TimeoutError("点击「上传」后未出现文件选择弹窗")

    @allure.step("选择本地文件：{path}")
    def select_file(self, path):
        """向弹窗内隐藏的 input[type=file] 写入本地文件路径，并捕获校验 toast。

        选择文件后前端立即校验：拒绝时会弹 role=alert 提示（如格式不支持 / 超过 20MB），
        提示约 2~3 秒后消失，故在 3 秒窗口内轮询捕获。
        :return: 捕获到的校验提示文本（无提示则 None）
        """
        self.driver.find_element(*self.file_input).send_keys(path)
        toast = None
        end = time.monotonic() + 3
        while time.monotonic() < end:
            for el in self.driver.find_elements(*self._alert):
                try:
                    text = (el.text or "").strip()
                except Exception:
                    continue  # toast 元素在渲染中被替换，跳过本次读取
                if text:
                    toast = text
            time.sleep(0.2)
        return toast

    @allure.step("读取「完成」按钮禁用状态")
    def is_done_disabled(self):
        """上传弹窗「完成」按钮是否禁用（文件被拒时禁用）。"""
        return self.driver.find_element(*self.done_btn).get_attribute("disabled") is not None

    @allure.step("点击「完成」上传")
    def click_done(self, timeout=20):
        """点击「完成」真正上传。

        弹窗内按钮在选文件后偶发经历短暂重渲染，普通 element_to_be_clickable
        一次性等待可能误判超时，故按秒轮询可点击状态；若期间弹窗已自动关闭
        （平台选文件后直接提交），视为已上传并直接返回。
        """
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                el = self.driver.find_element(*self.done_btn)
            except Exception:
                if "已选择文件" not in self.body_text():
                    return self
                time.sleep(1)
                continue
            try:
                if el.is_displayed() and el.is_enabled():
                    el.click()
                    return self
            except Exception:
                pass
            time.sleep(1)
        raise TimeoutError("点击「完成」按钮超时，且弹窗未自动关闭")

    @allure.step("等待上传弹窗关闭")
    def wait_upload_modal_closed(self, timeout=30):
        """点击完成后的上传弹窗关闭判定：body 不再出现「已选择文件」。"""
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            if "已选择文件" not in self.body_text():
                return True
            time.sleep(1)
        return False

    @allure.step("关闭上传弹窗")
    def close_upload(self):
        """校验类用例收尾：若弹窗仍打开则点「取消」关闭。"""
        try:
            if self.is_exist(self.cancel_btn, timeout=2):
                self.click(self.cancel_btn)
        except Exception as e:
            logger.warning("关闭上传弹窗失败: %s", e)
        return self

    # ==================== 文件夹 ====================

    def _folder_card(self, name):
        return (
            By.XPATH,
            f'//h3[normalize-space(.)="{name}"]/ancestor::div[contains(@class,"group")][1]',
        )

    @allure.step("打开文件夹：{name}")
    def open_folder(self, name):
        """点击文件夹卡片进入文件夹视图（出现「返回文件夹」按钮为标志）。

        上传弹窗关闭动画期间其黑色遮罩仍会短暂拦截普通点击（`data-state="closed"`
        且 `pointer-events: auto`），此处用 JS 强制点击绕过；进入前已完成上传、
        弹窗必然已关闭，不会点到真实弹窗背后的元素。
        """
        self.click_js(self._folder_card(name))
        self.wait_body_text("返回文件夹", timeout=10)
        return self

    @allure.step("判断是否处于文件夹视图")
    def is_folder_view(self):
        return self.has_text("返回文件夹")

    # ==================== 文件 ====================

    def _file_card(self, name):
        return (
            By.XPATH,
            f'//h3[normalize-space(.)="{name}"]/ancestor::div[contains(@class,"group")][1]',
        )

    @allure.step("等待文件卡片出现：{name}")
    def file_exists(self, name, timeout=10):
        return self.is_exist(self._file_card(name), timeout=timeout)

    # ==================== 收藏与图谱面板 ====================

    # 「我的收藏」「知识图谱」为根页入口，点开的是同 URL 上的抽屉/面板
    # （实测校准：仍在 /knowledgBase/mine?siteMode=c，不跳转页面）
    favorites_btn = (By.XPATH, '//button[normalize-space(.)="我的收藏"]')
    graph_btn = (By.XPATH, '//button[normalize-space(.)="知识图谱"]')

    # 收藏分类 Tab（我的收藏面板）
    fav_categories = ["全部", "政策", "协会", "荣誉", "高校", "文献", "国标", "行标", "会议"]
    # 图谱节点筛选（知识图谱面板）
    graph_filters = [
        "用户", "学校", "公司", "组织", "教育经历", "工作经历", "项目",
        "获奖", "荣誉", "论文", "专利", "软著", "培训", "能力", "行业", "其他",
    ]

    def _panel_btn(self, name):
        return (By.XPATH, f'//button[normalize-space(.)="{name}"]')

    @allure.step("打开「我的收藏」面板")
    def open_favorites(self):
        """点击「我的收藏」，等待面板加载（出现「项收藏」计数）。"""
        self.click_js(self.favorites_btn)
        self.wait_body_text("项收藏", timeout=10)
        return self

    @allure.step("打开「知识图谱」面板")
    def open_graph(self):
        """点击「知识图谱」，等待关系图加载（出现「人物关系图」）。"""
        self.click_js(self.graph_btn)
        self.wait_body_text("人物关系图", timeout=10)
        return self

    @allure.step("切换收藏分类：{category}")
    def click_fav_category(self, category):
        """点击收藏面板的分类 Tab（全部/政策/协会/荣誉/高校/文献/国标/行标/会议）。"""
        self.click(self._panel_btn(category))
        return self

    @allure.step("切换图谱节点筛选：{name}")
    def click_graph_filter(self, name):
        """点击知识图谱的节点筛选（用户/学校/公司/组织…）。"""
        self.click(self._panel_btn(name))
        return self

    # ==================== 搜索 ====================

    @allure.step("搜索关键字：{keyword}")
    def search(self, keyword):
        """在搜索框输入关键字（先清空）。根页过滤文件夹，文件夹内过滤文件。

        上传完成后的瞬间输入框可能短暂不可交互，做 10 秒内的重试。
        """
        deadline = time.monotonic() + 10
        while True:
            try:
                el = self.driver.find_element(*self.search_input)
                el.clear()
                el.send_keys(keyword)
                break
            except Exception:
                if time.monotonic() >= deadline:
                    raise
                time.sleep(0.5)
        time.sleep(2)
        return self

    @allure.step("清空搜索")
    def clear_search(self):
        return self.search("")

    # ==================== 删除 ====================

    @allure.step("删除文件：{name}")
    def delete_file(self, name, timeout=40):
        """删除所有匹配 name 的文件卡片（更多按钮 → 删除 → 确认原生 alert）。

        处理要点（实测校准）：
        - 更多按钮用 JS 点击，避免上传弹窗残留遮罩拦截普通点击；
        - 卡片仍显示「处理中」时先等待（处理中文件删除可能被平台推迟），
          处理完成 / 处理失败的文件均可直接删除；
        - 循环删除直到无同名卡片残留，兜底清理历史失败运行遗留的重复文件。
        :return: 原生确认框的提示文本（多次删除时返回最后一次）
        """
        alert_text = None
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            cards = self.driver.find_elements(*self._file_card(name))
            if not cards:
                break
            try:
                processing = "处理中" in cards[0].text
            except Exception:
                time.sleep(2)  # 卡片在重渲染中被替换，稍后再试
                continue
            if processing:
                time.sleep(2)  # 仍在处理中，稍后再试
                continue
            if not self._open_more_menu(name):
                raise TimeoutError(f"未能展开「{name}」的更多菜单")
            self.click(self.delete_btn)
            self.wait.until(EC.alert_is_present())
            alert = self.driver.switch_to.alert
            alert_text = alert.text
            alert.accept()
            time.sleep(2)
        return alert_text

    def _open_more_menu(self, name, attempts=4):
        """展开文件卡片更多按钮的下拉菜单。

        先派发完整指针事件序列（绕过遮罩且兼容 reka 的 pointerdown 触发），
        若菜单未弹出则回退为真实点击（此时残留遮罩通常已消失），
        直到「删除」菜单项出现。
        """
        for _ in range(attempts):
            cards = self.driver.find_elements(*self._file_card(name))
            if not cards:
                return False
            try:
                more = cards[0].find_element(
                    By.XPATH, './/button[@aria-haspopup="menu"]'
                )
            except Exception:
                return False
            self.driver.execute_script(self._OPEN_MENU_JS, more)
            time.sleep(1)
            if self.driver.find_elements(*self.delete_btn):
                return True
            try:
                more.click()
                time.sleep(1)
                if self.driver.find_elements(*self.delete_btn):
                    return True
            except Exception:
                pass
        return False

    # ==================== 空状态 / 校验提示 ====================

    @allure.step("判断列表是否为空状态")
    def is_empty(self, timeout=5):
        """列表为空时页面出现空状态提示（未找到匹配的文件夹 等）。"""
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            body = self.body_text()
            if any(k in body for k in self._EMPTY_KEYS):
                return True
            time.sleep(0.5)
        return False

    # ==================== 文本断言（复用基类） ====================

    def has_text(self, text):
        """判断页面正文是否包含指定文本（忽略空格差异）。"""
        return text.replace(" ", "") in self.body_text().replace(" ", "")
