<template>
  <div class="dashboard-layout">
    <DashBoardSidebar />
    <div class="main-content">
      <DashBoardTopbar />
      <div class="schedule-content">
        <div class="header">
          <div class="user-info">
            <div class="info-row">
              <span class="label">ID Number:</span>
              <span class="value">{{ user.idNumber || '12345678' }}</span>
            </div>
            <div class="info-row">
              <span class="label">Name:</span>
              <span class="value">{{ user.name || 'System Administrator' }}</span>
            </div>
            <div class="info-row">
              <span class="label">Classification:</span>
              <span class="value">{{ user.classification || 'System Administrator' }}</span>
            </div>
            <p class="current-date">{{ weekDateRange }}</p>
          </div>
        </div>

        <div class="schedule-actions">
          <div class="week-navigation">
            <button class="nav-btn" @click="previousWeek">
              <i class="pi pi-angle-left"></i>
            </button>
            <button class="nav-btn" @click="nextWeek">
              <i class="pi pi-angle-right"></i>
            </button>
          </div>
          <button class="btn-action" @click="downloadSchedule">
            <i class="fas fa-download"></i>
            Download Schedule
          </button>
        </div>

        <div class="schedule-container">
          <div class="schedule-card">
            <div class="schedule-header">
              <h2>Current Schedule</h2>
              <div class="lab-navigation">
                <select class="lab-dropdown" v-model="selectedLab">
                  <option v-for="lab in laboratories" :key="lab" :value="lab">
                    {{ lab }}
                  </option>
                </select>
              </div>
            </div>
            
            <div class="schedule-table">
              <table>
                <thead>
                  <tr>
                    <th>Time</th>
                    <th v-for="(day, index) in weekDays" :key="day.name">
                      <div class="day-header">
                        <span class="day-name">{{ day.name }}</span>
                        <span class="day-date">{{ day.date }}</span>
                      </div>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="time in displayTimeSlots" :key="time">
                    <td class="time-slot">{{ time }}</td>
                    <td v-for="day in weekDays" 
                        :key="day.name" 
                        class="schedule-slot">
                      <div 
                        v-if="isTimeSlotWithinSchedule(day.name, time)"
                        class="schedule-item" 
                        :style="getScheduleStyle(day.name, time)"
                      >
                        <div 
                          v-if="isScheduleStart(day.name, time)" 
                          class="schedule-item-content"
                        >
                          <div class="schedule-title">{{ getScheduleTitle(day.name, time) }}</div>
                          <div class="schedule-time">{{ getScheduleTime(day.name, time) }}</div>
                          <div class="schedule-details">{{ getScheduleDetails(day.name, time) }}</div>
                        </div>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import DashBoardSidebarSysAd from '../../components/DashBoardSidebarSysAd.vue'
import DashBoardTopbar from '../../components/DashBoardTopbar.vue'
import { userAPI, labRoomAPI } from '../../services/api.js'
import axios from 'axios'

