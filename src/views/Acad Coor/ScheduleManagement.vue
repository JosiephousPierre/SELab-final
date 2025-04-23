<template>
  <div class="dashboard-layout" ref="scheduleComponent">
    <DashBoardSidebar />
    <div class="main-content">
      <DashBoardTopbar />
      <div class="content-wrapper">
        <div class="header">
          <h1>Scheduling Management</h1>
          <div class="header-actions">
            <button class="import-excel-btn" @click="showImportCoursesModal">
              <span class="fa-icon">&#xf56f;</span> Import Course Offerings
            </button>
            <button class="import-excel-btn" style="background-color: #f44336;" @click="clearCourseOfferings">
              <span class="fa-icon">&#xf2ed;</span> Clear Course Offerings
            </button>
            <button class="create-schedule-btn" @click="openCreateSchedule">
              <span class="fa-icon">&#xf067;</span> Create Schedule
            </button>
          </div>
        </div>

        <div class="schedule-container">
          <div class="lab-navigation">
            <div class="select-semester">
              <label>Select Semester:</label>
              <div class="select-wrapper">
                <select class="form-select" v-model="selectedSemester" @change="filterSchedulesBySemester">
                  <option value="" disabled selected>Select Semester</option>
                  <option v-for="sem in semesterOptions" :key="sem" :value="sem">
                    {{ sem }}
                  </option>
                </select>
              </div>
            </div>
            <div class="center-navigation">
              <div class="select-lab-room">
                <label>Select Lab Room:</label>
                <div class="select-wrapper">
                  <select class="form-select" v-model="selectedLab">
                    <option value="" disabled>Select Lab Room</option>
                    <option v-for="lab in labRooms" :key="lab" :value="lab">
                      {{ lab }}
                    </option>
                  </select>
              </div>
              </div>
            </div>
            <div class="navigation-spacer"></div>
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
                      :class="['schedule-item', getScheduleStatusClass(day.name, time)]" 
                      @click="openEditDeleteModal(day.name, time)"
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
        <div class="schedule-actions-footer">
          <button class="send-all-approval-btn" @click="sendAllForApproval">
            <span class="fa-icon">&#xf1d8;</span>
            Send All Schedules for Approval
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- New Semester Modal -->
  <div class="modal" v-if="showNewSemesterModal">
    <div class="modal-content">
      <div class="modal-header">
        <h2>New Semester</h2>
        <button class="close-btn" @click="showNewSemesterModal = false">×</button>
      </div>
      <div class="modal-body">
        <div class="form-group">
          <label>Select Semester</label>
          <div class="select-wrapper">
            <select v-model="newSemester.semester" class="modal-dropdown">
              <option value="" disabled selected>Select Semester</option>
              <option value="1st">1st Semester</option>
              <option value="2nd">2nd Semester</option>
              <option value="summer">Summer</option>
            </select>
          </div>
        </div>
        <div class="form-group">
          <label>School Year</label>
          <div class="select-wrapper">
            <select v-model="newSemester.schoolYear" class="modal-dropdown">
              <option value="" disabled selected>Select School Year</option>
              <option value="2025">2025</option>
              <option value="2025-2026">2025-2026</option>
              <option value="2026-2027">2026-2027</option>
              <option value="2027">2027</option>
            </select>
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button class="cancel-btn" @click="showNewSemesterModal = false">Cancel</button>
        <button class="create-btn" @click="createNewSemester" :disabled="!isFormValid">Create</button>
      </div>
    </div>
  </div>

  <!-- Create Schedule Modal -->
  <div class="modal" v-if="showCreateScheduleModal">
    <div class="modal-content">
      <div class="modal-header">
        <h2>Create Schedule</h2>
        <button class="close-btn" @click="showCreateScheduleModal = false">×</button>
      </div>
      <div class="modal-body">
        <div class="schedule-type-selector">
          <button 
            :class="['type-btn', { active: scheduleTypes.includes('Lab') }]" 
            @click="toggleScheduleType('Lab')"
          >Lab</button>
          <button 
            :class="['type-btn', { active: scheduleTypes.includes('Lec') }]" 
            @click="toggleScheduleType('Lec')"
          >Lec</button>
        </div>

        <div class="left-column">
          <div class="form-group">
            <label>Select Semester</label>
            <div class="select-wrapper">
              <select v-model="newSchedule.semester" class="form-select" @change="refreshCourseDropdown">
                <option value="" disabled selected>Select Semester</option>
                <option v-for="sem in semesterOptions" :key="sem" :value="sem">
                  {{ sem }}
                </option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>Select Degree Program | Year & Section</label>
            <div class="select-wrapper">
              <select v-model="newSchedule.section" class="form-select" @change="refreshCourseDropdown">
                <option value="" disabled selected>Select Degree Program | Year & Section</option>
                <option v-for="section in sectionOptions" :key="section" :value="section">
                  {{ section }}
                </option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>Courses Offered</label>
            <div class="select-wrapper">
              <select 
                v-model="newSchedule.courseCode" 
                class="form-select"
                :key="`courses-${newSchedule.semester}-${newSchedule.section}`">
                <option value="" disabled selected>Select Course</option>
                <option v-for="course in availableCoursesOffered" :key="course.code" :value="course.code">
                  {{ course.code }} - {{ course.name }} {{ course.section ? `(${course.section})` : '' }} ({{ course.semester }})
                </option>
                <option v-if="availableCoursesOffered.length === 0" disabled>
                  No courses available - please add courses first
                </option>
              </select>
            </div>
          </div>
        </div>

        <div class="right-column">
          <div class="form-group">
            <label>Day</label>
            <div class="select-wrapper">
              <select v-model="newSchedule.day" class="form-select" required>
                <option value="" disabled selected>Select Day</option>
                <option v-for="day in days" :key="day" :value="day">{{ day }}</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>Second Day (Optional)</label>
            <div class="select-wrapper">
              <select v-model="newSchedule.secondDay" class="form-select">
                <option value="" selected>None</option>
                <option v-for="day in days" :key="day" :value="day">{{ day }}</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>Lab Room No.</label>
            <div class="select-wrapper">
              <select v-model="newSchedule.labRoom" class="form-select">
                <option value="" disabled selected>Select Lab Room</option>
                <option v-for="room in labRooms" :key="room" :value="room">{{ room }}</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>Start Time</label>
            <div class="time-picker">
              <select v-model="newSchedule.startHour" class="time-select">
                <option value="" disabled selected>--</option>
                <option v-for="hour in timeHours" :key="'start-'+hour" :value="hour">
                  {{ hour.toString().padStart(2, '0') }}
                </option>
              </select>
              <span>:</span>
              <select v-model="newSchedule.startMinute" class="time-select">
                <option v-for="minute in timeMinutes" :key="minute" :value="minute">{{ minute }}</option>
              </select>
              <select v-model="newSchedule.startPeriod" class="period-select"
                      @change="validateStartTime">
                <option value="AM">AM</option>
                <option value="PM">PM</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>End Time</label>
            <div class="time-picker">
              <select v-model="newSchedule.endHour" class="time-select">
                <option value="" disabled selected>--</option>
                <option v-for="hour in timeHours" :key="'end-'+hour" :value="hour">
                  {{ hour.toString().padStart(2, '0') }}
                </option>
              </select>
              <span>:</span>
              <select v-model="newSchedule.endMinute" class="time-select">
                <option v-for="minute in timeMinutes" :key="minute" :value="minute">{{ minute }}</option>
              </select>
              <select v-model="newSchedule.endPeriod" class="period-select"
                      @change="validateEndTime">
                <option value="AM">AM</option>
                <option value="PM">PM</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>Instructor Name</label>
            <div class="select-wrapper">
              <select v-model="newSchedule.instructorName" class="form-select" @change="handleInstructorSelect">
                <option value="" disabled selected>Select Instructor</option>
                <option v-for="instructor in instructors" :key="instructor" :value="instructor">
                  {{ instructor }}
                </option>
                <option value="add_new">+ Add New Instructor</option>
              </select>
            </div>
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button class="cancel-btn" @click="showCreateScheduleModal = false">Cancel</button>
        <button 
          class="create-btn" 
          @click="createSchedule" 
          :disabled="!isScheduleFormValid"
        >Create</button>
      </div>
    </div>
  </div>

  <!-- File Upload Modal -->
  <div class="modal" v-if="showFileUploadModal">
    <div class="modal-content">
      <div class="modal-header">
        <h2>Import Course Offerings</h2>
        <button class="close-btn" @click="showFileUploadModal = false">×</button>
      </div>
      <div class="modal-body">
        <p class="import-instructions">
          Upload an Excel file containing course offerings. The file should include:
        </p>
        <ul class="import-requirements">
          <li><strong>Column A:</strong> Course Code (e.g., "FW123.23")</li>
          <li><strong>Column B:</strong> Course Name (e.g., "Ignatian Spirituality & Christian Life 1")</li>
          <li><strong>Column C:</strong> Year and Section (e.g., "IT-1A")</li>
          <li><strong>Column D:</strong> Semester (e.g., "1st Sem")</li>
        </ul>
        <p class="import-note">
          The first row should contain column headers. Matches exactly the format shown in the sample template.
        </p>
        <div class="file-upload-area" 
             @drop.prevent="handleFileDrop"
             @dragover.prevent
             @click="triggerFileInput">
          <input 
            type="file" 
            ref="fileInput" 
            style="display: none" 
            @change="handleFileSelect"
            accept=".csv,.xlsx">
          <div class="upload-icon">
            <i class="fas fa-file-upload"></i>
          </div>
          <p>Click or drag file to this area to upload</p>
          <p class="file-format-text">Formats accepted are .csv and .xlsx</p>
        </div>
        <div v-if="selectedFile" class="selected-file">
          <p><strong>Selected file:</strong> {{ selectedFile.name }}</p>
        </div>
        <div v-else class="sample-template">
          <p>If you do not have a file you can use the sample below:</p>
          <button class="download-sample-btn" @click="downloadSampleTemplate">
            <i class="fas fa-download"></i>
            Download Sample Template
          </button>
        </div>
      </div>
      <div class="modal-footer">
        <button class="cancel-btn" @click="showFileUploadModal = false">Cancel</button>
        <button class="import-btn" 
                @click="uploadFile" 
                :disabled="!selectedFile">Import Courses</button>
      </div>
    </div>
  </div>

  <!-- Edit/Delete Modal -->
  <div class="modal" v-if="showEditDeleteModal">
    <div class="modal-content">
      <div class="modal-header">
        <h2>Schedule Options</h2>
        <button class="close-btn" @click="showEditDeleteModal = false">×</button>
      </div>
      <div class="modal-body">
        <div class="schedule-actions">
          <button class="edit-btn" @click="openEditSchedule">
            <i class="fas fa-edit"></i>
            Edit Schedule
          </button>
          <button class="delete-btn" @click="confirmDelete">
            <i class="fas fa-trash"></i>
            Delete Schedule
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- Edit Schedule Modal -->
  <div class="modal" v-if="showEditScheduleModal">
    <div class="modal-content">
      <div class="modal-header">
        <h2>Edit Schedule</h2>
        <button class="close-btn" @click="showEditScheduleModal = false">×</button>
      </div>
      <div class="modal-body">
        <div class="schedule-type-selector">
          <button 
            :class="['type-btn', { active: editSchedule.types.includes('Lab') }]" 
            @click="toggleEditScheduleType('Lab')"
          >Lab</button>
          <button 
            :class="['type-btn', { active: editSchedule.types.includes('Lec') }]" 
            @click="toggleEditScheduleType('Lec')"
          >Lec</button>
        </div>

        <div class="left-column">
          <div class="form-group">
            <label>Select Semester <span class="optional-text">(Optional)</span></label>
            <div class="select-wrapper">
              <select v-model="editSchedule.semester" class="form-select">
                <option value="">Keep current: {{ selectedSchedule.semester }}</option>
                <option v-for="sem in semesterOptions" :key="sem" :value="sem">
                  {{ sem }}
                </option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>Select Degree Program | Year & Section <span class="optional-text">(Optional)</span></label>
            <div class="select-wrapper">
              <select v-model="editSchedule.section" class="form-select">
                <option value="">Keep current: {{ selectedSchedule.section }}</option>
                <option v-for="section in sectionOptions" :key="section" :value="section">
                  {{ section }}
                </option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>Courses Offered <span class="optional-text">(Optional)</span></label>
            <div class="select-wrapper">
              <select v-model="editSchedule.courseCode" class="form-select" @focus="refreshEditCourseDropdown" @change="refreshEditCourseDropdown">
                <option value="">Keep current: {{ selectedSchedule.courseCode }}</option>
                <option v-for="course in availableCoursesOffered" :key="course.code" :value="course.code">
                  {{ course.code }} - {{ course.name }} ({{ course.semester }})
                </option>
                <option v-if="availableCoursesOffered.length === 0" disabled>
                  No courses available - please add courses first
                </option>
              </select>
            </div>
          </div>
        </div>

        <div class="right-column">
          <div class="form-group">
            <label>Day <span class="optional-text">(Optional)</span></label>
            <div class="select-wrapper">
              <select v-model="editSchedule.day" class="form-select">
                <option value="">Keep current: {{ selectedSchedule.day }}</option>
                <option v-for="day in days" :key="day" :value="day">{{ day }}</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>Second Day (Optional)</label>
            <div class="select-wrapper">
              <select v-model="editSchedule.secondDay" class="form-select">
                <option value="" selected>None</option>
                <option v-for="day in days" :key="day" :value="day">{{ day }}</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>Lab Room No. <span class="optional-text">(Optional)</span></label>
            <div class="select-wrapper">
              <select v-model="editSchedule.labRoom" class="form-select">
                <option value="">Keep current: {{ selectedSchedule.labRoom }}</option>
                <option v-for="room in labRooms" :key="room" :value="room">{{ room }}</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>Start Time <span class="optional-text">(Optional - must update both start and end time together)</span></label>
            <div class="time-picker">
              <select v-model="editSchedule.startHour" class="time-select">
                <option value="">Current</option>
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
            <label>End Time <span class="optional-text">(Optional - must update both start and end time together)</span></label>
            <div class="time-picker">
              <select v-model="editSchedule.endHour" class="time-select">
                <option value="">Current</option>
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
            <label>Instructor Name <span class="optional-text">(Optional)</span></label>
            <div class="select-wrapper">
              <select v-model="editSchedule.instructorName" class="form-select" @change="handleEditInstructorSelect">
                <option value="">Keep current: {{ selectedSchedule.instructorName }}</option>
                <option v-for="instructor in instructors" :key="instructor" :value="instructor">
                  {{ instructor }}
                </option>
                <option value="add_new">+ Add New Instructor</option>
              </select>
            </div>
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button class="cancel-btn" @click="showEditScheduleModal = false">Cancel</button>
        <button 
          class="update-btn" 
          @click="updateSchedule" 
          :disabled="!isEditScheduleFormValid"
        >Update</button>
      </div>
    </div>
  </div>

  <!-- Confirm Delete Modal -->
  <div class="modal" v-if="showDeleteConfirmModal">
    <div class="modal-content">
      <div class="modal-header">
        <h2>Confirm Delete</h2>
        <button class="close-btn" @click="showDeleteConfirmModal = false">×</button>
      </div>
      <div class="modal-body">
        <p>Are you sure you want to delete this schedule?</p>
        <div class="schedule-info">
          <p><strong>Course:</strong> {{ selectedSchedule?.courseCode }}</p>
          <p><strong>Section:</strong> {{ selectedSchedule?.section }}</p>
          <p><strong>Time:</strong> {{ getScheduleTime(selectedSchedule?.day, selectedSchedule?.startTime) }}</p>
        </div>
      </div>
      <div class="modal-footer">
        <button class="cancel-btn" @click="showDeleteConfirmModal = false">Cancel</button>
        <button class="delete-btn" @click="deleteSchedule">Delete</button>
      </div>
    </div>
  </div>

  <!-- Add New Instructor Modal -->
  <div class="modal" v-if="showAddInstructorModal">
    <div class="modal-content instructor-modal">
      <div class="modal-header instructor-modal-header">
        <h2>Add New Instructor</h2>
        <button class="close-btn" @click="showAddInstructorModal = false">×</button>
      </div>
      <div class="modal-body instructor-modal-body">
        <div class="form-group">
          <label>Instructor Name</label>
          <input 
            type="text" 
            v-model="newInstructorName" 
            class="form-input instructor-input"
            placeholder="Enter instructor name"
            autofocus
          >
          <div class="input-icon">
            <i class="fas fa-user-plus"></i>
          </div>
        </div>
        <div class="form-group">
          <label>Email (Optional)</label>
          <input 
            type="email" 
            v-model="newInstructorEmail" 
            class="form-input instructor-input"
            placeholder="Enter instructor email"
          >
          <div class="input-icon">
            <i class="fas fa-envelope"></i>
          </div>
        </div>
      </div>
      <div class="modal-footer instructor-modal-footer">
        <button class="cancel-btn instructor-cancel-btn" @click="showAddInstructorModal = false">Cancel</button>
        <button 
          class="add-btn instructor-add-btn" 
          @click="addNewInstructor" 
          :disabled="!newInstructorName.trim()"
        >
          <i class="fas fa-plus-circle"></i>
          Add Instructor
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import DashBoardSidebar from '../../components/DashBoardSidebarAcadCoor.vue'
import DashBoardTopbar from '../../components/DashBoardTopbar.vue'
import axios from 'axios'
import * as XLSX from 'xlsx'
import { scheduleAPI, semesterAPI, labRoomAPI, instructorAPI, courseOfferingAPI } from '../../services/api.js'

