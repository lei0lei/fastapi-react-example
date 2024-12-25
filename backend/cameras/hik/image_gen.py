import asyncio
import base64
import os

from fastapi import APIRouter, WebSocket
from algorithms.yolov8.detect.xianxu_detect import detect_and_draw_async  # 导入目标检测函数


from ctypes import *

import sys
sys.path.append('D:\\MFL\\work\\xianxu\\fastapi-react-example\\backend\\cameras\\hik\\MvImport')

from cameras.hik.MvImport.MvCameraControl_class import *
from cameras.hik.MvImport.MvCameraControl_class import *
from cameras.hik.MvImport.MvErrorDefine_const import *
from cameras.hik.MvImport.CameraParams_header import *
from memory_profiler import profile

from cameras.hik.HikCameraOperation_class import *
import asyncio

global cam
cam = MvCamera()
global obj_cam_operation
obj_cam_operation = None
global settings
settings = {}


def detect_camera():
    devList, devList_dc, deviceList = enum_devices()
    
    return devList, devList_dc, deviceList


async def close_device():
    global obj_cam_operation
    if obj_cam_operation:
        obj_cam_operation.Stop_grabbing()
        obj_cam_operation.Close_device()
        obj_cam_operation = None


def grab_once():
    print(f'grab once')
    global obj_cam_operation
    ret = obj_cam_operation.Save_Bmp()
    if ret != MV_OK:
        strError = "Save BMP failed ret:" + To_hex_str(ret)

    else:
        print("Save image success")

async def open_device():
    global obj_cam_operation,settings
    nSelCamIndex = 0
    _,_,deviceList = detect_camera()
    if not deviceList:
        raise Exception("未检测到相机设备")
    
    obj_cam_operation = CameraOperation(cam, deviceList, nSelCamIndex)
    
    ret = obj_cam_operation.Open_device()
    if 0 != ret:
        strError = "Open device failed ret:" + To_hex_str(ret)
        print(strError)
        
    else:
        obj_cam_operation.set_continue_mode()

        settings = obj_cam_operation.get_param()
        settings['frameRate'] = 9
        print(settings)
        obj_cam_operation.Set_parameter(**settings)
    
    
        print(f'相机已打开:{obj_cam_operation.b_open_device}')
        obj_cam_operation.Start_grabbing()
    # asyncio.run(cam_isopen())
      
# async def cam_isopen():
#     # self.isopen = True
#     print(f'cam is open {obj_cam_operation.b_open_device}, ready to show')
    
    
async def stream_frames():
    global obj_cam_operation
    if not obj_cam_operation:
        raise Exception("相机未打开")
    last_time = None  # 初始化时间
    async for frame_data in obj_cam_operation.grab_frame():
        current_time = time.time()  # 当前时间
        if last_time is None:
            last_time = current_time
            print(f"帧采集时间: {current_time:.6f}")
            continue
        
        frame_interval = current_time - last_time  # 帧间隔
        print(f"帧采集时间: {current_time:.6f}, 帧间隔: {frame_interval:.6f} 秒")
        last_time = current_time
        h,w,c = frame_data.shape
            
        
        frame_data = cv2.resize(frame_data,(int(w/3),int(h/3)))
        success, jpg_img = cv2.imencode('.jpg', frame_data)
        if not success:
            raise Exception("图像编码失败")
        yield jpg_img.tobytes()
        # yield frame_data
        await asyncio.sleep(0.01)

router = APIRouter()

# WebSocket 路由
@router.websocket("/get-hik-image")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        if obj_cam_operation is None:
            await open_device()

        async for img_bytes in stream_frames():
            result_img_bytes = await detect_and_draw_async(img_bytes)
            await websocket.send_bytes(img_bytes)
    except Exception as e:
        print(f"WebSocket 错误: {e}")

    finally:
        await close_device()
        await websocket.close()


if __name__ == '__main__':
    a,b,c = detect_camera()
    # grab_once()
    open_device()