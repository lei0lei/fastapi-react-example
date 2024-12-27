import asyncio
import base64
import os

from fastapi import APIRouter, WebSocket, HTTPException
from starlette.websockets import  WebSocketDisconnect, WebSocketState

from algorithms.yolov8.detect.xianxu_detect import detect_and_draw_async  # 导入目标检测函数
from pydantic import BaseModel
from typing import Optional
from fastapi.responses import StreamingResponse
from fastapi.responses import Response
from ctypes import *
import io
import sys
from typing import List, Tuple,Dict
import re
sys.path.append('D:\\MFL\\work\\xianxu\\fastapi-react-example\\backend\\cameras\\hik\\MvImport')
import uuid
from cameras.hik.MvImport.MvCameraControl_class import *
from cameras.hik.MvImport.MvCameraControl_class import *
from cameras.hik.MvImport.MvErrorDefine_const import *
from cameras.hik.MvImport.CameraParams_header import *
from memory_profiler import profile

from cameras.hik.HikCameraOperation_class import *
import asyncio
from datetime import datetime


class CameraStatus(BaseModel):
    name: str = 'Default'
    ip: str = '0.0.0.0'
    index: int = 0
    protocol: str = 'GigE'
    online: bool = False
    grabing: bool = False
    grabing_count: int = 0
    frame_rate: float = 0
    status: bool  = False# True 表示相机打开，False 表示关闭
    registered: bool = False
    last_ping: datetime  # 最后一次在线检查时间
    
    
global obj_cams_operation
obj_cams_operation = None
global cams_status
cams_status = {}

# 更新相机状态
def update_cams_status_on_detect(devList_dc):
    global cams_status
    
    # 获取当前存在的相机 IP 地址列表
    current_indexes = {cam.rank for cam in devList_dc}
    
    # 删除 cams_status 中不存在于 devList_dc 的相机
    cams_status = {index: status for index, status in cams_status.items() if index in current_indexes}

    for cam in devList_dc:
        cam_index = cam.rank  # 使用 int 类型的索引作为字典的键

        # 如果相机已存在
        if cam_index in cams_status:
            existing_cam = cams_status[cam_index]
            # 如果相机的属性有变化，则更新
            
            existing_cam.name = cam.name
            existing_cam.ip = cam.ip
            existing_cam.protocol = cam.protocol
            existing_cam.last_ping = datetime.now()  # 更新最后一次探测时间

        else:
            # 如果相机不存在，新增相机状态
            cams_status[cam_index] = CameraStatus(
                name=cam.name,
                ip=cam.ip,
                index=cam.rank,
                protocol=cam.protocol,
                online=True,  # 假设相机在线
                grabing=False,  # 假设不在取流
                grabing_count=0,  # 初始抓取次数为 0
                frame_rate=0,  # 默认帧率为 0
                status=False,  # 假设相机关闭
                registered=False,
                last_ping=datetime.now()  # 设置最后一次探测时间为当前时间
            )
            
            
def detect_camera():
    '''相机检测
    '''
    devList, devList_dc, deviceList = enum_devices()
    update_cams_status_on_detect(devList_dc)
    return devList, devList_dc, deviceList


def update_cams_status_on_close(nSelCamIndex):
    global cams_status
    if nSelCamIndex is None:
        return None
    
    if nSelCamIndex in cams_status:
        cams_status[nSelCamIndex].grabing = False
        cams_status[nSelCamIndex].status = False
        cams_status[nSelCamIndex].frame_rate = 0


async def close_device(nSelCamIndex=None):
    '''关闭相机
    '''
    global obj_cams_operation
    
    if nSelCamIndex is None:
        return None
    
    if obj_cams_operation:
        obj_cams_operation[nSelCamIndex].Stop_grabbing()
        obj_cams_operation[nSelCamIndex].Close_device()
    
    # obj_cams_operation[nSelCamIndex]=None
    update_cams_status_on_close(nSelCamIndex)


def update_cams_status_on_open(nSelCamIndex):
    global cams_status
    if nSelCamIndex is None:
        return None
    cams_status[nSelCamIndex].status = True
    cams_status[nSelCamIndex].frame_rate = 1
    cams_status[nSelCamIndex].grabing_count = 0

