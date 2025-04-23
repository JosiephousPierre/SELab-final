<template>
  <div class="calendar">
    <div class="calendar-header">
      <button @click="previousMonth"><i class="fas fa-chevron-left"></i></button>
      <span>{{ currentMonthName }} {{ currentYear }}</span>
      <button @click="nextMonth"><i class="fas fa-chevron-right"></i></button>
    </div>
    <div class="calendar-body">
      <div class="weekdays">
        <div v-for="day in weekDays" :key="day">{{ day }}</div>
      </div>
      <div class="days">
        <button
          v-for="{ day, current, selected } in days"
          :key="day"
          :class="{ 'current-month': current, selected }"
          @click="selectDate(day)"
        >
          {{ day.getDate() }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Calendar',
  data() {
    return {
      currentDate: new Date(),
      selectedDate: new Date(),
      weekDays: ['S', 'M', 'T', 'W', 'T', 'F', 'S']
    }
  },
  computed: {
    currentMonthName() {
      return this.currentDate.toLocaleString('default', { month: 'long' })
    },
    currentYear() {
      return this.currentDate.getFullYear()
    },
    selectedDateText() {
      const today = new Date()
      const isToday = this.selectedDate.toDateString() === today.toDateString()
      if (isToday) return 'Today'
      
      const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
      return days[this.selectedDate.getDay()]
    },
    days() {
      const year = this.currentDate.getFullYear()
      const month = this.currentDate.getMonth()
      const firstDay = new Date(year, month, 1)
      const lastDay = new Date(year, month + 1, 0)
      const days = []
      
      // Previous month days
      const firstDayOfWeek = firstDay.getDay()
      const previousMonth = new Date(year, month, 0)
      for (let i = firstDayOfWeek - 1; i >= 0; i--) {
        days.push({
          day: new Date(year, month - 1, previousMonth.getDate() - i),
          current: false,
          selected: false
        })
      }
      
      // Current month days
      for (let i = 1; i <= lastDay.getDate(); i++) {
        const date = new Date(year, month, i)
        days.push({
          day: date,
          current: true,
          selected: date.toDateString() === this.selectedDate.toDateString()
        })
      }
      
      // Next month days
      const remainingDays = 42 - days.length
      for (let i = 1; i <= remainingDays; i++) {
        days.push({
          day: new Date(year, month + 1, i),
          current: false,
          selected: false
        })
      }
      
      return days
    }
  },
  methods: {
    previousMonth() {
      this.currentDate = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth() - 1)
    },
    nextMonth() {
      this.currentDate = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth() + 1)
    },
    previousDay() {
      this.selectedDate = new Date(this.selectedDate.getTime() - 86400000)
      this.currentDate = new Date(this.selectedDate)
      this.$emit('date-selected', this.selectedDate)
    },
    nextDay() {
      this.selectedDate = new Date(this.selectedDate.getTime() + 86400000)
      this.currentDate = new Date(this.selectedDate)
      this.$emit('date-selected', this.selectedDate)
    },
    selectDate(date) {
      this.selectedDate = date
      this.$emit('date-selected', date)
    },
    goToToday() {
      const today = new Date()
      this.selectedDate = today
      this.currentDate = new Date(today)
      this.$emit('date-selected', today)
    }
  }
}
</script>

<style scoped>
.calendar {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 0rem;
  border-radius: 8px;
  background: white;
  min-width: 250px;
}

.calendar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 0.5rem;
}

.calendar-header span {
  font-size: 1rem;
  font-weight: 500;
  color: #E91E63;
}

.calendar-header button,
.nav-btn {
  border: none;
  background: none;
  padding: 0.5rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #E91E63;
  width: 32px;
  height: 32px;
  border-radius: 50%;
}

.calendar-header button:hover,
.nav-btn:hover {
  background: rgba(233, 30, 99, 0.1);
}

.calendar-body {
  padding: 0rem;
  background: #f9f9f9;
  border-radius: 8px;
}

.weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  text-align: center;
  font-weight: 500;
  color: #E91E63;
  margin-bottom: 0.75rem;
  margin-top: 0.25rem;
  font-size: 0.8rem;
}

.days {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
}

.days button {
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border-radius: 6px;
  color: #333;
  border: none;
  background: none;
  padding: 0;
  font-size: 0.9rem;
  width: 32px;
  height: 32px;
}

.days button:hover {
  background: rgba(233, 30, 99, 0.1);
}

.days button.current-month {
  color: #333;
}

.days button.selected {
  background: #E91E63;
  color: white;
}
</style>