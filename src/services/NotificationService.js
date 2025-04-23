import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

class NotificationService {
  // Get all notifications for the current user
  async getNotifications(filterType = 'all', sortBy = 'newest') {
    const token = sessionStorage.getItem('token') || localStorage.getItem('token');
    const userStr = sessionStorage.getItem('user') || localStorage.getItem('user');
    
    try {
      let userId = null;
      if (userStr) {
        const userData = JSON.parse(userStr);
        userId = userData.id;
        console.log('NotificationService: Using user ID from storage:', userId);
        console.log('NotificationService: Complete user data:', userData);
      }
      
      if (!userId) {
        console.error('No user ID found in storage');
        return [];
      }
      
      console.log(`NotificationService: Fetching notifications with params: filter_type=${filterType}, sort_by=${sortBy}, user_id=${userId}`);
      
      const response = await axios.get(`${API_URL}/notifications`, {
        params: { 
          filter_type: filterType, 
          sort_by: sortBy,
          user_id: userId  // Explicitly include user_id as query parameter
        },
        headers: {
          'Authorization': `Bearer ${token}`,
          'X-User-ID': userId  // Also include as header for redundancy
        }
      });
      
      console.log('NotificationService: Received response from server:', response.data);
      return response.data;
    } catch (error) {
      console.error('Error fetching notifications:', error);
      if (error.response) {
        console.error('Server response:', error.response.data);
        console.error('Status code:', error.response.status);
      }
      return [];
    }
  }
  
