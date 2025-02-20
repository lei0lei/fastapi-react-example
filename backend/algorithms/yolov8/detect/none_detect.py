from ultralytics import YOLO
from io import BytesIO
import asyncio
import cv2
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import supervision as sv
# 全局线程池
thread_pool = ThreadPoolExecutor()
# 加载YOLOv8模型
# model = YOLO("D:\\github\\fastapi-react-example\\backend\\algorithms\\yolov8\\detect\\best.pt")  # 使用你自己的YOLOv8模型路径
# 异步目标检测函数
async def detect_and_draw_async(image_bytes: bytes) -> dict:
    """
    异步目标检测并返回带检测结果的图片字节流。
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(thread_pool, detect_and_draw, image_bytes)

# 原始目标检测函数
def detect_and_draw(image_bytes: bytes) -> dict:
    """
    目标检测并返回带检测结果的图片字节流和检测结果。使用supervision绘制OBB框。
    """
    # 将字节数据转换为OpenCV图像
    np_array = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
    

    # 将处理后的图像转换为字节数据
    _, img_encoded = cv2.imencode('.jpg', img)
    img_bytes = img_encoded.tobytes()

    # 构建检测结果 JSON
    detection_results = {
        "type": 'ALGO-NONE',  # 算法类型
        "detections": [],  # 目标检测的结果列表
        "image_size": '640',  # 图片尺寸
        "reslut_OK": 'OK'
    }

    
    detection_results["detections"]=[]
            
    return {
        "image_bytes": img_bytes,
        "detection_results": detection_results
    }


def detect_result_check(detections, check):
    pass