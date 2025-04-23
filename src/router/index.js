// router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import Home from '../views/Home.vue';
import About from '../views/About.vue';
import Features from '../views/Features.vue';
import SignUp from '../views/SignUp.vue';
import Login from '../views/Login.vue';
import ForgotPassword from '../views/ForgotPassword.vue';
import ResetPassword from '../views/ResetPassword.vue';
import DashboardAcadCoor from '../views/Acad Coor/DashboardAcadCoor.vue';
import { getDashboardPathForRole, hasAccessToRoute } from '../utils/roleUtils.js';

const routes = [
  { 
    path: '/', 
    name: 'Home',
    component: Home 
  },
  {
    path: '/about',
    name: 'About',
    component: About
  },
  {
    path: '/features',
    name: 'Features',
    component: Features
  },
  {
    path: '/signup',
    name: 'SignUp',
    component: SignUp
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: ForgotPassword
  },
  {
    path: '/reset-password',
    name: 'ResetPassword',
    component: ResetPassword
  },
  // Academic Coordinator Routes
  {
    path: '/dashboard-acad-coor',
    name: 'DashboardAcadCoor',
    component: DashboardAcadCoor,
    meta: { requiresAuth: true, role: 'Academic Coordinator' }
  },
  {
    path: '/notifications-acad-coor',
    name: 'NotificationsAcadCoor',
    component: () => import('../views/Acad Coor/NotificationsAcadCoor.vue'),
    meta: { requiresAuth: true, role: 'Academic Coordinator' }
  },
  {
    path: '/schedule-acad-coor',
    name: 'ScheduleAcadCoor',
    component: () => import('../views/Acad Coor/ScheduleAcadCoor.vue'),
    meta: { requiresAuth: true, role: 'Academic Coordinator' }
  },
  {
    path: '/schedule-management',
    name: 'ScheduleManagement',
    component: () => import('../views/Acad Coor/ScheduleManagement.vue'),
    meta: { requiresAuth: true, role: 'Academic Coordinator' }
  },
  {
    path: '/user-profile-acad-coor',
    name: 'UserProfileAcadCoor',
    component: () => import('../views/Acad Coor/UserProfileAcadCoor.vue'),
    meta: { requiresAuth: true, role: 'Academic Coordinator' }
  },
  // Viewer Routes
  {
    path: '/dashboard-viewer',
    name: 'DashboardViewer',
    component: () => import('../views/Viewer/DashboardViewer.vue'),
    meta: { requiresAuth: true, role: ['Faculty/Staff', 'Student', 'Dean'] }
  },
  {
    path: '/notifications-viewer',
    name: 'NotificationsViewer',
    component: () => import('../views/Viewer/NotificationsViewer.vue'),
    meta: { requiresAuth: true, role: ['Faculty/Staff', 'Student', 'Dean'] }
  },
  {
    path: '/schedule-viewer',
    name: 'ScheduleViewer',
    component: () => import('../views/Viewer/ScheduleViewer.vue'),
    meta: { requiresAuth: true, role: ['Faculty/Staff', 'Student', 'Dean'] }
  },
  {
    path: '/user-profile-viewer',
    name: 'UserProfileViewer',
    component: () => import('../views/Viewer/UserProfileViewer.vue'),
    meta: { requiresAuth: true, role: ['Faculty/Staff', 'Student', 'Dean'] }
  },
  // System Administrator Routes
  {
    path: '/dashboard-sysad',
    name: 'DashboardSysAd',
    component: () => import('../views/System Admin/DashboardSysAd.vue'),
    meta: { requiresAuth: true, role: 'System Administrator' }
  },
  {
    path: '/notifications-sysad',
    name: 'NotificationsSysAd',
    component: () => import('../views/System Admin/NotificationsSysAd.vue'),
    meta: { requiresAuth: true, role: 'System Administrator' }
  },
  {
    path: '/all-schedules-sysad',
    name: 'AllSchedulesSysAd',
    component: () => import('../views/Dean/AllSchedSysAd.vue'),
    meta: { requiresAuth: true, role: 'System Administrator' }
  },
  {
    path: '/schedule-sysad',
    name: 'ScheduleSysAd',
    component: () => import('../views/System Admin/ScheduleSysAd.vue'),
    meta: { requiresAuth: true, role: 'System Administrator' }
  },
  {
    path: '/user-management-sysad',
    name: 'UserManagementSysAd',
    component: () => import('../views/System Admin/UserManagement.vue'),
    meta: { requiresAuth: true, role: 'System Administrator' }
  },
  {
    path: '/account-management-sysad',
    name: 'AccountManagementSysAd',
    component: () => import('../views/System Admin/AccountManagement.vue'),
    meta: { requiresAuth: true, role: 'System Administrator' }
  },
  {
    path: '/user-profile-sysad',
    name: 'UserProfileSysAd',
    component: () => import('../views/System Admin/UserProfileSysAd.vue'),
    meta: { requiresAuth: true, role: 'System Administrator' }
  },

  // Lab InCharge
  {
    path: '/dashboard-lab',
    name: 'DashboardLab',
    component: () => import('../views/Lab InCharge/DashboardLab.vue'),
    meta: { requiresAuth: true, role: 'Lab InCharge' }
  },
  {
    path: '/notifications-lab',
    name: 'NotificationsLab',
    component: () => import('../views/Lab InCharge/NotificationLab.vue'),
    meta: { requiresAuth: true, role: 'Lab InCharge' }
  },
  {
    path: '/calendar-lab',
    name: 'CalendarLab',
    component: () => import('../views/Lab InCharge/CalendarLab.vue'),
    meta: { requiresAuth: true, role: 'Lab InCharge' }
  },
  {
    path: '/user-profile-lab',
    name: 'UserProfileLab',
    component: () => import('../views/Lab InCharge/UserProfileLab.vue'),
    meta: { requiresAuth: true, role: 'Lab InCharge' }
  },
  // Dean Routes
  {
    path: '/dashboard-dean',
    name: 'DashboardDean',
    component: () => import('../views/Dean/DashboardDean.vue'),
    meta: { requiresAuth: true, role: 'Dean' }
  },
  {
    path: '/notifications-dean',
    name: 'NotificationsDean',
    component: () => import('../views/Dean/NotificationsDean.vue'),
    meta: { requiresAuth: true, role: 'Dean' }
  },
  {
    path: '/schedule-dean',
    name: 'ScheduleDean',
    component: () => import('../views/Dean/ScheduleDean.vue'),
    meta: { requiresAuth: true, role: 'Dean' }
  },
  {
    path: '/user-profile-dean',
    name: 'UserProfileDean',
    component: () => import('../views/Dean/UserProfileDean.vue'),
    meta: { requiresAuth: true, role: 'Dean' }
  },
  {
    path: '/all-schedules-dean',
    name: 'AllSchedulesDean',
    component: () => import('../views/Dean/AllSchedSysAd.vue'),
    meta: { requiresAuth: true, role: 'Dean' }
  },
  // Redirect for any unmatched routes
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
];

