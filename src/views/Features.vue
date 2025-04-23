// Features.vue
<template>
  <div class="main-content">
    <div class="features">
      <div class="content-wrapper">
        <div class="features-grid">
          <div class="feature-card">
            <h2 class="feature-title">Academic Coordinator</h2>
            <ul>
              <li>
                <i class="fas fa-calendar-plus feature-icon"></i>
                Scheduling Creation and Assignment
              </li>
              <li>
                <i class="fas fa-exclamation-triangle feature-icon"></i>
                Conflict Detection
              </li>
              <li>
                <i class="fas fa-chart-line feature-icon"></i>
                Audit Tracking
              </li>
            </ul>
          </div>

          <div class="feature-card">
            <h2 class="feature-title">All Users</h2>
            <ul>
              <li>
                <i class="fas fa-th-large feature-icon"></i>
                Centralized Dashboard
              </li>
              <li>
                <i class="fas fa-search feature-icon"></i>
                Search and Filter
              </li>
              <li>
                <i class="fas fa-bell feature-icon"></i>
                Receive Notifications
              </li>
            </ul>
          </div>

          <div class="feature-card">
            <h2 class="feature-title">Dean</h2>
            <ul>
              <li>
                <i class="fas fa-check-circle feature-icon"></i>
                Schedule Review and Approval
              </li>
              <li>
                <i class="fas fa-chart-bar feature-icon"></i>
                Activity Monitoring
              </li>
            </ul>
          </div>

          <div class="feature-card">
            <h2 class="feature-title">Faculty/Staff & Students</h2>
            <ul>
              <li>
                <i class="fas fa-calendar-alt feature-icon"></i>
                View Assigned Schedules
              </li>
            </ul>
          </div>

          <div class="feature-card">
            <h2 class="feature-title">System Administrator</h2>
            <ul>
              <li>
                <i class="fas fa-users-cog feature-icon"></i>
                User Management
              </li>
              <li>
                <i class="fas fa-shield-alt feature-icon"></i>
                Access Control
              </li>
            </ul>
          </div>
        </div>
      </div>

      <div class="illustration-section">
        <img src="../assets/features-page-image.svg" alt="Features Illustration" class="features-image" />
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Features'
}
</script>

<style scoped>
.main-content {
  height: 100vh;
  overflow-y: auto;
  background-color: white;
}

.features {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 4rem;
  max-width: 1400px;
  margin: 0 auto;
  gap: 4rem;
  min-height: min-content;
}

.content-wrapper {
  flex: 1;
  max-width: 600px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
}

.feature-card {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(221, 56, 90, 0.1);
}

.feature-icon {
  color: #DD385A;
  font-size: 1.2rem;
  width: 24px;
}

.feature-title {
  color: #DD385A;
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
}

.feature-card ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.feature-card li {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
  color: #333;
  font-size: 1rem;
}

.illustration-section {
  flex: 1;
  position: sticky;
  top: 4rem;
}

.features-image {
  max-width: 100%;
  height: auto;
}

@media (max-width: 1024px) {
  .features {
    flex-direction: column;
    padding: 2rem;
  }

  .illustration-section {
    position: static;
    margin-top: 2rem;
  }

  .content-wrapper {
    max-width: none;
  }
}
</style>