// Login.vue
<template>
  <div class="login-container">
    <div class="login-card">
      <div class="logo-section">
        <img src="../assets/uic-logo-3.svg" alt="UIC Logo" class="logo" />
        <img src="../assets/CCS-logo.svg" alt="CCS Logo" class="logo" />
      </div>

      <router-link to="/" class="back-link">
        <i class="fas fa-chevron-left"></i>
      </router-link>

      <h1>Log In</h1>

      <div v-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </div>

      <div class="login-form" @keyup.enter="handleLogin">
        <div class="form-group">
          <label for="idOrEmail">ID or Email</label>
          <input 
            type="text" 
            id="idOrEmail" 
            placeholder="Enter your ID or Email"
            v-model="idOrEmail"
          >
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <input 
            type="password" 
            id="password" 
            placeholder="Enter your password"
            v-model="password"
          >
        </div>

        <router-link to="/forgot-password" class="forgot-password">Forgot your password?</router-link>

        <button class="login-button" @click="handleLogin" :disabled="isLoading">
          {{ isLoading ? 'Logging in...' : 'Log In' }}
        </button>

        <div class="divider">
          <span>or</span>
        </div>

        <button class="google-button">
          <img src="../assets/Google-logo.svg" alt="Google" class="google-icon">
          Sign in with Google
        </button>

        <p class="signup-link">
          Don't have an account yet? 
          <router-link to="/signup">Sign Up</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import { getDashboardPathForRole } from '../utils/roleUtils.js';

