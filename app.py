#!/usr/bin/env python3
import re
import json
import os
import subprocess
import tempfile
import time
import logging
import shutil
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.utils import secure_filename

# ------------------ Logging ------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ------------------ Flask Setup ------------------
app = Flask(__name__)
CORS(app)
limiter = Limiter(app=app, key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])

UPLOAD_FOLDER = tempfile.gettempdir()
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
ALLOWED_EXTENSIONS = {'txt', 'dic', 'lst'}
CONFIG_FILE = 'config.json'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# ------------------ Config ------------------
def load_config():
    default_config = {
        "hash_patterns": {
            "MD5": {"pattern": r'^[a-fA-F0-9]{32}$', "description": "MD5 (128-bit)"},
            "SHA-1": {"pattern": r'^[a-fA-F0-9]{40}$', "description": "SHA-1 (160-bit)"},
            "SHA-224": {"pattern": r'^[a-fA-F0-9]{56}$', "description": "SHA-224 (224-bit)"},
            "SHA-256": {"pattern": r'^[a-fA-F0-9]{64}$', "description": "SHA-256 (256-bit)"},
            "SHA-384": {"pattern": r'^[a-fA-F0-9]{96}$', "description": "SHA-384 (384-bit)"},
            "SHA-512": {"pattern": r'^[a-fA-F0-9]{128}$', "description": "SHA-512 (512-bit)"},
            "SHA3-256": {"pattern": r'^[a-fA-F0-9]{64}$', "description": "SHA-3 (256-bit)"},
            "SHA3-512": {"pattern": r'^[a-fA-F0-9]{128}$', "description": "SHA-3 (512-bit)"},
            "Blake2b": {"pattern": r'^[a-fA-F0-9]{128}$', "description": "Blake2b (512-bit)"},
            "NTLM": {"pattern": r'^[a-fA-F0-9]{32}$', "description": "NTLM hash"},
            "MySQL323": {"pattern": r'^[a-fA-F0-9]{16}$', "description": "MySQL 3.23 hash"},
            "MySQL41": {"pattern": r'^\*[a-fA-F0-9]{40}$', "description": "MySQL 4.1+ hash"},
            "CRC32": {"pattern": r'^[a-fA-F0-9]{8}$', "description": "CRC32 checksum"},
            "Adler32": {"pattern": r'^[a-fA-F0-9]{8}$', "description": "Adler-32 checksum"},
            "RIPEMD-160": {"pattern": r'^[a-fA-F0-9]{40}$', "description": "RIPEMD-160 (160-bit)"},
            "Whirlpool": {"pattern": r'^[a-fA-F0-9]{128}$', "description": "Whirlpool (512-bit)"},
            "Tiger": {"pattern": r'^[a-fA-F0-9]{48}$', "description": "Tiger (192-bit)"},
            "GOST": {"pattern": r'^[a-fA-F0-9]{64}$', "description": "GOST R 34.11-94"}
        },
        "base64_patterns": {
            "Base64-MD5": {"pattern": r'^[A-Za-z0-9+/]{22}==$', "description": "Base64 encoded MD5"},
            "Base64-SHA1": {"pattern": r'^[A-Za-z0-9+/]{27}=$', "description": "Base64 encoded SHA-1"},
            "Base64-SHA256": {"pattern": r'^[A-Za-z0-9+/]{43}=$', "description": "Base64 encoded SHA-256"}
        }
    }
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(default_config, f, indent=4)
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load config: {e}. Using default.")
        return default_config

config = load_config()

# ------------------ Hash Detector ------------------
class HashDetector:
    SCORE_MAP = {'High': 3, 'Medium': 2, 'Low': 1}

    def __init__(self):
        self.hash_patterns = config['hash_patterns']
        self.base64_patterns = config['base64_patterns']

    def detect_hash_type(self, hash_string):
        hash_string = hash_string.strip().strip('"')
        original_input = hash_string
        possible_types = []

        for name, info in {**self.hash_patterns, **self.base64_patterns}.items():
            if re.match(info['pattern'], hash_string):
                confidence = self._calculate_confidence(hash_string, name)
                possible_types.append({
                    'algorithm': name,
                    'length': len(hash_string),
                    'confidence': confidence,
                    'description': info['description']
                })

        possible_types.sort(key=lambda x: self.SCORE_MAP.get(x['confidence'], 0), reverse=True)
        return possible_types, original_input

    def _calculate_confidence(self, hash_string, hash_type):
        length = len(hash_string)
        if hash_type in ['MD5', 'NTLM'] and length == 32:
            return 'Medium'
        elif hash_type in ['SHA-1', 'RIPEMD-160'] and length == 40:
            return 'Medium'
        elif hash_type in ['SHA-256', 'SHA3-256', 'GOST'] and length == 64:
            return 'Medium'
        elif hash_type in ['SHA-512', 'SHA3-512', 'Whirlpool', 'Blake2b'] and length == 128:
            return 'Medium'
        elif hash_type in ['CRC32', 'Adler32']:
            return 'Low'
        else:
            return 'High'

