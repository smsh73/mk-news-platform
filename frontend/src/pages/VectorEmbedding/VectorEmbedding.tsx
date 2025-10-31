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
  LinearProgress,
  Alert,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
} from '@mui/material';
import {
  PlayArrow,
  Stop,
  CheckCircle,
  Error as ErrorIcon,
  Warning,
  Info,
  Upload,
  Refresh,
  Visibility,
  Delete,
  CloudUpload,
  Functions,
} from '@mui/icons-material';

interface EmbeddingJob {
  id: string;
  filename: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  articlesCount?: number;
  embeddingsCount?: number;
  processingTime?: number;
  error?: string;
  createdAt: string;
}

interface EmbeddingStats {
  totalJobs: number;
  completedJobs: number;
  failedJobs: number;
  totalEmbeddings: number;
  avgProcessingTime: number;
}

const VectorEmbedding: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [embeddingJobs, setEmbeddingJobs] = useState<EmbeddingJob[]>([]);
  const [embeddingStats, setEmbeddingStats] = useState<EmbeddingStats>({
    totalJobs: 0,
    completedJobs: 0,
    failedJobs: 0,
    totalEmbeddings: 0,
    avgProcessingTime: 0,
  });
  const [isProcessing, setIsProcessing] = useState(false);
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [gcpAuthenticated, setGcpAuthenticated] = useState(false);
  const [gcpAuthStatus, setGcpAuthStatus] = useState<any>(null);
  const [gcpLoginDialogOpen, setGcpLoginDialogOpen] = useState(false);

  useEffect(() => {
    fetchEmbeddingJobs();
    fetchEmbeddingStats();
    checkGcpAuth();

    // 10초마다 자동 새로고침
    const interval = setInterval(() => {
      fetchEmbeddingJobs();
      fetchEmbeddingStats();
      checkGcpAuth();
    }, 10000);

    return () => clearInterval(interval);
  }, []);

  const checkGcpAuth = async () => {
    try {
      const response = await fetch('/api/gcp/auth-status');
      if (response.ok) {
        const data = await response.json();
        // Cloud Run 환경에서는 gcloud CLI가 없을 수 있으므로
        // 에러가 없거나 authenticated가 false여도 Service Account 인증으로 간주
        if (data.error) {
          // gcloud CLI 관련 에러인 경우 Cloud Run 환경으로 간주
          if ('gcloud' in data.error.toLowerCase() || 'not found' in data.error.toLowerCase()) {
            setGcpAuthenticated(true); // Service Account 인증 사용 중으로 간주
            setGcpAuthStatus({ ...data, is_service_account: true });
            return;
          }
        }
        setGcpAuthenticated(data.authenticated || false);
        setGcpAuthStatus(data);
      } else {
        // Cloud Run 환경에서는 Service Account를 사용하므로 인증된 것으로 간주
        setGcpAuthenticated(true);
        setGcpAuthStatus({ is_service_account: true });
      }
    } catch (error) {
      console.error('GCP 인증 상태 확인 실패:', error);
      // Cloud Run 환경에서는 Service Account를 사용하므로 인증된 것으로 간주
      setGcpAuthenticated(true);
      setGcpAuthStatus({ is_service_account: true });
    }
  };

  const handleGcpLogin = async () => {
    try {
      const response = await fetch('/api/gcp/init-login', {
        method: 'POST',
      });
      if (response.ok) {
        const data = await response.json();
        
        if (data.auth_url) {
          window.open(data.auth_url, '_blank', 'width=800,height=600');
          
          alert(`${data.message}\n\n인증 코드: ${data.verification_code || 'N/A'}\n\n브라우저에서 로그인을 완료하세요.`);
          
          // 주기적으로 인증 상태 확인 (최대 2분)
          let checkCount = 0;
          const checkInterval = setInterval(async () => {
            checkCount++;
            await checkGcpAuth();
            
            if (gcpAuthenticated) {
              clearInterval(checkInterval);
              setGcpLoginDialogOpen(false);
              alert('GCP 로그인이 완료되었습니다!');
            } else if (checkCount >= 40) {
              clearInterval(checkInterval);
            }
          }, 3000);
        } else {
          alert(data.message || data.instructions || '터미널에서 gcloud auth login 명령을 실행하세요.');
        }
      }
    } catch (error) {
      console.error('GCP 로그인 시작 실패:', error);
      alert('GCP 로그인 시작에 실패했습니다.');
    }
  };

  const fetchEmbeddingJobs = async () => {
    try {
      const response = await fetch('/api/embedding-jobs');
      if (response.ok) {
        const data = await response.json();
        if (data && data.jobs) {
          setEmbeddingJobs(data.jobs);
        }
      }
    } catch (error) {
      console.error('임베딩 작업 목록 가져오기 실패:', error);
    }
  };

  const fetchEmbeddingStats = async () => {
    try {
      const response = await fetch('/api/embedding-stats');
      if (response.ok) {
        const data = await response.json();
        if (data) {
          setEmbeddingStats({
            totalJobs: data.total_jobs || 0,
            completedJobs: data.completed_jobs || 0,
            failedJobs: data.failed_jobs || 0,
            totalEmbeddings: data.total_embeddings || 0,
            avgProcessingTime: data.avg_processing_time || 0,
          });
        }
      }
    } catch (error) {
      console.error('임베딩 통계 가져오기 실패:', error);
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;
    
    const xmlFiles: File[] = [];
    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      if (file.name.endsWith('.xml')) {
        xmlFiles.push(file);
      }
    }
    
    if (xmlFiles.length === 0) {
      alert('XML 파일만 업로드 가능합니다.');
      return;
    }
    
    if (xmlFiles.length === 1) {
      setSelectedFile(xmlFiles[0]);
      setSelectedFiles([xmlFiles[0]]);
    } else {
      setSelectedFile(null);
      setSelectedFiles(xmlFiles);
    }
    
    // 다이얼로그 없이 바로 파일 선택 완료
    // setUploadDialogOpen(true); // 제거 - 다이얼로그 없이 바로 업로드 가능
  };

  const handleStartEmbedding = async () => {
    if (activeTab === 0) {
      // FTP 파이프라인 실행
      await handleFTPPipeline();
    } else if (activeTab === 1) {
      // 파일 업로드 실행
      await handleFileUpload();
    }
  };

  const handleFTPPipeline = async () => {
    // GCP 인증 확인
    if (!gcpAuthenticated) {
      const confirmLogin = window.confirm('FTP 파이프라인 실행을 위해 GCP 로그인이 필요합니다. 로그인하시겠습니까?');
      if (confirmLogin) {
        await handleGcpLogin();
        return;
      } else {
        alert('GCP 로그인이 필요합니다.');
        return;
      }
    }

    setIsProcessing(true);
    try {
      const response = await fetch('/api/ftp/pipeline', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          download_from_ftp: true,
          upload_to_gcs: true,
          process_embeddings: true,
          upload_to_vector_search: true,
        }),
      });

      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          alert('FTP 파이프라인이 시작되었습니다.');
          // 작업 목록 새로고침
          setTimeout(() => {
            fetchEmbeddingJobs();
          }, 2000);
        } else {
          alert(`FTP 파이프라인 시작 실패: ${result.message || 'Unknown error'}`);
        }
      } else {
        const errorData = await response.json().catch(() => ({ message: 'Unknown error' }));
        alert(`FTP 파이프라인 실행 실패: ${errorData.message || response.statusText}`);
      }
    } catch (error: any) {
      console.error('FTP 파이프라인 실행 실패:', error);
      alert(`FTP 파이프라인 실행 실패: ${error.message || 'Network error'}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleFileUpload = async () => {
    const filesToUpload = selectedFile ? [selectedFile] : selectedFiles;
    
    if (filesToUpload.length === 0) {
      alert('파일을 선택해주세요.');
      return;
    }

    setIsProcessing(true);
    setUploadProgress(0);

    try {
      // GCP 인증 확인 (Cloud Run에서는 Service Account 사용, 로컬 개발만 체크)
      // Cloud Run 환경에서는 체크하지 않고 진행

      // 복수 파일 업로드
      const uploadPromises = filesToUpload.map(async (file, index) => {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('/api/upload-xml', {
          method: 'POST',
          body: formData,
        });

        if (response.ok) {
          const result = await response.json();
          return { success: true, filename: file.name, job_id: result.job_id, ...result };
        } else {
          return { success: false, filename: file.name, error: 'Upload failed' };
        }
      });

      const results = await Promise.all(uploadPromises);
      
      const successCount = results.filter(r => r.success).length;
      const failCount = results.filter(r => !r.success).length;

      if (successCount > 0) {
        alert(`${successCount}개 파일 업로드 및 임베딩이 시작되었습니다.${failCount > 0 ? `\n${failCount}개 파일 업로드 실패.` : ''}`);
        // 파일 선택 초기화
        setSelectedFile(null);
        setSelectedFiles([]);
        // input 요소도 초기화
        const fileInput = document.getElementById('xml-file-upload') as HTMLInputElement;
        if (fileInput) {
          fileInput.value = '';
        }
        
        // 작업 목록 새로고침
        setTimeout(() => {
          fetchEmbeddingJobs();
        }, 2000);
      } else {
        alert(`모든 파일 업로드 실패: ${results.map(r => r.filename).join(', ')}`);
      }
    } catch (error) {
      console.error('파일 업로드 실패:', error);
      alert('파일 업로드 실패');
    } finally {
      setIsProcessing(false);
      setUploadProgress(0);
    }
  };

  const handleStopJob = async (jobId: string) => {
    try {
      const response = await fetch(`/api/embedding-jobs/${jobId}/stop`, {
        method: 'POST',
      });

      if (response.ok) {
        fetchEmbeddingJobs();
      }
    } catch (error) {
      console.error('작업 중지 실패:', error);
    }
  };

  const handleViewDetails = async (jobId: string) => {
    try {
      const response = await fetch(`/api/embedding-jobs/${jobId}`);
      if (response.ok) {
        const data = await response.json();
        alert(`작업 상세:\n${JSON.stringify(data, null, 2)}`);
      }
    } catch (error) {
      console.error('작업 상세 가져오기 실패:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'processing':
        return 'info';
      case 'failed':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle />;
      case 'processing':
        return <Functions />;
      case 'failed':
        return <ErrorIcon />;
      default:
        return <Warning />;
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 600 }}>
          Vertex AI 벡터 임베딩
        </Typography>
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
          {gcpAuthenticated ? (
            <Chip 
              icon={<CheckCircle />} 
              label={`GCP 인증됨: ${gcpAuthStatus?.active_account || 'Service Account'}`} 
              color="success" 
              size="small"
            />
          ) : (
            <>
              <Chip 
                icon={<Warning />} 
                label="GCP 로그인 필요 (로컬 개발용)" 
                color="warning" 
                size="small"
              />
              <Button
                variant="outlined"
                size="small"
                onClick={handleGcpLogin}
                startIcon={<CloudUpload />}
              >
                GCP 로그인
              </Button>
            </>
          )}
        </Box>
      </Box>

      {/* 통계 카드 */}
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3, mb: 3 }}>
        <Box sx={{ flex: '1 1 200px', minWidth: '200px' }}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="body2">
                    전체 작업
                  </Typography>
                  <Typography variant="h4">
                    {embeddingStats.totalJobs}
                  </Typography>
                </Box>
                <Functions sx={{ fontSize: 40, color: 'primary.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Box>
        <Box sx={{ flex: '1 1 200px', minWidth: '200px' }}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="body2">
                    완료된 작업
                  </Typography>
                  <Typography variant="h4" color="success.main">
                    {embeddingStats.completedJobs}
                  </Typography>
                </Box>
                <CheckCircle sx={{ fontSize: 40, color: 'success.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Box>
        <Box sx={{ flex: '1 1 200px', minWidth: '200px' }}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="body2">
                    총 임베딩 수
                  </Typography>
                  <Typography variant="h4">
                    {embeddingStats.totalEmbeddings.toLocaleString()}
                  </Typography>
                </Box>
                <CloudUpload sx={{ fontSize: 40, color: 'info.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Box>
        <Box sx={{ flex: '1 1 200px', minWidth: '200px' }}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="body2">
                    평균 처리 시간
                  </Typography>
                  <Typography variant="h4">
                    {embeddingStats.avgProcessingTime.toFixed(1)}초
                  </Typography>
                </Box>
                <Refresh sx={{ fontSize: 40, color: 'warning.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Box>
      </Box>

      {/* 작업 시작 카드 */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
            <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
              <Tab label="FTP 파이프라인" />
              <Tab label="파일 업로드" />
            </Tabs>
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            {activeTab === 0 ? (
              <>
                <Alert severity="info" sx={{ flex: 1 }}>
                  FTP 서버에서 XML 파일을 다운로드하여 임베딩 처리합니다.
                </Alert>
                <Button
                  variant="contained"
                  onClick={handleStartEmbedding}
                  disabled={isProcessing}
                  startIcon={<PlayArrow />}
                >
                  FTP 파이프라인 시작
                </Button>
              </>
            ) : (
              <>
                <input
                  accept=".xml"
                  style={{ display: 'none' }}
                  id="xml-file-upload"
                  type="file"
                  multiple
                  onChange={handleFileSelect}
                />
                <Box sx={{ display: 'flex', flexDirection: 'column', flex: 1, gap: 1 }}>
                  <label htmlFor="xml-file-upload">
                    <Button
                      variant="outlined"
                      component="span"
                      startIcon={<Upload />}
                      fullWidth
                    >
                      XML 파일 선택 (복수 선택 가능) {selectedFiles.length > 0 && `(${selectedFiles.length}개 선택됨)`}
                    </Button>
                  </label>
                  {selectedFiles.length > 0 && (
                    <Box sx={{ pl: 1 }}>
                      <Typography variant="caption" color="text.secondary">
                        선택된 파일:
                      </Typography>
                      <List dense sx={{ py: 0 }}>
                        {selectedFiles.map((file, index) => (
                          <ListItem key={index} sx={{ py: 0, px: 1 }}>
                            <ListItemText 
                              primary={file.name}
                              secondary={`${(file.size / 1024).toFixed(2)} KB`}
                            />
                            <IconButton
                              size="small"
                              onClick={() => {
                                const newFiles = selectedFiles.filter((_, i) => i !== index);
                                setSelectedFiles(newFiles);
                                if (newFiles.length === 1) {
                                  setSelectedFile(newFiles[0]);
                                } else if (newFiles.length === 0) {
                                  setSelectedFile(null);
                                }
                              }}
                            >
                              <Delete fontSize="small" />
                            </IconButton>
                          </ListItem>
                        ))}
                      </List>
                    </Box>
                  )}
                </Box>
                <Button
                  variant="contained"
                  onClick={handleStartEmbedding}
                  disabled={isProcessing || (selectedFiles.length === 0 && !selectedFile)}
                  startIcon={<PlayArrow />}
                >
                  {selectedFiles.length > 1 
                    ? `업로드 및 임베딩 (${selectedFiles.length}개 파일)`
                    : '업로드 및 임베딩'}
                </Button>
              </>
            )}
          </Box>
        </CardContent>
      </Card>

      {/* 임베딩 작업 목록 */}
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">
              임베딩 작업 목록 ({embeddingJobs.length})
            </Typography>
            <Button
              variant="outlined"
              onClick={fetchEmbeddingJobs}
              startIcon={<Refresh />}
            >
              새로고침
            </Button>
          </Box>

          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>파일명</TableCell>
                  <TableCell>상태</TableCell>
                  <TableCell>진행률</TableCell>
                  <TableCell>기사 수</TableCell>
                  <TableCell>임베딩 수</TableCell>
                  <TableCell>처리 시간</TableCell>
                  <TableCell>작성일</TableCell>
                  <TableCell align="center">작업</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {embeddingJobs.map((job) => (
                  <TableRow key={job.id}>
                    <TableCell>{job.filename}</TableCell>
                    <TableCell>
                      <Chip
                        icon={getStatusIcon(job.status)}
                        label={
                          job.status === 'pending' ? '대기' :
                          job.status === 'processing' ? '처리 중' :
                          job.status === 'completed' ? '완료' :
                          job.status === 'failed' ? '실패' : job.status
                        }
                        color={getStatusColor(job.status) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <LinearProgress
                          variant="determinate"
                          value={job.progress}
                          sx={{ flex: 1 }}
                        />
                        <Typography variant="body2" sx={{ minWidth: '40px' }}>
                          {job.progress}%
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>{job.articlesCount || '-'}</TableCell>
                    <TableCell>{job.embeddingsCount || '-'}</TableCell>
                    <TableCell>{job.processingTime ? `${job.processingTime}초` : '-'}</TableCell>
                    <TableCell>{new Date(job.createdAt).toLocaleString()}</TableCell>
                    <TableCell align="center">
                      <Box sx={{ display: 'flex', gap: 0.5 }}>
                        <IconButton
                          size="small"
                          onClick={() => handleViewDetails(job.id)}
                        >
                          <Visibility />
                        </IconButton>
                        {job.status === 'processing' && (
                          <IconButton
                            size="small"
                            color="error"
                            onClick={() => handleStopJob(job.id)}
                          >
                            <Stop />
                          </IconButton>
                        )}
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </Box>
  );
};

export default VectorEmbedding;