async def open_device(deviceList=None, settings=None, nSelCamIndex=None):
    '''打开设备
    - 检测相机列表
    - 打开相机
    - 更新相机状态
    '''
    global obj_cams_operation
    
    if nSelCamIndex is None:
        nSelCamIndex = 0
    if deviceList is None:
        _,_,deviceList = detect_camera()
        
    if not deviceList:
        raise Exception("未检测到相机设备")
    if obj_cams_operation is None:
        obj_cams_operation = {}
    obj_cams_operation[nSelCamIndex] = CameraOperation(MvCamera(), deviceList, nSelCamIndex)

    ret = obj_cams_operation[nSelCamIndex].Open_device()
    if 0 != ret:
        strError = "Open device failed ret:" + To_hex_str(ret)
        print(strError)
    update_cams_status_on_open(nSelCamIndex)
    # 更新相机状态
    
    
        # else:
        #     op.set_continue_mode()

        # settings = obj_cam_operation.get_param()
        # settings['frameRate'] = 10
        # print(settings)
        # obj_cam_operation.Set_parameter(**settings)
    
    
            # print(f'相机已打开:{op.b_open_device}')
            # op.Start_grabbing()
    # asyncio.run(cam_isopen())

def update_cams_status_on_start_grabbing(nSelCamIndex):
    global cams_status
    cams_status[nSelCamIndex].grabing = True
        

async def cam_start_grabbing(deviceList=None, settings=None, nSelCamIndex=None):
    '''相机开始启用抓流
    '''
    global obj_cams_operation
    if nSelCamIndex is None:
        nSelCamIndex = 0
    obj_cams_operation[nSelCamIndex].set_continue_mode()
    obj_cams_operation[nSelCamIndex].Start_grabbing()

    # 更新相机状态
    update_cams_status_on_start_grabbing(nSelCamIndex)
    
def update_cams_status_on_stream_once(nSelCamIndex,frame_rate):
    global cams_status
    cams_status[nSelCamIndex].grabing_count+=1
    cams_status[nSelCamIndex].frame_rate+=frame_rate
    cams_status[nSelCamIndex].last_ping=datetime.now()
    
async def stream_frames(nSelCamIndex=0):
    '''抓取相机帧
    '''
    global obj_cams_operation
    if nSelCamIndex not in obj_cams_operation:
        raise Exception("相机未打开")
    last_time = None  # 初始化时间
    async for frame_data in obj_cams_operation[nSelCamIndex].grab_frame():
        current_time = time.time()  # 当前时间
        if last_time is None:
            last_time = current_time
            print(f"帧采集时间: {current_time:.6f}")
            continue
        
        frame_interval = current_time - last_time  # 帧间隔
        print(f"帧采集时间: {current_time:.6f}, 帧间隔: {frame_interval:.6f} 秒")
        frame_rate = 1/frame_interval
        update_cams_status_on_stream_once(nSelCamIndex,frame_rate)
        last_time = current_time
        h,w,c = frame_data.shape
            
        
        frame_data = cv2.resize(frame_data,(int(w/3),int(h/3)))
        success, jpg_img = cv2.imencode('.jpg', frame_data)
        if not success:
            raise Exception("图像编码失败")
        yield jpg_img.tobytes()
        # yield frame_data
        await asyncio.sleep(0.01)

def update_cams_status_on_grab_once(nSelCamIndex):
    global cams_status
    cams_status[nSelCamIndex].last_ping=datetime.now()

async def image_frame(nSelCamIndex=0):
    global obj_cams_operation
    if nSelCamIndex not in obj_cams_operation:
        raise Exception("相机未打开")
    last_time = None  # 初始化时间

    frame_data = obj_cams_operation[nSelCamIndex].grab_frame()
    update_cams_status_on_grab_once(nSelCamIndex)
    frame_data = cv2.resize(frame_data,(int(w/3),int(h/3)))
    success, jpg_img = cv2.imencode('.jpg', frame_data)
    return jpg_img.tobytes()


router = APIRouter()
import json
# WebSocket 路由
@router.websocket("/get-camera-stream/{nSelCamIndex}/{algo_registered}")
async def get_camera_stream(websocket: WebSocket, nSelCamIndex: int, algo_registered: str):
    '''相机串流
    '''
    global obj_cams_operation,cams_status
    if obj_cams_operation is None:
        obj_cams_operation ={}
    devList, devList_dc, deviceList = detect_camera()
    
    await websocket.accept()
    if nSelCamIndex not in cams_status:
        assert 'No camera opened'
        
    frame_queue = asyncio.Queue()  # 用于存储帧数据

    try:
        if nSelCamIndex not in obj_cams_operation:
            # 检测相机
            await open_device(deviceList, None, nSelCamIndex)
        await cam_start_grabbing(None, None, nSelCamIndex)

        async for img_bytes in stream_frames(nSelCamIndex):
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
    except WebSocketDisconnect:
        print("客户端已断开连接")
    except Exception as e:
        print(f"WebSocket 错误: {e}")

    finally:
        await close_device(nSelCamIndex)
        await websocket.close()
        
        
