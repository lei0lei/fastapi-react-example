import React, { useState } from "react";
import useWebSocket from "react-use-websocket";

const StreamDisplay = () => {
    const [imageSrc, setImageSrc] = useState<string | null>(null);
  
    // 设置 WebSocket 连接
    useWebSocket('ws://localhost:8000/ws/hik/get-cam-stream/0/no.0', {
      onMessage: (event) => {
        const blob = new Blob([event.data], { type: 'image/jpeg' });
        const url = URL.createObjectURL(blob);
        setImageSrc(url);
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
  
export default StreamDisplay;
