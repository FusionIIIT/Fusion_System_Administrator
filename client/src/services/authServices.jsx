import { signInWithEmailAndPassword } from "firebase/auth";
import { auth } from "../firebaseConfig";

// Fusion IIITDMJ compatible email credentials for development
const FUSION_CREDENTIALS = {
  'admin@iiitdmj.ac.in': 'Admin@123',
  'system.admin@iiitdmj.ac.in': 'Admin@123',
  'test.admin@iiitdmj.ac.in': 'Test@123',
  'faculty@iiitdmj.ac.in': 'Faculty@123',
  'student@iiitdmj.ac.in': 'Student@123'
};

export const handleLogin = async (email, password) => {
  try {
    // Try Firebase authentication first (for production)
    const userCredential = await signInWithEmailAndPassword(auth, email, password);
    const user = userCredential.user;
    console.log("User logged in via Firebase:", user);
    return user;
  } catch (error) {
    console.log("Firebase authentication failed or unavailable, checking development credentials");

    // Development mode: Check against Fusion IIITDMJ compatible credentials
    const expectedPassword = FUSION_CREDENTIALS[email];

    if (expectedPassword && password === expectedPassword) {
      // Create mock user object for development
      const mockUser = {
        email: email,
        uid: 'dev-user-' + Date.now(),
        displayName: email.split('@')[0],
        emailVerified: true,
        isAnonymous: false,
        providerData: [{ providerId: 'development' }]
      };

      console.log("User logged in via development credentials:", mockUser);
      return mockUser;
    } else {
      // Invalid credentials
      const errorMessage = `Invalid credentials. Valid development emails:\n${Object.keys(FUSION_CREDENTIALS).map(email => `  • ${email}`).join('\n')}`;
      console.error(errorMessage);
      throw new Error(errorMessage);
    }
  }
};
