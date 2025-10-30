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
  const [uploadProgress, setUploadProgress] = useState(0);

  useEffect(() => {
    fetchEmbeddingJobs();
    fetchEmbeddingStats();

    // 10초마다 자동 새로고침
    const interval = setInterval(() => {
      fetchEmbeddingJobs();
      fetchEmbeddingStats();
    }, 10000);

    return () => clearInterval(interval);
  }, []);

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
    const file = event.target.files?.[0];
    if (file && file.name.endsWith('.xml')) {
      setSelectedFile(file);
      setUploadDialogOpen(true);
    } else {
      alert('XML 파일만 업로드 가능합니다.');
    }
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
        }
      }
    } catch (error) {
      console.error('FTP 파이프라인 실행 실패:', error);
      alert('FTP 파이프라인 실행 실패');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleFileUpload = async () => {
    if (!selectedFile) {
      alert('파일을 선택해주세요.');
      return;
    }

    setIsProcessing(true);
    setUploadProgress(0);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await fetch('/api/upload-xml', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          alert('파일 업로드 및 임베딩이 시작되었습니다.');
          setUploadDialogOpen(false);
          setSelectedFile(null);
          
          // 작업 목록 새로고침
          setTimeout(() => {
            fetchEmbeddingJobs();
          }, 2000);
        }
      } else {
        alert('파일 업로드 실패');
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
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
        Vertex AI 벡터 임베딩
      </Typography>

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
                  onChange={handleFileSelect}
                />
                <label htmlFor="xml-file-upload">
                  <Button
                    variant="outlined"
                    component="span"
                    startIcon={<Upload />}
                    sx={{ flex: 1 }}
                  >
                    XML 파일 선택
                  </Button>
                </label>
                <Button
                  variant="contained"
                  onClick={handleStartEmbedding}
                  disabled={isProcessing || !selectedFile}
                  startIcon={<PlayArrow />}
                >
                  업로드 및 임베딩
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

