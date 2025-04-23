<template>
  <div class="topbar">
    <div class="left-section">
      <div class="logos">
        <img src="../assets/uic-logo-3.svg" alt="UIC Logo" class="logo" />
        <img src="../assets/CCS-logo.svg" alt="CCS Logo" class="logo" />
      </div>
    </div>
    <div class="right-section">
      <div class="user-menu" @click="toggleDropdown">
        <i class="fas fa-user user-icon"></i>
        <span class="username">{{ userName }}</span>
        <div class="dropdown-menu" v-show="showDropdown">
          <button class="menu-item" @click="goToProfile">
            <i class="fas fa-user-circle"></i>
            Profile
          </button>
          <button @click="logout" class="menu-item">
            <i class="fas fa-sign-out-alt"></i>
            Log Out
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DashBoardTopbar',
  data() {
    return {
      showDropdown: false,
      userName: 'User'
    }
  },
  methods: {
    checkAuth() {
      // Check if user is authenticated
      const token = sessionStorage.getItem('token') || localStorage.getItem('token');
      const userStr = sessionStorage.getItem('user') || localStorage.getItem('user');
      
      if (!token || !userStr) {
        console.warn('No authentication data found in topbar - will redirect to login');
        this.$router.push('/login');
        return false;
      }
      
      // Always update the user name when we check auth
      this.updateUserName();
      return true;
    },
    toggleDropdown() {
      this.showDropdown = !this.showDropdown
    },
    logout() {
      // Clear both session storage and local storage
      sessionStorage.removeItem('token');
      sessionStorage.removeItem('user');
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      
      // Redirect to login page
      this.$router.push('/login');
    },
    goToProfile() {
      // Get user data
      const userStr = sessionStorage.getItem('user') || localStorage.getItem('user');
      const user = userStr ? JSON.parse(userStr) : {};
      
      // Determine which profile page to go to based on role
      let profileRoute = '/user-profile-viewer'; // Default
      
      switch (user.role) {
        case 'System Administrator':
          profileRoute = '/user-profile-sysad';
          break;
        case 'Academic Coordinator':
          profileRoute = '/user-profile-acad-coor';
          break;
        case 'Lab InCharge':
          profileRoute = '/user-profile-lab';
          break;
        case 'Dean':
          profileRoute = '/user-profile-dean';
          break;
        default:
          profileRoute = '/user-profile-viewer';
          break;
      }

      // Only navigate if we're not already on the profile page
      if (this.$route.path !== profileRoute) {
        this.$router.push(profileRoute);
      }
      
      // Close the dropdown menu
      this.showDropdown = false;
    },
    updateUserName() {
      // Get user data from session or local storage
      const userStr = sessionStorage.getItem('user') || localStorage.getItem('user');
      const user = userStr ? JSON.parse(userStr) : {};
      
      // Set user name if available
      if (user.full_name) {
        this.userName = user.full_name;
      }
    }
  },
  created() {
    this.checkAuth();
  },
  mounted() {
    // Check authentication (which also updates username)
    this.checkAuth();
    
    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
      if (!this.$el.contains(e.target)) {
        this.showDropdown = false;
      }
    });
  }
}
</script>

<style scoped>
.topbar {
  background-color: white;
  height: 60px;
  padding: 0 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
}

.left-section {
  display: flex;
  align-items: center;
}

.logos {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.logo {
  height: 42px;
  width: auto;
}

.right-section {
  display: flex;
  align-items: center;
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  position: relative;
  padding: 0.5rem;
}

.user-icon {
  color: #DD385A;
  font-size: 1.1rem;
}

.username {
  color: #DD385A;
  font-size: 0.9rem;
  font-weight: 500;
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 0.5rem);
  right: 0;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 0.5rem;
  min-width: 150px;
  z-index: 1000;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 1rem;
  width: 100%;
  border: none;
  background: none;
  cursor: pointer;
  color: #DD385A;
  font-size: 0.9rem;
  text-align: left;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.menu-item:hover {
  background-color: rgba(221, 56, 90, 0.1);
}

.menu-item i {
  font-size: 1rem;
  color: #DD385A;
  margin-right: 8px;
}

.user-menu:hover {
  background-color: rgba(221, 56, 90, 0.1);
}
</style>