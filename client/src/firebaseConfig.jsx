// Firebase configuration - DISABLED for System Administrator Module
// The System Admin module uses localStorage-based authentication
// Firebase is not required for core functionality

// Lazy initialization to prevent errors
let _app = null;
let _auth = null;
let _db = null;

const getFirebaseConfig = () => {
    if (!_app) {
        try {
            const { initializeApp } = require("firebase/app");
            const { getAuth } = require("firebase/auth");
            const { getFirestore } = require("firebase/firestore");
            
            const apiKey = import.meta.env.VITE_API_KEY || "dummy-key-for-development";
            const authDomain = import.meta.env.VITE_AUTH_DOMAIN || "fusion-dev.firebaseapp.com";
            
            const firebaseConfig = {
                apiKey: apiKey,
                authDomain: authDomain,
                projectId: "fusion-system-admin",
                storageBucket: "fusion-system-admin.firebasestorage.app",
                messagingSenderId: "315737830873",
                appId: "1:315737830873:web:060aac2555855892e9d5c8"
            };
            
            _app = initializeApp(firebaseConfig);
            _auth = getAuth(_app);
            _db = getFirestore(_app);
        } catch (error) {
            console.log('Firebase initialization skipped for development');
            return null;
        }
    }
    return _app;
};

// Export lazy getters instead of direct instances
export const getAuth = () => {
    getFirebaseConfig();
    return _auth;
};

export const getDb = () => {
    getFirebaseConfig();
    return _db;
};

// For backward compatibility
export const auth = null;
export const db = null;