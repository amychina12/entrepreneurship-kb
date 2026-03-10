#!/bin/bash
# Run this script from inside the repo folder on your Mac.
# It will force-push to your existing entrepreneurship-kb repo,
# replacing the old single index.html with the full open-source project.
#
# Prerequisites:
#   - gh CLI installed (brew install gh) and authenticated (gh auth login)
#   - OR git configured with GitHub credentials
#
# Usage:
#   cd /path/to/this/repo
#   chmod +x PUSH_TO_GITHUB.sh
#   ./PUSH_TO_GITHUB.sh

set -e

echo "=== Entrepreneurship Research Knowledge Base — GitHub Push ==="

# Rename master to main if needed
BRANCH=$(git branch --show-current)
if [ "$BRANCH" = "master" ]; then
  git branch -m master main
  echo "Renamed branch to main"
fi

# Set remote (update USERNAME if different)
REMOTE_URL="https://github.com/amychina12/entrepreneurship-kb.git"
if git remote | grep -q origin; then
  git remote set-url origin "$REMOTE_URL"
else
  git remote add origin "$REMOTE_URL"
fi

# Commit if needed
if ! git log --oneline -1 2>/dev/null; then
  git add -A
  git commit -m "Initial release: full pipeline + 3,511-paper database + interactive web app

Includes:
- PDF extraction scripts and raw extracted data (ETP, JBV, SEJ)
- Standardization codebook (22 functions) and standardized database
- Paper-standardizer skill documentation
- Interactive single-file React web app with BM25 search, analytics, and filtering
- Full pipeline documentation (PROCEDURE.md, FIELD_MAPPING.md)"
fi

echo ""
echo "Ready to push. This will REPLACE the contents of:"
echo "  $REMOTE_URL"
echo ""
read -p "Continue? (y/N) " confirm
if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
  echo "Aborted."
  exit 0
fi

git push -u origin main --force

echo ""
echo "=== Push complete! ==="
echo ""
echo "Next steps:"
echo "  1. Go to https://github.com/amychina12/entrepreneurship-kb/settings/pages"
echo "  2. Under 'Source', select: Deploy from a branch"
echo "  3. Set branch to 'main' and folder to '/ (root)'"
echo "  4. Click Save"
echo "  5. Your site will be live at: https://amychina12.github.io/entrepreneurship-kb/"
echo ""
echo "The app (index.html) loads data.json dynamically."
echo "To update the database later, just replace data.json and push."