@router.get("/get-camera-image/{nSelCamIndex}")
async def get_camera_image(nSelCamIndex: int):
    """
    获取当前相机的图片
    """
    global obj_cams_operation,cams_status
    if obj_cams_operation is None:
        obj_cams_operation ={}
    devList, devList_dc, deviceList = detect_camera()

    if nSelCamIndex not in cams_status:
        assert 'No camera opened'
        
    try:
        
        if nSelCamIndex not in obj_cams_operation:
            # 检测相机
            await open_device(deviceList, None, nSelCamIndex)

        # if cams_status[nSelCamIndex].status is False:
        #     await open_device(deviceList, None, nSelCamIndex)

        await cam_start_grabbing(None, None, nSelCamIndex)
        # 调用 image_frame 获取单帧图片数据
        frame_data = await image_frame(nSelCamIndex)
        # 返回图片的二进制数据，设置响应头为 image/jpeg
        return Response(content=frame_data, media_type="image/jpeg")
    except Exception as e:
        # 捕获并返回错误
        raise HTTPException(status_code=400, detail=str(e))

# ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ====
# 模拟相机状态和参数
camera_status = {
    "is_running": False,
    "ip": "192.168.1.100",
    "info": {"model": "Hikvision-XYZ", "resolution": "1920x1080", "fps": 30},
}

camera_params = {
    "exposure": 100,
    "gain": 1.5,
    "white_balance": "auto",
}


# 请求模型
class CameraRegistration(BaseModel):
    ip: str
    index: int
    protocol: str
    algorithm: List[str]



# 设置相机参数的模型
class CameraParams(BaseModel):
    exposure: Optional[int] = None
    gain: Optional[float] = None
    white_balance: Optional[str] = None

# 相机信息
class CameraInfo(BaseModel):
    index: int
    protocol: str
    name: str
    ip: str
    

@router.get("/scan-camera", response_model=Dict[str, List[CameraInfo]])
async def scan_camera():
    """
    检测相机并返回相机IP和信息
    """
    devList, devList_dc, deviceList = detect_camera()  # 调用相机检测函数
    # 将返回的设备列表转换为 CameraInfo 数据模型
    # 解析相机列表信息
    
    if len(devList_dc) == 0:
        return {"device_descriptions": [], "message": "No camera detected"}
    else:
        device_descriptions = [
            CameraInfo(index=cam.rank, protocol=cam.protocol, name=cam.name, ip=cam.ip)
            for cam in devList_dc
        ]
        message = f'{len(devList_dc)} camera detected'
        return {"device_descriptions": device_descriptions,"message": message}

@router.get("/get-camera-status")
async def get_camera_status():
    """
    获取相机状态
    """
    if not camera_status["ip"]:
        raise HTTPException(status_code=404, detail="No camera detected")
    return {"ip": camera_status["ip"], "info": camera_status["info"]}



@router.post("/control-camera")
async def control_camera(action: str):
    """
    启动或停止相机
    :param action: "start" 或 "stop"
    """
    if action == "start":
        if camera_status["is_running"]:
            raise HTTPException(status_code=400, detail="Camera is already running")
        camera_status["is_running"] = True
        return {"message": "Camera started successfully"}
    elif action == "stop":
        if not camera_status["is_running"]:
            raise HTTPException(status_code=400, detail="Camera is not running")
        camera_status["is_running"] = False
        return {"message": "Camera stopped successfully"}
    else:
        raise HTTPException(status_code=400, detail="Invalid action. Use 'start' or 'stop'")


@router.put("/set-camera-params")
async def set_camera_parameters(params: CameraParams):
    """
    设置相机参数
    """
    updated_params = {}
    for key, value in params.dict().items():
        if value is not None:
            camera_params[key] = value
            updated_params[key] = value
    return {"message": "Camera parameters updated successfully", "updated_params": updated_params}

@router.get("/get-camera-params")
async def get_camera_parameters():
    """
    获取当前相机的参数
    """
    return {"camera_parameters": camera_params}

