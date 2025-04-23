// Topbar.vue
<template>
  <div class="topbar">
    <div class="logo-section">
      <img src="../assets/uic-logo-3.svg" alt="UIC Logo" class="icon" />
      <img src="../assets/CCS-logo.svg" alt="CCS Logo" class="icon" />
    </div>
    <nav class="nav-links">
      <router-link to="/" class="nav-link">
        <i class="fas fa-home"></i>
        Home
      </router-link>
      <router-link to="/about" class="nav-link">
        <i class="fas fa-info-circle"></i>
        About
      </router-link>
      <router-link to="/features" class="nav-link">
        <i class="fas fa-list"></i>
        Features
      </router-link>
      <router-link to="/login" class="nav-link login">
        <i class="fas fa-user"></i>
        Log In
      </router-link>
    </nav>
  </div>
</template>

<script>
export default {
  name: 'Topbar'
}
</script>

<style scoped>
.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background-color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.icon {
  height: 40px;
  width: auto;
}

.nav-links {
  display: flex;
  gap: 2rem;
  align-items: center;
}

.nav-link {
  text-decoration: none;
  color: #333;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: color 0.3s ease;
}

.nav-link:hover {
  color: #E91E63;
}

.nav-link i {
  font-size: 1.1rem;
}

.login {
  padding: 0.5rem 1.5rem;
  background-color: #E91E63;
  color: white;
  border-radius: 4px;
  transition: background-color 0.3s ease;
}

.login:hover {
  background-color: #D81B60;
  color: white;
}
</style>