<template>
  <div class="dashboard-layout">
    <DashBoardSidebarLab />
    <div class="main-content">
      <DashBoardTopbar />
      <div class="calendar-container">
        <!-- Calendar Header -->
        <div class="calendar-header">
          <div class="calendar-controls">
            <button class="today-btn">Today</button>
            <div class="nav-buttons">
              <button class="nav-btn" @click="previousPeriod">
                <i class="fas fa-chevron-left"></i>
              </button>
              <button class="nav-btn" @click="nextPeriod">
                <i class="fas fa-chevron-right"></i>
              </button>
            </div>
            <h2>{{ currentPeriodLabel }}</h2>
          </div>
          <div class="view-controls">
            <button class="view-btn" :class="{ active: currentView === 'month' }" @click="currentView = 'month'">Month</button>
            <button class="view-btn" :class="{ active: currentView === 'week' }" @click="currentView = 'week'">Week</button>
            <button class="view-btn" :class="{ active: currentView === 'day' }" @click="currentView = 'day'">Day</button>
          </div>
        </div>

        <div class="calendar-body">
          <!-- Left Sidebar -->
          <div class="calendar-sidebar" v-if="currentView === 'month'">
            <!-- Mini Calendar -->
            <div class="mini-calendar">
              <div class="mini-calendar-header">
                <span>{{ miniCalendarMonthYear }}</span>
              </div>
              <div class="mini-calendar-grid">
                <div class="mini-calendar-weekdays">
                  <span v-for="day in weekDays" :key="day">{{ day }}</span>
                </div>
                <div class="mini-calendar-days">
                  <div
                    v-for="date in miniCalendarDates"
                    :key="date.date"
                    class="mini-calendar-day"
                    :class="{
                      'other-month': !date.isCurrentMonth,
                      'today': isToday(date.date),
                      'selected': isSelected(date.date)
                    }"
                    @click="selectDate(date.date)"
                  >
                    {{ date.dayOfMonth }}
                  </div>
                </div>
              </div>
            </div>

            <!-- Recent Bookings -->
            <div class="recent-bookings">
              <h3>Recent Bookings</h3>
              <div class="search-box">
                <i class="fas fa-search"></i>
                <input type="text" placeholder="Search for people" />
              </div>
              <div class="bookings-list">
                <!-- Bookings will be populated here -->
              </div>
            </div>
          </div>

          <!-- Main Calendar Grid -->
          <div class="main-calendar" :class="currentView">
            <!-- Month View -->
            <div v-if="currentView === 'month'" class="calendar-grid">
              <div class="calendar-weekdays">
                <div v-for="day in weekDays" :key="day" class="weekday">
                  {{ day }}
                </div>
              </div>
              <div class="calendar-dates">
                <div
                  v-for="date in calendarDates"
                  :key="date.date"
                  class="calendar-day"
                  :class="{
                    'other-month': !date.isCurrentMonth,
                    'today': isToday(date.date),
                    'has-events': hasEvents(date.date)
                  }"
                >
                  <div class="date-header">
                    {{ date.dayOfMonth }}
                    <div v-if="hasBookings(date.date)" class="booking-indicator">
                      {{ getBookingsCount(date.date) }} bookings
                    </div>
                  </div>
                  <div class="events-container">
                    <div
                      v-for="event in getEventsForDate(date.date)"
                      :key="event.id"
                      class="event-item"
                      :style="{ backgroundColor: event.color }"
                    >
                      {{ event.title }}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Week View -->
            <div v-else-if="currentView === 'week'" class="week-view">
              <div class="week-header">
                <div class="time-column-header"></div>
                <div class="day-headers">
                  <div v-for="day in weekDaysWithDates" :key="day.date" class="day-header">
                    <div class="day-name">{{ day.name }}</div>
                    <div class="day-date">{{ formatDate(day.date) }}</div>
                    <div class="booking-count" v-if="getBookingsCount(day.date) > 0">
                      {{ getBookingsCount(day.date) }} Booking(s)
                    </div>
                  </div>
                </div>
              </div>
              <div class="week-body">
                <div class="time-column">
                  <div v-for="time in timeSlots" :key="time" class="time-slot">
                    {{ time }}
                  </div>
                </div>
                <div class="days-grid">
                  <div v-for="day in weekDaysWithDates" :key="day.date" class="day-column">
                    <div v-for="time in timeSlots" :key="time" class="time-slot">
                      <div 
                        v-for="event in getEventsForDateTime(day.date, time)" 
                        :key="event.id"
                        class="event-block"
                        :style="{
                          backgroundColor: event.color,
                          height: `${event.duration * 50}px`
                        }"
                      >
                        <div class="event-content">
                          <div class="event-title">{{ event.title }}</div>
                          <div class="event-details">{{ event.details }}</div>
                          <div class="event-section">{{ event.section }}</div>
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
  </div>
