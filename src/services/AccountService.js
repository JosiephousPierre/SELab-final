import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

class AccountService {
  // Get count of pending accounts that need approval
  async getPendingAccountsCount() {
    const token = sessionStorage.getItem('token') || localStorage.getItem('token');
    
    try {
      if (!token) {
        console.error('No auth token found in storage');
        return 0;
      }
      
      const response = await axios.get(`${API_URL}/users/pending-approval`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      return response.data.users ? response.data.users.length : 0;
    } catch (error) {
      console.error('Error fetching pending accounts count:', error);
      return 0;
    }
  }
}

export default new AccountService(); 