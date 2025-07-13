#!/usr/bin/env pwsh
# Simple Git Setup Script for HRMS Project
# This script initializes Git repository and prepares for GitHub

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   HRMS Git Repository Setup" -ForegroundColor Cyan  
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Initialize Git repository if not already done
if (-not (Test-Path ".git")) {
    Write-Host "Initializing Git repository..." -ForegroundColor Green
    git init
    Write-Host "Git repository initialized!" -ForegroundColor Green
} else {
    Write-Host "Git repository already exists." -ForegroundColor Yellow
}

# Check if remote origin exists
$remoteOrigin = git remote get-url origin 2>$null
if ($remoteOrigin) {
    Write-Host "Remote origin already configured: $remoteOrigin" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "To connect to GitHub:" -ForegroundColor Cyan
    Write-Host "1. Create a new repository on GitHub.com" -ForegroundColor White
    Write-Host "2. Copy the repository URL" -ForegroundColor White
    Write-Host "3. Run: git remote add origin <repository-url>" -ForegroundColor White
    Write-Host ""
}

# Add all files to staging
Write-Host "Adding files to Git..." -ForegroundColor Green
git add .

# Create initial commit
Write-Host "Creating initial commit..." -ForegroundColor Green
git commit -m "Initial commit: HRMS SaaS Platform

- Complete FastAPI backend with async support
- PostgreSQL database with comprehensive HR models
- SQLAlchemy ORM with proper relationships
- Authentication and authorization system
- Redis caching integration
- Professional GitHub workflows and documentation
- Docker configuration for development and production
- Comprehensive test coverage setup
- Security scanning and code quality tools

Ready for production deployment!"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   Git Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Create GitHub repository" -ForegroundColor White
Write-Host "2. Set up repository settings" -ForegroundColor White  
Write-Host "3. Add repository documentation" -ForegroundColor White
Write-Host "4. Configure development settings" -ForegroundColor White
Write-Host "5. Set up collaboration features" -ForegroundColor White
Write-Host "6. Set up branch protection rules" -ForegroundColor White
Write-Host ""

if ($remoteOrigin) {
    Write-Host "Ready to push to GitHub:" -ForegroundColor Green
    Write-Host "git push -u origin main" -ForegroundColor Yellow
} else {
    Write-Host "After setting up GitHub repository:" -ForegroundColor Green
    Write-Host "git remote add origin <repository-url>" -ForegroundColor Yellow
    Write-Host "git branch -M main" -ForegroundColor Yellow
    Write-Host "git push -u origin main" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Repository is ready for GitHub!" -ForegroundColor Green
