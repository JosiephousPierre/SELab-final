<template>
  <div class="sidebar" :class="{ expanded: isExpanded }" @mouseenter="expand" @mouseleave="collapse">
    <div class="logo-section">
      <img src="../assets/Logo-100px-white.png" alt="LabClass Logo" class="logo" />
      <span class="logo-text" v-show="isExpanded">LabClass</span>
    </div>

    <nav class="nav-links">
      <router-link to="/dashboard-acad-coor" class="nav-link" :class="{ active: $route.path === '/dashboard-acad-coor' }">
        <div class="icon-container">
          <i class="fas fa-home"></i>
        </div>
        <span v-show="isExpanded">Dashboard</span>
      </router-link>

      <router-link to="/notifications-acad-coor" class="nav-link" :class="{ active: $route.path === '/notifications-acad-coor' }">
        <div class="icon-container">
          <i class="fas fa-bell"></i>
          <span v-if="unreadCount > 0" class="notification-badge">{{ unreadCount }}</span>
        </div>
        <span v-show="isExpanded">Notifications</span>
      </router-link>

      <div class="nav-dropdown" :class="{ active: isScheduleDropdownOpen || isScheduleRouteActive }">
        <div class="nav-link" @click="toggleScheduleDropdown">
          <div class="icon-container">
            <i class="fas fa-calendar"></i>
          </div>
          <span v-show="isExpanded">Schedules</span>
          <i v-show="isExpanded" class="pi pi-angle-right dropdown-icon" :class="{ rotated: isScheduleDropdownOpen }"></i>
        </div>
        <div class="dropdown-menu" v-show="isExpanded && isScheduleDropdownOpen">
          <router-link to="/schedule-acad-coor" class="dropdown-item" :class="{ active: $route.path === '/schedule-acad-coor' }">
            <span>My Schedule</span>
          </router-link>
          <router-link to="/schedule-management" class="dropdown-item" :class="{ active: $route.path === '/schedule-management' }">
            <span>Scheduling Management</span>
          </router-link>
        </div>
      </div>

      <router-link to="/user-profile-acad-coor" class="nav-link" :class="{ active: $route.path === '/user-profile-acad-coor' }">
        <div class="icon-container">
          <i class="fas fa-user"></i>
        </div>
        <span v-show="isExpanded">Profile</span>
      </router-link>
    </nav>
  </div>
</template>

<script>
import NotificationService from '../services/NotificationService'

export default {
  name: 'DashBoardSidebarAcadCoor',
  data() {
    return {
      isExpanded: false,
      isScheduleDropdownOpen: false,
      unreadCount: 0
    }
  },
  computed: {
    isScheduleRouteActive() {
      return this.$route.path === '/schedule-acad-coor' || this.$route.path === '/schedule-management'
    }
  },
  methods: {
    expand() {
      this.isExpanded = true
    },
    collapse() {
      this.isExpanded = false
      this.isScheduleDropdownOpen = false
    },
    toggleScheduleDropdown() {
      if (this.isExpanded) {
        this.isScheduleDropdownOpen = !this.isScheduleDropdownOpen
      }
    },
    async fetchUnreadCount() {
      try {
        // Get unread notification count via direct database query for Academic Coordinator 
        // Use a custom method that we'll add to NotificationService
        this.unreadCount = await NotificationService.getAcadCoorUnreadCount();
        console.log('Academic Coordinator: Fetched unread notification count:', this.unreadCount);
      } catch (error) {
        console.error('Academic Coordinator: Error fetching unread notifications count:', error);
      }
    }
  },
  created() {
    this.fetchUnreadCount();

    // Set up interval to periodically check for new notifications (every 30 seconds)
    this.notificationTimer = setInterval(() => {
      this.fetchUnreadCount();
    }, 1000);
  },
  mounted() {
    // ... existing mounted code ...
  },
  beforeUnmount() {
    // Clear the interval when component is destroyed
    if (this.notificationTimer) {
      clearInterval(this.notificationTimer);
    }
  }
}
</script>

<style scoped>
.sidebar {
  background-color: #DD385A;
  height: 100vh;
  width: 70px;
  position: fixed;
  left: 0;
  top: 0;
  transition: all 0.3s ease;
  overflow: hidden;
  z-index: 1000;
  font-family: 'Inter', sans-serif;
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);
}

.sidebar.expanded {
  width: 250px;
}

.logo-section {
  padding: 1.5rem 1.25rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  margin-bottom: 1rem;
}

.logo {
  width: 32px;
  height: 32px;
  object-fit: contain;
}

.logo-text {
  color: white;
  font-size: 1.5rem;
  font-weight: 500;
  white-space: nowrap;
}

.nav-links {
  display: flex;
  flex-direction: column;
  padding: 0.5rem 0;
}

.nav-link {
  display: flex;
  align-items: center;
  padding: 0.875rem 1.25rem;
  color: rgba(255, 255, 255, 0.9);
  text-decoration: none;
  transition: all 0.2s ease;
  white-space: nowrap;
  font-size: 0.95rem;
  font-family: 'Inter', sans-serif;
  cursor: pointer;
  border-left: 3px solid transparent;
}

.nav-link:hover, .nav-link.active {
  background-color: rgba(255, 255, 255, 0.1);
  color: white;
  border-left-color: white;
}

.icon-container {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
}

.notification-badge {
  position: absolute;
  top: -7px;
  right: -7px;
  background-color: #478aff; /* Red notification badge */
  color: white;
  font-size: 0.6rem;
  font-weight: bold;
  min-width: 16px;
  height: 16px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.nav-link i {
  font-size: 1.1rem;
}

.nav-link span {
  margin-left: 1rem;
  font-weight: 400;
  flex: 1;
}

.dropdown-icon {
  font-size: 0.45rem;
  font-weight: 100;
  transition: transform 0.3s ease;
  opacity: 0.6;
  margin-left: 0.5rem;
  display: inline-block;
  color: rgba(255, 255, 255, 0.9);
  vertical-align: middle;
}

.dropdown-icon.rotated {
  transform: rotate(90deg);
}

.nav-dropdown {
  position: relative;
}

.nav-dropdown.active .nav-link {
  background-color: rgba(255, 255, 255, 0.1);
  border-left-color: white;
}

.dropdown-menu {
  background-color: rgba(0, 0, 0, 0.1);
  margin: 0;
}

.dropdown-item {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem 0.75rem calc(1.25rem + 24px + 1rem);
  color: rgba(255, 255, 255, 0.9);
  text-decoration: none;
  transition: all 0.2s ease;
  white-space: nowrap;
  font-size: 0.9rem;
  border-left: 3px solid transparent;
}

.dropdown-item:hover, .dropdown-item.active {
  background-color: rgba(255, 255, 255, 0.1);
  color: white;
  border-left-color: white;
}
</style>