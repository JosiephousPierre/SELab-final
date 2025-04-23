import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Add request interceptor to include authentication token if available
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      
      // For fallback tokens, also send user data in headers
      if (token.startsWith('user_fallback_token_')) {
        const userStr = localStorage.getItem('user') || sessionStorage.getItem('user');
        if (userStr) {
          config.headers['X-User-Data'] = userStr;
        }
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Schedule API
export const scheduleAPI = {
  getAll: (semesterId) => {
    const params = {};
    if (semesterId) params.semester_id = semesterId;
    return api.get('/schedules', { params });
  },
  getByStatus: (status) => api.get(`/schedules/status/${status}`),
  create: (scheduleData) => api.post('/schedules', scheduleData),
  update: (id, scheduleData) => {
    console.log(`API call: Updating schedule ${id} with data:`, scheduleData);
    
    try {
      // Create a new object with only the fields that the API expects
      const cleanedData = { ...scheduleData };
      
      // Make sure we don't send the ID in the body if it's already in the URL
      if (cleanedData.id === parseInt(id)) {
        delete cleanedData.id;
      }
      
      // Handle potential null values
      if (cleanedData.second_day === undefined) {
        cleanedData.second_day = null;
      }
      
      // Ensure schedule_types is an array
      if (!Array.isArray(cleanedData.schedule_types)) {
        cleanedData.schedule_types = cleanedData.schedule_types ? [cleanedData.schedule_types] : [];
      }
      
      console.log(`API call: Sending cleaned data:`, cleanedData);
      return api.put(`/schedules/${id}`, cleanedData);
    } catch (error) {
      console.error(`Error preparing update for schedule ${id}:`, error);
      return Promise.reject(error);
    }
  },
  updateStatus: (id, status) => api.patch(`/schedules/${id}/status`, { status }),
  updateBulkStatus: (scheduleIds, status, semesterId) => {
    console.log(`API call: Bulk updating ${scheduleIds.length} schedules to status: ${status}`);
    return api.patch('/schedules/bulk-status-update', { 
      schedule_ids: scheduleIds,
      status: status,
      semester_id: semesterId
    });
  },
  delete: (id) => api.delete(`/schedules/${id}`),
  deleteAll: () => api.delete('/schedules/all')
};

// Semester API
export const semesterAPI = {
  getAll: () => api.get('/semesters'),
  getById: (id) => api.get(`/semesters/${id}`),
  create: (semesterData) => api.post('/semesters', semesterData)
};

// LabRoom API
export const labRoomAPI = {
  getAll: () => api.get('/lab-rooms'),
  getById: (id) => api.get(`/lab-rooms/${id}`)
};

// Instructors API
export const instructorAPI = {
  getAll: () => api.get('/instructors'),
  getById: (id) => api.get(`/instructors/${id}`),
  create: (instructorData) => api.post('/instructors', instructorData)
};

// Notifications API
export const notificationAPI = {
  getAll: (params) => api.get('/notifications', { params }),
  getByUser: (userId) => api.get(`/users/${userId}/notifications`),
  getUnreadCount: (userId) => api.get(`/users/${userId}/notifications/unread/count`),
  markAsRead: (userId, notificationId) => api.patch(`/users/${userId}/notifications/${notificationId}/read`),
  markAllAsRead: (userId) => api.patch(`/users/${userId}/notifications/read-all`),
  create: (notificationData) => api.post('/notifications', notificationData)
};

// System Settings API
export const systemSettingsAPI = {
  getSetting: (key) => api.get(`/system-settings/${key}`),
  updateSetting: (key, value, description = null) => 
    api.put(`/system-settings/${key}`, { 
      setting_value: value, 
      description: description 
    }),
  getCurrentDisplaySemester: () => api.get('/system-settings/display-semester/current')
};

// Course Offerings API
export const courseOfferingAPI = {
  getAll: () => api.get('/course-offerings'),
  getById: (id) => api.get(`/course-offerings/${id}`),
  create: (courseData) => api.post('/course-offerings', courseData),
  update: (id, courseData) => api.put(`/course-offerings/${id}`, courseData),
  delete: (id) => api.delete(`/course-offerings/${id}`),
  deleteAll: () => api.delete('/course-offerings/all')
};

// User API
export const userAPI = {
  getProfile: (userId) => api.get(`/users/${userId}/profile`),
  updateProfile: (userId, userData) => api.put(`/users/${userId}/profile`, userData),
  getCurrentUser: () => {
    const token = sessionStorage.getItem('token') || localStorage.getItem('token');
    const userStr = sessionStorage.getItem('user') || localStorage.getItem('user');
    
    if (!token || !userStr) {
      return Promise.reject(new Error('No authentication found'));
    }
    
    try {
      const userData = JSON.parse(userStr);
      return api.get(`/users/${userData.id}/profile`);
    } catch (error) {
      return Promise.reject(error);
    }
  },
  getAllUsers: () => api.get('/users/all'),
  getApprovedUsers: () => api.get('/users/approved'),
  updateRole: (userId, role) => api.put(`/users/${userId}/role`, { role }),
  deactivateUser: (userId) => api.put(`/users/${userId}/deactivate`),
  activateUser: (userId) => api.put(`/users/${userId}/activate`),
  deleteUser: (userId) => api.delete(`/users/${userId}`)
};

export default api; 