const router = createRouter({ 
  history: createWebHistory(), 
  routes 
});

// Navigation guards
router.beforeEach(async (to, from, next) => {
  // Check if the route requires authentication
  if (to.matched.some(record => record.meta.requiresAuth)) {
    // Get the token and user data
    const token = sessionStorage.getItem('token') || localStorage.getItem('token');
    const userDataStr = sessionStorage.getItem('user') || localStorage.getItem('user');
    
    // If no token or user data, redirect to login
    if (!token || !userDataStr) {
      console.log('No authentication found, redirecting to login');
      next({ path: '/login' });
      return;
    }
    
    try {
      // Parse user data to get the role
      const userData = JSON.parse(userDataStr);
      const userRole = userData.role;
      
      console.log(`Navigation guard: User has role ${userRole}, navigating to ${to.path}`);
      
      // Check for forced logout on navigation - this helps catch role modifications
      // Import required services
      const AuthService = await import('../services/AuthService').then(module => module.default);
      await AuthService.checkForcedLogout();
      
      // Special case for System Admin dashboard - less strict token verification
      if (to.path === '/dashboard-sysad') {
        console.log('Navigating to System Admin dashboard');
        
        // Accept any valid token for System Administrators
        if (userRole === 'System Administrator') {
          console.log('User is a System Administrator, allowing access to dashboard');
          next();
          return;
        } else {
          console.log('Non-admin trying to access System Admin dashboard');
          // Redirect to appropriate dashboard
          const dashboardPath = getDashboardPathForRole(userRole);
          next({ path: dashboardPath });
          return;
        }
      }
      
      // Check if the route has a role requirement and if the user has access
      if (to.meta.role && !hasAccessToRoute(userRole, to)) {
        console.log(`User role (${userRole}) does not match required role for page ${to.path}`);
        
        // Redirect to the appropriate dashboard based on user's role
        const dashboardPath = getDashboardPathForRole(userRole);
        next({ path: dashboardPath });
      } else {
        // User has the right role or no specific role is required, proceed
        next();
      }
    } catch (error) {
      console.error('Error parsing user data in navigation guard:', error);
      // Don't clear storage immediately - it might be a temporary error
      // Just redirect to login and let the login page handle authentication recovery
      next({ path: '/login' });
    }
  } else {
    // Route doesn't require authentication, proceed
    next();
  }
});

export default router;