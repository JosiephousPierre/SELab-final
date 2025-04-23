<template>
  <div class="dashboard-layout">
    <DashBoardSideBarDean />
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
              <span class="role-badge dean">{{ userData.role }}</span>
              <p class="email">{{ userData.email }}</p>
            </div>
          </div>

          <div class="profile-details">
            <div class="detail-section">
              <h3>Personal Information</h3>
              <div class="detail-grid">
                <div class="detail-item">
                  <label>ID Number</label>
                  <p>{{ userData.id_number }}</p>
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
                  <p>{{ formatDate(userData.account_created) }}</p>
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
                <button class="edit-button" @click="showEditProfileModal">
                  <i class="fas fa-edit"></i>
                  Edit Profile
                </button>
                <button class="password-button" @click="showChangePasswordModal">
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
import DashBoardSideBarDean from '../../components/DashBoardSideBarDean.vue'
import DashBoardTopbar from '../../components/DashBoardTopbar.vue'

export default {
  name: 'UserProfileDean',
  components: {
    DashBoardSideBarDean,
    DashBoardTopbar
  },
  data() {
    return {
      userData: {
        id_number: '123333',
        full_name: 'Student Testing',
        email: 'student@gmail.com',
        role: 'error',
        permission_level: 'error',
        account_created: new Date('2025-03-28T02:12:05'),
        last_login: new Date('2025-03-28T02:00:42')
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
    this.checkAuth();
    this.loadUserData();
  },
  methods: {
    getInitial(name) {
      return name ? name.charAt(0).toUpperCase() : 'U';
    },
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
        
        // Verify the user has Dean role
        if (userData.role !== 'Dean') {
          console.error('User does not have permission to view this page');
          this.$router.push('/login');
        }
      } catch (error) {
        console.error('Error parsing user data:', error);
        this.$router.push('/login');
      }
    },
    loadUserData() {
      this.isLoading = true;
      this.errorMessage = null;
      
      try {
        // Get user data from storage
        const userStr = sessionStorage.getItem('user') || localStorage.getItem('user');
        if (userStr) {
          const userData = JSON.parse(userStr);
          
          this.userData = {
            id_number: userData.id || '123333',
            full_name: userData.full_name || 'Student Testing',
            email: userData.email || 'student@gmail.com',
            role: userData.role || 'error',
            permission_level: userData.role === 'Dean' ? 'Dean' : 'Viewer',
            account_created: userData.date_created ? new Date(userData.date_created) : new Date(),
            last_login: userData.last_login ? new Date(userData.last_login) : new Date()
          };
          
          // Initialize edit form
          this.editForm.full_name = this.userData.full_name;
          this.editForm.email = this.userData.email;
        }
        
        this.isLoading = false;
      } catch (error) {
        console.error('Error loading user data:', error);
        this.errorMessage = 'Failed to load user profile.';
        this.isLoading = false;
      }
    },
    showEditProfileModal() {
      this.editForm.full_name = this.userData.full_name;
      this.editForm.email = this.userData.email;
      this.showEditModal = true;
    },
    showChangePasswordModal() {
      this.passwordForm.currentPassword = '';
      this.passwordForm.newPassword = '';
      this.passwordForm.confirmPassword = '';
      this.showPasswordModal = true;
    },
    updateProfile() {
      // Validate inputs
      if (!this.editForm.full_name || !this.editForm.email) {
        alert('Please fill in all fields');
        return;
      }
      
      try {
        // Get existing user data
        const userStr = sessionStorage.getItem('user') || localStorage.getItem('user');
        if (userStr) {
          const userData = JSON.parse(userStr);
          
          // Update user data
          const updatedUser = {
            ...userData,
            full_name: this.editForm.full_name,
            email: this.editForm.email
          };
          
          // Save back to storage
          localStorage.setItem('user', JSON.stringify(updatedUser));
          sessionStorage.setItem('user', JSON.stringify(updatedUser));
          
          // Update component data
          this.userData.full_name = this.editForm.full_name;
          this.userData.email = this.editForm.email;
          
          // Close modal
          this.showEditModal = false;
          
          alert('Profile updated successfully');
        }
      } catch (error) {
        console.error('Error updating profile:', error);
        alert('Failed to update profile');
      }
    },
    updatePassword() {
      // Validate inputs
      if (!this.passwordForm.currentPassword || !this.passwordForm.newPassword || !this.passwordForm.confirmPassword) {
        alert('Please fill in all password fields');
        return;
      }
      
      if (this.passwordForm.newPassword !== this.passwordForm.confirmPassword) {
        alert('New passwords do not match');
        return;
      }
      
      // In a real app, this would call an API to update the password
      alert('Password updated successfully');
      this.showPasswordModal = false;
    },
    formatDate(dateValue) {
      if (!dateValue) return 'N/A';
      
      const date = new Date(dateValue);
      return date.toLocaleDateString('en-US', {
        month: 'long',
        day: 'numeric',
        year: 'numeric'
      }) + (date.getHours() ? (' at ' + date.toLocaleTimeString('en-US', {
        hour: 'numeric',
        minute: 'numeric',
        hour12: true
      })) : '');
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

.loading-indicator, .error-message {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
  font-size: 18px;
  color: #666;
}

.error-message {
  color: #DD385A;
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

.role-badge.dean {
  background-color: #FF9A3C;
  color: white;
}

.email {
  color: #666;
  font-family: 'Roboto Mono', monospace;
  font-size: 12px;
}

.profile-details {
  margin-top: 20px;
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
  gap: 20px;
}

.detail-item {
  margin-bottom: 16px;
}

.detail-item label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #666;
  margin-bottom: 4px;
}

.detail-item p {
  font-size: 16px;
  color: #333;
  margin: 0;
}

.settings-buttons {
  display: flex;
  gap: 16px;
  margin-top: 16px;
}

.edit-button, .password-button {
  background-color: #DD385A;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 10px 16px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  transition: background-color 0.2s ease;
}

.edit-button i, .password-button i {
  margin-right: 8px;
}

.edit-button:hover, .password-button:hover {
  background-color: #c52e4c;
}

/* Modal styles */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.modal-content {
  background-color: white;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid #eee;
}

.modal-header h2 {
  margin: 0;
  font-size: 20px;
  color: #333;
  font-weight: 500;
}

.close-button {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #999;
}

.modal-body {
  padding: 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #555;
  font-size: 14px;
}

.form-group input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.confirm-button {
  background-color: #DD385A;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 12px;
  font-weight: 500;
  cursor: pointer;
  width: 100%;
  font-size: 14px;
  transition: background-color 0.2s ease;
}

.confirm-button:hover {
  background-color: #c52e4c;
}

@media (max-width: 768px) {
  .detail-grid {
    grid-template-columns: 1fr;
  }
  
  .settings-buttons {
    flex-direction: column;
  }
  
  .edit-button, .password-button {
    width: 100%;
  }
  
  .profile-header {
    flex-direction: column;
    text-align: center;
  }
}
</style> 