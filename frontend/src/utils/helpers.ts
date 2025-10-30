// 유틸리티 함수들

// 날짜 포맷팅
export const formatDate = (date: string | Date): string => {
  const d = new Date(date);
  return d.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
};

// 상대 시간 포맷팅
export const formatRelativeTime = (date: string | Date): string => {
  const now = new Date();
  const target = new Date(date);
  const diffInSeconds = Math.floor((now.getTime() - target.getTime()) / 1000);

  if (diffInSeconds < 60) {
    return `${diffInSeconds}초 전`;
  } else if (diffInSeconds < 3600) {
    return `${Math.floor(diffInSeconds / 60)}분 전`;
  } else if (diffInSeconds < 86400) {
    return `${Math.floor(diffInSeconds / 3600)}시간 전`;
  } else {
    return `${Math.floor(diffInSeconds / 86400)}일 전`;
  }
};

// 파일 크기 포맷팅
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

// 숫자 포맷팅 (천 단위 콤마)
export const formatNumber = (num: number): string => {
  return num.toLocaleString('ko-KR');
};

// 퍼센트 포맷팅
export const formatPercentage = (value: number, decimals: number = 1): string => {
  return `${(value * 100).toFixed(decimals)}%`;
};

// 상태 색상 반환
export const getStatusColor = (status: string): 'success' | 'warning' | 'error' | 'info' | 'default' => {
  switch (status.toLowerCase()) {
    case 'active':
    case 'connected':
    case 'running':
    case 'success':
    case 'completed':
      return 'success';
    case 'inactive':
    case 'disconnected':
    case 'stopped':
    case 'warning':
      return 'warning';
    case 'error':
    case 'failed':
      return 'error';
    case 'pending':
    case 'processing':
    case 'downloading':
      return 'info';
    default:
      return 'default';
  }
};

// 상태 아이콘 반환
export const getStatusIcon = (status: string): string => {
  switch (status.toLowerCase()) {
    case 'active':
    case 'connected':
    case 'running':
    case 'success':
    case 'completed':
      return 'CheckCircle';
    case 'inactive':
    case 'disconnected':
    case 'stopped':
    case 'warning':
      return 'Warning';
    case 'error':
    case 'failed':
      return 'Error';
    case 'pending':
    case 'processing':
    case 'downloading':
      return 'Info';
    default:
      return 'Help';
  }
};

// 로그 레벨 색상 반환
export const getLogLevelColor = (level: string): 'success' | 'warning' | 'error' | 'info' => {
  switch (level.toUpperCase()) {
    case 'INFO':
      return 'info';
    case 'WARNING':
      return 'warning';
    case 'ERROR':
      return 'error';
    case 'SUCCESS':
      return 'success';
    default:
      return 'info';
  }
};

// 검색 결과 점수 색상 반환
export const getScoreColor = (score: number): 'success' | 'warning' | 'error' => {
  if (score >= 0.9) return 'success';
  if (score >= 0.7) return 'warning';
  return 'error';
};

// 디바운스 함수
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout;
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
};

// 스로틀 함수
export const throttle = <T extends (...args: any[]) => any>(
  func: T,
  limit: number
): ((...args: Parameters<T>) => void) => {
  let inThrottle: boolean;
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
};

// 로컬 스토리지 헬퍼
export const storage = {
  get: (key: string) => {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : null;
    } catch {
      return null;
    }
  },
  set: (key: string, value: any) => {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch {
      // 스토리지 오류 무시
    }
  },
  remove: (key: string) => {
    try {
      localStorage.removeItem(key);
    } catch {
      // 스토리지 오류 무시
    }
  },
};

// 에러 메시지 추출
export const getErrorMessage = (error: any): string => {
  if (error.response?.data?.message) {
    return error.response.data.message;
  }
  if (error.message) {
    return error.message;
  }
  return '알 수 없는 오류가 발생했습니다.';
};

// API 응답 처리
export const handleApiResponse = async <T>(
  apiCall: () => Promise<{ data: T }>
): Promise<{ data: T | null; error: string | null }> => {
  try {
    const response = await apiCall();
    return { data: response.data, error: null };
  } catch (error: any) {
    return { data: null, error: getErrorMessage(error) };
  }
};

// URL 유효성 검사
export const isValidUrl = (string: string): boolean => {
  try {
    new URL(string);
    return true;
  } catch {
    return false;
  }
};

// 이메일 유효성 검사
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

// 텍스트 자르기
export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

// 배열에서 중복 제거
export const removeDuplicates = <T>(array: T[], key?: keyof T): T[] => {
  if (!key) {
    return Array.from(new Set(array));
  }
  const seen = new Set();
  return array.filter(item => {
    const value = item[key];
    if (seen.has(value)) {
      return false;
    }
    seen.add(value);
    return true;
  });
};

// 배열 그룹화
export const groupBy = <T>(array: T[], key: keyof T): Record<string, T[]> => {
  return array.reduce((groups, item) => {
    const group = String(item[key]);
    groups[group] = groups[group] || [];
    groups[group].push(item);
    return groups;
  }, {} as Record<string, T[]>);
};

// 랜덤 ID 생성
export const generateId = (length: number = 8): string => {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let result = '';
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
};
