#PowerShell script for git hook for push checks

# Navigate to the root of the Git repository
$repoRoot = (git rev-parse --show-toplevel)
Set-Location -Path $repoRoot

Write-Output "Running pylint with max line length of 120..."

# Run pylint on all Python files, excluding any in venv directories, and capture the output
$pylintOutput = & pylint --max-line-length=120 (Get-ChildItem -Recurse -Filter *.py | Where-Object { $_.FullName -notmatch "\\venv\\" }) 2>&1

# Extract the pylint score from the output
$pylintScore = ($pylintOutput -match "Your code has been rated at" | ForEach-Object { $_ -split " " })[6] -replace "/.*", ""

# Check if the pylint score is above 9
if ([double]$pylintScore -ge 9) {
    Write-Output "Pylint check passed with score: $pylintScore"
} else {
    Write-Output $pylintOutput
    Write-Output "Pylint score is below 9 ($pylintScore). Push will continue, but consider improving code quality."
}

Write-Output "Running unit tests in the tests/ folder..."

# Run unit tests and capture the exit code
python -m unittest discover -s tests -p "*.py"
$testExitCode = $LASTEXITCODE

# Check if unit tests passed
if ($testExitCode -ne 0) {
    Write-Output "Some unit tests failed. Push will continue, but please review test results."
} else {
    Write-Output "All unit tests passed."
}

Write-Output "Checking YAML syntax..."

# Run yamllint on all YAML files and capture any output
$yamlFiles = Get-ChildItem -Recurse -Filter *.yml,*.yaml
$yamlLintOutput = & yamllint $yamlFiles 2>&1
$yamlLintExitCode = $LASTEXITCODE

# Check if yamllint found any issues
if ($yamlLintExitCode -ne 0) {
    Write-Output "YAML syntax errors detected:"
    Write-Output $yamlLintOutput
    exit 1  # Exit with error if YAML syntax check fails
} else {
    Write-Output "All YAML files passed syntax check."
}
