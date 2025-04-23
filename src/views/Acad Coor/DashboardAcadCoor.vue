// DashboardAcadCoor.vue
<template>
  <div class="dashboard-layout" ref="scheduleComponent">
    <DashBoardSidebarAcadCoor />
    <div class="main-content">
      <DashBoardTopbar />
      <div class="content-wrapper">
        <div class="dashboard-header">
          <div class="welcome-section">
            <h2>Welcome, {{ userName }}!</h2>
            <p class="date">{{ formattedDate }}</p>
          </div>
        </div>

        <div class="dashboard-content">
          <div class="left-panel">
            <div class="calendar-box">
              <Calendar @date-selected="generateWeekDays" ref="calendar" />
              <div class="calendar-navigation">
                <button class="cal-nav-btn" @click="previousMonth"><span>‹</span></button>
                <button class="today-btn" @click="goToToday">Today</button>
                <button class="cal-nav-btn" @click="nextMonth"><span>›</span></button>
              </div>
            </div>
          </div>

          <div class="right-panel">
            <div class="controls-top">
              <div class="semester-indicator">
                <div class="semester-box">
                  {{ currentSemesterName || "Loading semester..." }}
                </div>
              </div>
              
              
              <div class="lab-dropdown-wrapper">
                <select v-model="selectedLab" class="lab-dropdown">
                  <option v-for="lab in labs" :key="lab" :value="lab">{{ lab }}</option>
                </select>
              </div>
            </div>

            <div class="schedule-container">
              <div class="schedule-table">
                <div class="table-header">
                  <div class="time-header">Time</div>
                  <div class="day-headers">
                    <div class="day-header" v-for="(day, index) in weekDays" :key="index">
                      <div class="day-name">{{ day.name }}</div>
                      <div class="day-date">{{ day.date }}</div>
                    </div>
                  </div>
                </div>
                
                <div class="table-body">
                  <div class="time-column">
                    <div class="time-slot" v-for="time in displayTimeSlots" :key="time">
                      {{ time }}
                    </div>
                  </div>
                  
                  <div class="days-grid">
                    <div class="day-column" v-for="(day, dayIndex) in weekDays" :key="dayIndex">
                      <div class="time-slots">
                        <div class="slot" v-for="(time, timeIndex) in displayTimeSlots" :key="timeIndex">
                          <div 
                            v-if="isTimeSlotWithinSchedule(day.name, time)"
                            class="schedule-item" 
                            :class="getScheduleStatusClass(day.name, time)"
                            @click="showScheduleDetails(day.name, time)"
                          >
                            <div 
                              v-if="isScheduleStart(day.name, time)" 
                              class="schedule-content"
                            >
                              <div class="schedule-lab">{{ selectedLab }}</div>
                              <div class="schedule-time">{{ getScheduleTime(day.name, time) }}</div>
                              <div class="schedule-title">{{ getScheduleTitle(day.name, time) }}</div>
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
    </div>

    <!-- Schedule Details Popup -->
    <div class="schedule-popup" v-if="showPopup">
      <div class="popup-content">
        <div class="popup-header">
          <h3>{{ selectedSchedule.title }}</h3>
          <button class="close-btn" @click="closePopup">×</button>
        </div>
        <div class="popup-body">
          <div class="detail-row">
            <span class="detail-label">Lab:</span>
            <span class="detail-value">{{ selectedSchedule.labRoom }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Course:</span>
            <span class="detail-value">{{ selectedSchedule.courseName }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Section:</span>
            <span class="detail-value">{{ selectedSchedule.section }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Instructor:</span>
            <span class="detail-value">{{ selectedSchedule.instructorName }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Time:</span>
            <span class="detail-value">{{ selectedSchedule.startTime }} - {{ selectedSchedule.endTime }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Day:</span>
            <span class="detail-value">{{ selectedSchedule.day }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import DashBoardSidebarAcadCoor from '../../components/DashBoardSidebarAcadCoor.vue'
import DashBoardTopbar from '../../components/DashBoardTopbar.vue'
import Calendar from '../../components/Calendar.vue'
import { scheduleAPI } from '../../services/api.js'
import { systemSettingsAPI } from '../../services/api.js'

export default {
  name: 'DashboardAcadCoor',
  components: {
    DashBoardSidebarAcadCoor,
    DashBoardTopbar,
    Calendar
    
  },
  data() {
    return {
      selectedLab: 'L201',
      labs: ['L201', 'L202', 'L203', 'L204', 'L205', 'IOT'],
      displayTimeSlots: [
        '7:30 AM', '8:00 AM', '8:30 AM', '9:00 AM', '9:30 AM', '10:00 AM',
        '10:30 AM', '11:00 AM', '11:30 AM', '12:00 PM', '12:30 PM', '1:00 PM',
        '1:30 PM', '2:00 PM', '2:30 PM', '3:00 PM', '3:30 PM', '4:00 PM',
        '4:30 PM', '5:00 PM', '5:30 PM', '6:00 PM', '6:30 PM', '7:00 PM',
        '7:30 PM', '8:00 PM'
      ],
      schedules: [],
      weekDays: [],
      currentDate: new Date(),
      showPopup: false,
      selectedSchedule: {},
      userName: 'User',
      pollInterval: null,
      currentSemesterName: ''
    }
  },
  computed: {
    formattedDate() {
      const options = { month: 'long', day: 'numeric', year: 'numeric' };
      return this.currentDate.toLocaleDateString('en-US', options);
    }
  },
  mounted() {
    this.loadSchedulesFromStorage();
    
    // No longer automatically initialize sample schedules
    // if (this.schedules.length === 0) {
    //   this.initializeSchedules();
    // }
    
    this.generateWeekDays();
    this.getUserName();
    
    // Start polling for updates
    this.startPolling();
    // Load current semester name
    this.loadCurrentSemesterName();
  },
  beforeUnmount() {
    // Clear the interval when component is destroyed
    this.stopPolling();
  },
  methods: {
    startPolling() {
      // Poll every 1 second for updates
      this.pollInterval = setInterval(() => {
        // Load schedules without causing UI flickering
        this.loadSchedulesWithoutFlicker();
      }, 1000);
    },
    stopPolling() {
      if (this.pollInterval) {
        clearInterval(this.pollInterval);
        this.pollInterval = null;
      }
    },
    hasSchedulesChanged(oldSchedules, newSchedules) {
      // Check if the schedules arrays are different lengths
      if (oldSchedules.length !== newSchedules.length) {
        return true;
      }
      
      // Create a map of IDs to schedules for quick comparison
      const oldScheduleMap = new Map();
      oldSchedules.forEach(schedule => {
        const key = `${schedule.id}-${schedule.day}-${schedule.status}`;
        oldScheduleMap.set(key, schedule);
      });
      
      // Check if any schedule has changed or is new
      for (const newSchedule of newSchedules) {
        const key = `${newSchedule.id}-${newSchedule.day}-${newSchedule.status}`;
        const oldSchedule = oldScheduleMap.get(key);
        
        // If this schedule doesn't exist in old schedules, there's a change
        if (!oldSchedule) {
          return true;
        }
        
        // Check if any important properties have changed
        if (
          oldSchedule.status !== newSchedule.status ||
          oldSchedule.startTime !== newSchedule.startTime ||
          oldSchedule.endTime !== newSchedule.endTime ||
          oldSchedule.instructorName !== newSchedule.instructorName ||
          oldSchedule.labRoom !== newSchedule.labRoom
        ) {
          return true;
        }
      }
      
      // No changes detected
      return false;
    },
    loadSchedulesWithoutFlicker() {
      try {
        // First check if the user is still authenticated
        const token = sessionStorage.getItem('token') || localStorage.getItem('token');
        if (!token) {
          console.error('No token found when loading schedules');
          return;
        }

        // Initialize empty schedules array
        let processedSchedules = [];
        
        // First, get the current display semester
        systemSettingsAPI.getCurrentDisplaySemester()
          .then(semesterResponse => {
            const currentDisplaySemesterId = semesterResponse.data.semester_id;
            const currentDisplaySemesterName = semesterResponse.data.semester_name;
            
            console.log(`Current display semester: ${currentDisplaySemesterName} (ID: ${currentDisplaySemesterId})`);
            
            // Load only approved schedules from the database
            return scheduleAPI.getByStatus('approved')
              .then(response => {
                const approvedSchedules = response.data || [];
                
                console.log(`Loaded ${approvedSchedules.length} total approved schedules from API`);
                
                // Filter schedules by the current display semester
                const filteredSchedules = approvedSchedules.filter(schedule => 
                  schedule.semester_id === currentDisplaySemesterId
                );
                
                console.log(`Filtered to ${filteredSchedules.length} schedules from current display semester (${currentDisplaySemesterName})`);
                
                // Convert API response format to frontend format and handle second_day
                
                filteredSchedules.forEach(schedule => {
                  // Create the base schedule object
                  const baseSchedule = {
                    id: schedule.id,
                    semester: schedule.semester_name,
                    section: schedule.section,
                    courseCode: schedule.course_code,
                    courseName: schedule.course_name,
                    day: schedule.day,
                    secondDay: schedule.second_day,
                    labRoom: schedule.lab_room_name,
                    instructorName: schedule.instructor_name,
                    startTime: schedule.start_time,
                    endTime: schedule.end_time,
                    types: schedule.schedule_types,
                    status: schedule.status,
                    class_type: schedule.class_type,
                    // Additional properties for frontend
                    duration: this.calculateDurationMinutes(schedule.start_time, schedule.end_time),
                    title: `${schedule.course_code} (${schedule.class_type})`,
                    details: `${schedule.course_name}\n${schedule.section}\n${schedule.instructor_name}`,
                    color: '#4CAF50' // Green for approved schedules
                  };
                  
                  // Always add the primary day schedule
                  processedSchedules.push(baseSchedule);
                  
                  // If there's a second day, create a separate schedule object for it
                  if (schedule.second_day) {
                    // Create a duplicate entry but with the second_day as the primary day
                    // and a special flag to indicate it's a secondary entry
                    const secondDaySchedule = {
                      ...baseSchedule,
                      day: schedule.second_day,
                      secondDay: null, // Clear secondDay to avoid double processing
                      isSecondDayEntry: true,  // Mark that this is a secondary entry
                      originalId: schedule.id  // Keep track of the original ID
                    };
                    
                    processedSchedules.push(secondDaySchedule);
                  }
                });
                
                // Only update if something has actually changed to prevent flickering
                if (this.hasSchedulesChanged(this.schedules, processedSchedules)) {
                  this.schedules = processedSchedules;
                  console.log('Total schedules loaded for display (including second day entries):', this.schedules.length);
                } else {
                  console.log('No schedule changes detected, skipping UI update');
                }
              });
          })
          .catch(error => {
            console.error('Error fetching current display semester or schedules:', error);
            
            // Fallback to localStorage only if API fails
            this.loadSchedulesFromLocalStorage();
          });
      } catch (error) {
        console.error('Error in loadSchedulesWithoutFlicker:', error);
      }
    },
    loadSchedulesFromStorage() {
      this.loadSchedulesWithoutFlicker();
    },
    previousLab() {
      const currentIndex = this.labs.indexOf(this.selectedLab)
      if (currentIndex > 0) {
        this.selectedLab = this.labs[currentIndex - 1]
      }
    },
    nextLab() {
      const currentIndex = this.labs.indexOf(this.selectedLab)
      if (currentIndex < this.labs.length - 1) {
        this.selectedLab = this.labs[currentIndex + 1]
      }
    },
    generateWeekDays(date) {
      if (date) {
        this.currentDate = date;
      }
      
      const monday = new Date(this.currentDate);
      monday.setDate(this.currentDate.getDate() - this.currentDate.getDay() + 1);

      this.weekDays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'].map((name, index) => {
        const date = new Date(monday)
        date.setDate(monday.getDate() + index)
        
        // Format the date as "Mar 17, 2025" 
        const formattedDate = date.toLocaleDateString('en-US', { 
          month: 'short', 
          day: 'numeric', 
          year: 'numeric'
        });
        
        return {
          name,
          date: formattedDate
        }
      })
    },
    isTimeSlotInSchedule(timeSlot, startTime, endTime) {
      try {
        // Convert timeSlot, startTime, and endTime to minutes for easy comparison
        const timeSlotMinutes = this.convertTimeToMinutes(timeSlot);
        const startTimeMinutes = this.convertTimeToMinutes(startTime);
        const endTimeMinutes = this.convertTimeToMinutes(endTime);
        
        // Check if timeSlot is within or at the start of the schedule
        return timeSlotMinutes >= startTimeMinutes && timeSlotMinutes < endTimeMinutes;
      } catch (error) {
        console.error('Error checking if time slot is in schedule:', error);
        return false;
      }
    },
    convertTimeToMinutes(time) {
      try {
        // Parse time string (format: "HH:MM AM/PM")
        const [hourStr, minutePeriodStr] = time.split(':');
        if (!minutePeriodStr) {
          console.error('Invalid time format:', time);
          return 0;
        }
        
        const minutePeriod = minutePeriodStr.trim();
        const minuteStr = minutePeriod.split(' ')[0];
        const period = minutePeriod.split(' ')[1];
        
        if (!hourStr || !minuteStr || !period) {
          console.error('Invalid time components:', { hourStr, minuteStr, period });
          return 0;
        }
        
        let hour = parseInt(hourStr);
        const minute = parseInt(minuteStr);
        
        // Convert to 24-hour format
        if (period === 'PM' && hour < 12) hour += 12;
        if (period === 'AM' && hour === 12) hour = 0;
        
        const totalMinutes = hour * 60 + minute;
        
        // Return total minutes
        return totalMinutes;
      } catch (error) {
        console.error('Error converting time to minutes:', time, error);
        return 0;
      }
    },
    isTimeSlotWithinSchedule(dayName, timeSlot) {
      if (!this.schedules || this.schedules.length === 0) {
        return false;
      }
      
      const timeSlotMinutes = this.convertTimeToMinutes(timeSlot);
      
      // Filter by current lab room
      return this.schedules.some(schedule => {
        if (schedule.labRoom !== this.selectedLab || schedule.day !== dayName) {
          return false;
        }
        
        const startMinutes = this.convertTimeToMinutes(schedule.startTime);
        const endMinutes = this.convertTimeToMinutes(schedule.endTime);
        
        // Include the ending time slot as well
        return timeSlotMinutes >= startMinutes && timeSlotMinutes <= endMinutes;
      });
    },
    isScheduleStart(dayName, timeSlot) {
      if (!this.schedules || this.schedules.length === 0) {
        return false;
      }
      
      const timeSlotMinutes = this.convertTimeToMinutes(timeSlot);
      
      // Filter by current lab room
      return this.schedules.some(schedule => {
        if (schedule.labRoom !== this.selectedLab || schedule.day !== dayName) {
          return false;
        }
        
        const startMinutes = this.convertTimeToMinutes(schedule.startTime);
        return timeSlotMinutes === startMinutes;
      });
    },
    getScheduleTitle(dayName, timeSlot) {
      // Filter by current lab room
      const relevantSchedules = this.schedules.filter(schedule => {
        if (schedule.labRoom !== this.selectedLab || schedule.day !== dayName) {
          return false;
        }
        
        const startMinutes = this.convertTimeToMinutes(schedule.startTime);
        const slotMinutes = this.convertTimeToMinutes(timeSlot);
        
        return startMinutes === slotMinutes;
      });
      
      if (relevantSchedules.length === 0) return '';
      return relevantSchedules[0].title;
    },
    getScheduleTime(dayName, timeSlot) {
      // Filter by current lab room
      const relevantSchedules = this.schedules.filter(schedule => {
        if (schedule.labRoom !== this.selectedLab || schedule.day !== dayName) {
          return false;
        }
        
        const startMinutes = this.convertTimeToMinutes(schedule.startTime);
        const slotMinutes = this.convertTimeToMinutes(timeSlot);
        
        return startMinutes === slotMinutes;
      });
      
      if (relevantSchedules.length === 0) return '';
      return `${relevantSchedules[0].startTime} - ${relevantSchedules[0].endTime}`;
    },
    getScheduleDetails(dayName, timeSlot) {
      // Filter by current lab room
      const relevantSchedules = this.schedules.filter(schedule => {
        if (schedule.labRoom !== this.selectedLab || schedule.day !== dayName) {
          return false;
        }
        
        const startMinutes = this.convertTimeToMinutes(schedule.startTime);
        const slotMinutes = this.convertTimeToMinutes(timeSlot);
        
        return startMinutes === slotMinutes;
      });
      
      if (relevantSchedules.length === 0) return '';
      
      const schedule = relevantSchedules[0];
      return `${schedule.courseName}\n${schedule.section}\n${schedule.instructorName}`;
    },
    getScheduleStyle(dayName, timeSlot) {
      // Find the specific schedule that contains this time slot
      const schedule = this.schedules.find(schedule => {
        if (schedule.labRoom !== this.selectedLab || schedule.day !== dayName) {
          return false;
        }
        
        const slotMinutes = this.convertTimeToMinutes(timeSlot);
        const startMinutes = this.convertTimeToMinutes(schedule.startTime);
        const endMinutes = this.convertTimeToMinutes(schedule.endTime);
        
        return slotMinutes >= startMinutes && slotMinutes < endMinutes;
      });
      
      if (!schedule) return {};
      
      return {
        backgroundColor: schedule.color || '#DD385A'
      };
    },
    showScheduleDetails(dayName, timeSlot) {
      // Find the schedule for this day and timeSlot
      const relevantSchedules = this.schedules.filter(schedule => {
        if (schedule.labRoom !== this.selectedLab || schedule.day !== dayName) {
          return false;
        }
        
        const startMinutes = this.convertTimeToMinutes(schedule.startTime);
        const slotMinutes = this.convertTimeToMinutes(timeSlot);
        
        return startMinutes === slotMinutes;
      });
      
      if (relevantSchedules.length === 0) return;
      
      this.selectedSchedule = relevantSchedules[0];
      this.showPopup = true;
    },
    closePopup() {
      this.showPopup = false;
    },
    getUserName() {
      // Get user data from session or local storage
      const userStr = sessionStorage.getItem('user') || localStorage.getItem('user');
      if (userStr) {
        try {
          const userData = JSON.parse(userStr);
          if (userData.full_name) {
            // Get first name only
            this.userName = userData.full_name.split(' ')[0];
          }
        } catch (error) {
          console.error('Error parsing user data:', error);
        }
      }
    },
    getScheduleStatusClass(dayName, timeSlot) {
      // Find the specific schedule that contains this time slot
      const schedule = this.schedules.find(schedule => {
        if (schedule.labRoom !== this.selectedLab || schedule.day !== dayName) {
          return false;
        }
        
        const slotMinutes = this.convertTimeToMinutes(timeSlot);
        const startMinutes = this.convertTimeToMinutes(schedule.startTime);
        const endMinutes = this.convertTimeToMinutes(schedule.endTime);
        
        // Include the ending time slot as well
        return slotMinutes >= startMinutes && slotMinutes <= endMinutes;
      });
      
      if (!schedule) return '';
      
      return `status-${schedule.status.toLowerCase()}`;
    },
    calculateDurationMinutes(startTime, endTime) {
      try {
        const startMinutes = this.convertTimeToMinutes(startTime);
        const endMinutes = this.convertTimeToMinutes(endTime);
        return endMinutes - startMinutes;
      } catch (error) {
        console.error('Error calculating duration:', error);
        return 60; // Default to 60 minutes if calculation fails
      }
    },
    previousMonth() {
      if (this.$refs.calendar) {
        this.$refs.calendar.previousMonth();
      }
    },
    nextMonth() {
      if (this.$refs.calendar) {
        this.$refs.calendar.nextMonth();
      }
    },
    goToToday() {
      if (this.$refs.calendar) {
        this.$refs.calendar.goToToday();
      }
    },
    loadSchedulesFromLocalStorage() {
      try {
        console.warn('Falling back to localStorage for schedules');
        this.schedules = []; // Initialize as empty array
        
        // Try to get current display semester from localStorage (it might have been stored there)
        let currentDisplaySemesterId = null;
        const systemSettingsStr = localStorage.getItem('system_settings');
        if (systemSettingsStr) {
          try {
            const systemSettings = JSON.parse(systemSettingsStr);
            if (systemSettings && systemSettings.current_display_semester_id) {
              currentDisplaySemesterId = parseInt(systemSettings.current_display_semester_id);
              console.log(`Using current display semester ID from localStorage: ${currentDisplaySemesterId}`);
            }
          } catch (error) {
            console.error('Error parsing system settings from localStorage:', error);
          }
        }
        
        // First check for viewer_schedules
        const viewerSchedules = localStorage.getItem('viewer_schedules');
        if (viewerSchedules) {
          try {
            const parsedViewerSchedules = JSON.parse(viewerSchedules);
            if (Array.isArray(parsedViewerSchedules) && parsedViewerSchedules.length > 0) {
              // Only approved schedules
              let filteredSchedules = parsedViewerSchedules.filter(s => s.status === 'approved');
              
              // If we have a current semester ID, filter by it
              if (currentDisplaySemesterId && filteredSchedules.some(s => s.semester_id)) {
                filteredSchedules = filteredSchedules.filter(s => 
                  s.semester_id === currentDisplaySemesterId
                );
                console.log(`Filtered viewer schedules to semester ID ${currentDisplaySemesterId}:`, filteredSchedules.length);
              }
              
              this.schedules = filteredSchedules;
              console.log('Loaded from viewer schedules:', this.schedules.length);
              return; // Exit early
            }
          } catch (error) {
            console.error('Error parsing viewer schedules:', error);
          }
        }
        
        // Fallback to traditional sources
        let allSchedules = [];
        
        // Load system admin schedules
        const sysAdminSchedules = localStorage.getItem('sysadmin_schedules');
        if (sysAdminSchedules) {
          try {
            const parsedSysAdminSchedules = JSON.parse(sysAdminSchedules);
            if (Array.isArray(parsedSysAdminSchedules)) {
              const approvedSysAdminSchedules = parsedSysAdminSchedules.filter(schedule => schedule.status === 'approved');
              allSchedules = [...allSchedules, ...approvedSysAdminSchedules];
            }
          } catch (error) {
            console.error('Error parsing sysadmin schedules:', error);
          }
        }
        
        // Load academic coordinator schedules
        const acadCoorSchedules = localStorage.getItem('acad_coor_schedules');
        if (acadCoorSchedules) {
          try {
            const parsedAcadCoorSchedules = JSON.parse(acadCoorSchedules);
            if (Array.isArray(parsedAcadCoorSchedules)) {
              const approvedAcadCoorSchedules = parsedAcadCoorSchedules.filter(schedule => schedule.status === 'approved');
              allSchedules = [...allSchedules, ...approvedAcadCoorSchedules];
            }
          } catch (error) {
            console.error('Error parsing academic coordinator schedules:', error);
          }
        }
        
        // If we have a current semester ID, filter by it
        if (currentDisplaySemesterId && allSchedules.some(s => s.semester_id)) {
          allSchedules = allSchedules.filter(s => 
            s.semester_id === currentDisplaySemesterId
          );
          console.log(`Filtered all schedules to semester ID ${currentDisplaySemesterId}:`, allSchedules.length);
        }
        
        this.schedules = allSchedules;
        console.log('Loaded from localStorage fallback:', this.schedules.length);
      } catch (error) {
        console.error('Error loading schedules from localStorage:', error);
        this.schedules = []; // Ensure schedules is an array even if loading fails
      }
    },

    loadCurrentSemesterName() {
      systemSettingsAPI.getCurrentDisplaySemester()
        .then(response => {
          this.currentSemesterName = response.data.semester_name;
        })
        .catch(error => {
          console.error('Error fetching current semester name:', error);
        });
    }
  }
}
</script>

<style scoped>
* {
  font-family: 'Inter', sans-serif;
  box-sizing: border-box;
}

.dashboard-layout {
  display: flex;
  min-height: 100vh;
  background-color: #f5f5f5;
  width: 100%;
}

.main-content {
  flex: 1;
  margin-left: 70px;
  display: flex;
  flex-direction: column;
  width: calc(100% - 70px);
}

.content-wrapper {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
}

.semester-indicator {
  margin-top: 1rem;
  margin-left: -1rem; /* Adding negative left margin to move it more to the left */
}

.semester-box {
  background-color: #e91e63;
  color: white;
  padding: 0.5rem 1rem;
  margin-left: -53rem;
  border-radius: 4px;
  display: inline-block;
  font-weight: 500;
  
}

.dashboard-header {
  margin-bottom: 1.5rem;
}

.welcome-section h2 {
  color: #e91e63;
  font-size: 1.75rem;
  margin: 0;
  font-weight: 500;
}

.welcome-section .date {
  color: #666;
  margin: 5px 0 0 0;
  font-size: 1rem;
}

.dashboard-content {
  display: flex;
  gap: 1.5rem;
}

.left-panel {
  width: 340px;
  flex-shrink: 0;
}

.right-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.calendar-box {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.calendar-navigation {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 0.5rem 0;
}

.cal-nav-btn {
  background: none;
  border: none;
  color: #e91e63;
  font-size: 1.5rem;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.cal-nav-btn span {
  line-height: 1;
  position: relative;
  top: -2px;
}

.today-btn {
  background: #e91e63;
  border: none;
  color: white;
  padding: 0.5rem 1.5rem;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.controls-top {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-bottom: 1rem;
}

.search-box {
  display: flex;
  align-items: center;
  background: white;
  border-radius: 4px;
  padding: 0.5rem 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  width: 250px;
}

.search-icon {
  color: #999;
  margin-right: 0.5rem;
}

.search-box input {
  border: none;
  outline: none;
  font-size: 0.9rem;
  width: 100%;
}

.lab-dropdown-wrapper {
  width: 150px;
}

.lab-dropdown {
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 0.6rem 0.5rem;
  font-size: 0.9rem;
  color: #333;
  width: 100%;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23999' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 8px center;
  background-size: 16px;
  padding-right: 28px;
  cursor: pointer;
}

.schedule-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  position: relative;
  height: 100%;
}

.schedule-table {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.table-header {
  display: flex;
  border-bottom: 1px solid #eaeaea;
}

.time-header {
  width: 80px;
  padding: 0.75rem 0.5rem;
  text-align: center;
  font-weight: 500;
  color: #e91e63;
  font-size: 0.9rem;
  border-right: 1px solid #eaeaea;
}

.day-headers {
  flex: 1;
  display: flex;
}

.day-header {
  flex: 1;
  padding: 0.75rem 0.5rem;
  text-align: center;
  background-color: #e91e63;
  color: white;
  border-right: 1px solid rgba(255, 255, 255, 0.2);
}

.day-header:last-child {
  border-right: none;
}

.day-name {
  font-weight: 500;
  font-size: 0.9rem;
  margin-bottom: 0.25rem;
}

.day-date {
  font-size: 0.8rem;
  opacity: 0.9;
}

.table-body {
  display: flex;
  flex: 1;
  overflow-y: auto;
}

.time-column {
  width: 80px;
  flex-shrink: 0;
  border-right: 1px solid #eaeaea;
}

.time-slot {
  height: 60px;
  border-bottom: 1px solid #eaeaea;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  font-size: 0.85rem;
}

.days-grid {
  display: flex;
  flex: 1;
}

.day-column {
  flex: 1;
  border-right: 1px solid #eaeaea;
}

.day-column:last-child {
  border-right: none;
}

.time-slots {
  display: flex;
  flex-direction: column;
}

.slot {
  height: 60px;
  border-bottom: 1px solid #eaeaea;
  position: relative;
}

.schedule-item {
  position: absolute;
  left: 0;
  right: 0;
  top: 0;
  bottom: 0;
  background-color: #DD385A;
  color: white;
  padding: 0.5rem;
  overflow: hidden;
  z-index: 5;
}

.schedule-item.status-draft {
  background-color: #DD385A;
}

.schedule-item.status-pending {
  background-color: #DD385A;
}

.schedule-item.status-approved {
  background-color: #DD385A;
}

.schedule-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  cursor: pointer;
}

.schedule-lab {
  font-size: 0.7rem;
  opacity: 0.9;
  margin-bottom: 0.1rem;
}

.schedule-time {
  font-size: 0.7rem;
  margin-bottom: 0.2rem;
}

.schedule-title {
  font-size: 0.8rem;
  font-weight: 500;
}

.schedule-popup {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.popup-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background-color: #e91e63;
  color: white;
}

.popup-header h3 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 500;
}

.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.popup-body {
  padding: 1.5rem;
}

.detail-row {
  display: flex;
  margin-bottom: 1rem;
}

.detail-row:last-child {
  margin-bottom: 0;
}

.detail-label {
  width: 120px;
  font-weight: 500;
  color: #666;
}

.detail-value {
  flex: 1;
  color: #333;
}

@media (max-width: 1024px) {
  .dashboard-content {
    flex-direction: column;
  }
  
  .left-panel {
    width: 100%;
  }
}

@media (max-width: 768px) {
  .content-wrapper {
    padding: 1rem;
  }
  
  .controls-top {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-box {
    width: 100%;
    margin-bottom: 0.5rem;
  }
  
  .lab-dropdown-wrapper {
    width: 100%;
  }
}
</style>