  // Get notifications specifically for Dean
  async getDeanNotifications(filterType = 'all', sortBy = 'newest') {
    const token = sessionStorage.getItem('token') || localStorage.getItem('token');
    
    try {
      console.log(`Dean notification service: Fetching notifications from database with params: filter_type=${filterType}, sort_by=${sortBy}`);
      
      // Use the new endpoint that directly identifies the Dean in the database
      const response = await axios.get(`${API_URL}/dean-notifications`, {
        params: { 
          filter_type: filterType, 
          sort_by: sortBy
        },
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      console.log(`Dean notification service: Received ${response.data.length} notifications from database endpoint`);
      return response.data;
    } catch (error) {
      console.error('Dean notification service: Error fetching notifications from database:', error);
      if (error.response) {
        console.error('Server response:', error.response.data);
        console.error('Status code:', error.response.status);
        
        if (error.response.status === 404) {
          console.error('No Dean user found in the database. Please ensure a user with role "Dean" exists.');
        }
      }
      return [];
    }
  }

  // Mark a notification as read
  async markAsRead(notificationId) {
    const token = sessionStorage.getItem('token') || localStorage.getItem('token');
    const userStr = sessionStorage.getItem('user') || localStorage.getItem('user');
    
    try {
      let userId = null;
      if (userStr) {
        const userData = JSON.parse(userStr);
        userId = userData.id;
      }
      
      if (!userId) {
        console.error('No user ID found in storage');
        throw new Error('User ID required');
      }
      
      const response = await axios.patch(`${API_URL}/notifications/${notificationId}/read`, {}, {
        params: { user_id: userId },
        headers: {
          'Authorization': `Bearer ${token}`,
          'X-User-ID': userId  // Include as header as well
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error marking notification as read:', error);
      throw error;
    }
  }

  // Mark all notifications as read
  async markAllAsRead() {
    const token = sessionStorage.getItem('token') || localStorage.getItem('token');
    const userStr = sessionStorage.getItem('user') || localStorage.getItem('user');
    
    try {
      let userId = null;
      if (userStr) {
        const userData = JSON.parse(userStr);
        userId = userData.id;
      }
      
      if (!userId) {
        console.error('No user ID found in storage');
        throw new Error('User ID required');
      }
      
      const response = await axios.patch(`${API_URL}/notifications/read-all`, {}, {
        params: { user_id: userId },
        headers: {
          'Authorization': `Bearer ${token}`,
          'X-User-ID': userId  // Include as header as well
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error marking all notifications as read:', error);
      throw error;
    }
  }

  // Get the count of unread notifications
  async getUnreadCount() {
    const token = sessionStorage.getItem('token') || localStorage.getItem('token');
    const userStr = sessionStorage.getItem('user') || localStorage.getItem('user');
    
    try {
      let userId = null;
      if (userStr) {
        const userData = JSON.parse(userStr);
        userId = userData.id;
      }
      
      if (!userId) {
        console.error('No user ID found in storage');
        return 0;
      }
      
      const response = await axios.get(`${API_URL}/notifications/unread-count`, {
        params: { user_id: userId },
        headers: {
          'Authorization': `Bearer ${token}`,
          'X-User-ID': userId  // Include as header as well
        }
      });
      return response.data.count;
    } catch (error) {
      console.error('Error fetching unread notification count:', error);
      return 0;
    }
  }

  // Clear all notifications for the current user (permanently)
  async clearAllNotifications() {
    const token = sessionStorage.getItem('token') || localStorage.getItem('token');
    const userStr = sessionStorage.getItem('user') || localStorage.getItem('user');
    
    try {
      let userId = null;
      if (userStr) {
        const userData = JSON.parse(userStr);
        userId = userData.id;
      }
      
      if (!userId) {
        console.error('No user ID found in storage');
        throw new Error('User ID required');
      }
      
      const response = await axios.delete(`${API_URL}/notifications/clear-all`, {
        params: { user_id: userId },
        headers: {
          'Authorization': `Bearer ${token}`,
          'X-User-ID': userId  // Include as header as well
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error clearing notifications:', error);
      throw error;
    }
  }

  // Mark a Dean notification as read
  async markDeanAsRead(notificationId) {
    const token = sessionStorage.getItem('token') || localStorage.getItem('token');
    
    try {
      console.log(`Dean notification service: Marking notification ${notificationId} as read`);
      
      const response = await axios.patch(`${API_URL}/dean-notifications/${notificationId}/read`, {}, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      console.log('Dean notification service: Successfully marked notification as read');
      return response.data;
    } catch (error) {
      console.error('Dean notification service: Error marking notification as read:', error);
      if (error.response) {
        console.error('Server response:', error.response.data);
        console.error('Status code:', error.response.status);
      }
      throw error;
    }
  }

  // Mark all Dean notifications as read
  async markAllDeanAsRead() {
    const token = sessionStorage.getItem('token') || localStorage.getItem('token');
    
    try {
      console.log('Dean notification service: Marking all notifications as read');
      
      const response = await axios.patch(`${API_URL}/dean-notifications/read-all`, {}, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      console.log('Dean notification service: Successfully marked all notifications as read');
      return response.data;
    } catch (error) {
      console.error('Dean notification service: Error marking all notifications as read:', error);
      if (error.response) {
        console.error('Server response:', error.response.data);
        console.error('Status code:', error.response.status);
      }
      throw error;
    }
  }

  // Clear all Dean notifications
  async clearAllDeanNotifications() {
    const token = sessionStorage.getItem('token') || localStorage.getItem('token');
    
    try {
      console.log('Dean notification service: Clearing all notifications');
      
      const response = await axios.delete(`${API_URL}/dean-notifications/clear-all`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      console.log('Dean notification service: Successfully cleared all notifications');
      return response.data;
    } catch (error) {
      console.error('Dean notification service: Error clearing all notifications:', error);
      if (error.response) {
        console.error('Server response:', error.response.data);
        console.error('Status code:', error.response.status);
      }
      throw error;
    }
  }

  // Get notifications specifically for Academic Coordinator
  async getAcadCoorNotifications(filterType = 'all', sortBy = 'newest') {
    const token = sessionStorage.getItem('token') || localStorage.getItem('token');
    
    try {
      console.log(`Academic Coordinator notification service: Fetching notifications from database with params: filter_type=${filterType}, sort_by=${sortBy}`);
      
      // Use the new endpoint that directly identifies the Academic Coordinator in the database
      const response = await axios.get(`${API_URL}/acad-coor-notifications`, {
        params: { 
          filter_type: filterType, 
          sort_by: sortBy
        },
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      console.log(`Academic Coordinator notification service: Received ${response.data.length} notifications from database endpoint`);
      return response.data;
    } catch (error) {
      console.error('Academic Coordinator notification service: Error fetching notifications from database:', error);
      if (error.response) {
        console.error('Server response:', error.response.data);
        console.error('Status code:', error.response.status);
        
        if (error.response.status === 404) {
          console.error('No Academic Coordinator user found in the database. Please ensure a user with role "Academic Coordinator" exists.');
        }
      }
      return [];
    }
  }

  // Mark an Academic Coordinator notification as read
  async markAcadCoorAsRead(notificationId) {
    const token = sessionStorage.getItem('token') || localStorage.getItem('token');
    
    try {
      console.log(`Academic Coordinator notification service: Marking notification ${notificationId} as read`);
      
      const response = await axios.patch(`${API_URL}/acad-coor-notifications/${notificationId}/read`, {}, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      console.log('Academic Coordinator notification service: Successfully marked notification as read');
      return response.data;
    } catch (error) {
      console.error('Academic Coordinator notification service: Error marking notification as read:', error);
      if (error.response) {
        console.error('Server response:', error.response.data);
        console.error('Status code:', error.response.status);
      }
      throw error;
    }
  }

  // Mark all Academic Coordinator notifications as read
  async markAllAcadCoorAsRead() {
    const token = sessionStorage.getItem('token') || localStorage.getItem('token');
    
    try {
      console.log('Academic Coordinator notification service: Marking all notifications as read');
      
      const response = await axios.patch(`${API_URL}/acad-coor-notifications/read-all`, {}, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      console.log('Academic Coordinator notification service: Successfully marked all notifications as read');
      return response.data;
    } catch (error) {
      console.error('Academic Coordinator notification service: Error marking all notifications as read:', error);
      if (error.response) {
        console.error('Server response:', error.response.data);
        console.error('Status code:', error.response.status);
      }
      throw error;
    }
  }

  // Clear all Academic Coordinator notifications
  async clearAllAcadCoorNotifications() {
    const token = sessionStorage.getItem('token') || localStorage.getItem('token');
    
    try {
      console.log('Academic Coordinator notification service: Clearing all notifications');
      
      const response = await axios.delete(`${API_URL}/acad-coor-notifications/clear-all`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      console.log('Academic Coordinator notification service: Successfully cleared all notifications');
      return response.data;
    } catch (error) {
      console.error('Academic Coordinator notification service: Error clearing all notifications:', error);
      if (error.response) {
        console.error('Server response:', error.response.data);
        console.error('Status code:', error.response.status);
      }
      throw error;
    }
  }

  // Get the count of unread notifications specifically for Dean
  async getDeanUnreadCount() {
    const token = sessionStorage.getItem('token') || localStorage.getItem('token');
    
    try {
      console.log('Dean notification service: Fetching unread notification count');
      
      // Use a role-specific endpoint for the Dean
      const response = await axios.get(`${API_URL}/dean-notifications/unread-count`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      console.log(`Dean notification service: Unread count = ${response.data.count}`);
      return response.data.count;
    } catch (error) {
      console.error('Dean notification service: Error fetching unread notification count:', error);
      if (error.response) {
        console.error('Server response:', error.response.data);
        console.error('Status code:', error.response.status);
        
        if (error.response.status === 404) {
          console.error('No Dean user found in the database. Please ensure a user with role "Dean" exists.');
        }
      }
      return 0;
    }
  }

  // Get the count of unread notifications specifically for Academic Coordinator
  async getAcadCoorUnreadCount() {
    const token = sessionStorage.getItem('token') || localStorage.getItem('token');
    
    try {
      console.log('Academic Coordinator notification service: Fetching unread notification count');
      
      // Use a role-specific endpoint for the Academic Coordinator
      const response = await axios.get(`${API_URL}/acad-coor-notifications/unread-count`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      console.log(`Academic Coordinator notification service: Unread count = ${response.data.count}`);
      return response.data.count;
    } catch (error) {
      console.error('Academic Coordinator notification service: Error fetching unread notification count:', error);
      if (error.response) {
        console.error('Server response:', error.response.data);
        console.error('Status code:', error.response.status);
        
        if (error.response.status === 404) {
          console.error('No Academic Coordinator user found in the database. Please ensure a user with role "Academic Coordinator" exists.');
        }
      }
      return 0;
    }
  }
}

export default new NotificationService(); 