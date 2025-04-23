<template>
  <div class="dashboard-layout">
    <DashBoardSidebarSysAd />
    <div class="main-content">
      <DashBoardTopbar />
      <div class="dashboard-content">
        <div class="header">
          <h1>Account Management</h1>
        </div>

        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>

        <div class="filters-section">
          <div class="search-box">
            <input type="text" placeholder="Search..." v-model="searchQuery">
            <i class="fas fa-search"></i>
          </div>
          
          <div class="filter-dropdown">
            <div class="sort-control">
              <span>Sort: </span>
              <select v-model="sortOption">
                <option value="newest">Newest</option>
                <option value="oldest">Oldest</option>
                <option value="name">Name</option>
                <option value="id">ID</option>
                <option value="role">Role</option>
              </select>
            </div>
          </div>
        </div>

        <div v-if="isLoading" class="loading-indicator">
          Loading accounts...
        </div>

        <div v-else-if="pendingAccounts.length === 0" class="no-accounts-message">
          No pending accounts found. All accounts have been approved.
        </div>

        <div v-else class="accounts-table">
          <div class="table-container">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Full Name</th>
                  <th>Email</th>
                  <th>Role</th>
                  <th>Date Created</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="account in filteredAccounts" :key="account.id">
                  <td>{{ account.id }}</td>
                  <td>{{ account.full_name }}</td>
                  <td>{{ account.email }}</td>
                  <td>{{ account.role }}</td>
                  <td>{{ formatDate(account.date_created) }}</td>
                  <td class="action-buttons">
                    <button class="approve-button" @click="approveAccount(account)">Approve</button>
                    <button class="reject-button" @click="rejectAccount(account)">Reject</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import DashBoardSidebarSysAd from '../../components/DashBoardSidebarSysAd.vue'
import DashBoardTopbar from '../../components/DashBoardTopbar.vue'

