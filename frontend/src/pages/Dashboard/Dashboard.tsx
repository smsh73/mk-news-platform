import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  LinearProgress,
  Chip,
  Button,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Alert,
} from '@mui/material';
import {
  TrendingUp,
  Storage,
  Search,
  CloudUpload,
  CheckCircle,
  Error,
  Warning,
  Info,
} from '@mui/icons-material';

interface SystemStatus {
  vertexAI: 'active' | 'inactive' | 'error';
  cloudRun: 'active' | 'inactive' | 'error';
  cloudSQL: 'active' | 'inactive' | 'error';
  ftpConnection: 'connected' | 'disconnected' | 'error';
}

interface DashboardStats {
  totalArticles: number;
  processedToday: number;
  vectorIndexes: number;
  ftpFiles: number;
}

interface RecentActivity {
  id: string;
  action: string;
  time: string;
  status: 'success' | 'info' | 'warning' | 'error';
}

const Dashboard: React.FC = () => {
  const [systemStatus, setSystemStatus] = useState<SystemStatus>({
    vertexAI: 'inactive',
    cloudRun: 'inactive',
    cloudSQL: 'inactive',
    ftpConnection: 'disconnected',
  });

  const [stats, setStats] = useState<DashboardStats>({
    totalArticles: 0,
    processedToday: 0,
    vectorIndexes: 0,
    ftpFiles: 0,
  });

  const [recentActivities, setRecentActivities] = useState<RecentActivity[]>([]);
  const [loading, setLoading] = useState(true);

  // 컴포넌트 마운트 시 실제 데이터 가져오기
  useEffect(() => {
    fetchDashboardData();
    
    // 30초마다 데이터 갱신
    const interval = setInterval(fetchDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      // 시스템 상태 확인 - Cloud Run
      try {
        const healthResponse = await fetch('/api/health');
        if (healthResponse.ok) {
          setSystemStatus(prev => ({
            ...prev,
            cloudRun: 'active',
          }));
        } else {
          setSystemStatus(prev => ({
            ...prev,
            cloudRun: 'error',
          }));
        }
      } catch (error) {
        setSystemStatus(prev => ({
          ...prev,
          cloudRun: 'error',
        }));
      }

      // 통계 정보 가져오기
      const statsResponse = await fetch('/api/stats');
      if (statsResponse.ok) {
        const statsData = await statsResponse.json();
        if (statsData) {
          setStats({
            totalArticles: statsData.total_articles || 0,
            processedToday: statsData.processed_today || 0,
            vectorIndexes: statsData.vector_indexes || 0,
            ftpFiles: statsData.ftp_files || 0,
          });
        }
      }

      // FTP 연결 정보 가져오기
      try {
        const ftpResponse = await fetch('/api/ftp/connection-info');
        if (ftpResponse.ok) {
          const ftpData = await ftpResponse.json();
          // 백엔드는 success 필드 없이 connected 필드만 반환함
          if (ftpData) {
            setSystemStatus(prev => ({
              ...prev,
              ftpConnection: ftpData.connected ? 'connected' : 'disconnected',
            }));

            // FTP 파일 수 가져오기
            if (ftpData.connected) {
              try {
                const ftpFilesResponse = await fetch('/api/ftp/files');
                if (ftpFilesResponse.ok) {
                  const ftpFilesData = await ftpFilesResponse.json();
                  if (ftpFilesData && ftpFilesData.files) {
                    setStats(prev => ({
                      ...prev,
                      ftpFiles: ftpFilesData.files.length || 0,
                    }));
                  }
                }
              } catch (error) {
                console.error('FTP 파일 목록 가져오기 실패:', error);
              }
            }
          } else {
            setSystemStatus(prev => ({
              ...prev,
              ftpConnection: 'disconnected',
            }));
          }
        } else {
          setSystemStatus(prev => ({
            ...prev,
            ftpConnection: 'error',
          }));
        }
      } catch (error) {
        setSystemStatus(prev => ({
          ...prev,
          ftpConnection: 'error',
        }));
      }

      // 벡터 인덱스 상태 확인
      try {
        const indexResponse = await fetch('/api/vector-index/status');
        if (indexResponse.ok) {
          const indexData = await indexResponse.json();
          
          // 백엔드 응답 형식 확인
          // 성공: { index_status: { state: 'STATE_READY' }, endpoint_status: {...}, ... }
          // 없음: { status: 'not_created' }
          // 에러: { status: 'error', message: ... }
          
          if (indexData.status === 'error') {
            // 에러 상태
            setSystemStatus(prev => ({
              ...prev,
              vertexAI: 'error',
            }));
          } else if (indexData.status === 'not_created' || indexData.status === 'not_initialized') {
            // 인덱스 미생성 또는 초기화되지 않음
            setSystemStatus(prev => ({
              ...prev,
              vertexAI: 'inactive',
            }));
          } else if (indexData.index_status && indexData.index_status.state) {
            // 인덱스 상태 확인
            const indexState = indexData.index_status.state;
            const endpointState = indexData.endpoint_status?.state;
            
            // STATE_READY = 정상 동작
            // STATE_BUILDING = 생성 중
            // 기타 = 에러 또는 비활성
            if (indexState === 'STATE_READY' || indexState === 'READY') {
              // 엔드포인트도 확인 (있으면)
              if (indexData.endpoint_status) {
                if (endpointState === 'STATE_READY' || endpointState === 'READY') {
                  setSystemStatus(prev => ({
                    ...prev,
                    vertexAI: 'active',
                  }));
                } else if (endpointState === 'STATE_BUILDING' || endpointState === 'BUILDING') {
                  setSystemStatus(prev => ({
                    ...prev,
                    vertexAI: 'inactive',
                  }));
                } else {
                  setSystemStatus(prev => ({
                    ...prev,
                    vertexAI: 'error',
                  }));
                }
              } else {
                // 엔드포인트 없어도 인덱스만 있으면 active
                setSystemStatus(prev => ({
                  ...prev,
                  vertexAI: 'active',
                }));
              }
              
              // 벡터 인덱스 개수 (인덱스가 존재하면 1개로 표시)
              setStats(prev => ({
                ...prev,
                vectorIndexes: 1,
              }));
            } else if (indexState === 'STATE_BUILDING' || indexState === 'BUILDING') {
              setSystemStatus(prev => ({
                ...prev,
                vertexAI: 'inactive',
              }));
            } else {
              setSystemStatus(prev => ({
                ...prev,
                vertexAI: 'error',
              }));
            }
          } else {
            // 예상치 못한 응답 형식
            setSystemStatus(prev => ({
              ...prev,
              vertexAI: 'error',
            }));
          }
        } else {
          setSystemStatus(prev => ({
            ...prev,
            vertexAI: 'error',
          }));
        }
      } catch (error) {
        console.error('Vertex AI 상태 확인 실패:', error);
        setSystemStatus(prev => ({
          ...prev,
          vertexAI: 'error',
        }));
      }

      // 최근 활동 가져오기
      const logsResponse = await fetch('/api/processing-logs?limit=5');
      if (logsResponse.ok) {
        const logsData = await logsResponse.json();
        if (logsData && logsData.logs) {
          const activities = logsData.logs.map((log: any, index: number) => ({
            id: log.id || `activity-${index}`,
            action: log.message || '작업 수행',
            time: new Date(log.timestamp).toLocaleString(),
            status: log.status === 'success' ? 'success' as const : 
                    log.status === 'error' ? 'error' as const : 'info' as const,
          }));
          setRecentActivities(activities);
        }
      }

      // Cloud SQL 상태 확인
      try {
        const articlesResponse = await fetch('/api/articles?limit=1');
        if (articlesResponse.ok) {
          setSystemStatus(prev => ({
            ...prev,
            cloudSQL: 'active',
          }));
        } else {
          setSystemStatus(prev => ({
            ...prev,
            cloudSQL: 'error',
          }));
        }
      } catch (error) {
        setSystemStatus(prev => ({
          ...prev,
          cloudSQL: 'error',
        }));
      }

      setLoading(false);
    } catch (error) {
      console.error('대시보드 데이터 가져오기 실패:', error);
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
      case 'connected':
      case 'success':
        return 'success';
      case 'inactive':
      case 'disconnected':
        return 'warning';
      case 'error':
        return 'error';
      default:
        return 'info';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
      case 'connected':
      case 'success':
        return <CheckCircle />;
      case 'inactive':
      case 'disconnected':
        return <Warning />;
      case 'error':
        return <Error />;
      default:
        return <Info />;
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
        대시보드
      </Typography>

      {loading && (
        <Box sx={{ mb: 3 }}>
          <LinearProgress />
          <Typography variant="body2" sx={{ mt: 1 }} align="center">
            데이터를 불러오는 중...
          </Typography>
        </Box>
      )}

      {/* 시스템 상태 */}
      <Box sx={{ mb: 3 }}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              시스템 상태
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
              <Box sx={{ flex: '1 1 200px', minWidth: '200px' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Chip
                    icon={getStatusIcon(systemStatus.vertexAI)}
                    label="Vertex AI"
                    color={getStatusColor(systemStatus.vertexAI) as any}
                    variant="outlined"
                  />
                </Box>
              </Box>
              <Box sx={{ flex: '1 1 200px', minWidth: '200px' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Chip
                    icon={getStatusIcon(systemStatus.cloudRun)}
                    label="Cloud Run"
                    color={getStatusColor(systemStatus.cloudRun) as any}
                    variant="outlined"
                  />
                </Box>
              </Box>
              <Box sx={{ flex: '1 1 200px', minWidth: '200px' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Chip
                    icon={getStatusIcon(systemStatus.cloudSQL)}
                    label="Cloud SQL"
                    color={getStatusColor(systemStatus.cloudSQL) as any}
                    variant="outlined"
                  />
                </Box>
              </Box>
              <Box sx={{ flex: '1 1 200px', minWidth: '200px' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Chip
                    icon={getStatusIcon(systemStatus.ftpConnection)}
                    label="FTP 연결"
                    color={getStatusColor(systemStatus.ftpConnection) as any}
                    variant="outlined"
                  />
                </Box>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Box>

      {/* 통계 카드 */}
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3, mb: 3 }}>
        <Box sx={{ flex: '1 1 250px', minWidth: '250px' }}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="body2">
                    총 기사 수
                  </Typography>
                  <Typography variant="h4" component="div">
                    {stats.totalArticles.toLocaleString()}
                  </Typography>
                </Box>
                <TrendingUp sx={{ fontSize: 40, color: 'primary.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Box>
        <Box sx={{ flex: '1 1 250px', minWidth: '250px' }}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="body2">
                    오늘 처리된 기사
                  </Typography>
                  <Typography variant="h4" component="div">
                    {stats.processedToday}
                  </Typography>
                </Box>
                <Storage sx={{ fontSize: 40, color: 'success.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Box>
        <Box sx={{ flex: '1 1 250px', minWidth: '250px' }}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="body2">
                    벡터 인덱스
                  </Typography>
                  <Typography variant="h4" component="div">
                    {stats.vectorIndexes}
                  </Typography>
                </Box>
                <Search sx={{ fontSize: 40, color: 'info.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Box>
        <Box sx={{ flex: '1 1 250px', minWidth: '250px' }}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="body2">
                    FTP 파일
                  </Typography>
                  <Typography variant="h4" component="div">
                    {stats.ftpFiles}
                  </Typography>
                </Box>
                <CloudUpload sx={{ fontSize: 40, color: 'warning.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Box>
      </Box>

      {/* 최근 활동 */}
      <Box sx={{ mb: 3 }}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              최근 활동
            </Typography>
            {recentActivities.length === 0 ? (
              <Alert severity="info">
                <Typography variant="body2">
                  최근 활동이 없습니다.
                </Typography>
              </Alert>
            ) : (
              <List>
                {recentActivities.map((activity, index) => (
                  <React.Fragment key={activity.id}>
                    <ListItem>
                      <ListItemIcon>
                        {getStatusIcon(activity.status)}
                      </ListItemIcon>
                      <ListItemText
                        primary={activity.action}
                        secondary={activity.time}
                      />
                    </ListItem>
                    {index < recentActivities.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            )}
          </CardContent>
        </Card>
      </Box>

      {/* 알림 */}
      <Box>
        <Alert severity="info">
          <Typography variant="body2">
            <strong>고정 IP 설정 완료:</strong> FTP 서버 접속을 위한 고정 IP (34.50.19.65)가 설정되었습니다.
          </Typography>
        </Alert>
      </Box>
    </Box>
  );
};

export default Dashboard;