<template>
  <div class="schedule-container">
    <div class="schedule-header">
      <div class="nav-buttons">
        <button class="nav-btn" @click="previousLab"><i class="fas fa-chevron-left"></i></button>
        <span class="current-lab">{{ selectedLab }}</span>
        <button class="nav-btn" @click="nextLab"><i class="fas fa-chevron-right"></i></button>
      </div>
    </div>
    <div class="schedule-table-wrapper">
      <table class="schedule-table">
        <thead>
          <tr>
            <th class="time-header">Time</th>
            <th v-for="(day, index) in weekDays" :key="index" class="day-header">
              <div class="day-name">{{ day.name }}</div>
              <div class="day-date">{{ day.date }}</div>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="time in displayTimeSlots" :key="time" class="time-row">
            <td class="time-cell">{{ time }}</td>
            <td v-for="(day, dayIndex) in weekDays" 
                :key="dayIndex" 
                class="schedule-cell"
                :class="{ 'has-schedule': hasSchedule(day.date, time) }">
              <div v-if="hasSchedule(day.date, time)" 
                   class="schedule-item" 
                   :style="getScheduleStyle(day.date, time)">
                <div class="schedule-content">
                  <div class="schedule-title">{{ getScheduleTitle(day.date, time) }}</div>
                  <div class="schedule-time">{{ getScheduleTime(day.date, time) }}</div>
                  <div class="schedule-details">{{ getScheduleDetails(day.date, time) }}</div>
                </div>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ScheduleGrid',
  props: {
    selectedLab: {
      type: String,
      required: true
    },
    weekDays: {
      type: Array,
      required: true
    },
    scheduleData: {
      type: Array,
      required: true
    },
    displayTimeSlots: {
      type: Array,
      default: () => []
    }
  },
  methods: {
    previousLab() {
      this.$emit('previous-lab')
    },
    nextLab() {
      this.$emit('next-lab')
    },
    hasSchedule(date, time) {
      return this.scheduleData.some(schedule => 
        schedule.day === this.getDayName(date) && schedule.startTime === time
      )
    },
    getScheduleStyle(date, time) {
      const schedule = this.scheduleData.find(s => 
        s.day === this.getDayName(date) && s.startTime === time
      )
      if (schedule) {
        const startMinutes = this.convertTimeToMinutes(schedule.startTime)
        const endMinutes = this.convertTimeToMinutes(schedule.endTime)
        const firstSlotMinutes = this.convertTimeToMinutes(this.displayTimeSlots[0]) // 7:30 AM
        
        // Calculate positions using fixed 60px height
        const slotHeight = 60
        
        // Calculate number of 30-minute slots from 7:30 AM
        const startSlots = Math.floor((startMinutes - firstSlotMinutes) / 30)
        const endSlots = Math.ceil((endMinutes - firstSlotMinutes) / 30)
        
        // Calculate exact pixel positions
        const topPosition = startSlots * slotHeight
        const height = (endSlots - startSlots) * slotHeight

        return {
          position: 'absolute',
          top: `${topPosition}px`,
          height: `${height}px`,
          left: '2px',
          right: '2px',
          backgroundColor: schedule.color || '#DD385A',
          borderRadius: '4px',
          padding: '8px',
          overflow: 'hidden',
          zIndex: 1,
          border: '1px solid rgba(0, 0, 0, 0.1)',
          color: '#fff',
          cursor: 'pointer',
          transition: 'all 0.2s ease',
          boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)'
        }
      }
      return {}
    },
    convertTimeToMinutes(timeStr) {
      const [time, period] = timeStr.split(' ')
      let [hours, minutes] = time.split(':').map(Number)
      
      // Convert to 24-hour format
      if (period === 'PM' && hours !== 12) {
        hours += 12
      } else if (period === 'AM' && hours === 12) {
        hours = 0
      }
      
      return hours * 60 + minutes
    },
    getScheduleTitle(date, time) {
      const schedule = this.scheduleData.find(s => 
        s.day === this.getDayName(date) && s.startTime === time
      )
      return schedule ? schedule.title : ''
    },
    getScheduleTime(date, time) {
      const schedule = this.scheduleData.find(s => 
        s.day === this.getDayName(date) && s.startTime === time
      )
      return schedule ? `${schedule.startTime} - ${schedule.endTime}` : ''
    },
    getScheduleDetails(date, time) {
      const schedule = this.scheduleData.find(s => 
        s.day === this.getDayName(date) && s.startTime === time
      )
      return schedule ? schedule.details : ''
    },
    getDayName(dateStr) {
      const date = new Date(dateStr)
      const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
      return days[date.getDay()]
    }
  }
}
</script>

