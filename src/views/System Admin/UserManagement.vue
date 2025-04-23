<template>
    <div class="dashboard-layout">
      <DashBoardSidebarSysAd />
      <div class="main-content">
        <DashBoardTopbar />
        <div class="dashboard-content">
          <div class="header">
            <h1>User Management</h1>
          </div>
  
          <div v-if="errorMessage" class="error-message">
            {{ errorMessage }}
          </div>
  
          <div class="filters-section">
            <div class="search-box">
              <input type="text" placeholder="Search..." v-model="searchQuery">
              <i class="fas fa-search"></i>
            </div>
            
            <div class="filter-group">
              <div class="filter-dropdown">
                <select v-model="selectedRole">
                  <option value="">Roles</option>
                  <option value="System Administrator">System Administrator</option>
                  <option value="Academic Coordinator">Academic Coordinator</option>
                  <option value="Lab InCharge">Lab InCharge</option>
                  <option value="Dean">Dean</option>
                  <option value="Faculty/Staff">Faculty/Staff</option>
                  <option value="Student">Student</option>
                </select>
              </div>
  
              <div class="filter-dropdown">
                <select v-model="selectedPermission">
                  <option value="">Permissions</option>
                  <option value="Full Scheduling Control">Full Scheduling Control</option>
                  <option value="Approval & Oversight">Approval & Oversight</option>
                  <option value="Viewer">Viewer</option>
                  <option value="System Management">System Management</option>
                </select>
              </div>
              
              <div class="filter-dropdown">
                <select v-model="selectedStatus">
                  <option value="">Status</option>
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                </select>
              </div>
            </div>
          </div>
  
          <!-- Loading indicator -->
          <div v-if="isLoading" class="loading-indicator">
            Loading users...
          </div>
  
          <!-- Empty state -->
          <div v-else-if="users.length === 0" class="no-users-message">
            No users found. Users will appear here after they are approved.
          </div>
  
          <!-- Users table -->
          <div v-else class="users-table">
            <div class="table-container">
              <table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Full Name</th>
                    <th>Email</th>
                    <th>Permissions</th>
                    <th>Roles</th>
                    <th>Status</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="user in filteredUsers" :key="user.id" :class="{ 'inactive-user': !user.is_active }">
                    <td>{{ user.id }}</td>
                    <td>{{ user.full_name }}</td>
                    <td>{{ user.email }}</td>
                    <td>{{ user.permissions }}</td>
                    <td>
                      <span class="role-badge" :class="getRoleBadgeClass(user.role)">
                        {{ user.role }}
                      </span>
                    </td>
                    <td>
                      <span class="status-badge" :class="user.is_active ? 'active' : 'inactive'">
                        {{ user.is_active ? 'Active' : 'Inactive' }}
                      </span>
                    </td>
                    <td>
                      <div class="actions">
                        <button class="action-button" @click="toggleActionMenu(user, $event)">
                          <i class="fas fa-ellipsis-h"></i>
                        </button>
                        <div v-if="selectedUser === user" class="action-menu" :style="{ top: menuPosition.top, left: menuPosition.left }">
                          <button @click="showModifyModal(user)">
                            <i class="fas fa-edit"></i> Modify
                          </button>
                          <button @click="showDeleteModal(user)">
                            <i class="fas fa-trash"></i> Delete
                          </button>
                          <button v-if="user.is_active" @click="showDeactivateModal(user)">
                            <i class="fas fa-ban"></i> Deactivate
                          </button>
                          <button v-else @click="showActivateModal(user)">
                            <i class="fas fa-check-circle"></i> Activate
                          </button>
                        </div>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
  
      <!-- Modify User Modal -->
      <div v-if="showingModifyModal" class="modal">
        <div class="modal-content">
          <div class="modal-header">
            <h2>Please Select</h2>
            <button class="close-button" @click="closeModals">
              <i class="fas fa-times"></i>
            </button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label>Roles</label>
              <select v-model="modifyForm.role">
                <option v-for="role in availableRoles" :key="role" :value="role">{{ role }}</option>
              </select>
            </div>
            <div class="form-group">
              <label>Permissions</label>
              <select v-model="modifyForm.permissions" disabled>
                <option value="System Management">System Management</option>
                <option value="Full Scheduling Control">Full Scheduling Control</option>
                <option value="Laboratory Booking Management">Laboratory Booking Management</option>
                <option value="Approval & Oversight">Approval & Oversight</option>
                <option value="Viewer">Viewer</option>
              </select>
            </div>
            <button class="confirm-button" @click="confirmModify">Confirm</button>
          </div>
        </div>
      </div>
  
      <!-- Delete User Modal -->
      <div v-if="showingDeleteModal" class="modal">
        <div class="modal-content">
          <div class="modal-header">
            <h2>Delete User</h2>
            <button class="close-button" @click="closeModals">
              <i class="fas fa-times"></i>
            </button>
          </div>
          <div class="modal-body">
            <p class="delete-message">Are you sure you want to delete {{ selectedUser?.full_name }}?</p>
            <div class="modal-buttons">
              <button class="cancel-button" @click="closeModals">Cancel</button>
              <button class="confirm-button" @click="confirmDelete">Confirm</button>
            </div>
            </div>
          </div>
        </div>

      <!-- Deactivate User Modal -->
      <div v-if="showingDeactivateModal" class="modal">
        <div class="modal-content">
          <div class="modal-header">
            <h2>Deactivate User</h2>
            <button class="close-button" @click="closeModals">
              <i class="fas fa-times"></i>
            </button>
          </div>
          <div class="modal-body">
            <p class="delete-message">Are you sure you want to deactivate {{ selectedUser?.full_name }}?</p>
            <p class="info-message">This user will no longer be able to log in to the system.</p>
            <div class="modal-buttons">
              <button class="cancel-button" @click="closeModals">Cancel</button>
              <button class="confirm-button" @click="confirmDeactivate">Confirm</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Activate User Modal -->
      <div v-if="showingActivateModal" class="modal">
        <div class="modal-content">
          <div class="modal-header">
            <h2>Activate User</h2>
            <button class="close-button" @click="closeModals">
              <i class="fas fa-times"></i>
            </button>
          </div>
          <div class="modal-body">
            <p class="delete-message">Are you sure you want to activate {{ selectedUser?.full_name }}?</p>
            <p class="success-message">This user will be able to log in to the system again.</p>
            <div class="modal-buttons">
              <button class="cancel-button" @click="closeModals">Cancel</button>
              <button class="confirm-button" @click="confirmActivate">Confirm</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import DashBoardSidebarSysAd from '../../components/DashBoardSidebarSysAd.vue'
  import DashBoardTopbar from '../../components/DashBoardTopbar.vue'
  import { getPermissionsByRole } from '../../utils/roleUtils.js'
  
  export default {
    name: 'UserManagement',
    components: {
      DashBoardSidebarSysAd,
      DashBoardTopbar
    },
    data() {
      return {
        searchQuery: '',
        selectedRole: '',
        selectedPermission: '',
        selectedStatus: '',
        selectedUser: null,
        menuPosition: { top: 0, left: 0 },
        showingModifyModal: false,
        showingDeleteModal: false,
        showingDeactivateModal: false,
        showingActivateModal: false,
        modifyForm: {
          role: '',
          permissions: ''
        },
        users: [],
        isLoading: false,
        errorMessage: null,
        userDataInterval: null,
        availableRoles: []
      }
    },
    async created() {
      await this.fetchRoles();
      this.fetchApprovedUsers();
    },
    mounted() {
      this.fetchApprovedUsers();
      
      // Set up timer to refresh user data periodically, but less frequently
      this.userDataInterval = setInterval(() => {
        console.log('Periodic check for approved users');
        this.fetchApprovedUsers();
      },100000); // Check every 60 seconds instead of every 5 seconds
      
      // Also check when the component regains focus
      window.addEventListener('focus', this.fetchApprovedUsers);
      
      // Add visibility change event listener for better tab switching detection
      document.addEventListener('visibilitychange', this.handleVisibilityChange);
    },
    beforeUnmount() {
      // Clear interval and remove event listeners when component is destroyed
      if (this.userDataInterval) {
        clearInterval(this.userDataInterval);
      }
      window.removeEventListener('focus', this.fetchApprovedUsers);
      document.removeEventListener('visibilitychange', this.handleVisibilityChange);
    },
    computed: {
      filteredUsers() {
        return this.users.filter(user => {
          const matchesSearch = !this.searchQuery || 
            user.full_name.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
            user.email.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
            user.id.includes(this.searchQuery)
          
          const matchesRole = !this.selectedRole || user.role === this.selectedRole
          const matchesPermission = !this.selectedPermission || 
            this.getPermissionsByRole(user.role) === this.selectedPermission
          const matchesStatus = !this.selectedStatus || 
            (this.selectedStatus === 'active' && user.is_active) ||
            (this.selectedStatus === 'inactive' && !user.is_active)
          
          return matchesSearch && matchesRole && matchesPermission && matchesStatus
        })
      }
    },
    methods: {
      async fetchRoles() {
        try {
          const token = sessionStorage.getItem('token') || localStorage.getItem('token');
          
          if (!token) {
            this.errorMessage = 'Not authenticated. Please log in again.';
            this.$router.push('/login');
            return;
          }
          
          const response = await fetch('http://127.0.0.1:8000/api/roles', {
            method: 'GET',
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });
          
          if (!response.ok) {
            const errorData = await response.text();
            console.error('Failed to fetch roles. Status:', response.status, 'Response:', errorData);
            throw new Error(`Failed to fetch roles (${response.status}): ${errorData}`);
          }
          
          const data = await response.json();
          if (!data.roles || !Array.isArray(data.roles)) {
            console.error('Invalid roles data format:', data);
            throw new Error('Received invalid roles data format from server');
          }
          
          console.log('Successfully fetched roles:', data.roles);
          this.availableRoles = data.roles;
        } catch (error) {
          console.error('Error fetching roles:', error);
          // Fallback to default roles if API fails
          this.availableRoles = [
            'System Administrator',
            'Academic Coordinator',
            'Lab InCharge',
            'Dean',
            'Faculty/Staff',
            'Student'
          ];
          console.log('Using fallback roles:', this.availableRoles);
        }
      },
      async fetchApprovedUsers() {
        this.isLoading = true;
        this.errorMessage = null;
        
        try {
          // Get token from sessionStorage first, fall back to localStorage if needed
          const token = sessionStorage.getItem('token') || localStorage.getItem('token');
          
          if (!token) {
            this.errorMessage = 'Not authenticated. Please log in again.';
            this.$router.push('/login');
            return;
          }
          
          // Make API call to fetch approved users
          const response = await fetch('http://127.0.0.1:8000/api/users/approved', {
            method: 'GET',
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });
          
          if (!response.ok) {
            const data = await response.json();
            throw new Error(data.detail || 'Failed to fetch users');
          }
          
          const data = await response.json();
          
          // Filter out users with Student role
          const filteredUsers = data.users.filter(user => user.role !== 'Student');
          
          this.users = filteredUsers.map(user => ({
            ...user,
            permissions: this.getPermissionsByRole(user.role)
          }));
        } catch (error) {
          console.error('Error fetching approved users:', error);
          this.errorMessage = error.message;
          this.users = [];
        } finally {
          this.isLoading = false;
        }
      },
      
      getPermissionsByRole(role) {
        return getPermissionsByRole(role);
      },
      
      // Handle visibility change for better tab switching support
      handleVisibilityChange() {
        if (document.visibilityState === 'visible') {
          console.log('Tab is now visible, fetching latest user data');
          this.fetchApprovedUsers();
        }
      },
      
      getRoleBadgeClass(role) {
        const classes = {
          'System Administrator': 'admin',
          'Academic Coordinator': 'coordinator',
          'Dean': 'dean',
          'Faculty/Staff': 'staff',
          'Student': 'student',
          'Lab InCharge': 'staff'
        }
        return classes[role] || ''
      },
      toggleActionMenu(user, event) {
        if (this.selectedUser === user) {
          this.selectedUser = null;
          return;
        }
        
        this.selectedUser = user;
        
        // Get button position
        const button = event.target.closest('.action-button');
        const rect = button.getBoundingClientRect();
        
        // Calculate menu position
        this.menuPosition = {
          top: rect.bottom + window.scrollY + 'px',
          left: rect.left + window.scrollX - 110 + 'px' // Adjust 110px to align menu properly
        };
      },
      showModifyModal(user) {
        this.selectedUser = { ...user }
        this.modifyForm.role = user.role
        this.modifyForm.permissions = this.getPermissionsByRole(user.role)
        this.showingModifyModal = true
      },
      showDeleteModal(user) {
        this.selectedUser = { ...user }
        this.showingDeleteModal = true
      },
      showDeactivateModal(user) {
        this.selectedUser = { ...user }
        this.showingDeactivateModal = true
      },
      showActivateModal(user) {
        this.selectedUser = { ...user }
        this.showingActivateModal = true
      },
      closeModals() {
        this.showingModifyModal = false
        this.showingDeleteModal = false
        this.showingDeactivateModal = false
        this.showingActivateModal = false
        this.selectedUser = null
      },
      async confirmModify() {
        if (!this.selectedUser || !this.selectedUser.id) {
          console.error("Cannot modify: No user selected or missing user ID")
          alert("Error: Cannot identify user to modify")
          this.closeModals()
          return
        }
        
        const userId = this.selectedUser.id
        const userName = this.selectedUser.full_name || 'selected user'
        const currentRole = this.selectedUser.role
        const newRole = this.modifyForm.role
        
        // Skip the update if the role hasn't changed
        if (currentRole === newRole) {
          console.log(`Role not changed (still ${newRole}), skipping update`)
          alert(`No changes made - user's role is already ${newRole}`)
          this.closeModals()
          return
        }
        
        try {
          const token = sessionStorage.getItem('token') || localStorage.getItem('token')
          
          if (!token) {
            alert('You must be logged in to perform this action')
            this.$router.push('/login')
            return
          }
          
          console.log(`Modifying user ${userId} role from ${currentRole} to ${newRole}`)
          
          // Make API call to update user role
          const response = await fetch(`http://127.0.0.1:8000/api/users/${userId}/role`, {
            method: 'PUT',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              role: newRole
            })
          })
          
          if (!response.ok) {
            const data = await response.json()
            throw new Error(data.detail || 'Failed to update user')
          }
          
          // Update local user data
          const updatedUser = await response.json()
          const previousRole = this.users.find(u => u.id === updatedUser.id)?.role
          
          this.users = this.users.map(user => {
            if (user.id === updatedUser.id) {
              return {
                ...user,
                role: updatedUser.role,
                permissions: this.getPermissionsByRole(updatedUser.role)
              }
            }
            return user
          })
          
          // Check if the user we just modified is currently logged in
          const currentLoggedInUser = JSON.parse(sessionStorage.getItem('user') || '{}')
          if (currentLoggedInUser && currentLoggedInUser.id === updatedUser.id) {
            // Update current user data in sessionStorage
            currentLoggedInUser.role = updatedUser.role
            currentLoggedInUser.permissions = this.getPermissionsByRole(updatedUser.role)
            
            sessionStorage.setItem('user', JSON.stringify(currentLoggedInUser))
            
            // Tell the user they need to log out and back in to see the change
            alert(`User role updated from ${previousRole} to ${updatedUser.role}. Since this is your account, you will be logged out after clicking OK.`)
            
            // Log the current user out
            this.clearSession()
            this.$router.push('/login')
          } else {
            // Inform the admin that the modified user will be automatically logged out
            alert(`User ${updatedUser.full_name || userName}'s role has been updated from ${previousRole} to ${updatedUser.role}. The user will be automatically logged out of the system.`)
          }
          
          this.closeModals()
          
        } catch (error) {
          console.error('Error updating user:', error)
          alert(`Error: ${error.message}`)
          this.closeModals()
        }
      },
      async confirmDelete() {
        if (!this.selectedUser || !this.selectedUser.id) {
          console.error("Cannot delete: No user selected or missing user ID")
          alert("Error: Cannot identify user to delete")
          this.closeModals()
          return
        }
        
        const userId = this.selectedUser.id
        const userName = this.selectedUser.full_name || 'selected user'
        
        try {
          const token = sessionStorage.getItem('token') || localStorage.getItem('token')
          
          if (!token) {
            alert('You must be logged in to perform this action')
            this.$router.push('/login')
            return
          }
          
          // Make API call to delete the user
          console.log(`Deleting user with ID: ${userId}`)
          const response = await fetch(`http://127.0.0.1:8000/api/users/${userId}`, {
            method: 'DELETE',
            headers: {
              'Authorization': `Bearer ${token}`
            }
          })
          
          if (!response.ok) {
            const data = await response.json()
            throw new Error(data.detail || 'Failed to delete user')
          }
          
          // Remove user from local data
          this.users = this.users.filter(user => user.id !== userId)
          
          this.closeModals()
          alert(`User ${userName} has been deleted.`)
          
        } catch (error) {
          console.error('Error deleting user:', error)
          alert(`Error: ${error.message}`)
          this.closeModals()
        }
      },
      async confirmDeactivate() {
        if (!this.selectedUser || !this.selectedUser.id) {
          console.error("Cannot deactivate: No user selected or missing user ID")
          alert("Error: Cannot identify user to deactivate")
          this.closeModals()
          return
        }
        
        const userId = this.selectedUser.id
        const userName = this.selectedUser.full_name || 'selected user'
        
        try {
          const token = sessionStorage.getItem('token') || localStorage.getItem('token')
          
          if (!token) {
            alert('You must be logged in to perform this action')
            this.$router.push('/login')
            return
          }
          
          // Check if the user being deactivated is the last System Administrator
          if (this.selectedUser.role === 'System Administrator') {
            const activeAdmins = this.users.filter(user => 
              user.role === 'System Administrator' && user.is_active && user.id !== userId
            )
            
            if (activeAdmins.length === 0) {
              alert('Cannot deactivate the last active System Administrator account')
              this.closeModals()
              return
            }
          }
          
          // Check if trying to deactivate self
          const currentUser = JSON.parse(sessionStorage.getItem('user') || localStorage.getItem('user') || '{}')
          if (currentUser && currentUser.id === userId) {
            alert('You cannot deactivate your own account while logged in')
            this.closeModals()
            return
          }
          
          // Make API call to deactivate the user
          const response = await fetch(`http://127.0.0.1:8000/api/users/${userId}/deactivate`, {
            method: 'PUT',
            headers: {
              'Authorization': `Bearer ${token}`
            }
          })
          
          if (!response.ok) {
            const data = await response.json()
            throw new Error(data.detail || 'Failed to deactivate user')
          }
          
          // Update user in local data
          const updatedUser = await response.json()
          this.users = this.users.map(user => {
            if (user.id === updatedUser.id) {
              return {
                ...user,
                is_active: updatedUser.is_active
              }
            }
            return user
          })
          
          this.closeModals()
          alert(`User ${updatedUser.full_name || userName} has been deactivated. The user will be automatically logged out of the system.`)
          
        } catch (error) {
          console.error('Error deactivating user:', error)
          alert(`Error: ${error.message}`)
          this.closeModals()
        }
      },
      async confirmActivate() {
        if (!this.selectedUser || !this.selectedUser.id) {
          console.error("Cannot activate: No user selected or missing user ID")
          alert("Error: Cannot identify user to activate")
          this.closeModals()
          return
        }
        
        const userId = this.selectedUser.id
        const userName = this.selectedUser.full_name || 'selected user'
        
        try {
          const token = sessionStorage.getItem('token') || localStorage.getItem('token')
          
          if (!token) {
            alert('You must be logged in to perform this action')
            this.$router.push('/login')
            return
          }
          
          // Make API call to activate the user
          const response = await fetch(`http://127.0.0.1:8000/api/users/${userId}/activate`, {
            method: 'PUT',
            headers: {
              'Authorization': `Bearer ${token}`
            }
          })
          
          if (!response.ok) {
            const data = await response.json()
            throw new Error(data.detail || 'Failed to activate user')
          }
          
          // Update user in local data
          const updatedUser = await response.json()
          this.users = this.users.map(user => {
            if (user.id === updatedUser.id) {
              return {
                ...user,
                is_active: updatedUser.is_active
              }
            }
            return user
          })
          
          this.closeModals()
          alert(`User ${updatedUser.full_name || userName} has been activated. The user will need to log in again to access the system.`)
          
        } catch (error) {
          console.error('Error activating user:', error)
          alert(`Error: ${error.message}`)
          this.closeModals()
        }
      },
      // Add a utility method to clear session if needed
      clearSession() {
        sessionStorage.removeItem('token');
        sessionStorage.removeItem('user');
        localStorage.removeItem('token');
        localStorage.removeItem('user');
      }
    },
    watch: {
      'modifyForm.role': {
        handler(newRole) {
          this.modifyForm.permissions = getPermissionsByRole(newRole);
        }
      }
    }
  }
  </script>
  
  <style scoped>
  .dashboard-layout {
    display: flex;
    min-height: 100vh;
    background-color: #f5f5f5;
    width: 100vw;
  }
  
  .main-content {
    flex: 1;
    margin-left: 70px;
    width: calc(100vw - 70px);
    min-width: 0;
    display: flex;
    flex-direction: column;
    overflow-x: hidden;
  }

  .dashboard-content {
    padding: 24px;
    min-height: calc(100vh - 60px);
    background-color: #f5f5f5;
    width: 100%;
  }
  
  .header {
    margin-bottom: 24px;
  }
  
  .header h1 {
    font-size: 20px;
    font-weight: 500;
    color: #DD385A;
  }
  
  .filters-section {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    gap: 16px;
  }
  
  .search-box {
    position: relative;
    width: 220px;
  }
  
  .search-box input {
    width: 100%;
    padding: 8px 16px;
    padding-left: 40px;
    border: 1px solid #DD385A;
    border-radius: 8px;
    font-size: 14px;
  }

  .search-box input:focus {
    border-color: #DD385A;
    outline: none;
  }

  .search-box i {
    position: absolute;
    left: 12px;
    top: 50%;
    transform: translateY(-50%);
    color: #666;
  }
  
  .filter-group {
    display: flex;
    gap: 16px;
  }
  
  .filter-dropdown select {
    padding: 8px 16px;
    border: 1px solid #DD385A;
    border-radius: 8px;
    font-size: 14px;
    min-width: 150px;
    cursor: pointer;
    color: #666;
    font-weight: normal;
    background-color: white;
  }

  .filter-dropdown select:focus {
    border-color: #DD385A;
    outline: none;
  }

  .filter-dropdown select option[value=""] {
    color: rgba(102, 102, 102, 0.6);
  }

  .filter-dropdown select option:not([value=""]) {
    color: #DD385A;
    font-weight: 500;
    background-color: white;
  }

  .filter-dropdown select option:checked {
    background-color: #DD385A;
    color: white;
  }

  .filter-dropdown select option:hover {
    background-color: rgba(221, 56, 90, 0.1);
  }
  
  .users-table {
    background: white;
    border-radius: 8px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    position: relative;
    max-height: calc(100vh - 250px); /* Adjust based on your header and filters height */
    overflow: hidden;
  }
  
  .table-container {
    overflow-y: auto;
    max-height: 100%;
    position: relative;
  }

  /* Custom scrollbar styling */
  .table-container::-webkit-scrollbar {
    width: 8px;
  }

  .table-container::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 4px;
  }

  .table-container::-webkit-scrollbar-thumb {
    background: #DD385A;
    border-radius: 4px;
  }

  .table-container::-webkit-scrollbar-thumb:hover {
    background: #c62f4d;
  }

  .users-table table {
    width: 100%;
    border-collapse: collapse;
  }

  .users-table thead {
    position: sticky;
    top: 0;
    background-color: #f9f9f9;
    z-index: 1;
  }

  .users-table th, .users-table td {
    padding: 16px;
    text-align: left;
    border-bottom: 1px solid #eee;
  }
  
  .users-table th {
    font-weight: 600;
    color: #DD385A;
    background-color: #f9f9f9;
  }
  
  .users-table td {
    padding: 12px 16px;
    color: #666; /* Default color for all cells */
  }

  .users-table td:nth-child(1) { /* ID */
    font-family: 'Inter', sans-serif;
    color: #666;
  }

  .users-table td:nth-child(2) { /* Full Name */
    color: #DD385A;
    font-weight: 500;
  }

  .users-table td:nth-child(3) { /* Email */
    font-family: 'Inter', sans-serif;
    color: #666;
  }

  .users-table td:nth-child(4) { /* Permissions */
    color: #DD385A;
    font-weight: 500;
  }
  
  .users-table td:nth-child(5) { /* Roles */
    color: #666;
  }
  
  .role-badge {
    padding: 4px 12px;
    border-radius: 16px;
    font-size: 12px;
    font-weight: 500;
  }
  
  .role-badge.admin {
    background-color: #DD385A;
    color: white;
  }
  
  .role-badge.coordinator {
    background-color: #E57373;
    color: white;
  }
  
  .role-badge.dean {
    background-color: #F06292;
    color: white;
  }
  
  .role-badge.staff {
    background-color: #FFB74D;
    color: white;
  }
  
  .role-badge.student {
    background-color: #81C784;
    color: white;
  }
  
  .actions {
    position: relative;
  }
  
  .action-button {
    background: none;
    border: none;
    cursor: pointer;
    padding: 4px 8px;
    color: #DD385A;
  }
  
  .action-button i {
    color: #DD385A;
  }
  
  .action-menu {
    position: fixed;
    background: white;
    border-radius: 4px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    z-index: 1000;
    min-width: 150px;
  }
  
  .action-menu button {
    display: flex;
    align-items: center;
    gap: 8px;
    width: 100%;
    padding: 8px 16px;
    border: none;
    background: none;
    cursor: pointer;
    text-align: left;
    color: #DD385A;
  }
  
  .action-menu button i {
    margin-right: 8px;
    color: #DD385A;
  }
  
  .action-menu button:hover {
    color: #DD385A;
    background-color: rgba(221, 56, 90, 0.1);
  }
  
  .modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }
  
  .modal-content {
    background: white;
    border-radius: 8px;
    width: 100%;
    max-width: 400px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  }
  
  .modal-header {
    padding: 16px 24px;
    border-bottom: 1px solid rgba(221, 56, 90, 0.1);
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .modal-header h2 {
    color: #DD385A;
    font-size: 20px;
    font-weight: 500;
    margin: 0;
  }
  
  .close-button {
    background: none;
    border: none;
    color: #DD385A;
    cursor: pointer;
    font-size: 18px;
    padding: 4px;
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
    color: #DD385A;
    font-weight: 500;
  }
  
  .form-group select {
    width: 100%;
    padding: 8px 12px;
    border: 1px solid rgba(221, 56, 90, 0.2);
    border-radius: 6px;
    font-size: 14px;
    color: #666;
    background-color: white;
  }
  
  .form-group select:focus {
    outline: none;
    border-color: #DD385A;
  }
  
  .form-group select option {
    color: #DD385A;
    font-weight: 500;
  }
  
  .form-group select option[value=""] {
    color: rgba(102, 102, 102, 0.6);
  }
  
  .confirm-button {
    width: 100%;
    padding: 12px;
    background-color: #DD385A;
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 16px;
    font-weight: 500;
    cursor: pointer;
    transition: background-color 0.2s;
  }
  
  .confirm-button:hover {
    background-color: #c62f4d;
  }
  
  .warning-box {
    background-color: rgba(221, 56, 90, 0.05);
    border: 1px solid rgba(221, 56, 90, 0.2);
    border-radius: 6px;
    padding: 16px;
    margin: 16px 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  
  .warning-box i {
    color: #DD385A;
    font-size: 24px;
    margin-bottom: 8px;
  }
  
  .warning-box p {
    margin: 4px 0;
    color: #666;
  }
  
  .warning-box p:first-of-type {
    color: #DD385A;
    font-weight: 500;
    font-size: 16px;
  }
  
  .delete-message {
    font-size: 16px;
    color: #DD385A;
    margin-bottom: 16px;
    text-align: center;
    font-weight: 500;
  }
  
  .modal-actions {
    display: flex;
    gap: 12px;
    margin-top: 24px;
  }
  
  .delete-button {
    flex: 1;
    padding: 12px;
    background-color: #DD385A;
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 16px;
    font-weight: 500;
    cursor: pointer;
    transition: background-color 0.2s;
  }
  
  .delete-button:hover {
    background-color: #c62f4d;
  }
  
  .cancel-button {
    flex: 1;
    padding: 12px;
    background-color: #f5f5f5;
    color: #666;
    border: none;
    border-radius: 6px;
    font-size: 16px;
    font-weight: 500;
    cursor: pointer;
    transition: background-color 0.2s;
  }
  
  .cancel-button:hover {
    background-color: #ebebeb;
  }

  .error-message {
    background-color: #f8d7da;
    color: #721c24;
    padding: 12px;
    border-radius: 6px;
    margin-bottom: 20px;
    font-size: 14px;
  }

  .loading-indicator {
    text-align: center;
    padding: 30px;
    font-size: 16px;
    color: #777;
  }

  .no-users-message {
    text-align: center;
    padding: 30px;
    font-size: 16px;
    color: #555;
    background-color: #f9f9f9;
    border-radius: 8px;
    margin-top: 20px;
  }

  .info-message {
    color: #31708f;
    background-color: #d9edf7;
    border: 1px solid #bce8f1;
    padding: 10px;
    border-radius: 4px;
    margin-bottom: 15px;
    font-size: 14px;
  }

  .status-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 12px;
    font-weight: 500;
  }

  .status-badge.active {
    background-color: #28a745;
    color: white;
  }

  .status-badge.inactive {
    background-color: #dc3545;
    color: white;
  }

  .inactive-user {
    opacity: 0.6;
    background-color: #f8f9fa;
  }

  .success-message {
    color: #155724;
    background-color: #d4edda;
    border: 1px solid #c3e6cb;
    padding: 10px;
    border-radius: 4px;
    margin-bottom: 15px;
    font-size: 14px;
  }
  </style>