import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  LinearProgress,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
} from '@mui/material';
import {
  Refresh,
  CheckCircle,
  Error,
  Warning,
  Info,
  Storage,
  Cloud,
  Memory,
  Speed,
  NetworkCheck,
} from '@mui/icons-material';

interface ServiceStatus {
  name: string;
  status: 'running' | 'stopped' | 'error';
  uptime: string;
  lastCheck: string;
}

const SystemMonitor: React.FC = () => {
  const [services, setServices] = useState<ServiceStatus[]>([]);
  const [recentLogs, setRecentLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSystemData();
    const interval = setInterval(fetchSystemData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchSystemData = async () => {
    try {
      // 서비스 상태 확인
      const serviceList: ServiceStatus[] = [];
      
      // Cloud Run 상태
      try {
        const healthResponse = await fetch('/api/health');
        if (healthResponse.ok) {
          serviceList.push({
            name: 'Cloud Run (API)',
            status: 'running',
            uptime: 'N/A',
            lastCheck: new Date().toLocaleTimeString(),
          });
        } else {
          serviceList.push({
            name: 'Cloud Run (API)',
            status: 'stopped',
            uptime: 'N/A',
            lastCheck: new Date().toLocaleTimeString(),
          });
        }
      } catch {
        serviceList.push({
          name: 'Cloud Run (API)',
          status: 'error',
          uptime: 'N/A',
          lastCheck: new Date().toLocaleTimeString(),
        });
      }

      // Vertex AI 상태
      try {
        const indexResponse = await fetch('/api/vector-index/status');
        if (indexResponse.ok) {
          serviceList.push({
            name: 'Vertex AI',
            status: 'running',
            uptime: 'N/A',
            lastCheck: new Date().toLocaleTimeString(),
          });
        } else {
          serviceList.push({
            name: 'Vertex AI',
            status: 'error',
            uptime: 'N/A',
            lastCheck: new Date().toLocaleTimeString(),
          });
        }
      } catch {
        serviceList.push({
          name: 'Vertex AI',
          status: 'error',
          uptime: 'N/A',
          lastCheck: new Date().toLocaleTimeString(),
        });
      }

      // FTP 연결 상태
      try {
        const ftpResponse = await fetch('/api/ftp/connection-info');
        if (ftpResponse.ok) {
          const ftpData = await ftpResponse.json();
          serviceList.push({
            name: 'FTP 연결',
            status: ftpData.connected ? 'running' : 'stopped',
            uptime: 'N/A',
            lastCheck: new Date().toLocaleTimeString(),
          });
        }
      } catch {
        serviceList.push({
          name: 'FTP 연결',
          status: 'stopped',
          uptime: 'N/A',
          lastCheck: new Date().toLocaleTimeString(),
        });
      }

      // Cloud SQL 상태
      try {
        const articlesResponse = await fetch('/api/articles?limit=1');
        if (articlesResponse.ok) {
          serviceList.push({
            name: 'Cloud SQL',
            status: 'running',
            uptime: 'N/A',
            lastCheck: new Date().toLocaleTimeString(),
          });
        } else {
          serviceList.push({
            name: 'Cloud SQL',
            status: 'error',
            uptime: 'N/A',
            lastCheck: new Date().toLocaleTimeString(),
          });
        }
      } catch {
        serviceList.push({
          name: 'Cloud SQL',
          status: 'error',
          uptime: 'N/A',
          lastCheck: new Date().toLocaleTimeString(),
        });
      }

      setServices(serviceList);

      // 처리 로그 가져오기
      try {
        const logsResponse = await fetch('/api/processing-logs?limit=10');
        if (logsResponse.ok) {
          const logsData = await logsResponse.json();
          if (logsData && logsData.logs) {
            const formattedLogs = logsData.logs.map((log: any) => ({
              id: log.id,
              timestamp: new Date(log.timestamp).toLocaleString(),
              level: log.status === 'success' ? 'INFO' : log.status === 'error' ? 'ERROR' : 'WARNING',
              message: log.message || '작업 수행',
              service: log.process_type || 'System',
            }));
            setRecentLogs(formattedLogs);
          }
        }
      } catch (error) {
        console.error('로그 가져오기 실패:', error);
      }

      setLoading(false);
    } catch (error) {
      console.error('시스템 데이터 가져오기 실패:', error);
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
      case 'good':
        return 'success';
      case 'warning':
        return 'warning';
      case 'stopped':
      case 'error':
        return 'error';
      default:
        return 'info';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running':
      case 'good':
        return <CheckCircle />;
      case 'warning':
        return <Warning />;
      case 'stopped':
      case 'error':
        return <Error />;
      default:
        return <Info />;
    }
  };

  const getLogColor = (level: string) => {
    switch (level) {
      case 'INFO':
        return 'info';
      case 'WARNING':
        return 'warning';
      case 'ERROR':
        return 'error';
      default:
        return 'default';
    }
  };

  const handleRefresh = () => {
    fetchSystemData();
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 600 }}>
          시스템 모니터
        </Typography>
        <IconButton onClick={handleRefresh} disabled={loading}>
          <Refresh />
        </IconButton>
      </Box>

      {loading && (
        <Box sx={{ mb: 3 }}>
          <LinearProgress />
          <Typography variant="body2" sx={{ mt: 1 }} align="center">
            데이터를 불러오는 중...
          </Typography>
        </Box>
      )}

      <Box sx={{ display: 'flex', gap: 3 }}>
        {/* 서비스 상태 */}
        <Box sx={{ flex: 1 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                서비스 상태
              </Typography>
              {services.length === 0 ? (
                <Alert severity="info">
                  서비스 상태를 확인할 수 없습니다.
                </Alert>
              ) : (
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>서비스</TableCell>
                        <TableCell>상태</TableCell>
                        <TableCell>가동시간</TableCell>
                        <TableCell>마지막 확인</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {services.map((service) => (
                        <TableRow key={service.name}>
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              {service.name === 'Vertex AI' && <Cloud />}
                              {service.name.includes('Cloud Run') && <Speed />}
                              {service.name === 'Cloud SQL' && <Storage />}
                              {service.name === 'FTP 연결' && <NetworkCheck />}
                              <Typography variant="body2">
                                {service.name}
                              </Typography>
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Chip
                              icon={getStatusIcon(service.status)}
                              label={service.status === 'running' ? '실행 중' : service.status === 'stopped' ? '중지됨' : '오류'}
                              color={getStatusColor(service.status) as any}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              {service.uptime}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              {service.lastCheck}
                            </Typography>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </CardContent>
          </Card>
        </Box>

        {/* 최근 로그 */}
        <Box sx={{ flex: 1 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                최근 로그
              </Typography>
              {recentLogs.length === 0 ? (
                <Alert severity="info">
                  로그가 없습니다.
                </Alert>
              ) : (
                <List dense>
                  {recentLogs.map((log, index) => (
                    <React.Fragment key={log.id || index}>
                      <ListItem>
                        <ListItemIcon>
                          {getStatusIcon(log.level.toLowerCase())}
                        </ListItemIcon>
                        <ListItemText
                          primary={
                            <Box>
                              <Typography variant="body2" sx={{ fontWeight: 600 }}>
                                {log.message}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                {log.timestamp} • {log.service}
                              </Typography>
                            </Box>
                          }
                        />
                      </ListItem>
                      {index < recentLogs.length - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
              )}
            </CardContent>
          </Card>
        </Box>
      </Box>
    </Box>
  );
};

export default SystemMonitor;
