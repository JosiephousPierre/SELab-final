<template>
    <div class="dashboard-layout">
      <DashBoardSideBarLab />
      <div class="main-content">
        <DashBoardTopbar />
        <div class="dashboard-content">
          <div v-if="isLoading" class="loading-indicator">
            Loading profile...
          </div>
          
          <div v-else-if="errorMessage" class="error-message">
            {{ errorMessage }}
          </div>
          
          <div v-else class="profile-container">
            <div class="profile-header">
              <div class="profile-avatar">
                <i class="fas fa-user"></i>
              </div>
              <div class="profile-info">
                <h2>{{ userData.full_name }}</h2>
                <span class="role-badge lab-incharge">{{ userData.role }}</span>
                <p class="email">{{ userData.email }}</p>
              </div>
            </div>
  
            <div class="profile-details">
              <div class="detail-section">
                <h3>Personal Information</h3>
                <div class="detail-grid">
                  <div class="detail-item">
                    <label>ID Number</label>
                    <p>{{ userData.id }}</p>
                  </div>
                  <div class="detail-item">
                    <label>Full Name</label>
                    <p>{{ userData.full_name }}</p>
                  </div>
                  <div class="detail-item">
                    <label>Email</label>
                    <p>{{ userData.email }}</p>
                  </div>
                  <div class="detail-item">
                    <label>Role</label>
                    <p>{{ userData.role }}</p>
                  </div>
                  <div class="detail-item">
                    <label>Permission Level</label>
                    <p>{{ getPermissionsByRole(userData.role) }}</p>
                  </div>
                  <div class="detail-item">
                    <label>Account Created</label>
                    <p>{{ formatDate(userData.date_created) }}</p>
                  </div>
                  <div class="detail-item">
                    <label>Last Login</label>
                    <p>{{ userData.last_login ? formatDate(userData.last_login) : 'N/A' }}</p>
                  </div>
                </div>
              </div>
  
              <div class="detail-section">
                <h3>Account Settings</h3>
                <div class="settings-buttons">
                  <button class="edit-button" @click="showEditModal = true">
                    <i class="fas fa-edit"></i>
                    Edit Profile
                  </button>
                  <button class="password-button" @click="showPasswordModal = true">
                    <i class="fas fa-key"></i>
                    Change Password
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Edit Profile Modal -->
          <div v-if="showEditModal" class="modal">
            <div class="modal-content">
              <div class="modal-header">
                <h2>Edit Profile</h2>
                <button class="close-button" @click="showEditModal = false">
                  <i class="fas fa-times"></i>
                </button>
              </div>
              <div class="modal-body">
                <div class="form-group">
                  <label>Full Name</label>
                  <input type="text" v-model="editForm.full_name" placeholder="Enter your full name">
                </div>
                <div class="form-group">
                  <label>Email</label>
                  <input type="email" v-model="editForm.email" placeholder="Enter your email">
                </div>
                <button class="confirm-button" @click="updateProfile">Save Changes</button>
              </div>
            </div>
          </div>
          
          <!-- Change Password Modal -->
          <div v-if="showPasswordModal" class="modal">
            <div class="modal-content">
              <div class="modal-header">
                <h2>Change Password</h2>
                <button class="close-button" @click="showPasswordModal = false">
                  <i class="fas fa-times"></i>
                </button>
              </div>
              <div class="modal-body">
                <div class="form-group">
                  <label>Current Password</label>
                  <input type="password" v-model="passwordForm.currentPassword" placeholder="Enter current password">
                </div>
                <div class="form-group">
                  <label>New Password</label>
                  <input type="password" v-model="passwordForm.newPassword" placeholder="Enter new password">
                </div>
                <div class="form-group">
                  <label>Confirm New Password</label>
                  <input type="password" v-model="passwordForm.confirmPassword" placeholder="Confirm new password">
                </div>
                <button class="confirm-button" @click="updatePassword">Change Password</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import DashBoardSideBarLab from '../../components/DashBoardSidebarLab.vue'
  import DashBoardTopbar from '../../components/DashBoardTopbar.vue'
  
  export default {
    name: 'UserProfileLab',
    components: {
      DashBoardSideBarLab,
      DashBoardTopbar
    },
    data() {
      return {
        userData: {
          id: '',
          full_name: '',
          email: '',
          role: '',
          date_created: '',
          last_login: null
        },
        isLoading: true,
        errorMessage: null,
        showEditModal: false,
        showPasswordModal: false,
        editForm: {
          full_name: '',
          email: ''
        },
        passwordForm: {
          currentPassword: '',
          newPassword: '',
          confirmPassword: ''
        }
      }
    },
    created() {
      this.fetchUserProfile();
    },
    methods: {
      async fetchUserProfile() {
        this.isLoading = true;
        this.errorMessage = null;
        
        try {
          // Get user data from sessionStorage first, then localStorage
          const userDataStr = sessionStorage.getItem('user') || localStorage.getItem('user') || '{}';
          const userData = JSON.parse(userDataStr);
          const token = sessionStorage.getItem('token') || localStorage.getItem('token');
          
          if (!userData.id || !token) {
            this.errorMessage = 'User information not found. Please log in again.';
            this.$router.push('/login');
            return;
          }
          
          // Get the most recent login time from lastLogin in localStorage if available
          let lastLoginTime = null;
          try {
            const lastLoginData = JSON.parse(localStorage.getItem('lastLogin') || '{}');
            if (lastLoginData && lastLoginData.time) {
              lastLoginTime = lastLoginData.time;
            }
          } catch (e) {
            console.error('Error parsing last login data:', e);
          }
          
          // Check if this is an admin fallback account or similar non-API user
          if (token.startsWith('fallback_token_') || token.startsWith('admin_fallback_token_') || token.startsWith('user_fallback_token_')) {
            // Use the storage data directly instead of making API call
            console.log('Using fallback profile data');
            
            // Get current timestamp for date created if not present
            const now = new Date().toISOString();
            
            this.userData = {
              id: userData.id,
              full_name: userData.full_name,
              email: userData.email,
              role: userData.role,
              is_approved: userData.is_approved,
              date_created: userData.date_created || now,
              last_login: lastLoginTime || userData.last_login || now,
              is_active: true
            };
            
            // Initialize edit form with current values
            this.editForm.full_name = userData.full_name;
            this.editForm.email = userData.email;
            
            this.isLoading = false;
            return;
          }
          
          // Fetch user profile from API
          const response = await fetch(`http://localhost:8000/api/users/${userData.id}/profile`, {
            method: 'GET',
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });
          
          if (!response.ok) {
            const data = await response.json();
            throw new Error(data.detail || 'Failed to fetch user profile');
          }
          
          const data = await response.json();
          
          // Merge API data with localStorage last login if available
          this.userData = {
            ...data,
            last_login: lastLoginTime || data.last_login
          };
          
          // Initialize edit form with current values
          this.editForm.full_name = data.full_name;
          this.editForm.email = data.email;
          
        } catch (error) {
          console.error('Error fetching user profile:', error);
          this.errorMessage = error.message;
        } finally {
          this.isLoading = false;
        }
      },
      
      async updateProfile() {
        try {
          const token = sessionStorage.getItem('token') || localStorage.getItem('token');
          
          if (!token) {
            this.errorMessage = 'Authentication token not found. Please log in again.';
            this.$router.push('/login');
            return;
          }
          
          // Check if this is a fallback account (mock token)
          if (token.startsWith('admin_fallback_token_') || token.startsWith('user_fallback_token_')) {
            // Update both sessionStorage and localStorage if they exist
            const userData = {
              ...JSON.parse(sessionStorage.getItem('user') || localStorage.getItem('user') || '{}'),
              full_name: this.editForm.full_name,
              email: this.editForm.email
            };
            
            if (sessionStorage.getItem('user')) {
              sessionStorage.setItem('user', JSON.stringify(userData));
            }
            
            if (localStorage.getItem('user')) {
              localStorage.setItem('user', JSON.stringify(userData));
            }
            
            // Update the approvedUsers list in localStorage if it exists
            const approvedUsersJSON = localStorage.getItem('approvedUsers');
            if (approvedUsersJSON) {
              try {
                const approvedUsers = JSON.parse(approvedUsersJSON);
                // Find and update the user in the approvedUsers list
                const updatedApprovedUsers = approvedUsers.map(u => {
                  if (u.id === userData.id || u.email === userData.email) {
                    return { ...u, full_name: this.editForm.full_name, email: this.editForm.email };
                  }
                  return u;
                });
                localStorage.setItem('approvedUsers', JSON.stringify(updatedApprovedUsers));
              } catch (error) {
                console.error('Error updating approvedUsers list:', error);
              }
            }
            
            // Update local userData
            this.userData = {
              ...this.userData,
              full_name: this.editForm.full_name,
              email: this.editForm.email
            };
            
            // Close modal and show success message
            this.showEditModal = false;
            alert('Profile updated successfully');
            return;
          }
          
          // For normal users, try to update via API first
          try {
            const response = await fetch(`http://localhost:8000/api/users/${this.userData.id}/profile`, {
              method: 'PUT',
              headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
              },
              body: JSON.stringify({
                full_name: this.editForm.full_name,
                email: this.editForm.email
              })
            });
            
            if (!response.ok) {
              const data = await response.json();
              throw new Error(data.detail || 'Failed to update profile');
            }
            
            const updatedUser = await response.json();
            this.userData = updatedUser;
            
            // Update both sessionStorage and localStorage if they exist
            if (sessionStorage.getItem('user')) {
              const storedSessionUser = JSON.parse(sessionStorage.getItem('user'));
              storedSessionUser.full_name = updatedUser.full_name;
              storedSessionUser.email = updatedUser.email;
              sessionStorage.setItem('user', JSON.stringify(storedSessionUser));
            }
            
            if (localStorage.getItem('user')) {
              const storedLocalUser = JSON.parse(localStorage.getItem('user'));
              storedLocalUser.full_name = updatedUser.full_name;
              storedLocalUser.email = updatedUser.email;
              localStorage.setItem('user', JSON.stringify(storedLocalUser));
            }
            
            // Update the approvedUsers list in localStorage if it exists
            const approvedUsersJSON = localStorage.getItem('approvedUsers');
            if (approvedUsersJSON) {
              try {
                const approvedUsers = JSON.parse(approvedUsersJSON);
                // Find and update the user in the approvedUsers list
                const updatedApprovedUsers = approvedUsers.map(u => {
                  if (u.id === this.userData.id || u.email === u.email) {
                    return { ...u, full_name: updatedUser.full_name, email: updatedUser.email };
                  }
                  return u;
                });
                localStorage.setItem('approvedUsers', JSON.stringify(updatedApprovedUsers));
              } catch (error) {
                console.error('Error updating approvedUsers list:', error);
              }
            }
          } catch (error) {
            console.warn('API update failed, falling back to direct storage update:', error);
            
            // Fallback: update storage directly
            const userData = {
              ...JSON.parse(sessionStorage.getItem('user') || localStorage.getItem('user') || '{}'),
              full_name: this.editForm.full_name,
              email: this.editForm.email
            };
            
            if (sessionStorage.getItem('user')) {
              sessionStorage.setItem('user', JSON.stringify(userData));
            }
            
            if (localStorage.getItem('user')) {
              localStorage.setItem('user', JSON.stringify(userData));
            }
            
            // Update the approvedUsers list in localStorage if it exists
            const approvedUsersJSON = localStorage.getItem('approvedUsers');
            if (approvedUsersJSON) {
              try {
                const approvedUsers = JSON.parse(approvedUsersJSON);
                // Find and update the user in the approvedUsers list
                const updatedApprovedUsers = approvedUsers.map(u => {
                  if (u.id === userData.id || u.email === userData.email) {
                    return { ...u, full_name: this.editForm.full_name, email: this.editForm.email };
                  }
                  return u;
                });
                localStorage.setItem('approvedUsers', JSON.stringify(updatedApprovedUsers));
              } catch (error) {
                console.error('Error updating approvedUsers list:', error);
              }
            }
            
            // Update local userData
            this.userData = {
              ...this.userData,
              full_name: this.editForm.full_name,
              email: this.editForm.email
            };
          }
          
          // Close modal and show success message
          this.showEditModal = false;
          alert('Profile updated successfully');
        } catch (error) {
          console.error('Error updating profile:', error);
          alert(`Error: ${error.message}`);
        }
      },
      
      async updatePassword() {
        // Password validation
        if (!this.passwordForm.currentPassword) {
          alert('Please enter your current password');
          return;
        }
        
        if (!this.passwordForm.newPassword) {
          alert('Please enter a new password');
          return;
        }
        
        if (this.passwordForm.newPassword !== this.passwordForm.confirmPassword) {
          alert('New passwords do not match');
          return;
        }
        
        try {
          const token = sessionStorage.getItem('token') || localStorage.getItem('token');
          
          if (!token) {
            this.errorMessage = 'Authentication token not found. Please log in again.';
            this.$router.push('/login');
            return;
          }
          
          // Handle fallback token case
          if (token.startsWith('admin_fallback_token_') || token.startsWith('user_fallback_token_')) {
            // Verify the current password is correct by checking against the token
            // Extract the encoded password part from the token
            const parts = token.split('_fallback_token_');
            if (parts.length !== 2) {
              alert('Invalid token format. Please log in again.');
              this.$router.push('/login');
              return;
            }
            
            const encodedCurrentPassword = btoa(this.passwordForm.currentPassword);
            const storedEncodedPassword = parts[1];
            
            // Verify the current password matches the stored password
            if (encodedCurrentPassword !== storedEncodedPassword) {
              alert('Current password is incorrect');
              return;
            }
            
            // If current password is correct, proceed with the change
            // Hash the new password (simple mock for demo purposes)
            const hashedPassword = btoa(this.passwordForm.newPassword); // Not secure, just for demo
            
            // Create a new token with the updated password hash
            const userType = token.includes('admin') ? 'admin' : 'user';
            const newToken = `${userType}_fallback_token_${hashedPassword}`;
            
            // Update token in storage
            if (sessionStorage.getItem('token')) {
              sessionStorage.setItem('token', newToken);
            }
            
            if (localStorage.getItem('token')) {
              localStorage.setItem('token', newToken);
            }
            
            // Update user password in user object
            const userData = JSON.parse(sessionStorage.getItem('user') || localStorage.getItem('user') || '{}');
            if (userData && userData.id) {
              // Update the password in the user data
              userData.password = hashedPassword;
              
              // Save back to storage
              if (sessionStorage.getItem('user')) {
                sessionStorage.setItem('user', JSON.stringify(userData));
              }
              
              if (localStorage.getItem('user')) {
                localStorage.setItem('user', JSON.stringify(userData));
              }
              
              // Update in approvedUsers list if exists
              const approvedUsersJSON = localStorage.getItem('approvedUsers');
              if (approvedUsersJSON) {
                try {
                  const approvedUsers = JSON.parse(approvedUsersJSON);
                  // Find and update user
                  const updatedApprovedUsers = approvedUsers.map(u => {
                    if (u.id === userData.id || u.email === userData.email) {
                      return { ...u, password: hashedPassword };
                    }
                    return u;
                  });
                  localStorage.setItem('approvedUsers', JSON.stringify(updatedApprovedUsers));
                } catch (e) {
                  console.error('Error updating approved users:', e);
                }
              }
            }
            
            // Update last login data
            const lastLoginJSON = localStorage.getItem('lastLogin');
            if (lastLoginJSON) {
              try {
                const lastLogin = JSON.parse(lastLoginJSON);
                lastLogin.token = newToken;
                localStorage.setItem('lastLogin', JSON.stringify(lastLogin));
              } catch (e) {
                console.error('Error updating last login data:', e);
              }
            }
            
            // Close modal and show success message
            this.showPasswordModal = false;
            alert('Password changed successfully');
            
            // Clear form
            this.passwordForm = {
              currentPassword: '',
              newPassword: '',
              confirmPassword: ''
            };
            return;
          }
          
          // For regular accounts, make API call
          const response = await fetch(`http://localhost:8000/api/users/${this.userData.id}/change-password`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              current_password: this.passwordForm.currentPassword,
              new_password: this.passwordForm.newPassword
            })
          });
          
          if (!response.ok) {
            const data = await response.json();
            throw new Error(data.detail || 'Failed to change password');
          }
          
          // Close modal and show success message
          this.showPasswordModal = false;
          alert('Password changed successfully');
          
          // Clear form
          this.passwordForm = {
            currentPassword: '',
            newPassword: '',
            confirmPassword: ''
          };
        } catch (error) {
          console.error('Error changing password:', error);
          alert(`Error: ${error.message}`);
        }
      },
      
      formatDate(dateString) {
        if (!dateString) return 'N/A';
        
        try {
          const date = new Date(dateString);
          return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
        } catch (e) {
          return dateString;
        }
      },
      
      getPermissionsByRole(role) {
        // Map roles to permissions for display purposes
        const permissionsMap = {
          'System Administrator': 'System Management',
          'Academic Coordinator': 'Full Scheduling Control',
          'Lab InCharge': 'Full Scheduling Control',
          'Dean': 'Approval & Oversight',
          'Faculty/Staff': 'Viewer',
          'Student': 'Viewer'
        };
        
        return permissionsMap[role] || 'Viewer';
      }
    }
  }
  </script>
  
  <style scoped>
  .dashboard-layout {
    display: flex;
    min-height: 100vh;
    background-color: #f5f7fa;
    width: 100%;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 1000;
  }
  
  .main-content {
    flex: 1;
    margin-left: 70px;
    width: calc(100% - 70px);
    transition: margin-left 0.3s ease;
    height: 100vh;
    position: relative;
    overflow-y: auto;
  }
  
  .dashboard-content {
    padding: 24px;
    min-height: calc(100vh - 60px);
    font-family: 'Inter', sans-serif;
    background-color: #f5f7fa;
  }
  
  .profile-container {
    background: white;
    border-radius: 8px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    padding: 24px;
  }
  
  .profile-header {
    display: flex;
    align-items: center;
    gap: 24px;
    padding-bottom: 24px;
    border-bottom: 1px solid rgba(221, 56, 90, 0.1);
  }
  
  .profile-avatar {
    width: 80px;
    height: 80px;
    background: rgba(221, 56, 90, 0.1);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .profile-avatar i {
    font-size: 32px;
    color: #DD385A;
  }
  
  .profile-info h2 {
    font-size: 24px;
    font-weight: 500;
    color: #333;
    margin-bottom: 8px;
  }
  
  .role-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 16px;
    font-size: 14px;
    font-weight: 500;
    margin-bottom: 8px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    border: 1px solid rgba(0, 0, 0, 0.05);
  }
  
  .role-badge.lab-incharge {
    background-color: #4da0ff;
    color: white;
  }
  
  .email {
    color: #666;
    font-family: 'Roboto Mono', monospace;
    font-size: 12px;
  }
  
  .detail-section {
    margin-top: 24px;
  }
  
  .detail-section h3 {
    color: #DD385A;
    font-size: 18px;
    font-weight: 500;
    margin-bottom: 16px;
  }
  
  .detail-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 24px;
  }
  
  .detail-item label {
    display: block;
    color: #666;
    font-size: 14px;
    margin-bottom: 4px;
  }
  
  .detail-item p {
    color: #333;
    font-size: 16px;
    font-weight: 500;
  }
  
  .detail-item:nth-child(1) p,
  .detail-item:nth-child(3) p {
    font-family: 'Roboto Mono', monospace;
    font-size: 12px;
    color: #666;
  }
  
  .settings-buttons {
    display: flex;
    gap: 16px;
  }
  
  .settings-buttons button {
    padding: 10px 20px;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 8px;
    transition: all 0.2s ease;
  }
  
  .edit-button {
    background-color: #DD385A;
    color: white;
    border: none;
  }
  
  .edit-button:hover {
    background-color: #c62f4d;
  }
  
  .password-button {
    background-color: white;
    color: #DD385A;
    border: 1px solid #DD385A;
  }
  
  .password-button:hover {
    background-color: rgba(221, 56, 90, 0.05);
  }
  
  /* Modal styles */
  .modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 2000;
  }
  
  .modal-content {
    background: white;
    border-radius: 8px;
    width: 400px;
    max-width: 90%;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  }
  
  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px;
    border-bottom: 1px solid #eee;
  }
  
  .modal-header h2 {
    margin: 0;
    font-size: 18px;
    color: #DD385A;
    font-weight: 500;
  }
  
  .close-button {
    background: none;
    border: none;
    cursor: pointer;
    font-size: 18px;
    color: #666;
  }
  
  .close-button:hover {
    color: #333;
  }
  
  .modal-body {
    padding: 16px;
  }
  
  .form-group {
    margin-bottom: 16px;
  }
  
  .form-group label {
    display: block;
    margin-bottom: 8px;
    font-size: 14px;
    color: #333;
  }
  
  .form-group input {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
  }
  
  .confirm-button {
    width: 100%;
    padding: 10px;
    background-color: #DD385A;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
  }
  
  .confirm-button:hover {
    background-color: #c62f4d;
  }
  
  /* Error and loading indicators */
  .loading-indicator {
    text-align: center;
    padding: 50px;
    font-size: 16px;
    color: #666;
  }
  
  .error-message {
    background-color: #f8d7da;
    color: #721c24;
    padding: 16px;
    border-radius: 8px;
    margin-bottom: 20px;
  }
  </style>