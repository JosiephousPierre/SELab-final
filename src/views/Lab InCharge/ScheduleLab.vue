<template>
  <div class="dashboard-layout" ref="scheduleComponent">
    <DashBoardSidebar />
    <div class="main-content">
      <DashBoardTopbar />
      <div class="content-wrapper">
        <div class="header">
          <h1>Schedule View</h1>
          <div class="header-actions">
            <button class="download-btn" @click="downloadSchedule">
              <i class="fas fa-download"></i>
              Download Schedule
            </button>
          </div>
        </div>

        <div class="schedule-container">
          <div class="lab-navigation">
            <button class="nav-btn" @click="previousLab">
              <i class="nav-icon"><</i>
            </button>
            <div class="lab-indicator">
              {{ selectedLab }}
            </div>
            <button class="nav-btn" @click="nextLab">
              <i class="nav-icon">></i>
            </button>
          </div>
          <div class="week-header">
            <div class="time-header">
              <div class="time-label">Time</div>
            </div>
            <div class="day-headers">
              <div class="day-header" v-for="(day, index) in weekDays" :key="index">
                <div class="day-name">{{ day.name }}</div>
                <div class="day-date">{{ day.date }}</div>
              </div>
            </div>
          </div>
          <div class="schedule-grid">
            <div class="time-column">
              <div class="time-slot" v-for="time in displayTimeSlots" :key="time">
                {{ time }}
              </div>
            </div>
            <div class="schedule-content">
              <div class="day-column" v-for="(day, dayIndex) in weekDays" :key="dayIndex">
                <div class="day-slots">
                  <div class="time-slot" v-for="(time, timeIndex) in displayTimeSlots" :key="timeIndex">
                    <div 
                      v-if="isTimeSlotWithinSchedule(day.name, time)"
                      class="schedule-item" 
                      :style="getScheduleStyle(day.name, time)"
                    >
                      <div 
                        v-if="isScheduleStart(day.name, time)" 
                        class="schedule-content"
                      >
                        <div class="schedule-title">{{ getScheduleTitle(day.name, time) }}</div>
                        <div class="schedule-time">{{ getScheduleTime(day.name, time) }}</div>
                        <div class="schedule-details">{{ getScheduleDetails(day.name, time) }}</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import DashBoardSidebar from '../../components/DashBoardSideBarLab.vue'
import DashBoardTopbar from '../../components/DashBoardTopbar.vue'

