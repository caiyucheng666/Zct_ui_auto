# -*- coding: utf-8 -*-
"""
知识库测试用例（个人身份，数据驱动：数据来自 data/knowledge_base.yaml）。

覆盖场景（定位符已对真实站点实测校准）：
1. 入口导航   —— 个人首页进入知识库页（URL 含 knowledgBase + siteMode=c）
2. 列表展示   —— 根页文件夹卡片列表正常渲染（我的文件夹/上传/未分类等）
3. 上传成功   —— 支持格式 PDF/DOC/DOCX/PPT/PPTX 全格式上传成功（用后删除清理）
4. 上传校验   —— 不支持类型（exe/zip/txt）被前端拒绝，完成按钮置灰
5. 上传校验   —— 超大文件（>20MB）被前端拒绝，完成按钮置灰（空文件平台不拦截）
6. 搜索       —— 根页按文件夹名过滤文件夹卡片（命中/过滤/空结果）；
                 注：平台搜索索引仅收录已处理文件，故命中用稳定文件夹名而非新上传文件
7. 删除       —— 文件卡片更多按钮 → 删除 → 原生确认弹窗，列表移除
8. 收藏面板   —— 打开「我的收藏」抽屉，展示全部 9 个分类 Tab 与收藏计数
9. 图谱面板   —— 打开「知识图谱」抽屉，展示人物关系图与全部 16 个节点筛选

样例文件：启动时自动生成到 temps/test_files/（gitignore），
上传的临时文件用后删除，保持知识库干净。

TODO(企业身份)：企业首页「企业知识库」入口与个人同构，企业身份用例待补充。
"""
import io
import os
import zipfile

import allure
import pytest

from utils.config import ACCOUNT, BASE_DIR
from page.knowledge_base_page import KnowledgeBasePage
from page.login_page import LoginPage
from utils.read_yaml import read_yaml

# 从 YAML 读取知识库用例数据
_DATA = read_yaml("knowledge_base.yaml")
_PAGE = _DATA["page"]

# 样例文件目录（自动生成、不入库）
_TF_DIR = os.path.join(BASE_DIR, "temps", "test_files")


# ==================== 样例文件生成 ====================

def _docx_bytes():
    """生成一个最小合法 DOCX（OOXML 规范，zip 结构）。"""
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        '</Types>'
    )
    rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
        '</Relationships>'
    )
    document = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:body><w:p><w:r><w:t>zct knowledge base sample</w:t></w:r></w:p></w:body>'
        '</w:document>'
    )
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", rels)
        z.writestr("word/document.xml", document)
    return buf.getvalue()


def _pptx_bytes():
    """生成一个最小合法 PPTX（OOXML 规范，zip 结构）。"""
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>'
        '<Override PartName="/ppt/slides/slide1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        '</Types>'
    )
    rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>'
        '</Relationships>'
    )
    presentation = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<p:sldIdLst><p:sldId id="256" r:id="rId1"/></p:sldIdLst>'
        '<p:sldSz cx="9144000" cy="6858000"/>'
        '</p:presentation>'
    )
    pres_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide1.xml"/>'
        '</Relationships>'
    )
    slide1 = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
        'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
        '<p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
        '<p:grpSpPr/><p:sp><p:nvSpPr><p:cNvPr id="2" name="Title 1"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
        '<p:spPr/><p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:r><a:rPr lang="zh-CN"/><a:t>zct sample</a:t></a:r></a:p></p:txBody></p:sp>'
        '</p:spTree></p:cSld>'
        '</p:sld>'
    )
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", rels)
        z.writestr("ppt/presentation.xml", presentation)
        z.writestr("ppt/_rels/presentation.xml.rels", pres_rels)
        z.writestr("ppt/slides/slide1.xml", slide1)
    return buf.getvalue()


