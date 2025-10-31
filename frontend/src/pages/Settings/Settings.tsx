import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  TextField,
  Button,
  Switch,
  FormControlLabel,
  Divider,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
} from '@mui/material';
import {
  Save,
  Refresh,
  Edit,
  Delete,
  Add,
  Security,
  Cloud,
  Storage,
  Api,
  CheckCircle,
  Error as ErrorIcon,
  Login as LoginIcon,
} from '@mui/icons-material';

interface SystemConfig {
  vertexAIEndpoint: string;
  geminiApiKey: string;
  ftpHost: string;
  ftpPort: number;
  ftpUsername: string;
  ftpPassword: string;
  gcsBucket: string;
  maxConcurrentDownloads: number;
  embeddingBatchSize: number;
  searchResultLimit: number;
}

const Settings: React.FC = () => {
  const [config, setConfig] = useState<SystemConfig>({
    vertexAIEndpoint: 'https://asia-northeast3-aiplatform.googleapis.com',
    geminiApiKey: '••••••••••••••••',
    ftpHost: '210.179.172.2',
    ftpPort: 8023,
    ftpUsername: 'saltlux_vector',
    ftpPassword: '••••••••••••••••',
    gcsBucket: 'mk-ai-project-473000-mk-news-data',
    maxConcurrentDownloads: 5,
    embeddingBatchSize: 100,
    searchResultLimit: 20,
  });

  const [autoBackup, setAutoBackup] = useState(true);
  const [enableLogging, setEnableLogging] = useState(true);
  const [enableNotifications, setEnableNotifications] = useState(true);
  const [apiKeyDialogOpen, setApiKeyDialogOpen] = useState(false);
  const [newApiKey, setNewApiKey] = useState('');
  
  // GCP 인증 상태
  const [gcpAuthStatus, setGcpAuthStatus] = useState<{
    authenticated: boolean;
    active_account: string | null;
    project_id: string | null;
    loading: boolean;
  }>({
    authenticated: false,
    active_account: null,
    project_id: null,
    loading: true,
  });

  const handleSaveConfig = () => {
    // 설정 저장 로직
    console.log('설정 저장:', config);
  };

  const handleResetConfig = () => {
    // 설정 초기화 로직
    console.log('설정 초기화');
  };

  const handleUpdateApiKey = () => {
    setConfig(prev => ({
      ...prev,
      geminiApiKey: newApiKey,
    }));
    setApiKeyDialogOpen(false);
    setNewApiKey('');
  };

  // GCP 인증 상태 확인
  const checkGcpAuth = async () => {
    setGcpAuthStatus(prev => ({ ...prev, loading: true }));
    try {
      const response = await fetch('/api/gcp/auth-status');
      if (response.ok) {
        const data = await response.json();
        setGcpAuthStatus({
          authenticated: data.authenticated || false,
          active_account: data.active_account || null,
          project_id: data.project_id || null,
          loading: false,
        });
      } else {
        setGcpAuthStatus(prev => ({ ...prev, loading: false }));
      }
    } catch (error) {
      console.error('GCP 인증 상태 확인 실패:', error);
      setGcpAuthStatus(prev => ({ ...prev, loading: false }));
    }
  };

  // GCP 로그인 시작
  const handleGcpLogin = async () => {
    try {
      const response = await fetch('/api/gcp/init-login', {
        method: 'POST',
      });
      if (response.ok) {
        const data = await response.json();
        
        // 브라우저에서 직접 로그인할 수 있는 URL이 있으면 새 창으로 열기
        if (data.auth_url) {
          window.open(data.auth_url, '_blank', 'width=800,height=600');
          
          // 사용자에게 인증 코드 안내
          const codeMessage = data.verification_code 
            ? `인증 코드: ${data.verification_code}\n\n브라우저에서 이 코드를 입력하세요.`
            : '';
          
          alert(`${data.message}\n\n${codeMessage || data.instructions}`);
          
          // 주기적으로 인증 상태 확인 (최대 2분)
          let checkCount = 0;
          const checkInterval = setInterval(async () => {
            checkCount++;
            const prevAuth = gcpAuthStatus.authenticated;
            await checkGcpAuth();
            
            if (gcpAuthStatus.authenticated !== prevAuth && gcpAuthStatus.authenticated) {
              clearInterval(checkInterval);
              alert('GCP 로그인이 완료되었습니다!');
            } else if (checkCount >= 40) {
              clearInterval(checkInterval);
            }
          }, 3000);
        } else {
          alert(data.message || data.instructions || '터미널에서 gcloud auth login 명령을 실행하세요.');
          // 3초 후 상태 새로고침
          setTimeout(() => {
            checkGcpAuth();
          }, 3000);
        }
      } else {
        alert('GCP 로그인 시작에 실패했습니다. 터미널에서 직접 "gcloud auth login" 명령을 실행하세요.');
      }
    } catch (error) {
      console.error('GCP 로그인 시작 실패:', error);
      alert('GCP 로그인 시작에 실패했습니다. 터미널에서 직접 "gcloud auth login" 명령을 실행하세요.');
    }
  };

  useEffect(() => {
    checkGcpAuth();
  }, []);

  const configSections = [
    {
      title: 'AI 서비스 설정',
      icon: <Cloud />,
      items: [
        { label: 'Vertex AI 엔드포인트', value: config.vertexAIEndpoint },
        { label: 'Gemini API 키', value: config.geminiApiKey, isSecret: true },
      ],
    },
    {
      title: 'FTP 서버 설정',
      icon: <Storage />,
      items: [
        { label: 'FTP 호스트', value: config.ftpHost },
        { label: 'FTP 포트', value: config.ftpPort.toString() },
        { label: 'FTP 사용자명', value: config.ftpUsername },
        { label: 'FTP 비밀번호', value: config.ftpPassword, isSecret: true },
      ],
    },
    {
      title: 'API 설정',
      icon: <Api />,
      items: [
        { label: 'GCS 버킷', value: config.gcsBucket },
        { label: '최대 동시 다운로드', value: config.maxConcurrentDownloads.toString() },
        { label: '임베딩 배치 크기', value: config.embeddingBatchSize.toString() },
        { label: '검색 결과 제한', value: config.searchResultLimit.toString() },
      ],
    },
  ];

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
        설정
      </Typography>

      {/* 시스템 설정 */}
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3, mb: 3 }}>
        {configSections.map((section, sectionIndex) => (
          <Box key={sectionIndex} sx={{ flex: '1 1 300px', minWidth: '300px' }}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                  {section.icon}
                  <Typography variant="h6">
                    {section.title}
                  </Typography>
                </Box>
                <List dense>
                  {section.items.map((item, itemIndex) => (
                    <ListItem key={itemIndex}>
                      <ListItemText
                        primary={item.label}
                        secondary={item.isSecret ? '••••••••••••••••' : item.value}
                      />
                      <ListItemSecondaryAction>
                        <IconButton size="small">
                          <Edit />
                        </IconButton>
                      </ListItemSecondaryAction>
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Box>
        ))}
      </Box>

      {/* 시스템 옵션 */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            시스템 옵션
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
            <FormControlLabel
              control={
                <Switch
                  checked={autoBackup}
                  onChange={(e) => setAutoBackup(e.target.checked)}
                />
              }
              label="자동 백업"
            />
            <FormControlLabel
              control={
                <Switch
                  checked={enableLogging}
                  onChange={(e) => setEnableLogging(e.target.checked)}
                />
              }
              label="로깅 활성화"
            />
            <FormControlLabel
              control={
                <Switch
                  checked={enableNotifications}
                  onChange={(e) => setEnableNotifications(e.target.checked)}
                />
              }
              label="알림 활성화"
            />
          </Box>
        </CardContent>
      </Card>

      {/* GCP 인증 설정 */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Cloud />
              <Typography variant="h6">
                GCP 인증
              </Typography>
            </Box>
            <Button
              variant="outlined"
              size="small"
              onClick={checkGcpAuth}
              startIcon={<Refresh />}
              disabled={gcpAuthStatus.loading}
            >
              새로고침
            </Button>
          </Box>
          
          {gcpAuthStatus.loading ? (
            <Alert severity="info">
              <Typography variant="body2">인증 상태를 확인하는 중...</Typography>
            </Alert>
          ) : gcpAuthStatus.authenticated ? (
            <Box>
              <Alert severity="success" sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <CheckCircle />
                  <Typography variant="body1" fontWeight={600}>
                    GCP에 인증되어 있습니다
                  </Typography>
                </Box>
                <Typography variant="body2" sx={{ mt: 1 }}>
                  활성 계정: {gcpAuthStatus.active_account || 'N/A'}
                  {gcpAuthStatus.project_id ? <><br />프로젝트 ID: {gcpAuthStatus.project_id}</> : ''}
                </Typography>
              </Alert>
            </Box>
          ) : (
            <Box>
              <Alert severity="warning" sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <ErrorIcon />
                  <Typography variant="body1" fontWeight={600}>
                    GCP에 인증되지 않았습니다
                  </Typography>
                </Box>
                <Typography variant="body2" sx={{ mt: 1 }}>
                  Vertex AI 및 다른 GCP 서비스를 사용하려면 GCP에 로그인해야 합니다.
                </Typography>
              </Alert>
              <Button
                variant="contained"
                onClick={handleGcpLogin}
                startIcon={<LoginIcon />}
                sx={{ mt: 1 }}
              >
                GCP 로그인
              </Button>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                버튼을 클릭하면 로그인 가이드가 표시됩니다. 터미널에서 "gcloud auth login" 명령을 실행하거나, 
                Application Default Credentials를 설정하려면 "gcloud auth application-default login" 명령을 실행하세요.
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* 보안 설정 */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            보안 설정
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <Chip
              icon={<Security />}
              label="API 키 관리"
              color="primary"
              variant="outlined"
            />
            <Button
              variant="outlined"
              onClick={() => setApiKeyDialogOpen(true)}
              startIcon={<Edit />}
            >
              API 키 변경
            </Button>
          </Box>
          <Alert severity="info">
            <Typography variant="body2">
              API 키는 안전하게 저장되며, 정기적으로 갱신하는 것을 권장합니다.
            </Typography>
          </Alert>
        </CardContent>
      </Card>

      {/* 시스템 정보 */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            시스템 정보
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
            <Box sx={{ flex: '1 1 200px' }}>
              <Typography variant="body2" color="text.secondary">
                애플리케이션 버전
              </Typography>
              <Typography variant="body1">
                v1.0.0
              </Typography>
            </Box>
            <Box sx={{ flex: '1 1 200px' }}>
              <Typography variant="body2" color="text.secondary">
                마지막 업데이트
              </Typography>
              <Typography variant="body1">
                2024-01-15
              </Typography>
            </Box>
            <Box sx={{ flex: '1 1 200px' }}>
              <Typography variant="body2" color="text.secondary">
                GCP 프로젝트
              </Typography>
              <Typography variant="body1">
                mk-ai-project-473000
              </Typography>
            </Box>
            <Box sx={{ flex: '1 1 200px' }}>
              <Typography variant="body2" color="text.secondary">
                고정 IP
              </Typography>
              <Typography variant="body1">
                34.50.19.65
              </Typography>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* 액션 버튼 */}
      <Box sx={{ display: 'flex', gap: 2 }}>
        <Button
          variant="contained"
          onClick={handleSaveConfig}
          startIcon={<Save />}
        >
          설정 저장
        </Button>
        <Button
          variant="outlined"
          onClick={handleResetConfig}
          startIcon={<Refresh />}
        >
          초기화
        </Button>
      </Box>

      {/* API 키 변경 다이얼로그 */}
      <Dialog open={apiKeyDialogOpen} onClose={() => setApiKeyDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>API 키 변경</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="새로운 API 키"
            value={newApiKey}
            onChange={(e) => setNewApiKey(e.target.value)}
            type="password"
            sx={{ mt: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setApiKeyDialogOpen(false)}>취소</Button>
          <Button variant="contained" onClick={handleUpdateApiKey}>
            저장
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Settings;