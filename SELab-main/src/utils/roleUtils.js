// Role utility functions for the application

/**
 * Get the appropriate dashboard path based on user role
 * @param {string} role - The user's role
 * @returns {string} The dashboard path for the role
 */
export function getDashboardPathForRole(role) {
  switch (role) {
    case 'System Administrator':
      return '/dashboard-sysad';
    case 'Academic Coordinator':
      return '/dashboard-acad-coor';
    case 'Lab InCharge':
      return '/dashboard-lab';
    case 'Dean':
      return '/dashboard-dean';
    case 'Faculty/Staff':
    case 'Student':
    default:
      return '/schedule-viewer';
  }
}

/**
 * Get the appropriate profile path based on user role
 * @param {string} role - The user's role
 * @returns {string} The user profile path for the role
 */
export function getProfilePathForRole(role) {
  // ... existing code ...
} 