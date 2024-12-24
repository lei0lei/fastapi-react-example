import   ImageDisplay  from "@/components/image-display"
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {Progress } from "@/components/ui/progress";



export function DisplayPageSidebar(){
  return (

    <div>
      <p>Display</p>
    </div>
  )
}

const StatusBadge = ({ status }: { status: 'OK' | 'NG' }) => {
  return (
    <Badge
      color={status === 'OK' ? 'green' : 'red'}
      variant="solid"
      size="lg"
      style={{ margin: '20px 0' }}
    >
      {status}
    </Badge>
  );
};

const LogList = () => {
  const logs = [
    '系统启动成功',
    '开始接收图像数据',
    '图像处理完毕',
    '检测完毕，合格',
  ];

  return (
    <Card style={{ marginTop: '20px' }}>
      <p style={{ fontSize: '1.1rem', fontWeight: 'bold' }}>日志</p>
      <ul style={{ padding: '10px 0' }}>
        {logs.map((log, index) => (
          <li key={index} style={{ marginBottom: '10px' }}>
            <p>{log}</p>
          </li>
        ))}
      </ul>
    </Card>
  );
};

const QualityRate = () => {
  const qualityRate = 98; // 模拟合格率数据

  return (
    <Card style={{ marginTop: '20px' }}>
      <p style={{ fontSize: '1.1rem', fontWeight: 'bold' }}>合格率</p>
      <Progress value={qualityRate} max={100} style={{ marginTop: '10px' }} />
      <p style={{ marginTop: '10px' }}>{qualityRate}%</p>
    </Card>
  );
};


const DisplayPage = () => {
  return (
    <div style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div style={{ flex: 1, display: 'flex', flexDirection: 'row', gap: '20px' }}>
        <div style={{ flex: 2 }}>
          <ImageDisplay />
        </div>
        <div style={{ flex: 1 }}>
          <StatusBadge status="OK" />
          <LogList />
          <QualityRate />
        </div>
      </div>
    </div>
  );
};

export default DisplayPage;