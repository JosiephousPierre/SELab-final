// About.vue
<template>
  <div class="main-content">
    <div class="about">
      <div class="content-section">
        <h1>What is the Computer Laboratory Scheduling System?</h1>
        <p class="description">
          The Computer Laboratory Scheduling System is a web-based platform designed to streamline the scheduling and 
          management of computer laboratories at the University of the Immaculate Conception (UIC). It automates the scheduling 
          process, detects conflicts in real-time, and provides centralized access to up-to-date schedules, ensuring efficient 
          coordination among faculty, staff, and administrators.
        </p>

        <div class="users-section">
          <h2>Who can use this system?</h2>
          
          <div class="user-role">
            <h3>CCS Academic Coordinator</h3>
            <p>Creates and manages schedules.</p>
          </div>

          <div class="user-role">
            <h3>CCS Dean</h3>
            <p>Reviews and approves schedules.</p>
          </div>

          <div class="user-role">
            <h3>Faculty/Staff & Students</h3>
            <p>View assigned schedules and receive notifications.</p>
          </div>
        </div>
      </div>

      <div class="illustration-section">
        <img src="../assets/about-page-design.svg" alt="Scheduling Illustration" class="about-image" />
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'About'
}
</script>

<style scoped>
.about {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 4rem;
  max-width: 1400px;
  margin: 0 auto;
  gap: 4rem;
}

.content-section {
  flex: 1;
  max-width: 600px;
}

h1 {
  font-size: clamp(2rem, 4vw, 2.5rem);
  color: #DD385A;
  margin-bottom: 1.5rem;
  line-height: 1.2;
}

.description {
  font-size: 1.1rem;
  color: #666;
  line-height: 1.6;
  margin-bottom: 3rem;
}

.users-section {
  margin-top: 2rem;
}

.users-section h2 {
  font-size: 1.8rem;
  color: #DD385A;
  margin-bottom: 2rem;
}

.user-role {
  margin-bottom: 1.5rem;
}

.user-role h3 {
  font-size: 1.2rem;
  color: #333;
  margin-bottom: 0.5rem;
}

.user-role p {
  color: #666;
  line-height: 1.4;
}

.illustration-section {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  max-width: 45%;
}

.about-image {
  width: 100%;
  max-width: 500px;
  height: auto;
}

@media (max-width: 1024px) {
  .about {
    padding: 3rem;
    gap: 3rem;
  }

  .illustration-section {
    max-width: 50%;
  }
}

@media (max-width: 768px) {
  .about {
    flex-direction: column;
    padding: 2rem;
    text-align: center;
  }

  .content-section {
    max-width: 100%;
  }

  .illustration-section {
    max-width: 70%;
    margin: 0 auto;
  }

  .user-role {
    text-align: center;
  }
}

@media (max-width: 480px) {
  .about {
    padding: 1.5rem;
  }

  .illustration-section {
    max-width: 90%;
  }

  h1 {
    font-size: 1.8rem;
  }

  .users-section h2 {
    font-size: 1.5rem;
  }
}
</style>