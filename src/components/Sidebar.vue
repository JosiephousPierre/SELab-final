// Sidebar.vue
<template>
  <div class="sidebar">
    <div class="logo-section">
      <img src="../assets/Logo-100px-white.png" class="logo" alt="ClassTrack Logo" />
    </div>
    <div class="social-icons">
      <i class="pi pi-google"></i>
      <i class="pi pi-github"></i>
      <i class="pi pi-envelope"></i>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Sidebar'
}
</script>

<style scoped>
.sidebar {
  width: 80px;
  height: 100vh;
  background-color: #DD385A;
  border-right: 1px solid #eee;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem 0;
  position: fixed;
  left: 0;
  top: 0;
}

.logo-section {
  margin-bottom: 1rem;
}

.logo {
  width: 50px;
  height: auto;
}

.social-icons {
  margin-top: auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1rem 0;
}

.pi {
  font-size: 1.2rem;
  color: #ffffff;
  cursor: pointer;
  transition: color 0.3s ease;
}

.pi:hover {
  color: #E91E63;
}

@media (max-width: 768px) {
  .sidebar {
    display: none;
  }
}
</style>