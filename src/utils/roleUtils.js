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
  switch (role) {
    case 'System Administrator':
      return '/user-profile-sysad';
    case 'Academic Coordinator':
      return '/user-profile-acad-coor';
    case 'Lab InCharge':
      return '/user-profile-lab';
    case 'Dean':
      return '/user-profile-dean';
    case 'Faculty/Staff':
    case 'Student':
    default:
      return '/user-profile-viewer';
  }
}

/**
 * Check if a user has access to a specific route based on role
 * @param {string} userRole - The user's role
 * @param {object} route - The route object with meta information
 * @returns {boolean} Whether the user has access
 */
export function hasAccessToRoute(userRole, route) {
  if (!route.meta || !route.meta.role) {
    // No role requirements specified for the route
    return true;
  }

  // Handle routes with a single role or an array of roles
  const requiredRoles = Array.isArray(route.meta.role) 
    ? route.meta.role 
    : [route.meta.role];
  
  return requiredRoles.includes(userRole);
}

/**
 * Update user role in storage and handle redirection
 * @param {object} user - The user object to update
 * @param {string} newRole - The new role to assign
 * @param {object} router - Vue router instance for redirection
 * @returns {boolean} Whether the update was successful
 */
export function updateUserRoleAndRedirect(user, newRole, router) {
  if (!user || !user.id) {
    console.error('Invalid user object');
    return false;
  }

  try {
    // Get the current user data from storage
    const sessionUser = sessionStorage.getItem('user') 
      ? JSON.parse(sessionStorage.getItem('user')) 
      : null;
    
    const localUser = localStorage.getItem('user') 
      ? JSON.parse(localStorage.getItem('user')) 
      : null;
    
    // Check if the user being updated is the current logged-in user
    const isCurrentUser = 
      (sessionUser && sessionUser.id === user.id) || 
      (localUser && localUser.id === user.id);
    
    // Update role in approvedUsers list
    const approvedUsersJSON = localStorage.getItem('approvedUsers');
    if (approvedUsersJSON) {
      try {
        const approvedUsers = JSON.parse(approvedUsersJSON);
        const updatedApprovedUsers = approvedUsers.map(u => {
          if (u.id === user.id || u.email === user.email) {
            return {
              ...u,
              role: newRole,
              permissions: getPermissionsByRole(newRole)
            };
          }
          return u;
        });
        localStorage.setItem('approvedUsers', JSON.stringify(updatedApprovedUsers));
      } catch (error) {
        console.error('Error updating approvedUsers list:', error);
      }
    }
    
    // If this is the current user, update their data in sessionStorage and localStorage
    if (isCurrentUser) {
      if (sessionUser) {
        sessionUser.role = newRole;
        sessionUser.permissions = getPermissionsByRole(newRole);
        sessionStorage.setItem('user', JSON.stringify(sessionUser));
      }
      
      if (localUser) {
        localUser.role = newRole;
        localUser.permissions = getPermissionsByRole(newRole);
        localStorage.setItem('user', JSON.stringify(localUser));
      }
      
      // Redirect to the appropriate dashboard
      const dashboardPath = getDashboardPathForRole(newRole);
      router.push(dashboardPath);
    }
    
    return true;
  } catch (error) {
    console.error('Error updating user role:', error);
    return false;
  }
}

/**
 * Get permissions based on role
 * @param {string} role - The user role
 * @returns {string} The permissions for the role
 */
export function getPermissionsByRole(role) {
  // Map roles to permissions for display purposes
  const permissionsMap = {
    'System Administrator': 'System Management',
    'Academic Coordinator': 'Full Scheduling Control',
    'Lab InCharge': 'Laboratory Booking Management',
    'Dean': 'Approval & Oversight',
    'Faculty/Staff': 'Viewer',
    'Student': 'Viewer'
  };
  
  return permissionsMap[role] || 'Viewer';
} 
