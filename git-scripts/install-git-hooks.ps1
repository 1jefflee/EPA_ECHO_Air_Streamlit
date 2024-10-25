# Windows PowerShell script for installing git hooks

Write-Output "Installing Git hooks..."

# Define source and destination paths
$sourceHook = "git-scripts/git-hooks/pre-push.ps1"
$destinationHook = ".git/hooks/pre-push"

# Copy the pre-push hook to the .git/hooks directory
Copy-Item -Path $sourceHook -Destination $destinationHook -Force

# Make the hook executable (on Windows, this just verifies the hook is copied; no chmod equivalent is needed)
if (Test-Path $destinationHook) {
    Write-Output "Git hooks installed successfully."
} else {
    Write-Output "Failed to install Git hooks."
}
