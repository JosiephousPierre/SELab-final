const db = require('../config/db');

const authMiddleware = async (req, res, next) => {
  // Get token from header
  const sessionId = req.headers.authorization?.split(' ')[1];
  
  if (!sessionId) {
    return res.status(401).json({ message: 'No token provided, authorization denied' });
  }
  
  try {
    // Verify session exists and is not expired
    const [sessions] = await db.query(
      'SELECT * FROM user_sessions WHERE session_id = ? AND expires_at > NOW()',
      [sessionId]
    );
    
    if (sessions.length === 0) {
      return res.status(401).json({ message: 'Invalid or expired token' });
    }
    
    // Get user info
    const userId = sessions[0].user_id;
    const [users] = await db.query(
      'SELECT id, full_name, email, role FROM users WHERE id = ?',
      [userId]
    );
    
    if (users.length === 0) {
      return res.status(401).json({ message: 'User not found' });
    }
    
    // Attach user to request
    req.user = users[0];
    
    next();
  } catch (error) {
    console.error('Authentication error:', error);
    res.status(500).json({ message: 'Server error' });
  }
};

module.exports = authMiddleware; 