<style scoped>
.schedule-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  height: calc(100vh - 200px);
  display: flex;
  flex-direction: column;
}

.schedule-header {
  padding: 1rem;
  border-bottom: 1px solid #eee;
  flex-shrink: 0;
}

.nav-buttons {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
}

.nav-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.nav-btn:hover {
  background-color: #f5f5f5;
}

.current-lab {
  font-weight: 500;
  font-size: 1.1rem;
}

.schedule-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
}

.schedule-table-wrapper {
  overflow-y: auto;
  flex-grow: 1;
}

thead {
  position: sticky;
  top: 0;
  z-index: 2;
  background: white;
}

.time-header {
  width: 80px;
  height: 60px;
  padding: 12px;
  text-align: center;
  border: 1px solid #ddd;
  background: white;
  font-weight: normal;
  vertical-align: middle;
  position: sticky;
  left: 0;
  z-index: 3;
}

.day-header {
  height: 60px;
  padding: 12px;
  text-align: center;
  border: 1px solid #ddd;
  background-color: #DD385A;
  color: white;
  font-weight: normal;
  position: sticky;
  top: 0;
  z-index: 2;
}

.day-name {
  font-weight: 500;
  margin-bottom: 4px;
}

.day-date {
  font-size: 0.9rem;
  opacity: 0.9;
}

.time-row {
  height: 60px;
}

.time-cell {
  width: 80px;
  height: 60px;
  padding: 0 12px;
  text-align: right;
  border: 1px solid #ddd;
  font-size: 0.9rem;
  color: #666;
  background: white;
  vertical-align: top;
  position: sticky;
  left: 0;
  z-index: 1;
}

.schedule-cell {
  border: 1px solid #ddd;
  padding: 0;
  position: relative;
  vertical-align: top;
  height: 60px;
}

.schedule-item {
  position: absolute;
  left: 2px;
  right: 2px;
  background-color: #DD385A;
  color: white;
  z-index: 1;
  overflow: hidden;
  border-radius: 4px;
  padding: 8px;
  margin: 1px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
}

.schedule-item:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  transform: translateY(-1px);
}

.schedule-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  gap: 4px;
}

.schedule-title {
  font-weight: 500;
  font-size: 0.9rem;
  line-height: 1.2;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.schedule-time {
  font-size: 0.8rem;
  opacity: 0.9;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.schedule-details {
  font-size: 0.8rem;
  opacity: 0.9;
  line-height: 1.2;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Scrollbar styling */
.schedule-table-wrapper::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.schedule-table-wrapper::-webkit-scrollbar-track {
  background: #f5f5f5;
}

.schedule-table-wrapper::-webkit-scrollbar-thumb {
  background: #ddd;
  border-radius: 4px;
}

.schedule-table-wrapper::-webkit-scrollbar-thumb:hover {
  background: #ccc;
}

/* Grid lines */
.schedule-grid {
  display: grid;
  grid-template-columns: 80px 1fr;
  gap: 0;
  border: 1px solid #ddd;
  background: white;
}

.time-column {
  border-right: 1px solid #ddd;
}

.schedule-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 0;
}

.time-slot {
  height: 60px;
  border-bottom: 1px solid #ddd;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 0 8px;
  font-size: 0.85rem;
  color: #666;
  background: white;
}

.day-column {
  border-right: 1px solid #ddd;
  position: relative;
  min-width: 120px;
}

.day-column:last-child {
  border-right: none;
}
</style> 