export default {
  name: 'AccountManagement',
  components: {
    DashBoardSidebarSysAd,
    DashBoardTopbar
  },
  data() {
    return {
      searchQuery: '',
      sortOption: 'newest',
      pendingAccounts: [],
      isLoading: false,
      errorMessage: null,
      accountCheckInterval: null
    }
  },
  created() {
    this.fetchPendingAccounts();
  },
  mounted() {
    // Add event listener for route changes
    window.addEventListener('focus', this.checkForNewAccounts);
    
    // Set up a timer to check for pending accounts periodically
    this.accountCheckInterval = setInterval(() => {
      console.log('Periodic check for pending accounts');
      this.fetchPendingAccounts();
    }, 5000); // Check every 5 seconds
  },
  beforeUnmount() {
    // Remove event listener when component is destroyed
    window.removeEventListener('focus', this.checkForNewAccounts);
    
    // Clear the interval when component is destroyed
    if (this.accountCheckInterval) {
      clearInterval(this.accountCheckInterval);
    }
  },
  computed: {
    filteredAccounts() {
      // Filter by search query
      let accounts = this.pendingAccounts.filter(account => {
        const matchesSearch = !this.searchQuery || 
          account.full_name.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
          account.email.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
          account.role.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
          account.id.includes(this.searchQuery)
        
        return matchesSearch
      })
      
      // Sort accounts
      accounts = [...accounts].sort((a, b) => {
        switch(this.sortOption) {
          case 'newest':
            return new Date(b.date_created) - new Date(a.date_created)
          case 'oldest':
            return new Date(a.date_created) - new Date(b.date_created)
          case 'name':
            return a.full_name.localeCompare(b.full_name)
          case 'id':
            return a.id.localeCompare(b.id)
          case 'role':
            return a.role.localeCompare(b.role)
          default:
            return 0
        }
      })
      
      return accounts
    }
  },
  methods: {
    checkForNewAccounts() {
      console.log('Checking for new accounts');
      this.fetchPendingAccounts();
    },
    async fetchPendingAccounts() {
      this.isLoading = true;
      this.errorMessage = null;
      
      try {
        // Get token from sessionStorage first, fall back to localStorage if needed
        const token = sessionStorage.getItem('token') || localStorage.getItem('token');
        const userStr = sessionStorage.getItem('user') || localStorage.getItem('user');
        const user = userStr ? JSON.parse(userStr) : {};
        
        console.log('Current user:', user);
        console.log('Token:', token);
        
        if (!token) {
          this.errorMessage = 'Not authenticated. Please log in again.';
          this.$router.push('/login');
          return;
        }
        
        // Try to fetch from API
        try {
          const response = await fetch('http://localhost:8000/api/users/pending-approval', {
            method: 'GET',
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });
          
          if (!response.ok) {
            if (response.status === 403) {
              console.error('Permission denied when fetching pending accounts');
              this.errorMessage = 'You do not have permission to view pending accounts.';
              this.pendingAccounts = [];
            } else {
              const data = await response.json();
              throw new Error(data.detail || 'Failed to fetch pending accounts');
            }
          } else {
            const data = await response.json();
            this.pendingAccounts = data.users;
            console.log('Fetched pending accounts from API:', data.users);
          }
        } catch (error) {
          console.error('Error fetching from API:', error);
          this.errorMessage = `Error: ${error.message}`;
          this.pendingAccounts = [];
        }
      } catch (error) {
        this.errorMessage = error.message;
        console.error('Error in fetchPendingAccounts:', error);
        this.pendingAccounts = [];
      } finally {
        this.isLoading = false;
      }
    },
    async approveAccount(account) {
      try {
        // Get token from sessionStorage first, fall back to localStorage if needed
        const token = sessionStorage.getItem('token') || localStorage.getItem('token');
        
        if (!token) {
          this.$router.push('/login');
          return;
        }
        
        // For real backend, make API call
        const response = await fetch(`http://localhost:8000/api/users/${account.id}/approve`, {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            is_approved: 1,
            requires_approval: 0
          })
        });
        
        if (!response.ok) {
          const data = await response.json();
          throw new Error(data.detail || 'Failed to approve account');
        }
        
        // Remove from pending accounts
        this.pendingAccounts = this.pendingAccounts.filter(a => a.id !== account.id);
        
        // Manually trigger the instructor sync for non-student roles
        if (account.role !== 'Student') {
          try {
            const syncResponse = await fetch('http://127.0.0.1:8000/api/instructors/sync', {
              method: 'POST',
              headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
              }
            });
            
            if (!syncResponse.ok) {
              console.error('Failed to sync instructors after approval');
            } else {
              console.log('Successfully synced instructors');
            }
          } catch (syncError) {
            console.error('Error syncing instructors:', syncError);
          }
        }
        
        // Show notification
        alert(`Account for ${account.full_name} has been approved. The user can now log in and will appear in User Management.`);
      } catch (error) {
        alert(`Error: ${error.message}`);
        console.error('Error approving account:', error);
      }
    },
    async rejectAccount(account) {
      try {
        // Get token from sessionStorage first, fall back to localStorage if needed
        const token = sessionStorage.getItem('token') || localStorage.getItem('token');
        
        if (!token) {
          this.$router.push('/login');
          return;
        }
        
        // Make API call to reject the account
        const response = await fetch(`http://localhost:8000/api/users/${account.id}/reject`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        
        if (!response.ok) {
          const data = await response.json();
          throw new Error(data.detail || 'Failed to reject account');
        }
        
        // Remove from pending accounts
        this.pendingAccounts = this.pendingAccounts.filter(a => a.id !== account.id);
        
        // Show notification
        alert(`Account for ${account.full_name} has been rejected.`);
      } catch (error) {
        alert(`Error: ${error.message}`);
        console.error('Error rejecting account:', error);
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
    },
    formatDate(dateString) {
      if (!dateString) return 'N/A';
      
      try {
        const date = new Date(dateString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
      } catch (e) {
        return dateString;
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
  overflow-x: hidden;
}

.dashboard-content {
  padding: 20px 30px;
}

.header {
  margin-bottom: 20px;
}

.header h1 {
  font-size: 24px;
  color: #e91e63;
  font-weight: 600;
  margin: 0;
}

.filters-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.search-box {
  position: relative;
  width: 300px;
}

.search-box input {
  width: 100%;
  padding: 10px 15px;
  padding-right: 40px;
  border-radius: 50px;
  border: 1px solid #e0e0e0;
  background: #f9f9f9;
}

.search-box i {
  position: absolute;
  right: 15px;
  top: 50%;
  transform: translateY(-50%);
  color: #888;
}

.filter-dropdown {
  display: flex;
  gap: 10px;
}

.sort-control {
  display: flex;
  align-items: center;
  gap: 8px;
}

.sort-control select {
  padding: 8px 12px;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
  background: #f9f9f9;
  color: #333;
}

.table-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background-color: #e91e63;
  color: white;
}

th {
  padding: 15px 20px;
  text-align: left;
  font-weight: 600;
  font-size: 14px;
}

td {
  padding: 15px 20px;
  border-bottom: 1px solid #f0f0f0;
  font-size: 14px;
}

tr:last-child td {
  border-bottom: none;
}

.action-buttons {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.approve-button {
  background-color: #4CAF50;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s;
}

.approve-button:hover {
  background-color: #3e8e41;
}

.reject-button {
  background-color: #e74c3c;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s;
}

.reject-button:hover {
  background-color: #c0392b;
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

.no-accounts-message {
  text-align: center;
  padding: 30px;
  font-size: 16px;
  color: #555;
  background-color: #f9f9f9;
  border-radius: 8px;
  margin-top: 20px;
}
</style>
