<template>
  <div class="dashboard-layout">
    <DashBoardSideBarDean />
    <div class="main-content">
      <DashBoardTopbar />
      <div class="schedule-content">
        <div class="header">
          <div class="user-info">
            <div class="user-info-flex">
              <div class="info-row">
                <span class="label">ID Number:</span>
                <span class="value">{{ user.idNumber }}</span>
              </div>
              <div class="info-row">
                <span class="label">Name:</span>
                <span class="value">{{ user.name }}</span>
              </div>
              <div class="info-row">
                <span class="label">Classification:</span>
                <span class="value">{{ user.classification }}</span>
              </div>
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
            <h2>My Personalized Schedule</h2>
            <div class="lab-navigation">
              <select class="lab-dropdown" v-model="selectedLab">
                <option v-for="lab in laboratories" :key="lab" :value="lab">
                  {{ lab }}
                </option>
              </select>
            </div>
            </div>
            
            <div class="schedule-table">
              <div v-if="schedules.length === 0" class="no-schedules-message">
                <p>No approved personalized schedules found for you in this lab room.</p>
              </div>
              <table v-else>
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
import DashBoardSideBarDean from '../../components/DashBoardSideBarDean.vue'
import DashBoardTopbar from '../../components/DashBoardTopbar.vue'
import { userAPI, labRoomAPI, systemSettingsAPI } from '../../services/api.js'
import axios from 'axios'
import jsPDF from 'jspdf'
import html2canvas from 'html2canvas'

