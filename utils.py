import os
import uuid


def rename_image(old_filename):
    """yapf-pycharm重命名上传图片文件名"""
    ext = os.path.splitext(old_filename)[1]
    new_filename = uuid.uuid4().hex + ext
    return new_filename


def get_filenamewithoutext(filename):
    """去除上传文件的扩展名"""
    filename = os.path.splitext(filename)[0]
    return filename
