import axios, { AxiosInstance, AxiosResponse } from 'axios';

// API 기본 URL 설정
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // 요청 인터셉터
    this.api.interceptors.request.use(
      (config) => {
        console.log(`API 요청: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        console.error('API 요청 오류:', error);
        return Promise.reject(error);
      }
    );

    // 응답 인터셉터
    this.api.interceptors.response.use(
      (response) => {
        console.log(`API 응답: ${response.status} ${response.config.url}`);
        return response;
      },
      (error) => {
        console.error('API 응답 오류:', error);
        return Promise.reject(error);
      }
    );
  }

  // FTP 관련 API
  async connectFTP(host: string, port: number, username: string, password: string) {
    return this.api.post('/api/ftp/connect', {
      host,
      port,
      username,
      password,
    });
  }

  async disconnectFTP() {
    return this.api.post('/api/ftp/disconnect');
  }

  async getFTPFiles() {
    return this.api.get('/api/ftp/files');
  }

  async downloadFTPFile(filename: string) {
    return this.api.post('/api/ftp/download', { filename });
  }

  async downloadAllFTPFiles() {
    return this.api.post('/api/ftp/download-all');
  }

  async getFTPConnectionInfo() {
    return this.api.get('/api/ftp/connection-info');
  }

  // FTP 파이프라인
  async runFTPPipeline(options: {
    deleteAfterDownload?: boolean;
    uploadToGCS?: boolean;
    createEmbeddings?: boolean;
  }) {
    return this.api.post('/api/ftp/pipeline', options);
  }

  // GCS 관련 API
  async getGCSFiles() {
    return this.api.get('/api/gcs/files');
  }

  async getGCSFile(filePath: string) {
    return this.api.get(`/api/gcs/files/${filePath}`);
  }

  // 벡터 검색 API
  async searchVectors(query: string, options: {
    searchType?: 'vector' | 'keyword' | 'hybrid';
    similarityThreshold?: number;
    maxResults?: number;
    enableReranking?: boolean;
  }) {
    return this.api.post('/api/search/vectors', {
      query,
      ...options,
    });
  }

  // 시스템 상태 API
  async getSystemStatus() {
    return this.api.get('/api/system/status');
  }

  async getSystemMetrics() {
    return this.api.get('/api/system/metrics');
  }

  // 임베딩 관련 API
  async processXMLFile(filePath: string) {
    return this.api.post('/api/process-xml', { filePath });
  }

  async getEmbeddingStatus() {
    return this.api.get('/api/embedding/status');
  }

  // 설정 관련 API
  async getSystemConfig() {
    return this.api.get('/api/config');
  }

  async updateSystemConfig(config: any) {
    return this.api.put('/api/config', config);
  }

  // 헬스 체크
  async healthCheck() {
    return this.api.get('/health');
  }
}

export default new ApiService();

