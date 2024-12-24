from ultralytics import YOLO
from io import BytesIO

import cv2
import numpy as np

import supervision as sv

# 加载YOLOv8模型
model = YOLO("D:\\github\\fastapi-react-example\\backend\\algorithms\\yolov8\\detect\\best.pt")  # 使用你自己的YOLOv8模型路径

def detect_and_draw(image_bytes: bytes) -> bytes:
    """
    目标检测并返回带检测结果的图片字节流。使用supervision绘制OBB框。
    """
    # 将字节数据转换为OpenCV图像
    np_array = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

    # 使用YOLOv8进行目标检测
    result = model(img)[0]

    # 获取检测到的 OBB 框
    detections = sv.Detections.from_ultralytics(result)
    # xyxy = boxes.xyxy.numpy()  # 转换为numpy数组
    # confidences = boxes.conf.numpy()  # 置信度
    # class_ids = boxes.cls.numpy()  # 类别ID
    oriented_box_annotator = sv.OrientedBoxAnnotator()
    annotated_frame = oriented_box_annotator.annotate(
        scene=img.copy(),
        detections=detections
    )

    # 将处理后的图像转换为字节数据
    _, img_encoded = cv2.imencode('.jpg', annotated_frame)
    img_bytes = img_encoded.tobytes()
    
    return img_bytes