def _pdf_bytes():
    """生成一个含可抽取文本的最小合法 PDF（正确 xref 偏移）。

    仅含 Catalog/Pages/Page 骨架、没有可抽取文本的 PDF 会被平台服务端解析为
    「处理失败」，故补充字体资源与文本流，保证解析出文字、处理成功。
    """
    stream_data = b"BT /F1 24 Tf 72 720 Td (zct knowledge base sample) Tj ET\n"
    page = (
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> "
        b"/Contents 4 0 R >>"
    )
    objs = [
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
        b"3 0 obj\n" + page + b"\nendobj\n",
        b"4 0 obj\n<< /Length %d >>\nstream\n%sendstream\nendobj\n" % (len(stream_data), stream_data),
    ]
    buf = io.BytesIO()
    buf.write(b"%PDF-1.4\n")
    offsets = []
    for obj in objs:
        offsets.append(buf.tell())
        buf.write(obj)
    xref = buf.tell()
    buf.write(b"xref\n0 5\n")
    buf.write(b"0000000000 65535 f \n")
    for off in offsets:
        buf.write(("%010d 00000 n \n" % off).encode())
    buf.write(b"trailer\n<< /Size 5 /Root 1 0 R >>\n")
    buf.write(b"startxref\n%d\n%%%%EOF\n" % xref)
    return buf.getvalue()


def _ensure_sample_files():
    """生成知识库样例文件到 temps/test_files/（每次覆盖，生成器变更即时生效）。"""
    os.makedirs(_TF_DIR, exist_ok=True)
    # 旧版 .doc/.ppt 为 OLE2 二进制：写 magic 头 + 哑数据（平台按扩展名校验）
    _ole2 = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" + b"0" * 512
    files = {
        "kb_sample.pdf": _pdf_bytes(),
        "kb_sample.doc": _ole2,
        "kb_sample.docx": _docx_bytes(),
        "kb_sample.ppt": _ole2,
        "kb_sample.pptx": _pptx_bytes(),
        "kb_search_target.docx": _docx_bytes(),
        "kb_del_me.docx": _docx_bytes(),
        "kb_big.docx": b"x" * (21 * 1024 * 1024),  # >20MB，触发大小限制
        "kb_sample.exe": b"MZ" + b"\x00" * 64,
        "kb_sample.zip": b"PK\x03\x04" + b"\x00" * 64,
        "kb_sample.txt": b"hello kb",
    }
    for name, data in files.items():
        with open(os.path.join(_TF_DIR, name), "wb") as f:
            f.write(data)
    return _TF_DIR


_TF_DIR = _ensure_sample_files()


def _abs(name):
    """把样例文件名转为绝对路径。"""
    return os.path.join(_TF_DIR, name)


def _login_to_kb(driver):
    """登录个人身份并进入知识库页。"""
    (
        LoginPage(driver)
        .open()
        .login_password(ACCOUNT["mobile"], ACCOUNT["password"])
        .select_personal()
    )
    return KnowledgeBasePage(driver).enter()


def _upload(page, fname):
    """完整上传流程：开弹窗 → 选文件 → 点完成 → 等待弹窗关闭。"""
    page.open_upload()
    page.select_file(_abs(fname))
    assert not page.is_done_disabled(), f"「{fname}」应为合法文件，完成按钮应可用"
    page.click_done()
    assert page.wait_upload_modal_closed(), f"「{fname}」上传弹窗应在点击完成后关闭"
    return page


def _cleanup_uploaded(page, fname):
    """用后清理：删除本次上传的文件，保持知识库干净（失败仅告警不阻断）。"""
    try:
        page.close_upload()
        if page.has_text(fname) and not page.is_folder_view():
            page.open_folder("未分类")
        if page.is_folder_view() and page.has_text(fname):
            page.delete_file(fname)
    except Exception as e:  # noqa: BLE001 - 清理失败不影响用例主结论
        print(f"[cleanup] 删除 {fname} 失败: {e}")