@router.post("/register-camera")
async def register_camera(camera: CameraRegistration):
    '''注册相机
    '''
    camera_id = f"camera_{len(cameras) + 1}"
    cameras[camera_id] = {
        "ip": camera.ip,
        "status": "stopped",
        "parameters": {"exposure": 100, "gain": 1.5, "white_balance": "auto"},
        "logs": [],
    }
    return {"message": f"Camera {camera_id} registered successfully", "camera_id": camera_id}

@router.delete("/{camera_id}/delete-camera")
async def delete_camera(camera_id: str):
    '''删除注册的相机
    '''
    if camera_id not in cameras:
        raise HTTPException(status_code=404, detail="Camera not found")
    del cameras[camera_id]
    return {"message": f"Camera {camera_id} deleted successfully"}

@router.post("/restart-camera")
async def restart_camera(camera_id: str):
    '''重启相机
    '''
    if camera_id not in cameras:
        raise HTTPException(status_code=404, detail="Camera not found")
    cameras[camera_id]["status"] = "stopped"
    cameras[camera_id]["status"] = "running"
    return {"message": f"Camera {camera_id} restarted successfully"}

@router.post("/{camera_id}/stream/start")
async def start_camera_stream(camera_id: str):
    '''启动相机流
    '''
    if camera_id not in cameras:
        raise HTTPException(status_code=404, detail="Camera not found")
    cameras[camera_id]["status"] = "streaming"
    return {"message": f"Stream for camera {camera_id} started"}

@router.post("/{camera_id}/stream/stop")
async def stop_camera_stream(camera_id: str):
    '''中止相机流
    '''
    if camera_id not in cameras:
        raise HTTPException(status_code=404, detail="Camera not found")
    cameras[camera_id]["status"] = "stopped"
    return {"message": f"Stream for camera {camera_id} stopped"}

@router.get("/{camera_id}/logs")
async def get_camera_logs(camera_id: str):
    '''获取相机log
    '''
    if camera_id not in cameras:
        raise HTTPException(status_code=404, detail="Camera not found")
    return {"logs": cameras[camera_id]["logs"]}

@router.post("/{camera_id}/diagnose")
async def diagnose_camera(camera_id: str):
    '''相机诊断
    '''
    if camera_id not in cameras:
        raise HTTPException(status_code=404, detail="Camera not found")
    # 模拟诊断结果
    return {"diagnose": f"Camera {camera_id} is functioning properly"}

class AlgorithmRegistration(BaseModel):
    name: str
    description: Optional[str] = None
    parameters: Optional[dict] = None

@router.post("/{camera_id}/algorithm/register")
async def register_algorithm(camera_id: str, algorithm: AlgorithmRegistration):
    """相机注册算法， 返回绘图后的结果，或者原图及算法处理结果
    """
    if camera_id not in cameras:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    # 如果该相机还没有注册算法，则初始化算法列表
    if "algorithms" not in cameras[camera_id]:
        cameras[camera_id]["algorithms"] = []
    
    # 检查是否已经存在同名算法
    for existing_algo in cameras[camera_id]["algorithms"]:
        if existing_algo["name"] == algorithm.name:
            raise HTTPException(status_code=400, detail="Algorithm already registered")
    
    # 注册新算法
    algo_data = {
        "name": algorithm.name,
        "description": algorithm.description,
        "parameters": algorithm.parameters or {}
    }
    cameras[camera_id]["algorithms"].append(algo_data)
    
    return {"message": f"Algorithm '{algorithm.name}' registered successfully", "algorithm": algo_data}


@router.get("/{camera_id}/performance")
async def get_camera_performance(camera_id: str):
    '''
    获取相机帧率等信息
    '''
    if camera_id not in cameras:
        raise HTTPException(status_code=404, detail="Camera not found")
    return {"logs": cameras[camera_id]["logs"]}

@router.get("/{camera_id}/hardware-info")
async def get_camera_hardware_info(camera_id: str):
    '''
    获取相机硬件信息
    '''
    if camera_id not in cameras:
        raise HTTPException(status_code=404, detail="Camera not found")
    return {"logs": cameras[camera_id]["logs"]}

# ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ====

if __name__ == '__main__':
    a,b,c = detect_camera()
    print(cams_status)
    open_device(c,None,0)
    print(cams_status)
    cam_start_grabbing(None,None,0)
    print(cams_status)
    close_device(0)
    print(cams_status)
    # grab_once()
    # open_device()