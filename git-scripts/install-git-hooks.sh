#!/bin/bash
echo "Installing Git hooks..."

# Navigate to the root of the Git repository
cd "$(git rev-parse --show-toplevel)" || exit

# Copy the pre-push hook to the .git/hooks directory
cp git-scripts/git-hooks/pre-push .git/hooks/pre-push
chmod +x .git/hooks/pre-push

echo "Git hooks installed successfully."