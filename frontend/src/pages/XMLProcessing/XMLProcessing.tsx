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
  Grid,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  PlayArrow,
  Stop,
  CheckCircle,
  Error,
  Warning,
  Info,
  Description,
  Settings,
  ExpandMore,
  Upload,
  Download,
  Refresh,
  Delete,
  Visibility,
} from '@mui/icons-material';

interface XMLFile {
  name: string;
  size: number;
  modified: string;
  status: 'pending' | 'processing' | 'processed' | 'error';
  articles_count?: number;
  processing_time?: number;
}

interface ProcessingResult {
  success: boolean;
  processed_files: number;
  total_articles: number;
  errors: string[];
  processing_time: number;
}

const XMLProcessing: React.FC = () => {
  const [xmlFiles, setXmlFiles] = useState<XMLFile[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingProgress, setProcessingProgress] = useState(0);
  const [processingResult, setProcessingResult] = useState<ProcessingResult | null>(null);
  const [selectedFiles, setSelectedFiles] = useState<string[]>([]);
  const [settingsDialogOpen, setSettingsDialogOpen] = useState(false);
  
  // 설정 옵션들
  const [extractMetadata, setExtractMetadata] = useState(true);
  const [createEmbeddings, setCreateEmbeddings] = useState(true);
  const [updateIndex, setUpdateIndex] = useState(true);
  const [batchSize, setBatchSize] = useState(10);
  const [parallelProcessing, setParallelProcessing] = useState(true);

  // 컴포넌트 마운트 시 XML 파일 목록 가져오기
  useEffect(() => {
    loadXMLFiles();
  }, []);

  const loadXMLFiles = async () => {
    try {
      const response = await fetch('/api/xml/files', {
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
            articles_count: file.articles_count,
            processing_time: file.processing_time,
          }));
          setXmlFiles(formattedFiles);
        }
      }
    } catch (error) {
      console.error('XML 파일 목록 조회 실패:', error);
    }
  };

  const handleProcessSelected = async () => {
    if (selectedFiles.length === 0) return;
    
    setIsProcessing(true);
    setProcessingProgress(0);
    setProcessingResult(null);

    try {
      const response = await fetch('/api/process-xml', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          files: selectedFiles,
          extract_metadata: extractMetadata,
          create_embeddings: createEmbeddings,
          update_index: updateIndex,
          batch_size: batchSize,
          parallel_processing: parallelProcessing,
        }),
      });
      
      if (response.ok) {
        const result = await response.json();
        setProcessingResult(result);
        
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
        if (result.processed_files) {
          setXmlFiles(prev => 
            prev.map(file => {
              if (selectedFiles.includes(file.name)) {
                return { 
                  ...file, 
                  status: result.success ? 'processed' : 'error',
                  articles_count: result.total_articles || file.articles_count,
                  processing_time: result.processing_time || file.processing_time,
                };
              }
              return file;
            })
          );
        }
      } else {
        setIsProcessing(false);
      }
    } catch (error) {
      console.error('XML 처리 실패:', error);
      setIsProcessing(false);
    }
  };

  const handleProcessAll = async () => {
    const allFileNames = xmlFiles.map(file => file.name);
    setSelectedFiles(allFileNames);
    await handleProcessSelected();
  };

  const handleIncrementalProcess = async () => {
    setIsProcessing(true);
    setProcessingProgress(0);
    setProcessingResult(null);

    try {
      const response = await fetch('/api/incremental-process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          extract_metadata: extractMetadata,
          create_embeddings: createEmbeddings,
          update_index: updateIndex,
          batch_size: batchSize,
        }),
      });
      
      if (response.ok) {
        const result = await response.json();
        setProcessingResult(result);
        
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
        
        // 파일 목록 새로고침
        loadXMLFiles();
      } else {
        setIsProcessing(false);
      }
    } catch (error) {
      console.error('증분 처리 실패:', error);
      setIsProcessing(false);
    }
  };

  const handleFileSelect = (fileName: string) => {
    setSelectedFiles(prev => 
      prev.includes(fileName) 
        ? prev.filter(name => name !== fileName)
        : [...prev, fileName]
    );
  };

  const handleSelectAll = () => {
    if (selectedFiles.length === xmlFiles.length) {
      setSelectedFiles([]);
    } else {
      setSelectedFiles(xmlFiles.map(file => file.name));
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'processed':
        return 'success';
      case 'processing':
        return 'info';
      case 'error':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'processed':
        return <CheckCircle />;
      case 'processing':
        return <PlayArrow />;
      case 'error':
        return <Error />;
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
        XML 파일 처리
      </Typography>

      {/* 처리 옵션 및 버튼 */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">
              처리 옵션
            </Typography>
            <Box>
              <Button
                variant="outlined"
                onClick={() => setSettingsDialogOpen(true)}
                startIcon={<Settings />}
                sx={{ mr: 1 }}
              >
                설정
              </Button>
              <Button
                variant="contained"
                onClick={handleProcessSelected}
                disabled={isProcessing || selectedFiles.length === 0}
                startIcon={<PlayArrow />}
                sx={{ mr: 1 }}
              >
                선택된 파일 처리 ({selectedFiles.length})
              </Button>
              <Button
                variant="contained"
                onClick={handleProcessAll}
                disabled={isProcessing || xmlFiles.length === 0}
                startIcon={<PlayArrow />}
                sx={{ mr: 1 }}
              >
                전체 처리
              </Button>
              <Button
                variant="outlined"
                onClick={handleIncrementalProcess}
                disabled={isProcessing}
                startIcon={<Refresh />}
              >
                증분 처리
              </Button>
            </Box>
          </Box>

          {isProcessing && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" gutterBottom>
                XML 파일 처리 중... ({processingProgress}%)
              </Typography>
              <LinearProgress variant="determinate" value={processingProgress} />
            </Box>
          )}

          {processingResult && (
            <Alert 
              severity={processingResult.success ? 'success' : 'error'} 
              sx={{ mt: 2 }}
            >
              <Typography variant="body2">
                <strong>처리 결과:</strong> {processingResult.processed_files}개 파일 처리 완료
                {processingResult.total_articles && `, ${processingResult.total_articles}개 기사 추출`}
                {processingResult.processing_time && `, 처리 시간: ${processingResult.processing_time}초`}
              </Typography>
              {processingResult.errors && processingResult.errors.length > 0 && (
                <Box sx={{ mt: 1 }}>
                  <Typography variant="body2" color="error">
                    오류: {processingResult.errors.join(', ')}
                  </Typography>
                </Box>
              )}
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* XML 파일 목록 */}
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">
              XML 파일 목록 ({xmlFiles.length}개)
            </Typography>
            <Box>
              <Button
                variant="outlined"
                onClick={handleSelectAll}
                startIcon={<CheckCircle />}
                sx={{ mr: 1 }}
              >
                {selectedFiles.length === xmlFiles.length ? '전체 해제' : '전체 선택'}
              </Button>
              <Button
                variant="outlined"
                onClick={loadXMLFiles}
                startIcon={<Refresh />}
              >
                새로고침
              </Button>
            </Box>
          </Box>

          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell padding="checkbox">
                    <input
                      type="checkbox"
                      checked={selectedFiles.length === xmlFiles.length && xmlFiles.length > 0}
                      onChange={handleSelectAll}
                    />
                  </TableCell>
                  <TableCell>파일명</TableCell>
                  <TableCell>크기</TableCell>
                  <TableCell>수정일</TableCell>
                  <TableCell>기사 수</TableCell>
                  <TableCell>처리 시간</TableCell>
                  <TableCell>상태</TableCell>
                  <TableCell align="center">작업</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {xmlFiles.map((file) => (
                  <TableRow key={file.name}>
                    <TableCell padding="checkbox">
                      <input
                        type="checkbox"
                        checked={selectedFiles.includes(file.name)}
                        onChange={() => handleFileSelect(file.name)}
                      />
                    </TableCell>
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
                      <Typography variant="body2">
                        {file.articles_count || '-'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {file.processing_time ? `${file.processing_time}초` : '-'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        icon={getStatusIcon(file.status)}
                        label={
                          file.status === 'pending' ? '대기' :
                          file.status === 'processing' ? '처리 중' :
                          file.status === 'processed' ? '완료' :
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
                          onClick={() => {/* 파일 미리보기 */}}
                        >
                          <Visibility />
                        </IconButton>
                        <IconButton
                          size="small"
                          onClick={() => {/* 파일 삭제 */}}
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

      {/* 설정 다이얼로그 */}
      <Dialog open={settingsDialogOpen} onClose={() => setSettingsDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>XML 처리 설정</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <FormControlLabel
              control={
                <Switch
                  checked={extractMetadata}
                  onChange={(e) => setExtractMetadata(e.target.checked)}
                />
              }
              label="메타데이터 추출"
            />
            <FormControlLabel
              control={
                <Switch
                  checked={createEmbeddings}
                  onChange={(e) => setCreateEmbeddings(e.target.checked)}
                />
              }
              label="벡터 임베딩 생성"
            />
            <FormControlLabel
              control={
                <Switch
                  checked={updateIndex}
                  onChange={(e) => setUpdateIndex(e.target.checked)}
                />
              }
              label="인덱스 업데이트"
            />
            <FormControlLabel
              control={
                <Switch
                  checked={parallelProcessing}
                  onChange={(e) => setParallelProcessing(e.target.checked)}
                />
              }
              label="병렬 처리"
            />
            <FormControl sx={{ mt: 2, minWidth: 200 }}>
              <InputLabel>배치 크기</InputLabel>
              <Select
                value={batchSize}
                onChange={(e) => setBatchSize(Number(e.target.value))}
                label="배치 크기"
              >
                <MenuItem value={5}>5</MenuItem>
                <MenuItem value={10}>10</MenuItem>
                <MenuItem value={20}>20</MenuItem>
                <MenuItem value={50}>50</MenuItem>
              </Select>
            </FormControl>
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

export default XMLProcessing;
