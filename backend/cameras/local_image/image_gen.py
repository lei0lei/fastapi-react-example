import asyncio
import base64
import os

from fastapi import APIRouter, WebSocket
from algorithms.yolov8.detect.xianxu_detect import detect_and_draw_async  # 导入目标检测函数
from starlette.websockets import  WebSocketDisconnect, WebSocketState
import json
import cv2

router = APIRouter()

# 设置图片文件夹路径
IMAGE_FOLDER = "D:\\work\\xianxu\\data\\data2024-12-03\\产品1"





async def get_images_from_folder():
    if os.path.exists(IMAGE_FOLDER):
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
@router.websocket("/get-folder-image/{folderpath}")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    async for img_bytes in get_images_from_folder():
        frame_id = str(uuid.uuid4())
        result = await detect_and_draw_async(img_bytes)
        result_img_bytes,detect_results = result['image_bytes'],result['detection_results']
        detect_results['frame_id'] = frame_id
        try:
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.send_text(json.dumps(detect_results))
                # 检测结果发送，包含目标检测结果，OK,NG,统计数量

                # 发送图片数据（二进制），附加帧 ID 到头部
                frame_id_bytes = frame_id.encode("utf-8")
                frame_id_length = len(frame_id_bytes).to_bytes(4, byteorder="big")  # 用 4 字节记录 ID 长度
                await websocket.send_bytes(frame_id_length + frame_id_bytes + result_img_bytes)
                # await websocket.send_bytes(result_img_bytes['image_bytes'])

        except RuntimeError as e:
            print(f"WebSocket 错误: {e}")
            break  # 如果遇到错误，退出循环
        
async def get_images_from_video(videopath: str):
    cap = cv2.VideoCapture(videopath)
    if not cap.isOpened():
        print(f"无法打开视频文件: {videopath}")
        return

    while True:
        ret, frame = cap.read()  # 读取视频帧
        if not ret:
            break  # 视频结束时退出

        # 将帧转换为二进制数据
        h,w,c = frame.shape
            
        
        frame = cv2.resize(frame,(int(w/3),int(h/3)))
        
        _, img_bytes = cv2.imencode('.jpg', frame)  # 压缩为JPEG格式
        if img_bytes is None:
            continue

        yield img_bytes.tobytes()  # 转为字节流返回
        # await asyncio.sleep(0.05)  # 每秒发送一帧

    cap.release()  # 释放视频资源
        
import uuid
VIDEO_PATH = 'C:\\Users\\admin\\Desktop\\发动机螺孔\\1\\2.avi'
# WebSocket 路由
@router.websocket("/get-video-image/{videopath}")
async def websocket_endpoint(websocket: WebSocket,videopath: str):
    await websocket.accept()
    async for img_bytes in get_images_from_video(VIDEO_PATH):
        frame_id = str(uuid.uuid4())
        result = await detect_and_draw_async(img_bytes)
        result_img_bytes,detect_results = result['image_bytes'],result['detection_results']
        detect_results['frame_id'] = frame_id
        try:
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.send_text(json.dumps(detect_results))
                # 检测结果发送，包含目标检测结果，OK,NG,统计数量

                # 发送图片数据（二进制），附加帧 ID 到头部
                frame_id_bytes = frame_id.encode("utf-8")
                frame_id_length = len(frame_id_bytes).to_bytes(4, byteorder="big")  # 用 4 字节记录 ID 长度
                await websocket.send_bytes(frame_id_length + frame_id_bytes + result_img_bytes)
                # await websocket.send_bytes(result_img_bytes['image_bytes'])

        except RuntimeError as e:
            print(f"WebSocket 错误: {e}")
            break  # 如果遇到错误，退出循环