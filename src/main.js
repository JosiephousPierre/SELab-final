// main.js
import { createApp } from 'vue';
import App from './App.vue';
import PrimeVue from 'primevue/config';
import router from './router';
import 'primevue/resources/themes/saga-blue/theme.css';
import 'primevue/resources/primevue.min.css';
import 'primeicons/primeicons.css';
import './assets/styles.css';
import './assets/styles/global.css';

// Add utility functions for token management
const tokenUtils = {
  // Get token from sessionStorage (preferred) or localStorage as fallback
  getToken() {
    return sessionStorage.getItem('token') || localStorage.getItem('token');
  },
  
  // Get user from sessionStorage (preferred) or localStorage as fallback
  getUser() {
    const userStr = sessionStorage.getItem('user') || localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },
  
  // Clear token and user data from both storage types
  clearSession() {
    sessionStorage.removeItem('token');
    sessionStorage.removeItem('user');
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  }
};

const app = createApp(App);
app.use(PrimeVue);
app.use(router);

// Make token utilities available globally
app.config.globalProperties.$tokenUtils = tokenUtils;
// Also expose as a global property for components to use
window.tokenUtils = tokenUtils;

app.mount('#app');