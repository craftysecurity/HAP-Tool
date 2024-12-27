import os
import subprocess
import zipfile
import uuid
import requests
from loguru import logger
from .config import Config

class HapManager:
    TOOL_URL = "https://gitee.com/openharmony/developtools_hapsigner/raw/master/dist/hap-sign-tool.jar"
    TOOL_PATH = "hap-sign-tool.jar"
    
    def __init__(self):
        logger.debug("Initializing HapManager")
        self._ensure_signing_tool()
        
    def _ensure_signing_tool(self):
        if not os.path.exists(self.TOOL_PATH):
            logger.info("Signing tool not found. Downloading...")
            try:
                response = requests.get(self.TOOL_URL, stream=True)
                response.raise_for_status()
                
                with open(self.TOOL_PATH, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                        
                logger.success(f"Successfully downloaded signing tool to {self.TOOL_PATH}")
            except Exception as e:
                logger.error(f"Failed to download signing tool: {str(e)}")
                raise
        else:
            logger.debug("Signing tool already exists")

    def _find_java_path(self):
        try:
            # Try where command on Windows
            result = subprocess.run(
                ["where", "java"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                java_path = result.stdout.splitlines()[0].strip()
                logger.debug(f"Found Java at: {java_path}")
                return java_path
            raise Exception("Java not found using 'where' command")
        except Exception as e:
            logger.error(f"Error finding Java: {str(e)}")
            raise Exception("Java not found in system PATH")

    def pack(self, input_dir: str, output_hap: str, sign: bool = True):
        try:
            logger.debug(f"Packing directory {input_dir} to HAP: {output_hap}")
            
            # Create HAP file
            with zipfile.ZipFile(output_hap, 'w', zipfile.ZIP_DEFLATED) as hap_file:
                for root, _, files in os.walk(input_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, input_dir)
                        logger.debug(f"Adding to HAP: {arcname}")
                        hap_file.write(file_path, arcname)
            
            if sign:
                logger.info("Signing HAP file")
                self._sign_hap(output_hap)
                
            logger.success(f"Successfully created HAP: {output_hap}")
        except Exception as e:
            logger.error(f"Error packing HAP file: {str(e)}")
            raise

    def _sign_hap(self, hap_path: str):
        try:
            java_path = self._find_java_path()
            signed_hap = os.path.abspath("signed.hap")
            input_hap = os.path.abspath(hap_path)
            
            # Create command with working configuration
            cmd = [
                java_path,
                "-jar", os.path.abspath(self.TOOL_PATH),
                "sign-app",
                "-mode", "localSign",
                "-keyAlias", Config.KEY_ALIAS,
                "-keystoreFile", Config.P12_PATH,
                "-keystorePwd", Config.KEY_PASSWORD,
                "-profileFile", Config.PROFILE_PATH,
                "-appCertFile", Config.CERT_PATH,
                "-inFile", input_hap,
                "-outFile", signed_hap,
                "-signAlg", "SHA256withECDSA",
                "-profileSigned", "1",
                "-keyPwd", Config.KEY_PASSWORD,
                "-compatibleVersion", "8",
                "-signCode", "1"
            ]
            
            logger.debug(f"Using keystore: {Config.P12_PATH}")
            logger.debug(f"Using profile: {Config.PROFILE_PATH}")
            logger.debug(f"Using cert: {Config.CERT_PATH}")
            logger.debug(f"Using key alias: {Config.KEY_ALIAS}")
            logger.debug(f"Command: {' '.join(cmd)}")
            
            # Use Popen for better encoding control
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env={
                    **os.environ,
                    'PYTHONIOENCODING': 'utf-8'
                }
            )
            
            # Read output in binary and decode with error handling
            stdout, stderr = process.communicate()
            
            if stdout:
                logger.debug(f"Sign stdout: {stdout.decode('utf-8', errors='ignore')}")
            if stderr:
                logger.debug(f"Sign stderr: {stderr.decode('utf-8', errors='ignore')}")
            
            if process.returncode != 0:
                raise Exception(f"Signing failed: {stderr.decode('utf-8', errors='ignore')}")
            
            # Instead of replacing, keep both files
            if os.path.exists(signed_hap):
                # Copy signed.hap to output.hap as well
                import shutil
                shutil.copy2(signed_hap, hap_path)
                logger.success("HAP file signed successfully")
            else:
                raise Exception("Signed HAP file not created")

        except Exception as e:
            logger.error(f"Error signing HAP file: {str(e)}")
            raise

    def _run_command(self, cmd, desc, shell=False):
        logger.debug(f"Running {desc}: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, shell=shell)
        
        if result.stdout:
            logger.debug(f"{desc} stdout: {result.stdout}")
        if result.stderr:
            logger.debug(f"{desc} stderr: {result.stderr}")
            
        if result.returncode != 0 or "error:" in result.stdout.lower():
            raise Exception(f"{desc} failed: {result.stdout or result.stderr}")
            
        return result.stdout

    def install(self, hap_path: str, bundle_name: str = "com.echochat.hws", ability_name: str = "EntryAbility"):
        try:
            input_hap = os.path.abspath(hap_path)
            if not os.path.exists(input_hap):
                raise Exception(f"HAP file not found: {input_hap}")
            
            logger.debug(f"Installing HAP: {input_hap}")
                
            # Create temporary directory on device
            tmp_dir = f"data/local/tmp/{uuid.uuid4().hex}"
            logger.debug(f"Using remote path: {tmp_dir}")
            
            try:
                # Create directory
                self._run_command(["hdc", "shell", "mkdir", "-p", tmp_dir], "Creating temp directory")
                
                # Send HAP file
                self._run_command(
                    ["hdc", "file", "send", input_hap, tmp_dir], 
                    "Sending HAP to device"
                )
                
                # Get remote file path
                remote_file = f"{tmp_dir}/{os.path.basename(input_hap)}"
                
                # Install HAP
                self._run_command(
                    ["hdc", "shell", f"bm install -p {remote_file}"],
                    "Installing HAP",
                    shell=True
                )
                
                # Launch app
                self._run_command(
                    ["hdc", "shell", f"aa start -a {ability_name} -b {bundle_name}"],
                    "Launching app",
                    shell=True
                )
                
                logger.success("HAP installed and launched successfully")
                
            finally:
                # Cleanup
                self._run_command(
                    ["hdc", "shell", f"rm -rf {tmp_dir}"],
                    "Cleaning up",
                    shell=True
                )
        except Exception as e:
            logger.error(f"Installation failed: {str(e)}")
            raise

    def unpack(self, input_hap: str, output_dir: str):
        try:
            logger.debug(f"Unpacking HAP file: {input_hap} to {output_dir}")
            os.makedirs(output_dir, exist_ok=True)
            
            with zipfile.ZipFile(input_hap, 'r') as hap_file:
                logger.debug(f"HAP contents: {hap_file.namelist()}")
                hap_file.extractall(output_dir)
                
            logger.success(f"Successfully unpacked HAP to {output_dir}")
        except Exception as e:
            logger.error(f"Error unpacking HAP file: {str(e)}")
            raise