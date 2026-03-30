# NIRIX Diagnostics Windows Client

Windows desktop application for CAN-based vehicle diagnostics.

## Requirements

- Windows 10 or later
- Python 3.8+ (for development)
- CAN interface hardware (PCAN, Kvaser, or Vector)

## Installation

### For Development

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install CAN driver libraries (based on your hardware):
   - **PCAN**: Download PCANBasic from Peak Systems
   - **Kvaser**: Install canlib from Kvaser
   - **Vector**: Install python-can with Vector support

3. Run the application:
```bash
python -m nirix_win.main
```

### Building the EXE

1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Build the executable:
```bash
pyinstaller pyinstaller.spec
```

3. The executable will be in `dist/Nirix.exe`

## Configuration

Edit `nirix_win/config.py` to set:
- `API_BASE_URL`: Backend server URL
- `APP_VERSION`: Current version number

## Features

- User authentication with JWT tokens
- Vehicle selection and management
- Dynamic test program loading
- CAN bus communication (PCAN, Kvaser, Vector)
- Automatic test bundle updates
- Test execution logging
- Dark/Light theme support

## Project Structure

```
windows-client/
├── nirix_win/
│   ├── main.py              # Application entry point
│   ├── config.py            # Configuration settings
│   ├── ui/                  # User interface screens
│   ├── api_client/          # Backend API clients
│   ├── can_interface/       # CAN hardware drivers
│   ├── tests_runtime/       # Test execution engine
│   └── storage/             # Local storage management
├── Test_Programs/           # Diagnostic test scripts
├── requirements.txt
└── pyinstaller.spec
```

## CAN Driver Setup

### PCAN (Peak Systems)
1. Download and install PCAN drivers from peak-system.com
2. Install PCANBasic Python library
3. Connect PCAN-USB adapter

### Kvaser
1. Download and install Kvaser drivers from kvaser.com
2. Install canlib Python package: `pip install canlib`
3. Connect Kvaser adapter

### Vector
1. Download and install Vector drivers
2. python-can includes Vector support
3. Connect Vector adapter

## License

Proprietary - NIRIX Diagnostics