export default {
  name: 'ScheduleLab',
  components: {
    DashBoardSidebar,
    DashBoardTopbar
  },
  data() {
    return {
      selectedLab: 'L201',
      laboratories: ['L201', 'L202', 'L203', 'L204', 'L205', 'IOT'],
      displayTimeSlots: [
        '7:30 AM', '8:00 AM', '8:30 AM', '9:00 AM', '9:30 AM', 
        '10:00 AM', '10:30 AM', '11:00 AM', '11:30 AM', '12:00 PM',
        '12:30 PM', '1:00 PM', '1:30 PM', '2:00 PM', '2:30 PM',
        '3:00 PM', '3:30 PM', '4:00 PM', '4:30 PM', '5:00 PM',
        '5:30 PM', '6:00 PM', '6:30 PM', '7:00 PM', '7:30 PM',
        '8:00 PM'
      ],
      weekDays: [],
      schedules: []
    }
  },
  created() {
    this.generateWeekDays()
    this.loadSchedules()
  },
  methods: {
    loadSchedules() {
      try {
        const savedSchedules = localStorage.getItem('labSchedules')
        if (savedSchedules) {
          const schedules = JSON.parse(savedSchedules)
          this.schedules = schedules.filter(schedule => schedule.labRoom === this.selectedLab)
        }
      } catch (error) {
        console.error('Error loading schedules:', error)
        this.schedules = []
      }
    },
    generateWeekDays() {
      const currentDate = new Date()
      const dayOfWeek = currentDate.getDay()
      const diff = currentDate.getDate() - dayOfWeek + (dayOfWeek === 0 ? -6 : 1)
      const monday = new Date(currentDate.setDate(diff))
      
      const weekDays = []
      for (let i = 0; i < 6; i++) {
        const day = new Date(monday)
        day.setDate(monday.getDate() + i)
        weekDays.push({
          name: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'][i],
          date: day.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
        })
      }
      this.weekDays = weekDays
    },
    previousLab() {
      const currentIndex = this.laboratories.indexOf(this.selectedLab)
      if (currentIndex > 0) {
        this.selectedLab = this.laboratories[currentIndex - 1]
        this.loadSchedules()
      }
    },
    nextLab() {
      const currentIndex = this.laboratories.indexOf(this.selectedLab)
      if (currentIndex < this.laboratories.length - 1) {
        this.selectedLab = this.laboratories[currentIndex + 1]
        this.loadSchedules()
      }
    },
    isTimeSlotWithinSchedule(dayName, timeSlot) {
      if (!this.schedules || this.schedules.length === 0) {
        return false;
      }
      
      const timeSlotMinutes = this.convertTimeToMinutes(timeSlot);
      
      return this.schedules.some(schedule => {
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
        
        return slotMinutes === startMinutes;
      });
      
      if (!schedule) return {};
      
      const startMinutes = this.convertTimeToMinutes(schedule.startTime);
      const endMinutes = this.convertTimeToMinutes(schedule.endTime);
      const firstSlotMinutes = this.convertTimeToMinutes('7:30 AM');
      
      // Calculate exact position based on minutes from first slot
      const minutesFromStart = startMinutes - firstSlotMinutes;
      const topPosition = (minutesFromStart / 30) * 30;
      
      // Calculate exact duration in minutes and convert to pixels
      const durationMinutes = endMinutes - startMinutes;
      const height = Math.ceil(durationMinutes / 30) * 30;
      
      return {
        position: 'absolute',
        top: `${topPosition}px`,
        height: `${height}px`,
        left: 0,
        right: 0,
        backgroundColor: '#E84B75',
        padding: '4px 6px',
        overflow: 'hidden',
        zIndex: 1,
        color: '#fff',
        cursor: 'pointer',
        transition: 'all 0.2s ease',
        margin: '1px'
      };
    },
    getScheduleTitle(dayName, timeSlot) {
      const schedule = this.schedules.find(s => 
        s.labRoom === this.selectedLab && 
        s.day === dayName && 
        s.startTime === timeSlot
      );
      if (!schedule) return '';
      return `${schedule.courseCode} (${schedule.types[0]})`;
    },
    getScheduleTime(dayName, timeSlot) {
      const schedule = this.schedules.find(s => 
        s.labRoom === this.selectedLab && 
        s.day === dayName && 
        s.startTime === timeSlot
      );
      if (!schedule) return '';
      return `${this.formatTime(schedule.startTime)} - ${this.formatTime(schedule.endTime)}`;
    },
    getScheduleDetails(dayName, timeSlot) {
      const schedule = this.schedules.find(s => 
        s.labRoom === this.selectedLab && 
        s.day === dayName && 
        s.startTime === timeSlot
      );
      if (!schedule) return '';
      return `${schedule.courseName}\n${schedule.section}\n${schedule.instructorName}`;
    },
    formatTime(timeStr) {
      // Remove leading zeros from hours and standardize AM/PM
      const [time, period] = timeStr.split(' ');
      const [hours, minutes] = time.split(':');
      return `${parseInt(hours)}:${minutes} ${period}`;
    },
    convertTimeToMinutes(timeStr) {
      const [time, period] = timeStr.split(' ')
      let [hours, minutes] = time.split(':').map(Number)
      
      if (period === 'PM' && hours !== 12) {
        hours += 12
      } else if (period === 'AM' && hours === 12) {
        hours = 0
      }
      
      return hours * 60 + minutes
    },
    downloadSchedule() {
      // Implement schedule download functionality
      console.log('Downloading schedule...')
    }
  },
  watch: {
    selectedLab: {
      handler(newLab) {
        this.loadSchedules()
      },
      immediate: true
    }
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
  padding: 2rem;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.header h1 {
  font-size: 1.8rem;
  color: #333;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.download-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background-color: #DD385A;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

.download-btn:hover {
  background-color: #c62f4d;
  transform: translateY(-1px);
}

.schedule-container {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  height: calc(100vh - 200px);
  display: flex;
  flex-direction: column;
}

.lab-navigation {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
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
}

.lab-indicator {
  font-size: 1.1rem;
  font-weight: 500;
  color: #333;
}

.week-header {
  display: flex;
  margin-bottom: 0;
  position: sticky;
  top: 0;
  z-index: 3;
  background: white;
}

.time-header {
  width: 80px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 8px 0 0 8px;
  position: sticky;
  left: 0;
  z-index: 4;
}

.day-headers {
  display: flex;
  flex: 1;
}

.day-header {
  flex: 1;
  padding: 0.75rem;
  text-align: center;
  background-color: #E84B75;
  color: white;
  border-right: 1px solid rgba(255, 255, 255, 0.1);
}

.day-name {
  font-weight: 600;
  margin-bottom: 0.25rem;
  font-size: 0.95rem;
}

.day-date {
  font-size: 0.85rem;
  opacity: 0.9;
}

.schedule-grid {
  display: flex;
  min-height: calc(30px * 26); /* Fixed height for 26 slots from 7:30 AM to 8:00 PM */
  background-color: #fff;
  position: relative;
  border: 1px solid #e0e0e0;
  overflow-y: auto;
  flex: 1;
}

.time-column {
  width: 80px;
  flex-shrink: 0;
  background-color: #fff;
  border-right: 1px solid #e0e0e0;
  position: sticky;
  left: 0;
  z-index: 2;
}

.schedule-content {
  display: flex;
  flex: 1;
  min-width: fit-content;
}

.day-column {
  flex: 1;
  position: relative;
  min-width: 200px;
  border-right: 1px solid #e0e0e0;
  background-color: #fff;
}

.day-column:last-child {
  border-right: none;
}

.day-slots {
  position: relative;
  min-height: calc(30px * 26); /* Ensure all time slots are visible */
  background-color: #fff;
}

.time-slot {
  height: 30px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  position: relative;
  color: #666;
  font-size: 0.75rem;
  padding-right: 8px;
  background-color: #fff;
}

.schedule-item {
  position: absolute;
  left: 0;
  right: 0;
  background-color: #E84B75;
  padding: 4px 6px;
  overflow: hidden;
  z-index: 1;
  color: #fff;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  flex-direction: column;
  gap: 2px;
  border: none;
  margin: 1px;
}

.schedule-item:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  opacity: 0.95;
  transform: scale(1.005);
}

.schedule-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.schedule-title {
  font-weight: 500;
  font-size: 0.8rem;
  color: #fff;
  margin: 0;
  line-height: 1.2;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.schedule-time {
  font-size: 0.7rem;
  color: rgba(255, 255, 255, 0.9);
  margin: 0;
  line-height: 1.2;
}

.schedule-details {
  font-size: 0.7rem;
  color: rgba(255, 255, 255, 0.9);
  margin: 0;
  line-height: 1.2;
  white-space: pre-line;
}
</style> 