# ------------------ Hash Cracker ------------------
class HashCracker:
    def __init__(self):
        self.john_path = shutil.which('john')
        self.hashcat_path = shutil.which('hashcat')
        self.format_map = {
            'MD5': {'john': 'raw-md5', 'hashcat': '0'},
            'SHA-1': {'john': 'raw-sha1', 'hashcat': '100'},
            'SHA-256': {'john': 'raw-sha256', 'hashcat': '1400'},
            'SHA-512': {'john': 'raw-sha512', 'hashcat': '1700'},
            'SHA3-256': {'hashcat': '17800'},
            'SHA3-512': {'hashcat': '17900'},
            'Blake2b': {'hashcat': '600'},
            'NTLM': {'john': 'nt', 'hashcat': '1000'},
            'MySQL323': {'john': 'mysql', 'hashcat': '2'},
            'MySQL41': {'john': 'mysql-sha1', 'hashcat': '300'},
            'RIPEMD-160': {'john': 'raw-ripemd-160', 'hashcat': '6000'},
            'Whirlpool': {'john': 'whirlpool', 'hashcat': '6100'},
            'Tiger': {'john': 'tiger', 'hashcat': '6300'},
            'GOST': {'john': 'raw-gost', 'hashcat': '6900'}
        }

    def is_john_available(self): return self.john_path is not None
    def is_hashcat_available(self): return self.hashcat_path is not None

    def _parse_cracked_output(self, output):
        for line in output.strip().split('\n'):
            if ':' in line and not line.startswith('#'):
                parts = line.split(':', 1)
                if len(parts) == 2:
                    return parts[1].strip()
        return None

    def _crack_with_john(self, hash_string, wordlist, hash_file, hash_format):
        cmd = [self.john_path, f'--wordlist={wordlist}']
        if hash_format and 'john' in self.format_map.get(hash_format, {}):
            cmd.append(f'--format={self.format_map[hash_format]["john"]}')
        cmd.append(hash_file)
        try:
            subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            show_cmd = [self.john_path, '--show', hash_file]
            if hash_format and 'john' in self.format_map.get(hash_format, {}):
                show_cmd.insert(1, f'--format={self.format_map[hash_format]["john"]}')
            show_result = subprocess.run(show_cmd, capture_output=True, text=True, timeout=10)
            password = self._parse_cracked_output(show_result.stdout)
            if password:
                return {'cracked': True, 'password': password, 'hash': hash_string, 'hash_type': hash_format or 'auto', 'tool': 'John'}
            return {'cracked': False, 'message': 'Password not found', 'hash_type': hash_format or 'auto', 'tool': 'John'}
        except subprocess.TimeoutExpired:
            return {'cracked': False, 'error': 'John timeout'}

    def _crack_with_hashcat(self, hash_string, wordlist, hash_file, hash_format):
        # Default to MD5 if no format specified
        if not hash_format:
            hash_format = 'MD5'
        
        if 'hashcat' not in self.format_map.get(hash_format, {}):
            return {'cracked': False, 'error': f'{hash_format} not supported by Hashcat'}
        
        cmd = [self.hashcat_path, '-m', self.format_map[hash_format]['hashcat'], '-a', '0', hash_file, wordlist]
        try:
            logger.info(f"Running hashcat command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            logger.info(f"Hashcat stdout: {result.stdout}")
            logger.info(f"Hashcat stderr: {result.stderr}")
            
            show_cmd = [self.hashcat_path, '--show', '-m', self.format_map[hash_format]['hashcat'], hash_file]
            logger.info(f"Running show command: {' '.join(show_cmd)}")
            show_result = subprocess.run(show_cmd, capture_output=True, text=True, timeout=10)
            logger.info(f"Show stdout: {show_result.stdout}")
            
            password = self._parse_cracked_output(show_result.stdout)
            if password:
                return {'cracked': True, 'password': password, 'hash': hash_string, 'hash_type': hash_format, 'tool': 'Hashcat'}
            return {'cracked': False, 'message': 'Password not found', 'hash_type': hash_format or 'auto', 'tool': 'Hashcat'}
        except subprocess.TimeoutExpired:
            return {'cracked': False, 'error': 'Hashcat timeout'}

    def crack_hash(self, hash_string, wordlist_path, hash_format=None):
        hash_file_path = self._write_temp_hash(hash_string)
        try:
            # Fallback: Hashcat → John
            if self.is_hashcat_available():
                result = self._crack_with_hashcat(hash_string, wordlist_path, hash_file_path, hash_format)
                if result.get('cracked'): 
                    return result
                logger.info("Hashcat failed, trying John...")
            if self.is_john_available():
                result = self._crack_with_john(hash_string, wordlist_path, hash_file_path, hash_format)
                if result.get('cracked'): 
                    return result
            return {'cracked': False, 'message': 'Password not found with Hashcat or John', 'hash_type': hash_format or 'auto', 'tool': 'Hashcat→John'}
        finally:
            try:
                os.unlink(hash_file_path)
            except:
                pass

    def _write_temp_hash(self, hash_string):
        tmp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.hash', delete=False)
        tmp_file.write(hash_string + '\n')  # Add newline for proper parsing
        tmp_file.close()
        return tmp_file.name

# ------------------ Utilities ------------------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ------------------ Initialize ------------------
detector = HashDetector()
cracker = HashCracker()

# ------------------ Routes ------------------
@app.route('/')
def index(): return send_from_directory('.', 'index.html')
@app.route('/<path:filename>')
def serve_static(filename): return send_from_directory('.', filename)

@app.route('/api/detect-hash', methods=['POST'])
@limiter.limit("10 per minute")
def detect_hash():
    try:
        data = request.get_json()
        if not data or 'hash' not in data: return jsonify({'error': 'No hash provided'}), 400
        hash_string = data['hash'].strip()
        if not hash_string: return jsonify({'error': 'Empty hash'}), 400
        types, original = detector.detect_hash_type(hash_string)
        return jsonify({'possible_types': types, 'input_length': len(hash_string), 'original_input': original})
    except Exception as e:
        logger.error(f"Detection error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/crack-hash', methods=['POST'])
@limiter.limit("5 per minute")
def crack_hash():
    try:
        hash_string = request.form.get('hash', '').strip()
        hash_format = request.form.get('format', '').strip()
        if not hash_string: return jsonify({'error': 'No hash provided'}), 400
        if 'wordlist' not in request.files: return jsonify({'error': 'No wordlist uploaded'}), 400
        file = request.files['wordlist']
        if file.filename == '': return jsonify({'error': 'No wordlist selected'}), 400
        if not allowed_file(file.filename): return jsonify({'error': 'Invalid file type'}), 400

        filename = secure_filename(file.filename)
        wordlist_path = os.path.join(app.config['UPLOAD_FOLDER'], f"wordlist_{int(time.time())}_{filename}")
        file.save(wordlist_path)
        try:
            result = cracker.crack_hash(hash_string, wordlist_path, hash_format or None)
            return jsonify(result)
        finally:
            try: os.unlink(wordlist_path)
            except: pass
    except Exception as e:
        logger.error(f"Cracking error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/check-tools', methods=['GET'])
@limiter.limit("10 per minute")
def check_tools():
    return jsonify({
        'john_available': cracker.is_john_available(),
        'john_path': cracker.john_path,
        'hashcat_available': cracker.is_hashcat_available(),
        'hashcat_path': cracker.hashcat_path
    })

# ------------------ Run ------------------
if __name__ == '__main__':
    logger.info("Starting Enhanced Hash Detector & Cracker...")
    logger.info(f"John: {'✓ Found' if cracker.is_john_available() else '⚠ Not found'}")
    logger.info(f"Hashcat: {'✓ Found' if cracker.is_hashcat_available() else '⚠ Not found'}")
    app.run(debug=os.environ.get('FLASK_ENV') == 'development', host='0.0.0.0', port=5000)