export default {
  name: 'ScheduleSysAd',
  components: {
    DashBoardSidebar: DashBoardSidebarSysAd,
    DashBoardTopbar
  },
  data() {
    return {
      user: {
        idNumber: '',
        name: '',
        classification: ''
      },
      selectedLab: 'L201',
      laboratories: [], // Will be populated from database
      displayTimeSlots: [
        '7:30 AM', '8:00 AM', '8:30 AM', '9:00 AM', '9:30 AM', 
        '10:00 AM', '10:30 AM', '11:00 AM', '11:30 AM', '12:00 PM',
        '12:30 PM', '1:00 PM', '1:30 PM', '2:00 PM', '2:30 PM',
        '3:00 PM', '3:30 PM', '4:00 PM', '4:30 PM', '5:00 PM',
        '5:30 PM', '6:00 PM', '6:30 PM', '7:00 PM', '7:30 PM',
        '8:00 PM'
      ],
      currentWeekStart: new Date(),
      weekDays: [],
      schedules: []
    }
  },
  created() {
    this.fetchLabRooms();
    this.getUserInfo();
    this.loadSchedules();
  },
  watch: {
    currentWeekStart: {
      handler() {
        this.weekDays = this.getWeekDays();
      },
      immediate: true
    },
    selectedLab: {
      handler() {
        this.loadSchedules();
      }
    }
  },
  computed: {
    weekDateRange() {
      const days = this.getWeekDays();
      const firstDay = days[0].date;
      const lastDay = days[days.length - 1].date;
      const [firstMonth, firstDate] = firstDay.split(' ');
      const [lastMonth, lastDate] = lastDay.split(' ');
      
      // If same month, show only once
      if (firstMonth === lastMonth) {
        return `${firstMonth} ${firstDate} - ${lastDate}, 2025`;
      }
      return `${firstMonth} ${firstDate} - ${lastMonth} ${lastDate}, 2025`;
    }
  },
  methods: {
    async fetchLabRooms() {
      try {
        // Fetch lab rooms from API
        const response = await labRoomAPI.getAll();
        console.log('Lab rooms API response:', response.data);
        
        if (response.data && Array.isArray(response.data)) {
          // Mapping lab room data to get room identifiers
          this.laboratories = response.data.map(lab => lab.name);
          
          // Set default selected lab if available, otherwise keep current
          if (this.laboratories.length > 0 && !this.laboratories.includes(this.selectedLab)) {
            this.selectedLab = this.laboratories[0];
          }
          
          console.log('Loaded lab rooms from API:', this.laboratories);
        } else {
          console.error('Invalid lab rooms data format:', response.data);
          this.laboratories = [];
        }
      } catch (error) {
        console.error('Error fetching lab rooms from API:', error);
        this.laboratories = [];
      }
    },
    
    async loadSchedules() {
      try {
        this.schedules = []; // Initialize as empty array
        
        // Fetch schedules via API
        const token = sessionStorage.getItem('token') || localStorage.getItem('token');
        if (!token) {
          console.error('No token found, redirecting to login');
          this.$router.push('/login');
          return;
        }
        
        const response = await axios.get(`http://localhost:8000/api/schedules/lab/${this.selectedLab}`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        console.log('Schedule API response:', response.data);
        
        if (response.data && Array.isArray(response.data.schedules)) {
          this.schedules = response.data.schedules;
          console.log('Loaded schedules for lab ' + this.selectedLab + ':', this.schedules.length);
        } else {
          console.error('Invalid schedule data format:', response.data);
        }
      } catch (error) {
        console.error('Error loading schedules from API:', error);
        this.schedules = []; // Reset schedules on error
      }
    },
    
    async getUserInfo() {
      try {
        // Get user data from API
        const response = await userAPI.getCurrentUser();
        console.log('User API response:', response.data);
        
        if (response.data) {
          this.user.name = response.data.full_name || 'System Administrator';
          this.user.idNumber = response.data.id || '12345678';
          this.user.classification = response.data.role || 'System Administrator';
          console.log('User info loaded from API:', this.user);
        } else {
          console.error('Invalid user data format:', response.data);
          this.resetUserInfo();
        }
      } catch (error) {
        console.error('Error fetching user info from API:', error);
        this.resetUserInfo();
      }
    },
    
    resetUserInfo() {
      // Reset user info to blank state when API fails
      this.user.name = 'Error';
      this.user.idNumber = 'Error';
      this.user.classification = 'Error';
    },
    
    previousWeek() {
      const newDate = new Date(this.currentWeekStart);
      newDate.setDate(newDate.getDate() - 7);
      this.currentWeekStart = newDate;
    },
    
    nextWeek() {
      const newDate = new Date(this.currentWeekStart);
      newDate.setDate(newDate.getDate() + 7);
      this.currentWeekStart = newDate;
    },
    
    getWeekDays() {
      const days = [];
      const monday = new Date(this.currentWeekStart);
      // Adjust to Monday of the week
      const dayOfWeek = monday.getDay();
      const diff = monday.getDate() - dayOfWeek + (dayOfWeek === 0 ? -6 : 1);
      monday.setDate(diff);

      // Include Saturday (6 days instead of 5)
      for (let i = 0; i < 6; i++) {
        const date = new Date(monday);
        date.setDate(monday.getDate() + i);
        days.push({
          name: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'][i],
          date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
        });
      }
      return days;
    },
    
    isTimeSlotWithinSchedule(dayName, timeSlot) {
      if (!this.schedules || this.schedules.length === 0) {
        return false;
      }
      
      const timeSlotMinutes = this.convertTimeToMinutes(timeSlot);
      
      return this.schedules.some(schedule => {
        // Check if the schedule is for the current lab and day (including Saturday)
        if (schedule.labRoom !== this.selectedLab || schedule.day !== dayName) {
          return false;
        }
        
        const startMinutes = this.convertTimeToMinutes(schedule.startTime);
        const endMinutes = this.convertTimeToMinutes(schedule.endTime);
        
        // Check if the time slot is within the schedule's time range
        return timeSlotMinutes >= startMinutes && timeSlotMinutes < endMinutes;
      });
    },
    
    isScheduleStart(dayName, timeSlot) {
      if (!this.schedules || this.schedules.length === 0) {
        return false;
      }
      
      const timeSlotMinutes = this.convertTimeToMinutes(timeSlot);
      
      return this.schedules.some(schedule => {
        // Check if the schedule is for the current lab and day (including Saturday)
        if (schedule.labRoom !== this.selectedLab || schedule.day !== dayName) {
          return false;
        }
        
        const startMinutes = this.convertTimeToMinutes(schedule.startTime);
        return timeSlotMinutes === startMinutes;
      });
    },
    
    getScheduleStyle(dayName, timeSlot) {
      const schedule = this.schedules.find(s => {
        if (s.labRoom !== this.selectedLab || s.day !== dayName) {
          return false;
        }
        
        const slotMinutes = this.convertTimeToMinutes(timeSlot);
        const startMinutes = this.convertTimeToMinutes(s.startTime);
        const endMinutes = this.convertTimeToMinutes(s.endTime);
        
        return slotMinutes >= startMinutes && slotMinutes < endMinutes;
      });
      
      if (!schedule) return {};
      
      // Use a slightly different shade for Saturday schedules
      if (dayName === 'Saturday') {
        return {
          backgroundColor: schedule.color ? this.adjustColor(schedule.color, -20) : '#C62F4D',
        };
      }
      
      return {
        backgroundColor: schedule.color || '#DD385A',
      };
    },
    
    // Helper method to adjust color brightness
    adjustColor(color, amount) {
      // Remove the # if it's there
      color = color.replace('#', '');
      
      // Parse the color to RGB
      let r = parseInt(color.substring(0, 2), 16);
      let g = parseInt(color.substring(2, 4), 16);
      let b = parseInt(color.substring(4, 6), 16);
      
      // Adjust RGB values
      r = Math.max(0, Math.min(255, r + amount));
      g = Math.max(0, Math.min(255, g + amount));
      b = Math.max(0, Math.min(255, b + amount));
      
      // Convert back to hex
      return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
    },
    
    getScheduleTitle(dayName, timeSlot) {
      const schedule = this.schedules.find(s => {
        if (s.labRoom !== this.selectedLab || s.day !== dayName) {
          return false;
        }
        
        const slotMinutes = this.convertTimeToMinutes(timeSlot);
        const startMinutes = this.convertTimeToMinutes(s.startTime);
        
        return slotMinutes === startMinutes;
      });
      
      if (!schedule) return '';
      return schedule.title || '';
    },
    
    getScheduleTime(dayName, timeSlot) {
      const schedule = this.schedules.find(s => {
        if (s.labRoom !== this.selectedLab || s.day !== dayName) {
          return false;
        }
        
        const slotMinutes = this.convertTimeToMinutes(timeSlot);
        const startMinutes = this.convertTimeToMinutes(s.startTime);
        
        return slotMinutes === startMinutes;
      });
      
      if (!schedule) return '';
      return `${schedule.startTime} - ${schedule.endTime}`;
    },
    
    getScheduleDetails(dayName, timeSlot) {
      const schedule = this.schedules.find(s => {
        if (s.labRoom !== this.selectedLab || s.day !== dayName) {
          return false;
        }
        
        const slotMinutes = this.convertTimeToMinutes(timeSlot);
        const startMinutes = this.convertTimeToMinutes(s.startTime);
        
        return slotMinutes === startMinutes;
      });
      
      if (!schedule) return '';
      return `${schedule.courseName}\n${schedule.section}\n${schedule.instructorName}`;
    },
    
    convertTimeToMinutes(timeStr) {
      const [time, period] = timeStr.split(' ');
      let [hours, minutes] = time.split(':').map(Number);
      
      if (period === 'PM' && hours !== 12) {
        hours += 12;
      } else if (period === 'AM' && hours === 12) {
        hours = 0;
      }
      
      return hours * 60 + minutes;
    },
    
    downloadSchedule() {
      // Implement schedule download functionality
      console.log('Downloading schedule...');
    }
  }
}
</script>

<style scoped>
.dashboard-layout {
  display: flex;
  width: 100vw;
  height: 100vh;
  background-color: #f5f5f5;
  overflow: hidden;
  font-family: 'Inter', sans-serif;
}

.main-content {
  flex: 1;
  margin-left: 70px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.schedule-content {
  padding: 1.5rem;
  height: calc(100vh - 64px);
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: #DD385A rgba(221, 56, 90, 0.1);
}

.schedule-content::-webkit-scrollbar {
  width: 8px;
}

.schedule-content::-webkit-scrollbar-track {
  background: rgba(221, 56, 90, 0.1);
  border-radius: 4px;
}

.schedule-content::-webkit-scrollbar-thumb {
  background-color: #DD385A;
  border-radius: 4px;
}

.header {
  margin-bottom: 1rem;
}

.user-info {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.info-row {
  display: flex;
  gap: 1rem;
  margin-bottom: 0.75rem;
  align-items: center;
}

.info-row:last-of-type {
  margin-bottom: 1rem;
}

.label {
  color: #666;
  font-size: 0.9rem;
  min-width: 100px;
}

.value {
  color: #333;
  font-weight: 500;
  font-size: 0.95rem;
}

.current-date {
  color: #DD385A;
  font-size: 0.9rem;
  margin: 0;
  padding-top: 0.5rem;
  border-top: 1px solid #eee;
}

.schedule-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.week-navigation, .lab-navigation {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.lab-navigation {
  margin-left: auto;
}

.nav-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 6px;
  background-color: #DD385A;
  color: white;
  cursor: pointer;
  transition: all 0.2s ease;
}

.nav-btn:hover {
  background-color: #c62f4d;
  transform: translateY(-1px);
}

.lab-indicator {
  font-size: 1.1rem;
  font-weight: 500;
  color: #333;
  padding: 0 0.5rem;
}

.schedule-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.schedule-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.schedule-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.schedule-header h2 {
  color: #333;
  margin: 0;
  font-size: 1.5rem;
  font-weight: 500;
}

.btn-action {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  border: none;
  border-radius: 8px;
  background-color: #DD385A;
  color: white;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-action:hover {
  background-color: #c62f4d;
  transform: translateY(-1px);
}

.btn-action i {
  font-size: 1rem;
}

.schedule-table {
  flex: 1;
  overflow: auto;
  scrollbar-width: thin;
  scrollbar-color: #DD385A rgba(221, 56, 90, 0.1);
  position: relative;
  height: calc(100vh - 200px);
}

.schedule-table::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.schedule-table::-webkit-scrollbar-track {
  background: rgba(221, 56, 90, 0.1);
  border-radius: 4px;
}

.schedule-table::-webkit-scrollbar-thumb {
  background-color: #DD385A;
  border-radius: 4px;
}

table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  min-width: 800px;
}

th, td {
  border: 1px solid #eee;
  padding: 1rem;
  text-align: center;
  background-color: white;
  height: 60px;
}

th {
  background-color: #DD385A;
  color: white;
  font-weight: 500;
  position: sticky;
  top: 0;
  z-index: 10;
}

th:first-child {
  left: 0;
  z-index: 20;
}

td:first-child {
  position: sticky;
  left: 0;
  z-index: 5;
  background-color: rgba(221, 56, 90, 0.05);
  color: #DD385A;
  font-weight: 500;
}

.day-header {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  align-items: center;
  position: relative;
}

/* Add shadow effects for sticky elements */
th::after, td:first-child::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  width: 4px;
  pointer-events: none;
  box-shadow: inset -2px 0 4px -2px rgba(0, 0, 0, 0.1);
}

th:first-child::after {
  box-shadow: none;
}

/* Add bottom shadow for header row */
thead::after {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 4px;
  pointer-events: none;
  box-shadow: inset 0 -2px 4px -2px rgba(0, 0, 0, 0.1);
}

.day-name {
  font-size: 1rem;
}

.day-date {
  font-size: 0.8rem;
  opacity: 0.9;
}

.time-slot {
  color: #DD385A;
  font-weight: 500;
  background-color: rgba(221, 56, 90, 0.05);
}

.schedule-slot {
  background-color: white;
  transition: background-color 0.2s ease;
  position: relative;
}

.schedule-slot:hover {
  background-color: rgba(221, 56, 90, 0.05);
}

.schedule-item {
  background-color: #DD385A;
  color: white;
  border-radius: 4px;
  position: absolute;
  left: 5px;
  right: 5px;
  top: 5px;
  bottom: 5px;
  z-index: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  padding: 5px;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease;
}

.schedule-item:hover {
  transform: scale(1.02);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.schedule-item-content {
  display: flex;
  flex-direction: column;
  height: 100%;
  justify-content: center;
  align-items: center;
}

.schedule-title {
  font-weight: 600;
  font-size: 0.9rem;
  margin-bottom: 2px;
}

.schedule-time {
  font-size: 0.75rem;
  opacity: 0.9;
  margin-bottom: 2px;
}

.schedule-details {
  font-size: 0.75rem;
  opacity: 0.9;
  white-space: pre-line;
}

.lab-dropdown {
  padding: 0.5rem;
  border-radius: 6px;
  border: 1px solid #ddd;
  background-color: white;
  color: #333;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  outline: none;
  min-width: 120px;
}

.lab-dropdown:hover, .lab-dropdown:focus {
  border-color: #DD385A;
  box-shadow: 0 0 0 2px rgba(221, 56, 90, 0.1);
}

.lab-dropdown option {
  padding: 0.5rem;
  font-size: 0.9rem;
}
</style>