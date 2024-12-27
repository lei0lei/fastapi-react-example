import React, { useState } from "react";
import useWebSocket from "react-use-websocket";

const ImageDisplay = () => {
    const [imageSrc, setImageSrc] = useState<string | null>(null);
    const [detectionResult, setDetectionResult] = useState<any>(null);

    // 设置 WebSocket 连接
    useWebSocket('ws://localhost:8000/ws/hik/get-camera-stream/0/no.0', {
      onMessage: async (event) => {
        if (typeof event.data === 'string') {
        // 处理 JSON 数据
        const jsonData = JSON.parse(event.data);
        if (jsonData.type && jsonData.type.startsWith("ALGO")) {
          // console.log("Detection Result:", jsonData);
          setDetectionResult(jsonData);
        }
      } else if (event.data instanceof Blob) {
        // 处理二进制图片数据
        try {
          // 使用 arrayBuffer() 解析二进制数据
          const arrayBuffer = await event.data.arrayBuffer();
          const dataView = new DataView(arrayBuffer);
  
          // 解析 UUID 长度
          const uuidLength = dataView.getUint32(0, false); // 假设使用大端序
          const uuidBytes = new Uint8Array(arrayBuffer, 4, uuidLength);
          const uuid = new TextDecoder().decode(uuidBytes); // 将 UUID 转换为字符串
  
          // 获取图片数据
          const imageBytes = new Blob(
            [arrayBuffer.slice(4 + uuidLength)],
            { type: 'image/jpeg' }
          );
          // 释放旧的对象 URL（如果存在）
          if (imageSrc) {
            URL.revokeObjectURL(imageSrc);
          }
          // 创建图片 URL
          const imageUrl = URL.createObjectURL(imageBytes);
          setImageSrc(imageUrl);
  
          // console.log(`Received frame with UUID: ${uuid}`);
          // 可选：释放 URL 资源
          // URL.revokeObjectURL(imageUrl);
        } catch (error) {
          console.error("Error parsing WebSocket message:", error);
        }
      }
    },
    shouldReconnect: () => true,
    });
  
    return (
        <div
        style={{
          textAlign: 'center',
          width: '100%',
          maxHeight: '75vh', // 限制最大高度为视口的 80%
          overflow: 'hidden', // 防止出现滚动条
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
        }}
      >
        {imageSrc ? (
          <img
            src={imageSrc}
            alt="Real-time"
            style={{
              maxWidth: '100%',
              height: 'auto',
              objectFit: 'contain', // 保持图像比例，避免裁剪
              borderRadius: '8px',
              boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
            }}
          />
        ) : (
          <p>等待图片加载...</p>
        )}
      </div>
    );
  };
  
export default ImageDisplay;
