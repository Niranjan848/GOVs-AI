import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
});

// ── JWT Interceptor ─────────────────────────────────────────
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('govsai_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('govsai_token');
      localStorage.removeItem('govsai_user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;

// ── Auth API ────────────────────────────────────────────────
export const authAPI = {
  signup: (email: string, password: string, name: string) =>
    api.post('/api/signup', { email, password, name }),
  login: (email: string, password: string) =>
    api.post('/api/login', { email, password }),
};

// ── Chat API ────────────────────────────────────────────────
export const chatAPI = {
  send: (message: string, chat_id?: number) =>
    api.post('/api/chat', { message, chat_id }),
  getHistory: (skip = 0, limit = 20) =>
    api.get('/api/history', { params: { skip, limit } }),
  getChat: (chatId: number) =>
    api.get(`/api/chat/${chatId}`),
};

// ── Profile API ─────────────────────────────────────────────
export const profileAPI = {
  get: () => api.get('/api/profile'),
  update: (data: Record<string, unknown>) => api.put('/api/profile', data),
  getCompletion: () => api.get('/api/profile/completion'),
};

// ── Scheme API ──────────────────────────────────────────────
export const schemeAPI = {
  list: (params?: { category?: string; state?: string; search?: string }) =>
    api.get('/api/schemes', { params }),
  get: (id: number) => api.get(`/api/schemes/${id}`),
  getRecommendations: () => api.get('/api/recommendations'),
  bookmark: (scheme_id: number) => api.post('/api/bookmark', { scheme_id }),
  getBookmarks: () => api.get('/api/bookmarks'),
  removeBookmark: (scheme_id: number) => api.delete(`/api/bookmark/${scheme_id}`),
};

// ── Notification API ────────────────────────────────────────
export const notificationAPI = {
  list: (unread_only = false) =>
    api.get('/api/notifications', { params: { unread_only } }),
  markRead: (id: number) => api.put(`/api/notifications/${id}/read`),
  markAllRead: () => api.put('/api/notifications/read-all'),
};

// ── Document API ────────────────────────────────────────────
export const documentAPI = {
  upload: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/api/upload-pdf', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  list: () => api.get('/api/documents'),
};

// ── Admin API ───────────────────────────────────────────────
export const adminAPI = {
  getStats: () => api.get('/api/admin/stats'),
  getUsers: () => api.get('/api/admin/users'),
  getAnalytics: () => api.get('/api/admin/analytics'),
};
