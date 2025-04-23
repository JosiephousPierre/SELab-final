// App.vue
<template>
  <div class="app-container">
    <template v-if="!isDashboardRoute">
      <Sidebar />
      <div class="main-content standard-page">
        <Topbar />
        <router-view />
      </div>
    </template>
    <template v-else>
      <div class="dashboard-layout">
        <router-view />
      </div>
    </template>
  </div>
</template>

<script>
import Sidebar from './components/Sidebar.vue';
import Topbar from './components/Topbar.vue';
import AuthService from './services/AuthService';

export default {
  name: 'App',
  components: { Sidebar, Topbar },
  data() {
    return {
      forcedLogoutInterval: null
    };
  },
  computed: {
    isDashboardRoute() {
      return this.$route.path.startsWith('/dashboard') ||
             this.$route.path.startsWith('/notifications') ||
             this.$route.path.startsWith('/schedule') ||
             this.$route.path.startsWith('/all-schedules') ||
             this.$route.path.startsWith('/user-management') ||
             this.$route.path.startsWith('/account-management') ||
             this.$route.path.startsWith('/user-profile') ||
             this.$route.path.startsWith('/users');
    }
  },
  mounted() {
    // Start checking for forced logout every 30 seconds
    this.startForcedLogoutCheck();
  },
  beforeUnmount() {
    // Clear the interval when component is destroyed
    this.clearForcedLogoutCheck();
  },
  methods: {
    startForcedLogoutCheck() {
      // Clear any existing interval
      this.clearForcedLogoutCheck();
      
      // First, do an immediate check when the application starts
      if (AuthService.isAuthenticated()) {
        console.log('Initial forced logout check on application start');
        AuthService.checkForcedLogout();
      }
      
      // Set a new interval to check VERY frequently at first (2 seconds) 
      // to ensure we catch any modifications quickly
      this.forcedLogoutInterval = setInterval(async () => {
        // Only check if user is authenticated
        if (AuthService.isAuthenticated()) {
          console.log('Checking for forced logout (very frequent check)');
          await AuthService.checkForcedLogout();
        }
      }, 2000); // 2 seconds
      
      // After 30 seconds, switch to less frequent checks
      setTimeout(() => {
        this.clearForcedLogoutCheck();
        
        // Still keep reasonably frequent checks to ensure users don't miss notifications
        this.forcedLogoutInterval = setInterval(async () => {
          // Only check if user is authenticated
          if (AuthService.isAuthenticated()) {
            console.log('Checking for forced logout (standard interval)');
            await AuthService.checkForcedLogout();
          }
        }, 10000); // 10 seconds
      }, 30000); // After 30 seconds
    },
    clearForcedLogoutCheck() {
      if (this.forcedLogoutInterval) {
        clearInterval(this.forcedLogoutInterval);
        this.forcedLogoutInterval = null;
      }
    }
  }
};
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: 'Inter', sans-serif;
}

html, body {
  height: 100%;
  width: 100%;
  overflow: hidden;
  background-color: #f5f5f5;
}

.app-container {
  height: 100vh;
  width: 100vw;
  display: flex;
  overflow: hidden;
  background-color: #f5f5f5;
  position: relative;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0; /* Prevent flex item from overflowing */
  background-color: white;
}

.main-content.standard-page {
  width: calc(100vw - 80px); /* Full width minus sidebar */
  margin-left: 80px; /* Match the sidebar width */
}

/* Dashboard routes specific styles */
.dashboard-layout {
  display: flex;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  background-color: #f5f5f5;
}

.dashboard-layout .main-content {
  flex: 1;
  margin-left: 70px;
  width: calc(100vw - 70px);
  min-width: 0;
}
</style>