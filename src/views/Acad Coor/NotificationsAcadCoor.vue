// NotificationsAcadCoor.vue
<template>
  <div class="dashboard-layout">
    <DashBoardSidebar />
    <div class="main-content">
      <DashBoardTopbar :pageTitle="'Notifications'" />
      <div class="content-wrapper">
        <h1>Notifications</h1>
        
        <div class="filters">
          <div class="dropdown-container">
            <select v-model="selectedFilter" class="filter-dropdown" @change="fetchNotifications">
              <option value="all">All Notifications</option>
              <option value="schedule">Schedule Updates</option>
              <option value="system">System Announcements</option>
            </select>
          </div>
          
          <div class="dropdown-container">
            <select v-model="sortBy" class="filter-dropdown" @change="fetchNotifications">
              <option value="newest">Sort By: Newest</option>
              <option value="oldest">Sort By: Oldest</option>
            </select>
          </div>
          
          <button v-if="notifications.length > 0" @click="markAllAsRead" class="mark-all-btn">
            Mark All as Read
          </button>
          
          <button v-if="notifications.length > 0" @click="clearNotifications" class="clear-all-btn">
            Clear Notifications
          </button>
        </div>

        <div v-if="loading" class="loading-spinner">
          Loading notifications...
        </div>

        <div v-else class="notifications-list">
          <div v-if="notifications.length === 0" class="no-notifications">
            No notifications available
          </div>
          
          <div v-else>
            <div 
              v-for="notification in notifications" 
              :key="notification.id" 
              class="notification-item"
              :class="{ 'unread': !notification.is_read }"
              @click="markAsRead(notification)"
            >
              <div class="notification-icon" :class="notification.type">
                <i :class="getIconClass(notification.type)"></i>
              </div>
              <div class="notification-content">
                <div class="notification-header">
                  <h3 class="notification-title">{{ notification.title }}</h3>
                  <span class="notification-time">{{ formatTime(notification.created_at) }}</span>
                </div>
                <p class="notification-message">{{ notification.message }}</p>
              </div>
              <div v-if="!notification.is_read" class="unread-indicator"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import DashBoardSidebar from '../../components/DashBoardSidebarAcadCoor.vue'
import DashBoardTopbar from '../../components/DashBoardTopbar.vue'
import NotificationService from '../../services/NotificationService'

export default {
  name: 'NotificationsAcadCoor',
  components: {
    DashBoardSidebar,
    DashBoardTopbar
  },
  data() {
    return {
      selectedFilter: 'all',
      sortBy: 'newest',
      notifications: [],
      loading: false
    }
  },
  created() {
    this.checkAuth();
    this.fetchNotifications();
  },
  methods: {
    checkAuth() {
      // Check if user is authenticated and has the correct role
      const token = sessionStorage.getItem('token') || localStorage.getItem('token');
      const userStr = sessionStorage.getItem('user') || localStorage.getItem('user');
      
      if (!token || !userStr) {
        console.error('No authentication found, redirecting to login');
        this.$router.push('/login');
        return;
      }
      
      try {
        const userData = JSON.parse(userStr);
        
        // Verify the user has Academic Coordinator role
        if (userData.role !== 'Academic Coordinator') {
          console.error('User does not have Academic Coordinator role');
          // Redirect to the appropriate dashboard based on role
          if (userData.role === 'System Administrator') {
            this.$router.push('/dashboard-sysad');
          } else if (userData.role === 'Dean') {
            this.$router.push('/dashboard-dean');
          } else if (userData.role === 'Lab InCharge') {
            this.$router.push('/dashboard-lab');
          } else {
            this.$router.push('/dashboard-viewer');
          }
        }
      } catch (error) {
        console.error('Error parsing user data:', error);
        this.$router.push('/login');
      }
    },
    async fetchNotifications() {
      this.loading = true;
      try {
        // First, check authentication
        const token = sessionStorage.getItem('token') || localStorage.getItem('token');
        
        if (!token) {
          console.error('Academic Coordinator: No authentication token found, cannot fetch notifications');
          this.loading = false;
          return;
        }
        
        // Log debug information
        console.log('Academic Coordinator: Fetching notifications with filter:', this.selectedFilter, 'sort:', this.sortBy);
        
        // Use the Academic Coordinator-specific notification method that directly queries the database for the Academic Coordinator user
        console.log('Academic Coordinator: Calling NotificationService.getAcadCoorNotifications()');
        this.notifications = await NotificationService.getAcadCoorNotifications(this.selectedFilter, this.sortBy);
        console.log('Academic Coordinator: Notifications received:', this.notifications);
        
        // Check if we got notifications
        if (!this.notifications || this.notifications.length === 0) {
          console.warn('Academic Coordinator: No notifications returned from backend');
        } else {
          console.log(`Academic Coordinator: Successfully received ${this.notifications.length} notifications`);
        }
      } catch (error) {
        console.error('Academic Coordinator: Failed to fetch notifications:', error);
        if (error.response) {
          console.error('Academic Coordinator: Error response data:', error.response.data);
          console.error('Academic Coordinator: Error response status:', error.response.status);
        }
      } finally {
        this.loading = false;
      }
    },
    async markAsRead(notification) {
      if (!notification.is_read) {
        try {
          // Use the Academic Coordinator-specific method to mark a notification as read
          await NotificationService.markAcadCoorAsRead(notification.id);
          notification.is_read = true;
          notification.read_at = new Date().toISOString();
        } catch (error) {
          console.error('Academic Coordinator: Failed to mark notification as read:', error);
        }
      }
    },
    async markAllAsRead() {
      try {
        // Use the Academic Coordinator-specific method to mark all notifications as read
        await NotificationService.markAllAcadCoorAsRead();
        // Update UI to reflect changes
        this.notifications.forEach(notification => {
          notification.is_read = true;
          notification.read_at = new Date().toISOString();
        });
      } catch (error) {
        console.error('Academic Coordinator: Failed to mark all notifications as read:', error);
      }
    },
    async clearNotifications() {
      try {
        // Show confirmation dialog
        if (confirm('Are you sure you want to clear all notifications? This cannot be undone.')) {
          // Clear notifications using the Academic Coordinator-specific method
          await NotificationService.clearAllAcadCoorNotifications();
          // Clear notifications in the frontend
          this.notifications = [];
        }
      } catch (error) {
        console.error('Academic Coordinator: Failed to clear notifications:', error);
      }
    },
    formatTime(timestamp) {
      if (!timestamp) return '';
      
      const date = new Date(timestamp);
      const now = new Date();
      const diff = Math.floor((now - date) / 1000); // diff in seconds
      
      if (diff < 60) {
        return 'Just now';
      } else if (diff < 3600) {
        const minutes = Math.floor(diff / 60);
        return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
      } else if (diff < 86400) {
        const hours = Math.floor(diff / 3600);
        return `${hours} hour${hours > 1 ? 's' : ''} ago`;
      } else if (diff < 604800) {
        const days = Math.floor(diff / 86400);
        return `${days} day${days > 1 ? 's' : ''} ago`;
      } else {
        const options = { month: 'short', day: 'numeric' };
        return date.toLocaleDateString('en-US', options);
      }
    },
    getIconClass(type) {
      switch (type) {
        case 'info': return 'fas fa-info-circle';
        case 'alert': return 'fas fa-exclamation-triangle';
        case 'success': return 'fas fa-check-circle';
        default: return 'fas fa-bell';
      }
    }
  }
}
</script>

