# -*- coding: utf-8 -*-
"""
YAML 数据驱动读取工具。

作用：把测试数据从测试代码里剥离出来，统一放到 data/*.yaml 文件中，
测试用例通过本模块按需读取，实现"数据与代码分离"。

用法示例：
    from utils.read_yaml import read_yaml

    data = read_yaml("login_data.yaml")   # 读取整个文件，返回 dict
    cases = data["login_fail"]            # 取某一组用例数据
"""
import os

import yaml

from utils.config import DATA_DIR


def read_yaml(filename):
    """读取 data 目录下的 YAML 文件并解析为 Python 对象。

    :param filename: YAML 文件名，如 "login_data.yaml"
    :return: 解析后的数据（通常是 dict，内含 list）
    """
    file_path = os.path.join(DATA_DIR, filename)
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
