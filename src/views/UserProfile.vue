// Users.vue
<template>
  <div class="dashboard-layout">
    <DashBoardSidebar />
    <div class="main-content">
      <h1>Users</h1>
    </div>
  </div>
</template>

<script>
import DashBoardSidebar from '../components/DashBoardSidebar.vue'

export default {
  name: 'Users',
  components: {
    DashBoardSidebar
  }
}
</script>

<style scoped>
.dashboard-layout {
  display: flex;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.main-content {
  flex: 1;
  margin-left: 70px;
  padding: 2rem;
}

h1 {
  color: #333;
}
</style>