</template>

<script>
import DashBoardSidebarLab from '../../components/DashBoardSidebarLab.vue'
import DashBoardTopbar from '../../components/DashBoardTopbar.vue'

export default {
  name: 'CalendarLab',
  components: {
    DashBoardSidebarLab,
    DashBoardTopbar
  },
  data() {
    return {
      currentDate: new Date(),
      selectedDate: new Date(),
      currentView: 'month',
      weekDays: ['SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT'],
      timeSlots: [
        '7:30 AM', '8:00 AM', '8:30 AM', '9:00 AM', '9:30 AM',
        '10:00 AM', '10:30 AM', '11:00 AM', '11:30 AM', '12:00 PM',
        '12:30 PM', '1:00 PM', '1:30 PM', '2:00 PM', '2:30 PM',
        '3:00 PM', '3:30 PM', '4:00 PM', '4:30 PM', '5:00 PM',
        '5:30 PM', '6:00 PM', '6:30 PM', '7:00 PM', '7:30 PM'
      ],
      events: [
        {
          id: 1,
          title: 'COMP 123 (LECT/LAB)',
          details: 'Clorbis, V. H.',
          section: 'BSIT-1B',
          date: '2024-03-18',
          time: '8:30 AM',
          duration: 2,
          color: '#DD385A'
        },
        // Add more sample events here
      ]
    }
  },
  computed: {
    currentPeriodLabel() {
      if (this.currentView === 'month') {
        return this.currentMonthYear
      } else if (this.currentView === 'week') {
        const weekStart = this.getWeekStart(this.currentDate)
        const weekEnd = this.getWeekEnd(this.currentDate)
        return `${this.formatDate(weekStart)} - ${this.formatDate(weekEnd)}`
      }
      return this.formatDate(this.currentDate)
    },
    weekDaysWithDates() {
      const weekStart = this.getWeekStart(this.currentDate)
      return this.weekDays.map((day, index) => {
        const date = new Date(weekStart)
        date.setDate(weekStart.getDate() + index)
        return {
          name: day,
          date: date
        }
      })
    },
    currentMonthYear() {
      return new Intl.DateTimeFormat('en-US', { month: 'long', year: 'numeric' }).format(this.currentDate)
    },
    miniCalendarMonthYear() {
      return new Intl.DateTimeFormat('en-US', { month: 'long', year: 'numeric' }).format(this.currentDate)
    },
    calendarDates() {
      return this.generateCalendarDates(this.currentDate)
    },
    miniCalendarDates() {
      return this.generateCalendarDates(this.currentDate)
    }
  },
  methods: {
    generateCalendarDates(date) {
      const year = date.getFullYear()
      const month = date.getMonth()
      const firstDay = new Date(year, month, 1)
      const lastDay = new Date(year, month + 1, 0)
      const dates = []

      // Add days from previous month
      const firstDayOfWeek = firstDay.getDay()
      for (let i = firstDayOfWeek - 1; i >= 0; i--) {
        const prevDate = new Date(year, month, -i)
        dates.push({
          date: prevDate,
          dayOfMonth: prevDate.getDate(),
          isCurrentMonth: false
        })
      }

      // Add days of current month
      for (let i = 1; i <= lastDay.getDate(); i++) {
        const currentDate = new Date(year, month, i)
        dates.push({
          date: currentDate,
          dayOfMonth: i,
          isCurrentMonth: true
        })
      }

      // Add days from next month
      const remainingDays = 42 - dates.length // 6 rows × 7 days
      for (let i = 1; i <= remainingDays; i++) {
        const nextDate = new Date(year, month + 1, i)
        dates.push({
          date: nextDate,
          dayOfMonth: nextDate.getDate(),
          isCurrentMonth: false
        })
      }

      return dates
    },
    isToday(date) {
      const today = new Date()
      return date.toDateString() === today.toDateString()
    },
    isSelected(date) {
      return date.toDateString() === this.selectedDate.toDateString()
    },
    selectDate(date) {
      this.selectedDate = date
    },
    previousPeriod() {
      if (this.currentView === 'month') {
        this.previousMonth()
      } else if (this.currentView === 'week') {
        const newDate = new Date(this.currentDate)
        newDate.setDate(newDate.getDate() - 7)
        this.currentDate = newDate
      }
    },
    nextPeriod() {
      if (this.currentView === 'month') {
        this.nextMonth()
      } else if (this.currentView === 'week') {
        const newDate = new Date(this.currentDate)
        newDate.setDate(newDate.getDate() + 7)
        this.currentDate = newDate
      }
    },
    hasEvents(date) {
      // Implement logic to check if date has events
      return false
    },
    hasBookings(date) {
      // Implement logic to check if date has bookings
      return false
    },
    getBookingsCount(date) {
      // Implement logic to get bookings count
      return 0
    },
    getEventsForDate(date) {
      // Implement logic to get events for a specific date
      return []
    },
    formatDate(date) {
      return new Intl.DateTimeFormat('en-US', { 
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      }).format(date)
    },
    getWeekStart(date) {
      const d = new Date(date)
      const day = d.getDay()
      const diff = d.getDate() - day
      return new Date(d.setDate(diff))
    },
    getWeekEnd(date) {
      const weekStart = this.getWeekStart(date)
      const weekEnd = new Date(weekStart)
      weekEnd.setDate(weekStart.getDate() + 6)
      return weekEnd
    },
    getEventsForDateTime(date, time) {
      return this.events.filter(event => 
        event.date === this.formatDateISO(date) && 
        event.time === time
      )
    },
    formatDateISO(date) {
      return date.toISOString().split('T')[0]
    },
    previousMonth() {
      this.currentDate = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth() - 1)
    },
    nextMonth() {
      this.currentDate = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth() + 1)
    }
  }
}
</script>

