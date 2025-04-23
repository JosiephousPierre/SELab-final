// SignUp.vue
<template>
  <div class="signup-container">
    <div class="signup-card">
      <div class="logo-section">
        <img src="../assets/uic-logo-3.svg" alt="UIC Logo" class="logo" />
        <img src="../assets/CCS-logo.svg" alt="CCS Logo" class="logo" />
      </div>

      <router-link to="/" class="back-link">
        <i class="fas fa-chevron-left"></i>
      </router-link>

      <h1>Sign Up</h1>

      <div v-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </div>

      <div class="signup-form">
        <div class="form-group">
          <label for="email">Email</label>
          <input 
            type="email" 
            id="email" 
            placeholder="Enter your email"
            v-model="email"
          >
        </div>

        <div class="form-group">
          <label for="id">ID</label>
          <input 
            type="text" 
            id="id" 
            placeholder="Enter your ID"
            v-model="id"
          >
        </div>

        <div class="form-group">
          <label for="fullName">Full Name</label>
          <input 
            type="text" 
            id="fullName" 
            placeholder="Enter your full name"
            v-model="fullName"
          >
        </div>

        <div class="form-group">
          <label for="role">Role</label>
          <select id="role" v-model="selectedRole">
            <option value="" disabled selected>Select your role</option>
            <option value="Student">Student</option>
            <option value="Academic Coordinator">Academic Coordinator</option>
            <option value="Lab InCharge">Lab InCharge</option>
            <option value="Faculty/Staff">Faculty/Staff</option>
            <option value="Dean">Dean</option>
          </select>
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

        <button class="signup-button" @click="signup" :disabled="isLoading">
          {{ isLoading ? 'Signing up...' : 'Sign Up' }}
        </button>

        <div class="divider">
          <span>or</span>
        </div>

        <button class="google-button">
          <img src="../assets/Google-logo.svg" alt="Google" class="google-icon">
          Sign up with Google
        </button>

        <p class="login-link">
          Already have an account? 
          <router-link to="/login">Sign In</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SignUp',
  data() {
    return {
      selectedRole: '',
      email: '',
      id: '',
      fullName: '',
      password: '',
      isLoading: false,
      errorMessage: null
    }
  },
  methods: {
    async signup() {
      // Reset error message
      this.errorMessage = null;
      
      // Validate that all fields are filled
      if (!this.email || !this.id || !this.fullName || !this.selectedRole || !this.password) {
        this.errorMessage = 'Please fill in all fields';
        return;
      }
      
      this.isLoading = true;
      
      try {
        // Send user data to backend API
        const response = await fetch('http://localhost:8000/api/signup', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            id: this.id,
            full_name: this.fullName,
            email: this.email,
            role: this.selectedRole,
            password: this.password
          }),
        });
        
        const data = await response.json();
        
        if (!response.ok) {
          throw new Error(data.detail || 'An error occurred during sign up');
        }
        
        // Handle the successful sign up
        if (this.selectedRole !== 'Student') {
          // Non-student accounts require approval
          alert('Account created successfully! Please wait for approval by the system administrator.');
        } else {
          // Student accounts don't require approval
          alert('Sign up successful! You can now log in to your account.');
        }
        
        // Redirect to login page after successful signup
        this.$router.push('/login');
        
      } catch (error) {
        this.errorMessage = error.message;
        console.error('Error during signup:', error);
      } finally {
        this.isLoading = false;
      }
    }
  }
}
</script>

<style scoped>
.signup-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 93vh;
  background-color: #f5f5f5;
  padding: 1rem;
}

.signup-card {
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
  color: #DD385A;
  font-size: 1.8rem;
  margin-bottom: 1.5rem;
}

.signup-form {
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
  border-color: #DD385A;
}

select {
  padding: 0.7rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.9rem;
  transition: border-color 0.3s ease;
  background-color: white;
  appearance: auto;
}

select:focus {
  outline: none;
  border-color: #DD385A;
}

.signup-button {
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

.signup-button:hover {
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

.login-link {
  text-align: center;
  color: #DD385A;
  text-decoration: none;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

.login-link a {
  color: #DD385A;
  text-decoration: none;
  font-weight: 500;
}

.login-link a:hover {
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

.signup-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}
</style>
