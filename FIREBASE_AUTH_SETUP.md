# Firebase Authentication Setup Guide

## 🔧 Enable Firebase Authentication

To fix the "No auth provider found" error, you need to enable Firebase Authentication in your project:

### Step 1: Go to Firebase Console
1. Open [Firebase Console](https://console.firebase.google.com/)
2. Select your project: **test-36118**

### Step 2: Enable Authentication
1. In the left sidebar, click **"Authentication"**
2. Click **"Get started"** if you haven't set it up yet
3. Go to the **"Sign-in method"** tab
4. Enable **"Email/Password"** authentication:
   - Click on "Email/Password"
   - Toggle **"Enable"** to ON
   - Click **"Save"**

### Step 3: Configure Authorized Domains (Optional)
1. In the **"Sign-in method"** tab, scroll down to **"Authorized domains"**
2. Make sure `localhost` is listed (it should be by default)
3. Add your domain if deploying to production

### Step 4: Test the Application
1. Go back to http://localhost:3000
2. Try registering a new account
3. The authentication should now work!

## 🚀 Alternative: Quick Test Setup

If you want to test immediately without setting up Firebase Auth, you can use the demo mode:

1. The backend will create a temporary user profile
2. Use any email format for testing
3. The system will work in "development mode"

## 🔍 Verification

After enabling Firebase Auth, you should see:
- ✅ No more "CONFIGURATION_NOT_FOUND" errors
- ✅ Successful user registration
- ✅ Working login/logout functionality

## 📧 Test Account Creation

Once Firebase Auth is enabled, try creating an account with:
- **Email:** test@insighthire.com
- **Password:** TestPassword123
- **Display Name:** Test User

The system will create both the Firebase user and the backend user profile automatically.
