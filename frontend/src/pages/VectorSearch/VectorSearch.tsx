import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  TextField,
  Button,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Paper,
  Divider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Slider,
  Switch,
  FormControlLabel,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  Search,
  FilterList,
  Sort,
  Refresh,
  Download,
  Share,
  Bookmark,
  TrendingUp,
} from '@mui/icons-material';

interface SearchResult {
  id: string;
  title: string;
  content: string;
  category: string;
  date: string;
  score: number;
  tags: string[];
}

const VectorSearch: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [searchType, setSearchType] = useState('hybrid');
  const [similarityThreshold, setSimilarityThreshold] = useState(0.7);
  const [maxResults, setMaxResults] = useState(20);
  const [enableReranking, setEnableReranking] = useState(true);

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    
    setIsSearching(true);
    try {
      const response = await fetch('/api/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: searchQuery,
          top_k: maxResults,
          similarity_threshold: similarityThreshold,
          filters: {},
          max_context_length: 4000,
        }),
      });
      
      if (response.ok) {
        const result = await response.json();
        if (result && result.results) {
          const formattedResults = result.results.map((item: any) => ({
            id: item.id || item.article_id || '',
            title: item.title || item.metadata?.title || '제목 없음',
            content: item.content || item.text || '',
            category: item.category || item.metadata?.category || '',
            date: item.date || item.metadata?.date || '',
            score: item.score || item.similarity || 0,
            tags: item.tags || item.metadata?.tags || [],
          }));
          setSearchResults(formattedResults);
        } else {
          setSearchResults([]);
        }
      } else {
        setSearchResults([]);
      }
    } catch (error) {
      console.error('검색 실패:', error);
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter') {
      handleSearch();
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.9) return 'success';
    if (score >= 0.7) return 'warning';
    return 'error';
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
        벡터 검색
      </Typography>

      {/* 검색 영역 */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
            <Box sx={{ flex: 1 }}>
              <TextField
                fullWidth
                label="검색어를 입력하세요"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="예: 경제 성장률, AI 기술, 반도체 투자..."
                InputProps={{
                  endAdornment: (
                    <IconButton onClick={handleSearch} disabled={isSearching}>
                      {isSearching ? <CircularProgress size={20} /> : <Search />}
                    </IconButton>
                  ),
                }}
              />
            </Box>
            <Button
              variant="contained"
              onClick={handleSearch}
              disabled={isSearching || !searchQuery.trim()}
              startIcon={<Search />}
              sx={{ height: '56px' }}
            >
              검색
            </Button>
          </Box>
        </CardContent>
      </Card>

      <Box sx={{ display: 'flex', gap: 3 }}>
        {/* 검색 옵션 */}
        <Box sx={{ flex: '0 0 300px' }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                검색 옵션
              </Typography>
              
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>검색 유형</InputLabel>
                <Select
                  value={searchType}
                  onChange={(e) => setSearchType(e.target.value)}
                >
                  <MenuItem value="vector">벡터 검색</MenuItem>
                  <MenuItem value="keyword">키워드 검색</MenuItem>
                  <MenuItem value="hybrid">하이브리드 검색</MenuItem>
                </Select>
              </FormControl>

              <Typography gutterBottom>
                유사도 임계값: {similarityThreshold}
              </Typography>
              <Slider
                value={similarityThreshold}
                onChange={(_, value) => setSimilarityThreshold(value as number)}
                min={0}
                max={1}
                step={0.1}
                marks={[
                  { value: 0, label: '0' },
                  { value: 0.5, label: '0.5' },
                  { value: 1, label: '1' },
                ]}
                sx={{ mb: 2 }}
              />

              <Typography gutterBottom>
                최대 결과 수: {maxResults}
              </Typography>
              <Slider
                value={maxResults}
                onChange={(_, value) => setMaxResults(value as number)}
                min={5}
                max={100}
                step={5}
                marks={[
                  { value: 5, label: '5' },
                  { value: 50, label: '50' },
                  { value: 100, label: '100' },
                ]}
                sx={{ mb: 2 }}
              />

              <FormControlLabel
                control={
                  <Switch
                    checked={enableReranking}
                    onChange={(e) => setEnableReranking(e.target.checked)}
                  />
                }
                label="리랭킹 활성화"
              />
            </CardContent>
          </Card>

          {/* 검색 히스토리 */}
          <Card sx={{ mt: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                최근 검색
              </Typography>
              <List dense>
                <ListItem>
                  <ListItemText primary="경제 성장률" secondary="2시간 전" />
                </ListItem>
                <ListItem>
                  <ListItemText primary="AI 기술 발전" secondary="1일 전" />
                </ListItem>
                <ListItem>
                  <ListItemText primary="반도체 투자" secondary="2일 전" />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Box>

        {/* 검색 결과 */}
        <Box sx={{ flex: 1 }}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  검색 결과 ({searchResults.length}개)
                </Typography>
                <Box>
                  <IconButton>
                    <Sort />
                  </IconButton>
                  <IconButton>
                    <FilterList />
                  </IconButton>
                  <IconButton>
                    <Refresh />
                  </IconButton>
                </Box>
              </Box>

              {searchResults.length === 0 && !isSearching && (
                <Alert severity="info">
                  검색어를 입력하고 검색 버튼을 클릭하세요.
                </Alert>
              )}

              {isSearching && (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                  <CircularProgress />
                </Box>
              )}

              {searchResults.map((result, index) => (
                <Paper key={result.id} sx={{ p: 2, mb: 2, border: '1px solid #e0e0e0' }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                    <Typography variant="h6" sx={{ fontWeight: 600, flex: 1 }}>
                      {result.title}
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Chip
                        label={`${(result.score * 100).toFixed(1)}%`}
                        color={getScoreColor(result.score) as any}
                        size="small"
                      />
                      <IconButton size="small">
                        <Bookmark />
                      </IconButton>
                      <IconButton size="small">
                        <Share />
                      </IconButton>
                    </Box>
                  </Box>

                  <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                    {result.content}
                  </Typography>

                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <Chip label={result.category} size="small" variant="outlined" />
                    <Typography variant="caption" color="text.secondary">
                      {result.date}
                    </Typography>
                  </Box>

                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {result.tags.map((tag) => (
                      <Chip key={tag} label={tag} size="small" variant="outlined" />
                    ))}
                  </Box>
                </Paper>
              ))}
            </CardContent>
          </Card>
        </Box>
      </Box>
    </Box>
  );
};

export default VectorSearch;