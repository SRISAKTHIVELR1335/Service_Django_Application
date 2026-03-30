# NIRIX Diagnostics Android App

React Native mobile application for vehicle diagnostics companion features.

## Project Status

This folder contains the **source code** for the NIRIX Diagnostics Android app. To build the APK, you need to:

1. Create a new React Native project on your local machine
2. Copy this source code into the new project
3. Build using Android Studio or the React Native CLI

## Build Instructions

### Step 1: Create React Native Project

On a machine with Node.js and React Native CLI installed:

```bash
npx react-native init NirixDiagnostics
cd NirixDiagnostics
```

### Step 2: Install Dependencies

```bash
npm install @react-native-async-storage/async-storage @react-navigation/bottom-tabs @react-navigation/native @react-navigation/native-stack axios react-native-safe-area-context react-native-screens react-native-vector-icons
```

### Step 3: Copy Source Files

Copy the `src/` folder from this project into the new React Native project, replacing the default App.js.

### Step 4: Update index.js

Ensure index.js points to the App:
```javascript
import {AppRegistry} from 'react-native';
import App from './src/App';
import {name as appName} from './app.json';

AppRegistry.registerComponent(appName, () => App);
```

### Step 5: Link Native Dependencies

```bash
cd ios && pod install && cd ..  # iOS only
```

### Step 6: Configure API URL

Edit `src/api/config.js` and set `API_BASE_URL` to your deployed backend URL.

### Step 7: Build APK

```bash
# Debug build
npm run android

# Release APK
cd android
./gradlew assembleRelease
```

The APK will be in `android/app/build/outputs/apk/release/`

## Requirements

- Node.js 16+
- React Native CLI
- Android Studio with SDK
- JDK 11+

## Features

- User authentication with JWT tokens
- Vehicle listing and filtering by category
- Test metadata viewing (tests run on Windows client)
- Test execution log history
- Downloads page for client apps and CAN drivers
- Dark/Light theme support
- Automatic update checking

## Source Code Structure

```
src/
├── App.js               # Application entry point
├── api/                  # API client modules
│   ├── config.js         # API configuration
│   ├── client.js         # Axios client with interceptors
│   ├── AuthContext.js    # Authentication context/provider
│   ├── auth.js           # Authentication API
│   ├── vehicles.js       # Vehicles API
│   ├── tests.js          # Tests API
│   ├── versions.js       # Versions API
│   └── logs.js           # Logs API
├── screens/              # Screen components
│   ├── LoginScreen.js
│   ├── RegisterScreen.js
│   ├── DashboardScreen.js
│   ├── VehicleDetailScreen.js
│   ├── TestsScreen.js
│   ├── LogsScreen.js
│   ├── DownloadsScreen.js
│   └── SettingsScreen.js
├── navigation/           # Navigation configuration
│   ├── AppNavigator.js   # Main app tab navigation
│   └── AuthNavigator.js  # Authentication stack
└── theme/                # Theme configuration
    ├── ThemeContext.js   # Theme provider
    └── colors.js         # Light/dark color schemes
```

## Screens Overview

### Login / Register
- User authentication with email and password
- New user registration with admin approval workflow

### Dashboard
- Lists all available vehicles
- Filter by category (Electric, Motorcycle, Scooter, etc.)
- Tap vehicle to view available tests

### Tests
- Browse all diagnostic tests
- Filter by test type (check, read, write)
- View test details (module, function)

### Logs
- View test execution history
- Paginated list with pull-to-refresh

### Downloads
- Links to Windows client and Android APK
- CAN driver download links (PCAN, Kvaser, Vector)

### Settings
- User profile display
- Dark/Light theme toggle
- Logout functionality

## Note

CAN-based diagnostic tests require the Windows client with physical CAN hardware. This Android app serves as a companion for viewing test information, logs, and managing updates.

## License

Proprietary - NIRIX Diagnostics
