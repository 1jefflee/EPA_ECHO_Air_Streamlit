#!/bin/bash
echo "Installing Git hooks..."

# Copy the pre-push hook to the .git/hooks directory
cp git-scripts/git-hooks/pre-push .git/hooks/pre-push
chmod +x .git/hooks/pre-push

echo "Git hooks installed successfully."