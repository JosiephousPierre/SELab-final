<template>
  <div class="dashboard-layout">
    <DashBoardSideBarViewer />
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
              <span class="role-badge faculty-staff">{{ userData.role }}</span>
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
                <!-- Show Year & Section for students only -->
                <div v-if="userData.role === 'Student'" class="detail-item">
                  <label>Year & Section</label>
                  <p>{{ userData.year_section || 'Not specified' }}</p>
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
              <!-- Year & Section field for students only -->
              <div v-if="userData.role === 'Student'" class="form-group">
                <label>Year & Section</label>
                <select v-model="editForm.year_section" class="section-dropdown">
                  <option value="">Select Year & Section</option>
                  <option value="BSIT 1A">BSIT 1A</option>
                  <option value="BSIT 1B">BSIT 1B</option>
                  <option value="BSCS 1A">BSCS 1A</option>
                  <option value="BSIT 2A">BSIT 2A</option>
                  <option value="BSIT 2B">BSIT 2B</option>
                  <option value="BSCS 2A">BSCS 2A</option>
                  <option value="BSIT 3A">BSIT 3A</option>
                  <option value="BSIT 3B">BSIT 3B</option>
                  <option value="BSCS 3A">BSCS 3A</option>
                  <option value="BSIT 4A">BSIT 4A</option>
                  <option value="BSIT 4B">BSIT 4B</option>
                  <option value="BSCS 4A">BSCS 4A</option>
                </select>
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
import DashBoardSideBarViewer from '../../components/DashBoardSideBarViewer.vue'
import DashBoardTopbar from '../../components/DashBoardTopbar.vue'

export default {
  name: 'UserProfileViewer',
  components: {
    DashBoardSideBarViewer,
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
        email: '',
        year_section: ''
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
        // Get user id from storage
        const userDataStr = sessionStorage.getItem('user') || localStorage.getItem('user') || '{}';
        const userData = JSON.parse(userDataStr);
        const token = localStorage.getItem('token') || sessionStorage.getItem('token');
        
        if (!userData.id || !token) {
          this.errorMessage = 'User information not found. Please log in again.';
          this.$router.push('/login');
          return;
        }
        
        console.log('Fetching profile for user:', userData.id);
        console.log('User role from storage:', userData.role);
        
        // Always fetch from the API for debugging - removed fallback
        const response = await fetch(`http://localhost:8000/api/users/${userData.id}/profile`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        if (!response.ok) {
          const data = await response.json();
          console.error('API Error on profile fetch:', data);
          throw new Error(data.detail || 'Failed to fetch user profile');
        }
        
        const data = await response.json();
        console.log('Profile API response:', data);
        console.log('year_section in profile response:', data.year_section);
        
        this.userData = data;
        
        // Initialize edit form with current values
        this.editForm.full_name = data.full_name;
        this.editForm.email = data.email;
        this.editForm.year_section = data.year_section || '';
        
      } catch (error) {
        console.error('Error fetching user profile:', error);
        this.errorMessage = error.message;
      } finally {
        this.isLoading = false;
      }
    },
    
    async updateProfile() {
      try {
        const token = localStorage.getItem('token') || sessionStorage.getItem('token');
        
        if (!token) {
          this.errorMessage = 'Authentication token not found. Please log in again.';
          this.$router.push('/login');
          return;
        }
        
        console.log('Starting profile update');
        
        // Prepare base profile update data (always includes these)
        const baseUpdateData = {
          full_name: this.editForm.full_name,
          email: this.editForm.email
        };
        
        // First update the basic profile data
        console.log('Updating basic profile data:', baseUpdateData);
        
        const baseResponse = await fetch(`http://localhost:8000/api/users/${this.userData.id}/profile`, {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(baseUpdateData)
        });
        
        if (!baseResponse.ok) {
          const data = await baseResponse.json();
          console.error('API Error on base profile update:', data);
          throw new Error(data.detail || 'Failed to update profile');
        }
        
        let updatedUser = await baseResponse.json();
        console.log('Base profile update response:', updatedUser);
        
        // If the user is a Student and has a year_section value, update that separately
        if (this.userData.role === 'Student' && this.editForm.year_section !== undefined) {
          console.log('User is a Student, updating year_section separately:', this.editForm.year_section);
          
          // Use the dedicated endpoint for year_section updates
          const yearSectionResponse = await fetch(`http://localhost:8000/api/users/${this.userData.id}/year-section`, {
            method: 'PUT',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              year_section: this.editForm.year_section
            })
          });
          
          if (!yearSectionResponse.ok) {
            const data = await yearSectionResponse.json();
            console.error('API Error on year_section update:', data);
            throw new Error(data.detail || 'Failed to update year and section');
          }
          
          // Get the updated user data with the year_section
          updatedUser = await yearSectionResponse.json();
          console.log('Year section update response:', updatedUser);
          console.log('Updated year_section value:', updatedUser.year_section);
        } else {
          console.log('User is not a Student or no year_section provided, skipping dedicated endpoint');
        }
        
        // Update the local userData
        this.userData = updatedUser;
        
        // Update both sessionStorage and localStorage if they exist
        if (sessionStorage.getItem('user')) {
          const storedSessionUser = JSON.parse(sessionStorage.getItem('user'));
          storedSessionUser.full_name = updatedUser.full_name;
          storedSessionUser.email = updatedUser.email;
          storedSessionUser.year_section = updatedUser.year_section;
          sessionStorage.setItem('user', JSON.stringify(storedSessionUser));
        }
        
        if (localStorage.getItem('user')) {
          const storedLocalUser = JSON.parse(localStorage.getItem('user'));
          storedLocalUser.full_name = updatedUser.full_name;
          storedLocalUser.email = updatedUser.email;
          storedLocalUser.year_section = updatedUser.year_section;
          localStorage.setItem('user', JSON.stringify(storedLocalUser));
        }
        
        // Close modal and show success message
        this.showEditModal = false;
        alert('Profile updated successfully');
      } catch (error) {
        console.error('Error updating profile:', error);
        alert('Error: ' + error.message);
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
        const token = localStorage.getItem('token') || sessionStorage.getItem('token');
        
        if (!token) {
          this.errorMessage = 'Authentication token not found. Please log in again.';
          this.$router.push('/login');
          return;
        }
        
        // Handle fallback token case
        if (token.startsWith('admin_fallback_token_') || token.startsWith('user_fallback_token_') || token.startsWith('fallback_token_')) {
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
          if (localStorage.getItem('token')) {
            localStorage.setItem('token', newToken);
          }
          
          if (sessionStorage.getItem('token')) {
            sessionStorage.setItem('token', newToken);
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
}

.main-content {
  flex: 1;
  margin-left: 70px;
  width: calc(100vw - 70px);
  transition: margin-left 0.3s ease;
}

.dashboard-content {
  padding: 24px;
  min-height: calc(100vh - 60px);
  font-family: 'Inter', sans-serif;
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

.role-badge.faculty-staff {
  background-color: #FFB74D;
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

/* New styles for loading, error, and modals */
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

.form-group input, .form-group select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.section-dropdown {
  background-color: white;
  color: #333;
  cursor: pointer;
  appearance: auto;
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
  margin-top: 8px;
}

.confirm-button:hover {
  background-color: #c62f4d;
}
</style>