import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Alert,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
} from '@mui/material';
import {
  CloudUpload,
  CloudDownload,
  Delete,
  Refresh,
  PlayArrow,
  Stop,
  CheckCircle,
  Error,
  Warning,
  Info,
  Folder,
  Description,
  Settings,
} from '@mui/icons-material';

interface FTPFile {
  name: string;
  size: number;
  modified: string;
  status: 'pending' | 'downloading' | 'downloaded' | 'error';
}

interface FTPConnection {
  host: string;
  port: number;
  username: string;
  status: 'connected' | 'disconnected' | 'error';
  lastConnected?: string;
}

const FTPManagement: React.FC = () => {
  const [ftpConnection, setFtpConnection] = useState<FTPConnection>({
    host: '210.179.172.2',
    port: 8023,
    username: 'saltlux_vector',
    status: 'disconnected',
  });

  const [ftpFiles, setFtpFiles] = useState<FTPFile[]>([]);
  const [selectedFiles, setSelectedFiles] = useState<string[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingProgress, setProcessingProgress] = useState(0);
  const [settingsDialogOpen, setSettingsDialogOpen] = useState(false);
  const [deleteAfterDownload, setDeleteAfterDownload] = useState(false);
  const [uploadToGCS, setUploadToGCS] = useState(true);
  const [createEmbeddings, setCreateEmbeddings] = useState(true);
  const [ftpLogs, setFtpLogs] = useState<string[]>([]);

  // 컴포넌트 마운트 시 FTP 연결 상태 확인
  useEffect(() => {
    const checkFTPStatus = async () => {
      try {
        const response = await fetch('/api/ftp/connection-info', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });
        
        if (response.ok) {
          const result = await response.json();
          if (result.success) {
            setFtpConnection(prev => ({
              ...prev,
              status: result.connected ? 'connected' : 'disconnected',
              lastConnected: result.last_connected,
            }));
            
            // 연결되어 있으면 파일 목록 가져오기
            if (result.connected) {
              handleRefreshFiles();
            }
          }
        }
      } catch (error) {
        console.error('FTP 상태 확인 실패:', error);
      }
    };

    checkFTPStatus();
  }, []);

  const handleConnect = async () => {
    setIsProcessing(true);
    setFtpLogs([]); // 로그 초기화
    
    // 로그 추가 헬퍼 함수
    const addLog = (message: string) => {
      const timestamp = new Date().toLocaleTimeString();
      setFtpLogs(prev => [...prev, `[${timestamp}] ${message}`]);
    };
    
    addLog('FTP 연결 시작...');
    
    try {
      const response = await fetch('/api/ftp/connect', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          environment: 'test', // 환경 선택은 나중에 추가 가능
        }),
      });
      
      if (response.ok) {
        const result = await response.json();
        
        // 백엔드에서 받은 로그 표시
        if (result.logs && Array.isArray(result.logs)) {
          result.logs.forEach((log: string) => {
            addLog(log);
          });
        } else if (result.message) {
          addLog(result.message);
        }
        
        setFtpConnection(prev => ({
          ...prev,
          status: result.success ? 'connected' : 'error',
          lastConnected: result.success ? new Date().toISOString() : undefined,
        }));
        
        if (result.success) {
          addLog('✓ FTP 연결 완료');
        } else {
          addLog(`✗ FTP 연결 실패: ${result.error || 'Unknown error'}`);
        }
      } else {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        addLog(`✗ HTTP 오류: ${response.status} ${errorData.detail || response.statusText}`);
        setFtpConnection(prev => ({
          ...prev,
          status: 'error',
        }));
      }
    } catch (error: any) {
      console.error('FTP 연결 실패:', error);
      addLog(`✗ 네트워크 오류: ${error.message || 'Unknown error'}`);
      setFtpConnection(prev => ({
        ...prev,
        status: 'error',
      }));
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDisconnect = async () => {
    try {
      const response = await fetch('/api/ftp/disconnect', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        setFtpConnection(prev => ({
          ...prev,
          status: 'disconnected',
        }));
      }
    } catch (error) {
      console.error('FTP 연결 해제 실패:', error);
    }
  };

  const handleRefreshFiles = async () => {
    try {
      const response = await fetch('/api/ftp/files', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const result = await response.json();
        if (result.success && result.files) {
          const formattedFiles = result.files.map((file: any) => ({
            name: file.name,
            size: file.size,
            modified: file.modified || new Date().toISOString(),
            status: 'pending' as const,
          }));
          setFtpFiles(formattedFiles);
        }
      }
    } catch (error) {
      console.error('파일 목록 조회 실패:', error);
    }
  };

  const handleDownloadFile = async (fileName: string) => {
    setFtpFiles(prev => 
      prev.map(file => 
        file.name === fileName 
          ? { ...file, status: 'downloading' }
          : file
      )
    );

    try {
      const response = await fetch('/api/ftp/download', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ filename: fileName }),
      });
      
      if (response.ok) {
        const result = await response.json();
        setFtpFiles(prev => 
          prev.map(file => 
            file.name === fileName 
              ? { ...file, status: result.success ? 'downloaded' : 'error' }
              : file
          )
        );
      } else {
        setFtpFiles(prev => 
          prev.map(file => 
            file.name === fileName 
              ? { ...file, status: 'error' }
              : file
          )
        );
      }
    } catch (error) {
      console.error('파일 다운로드 실패:', error);
      setFtpFiles(prev => 
        prev.map(file => 
          file.name === fileName 
            ? { ...file, status: 'error' }
            : file
        )
      );
    }
  };

  const handleDownloadAll = async () => {
    setIsProcessing(true);
    setProcessingProgress(0);

    try {
      const response = await fetch('/api/ftp/download-all', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          delete_after_download: deleteAfterDownload,
          upload_to_gcs: uploadToGCS,
          create_embeddings: createEmbeddings
        }),
      });
      
      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          // 진행률 시뮬레이션
          const interval = setInterval(() => {
            setProcessingProgress(prev => {
              if (prev >= 100) {
                clearInterval(interval);
                setIsProcessing(false);
                return 100;
              }
              return prev + 10;
            });
          }, 500);
          
          // 파일 상태 업데이트
          if (result.downloaded_files) {
            setFtpFiles(prev => 
              prev.map(file => {
                const downloadedFile = result.downloaded_files.find((f: any) => f.remote_filename === file.name);
                if (downloadedFile) {
                  return { ...file, status: downloadedFile.success ? 'downloaded' : 'error' };
                }
                return file;
              })
            );
          }
        } else {
          setIsProcessing(false);
        }
      } else {
        setIsProcessing(false);
      }
    } catch (error) {
      console.error('전체 다운로드 실패:', error);
      setIsProcessing(false);
    }
  };

  const handleDeleteFile = (fileName: string) => {
    setFtpFiles(prev => prev.filter(file => file.name !== fileName));
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected':
      case 'downloaded':
        return 'success';
      case 'downloading':
        return 'info';
      case 'error':
        return 'error';
      case 'disconnected':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'connected':
      case 'downloaded':
        return <CheckCircle />;
      case 'downloading':
        return <CloudDownload />;
      case 'error':
        return <Error />;
      case 'disconnected':
        return <Warning />;
      default:
        return <Info />;
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
        FTP 관리
      </Typography>

      {/* 연결 상태 및 설정 */}
      <Box sx={{ display: 'flex', gap: 3, mb: 3 }}>
        <Box sx={{ flex: 1 }}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  FTP 연결 상태
                </Typography>
                <IconButton onClick={() => setSettingsDialogOpen(true)}>
                  <Settings />
                </IconButton>
              </Box>
              
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                <Chip
                  icon={getStatusIcon(ftpConnection.status)}
                  label={ftpConnection.status === 'connected' ? '연결됨' : '연결 안됨'}
                  color={getStatusColor(ftpConnection.status) as any}
                  variant="outlined"
                />
                {ftpConnection.lastConnected && (
                  <Typography variant="caption" color="text.secondary">
                    마지막 연결: {new Date(ftpConnection.lastConnected).toLocaleString()}
                  </Typography>
                )}
              </Box>

              <Box sx={{ display: 'flex', gap: 1 }}>
                <Button
                  variant="contained"
                  onClick={handleConnect}
                  disabled={isProcessing || ftpConnection.status === 'connected'}
                  startIcon={<PlayArrow />}
                >
                  연결
                </Button>
                <Button
                  variant="outlined"
                  onClick={handleDisconnect}
                  disabled={ftpConnection.status === 'disconnected'}
                  startIcon={<Stop />}
                >
                  연결 해제
                </Button>
                <Button
                  variant="outlined"
                  onClick={handleRefreshFiles}
                  startIcon={<Refresh />}
                >
                  새로고침
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Box>

        <Box sx={{ flex: 1 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                연결 정보
              </Typography>
              <List dense>
                <ListItem>
                  <ListItemText 
                    primary="호스트" 
                    secondary={ftpConnection.host}
                  />
                </ListItem>
                <ListItem>
                  <ListItemText 
                    primary="포트" 
                    secondary={ftpConnection.port.toString()}
                  />
                </ListItem>
                <ListItem>
                  <ListItemText 
                    primary="사용자명" 
                    secondary={ftpConnection.username}
                  />
                </ListItem>
                <ListItem>
                  <ListItemText 
                    primary="고정 IP" 
                    secondary="34.50.19.65"
                  />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Box>
      </Box>

      {/* 파일 목록 */}
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">
              FTP 파일 목록 ({ftpFiles.length}개)
            </Typography>
            <Box>
              <Button
                variant="contained"
                onClick={handleDownloadAll}
                disabled={isProcessing || ftpFiles.length === 0}
                startIcon={<CloudDownload />}
                sx={{ mr: 1 }}
              >
                전체 다운로드
              </Button>
              <Button
                variant="outlined"
                startIcon={<CloudUpload />}
              >
                GCS 업로드
              </Button>
            </Box>
          </Box>

          {isProcessing && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" gutterBottom>
                파일 처리 중... ({processingProgress}%)
              </Typography>
              <LinearProgress variant="determinate" value={processingProgress} />
            </Box>
          )}

          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>파일명</TableCell>
                  <TableCell>크기</TableCell>
                  <TableCell>수정일</TableCell>
                  <TableCell>상태</TableCell>
                  <TableCell align="center">작업</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {ftpFiles.map((file) => (
                  <TableRow key={file.name}>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Description />
                        <Typography variant="body2">
                          {file.name}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {formatFileSize(file.size)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {file.modified}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        icon={getStatusIcon(file.status)}
                        label={
                          file.status === 'pending' ? '대기' :
                          file.status === 'downloading' ? '다운로드 중' :
                          file.status === 'downloaded' ? '완료' :
                          file.status === 'error' ? '오류' : file.status
                        }
                        color={getStatusColor(file.status) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell align="center">
                      <Box sx={{ display: 'flex', gap: 0.5 }}>
                        <IconButton
                          size="small"
                          onClick={() => handleDownloadFile(file.name)}
                          disabled={file.status === 'downloading' || file.status === 'downloaded'}
                        >
                          <CloudDownload />
                        </IconButton>
                        <IconButton
                          size="small"
                          onClick={() => handleDeleteFile(file.name)}
                          color="error"
                        >
                          <Delete />
                        </IconButton>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* FTP 연결 로그 */}
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">
              FTP 연결 로그
            </Typography>
            <Button
              variant="outlined"
              size="small"
              onClick={() => setFtpLogs([])}
              disabled={ftpLogs.length === 0}
            >
              로그 지우기
            </Button>
          </Box>
          
          <Paper
            variant="outlined"
            sx={{
              p: 2,
              maxHeight: '400px',
              overflow: 'auto',
              backgroundColor: '#f5f5f5',
              fontFamily: 'monospace',
              fontSize: '0.875rem',
            }}
          >
            {ftpLogs.length === 0 ? (
              <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                FTP 연결을 시도하면 로그가 여기에 표시됩니다.
              </Typography>
            ) : (
              <Box component="pre" sx={{ margin: 0, whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                {ftpLogs.map((log, index) => {
                  // 로그 레벨에 따라 색상 구분
                  let color = 'text.primary';
                  if (log.includes('[ERROR]') || log.includes('✗')) {
                    color = 'error.main';
                  } else if (log.includes('[SUCCESS]') || log.includes('✓')) {
                    color = 'success.main';
                  } else if (log.includes('[INFO]')) {
                    color = 'info.main';
                  }
                  
                  return (
                    <Typography
                      key={index}
                      variant="body2"
                      sx={{
                        color,
                        mb: 0.5,
                      }}
                    >
                      {log}
                    </Typography>
                  );
                })}
              </Box>
            )}
          </Paper>
        </CardContent>
      </Card>

      {/* 설정 다이얼로그 */}
      <Dialog open={settingsDialogOpen} onClose={() => setSettingsDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>FTP 설정</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <FormControlLabel
              control={
                <Switch
                  checked={deleteAfterDownload}
                  onChange={(e) => setDeleteAfterDownload(e.target.checked)}
                />
              }
              label="다운로드 후 파일 삭제"
            />
            <FormControlLabel
              control={
                <Switch
                  checked={uploadToGCS}
                  onChange={(e) => setUploadToGCS(e.target.checked)}
                />
              }
              label="GCS 자동 업로드"
            />
            <FormControlLabel
              control={
                <Switch
                  checked={createEmbeddings}
                  onChange={(e) => setCreateEmbeddings(e.target.checked)}
                />
              }
              label="자동 임베딩 생성"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSettingsDialogOpen(false)}>취소</Button>
          <Button variant="contained" onClick={() => setSettingsDialogOpen(false)}>
            저장
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default FTPManagement;