export default {
  name: 'Login',
  data() {
    return {
      idOrEmail: '',
      password: '',
      isLoading: false,
      errorMessage: null
    }
  },
  methods: {
    async handleLogin() {
      // Reset error message
      this.errorMessage = null;
      
      // Simple validation
      if (!this.idOrEmail || !this.password) {
        this.errorMessage = 'Please enter both ID/Email and Password';
        return;
      }

      this.isLoading = true;
      
      try {
        // Check for admin fallback first
        if ((this.idOrEmail === 'admin' || this.idOrEmail === 'admin@uic.edu') && 
             this.password === 'admin123') {
          
          // Store admin user with mock token - use sessionStorage for tab-specific sessions
          // Encode the password in the token for future validation
          const encodedPassword = btoa(this.password);
          const mockToken = "admin_fallback_token_" + encodedPassword;
          
          // Record current login date/time
          const currentLoginTime = new Date().toISOString();
          
          const adminUser = {
            id: 'admin',
            full_name: 'System Administrator',
            email: 'admin@uic.edu',
            role: 'System Administrator',
            is_approved: true,
            is_active: true,
            last_login: currentLoginTime,
            date_created: localStorage.getItem('adminCreated') || currentLoginTime
          };
          
          sessionStorage.setItem('token', mockToken);
          sessionStorage.setItem('user', JSON.stringify(adminUser));
          
          // Also maintain localStorage for persistent login across browser restarts
          localStorage.setItem('token', mockToken);
          localStorage.setItem('adminCreated', localStorage.getItem('adminCreated') || currentLoginTime);
          localStorage.setItem('lastLogin', JSON.stringify({
            id: 'admin',
            token: mockToken,
            time: currentLoginTime
          }));
          
          console.log('Admin login successful (fallback method)');
          
          // Redirect to System Administrator dashboard
          this.$router.push('/dashboard-sysad');
          return;
        }

        // For non-admin users, check localStorage approved users first
        const approvedUsersJSON = localStorage.getItem('approvedUsers');
        if (approvedUsersJSON) {
          try {
            const approvedUsers = JSON.parse(approvedUsersJSON);
            // Find user by ID or email
            const user = approvedUsers.find(u => 
              u.id === this.idOrEmail || u.email === this.idOrEmail
            );
            
            if (user) {
              console.log('Found user in approved users:', user);
              
              // Check if user is active
              if (!user.is_active) {
                throw new Error('Your account has been deactivated. Please contact the administrator.');
              }
              
              // Check approval status based on role requirements
              if (user.requires_approval && !user.is_approved) {
                throw new Error('Your account is pending approval by an administrator');
              }

              // Check if user has a stored password
              if (user.password) {
                // Validate password
                const encodedPassword = btoa(this.password);
                if (encodedPassword !== user.password) {
                  throw new Error('Invalid password');
                }
              }
              
              // Create a token with encoded password
              const encodedPassword = btoa(this.password);
              const mockToken = "user_fallback_token_" + encodedPassword;
              
              // Record current login date/time
              const currentLoginTime = new Date().toISOString();
              
              // Update user data with last login
              user.last_login = currentLoginTime;
              if (!user.date_created) {
                user.date_created = currentLoginTime;
              }
              
              // Store in both sessionStorage and localStorage
              sessionStorage.setItem('token', mockToken);
              localStorage.setItem('token', mockToken);
              
              // Store the password in user object for future logins
              user.password = encodedPassword;
              
              // Update user in approvedUsers
              const updatedApprovedUsers = approvedUsers.map(u => 
                (u.id === user.id || u.email === user.email) ? user : u
              );
              localStorage.setItem('approvedUsers', JSON.stringify(updatedApprovedUsers));
              
              // Save user data
              sessionStorage.setItem('user', JSON.stringify(user));
              localStorage.setItem('user', JSON.stringify(user));
              
              // Track last login
              localStorage.setItem('lastLogin', JSON.stringify({
                id: user.id,
                token: mockToken,
                time: currentLoginTime
              }));
              
              console.log(`User ${user.full_name} logged in with role: ${user.role}`);
              
              // Redirect based on user role
              this.redirectBasedOnRole(user.role);
              return;
            }
          } catch (error) {
            console.error('Error in localStorage user validation:', error);
            this.errorMessage = error.message;
            this.isLoading = false;
            return;
          }
        }
        
        // Try API login with a catch for network errors
        try {
          console.log("Attempting login via API with:", { idOrEmail: this.idOrEmail });
          
          // Attempt to log in via the API
          const response = await fetch('http://localhost:8000/api/login', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              id_or_email: this.idOrEmail,
              password: this.password
            }),
            // Set a reasonable timeout
            signal: AbortSignal.timeout(5000)
          });
          
          console.log("API response status:", response.status);
          
          if (!response.ok) {
            const data = await response.json();
            console.error("API login error:", data);
            throw new Error(data.detail || 'Login failed');
          }
          
          const data = await response.json();
          console.log("API login success, user data:", { 
            id: data.user_id, 
            name: data.full_name, 
            role: data.role
          });
          
          // Record current login date/time
          const currentLoginTime = new Date().toISOString();
          
          // Create user object from API response
          const userData = {
            id: data.user_id,
            full_name: data.full_name,
            email: data.email,
            role: data.role,
            is_approved: data.is_approved,
            requires_approval: data.requires_approval,
            is_active: data.is_active,
            last_login: currentLoginTime
          };
          
          // Store token and user data in sessionStorage for tab-specific session
          sessionStorage.setItem('token', data.access_token);
          sessionStorage.setItem('user', JSON.stringify(userData));
          
          // Also store in localStorage for persistence
          localStorage.setItem('token', data.access_token);
          localStorage.setItem('user', JSON.stringify(userData));
          
          // Track last login
          localStorage.setItem('lastLogin', JSON.stringify({
            id: userData.id,
            token: data.access_token,
            time: currentLoginTime
          }));
          
          console.log(`User ${userData.full_name} logged in with role: ${userData.role}`);
          
          // Redirect based on user role
          this.redirectBasedOnRole(userData.role);
        } catch (error) {
          // Handle network errors or timeouts differently
          if (error.name === 'AbortError' || error.name === 'TypeError') {
            console.warn('API is unavailable, checking for local credentials');
            
            // Check if user exists in local storage
            if (approvedUsersJSON) {
              // Try to find credentials that match
              const approvedUsers = JSON.parse(approvedUsersJSON);
              const user = approvedUsers.find(u => 
                (u.id === this.idOrEmail || u.email === this.idOrEmail) && 
                btoa(this.password) === u.password
              );
              
              if (user) {
                if (!user.is_active) {
                  this.errorMessage = 'Your account has been deactivated. Please contact the administrator.';
                  this.isLoading = false;
                  return;
                }
                
                if (user.is_approved) {
                  // Create a token with encoded password
                  const encodedPassword = btoa(this.password);
                  const mockToken = "user_fallback_token_" + encodedPassword;
                  
                  // Record current login date/time
                  const currentLoginTime = new Date().toISOString();
                  
                  // Update user data with last login
                  user.last_login = currentLoginTime;
                  
                  // Store in both sessionStorage and localStorage
                  sessionStorage.setItem('token', mockToken);
                  localStorage.setItem('token', mockToken);
                  
                  // Update user in approvedUsers
                  const updatedApprovedUsers = approvedUsers.map(u => 
                    (u.id === user.id || u.email === user.email) ? user : u
                  );
                  localStorage.setItem('approvedUsers', JSON.stringify(updatedApprovedUsers));
                  
                  // Save user data
                  sessionStorage.setItem('user', JSON.stringify(user));
                  localStorage.setItem('user', JSON.stringify(user));
                  
                  console.log(`Fallback login: User ${user.full_name} logged in with role: ${user.role}`);
                  
                  // Redirect based on user role
                  this.redirectBasedOnRole(user.role);
                  return;
                } else {
                  this.errorMessage = 'Your account is pending approval by an administrator';
                }
              } else {
                this.errorMessage = 'Invalid credentials';
              }
            } else {
              this.errorMessage = 'Cannot connect to server and no local credentials found';
            }
          } else {
            // Other errors (like incorrect credentials)
            this.errorMessage = error.message || 'Login failed';
          }
        }
      } catch (error) {
        console.error('Error during login:', error);
        this.errorMessage = error.message;
      } finally {
        this.isLoading = false;
      }
    },
    
    // Helper method to redirect based on role
    redirectBasedOnRole(role) {
      console.log(`Redirecting user with role: ${role}`);
      const dashboardPath = getDashboardPathForRole(role);
      this.$router.push(dashboardPath);
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 93vh;
  background-color: #f5f5f5;
  padding: 1rem;
}

