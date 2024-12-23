'''
date: 20240419
by: lei.lei.fan.meng@gmail.com
update:   1. 相机连接，开启，关闭，取流等操作

'''
import sys
sys.path.append('.//demo//hik//MvImport')

from CamOperation_class import CameraOperation
from MvCameraControl_class import *
from MvErrorDefine_const import *
from CameraParams_header import *


import ctypes
# Decoding Characters
def decoding_char(c_ubyte_value):
    c_char_p_value = ctypes.cast(c_ubyte_value, ctypes.c_char_p)
    try:
        decode_str = c_char_p_value.value.decode('gbk')  # Chinese characters
    except UnicodeDecodeError:
        decode_str = str(c_char_p_value.value)
    return decode_str

# ch:枚举相机 | en:enum devices
def enum_devices():
    # MV_CC_DEVICE_INFO_LIST是定义在CameraParams_header中的底层结构体
    deviceList = MV_CC_DEVICE_INFO_LIST()
    # MV_GIGE_DEVICE和MV_USB_DEVICE是定义在CameraParams_const中的常量，表示GiGE设备或者usb设备
    # 直接调用dll,侦测结果保存在deviceList,包含了nDeviceNum和pDeviceInfo
    ret = MvCamera.MV_CC_EnumDevices(MV_GIGE_DEVICE | MV_USB_DEVICE, deviceList)
    # ret为0表示找到了设备
    if ret != 0:
        strError = "Enum devices fail! ret = :" + ToHexStr(ret)
        return ret

    if deviceList.nDeviceNum == 0:
        return ret
    print("Find %d devices!" % deviceList.nDeviceNum)

    devList = []
    for i in range(0, deviceList.nDeviceNum):
        mvcc_dev_info = cast(deviceList.pDeviceInfo[i], POINTER(MV_CC_DEVICE_INFO)).contents
        if mvcc_dev_info.nTLayerType == MV_GIGE_DEVICE:
            print("\ngige device: [%d]" % i)
            user_defined_name = decoding_char(mvcc_dev_info.SpecialInfo.stGigEInfo.chUserDefinedName)
            model_name = decoding_char(mvcc_dev_info.SpecialInfo.stGigEInfo.chModelName)
            print("device user define name: " + user_defined_name)
            print("device model name: " + model_name)

            nip1 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0xff000000) >> 24)
            nip2 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x00ff0000) >> 16)
            nip3 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x0000ff00) >> 8)
            nip4 = (mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x000000ff)
            print("current ip: %d.%d.%d.%d " % (nip1, nip2, nip3, nip4))
            devList.append(
                    "[" + str(i) + "]GigE: " + user_defined_name + " " + model_name + "(" + str(nip1) + "." + str(
                        nip2) + "." + str(nip3) + "." + str(nip4) + ")")
        elif mvcc_dev_info.nTLayerType == MV_USB_DEVICE:
            print("\nu3v device: [%d]" % i)
            user_defined_name = decoding_char(mvcc_dev_info.SpecialInfo.stUsb3VInfo.chUserDefinedName)
            model_name = decoding_char(mvcc_dev_info.SpecialInfo.stUsb3VInfo.chModelName)
            print("device user define name: " + user_defined_name)
            print("device model name: " + model_name)

            strSerialNumber = ""
            for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chSerialNumber:
                if per == 0:
                    break
                strSerialNumber = strSerialNumber + chr(per)
            print("user serial number: " + strSerialNumber)
            devList.append("[" + str(i) + "]USB: " + user_defined_name + " " + model_name
                               + "(" + str(strSerialNumber) + ")")
    return deviceList
# 将返回的错误码转换为十六进制显示
def ToHexStr(num):
    chaDic = {10: 'a', 11: 'b', 12: 'c', 13: 'd', 14: 'e', 15: 'f'}
    hexStr = ""
    if num < 0:
        num = num + 2 ** 32
    while num >= 16:
        digit = num % 16
        hexStr = chaDic.get(digit, str(digit)) + hexStr
        num //= 16
    hexStr = chaDic.get(num, str(num)) + hexStr
    return hexStr

# ch:打开相机 | en:open device
def open_device(deviceList, cam, isOpen = False):
    """打开相机

    Args:
        deviceList (_type_): 通过enum_device得到的MV_CC_DEVICE_INFO_LIST对象
        cam (_type_): mvcamera对象
        isOpen (bool, optional): 相机是否已打开. Defaults to False.

    Returns:
        _type_: _description_
    """    
    if isOpen:
            # QMessageBox.warning(mainWindow, "Error", 'Camera is Running!', QMessageBox.Ok)
        return MV_E_CALLORDER

    nSelCamIndex = 0#ui.ComboDevices.currentIndex()
    if nSelCamIndex < 0:
            # QMessageBox.warning(mainWindow, "Error", 'Please select a camera!', QMessageBox.Ok)
        return MV_E_CALLORDER

    obj_cam_operation = CameraOperation(cam, deviceList, nSelCamIndex)
    ret = obj_cam_operation.Open_device()
    # print(ret)
    if 0 != ret:
        strError = "Open device failed ret:" + ToHexStr(ret)
            # QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
        isOpen = False
    else:
        set_continue_mode(obj_cam_operation)

        get_param(obj_cam_operation)

        isOpen = True
        enable_controls()