<style scoped>
* {
  font-family: 'Inter', sans-serif;
}

.dashboard-layout {
  display: flex;
  min-height: 100vh;
  background-color: #f5f5f5;
  width: 100%;
}

.main-content {
  flex: 1;
  margin-left: 70px;
  transition: margin-left 0.3s;
  display: flex;
  flex-direction: column;
  width: calc(100% - 70px);
}

.main-content.expanded {
  margin-left: 240px;
  width: calc(100% - 240px);
}

.content-wrapper {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
}

.content-wrapper::-webkit-scrollbar {
  width: 8px;
}

.content-wrapper::-webkit-scrollbar-track {
  background: transparent;
}

.content-wrapper::-webkit-scrollbar-thumb {
  background: #DD385A;
  border-radius: 4px;
}

h1 {
  font-size: 1.75rem;
  font-weight: 500;
  color: #DD385A;
  margin-bottom: 1.5rem;
}

.filters {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  align-items: center;
}

.dropdown-container {
  position: relative;
}

.filter-dropdown {
  padding: 0.5rem 1rem;
  border: none;
  background: #ffebee;
  color: #DD385A;
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
}

.mark-all-btn {
  margin-left: auto;
  padding: 0.5rem 1rem;
  background-color: #DD385A;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.mark-all-btn:hover {
  background-color: #c62828;
}

.clear-all-btn {
  margin-left: 1rem;
  padding: 0.5rem 1rem;
  background-color: #DD385A;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.clear-all-btn:hover {
  background-color: #c62828;
}

.loading-spinner {
  text-align: center;
  padding: 2rem;
  color: #DD385A;
  font-size: 1rem;
}

.notifications-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.no-notifications {
  text-align: center;
  padding: 2rem;
  color: #DD385A;
  background: #ffebee;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
}

.notification-item {
  display: flex;
  padding: 1.25rem;
  border-radius: 8px;
  background-color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  cursor: pointer;
  position: relative;
}

.notification-item.unread {
  background-color: #ffebee;
}

.notification-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1rem;
  flex-shrink: 0;
}

.notification-icon.info {
  background-color: #e3f2fd;
  color: #1976d2;
}

.notification-icon.alert {
  background-color: #fff3e0;
  color: #e65100;
}

.notification-icon.success {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.notification-content {
  flex: 1;
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.notification-title {
  font-size: 1rem;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.notification-time {
  font-size: 0.75rem;
  color: #888;
}

.notification-message {
  font-size: 0.875rem;
  color: #555;
  margin: 0;
  line-height: 1.5;
}

.unread-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #DD385A;
  position: absolute;
  top: 1.25rem;
  right: 1.25rem;
}
</style>