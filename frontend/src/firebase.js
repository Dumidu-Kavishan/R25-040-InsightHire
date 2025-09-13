// Import the functions you need from the SDKs you need
import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';

// Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyBzCoLk3TdLHDWiQjDjfsuK3vR_7Pp_0I4",
  authDomain: "test-36118.firebaseapp.com", 
  projectId: "test-36118",
  storageBucket: "test-36118.appspot.com",
  messagingSenderId: "112669972686836625710",
  appId: "1:112669972686836625710:web:6e0ba04caee8c47783bfc0",
  measurementId: "G-3K2T4SBB0K"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase Authentication and get a reference to the service
export const auth = getAuth(app);

// Initialize Cloud Firestore and get a reference to the service
export const db = getFirestore(app);

export default firebaseConfig;