<style scoped>
.dashboard-layout {
  display: flex;
  min-height: 100vh;
  background-color: #f5f5f5;
  width: 100%;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
}

.main-content {
  flex: 1;
  margin-left: 70px;
  width: calc(100% - 70px);
  transition: margin-left 0.3s;
  overflow-x: hidden;
  height: 100vh;
  position: relative;
}

.calendar-container {
  padding: 20px;
  height: calc(100vh - 64px);
  display: flex;
  flex-direction: column;
  overflow-x: hidden;
  background-color: #f5f5f5;
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.calendar-controls {
  display: flex;
  align-items: center;
  gap: 16px;
}

.today-btn {
  padding: 8px 16px;
  background-color: #DD385A;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.nav-buttons {
  display: flex;
  gap: 8px;
}

.nav-btn {
  padding: 8px;
  background: none;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
}

.nav-btn:hover {
  background-color: #f5f5f5;
}

.view-controls {
  display: flex;
  gap: 8px;
}

.view-btn {
  padding: 8px 16px;
  background: none;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
}

.view-btn.active {
  background-color: #DD385A;
  color: white;
  border-color: #DD385A;
}

.calendar-body {
  display: flex;
  gap: 20px;
  flex: 1;
  overflow: hidden;
}

.calendar-sidebar {
  width: 280px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.mini-calendar {
  background: white;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.mini-calendar-header {
  text-align: center;
  margin-bottom: 12px;
  font-weight: 500;
}

.mini-calendar-weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  text-align: center;
  font-size: 12px;
  color: #666;
  margin-bottom: 8px;
}

.mini-calendar-days {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 2px;
}

.mini-calendar-day {
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  cursor: pointer;
  border-radius: 50%;
}

.mini-calendar-day:hover {
  background-color: #f5f5f5;
}

.mini-calendar-day.other-month {
  color: #ccc;
}

.mini-calendar-day.today {
  background-color: #DD385A;
  color: white;
}

.mini-calendar-day.selected {
  background-color: rgba(221, 56, 90, 0.1);
  color: #DD385A;
}

.recent-bookings {
  background: white;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  flex: 1;
}

.search-box {
  display: flex;
  align-items: center;
  background: #f5f5f5;
  border-radius: 4px;
  padding: 8px 12px;
  margin: 12px 0;
}

.search-box input {
  border: none;
  background: none;
  outline: none;
  width: 100%;
  margin-left: 8px;
}

.main-calendar {
  flex: 1;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.calendar-grid {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.calendar-weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  text-align: center;
  padding: 12px;
  background-color: #DD385A;
  color: white;
}

.calendar-dates {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  grid-template-rows: repeat(6, 1fr);
  border-top: 1px solid #eee;
}

.calendar-day {
  border-right: 1px solid #eee;
  border-bottom: 1px solid #eee;
  padding: 8px;
  min-height: 100px;
}

.calendar-day.other-month {
  background-color: #f9f9f9;
  color: #ccc;
}

.calendar-day.today {
  background-color: #fff5f7;
}

.date-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.booking-indicator {
  font-size: 12px;
  color: #DD385A;
}

.events-container {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.event-item {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  color: white;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.main-calendar.week {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.week-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.week-header {
  display: flex;
  border-bottom: 1px solid #eee;
}

.time-column-header {
  width: 80px;
  flex-shrink: 0;
}

.day-headers {
  display: flex;
  flex: 1;
}

.day-header {
  flex: 1;
  padding: 12px;
  text-align: center;
  background-color: #DD385A;
  color: white;
  border-right: 1px solid rgba(255, 255, 255, 0.1);
}

.day-name {
  font-weight: 500;
  margin-bottom: 4px;
}

.day-date {
  font-size: 0.9em;
  opacity: 0.9;
}

.booking-count {
  font-size: 0.8em;
  margin-top: 4px;
  padding: 2px 6px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  display: inline-block;
}

.week-body {
  display: flex;
  flex: 1;
  overflow-y: auto;
}

.time-column {
  width: 80px;
  flex-shrink: 0;
  border-right: 1px solid #eee;
}

.days-grid {
  display: flex;
  flex: 1;
}

.day-column {
  flex: 1;
  border-right: 1px solid #eee;
  position: relative;
}

.time-slot {
  height: 50px;
  padding: 4px;
  border-bottom: 1px solid #eee;
  font-size: 0.8em;
  color: #666;
  position: relative;
}

.time-column .time-slot {
  padding: 4px 8px;
  text-align: right;
}

.event-block {
  position: absolute;
  left: 4px;
  right: 4px;
  border-radius: 4px;
  padding: 4px;
  z-index: 1;
  overflow: hidden;
}

.event-content {
  height: 100%;
  color: white;
  font-size: 0.85em;
}

.event-title {
  font-weight: 500;
  margin-bottom: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.event-details {
  font-size: 0.9em;
  opacity: 0.9;
}

.event-section {
  font-size: 0.8em;
  opacity: 0.8;
}
</style>
