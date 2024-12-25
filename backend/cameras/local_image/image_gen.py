import asyncio
import base64
import os

from fastapi import APIRouter, WebSocket
from algorithms.yolov8.detect.xianxu_detect import detect_and_draw  # 导入目标检测函数


router = APIRouter()

# 设置图片文件夹路径
IMAGE_FOLDER = "D:\\work\\xianxu\\data\\data2024-12-03\\产品1"

async def get_images_from_folder():
    if os.path.exits(IMAGE_FOLDER):
        images = sorted(os.listdir(IMAGE_FOLDER))  # 按名称排序
        for image_name in images:
            image_path = os.path.join(IMAGE_FOLDER, image_name)
            with open(image_path, "rb") as img_file:  # 以二进制模式打开图片
                img_bytes = img_file.read()  # 读取图片的二进制数据
            yield img_bytes
            await asyncio.sleep(1)  # 每秒发送一张图片
    else:
        pass


# WebSocket 路由
@router.websocket("/get-folder-image")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    async for img_bytes in get_images_from_folder():
        result_img_bytes = detect_and_draw(img_bytes)
        await websocket.send_bytes(result_img_bytes)  # 向前端发送二进制数据