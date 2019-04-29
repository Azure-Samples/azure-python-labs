"Installing everything needed for the Calculating Primeness Lab."

# CONSTANTS =======================================================================================
$PYTHON_36_DOWNLOAD_URI = "https://www.python.org/ftp/python/3.6.8/python-3.6.8-embed-amd64.zip"
$PYTHON_36_ZIP_PATH = "$PSScriptRoot\python36.zip"
$PYTHON_36_DIR = "$PSScriptRoot\python36"
$NODE_10_DOWNLOAD_URI = "https://nodejs.org/dist/v10.15.3/node-v10.15.3-x64.msi"
$NODE_10_MSI_PATH = "$PSScriptRoot\node.msi"
# =================================================================================================

# Check if the user is running PowerShell as an Admin. 
# They must be for the script to run properly.
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal(
    [Security.Principal.WindowsIdentity]::GetCurrent()
)
If (!$currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw "You are not running this script as an administrator. Try again with an elevated prompt."
}

# Add the assembly for unpacking zip files.
Add-Type -AssemblyName System.IO.Compression.FileSystem

# PYTHON 3.6 ======================================================================================
# Download and Unzip Python Binaries for Windows to $PYTHON_36_DIR
"Downloading Python 3.6 from $PYTHON_36_DOWNLOAD_URI"
(New-Object System.Net.WebClient).DownloadFile($PYTHON_36_DOWNLOAD_URI, $PYTHON_36_ZIP_PATH)
New-Item -Path $PYTHON_36_DIR -ItemType directory -Force
[System.IO.Compression.ZipFile]::ExtractToDirectory($PYTHON_36_ZIP_PATH, $PYTHON_36_DIR)
# =================================================================================================

# DotNET CORE 2.X =================================================================================
If (!$(dotnet --list-sdks | Out-String) -match "2\..\..") {
    "Installing dotNet Core 2.2.104"
    dotnet-install.ps1 -Version "2.2.104" 
}
# =================================================================================================

# Node.js =========================================================================================
If (!$(node -v | Out-String) -match "[ 1][019]\..") { 
    "Installing Node 10.15.3"
    (New-Object System.Net.WebClient).DownloadFile($NODE_10_DOWNLOAD_URI, $NODE_10_MSI_PATH)
    Start-Process $NODE_10_MSI_PATH -Wait
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" 
    + [System.Environment]::GetEnvironmentVariable("Path", "User") 
}
# =================================================================================================

# Azure Functions Core Tools ======================================================================
If (!$(func -v | Out-String) -match "2\..") {
    "Installing Azure Functions Core Tools."
    npm install -g azure-functions-core-tools 
}
# =================================================================================================
