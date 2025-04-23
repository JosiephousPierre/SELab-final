// Home.vue
<template>
  <div class="main-content">
    <div class="home">
      <div class="content">
        <h1>Schedule a<br>class now.</h1>
        <p>Coordinating and managing computer laboratory schedules are made easy.</p>
        <button class="get-started cta-button" @click="navigateToSignUp">Get Started</button>
      </div>
      <div class="illustration">
        <img src="../assets/LandingPageIMG.png" alt="Calendar Illustration" class="landing-image" />
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Home',
  methods: {
    navigateToSignUp() {
      this.$router.push('/signup')
    }
  }
}
</script>

<style scoped>
.nav-link.router-link-active {
  color: #DD385A;
  font-weight: 500;
}

.nav-link:hover {
  color: #DD385A;
}

.cta-button {
  background-color: #DD385A;
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 500;
  transition: background-color 0.2s;
}

.cta-button:hover {
  background-color: #c4314f;
}

.highlight {
  color: #DD385A;
}

.login-buttons {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  z-index: 100;
}

.login-btn {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1.5rem;
  background-color: #DD385A;
  color: white;
  text-decoration: none;
  border-radius: 8px;
  font-weight: 500;
  font-size: 1rem;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.login-btn.viewer-btn {
  background-color: #2C3E50;
}

.login-btn.sysad-btn {
  background-color: #1a5f7a;
}

.login-btn i {
  font-size: 1.1rem;
}
</style>