export default {
  name: 'ScheduleDean',
  components: {
    DashBoardSideBarDean,
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
    schedules: [],
    labRoomData: [],
    currentSemesterId: null,
    currentSemesterName: '',
    pollInterval: null
  }
},
created() {
  this.fetchLabRooms();
  this.getUserInfo().then(() => {
    this.loadSchedules();
  });
},
mounted() {
  // Start polling for updates
  this.startPolling();
},
beforeUnmount() {
  // Clear the interval when component is destroyed
  this.stopPolling();
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
  },
  'user.name': {
    handler() {
      if (this.user.name) {
        this.loadSchedules();
      }
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
        oldSchedule.start_time !== newSchedule.start_time ||
        oldSchedule.end_time !== newSchedule.end_time ||
        oldSchedule.instructor_name !== newSchedule.instructor_name ||
        oldSchedule.lab_room_name !== newSchedule.lab_room_name
      ) {
        return true;
      }
    }
    
    // No changes detected
    return false;
  },
  
  async loadSchedulesWithoutFlicker() {
    try {
      // Get token from session storage or local storage
      const token = sessionStorage.getItem('token') || localStorage.getItem('token');
      if (!token) {
        console.error('No token found');
        return;
      }
      
      // Get the current display semester from system settings if needed
      if (!this.currentSemesterId) {
        try {
          const semesterResponse = await systemSettingsAPI.getCurrentDisplaySemester();
          this.currentSemesterId = semesterResponse.data.semester_id;
          this.currentSemesterName = semesterResponse.data.semester_name;
          console.log(`Loaded current display semester: ${this.currentSemesterName} (ID: ${this.currentSemesterId})`);
        } catch (semesterError) {
          console.error('Error fetching current display semester:', semesterError);
          // Continue without semester filter if we can't get the current semester
        }
      }
      
      // Prepare the params for the API request
      const params = {
          lab_room: this.selectedLab
      };
      
      // Add semester filter if we have a current semester ID
      if (this.currentSemesterId) {
        params.semester_id = this.currentSemesterId;
      }
      
      // Fetch schedules via API with the proper endpoint and parameters
      const response = await axios.get(`http://localhost:8000/api/schedules`, {
        params: params,
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.data && Array.isArray(response.data)) {
        // Filter schedules to only show approved ones with instructor name matching the current user
        const newSchedules = response.data.filter(schedule => {
          // Only include approved schedules
          const isApproved = schedule.status === 'approved';
          
          // Only include schedules where the instructor name matches the current user's name
          const isCurrentUserSchedule = schedule.instructor_name === this.user.name;
          
          return isApproved && isCurrentUserSchedule;
        });
        
        // Sanitize schedule objects to ensure all needed properties exist
        const processedSchedules = this.sanitizeSchedules(newSchedules);
        
        // Only update if something has actually changed to prevent flickering
        if (this.hasSchedulesChanged(this.schedules, processedSchedules)) {
          this.schedules = processedSchedules;
          console.log(`Updated ${this.schedules.length} personalized schedules for lab ${this.selectedLab}`);
        }
      }
    } catch (error) {
      console.error('Error fetching schedules during polling:', error);
    }
  },
  
  async fetchLabRooms() {
    try {
      // Fetch lab rooms from API
      const response = await labRoomAPI.getAll();
      console.log('Lab rooms API response:', response.data);
      
      if (response.data && Array.isArray(response.data)) {
        // Store the full lab room data for mapping between id and name
        this.labRoomData = response.data;
        
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
    this.loadSchedulesWithoutFlicker();
  },
  
  async getUserInfo() {
    try {
      // Fetch user data from API
      const token = sessionStorage.getItem('token') || localStorage.getItem('token');
      const userStr = sessionStorage.getItem('user') || localStorage.getItem('user');
      
      if (!token || !userStr) {
        console.error('No authentication found');
        this.resetUserInfo();
        return;
      }
      
      try {
        const userData = JSON.parse(userStr);
        const response = await userAPI.getProfile(userData.id);
        console.log('User API response:', response.data);
        
        if (response.data) {
          this.user.name = response.data.full_name || '';
          this.user.idNumber = response.data.id || '';
          this.user.classification = response.data.role || '';
          console.log('User info loaded from API:', this.user);
          return true; // Indicate successful load
        } else {
          console.error('Invalid user data format:', response.data);
          this.resetUserInfo();
          return false;
        }
      } catch (parseError) {
        console.error('Error parsing user data:', parseError);
        this.resetUserInfo();
        return false;
      }
    } catch (error) {
      console.error('Error fetching user info from API:', error);
      this.resetUserInfo();
      return false;
    }
  },
  
  resetUserInfo() {
    this.user = {
      name: '',
      idNumber: '',
      classification: ''
    };
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
    
    // Check if any schedule matches the criteria
    const result = this.schedules.some(schedule => {
      // Check if the schedule is for the current lab and day (including Saturday)
      if (schedule.lab_room_name !== this.selectedLab || schedule.day !== dayName) {
        return false;
      }
      
      const startMinutes = this.convertTimeToMinutes(schedule.start_time);
      const endMinutes = this.convertTimeToMinutes(schedule.end_time);
      
      // Check if the time slot is within the schedule's time range
      // Important: Include the end time slot itself by adding 30 minutes to endMinutes
      // This ensures the colored block extends fully to the end time
      const isWithin = timeSlotMinutes >= startMinutes && timeSlotMinutes < (endMinutes + 30);
      
      // Debug: Log a successful match
      if (isWithin) {
        console.log(`Found schedule match for ${dayName} at ${timeSlot}:`, 
          schedule.course_code, 
          schedule.start_time, 
          schedule.end_time
        );
      }
      
      return isWithin;
    });
    
    return result;
  },
  
  isScheduleStart(dayName, timeSlot) {
    if (!this.schedules || this.schedules.length === 0) {
      return false;
    }
    
    const timeSlotMinutes = this.convertTimeToMinutes(timeSlot);
    
    return this.schedules.some(schedule => {
      // Check if the schedule is for the current lab and day (including Saturday)
      if (schedule.lab_room_name !== this.selectedLab || schedule.day !== dayName) {
        return false;
      }
      
      const startMinutes = this.convertTimeToMinutes(schedule.start_time);
      return timeSlotMinutes === startMinutes;
    });
  },
  
  getScheduleStyle(dayName, timeSlot) {
    const schedule = this.schedules.find(s => {
      if (s.lab_room_name !== this.selectedLab || s.day !== dayName) {
        return false;
      }
      
      const slotMinutes = this.convertTimeToMinutes(timeSlot);
      const startMinutes = this.convertTimeToMinutes(s.start_time);
      const endMinutes = this.convertTimeToMinutes(s.end_time);
      
      // Apply the same logic as in isTimeSlotWithinSchedule
      return slotMinutes >= startMinutes && slotMinutes < (endMinutes + 30);
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
      if (s.lab_room_name !== this.selectedLab || s.day !== dayName) {
        return false;
      }
      
      const slotMinutes = this.convertTimeToMinutes(timeSlot);
      const startMinutes = this.convertTimeToMinutes(s.start_time);
      
      return slotMinutes === startMinutes;
    });
    
    if (!schedule) return '';
    return schedule.course_code || '';
  },
  
  getScheduleTime(dayName, timeSlot) {
    const schedule = this.schedules.find(s => {
      if (s.lab_room_name !== this.selectedLab || s.day !== dayName) {
        return false;
      }
      
      const slotMinutes = this.convertTimeToMinutes(timeSlot);
      const startMinutes = this.convertTimeToMinutes(s.start_time);
      
      return slotMinutes === startMinutes;
    });
    
    if (!schedule) return '';
    return `${schedule.start_time} - ${schedule.end_time}`;
  },
  
  getScheduleDetails(dayName, timeSlot) {
    const schedule = this.schedules.find(s => {
      if (s.lab_room_name !== this.selectedLab || s.day !== dayName) {
        return false;
      }
      
      const slotMinutes = this.convertTimeToMinutes(timeSlot);
      const startMinutes = this.convertTimeToMinutes(s.start_time);
      
      return slotMinutes === startMinutes;
    });
    
    if (!schedule) return '';
    return `${schedule.course_code}\n${schedule.section}\n${schedule.instructor_name}`;
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
  
  async downloadSchedule() {
    console.log('Generating PDF schedule...');
    
    // Create a new jsPDF instance with portrait orientation
    const pdf = new jsPDF('portrait', 'mm', 'a4');
    
    // Get page dimensions
    const pageWidth = pdf.internal.pageSize.getWidth();
    const pageHeight = pdf.internal.pageSize.getHeight();
    const margin = 15;
    const contentWidth = pageWidth - (margin * 2);
    
    // Add header information
    pdf.setFontSize(14);
    pdf.setFont(undefined, 'bold');
    pdf.text('UNIVERSITY OF THE IMMACULATE CONCEPTION', pageWidth / 2, margin + 5, { align: 'center' });
    pdf.setFontSize(11);
    pdf.text('COLLEGE DEPARTMENT', pageWidth / 2, margin + 12, { align: 'center' });
    pdf.setFontSize(9);
    pdf.text('Fr. Selga St., Bankerohan / Bonifacio St., Davao City 8000', pageWidth / 2, margin + 18, { align: 'center' });
    
    // Add schedule title
    pdf.setFontSize(12);
    pdf.text(`${this.user.name.toUpperCase()} CLASS SCHEDULE`, pageWidth / 2, margin + 26, { align: 'center' });
    pdf.setFontSize(10);
    pdf.text(`${this.currentSemesterName || '(Current Semester)'}`, pageWidth / 2, margin + 32, { align: 'center' });
    
    // Add date information
    const currentDate = new Date();
    pdf.setFont(undefined, 'normal');
    pdf.text(`As of ${currentDate.toLocaleDateString()}`, margin, margin + 40);
    
    // Draw a horizontal line
    pdf.setDrawColor(0, 0, 0);
    pdf.line(margin, margin + 42, pageWidth - margin, margin + 42);
    
    // Add user information
    pdf.setFont(undefined, 'bold');
    pdf.text('ID Number', margin, margin + 48);
    pdf.text(':', margin + 30, margin + 48);
    pdf.setFont(undefined, 'normal');
    pdf.text(this.user.idNumber, margin + 35, margin + 48);
    
    pdf.setFont(undefined, 'bold');
    pdf.text('Name', margin, margin + 54);
    pdf.text(':', margin + 30, margin + 54);
    pdf.setFont(undefined, 'normal');
    pdf.text(this.user.name, margin + 35, margin + 54);
    
    pdf.setFont(undefined, 'bold');
    pdf.text('Classification', margin, margin + 60);
    pdf.text(':', margin + 30, margin + 60);
    pdf.setFont(undefined, 'normal');
    pdf.text(this.user.classification, margin + 35, margin + 60);
    
    // Draw another horizontal line
    pdf.line(margin, margin + 62, pageWidth - margin, margin + 62);
    
    // Create table for class schedule
    // Column headers
    const tableTop = margin + 68;
    const tableLeft = margin;
    const tableWidth = contentWidth;
    
    // Calculate column widths as percentages of the content width
    // Course Code, Description, Lec/Lab, Schedule, Room, Section (%)
    const colWidthPercentages = [15, 35, 10, 20, 10, 10]; 
    const colWidths = colWidthPercentages.map(pct => (contentWidth * pct) / 100);
    
    // Calculate positions for columns
    const colPositions = [];
    let currentPos = tableLeft;
    
    for (const width of colWidths) {
      colPositions.push(currentPos);
      currentPos += width;
    }
    
    // Draw table headers
    pdf.setFillColor(240, 240, 240);
    pdf.rect(tableLeft, tableTop, tableWidth, 7, 'F');
    
    pdf.setFont(undefined, 'bold');
    pdf.setFontSize(9);
    
    const headers = ['Course Code', 'Description', 'Lec/Lab', 'Schedule', 'Room', 'Section'];
    
    headers.forEach((header, index) => {
      // Center text in each column
      const textWidth = pdf.getStringUnitWidth(header) * pdf.getFontSize() / pdf.internal.scaleFactor;
      const colCenter = colPositions[index] + (colWidths[index] / 2);
      pdf.text(header, colCenter, tableTop + 5, { align: 'center' });
    });
    
    // Draw horizontal line after headers
    pdf.line(tableLeft, tableTop + 7, tableLeft + tableWidth, tableTop + 7);
    
    // Process schedules to remove duplicates but keep different schedules for same course
    const rows = [];
    
    // Group schedules by course_code, section, day, and time to identify unique schedules
    const uniqueSchedules = {};
    
    this.schedules.forEach(schedule => {
      // Create a unique key for each schedule based on course code, section, start and end time
      // This ensures different schedules for the same course are preserved
      const scheduleKey = `${schedule.course_code}_${schedule.section}_${schedule.start_time}_${schedule.end_time}`;
      
      // If we already have this schedule and it's a second day instance, we merge the days
      if (uniqueSchedules[scheduleKey]) {
        // If this is a second_day entry, add the day to the existing schedule's second_day field
        if (schedule.isSecondDayInstance) {
          uniqueSchedules[scheduleKey].second_day = schedule.day;
        }
      } else {
        // This is a new unique schedule, add it to our collection
        uniqueSchedules[scheduleKey] = { ...schedule };
      }
    });
    
    // Convert the unique schedules back to an array
    const processedSchedules = Object.values(uniqueSchedules);
    
    // Process each unique schedule as its own row
    processedSchedules.forEach(schedule => {
      // Determine if it's a Lec or Lab based on class_type
      let type = '';
      if (schedule.class_type === 'lec') {
        type = 'Lec';
      } else if (schedule.class_type === 'lab') {
        type = 'Lab';
      } else if (schedule.class_type === 'lab/lec') {
        type = 'Lab/Lec';
      } else {
        type = schedule.class_type || 'Lec'; // Default to Lec if not specified
      }
      
      // Create a row for this schedule
      rows.push({
        courseCode: schedule.course_code,
        description: schedule.course_name,
        type: type,
        schedule: this.formatScheduleForPDF([schedule]),
        room: schedule.lab_room_name || '',
        section: schedule.section || ''
      });
    });
    
    // Sort rows by course code
    rows.sort((a, b) => {
      if (a.courseCode < b.courseCode) return -1;
      if (a.courseCode > b.courseCode) return 1;
      // If course codes are the same, sort by Lec/Lab (Lec first)
      if (a.type === 'Lec' && b.type === 'Lab') return -1;
      if (a.type === 'Lab' && b.type === 'Lec') return 1;
      return 0;
    });
    
    // Draw the table rows with fixed height
    let currentY = tableTop + 7;
    const rowHeight = 10; // Increased row height to ensure text doesn't overlap
    
    pdf.setFont(undefined, 'normal');
    pdf.setFontSize(8); // Smaller font for content to fit better
    
    rows.forEach((row, rowIndex) => {
      // Check if we need to add a new page
      if (currentY + rowHeight > pageHeight - margin) {
        pdf.addPage();
        currentY = margin;
        
        // Add column headers on new page
        pdf.setFillColor(240, 240, 240);
        pdf.rect(tableLeft, currentY, tableWidth, 7, 'F');
        pdf.setFont(undefined, 'bold');
        pdf.setFontSize(9);
        headers.forEach((header, index) => {
          const textWidth = pdf.getStringUnitWidth(header) * pdf.getFontSize() / pdf.internal.scaleFactor;
          const colCenter = colPositions[index] + (colWidths[index] / 2);
          pdf.text(header, colCenter, currentY + 5, { align: 'center' });
        });
        pdf.line(tableLeft, currentY + 7, tableLeft + tableWidth, currentY + 7);
        currentY += 7;
        pdf.setFont(undefined, 'normal');
        pdf.setFontSize(8);
      }
      
      // Draw row background (alternating colors)
      if (rowIndex % 2 === 1) {
        pdf.setFillColor(248, 248, 248);
        pdf.rect(tableLeft, currentY, tableWidth, rowHeight, 'F');
      }
      
      // Draw row content with text trimming to fit in columns
      const maxCharsByCol = [15, 100, 10, 30, 6, 50]; // Max chars per column
      
      // Helper function to trim text to fit in column
      const trimText = (text, maxChars) => {
        if (!text) return '';
        return text.length > maxChars ? text.substring(0, maxChars - 1) + '…' : text;
      };
      
      // Cell padding
      const padding = 2;
      
      // Position text within cells
      pdf.text(trimText(row.courseCode, maxCharsByCol[0]), colPositions[0] + padding, currentY + 5);
      pdf.text(trimText(row.description, maxCharsByCol[1]), colPositions[1] + padding, currentY + 5);
      
      // Center the Lec/Lab text
      const typeText = trimText(row.type, maxCharsByCol[2]);
      const typeWidth = pdf.getStringUnitWidth(typeText) * pdf.getFontSize() / pdf.internal.scaleFactor;
      const typeColCenter = colPositions[2] + (colWidths[2] / 2);
      pdf.text(typeText, typeColCenter, currentY + 5, { align: 'center' });
      
      // Format the schedule text
      const scheduleLines = row.schedule.split('\n');
      if (scheduleLines.length > 0) {
        // If multiple schedule lines, position them properly
        scheduleLines.forEach((line, i) => {
          if (i < 2) { // Limit to 2 lines to prevent overflow
            const trimmedLine = trimText(line, maxCharsByCol[3]);
            pdf.text(trimmedLine, colPositions[3] + padding, currentY + 3 + (i * 4));
          }
        });
      } else {
        pdf.text(trimText(row.schedule, maxCharsByCol[3]), colPositions[3] + padding, currentY + 5);
      }
      
      // Center the Room text
      const roomText = trimText(row.room, maxCharsByCol[4]);
      const roomWidth = pdf.getStringUnitWidth(roomText) * pdf.getFontSize() / pdf.internal.scaleFactor;
      const roomColCenter = colPositions[4] + (colWidths[4] / 2);
      pdf.text(roomText, roomColCenter, currentY + 5, { align: 'center' });
      
      // Center the Section text
      const sectionText = trimText(row.section, maxCharsByCol[5]);
      const sectionWidth = pdf.getStringUnitWidth(sectionText) * pdf.getFontSize() / pdf.internal.scaleFactor;
      const sectionColCenter = colPositions[5] + (colWidths[5] / 2);
      pdf.text(sectionText, sectionColCenter, currentY + 5, { align: 'center' });
      
      // Advance to next row
      currentY += rowHeight;
    });
    
    // Draw vertical lines for columns
    colPositions.forEach(xPos => {
      pdf.line(xPos, tableTop, xPos, currentY);
    });
    
    // Draw right border of the table
    pdf.line(tableLeft + tableWidth, tableTop, tableLeft + tableWidth, currentY);
    
    // Add PDF filename with date
    const fileName = `schedule_${this.user.name.replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.pdf`;
    
    // Save the PDF
    pdf.save(fileName);
    console.log('PDF generated successfully:', fileName);
  },
  
  // Helper to format schedule for PDF
  formatScheduleForPDF(schedules) {
    const dayMap = {
      'Monday': 'M',
      'Tuesday': 'T',
      'Wednesday': 'W',
      'Thursday': 'Th',
      'Friday': 'F',
      'Saturday': 'S',
      'Sunday': 'Su',
      'Mon': 'M',
      'Tue': 'T',
      'Wed': 'W',
      'Thu': 'Th',
      'Fri': 'F',
      'Sat': 'S',
      'Sun': 'Su'
    };
    
    // Group by time (in case there are multiple days with same time)
    const timeGroups = {};
    
    schedules.forEach(schedule => {
      const timeKey = `(${schedule.start_time}-${schedule.end_time})`;
      if (!timeGroups[timeKey]) {
        timeGroups[timeKey] = {
          time: timeKey,
          days: []
        };
      }
      
      // Add the day abbreviation for the primary day
      const dayAbbr = dayMap[schedule.day] || schedule.day.substring(0,1);
      if (!timeGroups[timeKey].days.includes(dayAbbr)) {
        timeGroups[timeKey].days.push(dayAbbr);
      }
      
      // Add the second day if it exists
      if (schedule.second_day) {
        const secondDayAbbr = dayMap[schedule.second_day] || schedule.second_day.substring(0,1);
        if (!timeGroups[timeKey].days.includes(secondDayAbbr)) {
          timeGroups[timeKey].days.push(secondDayAbbr);
        }
      }
    });
    
    // Format each time group with day codes clearly visible
    const formattedSchedules = Object.values(timeGroups).map(group => {
      // Sort days in correct order: M, T, W, Th, F, S, Su
      const dayOrder = { 'M': 0, 'T': 1, 'W': 2, 'Th': 3, 'F': 4, 'S': 5, 'Su': 6 };
      group.days.sort((a, b) => {
        return (dayOrder[a] || 999) - (dayOrder[b] || 999);
      });
      
      const dayStr = group.days.join('');
      // Ensure the time and day codes are both clearly visible
      return `${group.time} [${dayStr}]`;
    });
    
    return formattedSchedules.join('\n');
  },
  
  // Helper to get unique rooms from schedules
  getUniqueRooms(schedules) {
    const rooms = new Set();
    schedules.forEach(schedule => {
      if (schedule.lab_room_name) {
        rooms.add(schedule.lab_room_name);
      }
    });
    return Array.from(rooms).join(', ');
  },
  
  // Ensure schedule objects have all necessary properties
  sanitizeSchedules(schedules) {
    let processedSchedules = [];
    
    schedules.forEach(schedule => {
      // Log raw schedule object for debugging
      console.log('Raw schedule from API:', schedule);
      
      // Create a consistent schedule object with all required properties
      const sanitizedSchedule = {
        ...schedule,
        // Ensure lab_room_name is set (might be lab_room in some API responses)
        lab_room_name: schedule.lab_room_name || schedule.lab_room || this.selectedLab,
        // Ensure day field is capitalized consistently
        day: schedule.day ? schedule.day.charAt(0).toUpperCase() + schedule.day.slice(1) : '',
        // Ensure time fields are in correct format
        start_time: schedule.start_time || '8:00 AM',
        end_time: schedule.end_time || '9:00 AM',
        // Ensure other required fields exist
        course_code: schedule.course_code || schedule.title || 'Unknown Course',
        course_name: schedule.course_name || schedule.description || '',
        instructor_name: schedule.instructor_name || this.user.name || '',
        section: schedule.section || ''
      };
      
      // Add the primary day schedule
      processedSchedules.push(sanitizedSchedule);
      
      // If this schedule has a second_day, create a duplicate entry with day = second_day
      if (schedule.second_day) {
        const secondDaySchedule = {
          ...sanitizedSchedule,
          day: schedule.second_day.charAt(0).toUpperCase() + schedule.second_day.slice(1),
          // Add a flag to indicate this is the second day instance
          isSecondDayInstance: true
        };
        processedSchedules.push(secondDaySchedule);
        console.log('Created second day schedule entry for:', schedule.course_code, 'on', secondDaySchedule.day);
      }
    });
    
    return processedSchedules;
  }
}}
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
  border-radius: 12px;
  padding: 1.25rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(221, 56, 90, 0.1);
}

.user-info-flex {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  margin-bottom: 1rem;
  align-items: center;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid rgba(221, 56, 90, 0.15);
}

.info-row {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0;
  align-items: center;
  background-color: rgba(221, 56, 90, 0.03);
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.info-row:hover {
  background-color: rgba(221, 56, 90, 0.08);
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.info-row:last-of-type {
  margin-bottom: 0;
}

.label {
  color: #777;
  font-size: 0.85rem;
  white-space: nowrap;
  font-weight: 500;
}

.value {
  color: #333;
  font-weight: 600;
  font-size: 0.95rem;
}

.current-date {
  color: #DD385A;
  font-size: 0.95rem;
  margin: 0;
  font-weight: 500;
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
  table-layout: fixed;
}

th, td {
  border: 0.5px solid #ddd;
  padding: 0;
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
  padding: 0.75rem;
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
  padding: 0.75rem;
}

.schedule-slot {
  background-color: white;
  transition: background-color 0.2s ease;
  position: relative;
  padding: 0;
}

.schedule-slot:hover {
  background-color: rgba(221, 56, 90, 0.05);
}

.schedule-item {
background-color: #DD385A;
color: white;
position: absolute;
left: 0;
right: 0;
top: 0;
bottom: 0;
z-index: 1;
overflow: hidden;
display: flex;
flex-direction: column;
cursor: pointer;
transition: all 0.2s ease;
}

.schedule-item:hover {
filter: brightness(1.05);
}

.schedule-item-content {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  justify-content: center;
  align-items: center;
  padding: 8px;
  box-sizing: border-box;
}

.schedule-title {
  font-weight: 600;
  font-size: 1rem;
  margin-bottom: 4px;
  text-shadow: 0 1px 1px rgba(0, 0, 0, 0.1);
}

.schedule-time {
  font-size: 0.8rem;
  opacity: 0.95;
  margin-bottom: 4px;
  font-weight: 500;
}

.schedule-details {
  font-size: 0.8rem;
  opacity: 0.95;
  white-space: pre-line;
  text-align: center;
  line-height: 1.4;
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

.no-schedules-message {
  text-align: center;
  padding: 2rem;
  color: #666;
  font-size: 1rem;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 1rem;
}

.no-schedules-message p {
  margin: 0;
  max-width: 80%;
}

.no-schedules-message p:first-child {
  font-weight: 500;
  color: #DD385A;
  font-size: 1.1rem;
}
</style>