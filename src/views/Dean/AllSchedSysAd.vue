<template>
  <div class="dashboard-layout" ref="scheduleComponent">
    <DashBoardSideBarDean />
    <div class="main-content">
      <DashBoardTopbar />
      <div class="content-wrapper">
        <div class="dashboard-header">
          <div class="welcome-section">
            <div class="header-content">
              <h2>Schedules Approval</h2>
              <div class="action-buttons" v-if="hasPendingSchedules">
                <button class="approve-btn" @click="approveSelectedSchedule">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M20 6L9 17l-5-5"/>
                  </svg>
                  Approve All
                </button>
                <button class="reject-btn" @click="rejectSelectedSchedule">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                  </svg>
                  Reject All
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="dashboard-content">
          <div class="right-panel">
            <div class="controls-top">
              
              <div class="semester-dropdown-wrapper">
                <select v-model="selectedSemester" class="semester-dropdown" @change="fetchCourseOfferings">
                  <option value="" disabled selected>Select Semester</option>
                  <option v-for="semester in semesters" :key="semester" :value="semester">{{ semester }}</option>
                </select>
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
                          >
                            <div 
                              v-if="isScheduleStart(day.name, time)" 
                              class="schedule-content"
                              @click="showScheduleDetails(day.name, time)"
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
            <span class="detail-value">{{ selectedSchedule.day }}{{ selectedSchedule.secondDay ? ' / ' + selectedSchedule.secondDay : '' }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Schedule Modal -->
    <div class="modal" v-if="showEditScheduleModal">
      <div class="modal-content">
        <div class="modal-header">
          <h2>Edit Schedule</h2>
          <button class="close-btn" @click="closeEditModal">×</button>
        </div>
        <div class="modal-body">
          <!-- Warning message for approved schedules -->
          <div v-if="selectedSchedule.status === 'approved'" class="status-warning">
            <i class="fas fa-exclamation-triangle"></i>
            Editing an approved schedule will change its status back to pending and require re-approval.
          </div>
          
          <div class="schedule-type-selector">
            <button 
              :class="['type-btn', { active: editSchedule.scheduleTypes.includes('Lab') }]" 
              @click="toggleScheduleType('Lab')"
            >Lab</button>
            <button 
              :class="['type-btn', { active: editSchedule.scheduleTypes.includes('Lec') }]" 
              @click="toggleScheduleType('Lec')"
            >Lec</button>
          </div>

          <div class="edit-form-layout">
            <div class="left-column">
              <div class="form-group">
                <label>Select Semester</label>
                <div class="select-wrapper">
                  <select v-model="editSchedule.semester" class="form-select" @change="refreshCourseDropdown">
                    <option v-for="semester in semesters" :key="semester" :value="semester">
                      {{ semester }}
                    </option>
                  </select>
                </div>
              </div>

              <div class="form-group">
                <label>Select Degree Program | Year & Section</label>
                <div class="select-wrapper">
                  <select v-model="editSchedule.section" class="form-select" @change="refreshCourseDropdown">
                    <option v-for="section in sectionOptions" :key="section" :value="section">
                      {{ section }}
                    </option>
                  </select>
                </div>
              </div>

              <div class="form-group">
                <label>Course Offered</label>
                <div class="select-wrapper">
                  <select v-model="editSchedule.courseCode" class="form-select" @focus="refreshCourseDropdown">
                    <option v-for="course in filteredCourseOfferings" :key="course.code" :value="course.code">
                      {{ course.code }} - {{ course.name }} {{ course.section ? `(${course.section})` : '' }} {{ course.semester ? `(${course.semester})` : '' }}
                    </option>
                    <option v-if="filteredCourseOfferings.length === 0" disabled>
                      No matching courses - try selecting a different semester or section
                    </option>
                  </select>
                </div>
              </div>
            </div>

            <div class="right-column">
              <div class="form-group">
                <label>Day</label>
                <div class="select-wrapper">
                  <select v-model="editSchedule.day" class="form-select">
                    <option v-for="day in days" :key="day" :value="day">{{ day }}</option>
                  </select>
                </div>
              </div>

              <div class="form-group">
                <label>Second Day (Optional)</label>
                <div class="select-wrapper">
                  <select v-model="editSchedule.secondDay" class="form-select">
                    <option value="">None</option>
                    <option v-for="day in days" :key="day" :value="day">{{ day }}</option>
                  </select>
                </div>
              </div>

              <div class="form-group">
                <label>Lab Room No.</label>
                <div class="select-wrapper">
                  <select v-model="editSchedule.labRoom" class="form-select">
                    <option v-for="lab in labs" :key="lab" :value="lab">{{ lab }}</option>
                  </select>
                </div>
              </div>

              <div class="form-group">
                <label>Start Time</label>
                <div class="time-picker">
                  <select v-model="editSchedule.startHour" class="time-select">
                    <option v-for="hour in timeHours" :key="'start-'+hour" :value="hour">
                      {{ hour.toString().padStart(2, '0') }}
                    </option>
                  </select>
                  <span>:</span>
                  <select v-model="editSchedule.startMinute" class="time-select">
                    <option value="00">00</option>
                    <option value="30">30</option>
                  </select>
                  <select v-model="editSchedule.startPeriod" class="period-select">
                    <option value="AM">AM</option>
                    <option value="PM">PM</option>
                  </select>
                </div>
              </div>

              <div class="form-group">
                <label>End Time</label>
                <div class="time-picker">
                  <select v-model="editSchedule.endHour" class="time-select">
                    <option v-for="hour in timeHours" :key="'end-'+hour" :value="hour">
                      {{ hour.toString().padStart(2, '0') }}
                    </option>
                  </select>
                  <span>:</span>
                  <select v-model="editSchedule.endMinute" class="time-select">
                    <option value="00">00</option>
                    <option value="30">30</option>
                  </select>
                  <select v-model="editSchedule.endPeriod" class="period-select">
                    <option value="AM">AM</option>
                    <option value="PM">PM</option>
                  </select>
                </div>
              </div>

              <div class="form-group">
                <label>Instructor Name</label>
                <div class="select-wrapper">
                  <select v-model="editSchedule.instructorName" class="form-select">
                    <option v-for="instructor in instructors" :key="instructor" :value="instructor">
                      {{ instructor }}
                    </option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="cancel-btn" @click="closeEditModal">Cancel</button>
          <button 
            class="update-btn" 
            @click="updateSchedule" 
            :disabled="!isEditFormValid"
          >Update</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import DashBoardSideBarDean from '../../components/DashBoardSideBarDean.vue'
import DashBoardTopbar from '../../components/DashBoardTopbar.vue'
import { scheduleAPI } from '../../services/api.js'
import axios from 'axios'
import { courseOfferingAPI } from '../../services/api.js'

export default {
  name: 'AllSchedSysAd',
  components: {
    DashBoardSideBarDean,
    DashBoardTopbar
  },
  data() {
    return {
      selectedLab: '',
      labs: [],
      labRoomsData: [], // Full lab room objects from API
      selectedSemester: '',
      semesters: [],
      semestersData: [], // Full semester objects from API
      displayTimeSlots: [
        '7:30 AM', '8:00 AM', '8:30 AM', '9:00 AM', '9:30 AM', '10:00 AM',
        '10:30 AM', '11:00 AM', '11:30 AM', '12:00 PM', '12:30 PM', '1:00 PM',
        '1:30 PM', '2:00 PM', '2:30 PM', '3:00 PM', '3:30 PM', '4:00 PM',
        '4:30 PM', '5:00 PM', '5:30 PM', '6:00 PM', '6:30 PM', '7:00 PM',
        '7:30 PM', '8:00 PM'
      ],
      schedules: [],
      allSchedules: [], // To store all schedules before filtering
      weekDays: [],
      showPopup: false,
      selectedSchedule: {},
      userName: 'User',
      pollInterval: null, // For storing the polling interval
      lastUpdateTimestamp: null, // To track the last update time

      // New properties for edit functionality
      showEditScheduleModal: false,
      days: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
      timeHours: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
      instructors: [],
      instructorsData: [], // Full instructor objects from API
      courseOfferings: [], // Course offerings from Excel file
      sectionOptions: [
        'BSIT 1A', 'BSIT 1B',
        'BSCS 1A',
        'BSIT 2A', 'BSIT 2B',
        'BSCS 2A',
        'BSIT 3A', 'BSIT 3B',
        'BSCS 3A',
        'BSIT 4A', 'BSIT 4B',
        'BSCS 4A'
      ],
      editSchedule: {
        id: null,
        semester: '',
        section: '',
        courseCode: '',
        day: '',
        labRoom: '',
        instructorName: '',
        startHour: '',
        startMinute: '00',
        startPeriod: 'AM',
        endHour: '',
        endMinute: '00',
        endPeriod: 'AM',
        secondDay: '',
        scheduleTypes: []
      }
    }
  },
  created() {
    this.checkAuth();
    // Start polling for updates
    this.startPolling();
    // Fetch data for dropdowns - first semesters, then the rest
    this.fetchSemesters();
    this.fetchLabRooms();
    this.fetchInstructors();
    // Note: Course offerings will be fetched after semesters are loaded
  },
  beforeDestroy() {
    // Clean up polling when component is destroyed
    this.stopPolling();
  },
  mounted() {
    this.checkAuth();
    this.getUserName();
    this.loadSchedulesFromStorage();
    this.generateWeekDays();
    this.loadPendingSchedules();
    this.loadRegistrationRequests();
  },
  watch: {
    selectedSemester: {
      handler(newSemester) {
        this.filterSchedulesBySemester();
      },
      immediate: true
    },
    // Add watchers for the edit form filters
    'editSchedule.semester': function(newValue) {
      console.log('Selected semester changed in edit form:', newValue);
      // The filteredCourseOfferings computed property will update automatically
    },
    'editSchedule.section': function(newValue) {
      console.log('Selected section changed in edit form:', newValue);
      // The filteredCourseOfferings computed property will update automatically
    }
  },
  computed: {
    hasPendingSchedules() {
      return this.allSchedules.some(schedule => 
        schedule.status === 'pending' &&
        schedule.semester === this.selectedSemester
      );
    },
    isEditFormValid() {
      // Basic validation - we allow partial edits so just make sure we have a schedule ID
      return this.editSchedule.id !== null;
    },
    // Add a computed property to filter course offerings based on selected semester and section
    filteredCourseOfferings() {
      // Start with all courses
      let filteredCourses = [...this.courseOfferings];
      console.log('Initial courses for filtering:', filteredCourses.length);
      
      // First filter by selected semester in edit modal if available
      if (this.editSchedule.semester) {
        const selectedSemester = this.editSchedule.semester;
        console.log('Filtering courses by semester:', selectedSemester);
        
        // Extract semester type (1st Sem, 2nd Sem, Summer) from active semester
        let selectedSemesterType = '';
        if (selectedSemester.includes('1st Sem')) {
          selectedSemesterType = '1st Sem';
        } else if (selectedSemester.includes('2nd Sem')) {
          selectedSemesterType = '2nd Sem';
        } else if (selectedSemester.includes('Summer')) {
          selectedSemesterType = 'Summer';
        }
        
        console.log(`Selected semester type: "${selectedSemesterType}"`);
        
        // Filter courses based on semester type rather than exact semester
        if (selectedSemesterType) {
          filteredCourses = filteredCourses.filter(course => {
            // Extract semester type from course semester
            let courseSemesterType = '';
            if (course.semester && typeof course.semester === 'string') {
              if (course.semester.includes('1st Sem')) {
                courseSemesterType = '1st Sem';
              } else if (course.semester.includes('2nd Sem')) {
                courseSemesterType = '2nd Sem';
              } else if (course.semester.includes('Summer')) {
                courseSemesterType = 'Summer';
              }
            }
            
            const matches = courseSemesterType === selectedSemesterType;
            if (matches) {
              console.log(`Course ${course.code} semester type "${courseSemesterType}" matches "${selectedSemesterType}"`);
            }
            return matches;
          });
          
          console.log(`After semester type filter: ${filteredCourses.length} courses remain`);
          
          // Now update the semester display for all filtered courses to match the active semester
          filteredCourses = filteredCourses.map(course => {
            return {
              ...course,
              originalSemester: course.semester, // Keep original semester for reference
              semester: selectedSemester, // Update to active semester for display
            };
          });
          
          console.log('Courses with updated semester display:', 
            filteredCourses.map(c => `${c.code} (${c.semester}, original: ${c.originalSemester})`));
        }
      }
      
      // Filter by selected section if available
      if (this.editSchedule.section) {
        filteredCourses = filteredCourses.filter(course => 
          !course.section || course.section === this.editSchedule.section
        );
        console.log('After section filtering:', filteredCourses.length);
      }
      
      return filteredCourses;
    }
  },
  methods: {
    checkAuth() {
      // Check if user is authenticated and has the correct role
      const token = sessionStorage.getItem('token') || localStorage.getItem('token');
      const userStr = sessionStorage.getItem('user') || localStorage.getItem('user');
      
      if (!token || !userStr) {
        console.error('No authentication found, redirecting to login');
        this.$router.push('/login');
        return;
      }
      
      try {
        const userData = JSON.parse(userStr);
        
        // Verify the user has either System Administrator or Dean role
        if (userData.role !== 'System Administrator' && userData.role !== 'Dean') {
          console.error('User does not have permission to view this page');
          // Redirect to the appropriate dashboard based on role
          if (userData.role === 'Academic Coordinator') {
            this.$router.push('/dashboard-acad-coor');
          } else if (userData.role === 'Lab InCharge') {
            this.$router.push('/dashboard-lab');
          } else {
            this.$router.push('/dashboard-viewer');
          }
        }
      } catch (error) {
        console.error('Error parsing user data:', error);
        this.$router.push('/login');
      }
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
    generateWeekDays() {
      // Simply use the fixed days without dates
      this.weekDays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'].map(name => {
        return { name }
      });
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
        // Check if this day matches the schedule day
        // (we don't need to check secondDay because we already created separate entries for secondDay)
        if (schedule.labRoom !== this.selectedLab || schedule.day !== dayName) {
          return false;
        }
        
        const startMinutes = this.convertTimeToMinutes(schedule.startTime);
        const endMinutes = this.convertTimeToMinutes(schedule.endTime);
        
        // Include the ending time slot as well - exactly like in schedule-management
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
        // We no longer need to check secondDay since we created separate entries
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
        // We no longer need to check secondDay since we created separate entries
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
        // Check if day matches primary day OR secondary day
        const dayMatches = schedule.day === dayName || schedule.secondDay === dayName;
        
        if (schedule.labRoom !== this.selectedLab || !dayMatches) {
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
        // Check if day matches primary day OR secondary day
        const dayMatches = schedule.day === dayName || schedule.secondDay === dayName;
        
        if (schedule.labRoom !== this.selectedLab || !dayMatches) {
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
    getScheduleStatusClass(dayName, timeSlot) {
      // Find the specific schedule that contains this time slot
      const schedule = this.schedules.find(s => {
        // We no longer need to check secondDay since we created separate entries
        if (s.labRoom !== this.selectedLab || s.day !== dayName) {
          return false;
        }
        
        const slotMinutes = this.convertTimeToMinutes(timeSlot);
        const startMinutes = this.convertTimeToMinutes(s.startTime);
        const endMinutes = this.convertTimeToMinutes(s.endTime);
        
        // Include the ending time slot as well
        return slotMinutes >= startMinutes && slotMinutes <= endMinutes;
      });
      
      if (!schedule) return '';
      
      // Return a CSS class based on the schedule status
      return schedule.status === 'pending' ? 'pending-schedule' : 'approved-schedule';
    },
    loadSchedulesFromStorage() {
      try {
        // First check if the user is still authenticated
        const token = sessionStorage.getItem('token') || localStorage.getItem('token');
        if (!token) {
          console.error('No token found when loading schedules');
          return;
        }

        // Initialize empty schedules array
        this.allSchedules = [];
        
        // Load both pending and approved schedules from the database
        Promise.all([
          scheduleAPI.getByStatus('pending'),
          scheduleAPI.getByStatus('approved')
        ])
        .then(([pendingResponse, approvedResponse]) => {
          const pendingSchedules = pendingResponse.data || [];
          const approvedSchedules = approvedResponse.data || [];
          
          console.log(`Loaded ${pendingSchedules.length} pending and ${approvedSchedules.length} approved schedules from API`);
          
          // Combine all schedules
          const allSchedulesFromAPI = [...pendingSchedules, ...approvedSchedules];
          
          // Convert API response format to frontend format and handle second_day
          const processedSchedules = [];
          
          allSchedulesFromAPI.forEach(schedule => {
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
              details: `${schedule.course_name}\n${schedule.section}\n${schedule.instructor_name}`
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
          
          this.allSchedules = processedSchedules;
          
          console.log('Total schedules loaded from API (including second day entries):', this.allSchedules.length);
          
          // Apply initial filtering based on selected semester
          this.filterSchedulesBySemester();
        })
        .catch(error => {
          console.error('Error fetching schedules from API:', error);
          this.allSchedules = [];
          this.schedules = [];
          
          // Fallback to localStorage only if API fails
          this.loadSchedulesFromLocalStorage();
        });
      } catch (error) {
        console.error('Error in loadSchedulesFromStorage:', error);
        this.schedules = [];
      }
    },
    loadSchedulesFromLocalStorage() {
      try {
        console.warn('Falling back to localStorage for schedules');
        // Initialize empty schedules array
        this.allSchedules = [];
        
        // 1. Lab schedules
        const labSchedules = localStorage.getItem('labSchedules');
        if (labSchedules) {
          try {
            const parsedLabData = JSON.parse(labSchedules);
            const labSchedulesArray = Array.isArray(parsedLabData) ? parsedLabData : (parsedLabData.schedules || []);
            this.allSchedules = [...this.allSchedules, ...labSchedulesArray];
          } catch (e) {
            console.error('Error parsing lab schedules from localStorage:', e);
          }
        }
        
        // 2. System Admin schedules
        const sysAdminSchedules = localStorage.getItem('sysadmin_schedules');
        if (sysAdminSchedules) {
          try {
            const parsedSysAdminData = JSON.parse(sysAdminSchedules);
            const sysAdminSchedulesArray = Array.isArray(parsedSysAdminData) ? parsedSysAdminData : (parsedSysAdminData.schedules || []);
            this.allSchedules = [...this.allSchedules, ...sysAdminSchedulesArray];
          } catch (e) {
            console.error('Error parsing system admin schedules from localStorage:', e);
          }
        }
        
        // 3. Academic Coordinator schedules
        const acadCoorSchedules = localStorage.getItem('acad_coor_schedules');
        if (acadCoorSchedules) {
          try {
            const parsedAcadCoorData = JSON.parse(acadCoorSchedules);
            const acadCoorSchedulesArray = Array.isArray(parsedAcadCoorData) ? parsedAcadCoorData : (parsedAcadCoorData.schedules || []);
            this.allSchedules = [...this.allSchedules, ...acadCoorSchedulesArray];
          } catch (e) {
            console.error('Error parsing academic coordinator schedules from localStorage:', e);
          }
        }
        
        // Remove duplicates based on schedule ID
        const uniqueSchedules = [];
        const seen = new Set();
        this.allSchedules.forEach(schedule => {
          if (!seen.has(schedule.id)) {
            seen.add(schedule.id);
            uniqueSchedules.push(schedule);
          }
        });
        
        this.allSchedules = uniqueSchedules;
        console.log('Total unique schedules loaded from localStorage:', this.allSchedules.length);
        
        // Apply initial filtering based on selected semester
        this.filterSchedulesBySemester();
      } catch (error) {
        console.error('Error in loadSchedulesFromLocalStorage:', error);
      }
    },
    filterSchedulesBySemester() {
      console.log('Filtering by semester:', this.selectedSemester);
      
      if (!this.selectedSemester || !this.allSchedules) {
        this.schedules = [];
        return;
      }
      
      // Show both pending and approved schedules in All Schedules view
      this.schedules = this.allSchedules.filter(schedule => 
        schedule.semester === this.selectedSemester &&
        (schedule.status === 'pending' || schedule.status === 'approved')
      );
      
      console.log(`Filtered ${this.schedules.length} schedules for semester ${this.selectedSemester}`);
    },
    showScheduleDetails(dayName, timeSlot) {
      // Find the schedule for this day and timeSlot
      const relevantSchedules = this.schedules.filter(schedule => {
        // Check if day matches primary day OR secondary day
        const dayMatches = schedule.day === dayName || schedule.secondDay === dayName;
        
        if (schedule.labRoom !== this.selectedLab || !dayMatches) {
          return false;
        }
        
        const startMinutes = this.convertTimeToMinutes(schedule.startTime);
        const slotMinutes = this.convertTimeToMinutes(timeSlot);
        
        return startMinutes === slotMinutes;
      });
      
      if (relevantSchedules.length === 0) return;
      
      this.selectedSchedule = relevantSchedules[0];
      
      // Show the edit modal for both pending and approved schedules
      if (this.selectedSchedule.status === 'pending' || this.selectedSchedule.status === 'approved') {
        this.setupEditForm();
        this.showEditScheduleModal = true;
      } else {
        this.showPopup = true;
      }
    },
    closePopup() {
      this.showPopup = false;
    },
    loadPendingSchedules() {
      try {
        // First check if the user is still authenticated
        const token = sessionStorage.getItem('token') || localStorage.getItem('token');
        if (!token) {
          console.error('No token found when loading pending schedules');
          return;
        }
        
        // Load pending schedules logic would go here
        console.log('Loading pending schedules...');
      } catch (error) {
        console.error('Error in loadPendingSchedules:', error);
      }
    },
    loadRegistrationRequests() {
      try {
        // First check if the user is still authenticated
        const token = sessionStorage.getItem('token') || localStorage.getItem('token');
        if (!token) {
          console.error('No token found when loading registration requests');
          return;
        }
        
        // Load registration requests logic would go here
        console.log('Loading registration requests...');
      } catch (error) {
        console.error('Error in loadRegistrationRequests:', error);
      }
    },
    approveSelectedSchedule() {
      // Get all pending schedules for current semester across ALL labs
      const pendingSchedules = this.allSchedules.filter(schedule => 
        schedule.status === 'pending' &&
        schedule.semester === this.selectedSemester
        // No lab filter here to include all labs
      );

      if (pendingSchedules.length === 0) {
        alert('No pending schedules to approve for the selected semester');
        return;
      }

      try {
        // Create an array of promises for all status updates
        const updatePromises = pendingSchedules.map(schedule => 
          scheduleAPI.updateStatus(schedule.id, 'approved')
        );
        
        // Execute all update requests in parallel
        Promise.all(updatePromises)
          .then(responses => {
            console.log('All schedules approved successfully:', responses);
            
            // Update local data to reflect the changes
            this.allSchedules = this.allSchedules.map(schedule => {
              if (pendingSchedules.some(pending => pending.id === schedule.id)) {
                return { ...schedule, status: 'approved' };
              }
              return schedule;
            });
            
            // Refresh the filtered schedules
            this.filterSchedulesBySemester();
            
            // Close the popup if it's open
            this.closePopup();
            
            // Display success message
            alert(`${pendingSchedules.length} schedule(s) approved successfully. All users will be notified.`);
            
            // Reload schedules from API to ensure data consistency
            this.loadSchedulesFromStorage();
          })
          .catch(error => {
            console.error('Error approving schedules:', error);
            alert('Error approving schedules. Please try again.');
          });
      } catch (error) {
        console.error('Error approving schedules:', error);
        alert('Error approving schedules. Please try again.');
      }
    },
    rejectSelectedSchedule() {
      // Get all pending schedules for current semester across ALL labs
      const pendingSchedules = this.allSchedules.filter(schedule => 
        schedule.status === 'pending' &&
        schedule.semester === this.selectedSemester
        // No lab filter here to include all labs
      );

      if (pendingSchedules.length === 0) {
        alert('No pending schedules to reject for the selected semester');
        return;
      }

      try {
        // Create an array of promises for all status updates
        const updatePromises = pendingSchedules.map(schedule => 
          scheduleAPI.updateStatus(schedule.id, 'draft')
        );
        
        // Execute all update requests in parallel
        Promise.all(updatePromises)
          .then(responses => {
            console.log('All schedules rejected successfully:', responses);
            
            // Update local data to reflect the changes
            this.allSchedules = this.allSchedules.map(schedule => {
              if (pendingSchedules.some(pending => pending.id === schedule.id)) {
                return { ...schedule, status: 'draft' };
              }
              return schedule;
            });
            
            // Refresh the filtered schedules
            this.filterSchedulesBySemester();
            
            // Close the popup if it's open
            this.closePopup();
            
            alert(`${pendingSchedules.length} schedule(s) rejected and sent back to draft`);
            
            // Reload schedules from API to ensure data consistency
            this.loadSchedulesFromStorage();
          })
          .catch(error => {
            console.error('Error rejecting schedules:', error);
            alert('Error rejecting schedules. Please try again.');
          });
      } catch (error) {
        console.error('Error rejecting schedules:', error);
        alert('Error rejecting schedules. Please try again.');
      }
    },
    calculateDurationMinutes(startTime, endTime) {
      try {
        const startMinutes = this.convertTimeToMinutes(startTime);
        const endMinutes = this.convertTimeToMinutes(endTime);
        return endMinutes - startMinutes;
      } catch (error) {
        console.error('Error calculating duration:', error);
        return 60;
      }
    },
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
    loadSchedulesWithoutFlicker() {
      try {
        // First check if the user is still authenticated
        const token = sessionStorage.getItem('token') || localStorage.getItem('token');
        if (!token) {
          console.error('No token found when loading schedules');
          return;
        }

        // Load both pending and approved schedules from the database without UI updates
        Promise.all([
          scheduleAPI.getByStatus('pending'),
          scheduleAPI.getByStatus('approved')
        ])
        .then(([pendingResponse, approvedResponse]) => {
          const pendingSchedules = pendingResponse.data || [];
          const approvedSchedules = approvedResponse.data || [];
          
          // Combine all schedules
          const allSchedulesFromAPI = [...pendingSchedules, ...approvedSchedules];
          
          // Convert API response format to frontend format and handle second_day
          const processedSchedules = [];
          
          allSchedulesFromAPI.forEach(schedule => {
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
              details: `${schedule.course_name}\n${schedule.section}\n${schedule.instructor_name}`
            };
            
            // Always add the primary day schedule
            processedSchedules.push(baseSchedule);
            
            // If there's a second day, create a separate schedule object for it
            if (schedule.second_day) {
              // Create a duplicate entry but with the second_day as the primary day
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
          
          // Only update the allSchedules array if something has actually changed
          // This prevents unnecessary re-renders
          if (this.hasSchedulesChanged(this.allSchedules, processedSchedules)) {
            this.allSchedules = processedSchedules;
            // Apply filtering based on selected semester
            this.filterSchedulesBySemester();
          }
        })
        .catch(error => {
          console.error('Error fetching schedules from API:', error);
        });
      } catch (error) {
        console.error('Error in loadSchedulesWithoutFlicker:', error);
      }
    },
    hasSchedulesChanged(oldSchedules, newSchedules) {
      // Quick length check
      if (oldSchedules.length !== newSchedules.length) {
        return true;
      }
      
      // Create a map of IDs to statuses for quick lookups
      const oldScheduleMap = new Map();
      oldSchedules.forEach(schedule => {
        oldScheduleMap.set(schedule.id, schedule.status);
      });
      
      // Check if any schedule has a different status
      for (const schedule of newSchedules) {
        if (!oldScheduleMap.has(schedule.id) || oldScheduleMap.get(schedule.id) !== schedule.status) {
          return true;
        }
      }
      
      return false;
    },
    checkForUpdates() {
      try {
        // Get the latest schedules from localStorage
        const latestSchedules = localStorage.getItem('schedules');
        if (!latestSchedules) return;

        const parsedSchedules = JSON.parse(latestSchedules);
        const latestTimestamp = parsedSchedules.timestamp || 0;

        // If this is the first check or if there's a new update
        if (!this.lastUpdateTimestamp || latestTimestamp > this.lastUpdateTimestamp) {
          console.log('New schedule updates detected, refreshing data...');
          this.loadSchedulesFromStorage();
          this.lastUpdateTimestamp = latestTimestamp;
        }
      } catch (error) {
        console.error('Error checking for updates:', error);
      }
    },
    clearAllSchedules() {
      if (confirm('Are you sure you want to clear all schedules? This action cannot be undone.')) {
        scheduleAPI.deleteAll()
          .then(response => {
            console.log('All schedules deleted from database:', response);
            
            // Reset the component's schedule arrays
            this.allSchedules = [];
            this.schedules = [];
            
            alert('All schedules cleared successfully');
          })
          .catch(error => {
            console.error('Error clearing all schedules:', error);
            alert('Error clearing schedules. Please try again.');
          });
      }
    },
    mergeSchedules(existingSchedules, newSchedules) {
      const seen = new Set();
      const mergedSchedules = [];

      existingSchedules.forEach(schedule => {
        if (!seen.has(schedule.id)) {
          seen.add(schedule.id);
          mergedSchedules.push(schedule);
        }
      });

      newSchedules.forEach(schedule => {
        if (!seen.has(schedule.id)) {
          seen.add(schedule.id);
          mergedSchedules.push(schedule);
        }
      });

      return mergedSchedules;
    },
    setupEditForm() {
      // Reset the edit form with current values
      this.editSchedule = {
        id: this.selectedSchedule.id,
        semester: this.selectedSchedule.semester || '',
        section: this.selectedSchedule.section || '',
        courseCode: this.selectedSchedule.courseCode || '',
        day: this.selectedSchedule.day || '',
        labRoom: this.selectedSchedule.labRoom || '',
        instructorName: this.selectedSchedule.instructorName || '',
        startHour: '',
        startMinute: '00',
        startPeriod: 'AM',
        endHour: '',
        endMinute: '00',
        endPeriod: 'AM',
        secondDay: this.selectedSchedule.secondDay || '',
        scheduleTypes: this.selectedSchedule.types || []
      };
      
      // Pre-fill current time values for reference
      if (this.selectedSchedule.startTime) {
        const startTimeParts = this.parseTime(this.selectedSchedule.startTime);
        if (startTimeParts) {
          this.editSchedule.startHour = startTimeParts.hour;
          this.editSchedule.startMinute = startTimeParts.minute;
          this.editSchedule.startPeriod = startTimeParts.period;
        }
      }
      
      if (this.selectedSchedule.endTime) {
        const endTimeParts = this.parseTime(this.selectedSchedule.endTime);
        if (endTimeParts) {
          this.editSchedule.endHour = endTimeParts.hour;
          this.editSchedule.endMinute = endTimeParts.minute;
          this.editSchedule.endPeriod = endTimeParts.period;
        }
      }
    },
    parseTime(timeStr) {
      try {
        // Parse time string like "9:00 AM"
        const [timePart, period] = timeStr.split(' ');
        const [hourStr, minuteStr] = timePart.split(':');
        
        return {
          hour: parseInt(hourStr),
          minute: minuteStr,
          period: period
        };
      } catch (error) {
        console.error('Error parsing time:', error);
        return null;
      }
    },
    closeEditModal() {
      this.showEditScheduleModal = false;
      this.selectedSchedule = {};
      this.editSchedule = {
        id: null,
        semester: '',
        section: '',
        courseCode: '',
        day: '',
        labRoom: '',
        instructorName: '',
        startHour: '',
        startMinute: '00',
        startPeriod: 'AM',
        endHour: '',
        endMinute: '00',
        endPeriod: 'AM',
        secondDay: '',
        scheduleTypes: []
      };
    },
    updateSchedule() {
      // Store the original status to check if it was approved
      const wasApproved = this.selectedSchedule.status === 'approved';
      
      // Find the semester ID from semestersData
      const semesterObj = this.semestersData.find(s => s.name === this.editSchedule.semester);
      // Find the lab room ID from labRoomsData
      const labRoomObj = this.labRoomsData.find(l => l.name === this.editSchedule.labRoom);
      
      // Check if we found the objects
      if (!semesterObj && this.editSchedule.semester) {
        console.warn(`Could not find semester object for: ${this.editSchedule.semester}`);
        console.log('Available semesters:', this.semestersData);
      }
      
      if (!labRoomObj && this.editSchedule.labRoom) {
        console.warn(`Could not find lab room object for: ${this.editSchedule.labRoom}`);
        console.log('Available lab rooms:', this.labRoomsData);
      }
      
      // Build the update data based on what was changed
      const updateData = {
        id: this.editSchedule.id
      };
      
      // Only include fields that were changed and are valid
      if (semesterObj) {
        updateData.semester_id = semesterObj.id;
        console.log(`Setting semester_id to ${semesterObj.id} from ${semesterObj.name}`);
      }
      
      if (this.editSchedule.section) {
        updateData.section = this.editSchedule.section;
        console.log(`Setting section to ${this.editSchedule.section}`);
      }
      
      if (this.editSchedule.courseCode) {
        updateData.course_code = this.editSchedule.courseCode;
        
        // Try to find the course from filteredCourseOfferings to get the most up-to-date version
        const courseObj = this.filteredCourseOfferings.find(c => c.code === this.editSchedule.courseCode);
        
        if (courseObj) {
          updateData.course_name = courseObj.name;
          console.log(`Setting course_code to ${courseObj.code} and course_name to ${courseObj.name}`);
          
          // Check if the course has an originalSemester property and it differs from the current semester
          const needsNewCourseOffering = courseObj.originalSemester !== undefined && 
                                       courseObj.originalSemester !== this.editSchedule.semester;
          
          if (needsNewCourseOffering && semesterObj) {
            console.log(`Selected course needs a new course offering - original semester: ${courseObj.originalSemester}, new semester: ${this.editSchedule.semester}`);
            
            // Create a new course offering in the database
            const newCourseData = {
              code: courseObj.code,
              name: courseObj.name,
              year_and_section: this.editSchedule.section,
              semester_id: semesterObj.id
            };
            
            courseOfferingAPI.create(newCourseData)
              .then(response => {
                console.log('Created new course offering for semester change:', response.data);
                // Refresh course offerings
                this.fetchCourseOfferings();
              })
              .catch(error => {
                console.error('Error creating course offering for semester change:', error);
                // Continue with schedule update, just won't have real course offering in database
              });
          }
        } else {
          // If we can't find the course name in filteredCourseOfferings, use the existing course name
          // from the selectedSchedule to ensure we always include it
          updateData.course_name = this.selectedSchedule.courseName || '';
          console.log(`Setting course_code to ${this.editSchedule.courseCode} with existing course name: ${updateData.course_name}`);
        }
      }
      
      if (this.editSchedule.day) {
        updateData.day = this.editSchedule.day;
        console.log(`Setting day to ${this.editSchedule.day}`);
      }
      
      if (labRoomObj) {
        updateData.lab_room_id = labRoomObj.id;
        console.log(`Setting lab_room_id to ${labRoomObj.id} from ${labRoomObj.name}`);
      }
      
      if (this.editSchedule.instructorName) {
        updateData.instructor_name = this.editSchedule.instructorName;
        console.log(`Setting instructor_name to ${this.editSchedule.instructorName}`);
      }
      
      if (this.editSchedule.scheduleTypes && this.editSchedule.scheduleTypes.length > 0) {
        updateData.schedule_types = this.editSchedule.scheduleTypes;
        console.log(`Setting schedule_types to ${JSON.stringify(this.editSchedule.scheduleTypes)}`);
        
        // Set class_type based on scheduleTypes
        if (this.editSchedule.scheduleTypes.includes('Lab') && this.editSchedule.scheduleTypes.includes('Lec')) {
          updateData.class_type = 'lab/lec';
        } else if (this.editSchedule.scheduleTypes.includes('Lab')) {
          updateData.class_type = 'lab';
        } else if (this.editSchedule.scheduleTypes.includes('Lec')) {
          updateData.class_type = 'lec';
        } else {
          // Default to existing class_type or 'lab' as fallback
          updateData.class_type = this.selectedSchedule.class_type || 'lab';
        }
        console.log(`Setting class_type to ${updateData.class_type}`);
      } else {
        // If no schedule types are selected, use existing class_type or default to 'lab'
        updateData.class_type = this.selectedSchedule.class_type || 'lab';
        console.log(`No schedule types selected, setting class_type to ${updateData.class_type}`);
      }
      
      // Handle second day separately (it can be set to empty)
      updateData.second_day = this.editSchedule.secondDay;
      console.log(`Setting second_day to ${this.editSchedule.secondDay || 'empty string'}`);
      
      // Handle time updates only if hours are provided
      if (this.editSchedule.startHour && this.editSchedule.endHour) {
        updateData.start_time = `${this.editSchedule.startHour}:${this.editSchedule.startMinute} ${this.editSchedule.startPeriod}`;
        updateData.end_time = `${this.editSchedule.endHour}:${this.editSchedule.endMinute} ${this.editSchedule.endPeriod}`;
        console.log(`Setting start_time to ${updateData.start_time} and end_time to ${updateData.end_time}`);
      } else {
        console.warn('Start or end hour not provided, not updating times');
      }
      
      // If the schedule was previously approved, first change its status to pending
      if (wasApproved) {
        this.changeScheduleStatus(this.editSchedule.id, 'pending', () => {
          // After status update, proceed with the content update
          this.updateScheduleContent(updateData);
        });
      } else {
        // For pending schedules, just update the content directly
        this.updateScheduleContent(updateData);
      }
    },
    
    // New helper method to update schedule status
    changeScheduleStatus(scheduleId, newStatus, callback) {
      scheduleAPI.updateStatus(scheduleId, newStatus)
        .then(response => {
          console.log(`Schedule ${scheduleId} status changed to ${newStatus}:`, response.data);
          
          // Update status in local data
          const index = this.allSchedules.findIndex(s => s.id === scheduleId);
          if (index !== -1) {
            this.allSchedules[index].status = newStatus;
          }
          
          // Call the callback function to continue with content update
          if (callback) callback();
        })
        .catch(error => {
          console.error(`Error changing schedule status to ${newStatus}:`, error);
          let errorMessage = `Error changing schedule status to ${newStatus}. Please try again.`;
          
          if (error.response) {
            console.error('Error response:', error.response.data);
            errorMessage = error.response.data.detail || errorMessage;
          }
          
          alert(errorMessage);
        });
    },
    
    // New helper method to update schedule content
    updateScheduleContent(updateData) {
      console.log("Sending update for schedule:", this.editSchedule.id, "with data:", updateData);
      
      // Update using the API
      scheduleAPI.update(this.editSchedule.id, updateData)
        .then(response => {
          console.log('Schedule updated successfully, backend response:', response.data);
          
          // Check if the response contains the updated schedule data
          if (response.data && (response.data.id || response.data.schedule_id)) {
            // Update the schedule in our local arrays using the returned data
            this.updateLocalSchedule(response.data);
          } else {
            console.log('Backend did not return schedule data, reloading from storage instead');
            // If no schedule data in response, refresh schedules from storage
            this.loadSchedulesFromStorage();
          }
          
          // Close the modal
          this.closeEditModal();
        })
        .catch(error => {
          console.error('Error updating schedule:', error);
          
          let errorMessage = 'Error updating schedule. Please try again.';
          if (error.response) {
            console.error('Error response data:', error.response.data);
            console.error('Error response status:', error.response.status);
            console.error('Error response headers:', error.response.headers);
            errorMessage = error.response.data.detail || errorMessage;
          }
          
          alert(errorMessage);
        });
    },
    updateLocalSchedule(updatedSchedule) {
      // Find and update the schedule in allSchedules
      const index = this.allSchedules.findIndex(s => s.id === updatedSchedule.id);
      if (index !== -1) {
        // Map the API response to our frontend format
        const updatedScheduleFormatted = {
          ...this.allSchedules[index],
          semester: updatedSchedule.semester_name,
          section: updatedSchedule.section,
          courseCode: updatedSchedule.course_code,
          courseName: updatedSchedule.course_name,
          day: updatedSchedule.day,
          secondDay: updatedSchedule.second_day,
          labRoom: updatedSchedule.lab_room_name,
          instructorName: updatedSchedule.instructor_name,
          startTime: updatedSchedule.start_time,
          endTime: updatedSchedule.end_time,
          types: updatedSchedule.schedule_types,
          class_type: updatedSchedule.class_type,
          title: `${updatedSchedule.course_code} (${updatedSchedule.class_type})`
        };
        
        this.allSchedules[index] = updatedScheduleFormatted;
      }
      
      // Also update in schedules array if it exists there
      const scheduleIndex = this.schedules.findIndex(s => s.id === updatedSchedule.id);
      if (scheduleIndex !== -1) {
        const updatedScheduleFormatted = {
          ...this.schedules[scheduleIndex],
          semester: updatedSchedule.semester_name,
          section: updatedSchedule.section,
          courseCode: updatedSchedule.course_code,
          courseName: updatedSchedule.course_name,
          day: updatedSchedule.day,
          secondDay: updatedSchedule.second_day,
          labRoom: updatedSchedule.lab_room_name,
          instructorName: updatedSchedule.instructor_name,
          startTime: updatedSchedule.start_time,
          endTime: updatedSchedule.end_time,
          types: updatedSchedule.schedule_types,
          class_type: updatedSchedule.class_type,
          title: `${updatedSchedule.course_code} (${updatedSchedule.class_type})`
        };
        
        this.schedules[scheduleIndex] = updatedScheduleFormatted;
      }
    },
    toggleScheduleType(type) {
      if (this.editSchedule.scheduleTypes.includes(type)) {
        this.editSchedule.scheduleTypes = this.editSchedule.scheduleTypes.filter(t => t !== type);
      } else {
        this.editSchedule.scheduleTypes.push(type);
      }
    },
    fetchSemesters() {
      axios.get('http://127.0.0.1:8000/api/semesters', {
        headers: {
          // Add proper headers for CORS
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        // Set withCredentials to false to avoid preflight complexity
        withCredentials: false
      })
        .then(response => {
          console.log('Fetched semesters from API:', response.data);
          
          // Store the complete semester data with IDs
          this.semestersData = response.data;
          
          // Sort the semesters first by most recent
          const sortedSemesters = this.sortSemestersByDate(response.data);
          
          // Take only the 6 most recent semesters
          const sixMostRecentSemesters = sortedSemesters.slice(0, 6);
          console.log('Six most recent semesters:', sixMostRecentSemesters.map(s => s.name));
          
          // Map to semester names for the dropdown
          this.semesters = sixMostRecentSemesters.map(semester => semester.name);
          
          // Keep selectedSemester empty to show the "Select Semester" placeholder
          // Don't auto-select a semester
          if (this.semesters.length > 0) {
            // Don't set selectedSemester here, leave it as empty string
            // No filterSchedulesBySemester() call needed since no semester is selected
          }
          
          // Now that we have semesters, fetch course offerings
          this.fetchCourseOfferings();
        })
        .catch(error => {
          console.error('Error fetching semesters:', error);
          // Fallback to hardcoded semesters in case of error - exactly 6 semesters
          this.semesters = [
            'Summer 2026',
            'Summer 2027',
            '1st Sem 2027-2028',
            '2nd Sem 2027-2028',
            'Summer 2028',
            '1st Sem 2026-2027'
          ];
          // Don't set selectedSemester here, leave it as empty string
          // No filterSchedulesBySemester() call needed since no semester is selected
          
          // Create matching semestersData for compatibility with other functions
          this.semestersData = this.semesters.map((name, index) => ({
            id: index + 1,
            name: name,
            is_active: index === 0 // Make the first one active by default
          }));
          
          // Still try to fetch course offerings even with fallback semesters
          this.fetchCourseOfferings();
        });
    },

    // Method to sort semesters by date (most recent first)
    sortSemestersByDate(semesters) {
      // Parse semesters first to extract year information
      const parsedSemesters = semesters.map(sem => {
        let type = '';
        let year = 0;
        let academicYearStart = 0;
        let academicYearEnd = 0;
        let order = 0; // For sorting: 1st Sem = 1, 2nd Sem = 2, Summer = 3
        let sortValue = 0; // Combined value for sorting
        
        if (sem.name.includes('1st Sem')) {
          type = '1st Sem';
          order = 1;
          // Extract academic year (e.g., "2025-2026" -> start year = 2025)
          const match = sem.name.match(/(\d{4})-(\d{4})/);
          if (match) {
            academicYearStart = parseInt(match[1], 10);
            academicYearEnd = parseInt(match[2], 10);
            // Use academic year and order for precise sorting
            sortValue = academicYearStart * 10 + order;
          }
        } else if (sem.name.includes('2nd Sem')) {
          type = '2nd Sem';
          order = 2;
          // Extract academic year
          const match = sem.name.match(/(\d{4})-(\d{4})/);
          if (match) {
            academicYearStart = parseInt(match[1], 10);
            academicYearEnd = parseInt(match[2], 10);
            // Use academic year and order for precise sorting
            sortValue = academicYearStart * 10 + order;
          }
        } else if (sem.name.includes('Summer')) {
          type = 'Summer';
          order = 3;
          // Extract year (e.g., "Summer 2026" -> year = 2026)
          const match = sem.name.match(/Summer (\d{4})/);
          if (match) {
            year = parseInt(match[1], 10);
            // Summer belongs to the previous academic year
            academicYearStart = year - 1;
            academicYearEnd = year;
            // Use academic year and order for precise sorting
            sortValue = academicYearStart * 10 + order;
          }
        }
        
        return {
          ...sem,
          type,
          year,
          academicYearStart,
          academicYearEnd,
          order,
          sortValue
        };
      });
      
      // Sort by sortValue (descending) to get most recent first
      return parsedSemesters.sort((a, b) => a.sortValue - b.sortValue);
    },
    fetchLabRooms() {
      axios.get('http://127.0.0.1:8000/api/lab-rooms')
        .then(response => {
          console.log('Fetched lab rooms from API:', response.data);
          
          // Store the complete lab room data with IDs
          this.labRoomsData = response.data;
          
          // Extract the lab room names from the response
          this.labs = response.data.map(room => room.name);
          
          // Set the first lab room as selected if available
          if (this.labs.length > 0) {
            this.selectedLab = this.labs[0];
          }
        })
        .catch(error => {
          console.error('Error fetching lab rooms:', error);
          // Fallback to hardcoded lab rooms in case of error
          this.labs = ['L201', 'L202', 'L203', 'L204', 'L205', 'IOT'];
          this.selectedLab = this.labs[0];
        });
    },
    fetchInstructors() {
      // First try to sync instructors from users
      axios.post('http://127.0.0.1:8000/api/sync-instructors-from-users')
        .then(response => {
          console.log('Synced instructors from users:', response.data);
          
          // Now fetch the updated instructor list
          return axios.get('http://127.0.0.1:8000/api/instructors');
        })
        .catch(error => {
          console.warn('Error syncing instructors from users:', error);
          // Continue to fetch instructors anyway
          return axios.get('http://127.0.0.1:8000/api/instructors');
        })
        .then(response => {
          console.log('Fetched instructors from API:', response.data);
          
          // Store the complete instructor data
          this.instructorsData = response.data;
          
          // Extract instructor names from the response
          this.instructors = response.data.map(instructor => instructor.full_name);
          
          // Sort alphabetically
          this.instructors.sort();
          
          console.log(`Loaded ${this.instructors.length} instructors from API`);
        })
        .catch(error => {
          console.error('Error fetching instructors:', error);
        });
    },
    fetchCourseOfferings() {
      try {
        console.log('Fetching course offerings from API...');
        const token = sessionStorage.getItem('token') || localStorage.getItem('token');
        axios.get('http://127.0.0.1:8000/api/course-offerings', {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          },
          withCredentials: false,
          params: {
            include_hidden: true
          },
          timeout: 5000
        })
        .then(response => {
          // Make sure we have semesters data available
          if (!this.semestersData || this.semestersData.length === 0) {
            console.log('Semesters data not available yet, will try to use fallback mappings');
          }
          
          console.log('Raw courses from API:', response.data);
          console.log('Total courses received:', Array.isArray(response.data.courses) ? response.data.courses.length : 'Not an array');
          
          if (Array.isArray(response.data.courses)) {
            this.courseOfferings = response.data.courses.map(course => {
              // Get the semester name from the semester_id
              let semesterName = '';
              
              // First try to find it in the semestersData if available
              if (this.semestersData && this.semestersData.length > 0) {
                const semesterObj = this.semestersData.find(s => s.id === course.semester_id);
                if (semesterObj) {
                  semesterName = semesterObj.name;
                }
              }
              
              // If not found in semestersData, use a direct mapping based on the ID
              if (!semesterName) {
                if (course.semester_id === 1) semesterName = '1st Sem 2025-2026';
                else if (course.semester_id === 2) semesterName = '2nd Sem 2025-2026';
                else if (course.semester_id === 3) semesterName = 'Summer 2026';
                else semesterName = `Semester ID: ${course.semester_id}`; // Fallback
              }
              
              return {
                code: course.code,
                name: course.name,
                section: course.year_and_section,
                semester: semesterName,
                id: course.id
              };
            });
            
            console.log('Transformed course offerings:', this.courseOfferings);
            console.log('Total courses after transform:', this.courseOfferings.length);
          } else {
            console.error('Invalid courses data format:', response.data);
            this.courseOfferings = [];
          }
        })
        .catch(error => {
          console.error('Error fetching course offerings:', error);
          console.log('Using empty course offerings array as fallback');
          this.courseOfferings = [];
          // Try fallback method with localStorage
          this.fetchCourseOfferingsFromLocalStorage();
        });
      } catch (error) {
        console.error('Error in fetchCourseOfferings:', error);
        // Try fallback method with localStorage
        this.fetchCourseOfferingsFromLocalStorage();
      }
    },
    // Fallback method to use if API call fails
    fetchCourseOfferingsFromLocalStorage() {
      try {
        console.warn('Falling back to localStorage for course offerings');
        // First try to get availableCoursesOffered which includes section and semester info
        const availableCoursesOfferedStr = localStorage.getItem('availableCoursesOffered');
        if (availableCoursesOfferedStr) {
          try {
            const availableCoursesOfferedData = JSON.parse(availableCoursesOfferedStr);
            console.log('Found availableCoursesOffered in localStorage:', availableCoursesOfferedData);
            
            if (Array.isArray(availableCoursesOfferedData)) {
              this.courseOfferings = availableCoursesOfferedData;
              console.log('Using availableCoursesOffered for dropdown:', this.courseOfferings);
              return;
            }
          } catch (error) {
            console.error('Error parsing availableCoursesOffered:', error);
          }
        }
        
        // Direct access to the courses array from the ScheduleManagement view
        const scheduleMgmtDataStr = localStorage.getItem('scheduleMgmtData');
        if (scheduleMgmtDataStr) {
          try {
            const scheduleMgmtData = JSON.parse(scheduleMgmtDataStr);
            if (scheduleMgmtData && Array.isArray(scheduleMgmtData.courses)) {
              this.courseOfferings = scheduleMgmtData.courses;
              console.log('Using scheduleMgmtData.courses for dropdown:', this.courseOfferings);
              return;
            }
          } catch (error) {
            console.error('Error parsing scheduleMgmtData:', error);
          }
        }
        
        // Fallback to other storage keys and transformation as needed
        const coursesOfferedStr = localStorage.getItem('coursesOffered');
        if (coursesOfferedStr) {
          try {
            const coursesOfferedData = JSON.parse(coursesOfferedStr);
            console.log('Found coursesOffered in localStorage:', coursesOfferedData);
            
            // If this is already in the right format with section and semester info
            if (Array.isArray(coursesOfferedData) && coursesOfferedData.length > 0 && 
                (coursesOfferedData[0].section || coursesOfferedData[0].semester)) {
              this.courseOfferings = coursesOfferedData;
              console.log('Using coursesOffered for dropdown:', this.courseOfferings);
              return;
            }
          } catch (error) {
            console.error('Error parsing coursesOffered:', error);
          }
        }
      } catch (error) {
        console.error('Error in fetchCourseOfferingsFromLocalStorage:', error);
        this.courseOfferings = [];
      }
    },
    refreshCourseDropdown() {
      // Force recomputation of filteredCourseOfferings
      console.log('Course dropdown focused, refreshing available courses');
      
      // If we have semester and section selected but no courses for this semester yet,
      // check if we need to create virtual courses
      if (this.editSchedule.semester && this.editSchedule.section) {
        const selectedSemester = this.editSchedule.semester;
        
        // Check if we have any courses for this semester
        const hasCoursesForSemester = this.courseOfferings.some(course => 
          course.semester === selectedSemester
        );
        
        if (!hasCoursesForSemester) {
          console.log('No courses found for semester:', selectedSemester, 'Creating virtual courses');
          
          // This will trigger the filteredCourseOfferings computed property
          // which will create virtual courses for this semester
        }
      }
      
      // Trigger a reactivity update
      this.$forceUpdate();
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

.dashboard-header {
  margin-bottom: 1.5rem;
}

.welcome-section h2 {
  color: #e91e63;
  font-size: 1.75rem;
  margin: 0;
  font-weight: 500;
}

.dashboard-content {
  display: flex;
  gap: 1.5rem;
}

.right-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
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

.semester-dropdown-wrapper {
  width: 200px;
}

.semester-dropdown {
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
  display: flex;
  align-items: center;
  justify-content: center;
}

.day-header:last-child {
  border-right: none;
}

.day-name {
  font-weight: 500;
  font-size: 0.9rem;
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
  color: white;
  padding: 0.5rem;
  overflow: hidden;
  z-index: 5;
}

.schedule-item.status-draft {
  background-color: #DD385A;
}

.schedule-item.status-pending {
  background-color: #FFA500;
}

.schedule-item.status-approved {
  background-color: #4CAF50;
}

.schedule-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  width: 100%;
  height: 100%;
  padding: 8px;
  box-sizing: border-box;
  cursor: pointer;
  text-align: center;
}

.schedule-title {
  font-weight: 600;
  font-size: 0.85rem;
  margin-bottom: 0.25rem;
}

.schedule-lab {
  font-weight: 600;
  font-size: 0.8rem;
  margin-bottom: 0.25rem;
  background-color: rgba(0, 0, 0, 0.15);
  padding: 2px 5px;
  border-radius: 3px;
  display: inline-block;
}

.schedule-time {
  font-size: 0.75rem;
  opacity: 0.9;
  margin-bottom: 0.25rem;
  font-weight: 500;
}

.schedule-details {
  font-size: 0.75rem;
  opacity: 0.9;
  white-space: pre-line;
  line-height: 1.4;
}

.table-body::-webkit-scrollbar {
  width: 8px;
}

.table-body::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.table-body::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 4px;
}

.table-body::-webkit-scrollbar-thumb:hover {
  background: #999;
}

.schedule-popup {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.popup-content {
  background-color: white;
  border-radius: 8px;
  width: 420px;
  max-width: 90%;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
  overflow: hidden;
}

.popup-header {
  background-color: #e91e63;
  color: white;
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.popup-header h3 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 500;
}

.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  line-height: 1;
}

.popup-body {
  padding: 1.5rem;
}

.detail-row {
  margin-bottom: 0.75rem;
  display: flex;
}

.detail-label {
  font-weight: 500;
  width: 100px;
  color: #666;
}

.detail-value {
  flex: 1;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.action-buttons {
  display: flex;
  gap: 1rem;
}

.approve-btn, .reject-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.approve-btn {
  background-color: #4CAF50;
  color: white;
}

.approve-btn:hover {
  background-color: #45a049;
}

.reject-btn {
  background-color: #f44336;
  color: white;
}

.reject-btn:hover {
  background-color: #da190b;
}

.approve-btn svg, .reject-btn svg {
  margin-right: 4px;
}

.clear-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  background-color: #ff9800;
  color: white;
}

.clear-btn:hover {
  background-color: #f57c00;
}

.clear-btn svg {
  margin-right: 4px;
}

/* Add styles for the edit modal */
.modal {
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

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.modal-header {
  padding: 1rem 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #e91e63;
  color: white;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.25rem;
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

.modal-body {
  padding: 1.5rem;
}

.modal-footer {
  padding: 1rem 1.5rem;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  border-top: 1px solid #eee;
}

.schedule-type-selector {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.type-btn {
  padding: 0.5rem 1.5rem;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.type-btn.active {
  background-color: #DD385A;
  border-color: #DD385A;
  color: white;
}

.type-btn.active:disabled {
  opacity: 0.8;
}

.edit-form-layout {
  display: flex;
  gap: 2rem;
}

.left-column, .right-column {
  flex: 1;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
  color: #333;
}

.form-select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
}

.time-picker {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.time-select {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
}

.period-select {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
}

.cancel-btn {
  padding: 0.5rem 1.5rem;
  background: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
}

.update-btn {
  padding: 0.5rem 1.5rem;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
}

.update-btn:disabled {
  background: #cccccc;
  cursor: not-allowed;
}

.optional-text {
  font-size: 0.8rem;
  color: #666;
  font-weight: normal;
}

/* Add styles for schedule status */
.pending-schedule {
  background-color: #FFC107; /* Yellow for pending */
}

.approved-schedule {
  background-color: #4CAF50; /* Green for approved */
}

.status-warning {
  background-color: #fff3cd;
  color: #856404;
  border: 1px solid #ffeeba;
  border-radius: 4px;
  padding: 10px;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  font-size: 0.9rem;
}

.status-warning i {
  margin-right: 8px;
  color: #e0a800;
  font-size: 1.1rem;
}
</style>
