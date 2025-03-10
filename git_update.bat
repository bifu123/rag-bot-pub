@echo off
git add -f .
git rm --cached .env
git commit -m "chat with many peaple"
git push --force origin main
git rm --cached .env
pause