@allure.epic("职策佳平台")
@allure.feature("知识库")
@pytest.mark.knowledge_base
class TestKnowledgeBase:
    """知识库功能测试集（个人身份）。"""

    @pytest.mark.skip(reason="临时跳过，待补充新的用例")
    @allure.story("入口导航")
    @allure.title("个人身份进入知识库页")
    def test_enter_knowledge_base(self, driver, screenshot_on_end):
        """个人首页点知识库导航，应进入知识库页。"""
        page = _login_to_kb(driver)

        assert page.is_kb_page(), "应进入知识库页"
        assert _PAGE["url_keyword"] in driver.current_url, (
            f"URL 应含 {_PAGE['url_keyword']}，实际：{driver.current_url}"
        )
        assert "siteMode=c" in driver.current_url, "个人模式 URL 应携带 siteMode=c"

    @pytest.mark.skip(reason="临时跳过，待补充新的用例")
    @allure.story("列表展示")
    @allure.title("知识库文件夹列表正常展示")
    def test_file_list_display(self, driver, screenshot_on_end):
        """根页应渲染文件夹卡片列表（我的文件夹/上传/未分类等）。"""
        page = _login_to_kb(driver)
        body = page.body_text()
        assert "我的文件夹" in body, "根页应展示「我的文件夹」"
        assert "上传" in body, "根页应有「上传」入口"
        assert any(f in body for f in ("未分类", "项目材料", "获奖情况", "资质证书")), (
            "根页应展示文件夹卡片"
        )

    @pytest.mark.skip(reason="临时跳过，待补充新的用例")
    @allure.story("上传")
    @allure.title("上传成功：{case[name]}")
    @pytest.mark.parametrize("case", _DATA["upload_supported"], ids=lambda c: c["name"])
    def test_upload_success(self, driver, screenshot_on_end, case):
        """上传支持格式文件应成功，且用后删除清理知识库。"""
        page = _login_to_kb(driver)
        fname = case["file"]
        try:
            _upload(page, fname)
            page.open_folder("未分类")
            assert page.file_exists(fname), f"未分类文件夹应出现「{fname}」"
        finally:
            _cleanup_uploaded(page, fname)

    @pytest.mark.skip(reason="临时跳过，待补充新的用例")
    @allure.story("上传校验")
    @allure.title("不支持类型被拒绝：{case[name]}")
    @pytest.mark.parametrize("case", _DATA["upload_unsupported"], ids=lambda c: c["name"])
    def test_upload_unsupported(self, driver, screenshot_on_end, case):
        """选择不支持类型文件应出现前端校验提示，文件不进入列表。"""
        page = _login_to_kb(driver)
        fname = case["file"]
        page.open_upload()
        toast = page.select_file(_abs(fname))

        assert toast and "格式不支持" in toast, f"「{fname}」应被拒绝并提示格式不支持，实际：{toast}"
        assert page.is_done_disabled(), f"「{fname}」被拒后完成按钮应置灰"
        assert "已选择文件" not in page.body_text(), f"「{fname}」不应进入选择列表"
        page.close_upload()

    @pytest.mark.skip(reason="临时跳过，待补充新的用例")
    @allure.story("上传校验")
    @allure.title("超大文件（>20MB）被拒绝")
    def test_upload_oversized(self, driver, screenshot_on_end):
        """超过 20MB 的文件应被前端拒绝（完成按钮置灰），不进入列表。"""
        page = _login_to_kb(driver)
        fname = _DATA["upload_oversized"]["file"]
        page.open_upload()
        toast = page.select_file(_abs(fname))

        assert "已选择文件" not in page.body_text(), "超大文件不应进入选择列表"
        assert page.is_done_disabled(), "超过 20MB 的文件完成按钮应置灰"
        assert toast and "超过20MB" in toast, f"应提示超过 20MB 限制，实际：{toast}"
        page.close_upload()

    @pytest.mark.skip(reason="临时跳过，待补充新的用例")
    @allure.story("搜索")
    @allure.title("搜索命中：{case[name]}")
    @pytest.mark.parametrize("case", _DATA["search_hit"], ids=lambda c: c["name"])
    def test_search_hit(self, driver, screenshot_on_end, case):
        """按文件夹名搜索，应命中该文件夹并过滤掉不匹配的文件夹。

        说明：根页「搜索文件夹」按关键字过滤文件夹卡片。平台搜索索引只收录已处理的
        文件，新上传文件在处理完成前搜不到，故此处用稳定存在的文件夹名做命中断言。
        """
        page = _login_to_kb(driver)
        page.search(case["keyword"])
        assert page.has_text(case["keyword"]), f"搜索「{case['keyword']}」应命中该文件夹"
        assert not page.has_text(case["filtered_out"]), (
            f"不匹配的文件夹「{case['filtered_out']}」应被过滤掉"
        )
        page.clear_search()

    @pytest.mark.skip(reason="临时跳过，待补充新的用例")
    @allure.story("搜索")
    @allure.title("搜索无结果：{case[name]}")
    @pytest.mark.parametrize("case", _DATA["search_no_result"], ids=lambda c: c["name"])
    def test_search_no_result(self, driver, screenshot_on_end, case):
        """搜索不存在的关键字，列表应清空并展示空结果提示。"""
        page = _login_to_kb(driver)
        page.search(case["keyword"])

        assert page.is_empty(), f"搜索「{case['keyword']}」应展示空结果提示"
        assert "未找到匹配的文件夹" in page.body_text(), "空结果提示应包含「未找到匹配的文件夹」"
        page.clear_search()

    @pytest.mark.skip(reason="临时跳过，待补充新的用例")
    @allure.story("删除")
    @allure.title("删除知识文件")
    def test_delete_file(self, driver, screenshot_on_end):
        """文件卡片更多按钮 → 删除 → 原生确认，文件应从列表移除。"""
        page = _login_to_kb(driver)
        target = "kb_del_me.docx"
        _upload(page, target)
        page.open_folder("未分类")
        assert page.file_exists(target), f"删除前应存在「{target}」"

        alert_text = page.delete_file(target)
        assert "确定要删除" in alert_text, f"应弹出原生删除确认框，实际：{alert_text}"
        assert not page.file_exists(target), f"删除后「{target}」应从列表移除"

    @pytest.mark.skip(reason="临时跳过，待补充新的用例")
    @allure.story("收藏面板")
    @allure.title("打开「我的收藏」面板")
    def test_favorites_panel(self, driver, screenshot_on_end):
        """点击「我的收藏」，应打开收藏抽屉：展示计数与全部分类 Tab。"""
        page = _login_to_kb(driver)
        page.open_favorites()
        body = page.body_text()

        assert "收藏" in body, "收藏面板应展示标题"
        assert "项收藏" in body, "收藏面板应展示收藏计数（共 N 项收藏）"
        for cat in _DATA["favorites_categories"]:
            assert cat in body, f"收藏面板应展示分类 Tab：{cat}"

    @pytest.mark.skip(reason="临时跳过，待补充新的用例")
    @allure.story("收藏面板")
    @allure.title("收藏分类切换：{category}")
    @pytest.mark.parametrize(
        "category", _DATA["favorites_categories"][1:], ids=lambda c: c
    )
    def test_favorites_category_switch(self, driver, screenshot_on_end, category):
        """点击收藏分类 Tab，分类应可正常切换（面板保持打开）。"""
        page = _login_to_kb(driver)
        page.open_favorites()
        page.click_fav_category(category)

        assert "项收藏" in page.body_text(), f"切换分类「{category}」后收藏面板应保持打开"

    @pytest.mark.skip(reason="临时跳过，待补充新的用例")
    @allure.story("图谱面板")
    @allure.title("打开「知识图谱」面板")
    def test_graph_panel(self, driver, screenshot_on_end):
        """点击「知识图谱」，应打开图谱抽屉：人物关系图 + 全部节点筛选。"""
        page = _login_to_kb(driver)
        page.open_graph()
        body = page.body_text()

        assert "人物关系图" in body, "图谱面板应展示人物关系图"
        for name in _DATA["graph_filters"]:
            assert name in body, f"图谱面板应展示节点筛选：{name}"

    @pytest.mark.skip(reason="临时跳过，待补充新的用例")
    @allure.story("图谱面板")
    @allure.title("图谱节点筛选：{name}")
    @pytest.mark.parametrize("name", _DATA["graph_filters"], ids=lambda c: c)
    def test_graph_filter_switch(self, driver, screenshot_on_end, name):
        """点击图谱节点筛选，筛选应可正常切换（图谱面板保持打开）。"""
        page = _login_to_kb(driver)
        page.open_graph()
        page.click_graph_filter(name)

        assert "人物关系图" in page.body_text(), f"切换节点筛选「{name}」后图谱面板应保持打开"
