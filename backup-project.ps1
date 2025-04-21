# Simple backup script for Text-To-Video-AI project

# Get current date and time in the correct format
$date = Get-Date -Format "yyyy-MM-dd"
$time = Get-Date -Format "HH-mm"

# Set paths
$sourceDir = $PSScriptRoot  # The directory where this script is located
$projectName = Split-Path -Leaf $sourceDir
$backupDir = "D:\live\Documents\GitHub\_versions\$projectName - $date - $time"

# Create backup directory
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

# Define what to exclude
$excludedItems = @("exports", "node_modules", "venv", "__pycache__", "temp", "*.mp4", "*.mp3", "*.wav", "*.pyc")

# Simple copy operation
Get-ChildItem -Path $sourceDir -Recurse -Force | 
    Where-Object { 
        $item = $_
        $exclude = $false
        foreach ($pattern in $excludedItems) {
            if ($pattern.StartsWith("*")) {
                # It's a file extension pattern
                if ($item.Name -like $pattern) {
                    $exclude = $true
                    break
                }
            } else {
                # It's a directory name
                if ($item.FullName.Contains("\$pattern\") -or $item.Name -eq $pattern) {
                    $exclude = $true
                    break
                }
            }
        }
        -not $exclude
    } | 
    ForEach-Object {
        $targetPath = $_.FullName.Replace($sourceDir, $backupDir)
        
        if ($_.PSIsContainer) {
            # It's a directory
            if (!(Test-Path $targetPath)) {
                New-Item -ItemType Directory -Path $targetPath -Force | Out-Null
            }
        } else {
            # It's a file
            $targetDir = Split-Path -Parent $targetPath
            if (!(Test-Path $targetDir)) {
                New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
            }
            Copy-Item -Path $_.FullName -Destination $targetPath -Force
        }
    }

# Output success message
Write-Host "Backup completed successfully!" -ForegroundColor Green
Write-Host "Project backed up to: $backupDir" -ForegroundColor Cyan
