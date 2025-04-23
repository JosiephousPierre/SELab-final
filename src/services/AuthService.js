import axios from 'axios';
import router from '../router';

const API_URL = 'http://localhost:8000/api';

class AuthService {
  // Login user
  async login(credentials) {
    try {
      const response = await axios.post(`${API_URL}/login`, credentials);
      if (response.data.access_token) {
        // Store in both storage options for redundancy
        sessionStorage.setItem('token', response.data.access_token);
        sessionStorage.setItem('user', JSON.stringify({
          id: response.data.user_id,
          full_name: response.data.full_name,
          email: response.data.email,
          role: response.data.role,
          is_approved: response.data.is_approved,
          requires_approval: response.data.requires_approval,
          is_active: response.data.is_active,
          last_auth_check: new Date().toISOString()
        }));
        
        // Also store in localStorage as a fallback
        localStorage.setItem('token', response.data.access_token);
        localStorage.setItem('user', JSON.stringify({
          id: response.data.user_id,
          full_name: response.data.full_name,
          email: response.data.email,
          role: response.data.role,
          is_approved: response.data.is_approved,
          requires_approval: response.data.requires_approval,
          is_active: response.data.is_active,
          last_auth_check: new Date().toISOString()
        }));
      }
      return response.data;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }

  // Logout user
  logout() {
    // Clear both storage options
    sessionStorage.removeItem('token');
    sessionStorage.removeItem('user');
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    
    // Redirect to login page
    router.push('/login');
  }

  // Force logout specific user (called by admin actions)
  async forceLogout(userId) {
    try {
      const token = sessionStorage.getItem('token') || localStorage.getItem('token');
      const response = await axios.put(
        `${API_URL}/users/${userId}/force-logout`, 
        {}, 
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );
      return response.data;
    } catch (error) {
      console.error('Force logout error:', error);
      throw error;
    }
  }

  // Check if current user has been forced to logout
  async checkForcedLogout() {
    const userStr = sessionStorage.getItem('user') || localStorage.getItem('user');
    const token = sessionStorage.getItem('token') || localStorage.getItem('token');
    
    if (!userStr || !token) {
      console.log('No authenticated user found');
      return false;
    }
    
    try {
      const userData = JSON.parse(userStr);
      const userId = userData.id;
      const lastAuthCheck = userData.last_auth_check || null;
      const currentRole = userData.role; // Store current role before check
      
      console.log(`Checking forced logout for user ${userId} (${currentRole})`);
      
      const response = await axios.get(
        `${API_URL}/users/${userId}/check-forced-logout`, 
        {
          headers: { 'Authorization': `Bearer ${token}` },
          params: { last_auth_time: lastAuthCheck }
        }
      );
      
      // Update the last auth check time
      const currentTime = new Date().toISOString();
      userData.last_auth_check = currentTime;
      
      // Update storage
      if (sessionStorage.getItem('user')) {
        sessionStorage.setItem('user', JSON.stringify(userData));
      }
      if (localStorage.getItem('user')) {
        localStorage.setItem('user', JSON.stringify(userData));
      }
      
      // If should_logout is true, the user has been forced to logout
      if (response.data.should_logout) {
        console.log(`FORCE LOGOUT DETECTED: User ${userId} has been forced to logout at ${response.data.timestamp}`);
        
        // Get user info from response
        const { user_info } = response.data;
        const timestamp = new Date(response.data.timestamp);
        const formattedTime = timestamp.toLocaleTimeString();
        
        // Determine what changed
        let changeDescription = '';
        if (user_info && currentRole !== user_info.role) {
          changeDescription = `Your role has been changed from "${currentRole}" to "${user_info.role}".`;
        } else if (user_info && !user_info.is_active) {
          changeDescription = 'Your account has been deactivated.';
        } else {
          changeDescription = 'Your account settings have been modified.';
        }
        
        // Create a clear message for the user with informative title
        const title = 'Account Modified by Administrator';
        let message = 'Your account has been modified by an administrator.\n\n';
        message += changeDescription + '\n\n';
        message += 'You will be logged out now. Please log in again to continue with your updated access level.';
        
        // Show alert with the message
        // Use a more prominent alert
        window.alert(message);
        
        // Log the user out after they acknowledge the alert
        console.log('User acknowledged the alert, logging out...');
        this.logout();
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('Error checking forced logout:', error);
      // Don't logout the user on error checking - only on positive confirmation
      return false;
    }
  }

  // Get current authenticated user
  getCurrentUser() {
    const userStr = sessionStorage.getItem('user') || localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  }

  // Check if user is authenticated
  isAuthenticated() {
    return !!this.getCurrentUser() && !!(sessionStorage.getItem('token') || localStorage.getItem('token'));
  }
}

export default new AuthService(); 