# ch: 获取参数 | en:get param
def get_param(obj_cam_operation):
    ret = obj_cam_operation.Get_parameter()
    if ret != MV_OK:
        strError = "Get param failed ret:" + ToHexStr(ret)
        # QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
    # else:
    #     ui.edtExposureTime.setText("{0:.2f}".format(obj_cam_operation.exposure_time))
    #     ui.edtGain.setText("{0:.2f}".format(obj_cam_operation.gain))
    #     ui.edtFrameRate.setText("{0:.2f}".format(obj_cam_operation.frame_rate))

# ch: 设置参数 | en:set param
def set_param(f,e,g):
    frame_rate = f#ui.edtFrameRate.text()
    exposure = e#ui.edtExposureTime.text()
    gain = g#ui.edtGain.text()

    if is_float(frame_rate)!=True or is_float(exposure)!=True or is_float(gain)!=True:
        strError = "Set param failed ret:" + ToHexStr(MV_E_PARAMETER)
        # QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
        return MV_E_PARAMETER
        
    ret = obj_cam_operation.Set_parameter(frame_rate, exposure, gain)
    if ret != MV_OK:
        strError = "Set param failed ret:" + ToHexStr(ret)
        # QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)

    return MV_OK

def enable_controls():
    global isGrabbing
    global isOpen

    # 先设置group的状态，再单独设置各控件状态
    # ui.groupGrab.setEnabled(isOpen)
    # ui.groupParam.setEnabled(isOpen)

    # ui.bnOpen.setEnabled(not isOpen)
    # ui.bnClose.setEnabled(isOpen)

    # ui.bnStart.setEnabled(isOpen and (not isGrabbing))
    # ui.bnStop.setEnabled(isOpen and isGrabbing)
    # ui.bnSoftwareTrigger.setEnabled(isGrabbing and ui.radioTriggerMode.isChecked())

    # ui.bnSaveImage.setEnabled(isOpen and isGrabbing)
    
    
# 获取选取设备信息的索引，通过[]之间的字符去解析
def TxtWrapBy(start_str, end, all):
    start = all.find(start_str)
    if start >= 0:
        start += len(start_str)
        end = all.find(end, start)
        if end >= 0:
            return all[start:end].strip()


# ch:开始取流 | en:Start grab image
def start_grabbing():
    global obj_cam_operation
    global isGrabbing

    ret = obj_cam_operation.Start_grabbing(ui.widgetDisplay.winId())
    if ret != 0:
        strError = "Start grabbing failed ret:" + ToHexStr(ret)
        # QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
    else:
        isGrabbing = True
        enable_controls()

# ch:停止取流 | en:Stop grab image
def stop_grabbing():
    global obj_cam_operation
    global isGrabbing
    ret = obj_cam_operation.Stop_grabbing()
    if ret != 0:
        strError = "Stop grabbing failed ret:" + ToHexStr(ret)
        # QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
    else:
        isGrabbing = False
        enable_controls()

# ch:关闭设备 | Close device
def close_device():
    global isOpen
    global isGrabbing
    global obj_cam_operation

    if isOpen:
        obj_cam_operation.Close_device()
        isOpen = False

    isGrabbing = False

    enable_controls()

# ch:设置触发模式 | en:set trigger mode
def set_continue_mode(obj_cam_operation):
    strError = None

    ret = obj_cam_operation.Set_trigger_mode(False)
    if ret != 0:
        strError = "Set continue mode failed ret:" + ToHexStr(ret) + " mode is " + str(is_trigger_mode)
    #     QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
    # else:
    #     ui.radioContinueMode.setChecked(True)
    #     ui.radioTriggerMode.setChecked(False)
    #     ui.bnSoftwareTrigger.setEnabled(False)


# ch:设置软触发模式 | en:set software trigger mode
def set_software_trigger_mode():

    ret = obj_cam_operation.Set_trigger_mode(True)
    if ret != 0:
        strError = "Set trigger mode failed ret:" + ToHexStr(ret)
    #     QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
    # else:
    #     ui.radioContinueMode.setChecked(False)
    #     ui.radioTriggerMode.setChecked(True)
    #     ui.bnSoftwareTrigger.setEnabled(isGrabbing)

# ch:设置触发命令 | en:set trigger software
def trigger_once():
    ret = obj_cam_operation.Trigger_once()
    if ret != 0:
        strError = "TriggerSoftware failed ret:" + ToHexStr(ret)
        # QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)

# ch:存图 | en:save image
def save_bmp():
    ret = obj_cam_operation.Save_Bmp()
    if ret != MV_OK:
        strError = "Save BMP failed ret:" + ToHexStr(ret)
        # QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
    else:
        print("Save image success")
        
def is_float(str):
    try:
        float(str)
        return True
    except ValueError:
        return False



if __name__ == '__main__':
    # global deviceList
    # global cam
    # 相机对象，定义在mvimport中的MvCameraControl_class中
    cam = MvCamera()
    # global nSelCamIndex
    # global obj_cam_operation
    obj_cam_operation = 0
    # global isOpen
    isOpen = False
    # global isGrabbing
    isGrabbing = False
    # global isCalibMode  # 是否是标定模式（获取原始图像）
    isCalibMode = True
    # 设备检测
    deviceList = enum_devices()
    open_device(deviceList,cam )