# HAP-Tool

A command-line tool for managing HarmonyOS Application Packages (HAP files). This tool allows you to pack, unpack, sign, and install HAP files.

## Features
- Pack directories into HAP files
- Sign HAP files using local certificates
- Unpack HAP files for inspection or modification
- Install signed HAP files to connected devices
- Launch installed applications

## Prerequisites
- Python 3.x
- Java (for signing HAP files)
- HDC (HarmonyOS Device Connector) tool in PATH
- Required signing materials (certificates, debug keys, profile)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd HAP-Tool
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy the signing tool from Dev-eco Studio to the root direcotry or download it from gitee
```bash
C:\Program Files\Huawei\DevEco Studio\sdk\default\openharmony\toolchains\lib\hap-sign-tool.jar .
https://gitee.com/openharmony/developtools_hapsigner/blob/master/dist/hap-sign-tool.jar
```

## Usage

### Pack and Sign a HAP
```bash
# Pack a directory into a HAP file and sign it
python src/main.py pack ./source_dir output.hap --sign

# Pack without signing
python src/main.py pack ./source_dir output.hap --no-sign
```

### Unpack a HAP
```bash
# Extract contents of a HAP file to a directory
python src/main.py unpack input.hap ./output_dir
```

### Install to Device
```bash
# Install and launch a signed HAP
python src/main.py install output.hap

# Install with custom bundle and ability names
python src/main.py install output.hap -b com.example.app -a CustomAbility
```

## Debug Mode
Enable debug logging by setting `DEBUG=true` in your `.env` file or use the `--debug` flag:
```bash
python src/main.py --debug pack ./source_dir output.hap --sign
```