.login-card {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 360px;
  position: relative;
}

.logo-section {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.logo {
  height: 50px;
  width: auto;
}

.back-link {
  position: absolute;
  top: 1.5rem;
  left: 1.5rem;
  color: #666;
  text-decoration: none;
  font-size: 1.2rem;
}

h1 {
  text-align: center;
  color: #E91E63;
  font-size: 1.8rem;
  margin-bottom: 1.5rem;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

label {
  color: #666;
  font-size: 0.9rem;
}

input {
  padding: 0.7rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.9rem;
  transition: border-color 0.3s ease;
}

input:focus {
  outline: none;
  border-color: #E91E63;
}

.forgot-password {
  color: #E91E63;
  text-decoration: none;
  font-size: 0.9rem;
  align-self: flex-end;
  margin-top: -0.5rem;
}

.forgot-password:hover {
  text-decoration: underline;
}

.login-button {
  background-color: #DD385A;
  color: white;
  border: none;
  padding: 0.75rem;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  width: 100%;
  font-weight: 500;
  transition: background-color 0.2s;
}

.login-button:hover {
  background-color: #c4314f;
}

.divider {
  display: flex;
  align-items: center;
  text-align: center;
  margin: 0.5rem 0;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  border-bottom: 1px solid #ddd;
}

.divider span {
  padding: 0 10px;
  color: #666;
  font-size: 0.9rem;
}

.google-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.8rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  background: white;
  color: #666;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.google-button:hover {
  background-color: #f5f5f5;
}

.google-icon {
  height: 18px;
  width: auto;
}

.signup-link {
  text-align: center;
  color: #DD385A;
  text-decoration: none;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

.signup-link a {
  color: #DD385A;
  text-decoration: none;
  font-weight: 500;
}

.signup-link a:hover {
  text-decoration: underline;
}

.error-message {
  color: #e74c3c;
  background-color: #fadbd8;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 15px;
  font-size: 0.9rem;
  text-align: center;
}

.login-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}
</style>