export default {
  name: 'ScheduleManagement',
  components: {
    DashBoardSidebar,
    DashBoardTopbar
  },
  data() {
    return {
      selectedLab: '',
      labs: [], // Will be populated from API
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
      selectedSemester: '', // Default empty, will be set after fetching
      selectedDay: '',
      selectedSection: '',
      showNewSemesterModal: false,
      newSemester: {
        semester: '',
        schoolYear: ''
      },
      showCreateScheduleModal: false,
      scheduleTypes: [],
      semesterOptions: [], // Will be populated from API
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
      coursesOffered: [], // Remove hardcoded courses, will be populated by imports
      days: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
      labRooms: [], // Will be populated from API
      timeHours: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], // Modified to match available hours
      timeMinutes: ['00', '30'], // Added for better time selection
      instructors: [], // Will be populated from API
      newSchedule: {
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
        secondDay: ''
      },
      showFileUploadModal: false,
      selectedFile: null,
      showEditDeleteModal: false,
      showEditScheduleModal: false,
      showDeleteConfirmModal: false,
      selectedSchedule: null,
      editSchedule: {
        id: null,
        types: [],
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
        secondDay: ''
      },
      showAddInstructorModal: false,
      newInstructorName: '',
      newInstructorEmail: '',
      semestersData: [], // Full semester objects from API
      labRoomsData: [],  // Full lab room objects from API
      instructorsData: [], // Full instructor objects from API
      usedCoursesList: [],
      currentlyEditingSchedule: null,
    }
  },
  methods: {
    fetchInstructors() {
      // First try to sync instructors from users
      axios.post('http://localhost:8000/api/sync-instructors-from-users')
        .then(response => {
          console.log('Synced instructors from users:', response.data);
          
          // Now fetch the updated instructor list
          return axios.get('http://localhost:8000/api/instructors');
        })
        .catch(error => {
          console.warn('Error syncing instructors from users:', error);
          // Continue to fetch instructors anyway
          return axios.get('http://localhost:8000/api/instructors');
        })
        .then(response => {
          console.log('Fetched instructors from API:', response.data);
          
          // Extract instructor names from the response
          this.instructors = response.data.map(instructor => instructor.full_name);
          
          // Sort alphabetically
          this.instructors.sort();
          
          console.log(`Loaded ${this.instructors.length} instructors from API`);
        })
        .catch(error => {
          console.error('Error fetching instructors:', error);
          // Use localStorage as fallback
          this.loadInstructorsFromStorage();
        });
    },
    fetchLabRooms() {
      axios.get('http://localhost:8000/api/lab-rooms')
        .then(response => {
          console.log('Fetched lab rooms from API:', response.data);
          
          // Store the complete lab room data with IDs
          this.labRoomsData = response.data;
          
          // Extract the lab room names from the response
          this.labRooms = response.data.map(room => room.name);
          
          // Also update the labs array for consistency
          this.labs = [...this.labRooms];
          
          // Set the first lab room as selected if available
          if (this.labRooms.length > 0) {
            this.selectedLab = this.labRooms[0];
          }
        })
        .catch(error => {
          console.error('Error fetching lab rooms:', error);
          // Fallback to hardcoded lab rooms in case of error
          this.labRooms = ['L201', 'L202', 'L203', 'L204', 'L205', 'IOT'];
          this.labs = [...this.labRooms];
          this.selectedLab = this.labRooms[0];
        });
    },
    fetchSemesters() {
      console.log('Fetching semesters from API...');
      
      // Using 127.0.0.1 instead of localhost to avoid potential CORS issues
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
          
          // Sort the semesters first
          const sortedSemesters = this.sortSemestersByDate(response.data);
          
          // Take only the 6 most recent semesters
          const sixMostRecentSemesters = sortedSemesters.slice(0, 6);
          console.log('Six most recent semesters:', sixMostRecentSemesters.map(s => s.name));
          
          // Map to semester names for the dropdown
          this.semesterOptions = sixMostRecentSemesters.map(semester => semester.name);
          
          // Keep selectedSemester empty to show the "Select Semester" placeholder
          // Don't auto-select a semester
          if (this.semesterOptions.length > 0) {
            // Don't set selectedSemester, leave it as empty string
            // Remove call to filterSchedulesBySemester()
          }
        })
        .catch(error => {
          console.error('Error fetching semesters:', error);
          console.log('Using fallback hardcoded semesters');
          
          // Create fallback semester data with IDs - exactly 6 semesters
          this.semestersData = [
            { id: 1, name: '1st Sem 2025-2026' },
            { id: 2, name: '2nd Sem 2025-2026' },
            { id: 3, name: 'Summer 2026' },
            { id: 4, name: '1st Sem 2026-2027' },
            { id: 5, name: '2nd Sem 2026-2027' },
            { id: 6, name: 'Summer 2027' }
          ];
          
          // Fallback to hardcoded semesters in case of error
          this.semesterOptions = this.semestersData.map(s => s.name);
          // Don't set selectedSemester, leave it as empty string
          // Remove call to filterSchedulesBySemester()
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
    generateWeekDays() {
      const today = new Date()
      const monday = new Date(today)
      monday.setDate(today.getDate() - today.getDay() + 1)

      this.weekDays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'].map((name, index) => {
        const date = new Date(monday)
        date.setDate(monday.getDate() + index)
        
        // Format the date as "Mar 17, 2025" to match the design
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
        
        console.log('Time comparison:', 
          { timeSlot, timeSlotMinutes, 
            startTime, startTimeMinutes, 
            endTime, endTimeMinutes,
            isWithinRange: timeSlotMinutes >= startTimeMinutes && timeSlotMinutes < endTimeMinutes
          }
        );
        
        // Check if timeSlot is within or at the start of the schedule
        return timeSlotMinutes >= startTimeMinutes && timeSlotMinutes < endTimeMinutes;
      } catch (error) {
        console.error('Error checking if time slot is in schedule:', error);
        return false;
      }
    },
    convertTimeToMinutes(time) {
      try {
        // Handle undefined or invalid time value
        if (!time) {
          console.error('Invalid time: undefined or empty');
          return 0;
        }
        
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
          console.error('Invalid time components:', { hourStr, minuteStr, period, time });
          return 0;
        }
        
        let hour = parseInt(hourStr);
        const minute = parseInt(minuteStr);
        
        // Convert to 24-hour format
        if (period === 'PM' && hour < 12) hour += 12;
        if (period === 'AM' && hour === 12) hour = 0;
        
        const totalMinutes = hour * 60 + minute;
        // For debugging
        console.log(`Time conversion: "${time}" = ${hour}:${minute} (${period}) = ${totalMinutes} minutes`);
        
        // Return total minutes
        return totalMinutes;
      } catch (error) {
        console.error('Error converting time to minutes:', time, error);
        return 0;
      }
    },
    getScheduleForTimeSlot(dayName, timeSlot) {
      if (!this.schedules || this.schedules.length === 0) {
        return null;
      }
      
      const timeSlotMinutes = this.convertTimeToMinutes(timeSlot);
      
      // Filter by current lab room
      return this.schedules.find(schedule => {
        // Check if day matches primary day OR secondary day
        const dayMatches = schedule.day === dayName || schedule.secondDay === dayName;
        
        const matchesLab = schedule.labRoom === this.selectedLab;
        const startTimeMinutes = this.convertTimeToMinutes(schedule.startTime);
        const matchesExactStartTime = timeSlotMinutes === startTimeMinutes;
        
        return matchesLab && dayMatches && matchesExactStartTime;
      }) || null;
    },
    isTimeSlotWithinSchedule(dayName, timeSlot) {
      if (!this.schedules || this.schedules.length === 0) {
        return false;
      }
      
      const timeSlotMinutes = this.convertTimeToMinutes(timeSlot);
      
      // Filter by current lab room
      return this.schedules.some(schedule => {
        // Skip schedules that don't have all required properties
        if (!schedule.labRoom || !schedule.day || !schedule.startTime || !schedule.endTime) {
          console.warn('Schedule is missing required properties:', schedule);
          return false;
        }
        
        // Check if day matches primary day OR secondary day
        const dayMatches = schedule.day === dayName || schedule.secondDay === dayName;
        
        if (schedule.labRoom !== this.selectedLab || !dayMatches) {
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
        // Check if day matches primary day OR secondary day
        const dayMatches = schedule.day === dayName || schedule.secondDay === dayName;
        
        if (schedule.labRoom !== this.selectedLab || !dayMatches) {
          return false;
        }
        
        const startMinutes = this.convertTimeToMinutes(schedule.startTime);
        return timeSlotMinutes === startMinutes;
      });
    },
    getScheduleTitle(dayName, timeSlot) {
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
        // Check if day matches primary day OR secondary day
        const dayMatches = s.day === dayName || s.secondDay === dayName;
        
        if (s.labRoom !== this.selectedLab || !dayMatches) {
          return false;
        }
        
        const slotMinutes = this.convertTimeToMinutes(timeSlot);
        const startMinutes = this.convertTimeToMinutes(s.startTime);
        const endMinutes = this.convertTimeToMinutes(s.endTime);
        
        // Include the ending time slot as well
        return slotMinutes >= startMinutes && slotMinutes <= endMinutes;
      });
      
      if (!schedule) return '';
      
      // Return the appropriate CSS class based on status
      switch (schedule.status) {
        case 'draft':
          return 'status-draft';
        case 'pending':
          return 'status-pending';
        case 'approved':
          return 'status-approved';
        default:
          return 'status-draft';
      }
    },
    getScheduleStyle(dayName, timeSlot) {
      // Find the specific schedule that contains this time slot
      const schedule = this.schedules.find(s => {
        // Check if day matches primary day OR secondary day
        const dayMatches = s.day === dayName || s.secondDay === dayName;
        
        if (s.labRoom !== this.selectedLab || !dayMatches) {
          return false;
        }
        
        const slotMinutes = this.convertTimeToMinutes(timeSlot);
        const startMinutes = this.convertTimeToMinutes(s.startTime);
        const endMinutes = this.convertTimeToMinutes(s.endTime);
        
        return slotMinutes >= startMinutes && slotMinutes < endMinutes;
      });
      
      if (!schedule) return {};
      
      // Use different colors for different schedule statuses
      let backgroundColor;
      switch (schedule.status) {
        case 'draft':
          backgroundColor = '#DD385A'; // Red
          break;
        case 'pending':
          backgroundColor = '#FFA500'; // Orange/Yellow
          break;
        case 'approved':
          backgroundColor = '#4CAF50'; // Green
          break;
        default:
          backgroundColor = '#DD385A';
      }
      
      return { backgroundColor };
    },
    handleNewSemester() {
      this.showNewSemesterModal = true;
    },
    handleSemesterChange() {
      if (this.selectedSemester === 'new') {
        this.handleNewSemester();
        this.selectedSemester = ''; // Reset selection
      }
    },
    createNewSemester() {
      // Here you'll add the logic to create the new semester
      console.log('Creating new semester:', this.newSemester);
      this.showNewSemesterModal = false;
      // Reset form
      this.newSemester = {
        semester: '',
        schoolYear: ''
      };
    },
    openCreateSchedule() {
      this.showCreateScheduleModal = true;
      this.resetNewScheduleForm();
      // Reset used courses list and editing schedule
      this.currentlyEditingSchedule = null;
      this.usedCoursesList = [];
    },
    // Add the formatTime function
    formatTime(hour, minute, period) {
      // Pad the hour and minute with zeros if needed
      const formattedHour = hour.toString().padStart(2, '0');
      const formattedMinute = minute.toString().padStart(2, '0');
      
      // Return in the format "HH:MM AM/PM"
      return `${formattedHour}:${formattedMinute} ${period}`;
    },
    
    async createSchedule() {
      try {
        console.log('Creating schedule...');
        
        // Simple validation check
        if (!this.isScheduleFormValid) {
          alert('Please fill in all required fields');
          return;
        }
        
        // Format times for easy comparison and conflict checking
        const formattedStartTime = `${this.newSchedule.startHour}:${this.newSchedule.startMinute} ${this.newSchedule.startPeriod}`;
        const formattedEndTime = `${this.newSchedule.endHour}:${this.newSchedule.endMinute} ${this.newSchedule.endPeriod}`;
        
        // Check for conflicts with approved schedules
        const conflictExists = this.checkForScheduleConflicts(
          this.newSchedule.day, 
          formattedStartTime, 
          formattedEndTime,
          this.newSchedule.labRoom,
          this.newSchedule.secondDay
        );
        
        if (conflictExists) {
          alert('This schedule conflicts with an existing approved schedule. Please choose a different time or lab room.');
          return;
        }
        
        // Get authentication token for the API request
        const token = sessionStorage.getItem('token') || localStorage.getItem('token');
        
        // Get user ID for created_by field
        let userId = null;
        try {
          const userStr = sessionStorage.getItem('user') || localStorage.getItem('user');
          if (userStr) {
            const userData = JSON.parse(userStr);
            userId = userData.id;
            console.log('Using current user ID for created_by:', userId);
          }
        } catch (error) {
          console.error('Error parsing user data:', error);
        }
        
        if (!token) {
          alert('You must be logged in to create a schedule');
          this.$router.push('/login');
          return;
        }
        
        // Get semester ID based on the currently selected semester
        const semesterName = this.newSchedule.semester;
        const semesterObj = this.semestersData.find(s => s.name === semesterName);
        
        if (!semesterObj) {
          alert('Selected semester not found. Please try again.');
          return;
        }
        
        const semesterId = semesterObj.id;
        console.log(`Using semester ID ${semesterId} (${semesterName}) for schedule creation`);
        
        // Get lab room ID
        const labRoomName = this.newSchedule.labRoom;
        const labRoomObj = this.labRoomsData.find(lr => lr.name === labRoomName);
        
        if (!labRoomObj) {
          alert('Selected lab room not found. Please try again.');
          return;
        }
        
        const labRoomId = labRoomObj.id;
        
        // Get selected course from the availableCoursesOffered
        const courseCode = this.newSchedule.courseCode;
        const selectedCourse = this.availableCoursesOffered.find(c => c.code === courseCode);
        
        if (!selectedCourse) {
          alert('Selected course not found. Please try again.');
          return;
        }
        
        // If the course has an originalSemester property, it means we've modified the display
        const needsNewCourseOffering = selectedCourse.originalSemester !== undefined && 
                                      selectedCourse.originalSemester !== selectedCourse.semester;
        
        console.log('Selected course:', selectedCourse);
        console.log('Needs new course offering:', needsNewCourseOffering);
        
        // Format times for API
        const startHour = parseInt(this.newSchedule.startHour);
        const startMinute = this.newSchedule.startMinute;
        const startPeriod = this.newSchedule.startPeriod;
        
        const endHour = parseInt(this.newSchedule.endHour);
        const endMinute = this.newSchedule.endMinute;
        const endPeriod = this.newSchedule.endPeriod;
        
        // Format as "10:30 AM" for API
        const startTime = `${startHour}:${startMinute} ${startPeriod}`;
        const endTime = `${endHour}:${endMinute} ${endPeriod}`;
        
        // Check if we need to create a new course offering for this semester
        let courseOfferingId = null;
        let courseName = selectedCourse.name;
        
        // If this course needs a new course offering for the target semester
        if (needsNewCourseOffering) {
          console.log(`Creating a new course offering for ${courseName} in semester ${semesterName}`);
          
          try {
            // Create a new course offering for this semester
            const courseOfferingResponse = await courseOfferingAPI.create({
              code: courseCode,
              name: courseName,
              year_and_section: this.newSchedule.section,
              semester_id: semesterId
            });
            
            console.log('Created new course offering for the selected semester:', courseOfferingResponse.data);
            courseOfferingId = courseOfferingResponse.data.id;
            
            // After creating a new course offering, refresh the course offerings data
            await this.fetchCourseOfferings();
          } catch (error) {
            console.error('Failed to create course offering:', error);
            // Continue with schedule creation anyway
          }
        } else {
          console.log('Using existing course offering for this semester');
        }
        
        // Create schedule data
        const scheduleData = {
          semester_id: semesterId,
          section: this.newSchedule.section,
          course_code: courseCode,
          course_name: courseName,
          day: this.newSchedule.day,
          second_day: this.newSchedule.secondDay || null,
          lab_room_id: labRoomId,
          instructor_name: this.newSchedule.instructorName,
          start_time: startTime,
          end_time: endTime,
          schedule_types: this.scheduleTypes,
          class_type: this.scheduleTypes.length > 0 ? this.scheduleTypes.join('/').toLowerCase() : 'unknown',
          status: 'draft',
          created_by: userId // Include the current user's ID in the schedule data
        };
        
        console.log('Creating schedule with data:', scheduleData);
        
        // Create the schedule using axios directly with token header instead of scheduleAPI
        // This ensures we have full control over the authentication header
        const response = await axios.post('http://127.0.0.1:8000/api/schedules', scheduleData, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-User-Data': sessionStorage.getItem('user') || localStorage.getItem('user') // Also include user data in headers
          }
        });
        
        console.log('Schedule created successfully:', response.data);
        
        // Reset form and refresh data
        this.showCreateScheduleModal = false;
        this.resetScheduleForm();
        
        // Reset tracking variables
        this.currentlyEditingSchedule = null;
        this.usedCoursesList = [];
        
        // Refresh data from API
        await this.loadSchedulesFromAPI();
        await this.fetchCourseOfferings();
        
        alert('Schedule created successfully!');
        
      } catch (error) {
        console.error('Error creating schedule:', error);
        let errorMessage = 'Failed to create schedule';
        
        if (error.response) {
          console.error('Error response:', error.response.data);
          if (error.response.status === 401) {
            // Handle unauthorized error specifically
            errorMessage = 'Authentication failed. Please try logging out and back in.';
            // Consider redirecting to login page
            setTimeout(() => {
              this.$router.push('/login');
            }, 2000);
          } else {
            errorMessage += ': ' + (error.response.data.detail || error.message || 'Unknown error');
          }
        } else {
          errorMessage += ': ' + (error.message || 'Unknown error');
        }
        
        alert(errorMessage);
      }
    },
    
    async deleteSchedule(scheduleId) {
      try {
        // Get the schedule details
        const schedule = this.schedules.find(s => s.id === scheduleId);
        if (!schedule) {
          throw new Error('Schedule not found');
        }
        
        // Delete the schedule
        await scheduleAPI.delete(scheduleId);
        
        // Refresh data
        await this.loadSchedulesFromAPI();
        await this.fetchCourseOfferings();
        
        alert('Schedule deleted successfully!');
        
      } catch (error) {
        console.error('Error deleting schedule:', error);
        alert('Failed to delete schedule: ' + (error.message || 'Unknown error'));
      }
    },
    validateScheduleForm() {
      // Add your validation logic here
      return true;
    },
    triggerFileInput() {
      this.$refs.fileInput.click();
    },
    handleFileSelect(event) {
      const file = event.target.files[0];
      if (file) {
        this.selectedFile = file;
      }
    },
    handleFileDrop(event) {
      const file = event.dataTransfer.files[0];
      const allowedTypes = ['.xlsx', '.csv'];
      const fileExtension = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
      
      if (allowedTypes.includes(fileExtension)) {
        this.selectedFile = file;
      } else {
        alert('Please upload a valid Excel or CSV file.');
      }
    },
    downloadSampleTemplate() {
      // Create a workbook with a worksheet
      const wb = XLSX.utils.book_new();
      
      // Create sample data exactly matching the format in the screenshot
      const sampleData = [
        { A: "Course Code", B: "Course Name", C: "Year and Section", D: "Semester" },
        { A: "FW123.23", B: "Ignatian Spirituality & Christian Life 1", C: "IT-1A", D: "1st Sem" },
        { A: "FW123.23", B: "Ignatian Spirituality & Christian Life 1", C: "IT-1B", D: "1st Sem" },
        { A: "FW123.23", B: "Ignatian Spirituality & Christian Life 1", C: "CS-1A", D: "1st Sem" },
        { A: "GEC123.23", B: "Science, Technology & Society", C: "IT-1A", D: "1st Sem" },
        { A: "GEC123.23", B: "Science, Technology & Society", C: "IT-1B", D: "1st Sem" },
        { A: "GEC123.23", B: "Science, Technology & Society", C: "CS-1A", D: "1st Sem" },
        { A: "GEC112.23", B: "Mathematics in the Modern World", C: "IT-1A", D: "2nd Sem" },
        { A: "GEC112.23", B: "Mathematics in the Modern World", C: "IT-1B", D: "2nd Sem" },
        { A: "GEC112.23", B: "Mathematics in the Modern World", C: "CS-1A", D: "2nd Sem" },
        { A: "CC103.23", B: "Introduction to Computing", C: "IT-1A", D: "2nd Sem" },
        { A: "CC103.23", B: "Introduction to Computing", C: "IT-1B", D: "2nd Sem" },
        { A: "CC103.23", B: "Introduction to Computing", C: "CS-1A", D: "2nd Sem" }
      ];
      
      // Create a worksheet from the data
      const ws = XLSX.utils.json_to_sheet(sampleData, { skipHeader: true });
      
      // Set column widths
      const colWidths = [
        { wch: 15 }, // A: Course Code
        { wch: 40 }, // B: Course Name
        { wch: 15 }, // C: Year and Section
        { wch: 15 }  // D: Semester
      ];
      
      ws['!cols'] = colWidths;
      
      // Add the worksheet to the workbook
      XLSX.utils.book_append_sheet(wb, ws, "Course Offerings");
      
      // Generate Excel file
      const excelBuffer = XLSX.write(wb, { bookType: 'xlsx', type: 'array' });
      
      // Convert to Blob
      const blob = new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
      
      // Create download link
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'course_offerings_template.xlsx';
      document.body.appendChild(a);
      a.click();
      
      // Clean up
      setTimeout(() => {
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }, 0);
    },
    async uploadFile(event) {
      if (!this.selectedFile) {
        alert('Please select a file to upload.');
        return;
      }
      
      const file = this.selectedFile;
      console.log('Processing file:', file.name);
      
      // Check file extension
      const fileExt = file.name.split('.').pop().toLowerCase();
      if (fileExt !== 'xlsx' && fileExt !== 'csv') {
        alert('Please upload an Excel (.xlsx) or CSV (.csv) file.');
        return;
      }
      
      const reader = new FileReader();
      
      reader.onload = async (e) => {
        try {
          // Use a try/catch block to handle any parsing errors
          let wb;
          
          if (fileExt === 'csv') {
            // Handle CSV files
            const csvData = e.target.result;
            wb = XLSX.read(csvData, { type: 'string' });
          } else {
            // Handle Excel files
            const data = e.target.result;
            wb = XLSX.read(data, { type: 'binary' });
          }
          
          // Get the first sheet
          const firstSheetName = wb.SheetNames[0];
          if (!firstSheetName) {
            throw new Error('No worksheet found in file');
          }
          
          const ws = wb.Sheets[firstSheetName];
          
          // Use row object array format (each row is an object with keys)
          const rawData = XLSX.utils.sheet_to_json(ws);
          console.log('Raw data from Excel:', rawData);
          
          if (!rawData || rawData.length === 0) {
            alert('No data found in the file or invalid format.');
            return;
          }
          
          // Process the course data
          const processedCourses = [];
          let hasErrors = false;
          
          // Get semester mappings before processing
          const semesterMappings = this.getSemesterMappings();
          
          // Process each row of data
          for (const row of rawData) {
            // Skip header row if present
            if (row['Course Code'] === 'Course Code') continue;
            
            // Get values from the Excel columns
            const code = row['Course Code'] || row['A'];
            const name = row['Course Name'] || row['B'];
            const yearSection = row['Year and Section'] || row['C'];
            const semester = row['Semester'] || row['D'];
            
            // Basic validation
            if (!code || !name || !yearSection || !semester) {
              console.error('Missing required data in row:', row);
              hasErrors = true;
              continue;
            }
            
            // Find the full semester name from our mappings
            const mappedSemester = semesterMappings[semester];
            if (!mappedSemester) {
              console.error('Invalid semester:', semester);
              hasErrors = true;
              continue;
            }
            
            // Find the semester in our options
            const semesterData = this.semesterOptions.find(s => s === mappedSemester);
            if (!semesterData) {
              console.error('Semester not found in options:', mappedSemester);
              hasErrors = true;
              continue;
            }
            
            // Get the semester ID (assuming it's stored in a data structure that maps names to IDs)
            // Example: If your backend returns {id: 1, name: "1st Sem 2025-2026"} objects, 
            // you might need to adjust this to get the ID correctly
            const semesterId = this.getSemesterIdFromName(semesterData);
            
            processedCourses.push({
              code: code.toString().trim(),
              name: name.toString().trim(),
              year_and_section: yearSection.toString().trim(),
              semester_id: semesterId,
              is_hidden: false
            });
          }
          
            if (hasErrors) {
            alert('Some rows had errors and were skipped. Please check the console for details.');
            }
          
          if (processedCourses.length === 0) {
            alert('No valid courses found in the file.');
            return;
          }
          
          // Send to backend API
          const token = sessionStorage.getItem('token') || localStorage.getItem('token');
          const response = await axios.post(
            'http://127.0.0.1:8000/api/course-offerings/import',
            processedCourses,
            {
              headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
              }
            }
          );
          
          alert(`Successfully imported ${processedCourses.length} courses to the database.`);
          this.showFileUploadModal = false;
          this.selectedFile = null;
          
          // Refresh the course offerings list
          await this.fetchCourseOfferings();
          
        } catch (error) {
          console.error('Error processing file:', error);
          alert('Error processing the file: ' + (error.message || 'Invalid file format'));
        }
      };
      
      reader.onerror = () => {
        console.error('Error reading file');
        alert('Error reading the file. Please try again.');
      };
      
      // Read the file based on its type
      if (fileExt === 'csv') {
        reader.readAsText(file);
      } else {
        reader.readAsBinaryString(file);
      }
    },
    
    async fetchCourseOfferings() {
      try {
        console.log('Fetching course offerings from API...');
        const token = sessionStorage.getItem('token') || localStorage.getItem('token');
        const response = await axios.get('http://127.0.0.1:8000/api/course-offerings', {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          },
          withCredentials: false,
          params: {
            // No longer filtering by hidden status - show all courses
            include_hidden: true
          },
          timeout: 5000
        });
        
        // Make sure we have semesters data available first
        if (!this.semestersData || this.semestersData.length === 0) {
          try {
            await this.fetchSemesters(); // Fetch semesters if not already available
          } catch (err) {
            console.error('Error fetching semesters:', err);
            // Continue anyway, using fallback mapping
          }
        }
        
        // Debug what we received
        console.log('Raw courses from API:', response.data);
        console.log('Total courses received:', Array.isArray(response.data.courses) ? response.data.courses.length : 'Not an array');
        console.log('Available semesters:', this.semestersData);
        
        if (Array.isArray(response.data.courses)) {
          this.coursesOffered = response.data.courses.map(course => {
            // Get the semester name from the semester_id
            let semesterName = '';
            
            // First try to find it in the semestersData if available
            if (this.semestersData && this.semestersData.length > 0) {
              const semesterObj = this.semestersData.find(s => s.id === course.semester_id);
              if (semesterObj) {
                semesterName = semesterObj.name;
                console.log(`Mapped semester_id ${course.semester_id} to name "${semesterName}" from semestersData`);
              } else {
                console.warn(`Could not find semester with ID ${course.semester_id} in semestersData`);
              }
            }
            
            // If not found in semestersData, use a more dynamic approach
            if (!semesterName) {
              // Instead of hardcoded values, fetch the semester data directly to make sure we have the latest
              console.log(`No semester name found for ID ${course.semester_id}, attempting to fetch it`);
              
              // Use a generic fallback but try to fetch the actual semester data asynchronously
              semesterName = `Semester ${course.semester_id}`;
              
              // Immediately trigger a semester fetch to update the data for next time
              this.fetchSpecificSemester(course.semester_id)
                .then(fetchedSemester => {
                  if (fetchedSemester) {
                    // Find the course in our array and update its semester name
                    const courseIndex = this.coursesOffered.findIndex(c => 
                      c.code === course.code && c.semester_id === course.semester_id
                    );
                    
                    if (courseIndex !== -1) {
                      this.coursesOffered[courseIndex].semester = fetchedSemester.name;
                      console.log(`Updated semester name for ${course.code} to "${fetchedSemester.name}"`);
                    }
                  }
                })
                .catch(err => {
                  console.error(`Error fetching specific semester ${course.semester_id}:`, err);
                });
            }
            
            return {
              code: course.code,
              name: course.name,
              section: course.year_and_section,
              semester: semesterName,
              semester_id: course.semester_id, // Store the semester_id for filtering
              id: course.id,
              is_hidden: course.is_hidden
            };
          });
          
          console.log('Transformed course offerings:', this.coursesOffered);
          console.log('Total courses after transform:', this.coursesOffered.length);
        } else {
          console.error('Invalid courses data format:', response.data);
          this.coursesOffered = [];
        }
        
      } catch (error) {
        console.error('Error fetching course offerings:', error);
        console.log('Using empty course offerings array as fallback');
        this.coursesOffered = [];
      }
    },
    
    // Add a new method to fetch a specific semester by ID
    async fetchSpecificSemester(semesterId) {
      try {
        console.log(`Fetching specific semester with ID ${semesterId}`);
        const token = sessionStorage.getItem('token') || localStorage.getItem('token');
        
        const response = await axios.get(`http://127.0.0.1:8000/api/semesters/${semesterId}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          },
          withCredentials: false,
          timeout: 5000
        });
        
        if (response.data) {
          console.log(`Got semester data for ID ${semesterId}:`, response.data);
          
          // Add this semester to our semestersData array if it's not already there
          if (!this.semestersData.some(s => s.id === response.data.id)) {
            this.semestersData.push(response.data);
            console.log(`Added semester "${response.data.name}" to semestersData`);
            
            // Refresh semester options if needed
            if (!this.semesterOptions.includes(response.data.name)) {
              this.semesterOptions.push(response.data.name);
              console.log(`Added "${response.data.name}" to semester options`);
            }
          }
          
          return response.data;
        }
        return null;
      } catch (error) {
        console.error(`Error fetching semester ${semesterId}:`, error);
        return null;
      }
    },
    async hideCourseOffering(courseId) {
      try {
        if (!courseId) {
          console.error('Invalid course ID:', courseId);
          return;
        }
        
        console.log(`Hiding course offering with ID: ${courseId}`);
        const token = sessionStorage.getItem('token') || localStorage.getItem('token');
        
        // Use a more complete request configuration
        await axios.put(
          `http://127.0.0.1:8000/api/course-offerings/${courseId}/hide`,
          { is_hidden: true }, // Send actual data in the request body
          {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Accept': 'application/json',
              'Content-Type': 'application/json'
            },
            withCredentials: false,
            timeout: 5000
          }
        );
        
        console.log(`Successfully hid course offering with ID: ${courseId}`);
        
        // Update local state
        const courseIndex = this.coursesOffered.findIndex(c => c.id === courseId);
        if (courseIndex !== -1) {
          this.coursesOffered[courseIndex].is_hidden = true;
        }
        
      } catch (error) {
        console.error('Error hiding course offering:', error);
        if (error.response) {
          console.error('Error response data:', error.response.data);
          console.error('Error response status:', error.response.status);
        }
        throw error; // Re-throw to allow parent function to handle error
      }
    },
    
    async unhideCourseOffering(courseId) {
      try {
        if (!courseId) {
          console.error('Invalid course ID:', courseId);
          return;
        }
        
        console.log(`Unhiding course offering with ID: ${courseId}`);
        const token = sessionStorage.getItem('token') || localStorage.getItem('token');
        
        // Use a more complete request configuration
        await axios.put(
          `http://127.0.0.1:8000/api/course-offerings/${courseId}/unhide`,
          { is_hidden: false }, // Send actual data in the request body
          {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Accept': 'application/json',
              'Content-Type': 'application/json'
            },
            withCredentials: false,
            timeout: 5000
          }
        );
        
        console.log(`Successfully unhid course offering with ID: ${courseId}`);
        
        // Update local state
        const courseIndex = this.coursesOffered.findIndex(c => c.id === courseId);
        if (courseIndex !== -1) {
          this.coursesOffered[courseIndex].is_hidden = false;
        }
        
      } catch (error) {
        console.error('Error unhiding course offering:', error);
        if (error.response) {
          console.error('Error response data:', error.response.data);
          console.error('Error response status:', error.response.status);
        }
        throw error; // Re-throw to allow parent function to handle error
      }
    },
    toggleScheduleType(type) {
      const index = this.scheduleTypes.indexOf(type);
      if (index === -1) {
        this.scheduleTypes.push(type);
      } else {
        this.scheduleTypes.splice(index, 1);
      }
    },
    clearAllSchedules() {
      try {
        // Confirm before clearing
        if (!confirm('Are you sure you want to clear ALL schedules? This cannot be undone.')) {
          return;
        }
        
        // Use API endpoint to delete all schedules from database
        scheduleAPI.deleteAll()
          .then(response => {
            console.log('All schedules cleared via API:', response.data);
            
            // Reset the component's schedule arrays
            this.allSchedules = [];
            this.schedules = [];
            
            // Clear localStorage for compatibility with other views
        localStorage.removeItem('labSchedules');
        localStorage.removeItem('sysadmin_schedules');
        localStorage.removeItem('acad_coor_schedules');
        localStorage.removeItem('schedules');
        localStorage.removeItem('viewer_schedules');
        localStorage.removeItem('generic_schedules');
        localStorage.removeItem('coursesOffered');
        this.coursesOffered = [];
        
        console.log('All schedules and course offerings cleared');
            alert('All schedules have been deleted successfully from the database');
        
        // Reload the page to ensure everything is reset
        window.location.reload();
          })
          .catch(error => {
            console.error('Error clearing schedules via API:', error);
            alert('Error clearing schedules. Please try again.');
          });
      } catch (error) {
        console.error('Error clearing schedules:', error);
        alert('Error clearing schedules. Please try again.');
      }
    },
    openEditDeleteModal(dayName, timeSlot) {
      const schedule = this.getScheduleForTimeSlot(dayName, timeSlot);
      if (!schedule) return;
      
      this.currentlyEditingSchedule = {
        id: schedule.id,
        course_code: schedule.courseCode
      };
      
      console.log('Editing schedule:', this.currentlyEditingSchedule);
      
      if (schedule) {
        this.selectedSchedule = { ...schedule };
        
        // Parse times
        const startTimeParts = schedule.startTime.match(/(\d+):(\d+)\s+(AM|PM)/);
        const endTimeParts = schedule.endTime.match(/(\d+):(\d+)\s+(AM|PM)/);
        
        if (startTimeParts && endTimeParts) {
          this.editSchedule = {
            id: schedule.id,
            types: [...schedule.types],
            semester: schedule.semester,
            section: schedule.section,
            courseCode: schedule.courseCode,
            day: schedule.day,
            labRoom: schedule.labRoom,
            instructorName: schedule.instructorName,
            startHour: startTimeParts[1],
            startMinute: startTimeParts[2],
            startPeriod: startTimeParts[3],
            endHour: endTimeParts[1],
            endMinute: endTimeParts[2],
            endPeriod: endTimeParts[3],
            secondDay: schedule.secondDay
          };
          
          this.showEditDeleteModal = true;
        }
      }
    },
    
    openEditSchedule() {
      this.showEditDeleteModal = false;
      
      // Pre-fill the edit form with current values
      this.editSchedule = {
        id: this.selectedSchedule.id,
        types: [...this.selectedSchedule.types],
        semester: this.selectedSchedule.semester,
        section: this.selectedSchedule.section,
        courseCode: this.selectedSchedule.courseCode,
        day: this.selectedSchedule.day,
        labRoom: this.selectedSchedule.labRoom,
        instructorName: this.selectedSchedule.instructorName,
        startHour: '',
        startMinute: '00',
        startPeriod: 'AM',
        endHour: '',
        endMinute: '00',
        endPeriod: 'AM',
        secondDay: this.selectedSchedule.secondDay
      };
      
      setTimeout(() => {
        this.showEditScheduleModal = true;
      }, 100);
    },
    
    toggleEditScheduleType(type) {
      const index = this.editSchedule.types.indexOf(type);
      if (index === -1) {
        this.editSchedule.types.push(type);
      } else {
        this.editSchedule.types.splice(index, 1);
      }
    },
    
    updateSchedule() {
      // Create a copy of the selected schedule to modify
      const scheduleToUpdate = { ...this.selectedSchedule };
      
      // Allow updating of draft and approved schedules
      // If it's approved, we will change the status to draft
      if (scheduleToUpdate.status !== 'draft' && scheduleToUpdate.status !== 'approved') {
        alert('Only draft or approved schedules can be edited. This schedule is ' + scheduleToUpdate.status);
        return;
      }
      
      const wasApproved = scheduleToUpdate.status === 'approved';
      
      // Update fields if the user changed them, otherwise keep existing values
      scheduleToUpdate.semester = this.editSchedule.semester || scheduleToUpdate.semester;
      scheduleToUpdate.section = this.editSchedule.section || scheduleToUpdate.section;
      scheduleToUpdate.courseCode = this.editSchedule.courseCode || scheduleToUpdate.courseCode;
      scheduleToUpdate.day = this.editSchedule.day || scheduleToUpdate.day;
      scheduleToUpdate.labRoom = this.editSchedule.labRoom || scheduleToUpdate.labRoom;
      scheduleToUpdate.instructorName = this.editSchedule.instructorName || scheduleToUpdate.instructorName;
      scheduleToUpdate.secondDay = this.editSchedule.secondDay;  // Can be set to empty string to remove it
      
      // Handle time changes
      let startTimeChanged = false;
      let endTimeChanged = false;
      let newStartTime = scheduleToUpdate.startTime;
      let newEndTime = scheduleToUpdate.endTime;
      
      if (this.editSchedule.startHour && this.editSchedule.startMinute) {
        newStartTime = `${this.editSchedule.startHour}:${this.editSchedule.startMinute} ${this.editSchedule.startPeriod}`;
        scheduleToUpdate.startTime = newStartTime;
        startTimeChanged = true;
      }
      
      if (this.editSchedule.endHour && this.editSchedule.endMinute) {
        newEndTime = `${this.editSchedule.endHour}:${this.editSchedule.endMinute} ${this.editSchedule.endPeriod}`;
        scheduleToUpdate.endTime = newEndTime;
        endTimeChanged = true;
      }
      
      // Check for conflicts with approved schedules if time or location changed
      if (startTimeChanged || endTimeChanged || 
          this.editSchedule.day !== scheduleToUpdate.day || 
          this.editSchedule.labRoom !== scheduleToUpdate.labRoom || 
          this.editSchedule.secondDay !== scheduleToUpdate.secondDay) {
        
        // Only check for conflicts with other approved schedules
        const dayToCheck = this.editSchedule.day || scheduleToUpdate.day;
        const labToCheck = this.editSchedule.labRoom || scheduleToUpdate.labRoom;
        const secondDayToCheck = this.editSchedule.secondDay !== undefined ? 
                                this.editSchedule.secondDay : 
                                scheduleToUpdate.secondDay;
        
        // Skip the current schedule when checking for conflicts
        const conflictExists = this.checkForScheduleConflicts(
          dayToCheck, 
          newStartTime, 
          newEndTime,
          labToCheck,
          secondDayToCheck,
          scheduleToUpdate.id // Skip this schedule ID when checking conflicts
        );
        
        if (conflictExists) {
          alert('This schedule conflicts with an existing approved schedule. Please choose a different time or lab room.');
          return;
        }
      }
      
      // Use the updated or original schedule types
      const types = this.editSchedule.types.length > 0 ? this.editSchedule.types : scheduleToUpdate.types;
      scheduleToUpdate.types = types;
      
      // Determine class_type based on selected types
      let classType = '';
      if (types.includes('Lab') && types.includes('Lec')) {
        classType = 'lab/lec';
      } else if (types.includes('Lab')) {
        classType = 'lab';
      } else if (types.includes('Lec')) {
        classType = 'lec';
      }
      scheduleToUpdate.class_type = classType;
      
      // Update title to reflect schedule type
      scheduleToUpdate.title = `${scheduleToUpdate.courseCode} (${types.join('/')})`;
      
      // Get course name for the course code, if it changed
      if (this.editSchedule.courseCode) {
        const selectedCourse = this.availableCoursesOffered.find(course => course.code === this.editSchedule.courseCode);
        scheduleToUpdate.courseName = selectedCourse ? selectedCourse.name : scheduleToUpdate.courseName;
      }
      
      // Update details
      scheduleToUpdate.details = `${scheduleToUpdate.courseName}\n${scheduleToUpdate.section}\n${scheduleToUpdate.instructorName}`;
      
      // Prepare data for API
      const scheduleData = {
        semester_id: this.getSemesterId(scheduleToUpdate.semester),
        section: scheduleToUpdate.section,
        course_code: scheduleToUpdate.courseCode,
        course_name: scheduleToUpdate.courseName,
        day: scheduleToUpdate.day,
        second_day: scheduleToUpdate.secondDay || null,
        lab_room_id: this.getLabRoomId(scheduleToUpdate.labRoom),
        instructor_name: scheduleToUpdate.instructorName,
        start_time: scheduleToUpdate.startTime,
        end_time: scheduleToUpdate.endTime,
        schedule_types: scheduleToUpdate.types,
        class_type: scheduleToUpdate.class_type,
        status: 'draft'  // Always set status to draft when updating
      };
      
      // Function to update schedule details - define it before using it
      const updateScheduleDetails = () => {
        // Use our API service to update the schedule
        scheduleAPI.update(scheduleToUpdate.id, scheduleData)
          .then(response => {
            console.log('Schedule updated via API:', response.data);
            
            // Find and update the schedule in our local array
            const index = this.allSchedules.findIndex(s => s.id === scheduleToUpdate.id);
            if (index !== -1) {
              // If it was approved before, update the status
              if (wasApproved) {
                scheduleToUpdate.status = 'draft';
              }
              this.allSchedules[index] = scheduleToUpdate;
            }
            
            // Refresh the schedules display
            this.filterSchedulesBySemester();
      
            // Show success feedback
            if (wasApproved) {
              alert('Schedule was approved but has been changed to draft status.');
            } else {
              alert('Schedule updated successfully');
            }
            
            this.showEditScheduleModal = false;
            this.resetEditScheduleForm();
            this.currentlyEditingSchedule = null;
            this.usedCoursesList = [];
          })
          .catch(error => {
            console.error('Error updating schedule via API:', error);
            let errorMessage = 'Error updating schedule. Please try again.';
            
            if (error.response) {
              console.error('Error response:', error.response.data);
              errorMessage = error.response.data.detail || errorMessage;
            }
            
            alert(errorMessage);
          });
      };
      
      try {
        // If the schedule was previously approved, first update the status to draft
        if (wasApproved) {
          scheduleAPI.updateStatus(scheduleToUpdate.id, 'draft')
            .then(response => {
              console.log(`Schedule ${scheduleToUpdate.id} status changed from approved to draft:`, response.data);
              
              // Now update the schedule details
              updateScheduleDetails();
            })
            .catch(error => {
              console.error('Error changing schedule status:', error);
              let errorMessage = 'Error changing schedule status. Please try again.';
              
              if (error.response) {
                console.error('Error response:', error.response.data);
                errorMessage = error.response.data.detail || errorMessage;
              }
              
              alert(errorMessage);
            });
        } else {
          // If it was already a draft, just update the details
          updateScheduleDetails();
        }
      } catch (error) {
        console.error('Error updating schedule:', error);
        alert('Error updating schedule. Please try again.');
      }
    },
    
    confirmDelete() {
      this.showEditDeleteModal = false;
      setTimeout(() => {
        this.showDeleteConfirmModal = true;
      }, 100);
    },
    
    deleteSchedule() {
      const scheduleId = this.selectedSchedule.id;
      const courseCode = this.selectedSchedule.courseCode;
      
      // Allow deletion of draft and approved schedules
      // If it's approved, we will change the status to draft first
      if (this.selectedSchedule.status !== 'draft' && this.selectedSchedule.status !== 'approved') {
        alert('Only draft or approved schedules can be deleted. This schedule is ' + this.selectedSchedule.status);
        return;
      }
      
      const wasApproved = this.selectedSchedule.status === 'approved';
      
      try {
        // Function to delete the schedule - moved before it's used
        const deleteScheduleDetails = () => {
          // Use our API service to delete the schedule
          scheduleAPI.delete(scheduleId)
            .then(() => {
              // Remove from allSchedules array
              this.allSchedules = this.allSchedules.filter(schedule => 
                schedule.id !== scheduleId
              );
          
              // Update the filtered schedules display
              this.schedules = this.schedules.filter(schedule => 
                schedule.id !== scheduleId
              );
              
              // Show success feedback
              if (wasApproved) {
                alert(`Approved schedule ${courseCode} has been deleted.`);
              } else {
                alert(`Schedule ${courseCode} has been deleted.`);
              }
              
              // Close modals and reset selected schedule
              this.showDeleteConfirmModal = false;
              this.selectedSchedule = null;
              
              // Refresh the schedules display
              this.filterSchedulesBySemester();
              this.currentlyEditingSchedule = null;
              this.usedCoursesList = [];
            })
            .catch(error => {
              console.error('Error deleting schedule via API:', error);
              let errorMessage = 'Error deleting schedule. Please try again.';
              
              if (error.response) {
                console.error('Error response:', error.response.data);
                errorMessage = error.response.data.detail || errorMessage;
              }
              
              alert(errorMessage);
            });
        };

        // If the schedule was previously approved, first update the status to draft
        if (wasApproved) {
          scheduleAPI.updateStatus(scheduleId, 'draft')
            .then(response => {
              console.log(`Schedule ${scheduleId} status changed from approved to draft:`, response.data);
              
              // Now delete the schedule
              deleteScheduleDetails();
            })
            .catch(error => {
              console.error('Error changing schedule status:', error);
              let errorMessage = 'Error changing schedule status. Please try again.';
              
              if (error.response) {
                console.error('Error response:', error.response.data);
                errorMessage = error.response.data.detail || errorMessage;
              }
              
              alert(errorMessage);
            });
        } else {
          // If it was already a draft, just delete it
          deleteScheduleDetails();
        }
      } catch (error) {
        console.error('Error deleting schedule:', error);
        alert('Error deleting schedule. Please try again.');
      }
    },
    
    resetEditScheduleForm() {
      this.editSchedule = {
        id: null,
        types: [],
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
        secondDay: ''
      };
    },
    
    resetScheduleForm() {
      // Reset the newSchedule object to its default values
      this.newSchedule = {
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
        secondDay: ''
      };
      
      // Reset schedule types
      this.scheduleTypes = [];
    },
    showImportCoursesModal() {
      this.showFileUploadModal = true;
    },
    clearCourseOfferings() {
      if (confirm('Are you sure you want to clear all course offerings? This cannot be undone.')) {
        try {
          // Clear frontend state
        this.coursesOffered = [];
          localStorage.removeItem('coursesOffered');
          
          // Use the API to clear all course offerings from the backend
          courseOfferingAPI.deleteAll()
            .then(response => {
              console.log('Course offerings cleared from backend:', response.data);
              alert('Course offerings have been cleared successfully from both frontend and backend.');
            })
            .catch(error => {
              console.error('Error clearing course offerings from backend:', error);
              alert('Error clearing course offerings from backend. Local data has been cleared.');
            });
        } catch (error) {
          console.error('Error in clearCourseOfferings:', error);
          alert('Error clearing course offerings. Please try again.');
        }
      }
    },
    filterSchedulesBySemester() {
      console.log('Filtering by semester:', this.selectedSemester);
      
      if (!this.selectedSemester || !this.allSchedules) {
        this.schedules = [];
        return;
      }
      
      // Filter schedules based on the selected semester
      // Since we're now using semester names directly, we need to match by name
      this.schedules = this.allSchedules.filter(schedule => {
        // Make sure schedule has a semester property
        if (!schedule.semester) return false;
        
        // Match either by exact match or containing the semester name
        return schedule.semester === this.selectedSemester || 
               schedule.semester.includes(this.selectedSemester);
      });
      
      console.log(`Filtered ${this.schedules.length} schedules for semester ${this.selectedSemester}`);
    },
    getScheduleStatus(dayName, timeSlot) {
      const schedule = this.schedules.find(s => 
        s.day === dayName && 
        s.startTime === timeSlot && 
        s.labRoom === this.selectedLab
      );
      return schedule ? schedule.status : null;
    },
    sendForApproval(dayName, timeSlot) {
      const schedule = this.schedules.find(s => 
        s.day === dayName && 
        s.startTime === timeSlot && 
        s.labRoom === this.selectedLab
      );

      if (schedule) {
        if (schedule.status !== 'draft') {
          alert('Only draft schedules can be sent for approval');
          return;
        }

        schedule.status = 'pending';
        this.saveSchedulesToStorage();
        alert('Schedule sent for approval successfully!');
      }
    },
    async sendAllForApproval() {
      try {
        // Filter draft schedules for the current semester
        const currentSemester = this.selectedSemester; // Use selectedSemester instead of currentDisplaySemester
        
        if (!currentSemester) {
          alert('Please select a semester first');
          return;
        }
        
        const draftSchedules = this.schedules.filter(
          schedule => schedule.status === 'draft' && schedule.semester === currentSemester
        );
        
        if (draftSchedules.length === 0) {
          alert('No draft schedules to send for approval in the selected semester');
          return;
        }
        
        // Ask for confirmation using standard confirm dialog instead of SweetAlert2
        const isConfirmed = confirm(`Are you sure you want to send ${draftSchedules.length} draft schedule(s) for approval?`);
        
        if (!isConfirmed) {
          return;
        }
        
        this.isLoading = true;
        
        // Get all schedule IDs to update
        const scheduleIds = draftSchedules.map(schedule => schedule.id);
        
        // Get the semester ID for the notification
        const semesterId = this.getSemesterId(currentSemester);
        
        // Use the bulk update API
        const response = await scheduleAPI.updateBulkStatus(
          scheduleIds,
          'pending',
          semesterId
        );
        
        // Check if the update was successful
        if (response.status === 200) {
          // Update local state
          draftSchedules.forEach(schedule => {
            const index = this.schedules.findIndex(s => s.id === schedule.id);
            if (index !== -1) {
              this.schedules[index].status = 'pending';
            }
          });
          
          // Refresh filtered schedules
          this.filterSchedulesBySemester();
          
          alert(`Successfully sent ${draftSchedules.length} schedules for approval`);
          console.log('All schedules sent for approval successfully');
        } else {
          alert('Failed to send schedules for approval');
          console.error('Error sending schedules for approval:', response);
        }
      } catch (error) {
        console.error('Error in sendAllForApproval:', error);
        // Check if it's a server error with a specific message
        if (error.response && error.response.data && error.response.data.detail) {
          alert(`Error: ${error.response.data.detail}`);
        } else {
          alert('Failed to send schedules for approval. Please try again later.');
        }
      } finally {
        this.isLoading = false;
      }
    },
    validateStartTime() {
      const startTime = `${this.newSchedule.startHour}:${this.newSchedule.startMinute} ${this.newSchedule.startPeriod}`;
      const startMinutes = this.convertTimeToMinutes(startTime);
      const minStartTime = this.convertTimeToMinutes('7:30 AM');
      
      if (startMinutes < minStartTime) {
        alert('Schedule cannot start before 7:30 AM');
        // Reset to 7:30 AM
        this.newSchedule.startHour = '7';
        this.newSchedule.startMinute = '30';
        this.newSchedule.startPeriod = 'AM';
      }
    },
    
    validateEndTime() {
      const endTime = `${this.newSchedule.endHour}:${this.newSchedule.endMinute} ${this.newSchedule.endPeriod}`;
      const endMinutes = this.convertTimeToMinutes(endTime);
      const maxEndTime = this.convertTimeToMinutes('8:00 PM');
      
      if (endMinutes > maxEndTime) {
        alert('Schedule cannot end after 8:00 PM');
        // Reset to 8:00 PM
        this.newSchedule.endHour = '8';
        this.newSchedule.endMinute = '00';
        this.newSchedule.endPeriod = 'PM';
      }
    },
    handleInstructorSelect() {
      if (this.newSchedule.instructorName === 'add_new') {
        this.showAddInstructorModal = true;
        // Reset the selected value so dropdown still works if they cancel
        this.newSchedule.instructorName = '';
      }
    },
    addNewInstructor() {
      if (!this.newInstructorName.trim()) {
        return;
      }
      
      const newInstructor = {
        full_name: this.newInstructorName.trim(),
        email: this.newInstructorEmail.trim() || null
      };

      // Send the new instructor to the API
      axios.post('http://localhost:8000/api/instructors', newInstructor)
        .then(response => {
          console.log('Added new instructor via API:', response.data);
          
          // Add to our array if not already included
          if (!this.instructors.includes(newInstructor.full_name)) {
            this.instructors.push(newInstructor.full_name);
            // Sort alphabetically
            this.instructors.sort();
          }
          
          // Set the new instructor as selected based on which form is open
          if (this.showCreateScheduleModal) {
            this.newSchedule.instructorName = newInstructor.full_name;
          } else if (this.showEditScheduleModal) {
            this.editSchedule.instructorName = newInstructor.full_name;
          }
          
          // Close modal and reset
          this.showAddInstructorModal = false;
          this.newInstructorName = '';
          this.newInstructorEmail = '';
          
          // Show success message
          alert('Instructor added successfully!');
        })
        .catch(error => {
          console.error('Error adding new instructor:', error);
          
          // Fallback to local addition if API is unreachable
          if (!this.instructors.includes(this.newInstructorName.trim())) {
            this.instructors.push(this.newInstructorName.trim());
            this.instructors.sort();
            
            // Save to localStorage as fallback
            localStorage.setItem('instructors', JSON.stringify(this.instructors));
            
            // Set the new instructor as selected based on which form is open
            if (this.showCreateScheduleModal) {
              this.newSchedule.instructorName = this.newInstructorName.trim();
            } else if (this.showEditScheduleModal) {
              this.editSchedule.instructorName = this.newInstructorName.trim();
            }
            
            // Close modal and reset
            this.showAddInstructorModal = false;
            this.newInstructorName = '';
            this.newInstructorEmail = '';
            
            // Show success message
            alert('Instructor added locally (API unavailable)');
          } else {
            // Show error message
            alert('An error occurred while adding the instructor');
          }
        });
    },
    loadInstructorsFromStorage() {
      try {
        const savedInstructors = localStorage.getItem('instructors');
        if (savedInstructors) {
          const parsedInstructors = JSON.parse(savedInstructors);
          if (Array.isArray(parsedInstructors) && parsedInstructors.length > 0) {
            this.instructors = parsedInstructors;
            console.log(`Loaded ${parsedInstructors.length} instructors from localStorage`);
          }
        }
      } catch (error) {
        console.error('Error loading instructors from localStorage:', error);
      }
    },
    handleEditInstructorSelect() {
      if (this.editSchedule.instructorName === 'add_new') {
        this.showAddInstructorModal = true;
        // Reset the selected value so dropdown still works if they cancel
        this.editSchedule.instructorName = '';
      }
    },
    getSemesterId(semesterName) {
      // Find semester ID from the state
      const semester = this.semestersData?.find(s => s.name === semesterName);
      return semester ? semester.id : 1;
    },
    getLabRoomId(labRoomName) {
      // Find lab room ID from the state
      console.log('Getting lab room ID for:', labRoomName);
      console.log('Available lab rooms:', this.labRoomsData);
      
      const labRoom = this.labRoomsData?.find(l => l.name === labRoomName);
      
      if (labRoom) {
        console.log(`Found lab room with ID ${labRoom.id} for ${labRoomName}`);
        return labRoom.id;
      } else {
        console.warn(`Lab room "${labRoomName}" not found in labRoomsData, using default ID 1`);
        return 1;
      }
    },
    loadSemesters() {
      semesterAPI.getAll()
        .then(response => {
          this.semestersData = response.data;
          // Update semester options from the API data
          this.semesterOptions = this.semestersData.map(s => s.name);
          console.log('Loaded semesters from API:', this.semestersData);
        })
        .catch(error => {
          console.error('Error loading semesters:', error);
        });
    },
    loadLabRooms() {
      labRoomAPI.getAll()
        .then(response => {
          this.labRoomsData = response.data;
          // Update lab room options from the API data
          this.labRooms = this.labRoomsData.map(l => l.name);
          console.log('Loaded lab rooms from API:', this.labRoomsData);
        })
        .catch(error => {
          console.error('Error loading lab rooms:', error);
        });
    },
    loadInstructors() {
      instructorAPI.getAll()
        .then(response => {
          this.instructorsData = response.data;
          // Update instructor options from the API data
          this.instructors = this.instructorsData.map(i => i.full_name);
          console.log('Loaded instructors from API:', this.instructorsData);
        })
        .catch(error => {
          console.error('Error loading instructors:', error);
        });
    },
    // Add this new method to calculate duration in minutes between two time strings
    calculateDurationMinutes(startTime, endTime) {
      if (!startTime || !endTime) {
        return 0;
      }
      
      try {
        const startMinutes = this.convertTimeToMinutes(startTime);
        const endMinutes = this.convertTimeToMinutes(endTime);
        return endMinutes - startMinutes;
      } catch (error) {
        console.error('Error calculating duration:', error);
        return 0;
      }
    },
    
    loadSchedulesFromAPI() {
      console.log('Loading schedules from API...');
      // Get authentication token
      const token = sessionStorage.getItem('token') || localStorage.getItem('token');
      
      // Using 127.0.0.1 instead of localhost for consistency
      axios.get('http://127.0.0.1:8000/api/schedules', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        // Set withCredentials to false to avoid preflight complexity
        withCredentials: false,
        // Add timeout to prevent long waiting when backend is unavailable
        timeout: 5000
      })
        .then(response => {
          console.log('Raw schedules data from API:', response.data);
          
          // Transform API response to our frontend format
          this.allSchedules = response.data.map(schedule => {
            // Make sure we have the convertTimeToMinutes method before calculating duration
            let duration = 0;
            try {
              if (schedule.start_time && schedule.end_time) {
                const startMinutes = this.convertTimeToMinutes(schedule.start_time);
                const endMinutes = this.convertTimeToMinutes(schedule.end_time);
                duration = endMinutes - startMinutes;
              }
            } catch (error) {
              console.error('Error calculating duration:', error);
            }
            
            return {
            id: schedule.id,
              title: `${schedule.course_code || ''} (${schedule.class_type || 'unknown'})`,
              details: `${schedule.course_name || ''}\n${schedule.section || ''}\n${schedule.instructor_name || ''}`,
            semester: this.getSemesterName(schedule.semester_id),
              section: schedule.section || '',
              courseCode: schedule.course_code || '',
              courseName: schedule.course_name || '',
              day: schedule.day || '',
            labRoom: this.getLabRoomName(schedule.lab_room_id),
              instructorName: schedule.instructor_name || '',
              startTime: schedule.start_time || '',
              endTime: schedule.end_time || '',
              duration: duration, // Use the calculated duration
              types: schedule.schedule_types || [],
              schedule_types: schedule.schedule_types || [],
            color: '#DD385A',
              status: schedule.status || 'draft',
              secondDay: schedule.second_day || '',
              class_type: schedule.class_type || ''
            };
          });
          
          console.log('Processed schedules for UI:', this.allSchedules.length);
          
          // Apply initial filtering based on selected semester
          this.filterSchedulesBySemester();
        })
        .catch(error => {
          console.error('Error loading schedules from API:', error);
          console.log('Using empty schedules array as fallback');
          this.schedules = [];
          this.allSchedules = [];
          
          // Still try to filter (will result in empty array)
          this.filterSchedulesBySemester();
        });
    },
    getSemesterName(semesterId) {
      // First try to find the semester in semestersData
      const semester = this.semestersData.find(s => s.id === semesterId);
      if (semester) {
        return semester.name;
      }
      
      // Fallback for common semester IDs
      const semesterMap = {
        1: '1st Sem 2025-2026',
        2: '2nd Sem 2025-2026',
        3: 'Summer 2026'
      };
      
      return semesterMap[semesterId] || 'Unknown Semester';
    },
    getLabRoomName(labRoomId) {
      const labRoom = this.labRoomsData.find(l => l.id === labRoomId);
      return labRoom ? labRoom.name : 'Unknown Lab';
    },
    // Helper method to get semester ID from name
    getSemesterIdFromName(semesterName) {
      // Find semester ID from semesterData array
      const semesterObj = this.semestersData.find(s => s.name === semesterName);
      if (semesterObj) {
        return semesterObj.id;
      }
      
      // Fallback: try to find by simple name matching
      if (semesterName.includes("1st Sem")) {
        return 1;
      } else if (semesterName.includes("2nd Sem")) {
        return 2;
      } else if (semesterName.includes("Summer")) {
        return 3;
      }
      
      console.warn(`Could not find semester ID for ${semesterName}`);
      return 1; // Default to first semester as fallback
    },
    // Add a new method to get semester mappings
    getSemesterMappings() {
      // Create a mapping object from simple semester names to full semester names
      const mappings = {};
      
      // First check if we have semesterData loaded
      if (this.semestersData && this.semestersData.length > 0) {
        // Use the semester data from the API
        this.semestersData.forEach(sem => {
          if (sem.name.toLowerCase().includes("1st sem")) {
            mappings["1st Sem"] = sem.name;
          } else if (sem.name.toLowerCase().includes("2nd sem")) {
            mappings["2nd Sem"] = sem.name;
          } else if (sem.name.toLowerCase().includes("summer")) {
            mappings["Summer"] = sem.name;
          }
        });
      } else {
        // Fallback to semesterOptions if semestersData is not available
        this.semesterOptions.forEach(sem => {
          if (sem.toLowerCase().includes("1st sem")) {
            mappings["1st Sem"] = sem;
          } else if (sem.toLowerCase().includes("2nd sem")) {
            mappings["2nd Sem"] = sem;
          } else if (sem.toLowerCase().includes("summer")) {
            mappings["Summer"] = sem;
          }
        });
      }
      
      console.log("Semester mappings:", mappings);
      return mappings;
    },
    // Add a method to fetch used courses for a specific semester
    async fetchUsedCourses(semesterId, scheduleId = null) {
      try {
        // Get the semester ID from the name
        const semesterObj = this.semestersData.find(s => s.name === this.newSchedule.semester);
        if (!semesterObj) {
          console.error('Could not find semester ID for:', this.newSchedule.semester);
          return [];
        }

        // Get the current section
        const currentSection = this.showCreateScheduleModal ? this.newSchedule.section : this.editSchedule.section;

        const token = sessionStorage.getItem('token') || localStorage.getItem('token');
        const response = await axios.get(`http://127.0.0.1:8000/api/schedules/used-courses/${semesterObj.id}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          },
          withCredentials: false,
          params: { 
            schedule_id: scheduleId,
            section: currentSection // Add section parameter
          }
        });

        console.log('Used courses response:', response.data);
        return response.data;
      } catch (error) {
        console.error('Error fetching used courses:', error);
        return { used_courses: [], edited_schedule: null };
      }
    },
    async onSemesterChange() {
      console.log('Semester changed to:', this.newSchedule.semester);
      
      // If a semester is selected, fetch the used courses for that semester
      if (this.newSchedule.semester && this.newSchedule.section) { // Only fetch if both semester and section are selected
        try {
          // Get the semester ID from the name
          const semesterObj = this.semestersData.find(s => s.name === this.newSchedule.semester);
          if (!semesterObj) {
            console.error('Could not find semester ID for:', this.newSchedule.semester);
            this.usedCoursesList = [];
            return;
          }
          
          console.log('Fetching used courses for semester:', this.newSchedule.semester, 'with ID:', semesterObj.id);
          const result = await this.fetchUsedCourses(semesterObj.id);
          
          // Update the used courses list, filtering by current section
          this.usedCoursesList = result.used_courses
            .filter(c => c.section === this.newSchedule.section)
            .map(c => c.course_code);
          console.log('Updated used courses list:', this.usedCoursesList);
          
          // Clear the selected course if it's not available for this semester and section
          // We'll do this by checking if it still exists in availableCoursesOffered
          if (this.newSchedule.courseCode) {
            const isStillAvailable = this.availableCoursesOffered.some(c => c.code === this.newSchedule.courseCode);
            if (!isStillAvailable) {
              console.log('Selected course is no longer available for this semester/section, clearing selection');
              this.newSchedule.courseCode = '';
            } else {
              console.log('Selected course is still available for this semester/section');
            }
          }
        } catch (error) {
          console.error('Error in onSemesterChange:', error);
          this.usedCoursesList = [];
        }
      } else {
        // Clear the used courses list if no semester or section is selected
        this.usedCoursesList = [];
      }
    },
    resetNewScheduleForm() {
      this.newSchedule = {
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
        secondDay: ''
      };
    },
    refreshCourseDropdown() {
      console.log('==========================================');
      this.availableCoursesOffered = this.getFilteredCourses();
      console.log('Refreshed course dropdown with', this.availableCoursesOffered.length, 'courses');
      console.log('==========================================');
    },
    // Get semester ID based on semester name
    getSemesterId(semesterName) {
      // First check if we have the semester in our semestersData
      const semesterObj = this.semestersData.find(s => s.name === semesterName);
      if (semesterObj) {
        console.log(`Found semester ID ${semesterObj.id} for name "${semesterName}"`);
        return semesterObj.id;
      }
      
      // Fallback: Check for matching semester by parsing name pattern
      let id = null;
      if (semesterName.includes('1st Sem')) {
        const existing = this.semestersData.find(s => s.name.includes('1st Sem'));
        id = existing ? existing.id : 1;
      } else if (semesterName.includes('2nd Sem')) {
        const existing = this.semestersData.find(s => s.name.includes('2nd Sem'));
        id = existing ? existing.id : 2;
      } else if (semesterName.includes('Summer')) {
        const existing = this.semestersData.find(s => s.name.includes('Summer'));
        id = existing ? existing.id : 3;
      }
      
      console.warn(`Using fallback ID ${id} for semester "${semesterName}"`);
      return id || 1; // Default to 1 if no match found
    },
    refreshEditCourseDropdown() {
      // Similar logic to refreshCourseDropdown but for the edit form
      console.log('Edit mode: Course dropdown focused, refreshing available courses');
      
      // If we have semester and section selected
      if (this.editSchedule.semester && this.editSchedule.section) {
        const selectedSemester = this.editSchedule.semester || this.selectedSchedule.semester;
        
        // Check if we have any courses for this semester
        const hasCoursesForSemester = this.coursesOffered.some(course => 
          course.semester === selectedSemester
        );
        
        // Always update used courses list for this semester/section
        const semesterObj = this.semestersData.find(s => s.name === selectedSemester);
        if (semesterObj) {
          const editingId = this.currentlyEditingSchedule ? this.currentlyEditingSchedule.id : null;
          
          // Use a promise to handle the async operation
          this.fetchUsedCourses(semesterObj.id, editingId).then(result => {
            console.log('Edit mode: Refreshed used courses for dropdown:', result);
            this.usedCoursesList = result.used_courses
              .filter(c => c.section === this.editSchedule.section)
              .map(c => c.course_code);
          }).catch(error => {
            console.error('Error fetching used courses during edit dropdown refresh:', error);
          });
        }
        
        if (!hasCoursesForSemester) {
          console.log('Edit mode: No courses found for semester:', selectedSemester, 'Creating virtual courses');
          // The availableCoursesOffered computed property will handle virtual courses
        }
      }
      
      // Trigger a reactivity update
      this.$forceUpdate();
    },
    // Add new method to check for schedule conflicts
    checkForScheduleConflicts(day, startTime, endTime, labRoom, secondDay = null, scheduleIdToSkip = null) {
      // Only check with approved schedules, not drafts or pending schedules
      const approvedSchedules = this.schedules.filter(schedule => 
        schedule.status === 'approved' && 
        (scheduleIdToSkip === null || schedule.id !== scheduleIdToSkip)
      );
      
      if (approvedSchedules.length === 0) {
        console.log('No approved schedules to check conflicts with');
        return false;
      }
      
      // Convert new schedule times to minutes for comparison
      const newStartMinutes = this.convertTimeToMinutes(startTime);
      const newEndMinutes = this.convertTimeToMinutes(endTime);
      
      console.log('Checking for conflicts:', { day, startTime, endTime, newStartMinutes, newEndMinutes, labRoom, secondDay });
      
      // Check for conflicts with primary day
      const primaryDayConflict = approvedSchedules.some(schedule => {
        // We only care about schedules in the same lab room and on the same day
        const sameLab = schedule.labRoom === labRoom;
        const sameDay = schedule.day === day;
        
        if (!sameLab || !sameDay) {
          return false;
        }
        
        const scheduleStartMinutes = this.convertTimeToMinutes(schedule.startTime);
        const scheduleEndMinutes = this.convertTimeToMinutes(schedule.endTime);
        
        // Check if there's an overlap
        // There's a conflict if:
        // 1. The new schedule starts during an existing schedule, OR
        // 2. The new schedule ends during an existing schedule, OR
        // 3. The new schedule completely contains an existing schedule
        const newStartsDuringExisting = newStartMinutes >= scheduleStartMinutes && newStartMinutes < scheduleEndMinutes;
        const newEndsDuringExisting = newEndMinutes > scheduleStartMinutes && newEndMinutes <= scheduleEndMinutes;
        const newContainsExisting = newStartMinutes <= scheduleStartMinutes && newEndMinutes >= scheduleEndMinutes;
        
        const hasConflict = newStartsDuringExisting || newEndsDuringExisting || newContainsExisting;
        
        if (hasConflict) {
          console.log('Found conflict with schedule:', schedule);
        }
        
        return hasConflict;
      });
      
      // If there's a secondary day, check for conflicts there too
      if (!primaryDayConflict && secondDay) {
        const secondaryDayConflict = approvedSchedules.some(schedule => {
          const sameLab = schedule.labRoom === labRoom;
          const sameDay = schedule.day === secondDay || schedule.secondDay === secondDay;
          
          if (!sameLab || !sameDay) {
            return false;
          }
          
          const scheduleStartMinutes = this.convertTimeToMinutes(schedule.startTime);
          const scheduleEndMinutes = this.convertTimeToMinutes(schedule.endTime);
          
          // Same conflict logic as above
          const newStartsDuringExisting = newStartMinutes >= scheduleStartMinutes && newStartMinutes < scheduleEndMinutes;
          const newEndsDuringExisting = newEndMinutes > scheduleStartMinutes && newEndMinutes <= scheduleEndMinutes;
          const newContainsExisting = newStartMinutes <= scheduleStartMinutes && newEndMinutes >= scheduleEndMinutes;
          
          const hasConflict = newStartsDuringExisting || newEndsDuringExisting || newContainsExisting;
          
          if (hasConflict) {
            console.log('Found conflict with schedule on secondary day:', schedule);
          }
          
          return hasConflict;
        });
        
        return secondaryDayConflict;
      }
      
      return primaryDayConflict;
    },
  },
  computed: {
    isFormValid() {
      return this.newSemester.semester && this.newSemester.schoolYear;
    },
    isScheduleFormValid() {
      return this.scheduleTypes.length > 0 &&
        this.newSchedule.semester &&
        this.newSchedule.section &&
        this.newSchedule.courseCode &&
        this.newSchedule.day &&
        this.newSchedule.labRoom &&
        this.newSchedule.instructorName &&
        this.newSchedule.startHour &&
        this.newSchedule.endHour;
    },
    isEditScheduleFormValid() {
      // Allow partial updates - no need to validate all fields
      // Just check if at least one field has been modified
      return true; // We'll validate specific fields in the updateSchedule method instead
    },
    // Filter out courses that are already in use in any schedule
    availableCoursesOffered() {
      // Start with all courses and apply filters in sequence
      let filteredCourses = [...this.coursesOffered];
      
      // Determine which modal is active and get the relevant semester and section
      let activeSemester = '';
      let activeSection = '';
      
      if (this.showCreateScheduleModal) {
        activeSemester = this.newSchedule.semester;
        activeSection = this.newSchedule.section;
      } else if (this.showEditScheduleModal) {
        activeSemester = this.editSchedule.semester || (this.selectedSchedule ? this.selectedSchedule.semester : '');
        activeSection = this.editSchedule.section || (this.selectedSchedule ? this.selectedSchedule.section : '');
      }
      
      // Add detailed debugging to see what's happening with the filtering
      console.log(`Filtering courses with semester: "${activeSemester}", section: "${activeSection}"`);
      console.log(`Total courses before filtering: ${filteredCourses.length}`);
      
      // Filter by semester type if selected, then update display to match current selection
      if (activeSemester) {
        // Extract semester type (1st Sem, 2nd Sem, Summer) from active semester
        let activeSemesterType = '';
        if (activeSemester.includes('1st Sem')) {
          activeSemesterType = '1st Sem';
        } else if (activeSemester.includes('2nd Sem')) {
          activeSemesterType = '2nd Sem';
        } else if (activeSemester.includes('Summer')) {
          activeSemesterType = 'Summer';
        }
        
        console.log(`Active semester type: "${activeSemesterType}"`);
        
        // Filter courses based on semester type
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
          
          const matches = courseSemesterType === activeSemesterType;
          console.log(`Course ${course.code} semester type "${courseSemesterType}" matches "${activeSemesterType}": ${matches}`);
          return matches;
        });
        
        console.log(`After semester type filter: ${filteredCourses.length} courses remain`);
        
        // Now update the semester display for all filtered courses to match the active semester
        filteredCourses = filteredCourses.map(course => {
          return {
            ...course,
            originalSemester: course.semester, // Keep original semester for reference
            semester: activeSemester, // Update to active semester for display
          };
        });
        
        console.log('Courses with updated semester display:', 
          filteredCourses.map(c => `${c.code} (${c.semester}, original: ${c.originalSemester})`));
      }
      
      // Filter by section if selected
      if (activeSection) {
        filteredCourses = filteredCourses.filter(course => {
          // Include courses that match the section OR don't have a specific section
          const matches = course.section === activeSection || !course.section;
          return matches;
        });
        console.log(`After section filter: ${filteredCourses.length} courses remain`);
      }
      
      // Filter out courses that are already used in schedules for the current semester and section
      if (this.usedCoursesList && this.usedCoursesList.length > 0) {
        const editingCourseCode = this.currentlyEditingSchedule ? this.currentlyEditingSchedule.courseCode : null;
        
        filteredCourses = filteredCourses.filter(course => {
          // If this is the course we're currently editing, always include it
          if (editingCourseCode && course.code === editingCourseCode) {
            return true;
          }
          
          // Filter out courses that are already used in the current section
          const isUsed = this.usedCoursesList.includes(course.code);
          return !isUsed;
        });
        console.log(`After used courses filter: ${filteredCourses.length} courses remain`);
      }
      
      // Log final list of available courses
      console.log('Final available courses:', filteredCourses.map(c => c.code));
      
      return filteredCourses;
    }
  },
  watch: {
    selectedLab(newVal, oldVal) {
      if (newVal !== oldVal) {
        console.log(`Lab room selection changed from ${oldVal} to ${newVal}`);
        // No need to do anything special here as the reactivity will update the view
        // All methods that reference selectedLab will use the new value
      }
    },
    'newSchedule.semester': function(newVal, oldVal) {
      if (newVal !== oldVal) {
        console.log(`==========================================`);
        console.log(`SEMESTER CHANGED from "${oldVal}" to "${newVal}"`);
        console.log(`==========================================`);
        
        // Clear course selection when semester changes
        this.newSchedule.courseCode = '';
        
        // Refresh the course dropdown with the new semester value
        this.$nextTick(() => {
          this.refreshCourseDropdown();
        });
      }
    },
    'newSchedule.section': function(newVal, oldVal) {
      if (newVal !== oldVal) {
        console.log(`==========================================`);
        console.log(`SECTION CHANGED from "${oldVal}" to "${newVal}"`);
        console.log(`==========================================`);
        
        // Clear course selection when section changes
        this.newSchedule.courseCode = '';
        
        // Refresh the course dropdown with the new section value
        this.$nextTick(() => {
          this.refreshCourseDropdown();
        });
      }
    },
    'editSchedule.semester': async function(newVal, oldVal) {
      if (newVal !== oldVal) {
        // Similar action for edit mode
        console.log('Edit mode: Semester changed to:', newVal);
        
        // If a semester is selected, fetch the used courses for that semester
        if (newVal && this.editSchedule.section) {
          const semesterObj = this.semestersData.find(s => s.name === newVal);
          if (semesterObj) {
            const editingId = this.currentlyEditingSchedule ? this.currentlyEditingSchedule.id : null;
            const result = await this.fetchUsedCourses(semesterObj.id, editingId);
            
            // Update the used courses list, filtering by current section
            this.usedCoursesList = result.used_courses
              .filter(c => c.section === this.editSchedule.section)
              .map(c => c.course_code);
            console.log('Edit mode: Updated used courses list:', this.usedCoursesList);
          }
        } else {
          // Clear the used courses list if no semester or section is selected
          this.usedCoursesList = [];
        }
      }
    },
    'editSchedule.section': async function(newVal, oldVal) {
      if (newVal !== oldVal && this.editSchedule.semester) {
        const semesterObj = this.semestersData.find(s => s.name === this.editSchedule.semester);
        if (semesterObj) {
          const editingId = this.currentlyEditingSchedule ? this.currentlyEditingSchedule.id : null;
          const result = await this.fetchUsedCourses(semesterObj.id, editingId);
          
          // Update the used courses list, filtering by current section
          this.usedCoursesList = result.used_courses
            .filter(c => c.section === newVal)
            .map(c => c.course_code);
          console.log('Edit mode: Updated used courses list after section change:', this.usedCoursesList);
        }
      }
    }
  },
  mounted() {
    console.log('Schedule Management component mounted');
    
    // Fetch semesters from the API
    this.fetchSemesters();
    
    // Fetch lab rooms from the API
    this.fetchLabRooms();
    
    // Fetch instructors from the API
    this.fetchInstructors();
    
    // Fetch course offerings from the database
    this.fetchCourseOfferings();
    
    // Then load schedules and generate week days
    this.loadSchedulesFromAPI();
    this.generateWeekDays();
  }
}
</script>

<style scoped>
* {
  font-family: 'Inter', sans-serif;
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
  transition: margin-left 0.3s;
  display: flex;
  flex-direction: column;
  width: calc(100% - 70px);
}

.content-wrapper {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

h1 {
  font-size: 24px;
  color: #e91e63;
  margin: 0;
  font-weight: 500;
}

.header-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.import-excel-wrapper {
  position: relative;
}

.import-excel-btn {
  background-color: #4caf50;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 14px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.import-excel-btn i {
  font-size: 12px;
}

.import-excel-btn:hover {
  background-color: #45a049;
}

.import-instructions {
  margin-bottom: 15px;
}

.import-requirements {
  margin-top: 5px;
  padding-left: 20px;
}

.selected-file {
  margin: 15px 0;
  padding: 10px;
  background-color: #f1f1f1;
  border-radius: 4px;
}

.import-btn {
  background-color: #4caf50;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.import-btn:hover {
  background-color: #45a049;
}

.import-btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.create-schedule-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 8px 16px;
  background-color: #e91e63;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.create-schedule-btn i {
  font-size: 12px;
}

.schedule-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.select-semester, .select-lab-room {
  display: flex;
  align-items: center;
  gap: 10px;
}

.select-semester label, .select-lab-room label {
  white-space: nowrap;
  font-size: 0.9rem;
  color: #333;
  font-weight: 500;
}

.select-wrapper {
  position: relative;
  width: 100%;
}

.select-semester .select-wrapper {
  width: 180px;
}

.select-semester .form-select {
  border: 1px solid #ccc;
  font-size: 14px;
  padding: 6px 10px;
  height: 36px;
  width: 180px;
}

.select-wrapper {
  position: relative;
  width: 100%;
}

.form-select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.9rem;
  color: #333;
  background: white;
  /* Force dropdown to appear at the bottom */
  -webkit-appearance: menulist;
  -moz-appearance: menulist;
  appearance: menulist;
  cursor: pointer;
}

.form-select:focus {
  outline: none;
  border-color: #DD385A;
}

.select-wrapper::after {
  display: none;
}

.lab-navigation {
  display: flex;
  align-items: center;
  padding: 1rem;
  gap: 0.5rem;
  border-bottom: 1px solid #DD385A;
  justify-content: space-between;
}

.nav-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  transition: all 0.2s ease;
}

.nav-btn:hover {
  color: #DD385A;
}

.nav-icon {
  font-size: 1rem;
  font-style: normal;
}

.lab-indicator {
  background: none;
  color: #DD385A;
  font-size: 1.2rem;
  font-weight: 500;
  padding: 0 0.5rem;
  min-width: 80px;
  text-align: center;
}

.week-header {
  display: flex;
  border-bottom: 1px solid #e0e0e0;
}

.time-header {
  width: 80px;
  border-right: 1px solid #e0e0e0;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 15px 10px;
}

.time-label {
  font-weight: 600;
  color: #e91e63;
  font-size: 0.9em;
}

.day-headers {
  display: flex;
  flex: 1;
}

.day-header {
  flex: 1;
  padding: 15px 10px;
  text-align: center;
  border-right: 1px solid #e0e0e0;
  background-color: #e91e63;
}

.day-name {
  font-weight: 600;
  color: #fff;
  font-size: 0.9em;
  margin-bottom: 4px;
}

.day-date {
  font-size: 0.8em;
  color: #fff;
}

.schedule-grid {
  display: flex;
  height: calc(100vh - 450px);
  overflow-y: auto;
  background-color: #fff;
  position: relative;
  max-height: calc((60px * 30) + 50px);
}

.time-column {
  width: 80px;
  border-right: 1px solid #e0e0e0;
  flex-shrink: 0;
}

.schedule-content {
  display: flex;
  flex: 1;
  position: relative;
  min-height: calc(60px * 26);
}

.schedule-content::before {
  display: none;
}

.day-column {
  flex: 1;
  border-right: 1px solid #e0e0e0;
  position: relative;
  min-width: 120px;
  height: 100%;
  z-index: 2;
}

.day-column:last-child {
  border-right: none;
}

.day-slots {
  position: relative;
  height: 100%;
  min-height: calc(60px * 26);
}

.time-slot {
  height: 60px;
  padding: 0;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  position: relative;
  color: #666;
  font-size: 0.85em;
  padding-right: 10px;
  box-sizing: border-box;
}

.time-column .time-slot {
  background-color: #fff;
  z-index: 2;
  padding-right: 10px;
}

.schedule-item {
  position: absolute;
  left: 0;
  right: 0;
  top: 0;
  bottom: 0;
  /* Remove the static background-color from here */
  padding: 8px;
  overflow: hidden;
  z-index: 10;
  color: white;
  box-shadow: none;
  border: none;
  box-sizing: border-box;
  transition: all 0.2s ease;
  cursor: pointer;
  margin: 0;
}

/* Add specific status-based color classes */
.schedule-item.status-draft {
  background-color: #DD385A; /* Red */
}

.schedule-item.status-pending {
  background-color: #FFA500; /* Orange/Yellow */
}

.schedule-item.status-approved {
  background-color: #4CAF50; /* Green */
}

.schedule-item:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  opacity: 0.95;
  transform: scale(1.005);
}

.schedule-content {
  width: 100%;
  height: 100%;
  cursor: pointer;
  user-select: none;
}

.schedule-title {
  font-weight: 600;
  font-size: 0.85em;
  margin-bottom: 4px;
  cursor: pointer;
}

.schedule-time {
  font-size: 0.75em;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 4px;
  font-weight: 500;
  cursor: pointer;
}

.schedule-details {
  font-size: 0.75em;
  color: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  gap: 2px;
  white-space: pre-wrap;
  cursor: pointer;
}

.schedule-grid::-webkit-scrollbar {
  width: 8px;
}

.schedule-grid::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.schedule-grid::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

.schedule-grid::-webkit-scrollbar-thumb:hover {
  background: #555;
}

.schedule-content::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: none;
  pointer-events: none;
  z-index: 1;
}

.time-slot::after {
  display: none;
}

.time-slot {
  border-bottom: 1px solid #e0e0e0;
}

.day-column .time-slot {
  position: relative;
  box-sizing: border-box;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 800px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.modal-header {
  padding: 1.5rem;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  color: #DD385A;
  font-size: 1.25rem;
  font-weight: 500;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #666;
  cursor: pointer;
  padding: 0;
}

.modal-body {
  padding: 1.5rem;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.schedule-type-selector {
  grid-column: 1 / -1;
  display: flex;
  justify-content: flex-start;
  gap: 8px;
  margin-bottom: 20px;
}

.type-btn {
  padding: 8px 24px;
  border: 1px solid #DD385A;
  background: white;
  color: #DD385A;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
  min-width: 80px;
}

.type-btn:hover {
  background: #fff5f7;
}

.type-btn.active {
  background: #DD385A;
  color: white;
}

.left-column {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.right-column {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group {
  margin-bottom: 0;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #666;
  font-size: 0.9rem;
}

.modal-dropdown {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.9rem;
  color: #333;
  background: white;
  /* Force dropdown to appear at the bottom */
  -webkit-appearance: menulist;
  -moz-appearance: menulist;
  appearance: menulist;
  cursor: pointer;
}

.modal-dropdown:focus {
  outline: none;
  border-color: #DD385A;
}

.modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: center;
  gap: 1rem;
}

.cancel-btn, .create-btn {
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-btn {
  background: #ffebee;
  color: #DD385A;
  border: none;
}

.cancel-btn:hover {
  background: #ffdde3;
}

.create-btn {
  background: #DD385A;
  color: white;
  border: none;
  min-width: 120px;
}

.create-btn:hover {
  background: #c4314f;
}

.create-btn:disabled {
  background: #ddd;
  cursor: not-allowed;
}

.time-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.select-wrapper {
  position: relative;
  width: 100%;
}

.form-select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  color: #333;
  background: white;
  /* Force dropdown to appear at the bottom */
  -webkit-appearance: menulist;
  -moz-appearance: menulist;
  appearance: menulist;
  cursor: pointer;
}

.form-select:focus {
  border-color: #DD385A;
  outline: none;
}

.select-wrapper::after {
  display: none;
}

.time-picker {
  display: flex;
  align-items: center;
  gap: 8px;
}

.time-select {
  width: 60px;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.period-select {
  width: 70px;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.file-upload-area {
  border: 2px dashed #ddd;
  border-radius: 8px;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 1.5rem;
}

.file-upload-area:hover {
  border-color: #DD385A;
  background-color: #fff5f7;
}

.upload-icon {
  width: 60px;
  height: 60px;
  background-color: #fff5f7;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1rem;
}

.upload-icon svg {
  color: #DD385A;
  width: 30px;
  height: 30px;
}

.file-format-text {
  color: #666;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

.sample-template {
  text-align: center;
  padding: 1rem 0;
  border-top: 1px solid #eee;
}

.download-sample-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background-color: #fff;
  color: #DD385A;
  border: 1px solid #DD385A;
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
  margin-top: 0.5rem;
}

.download-sample-btn:hover {
  background-color: #fff5f7;
}

.download-sample-btn i {
  font-size: 1rem;
}

.instructor-input {
  width: 100%;
  min-height: 60px;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  resize: vertical;
  font-family: inherit;
}

.instructor-input:focus {
  outline: none;
  border-color: #DD385A;
}

.schedule-actions {
  margin-top: 8px;
  display: flex;
  justify-content: flex-end;
}

.send-for-approval-btn {
  background-color: #4CAF50;
  color: white;
  border: none;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8em;
  cursor: pointer;
  transition: background-color 0.2s;
}

.send-for-approval-btn:hover {
  background-color: #45a049;
}

.edit-btn, .delete-btn {
  padding: 0.85rem 1.5rem;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  min-width: 180px;
  justify-content: center;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.edit-btn {
  background: linear-gradient(to right, #DD385A, #e91e63);
  color: white;
  border: none;
}

.edit-btn:hover {
  background: linear-gradient(to right, #c4314f, #d81b60);
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(221, 56, 90, 0.3);
}

.delete-btn {
  background: white;
  color: #DD385A;
  border: 2px solid #DD385A;
}

.delete-btn:hover {
  background: #fff5f7;
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(221, 56, 90, 0.2);
}

.edit-btn i, .delete-btn i {
  font-size: 1.1rem;
}

.schedule-info {
  margin-top: 1rem;
  padding: 1.5rem;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: #f8f9fa;
}

.schedule-info p {
  margin: 0.75rem 0;
  font-size: 0.95rem;
  color: #333;
}

.schedule-info p strong {
  color: #DD385A;
  margin-right: 0.5rem;
}

.optional-text {
  color: #666;
  font-size: 0.8em;
  font-weight: normal;
  font-style: italic;
}

.form-select option[value=""] {
  font-style: italic;
  color: #666;
}

.import-note {
  margin-top: 5px;
  font-style: italic;
  color: #666;
  font-size: 0.9rem;
}

.center-navigation {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.navigation-spacer {
  width: 200px;
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
  margin-right: 1rem;
}

.clear-btn:hover {
  background-color: #f57c00;
}

.clear-btn svg {
  margin-right: 4px;
}

.send-approval-btn {
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
  background-color: #2196F3;
  color: white;
  margin-right: 1rem;
}

.send-approval-btn:hover {
  background-color: #1976D2;
}

.send-approval-btn svg {
  margin-right: 4px;
}

.schedule-actions-footer {
  margin-top: 1rem;
  padding: 1rem;
  display: flex;
  justify-content: flex-end;
  background: white;
  border-radius: 0 0 8px 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.send-all-approval-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  background-color: #4CAF50;
  color: white;
  box-shadow: 0 2px 4px rgba(76, 175, 80, 0.2);
}

.send-all-approval-btn:hover {
  background-color: #45a049;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(76, 175, 80, 0.3);
}

.send-all-approval-btn i {
  font-size: 1rem;
}

.clear-courses-btn {
  background-color: #ff5722;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 14px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.clear-courses-btn i {
  font-size: 12px;
}

.clear-courses-btn:hover {
  background-color: #e64a19;
}

/* Add New Instructor Modal Styles */
.instructor-modal {
  max-width: 450px;
  border-radius: 10px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
  overflow: hidden;
}

.instructor-modal-header {
  background-color: #DD385A;
  color: white;
  padding: 15px 20px;
  border-bottom: none;
}

.instructor-modal-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 500;
}

.instructor-modal-body {
  padding: 25px;
  background-color: #f8f9fa;
}

.instructor-input {
  width: 100%;
  padding: 12px 15px 12px 40px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 15px;
  transition: all 0.3s;
  background-color: white;
}

.instructor-input:focus {
  border-color: #DD385A;
  box-shadow: 0 0 0 3px rgba(221, 56, 90, 0.2);
  outline: none;
}

.input-icon {
  position: absolute;
  left: 12px;
  top: 39px;
  color: #888;
}

.instructor-modal-footer {
  padding: 15px 20px;
  background-color: #f8f9fa;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.instructor-cancel-btn {
  background-color: #f1f1f1;
  color: #555;
  border: none;
  padding: 10px 15px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.instructor-cancel-btn:hover {
  background-color: #e1e1e1;
}

.instructor-add-btn {
  background-color: #DD385A;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.instructor-add-btn:hover {
  background-color: #c62e4e;
}

.instructor-add-btn:disabled {
  background-color: #f5a5b5;
  cursor: not-allowed;
}

.instructor-add-btn i {
  font-size: 14px;
}

/* Add style for Font Awesome unicode icons */
.fa-icon {
  display: inline-block;
  font-family: "Font Awesome 5 Free";
  font-weight: 900;
  font-style: normal;
  font-size: 16px;
  margin-right: 8px;
}
</style>
