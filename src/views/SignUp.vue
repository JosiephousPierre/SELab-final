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
        <div class="form-group-container">
          <div class="form-group">
            <label for="email">Email</label>
            <input 
              type="email" 
              id="email" 
              placeholder="Enter your email"
              v-model="email"
              @blur="validateEmail"
              :class="{ 'input-error': emailError }"
            >
            <span v-if="emailError" class="field-error">{{ emailError }}</span>
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
        </div>

        <div class="buttons-container">
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
      errorMessage: null,
      emailError: null
    }
  },
  methods: {
    async signup() {
      // Reset error message
      this.errorMessage = null;
      
      // Validate email domain
      this.validateEmail();
      if (this.emailError) {
        this.errorMessage = 'Only UIC email is valid';
        return;
      }
      
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
    },
    validateEmail() {
      // Clear previous error
      this.emailError = null;
      
      // Skip validation if email is empty (will be caught by general validation)
      if (!this.email) return;
      
      // Check if it has @ symbol
      if (this.email.indexOf('@') === -1) {
        this.emailError = 'Please enter a valid email address';
        return;
      }
      
      // Extract domain and validate
      const domain = this.email.split('@')[1];
      if (domain !== 'uic.edu.ph') {
        this.emailError = 'Only UIC email is valid';
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
  min-height: 90vh;
  background-color: #f5f5f5;
  padding: 1rem;
}

.signup-card {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 480px;
  position: relative;
  overflow-y: auto;
  max-height: 90vh;
}

.logo-section {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  margin-bottom: 1rem;
}

.logo {
  height: 45px;
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
  font-size: 1.7rem;
  margin-bottom: 1rem;
}

.signup-form {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.form-group-container {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

label {
  color: #666;
  font-size: 0.9rem;
}

input {
  padding: 0.6rem;
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
  padding: 0.6rem;
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

.buttons-container {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.signup-button {
  background-color: #DD385A;
  color: white;
  border: none;
  padding: 0.7rem;
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

.input-error {
  border-color: #e74c3c;
}

.field-error {
  color: #e74c3c;
  font-size: 0.8rem;
  margin-top: 0.25rem;
}

/* Media query styling for larger screens */
@media (min-width: 768px) {
  .signup-card {
    max-width: 620px;
    padding: 2rem 2.5rem;
  }
  
  .form-group-container {
    flex-direction: row;
    flex-wrap: wrap;
    gap: 1rem;
  }
  
  .form-group {
    flex: 1 1 calc(50% - 0.5rem);
    min-width: 200px;
  }
  
  /* Full width items */
  .buttons-container {
    width: 100%;
  }
}
</style>
