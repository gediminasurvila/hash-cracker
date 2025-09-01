# Hash Type Detector & Cracker

A comprehensive web application for identifying hash algorithm types and cracking hashes using John the Ripper. Upload wordlists, detect hash types, and crack passwords with a modern, clean interface.

## Features

- **Hash Type Detection**: Identify 15+ hash algorithms with confidence levels
- **Hash Cracking**: Crack hashes using John the Ripper with custom wordlists
- **Wordlist Upload**: Support for .txt, .dic, .lst wordlist files (up to 100MB)
- **Clean, Modern UI**: Responsive design with smooth animations
- **Real-time Analysis**: Instant results with loading indicators
- **No Data Storage**: Privacy-focused - no hashes or wordlists are stored
- **Error Handling**: Graceful error handling with user-friendly messages
- **Cross-Platform**: Works on Linux, macOS, and Windows

## Supported Hash Types

- MD5 (32 chars)
- SHA-1 (40 chars)
- SHA-224 (56 chars)
- SHA-256 (64 chars)
- SHA-384 (96 chars)
- SHA-512 (128 chars)
- NTLM (32 chars)
- MySQL 3.23 (16 chars)
- MySQL 4.1+ (41 chars, starts with *)
- CRC32 (8 chars)
- RIPEMD-160 (40 chars)
- Whirlpool (128 chars)
- Tiger (48 chars)
- GOST (64 chars)
- Base64 encoded variants

## Installation

### Option 1: Docker (Recommended)

**Prerequisites:**
- Docker and Docker Compose

**Quick Start:**
```bash
# Clone the repository
git clone <repository-url>
cd hash-detector-cracker

# Build and run with Docker Compose
docker-compose up --build
```

**Or run pre-built image:**
```bash
docker run -p 5000:5000 yourusername/hash-detector-cracker:latest
```

### Option 2: Local Installation

**Prerequisites:**
- Python 3.7 or higher
- pip (Python package installer)
- John the Ripper (for hash cracking functionality)

### Setup

1. **Clone or download the project:**
   ```bash
   # If using git
   git clone <repository-url>
   cd hash-type-detector
   
   # Or extract the downloaded files to a directory
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   
   **On Linux/macOS:**
   ```bash
   source venv/bin/activate
   ```
   
   **On Windows:**
   ```bash
   venv\Scripts\activate
   ```

4. **Install John the Ripper (for hash cracking):**
   
   **Ubuntu/Debian:**
   ```bash
   sudo apt-get update
   sudo apt-get install john
   ```
   
   **macOS (with Homebrew):**
   ```bash
   brew install john
   ```
   
   **Windows:**
   Download from https://www.openwall.com/john/
   
   **Note:** Hash detection works without John the Ripper, but cracking requires it.

5. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

6. **Run the application:**
   ```bash
   python app.py
   ```

7. **Open your browser:**
   Navigate to `http://localhost:5000`

### Deactivating the Virtual Environment

When you're done using the app, deactivate the virtual environment:
```bash
deactivate
```

## Usage

### Hash Type Detection
1. Paste or type your hash into the input field
2. Click "Detect Hash Type" button
3. View the detection results with confidence levels
4. For ambiguous cases, multiple possible types are shown

### Hash Cracking
1. Paste or type your hash into the input field
2. Click "Crack Hash" button to reveal cracking options
3. Upload a wordlist file (.txt, .dic, .lst format)
4. Optionally select a specific hash format (or leave as auto-detect)
5. Click "Start Cracking" to begin the process
6. View results showing cracked password or failure reason

### Supported Wordlist Formats
- Plain text files (.txt)
- Dictionary files (.dic)
- List files (.lst)
- Maximum file size: 100MB

## Technical Details

- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Backend**: Python Flask with pattern matching
- **No Authentication**: Open tool, no user accounts needed
- **No Data Persistence**: Hashes are analyzed in memory only

## API Endpoints

### Hash Detection
```bash
curl -X POST http://localhost:5000/api/detect-hash \
  -H "Content-Type: application/json" \
  -d '{"hash": "5d41402abc4b2a76b9719d911017c592"}'
```

### Hash Cracking
```bash
curl -X POST http://localhost:5000/api/crack-hash \
  -F "hash=5d41402abc4b2a76b9719d911017c592" \
  -F "wordlist=@/path/to/wordlist.txt" \
  -F "format=raw-md5"
```

### Check John the Ripper Availability
```bash
curl http://localhost:5000/api/check-john
```

## Development

The application uses:
- Flask for the backend API with file upload support
- John the Ripper for hash cracking via subprocess calls
- Vanilla JavaScript for frontend interactivity
- CSS Grid and Flexbox for responsive layout
- Regular expressions for hash pattern matching
- Temporary file handling for security

### Development Setup
Always use a virtual environment to avoid dependency conflicts:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Project Structure
```
hash-detector-cracker/
├── venv/                 # Virtual environment (not tracked)
├── app.py               # Flask backend
├── index.html           # Main HTML page
├── styles.css           # Styling
├── script.js            # Frontend JavaScript
├── requirements.txt     # Python dependencies
├── Dockerfile           # Docker configuration
├── docker-compose.yml   # Docker Compose configuration
├── .dockerignore        # Docker ignore rules
├── build.sh            # Docker build script
├── deploy.sh           # DockerHub deployment script
├── install.sh          # Local installation script
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## Docker Deployment

### Building the Image
```bash
# Build locally
./build.sh

# Or manually
docker build -t hash-detector-cracker:latest .
```

### Running the Container
```bash
# Using Docker Compose (recommended)
docker-compose up

# Or directly with Docker
docker run -p 5000:5000 hash-detector-cracker:latest
```

### Deploying to DockerHub
```bash
# Deploy to your DockerHub account
./deploy.sh yourusername

# Or manually
docker tag hash-detector-cracker:latest yourusername/hash-detector-cracker:latest
docker push yourusername/hash-detector-cracker:latest
```

## License

Open source - feel free to modify and distribute.