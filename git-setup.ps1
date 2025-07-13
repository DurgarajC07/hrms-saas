# HRMS GitHub Repository Setup and Push Script (PowerShell)

Write-Host "🚀 Setting up HRMS repository for GitHub..." -ForegroundColor Green

# Check if git is installed
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Git is not installed. Please install Git first." -ForegroundColor Red
    exit 1
}

# Initialize git repository if not already initialized
if (-not (Test-Path ".git")) {
    Write-Host "📦 Initializing Git repository..." -ForegroundColor Yellow
    git init
} else {
    Write-Host "✅ Git repository already initialized" -ForegroundColor Green
}

# Configure git user if not set (optional)
$gitName = git config user.name
if (-not $gitName) {
    Write-Host "⚙️  Git user not configured." -ForegroundColor Yellow
    $gitName = Read-Host "Enter your name"
    git config user.name $gitName
}

$gitEmail = git config user.email
if (-not $gitEmail) {
    Write-Host "⚙️  Git email not configured." -ForegroundColor Yellow
    $gitEmail = Read-Host "Enter your email"
    git config user.email $gitEmail
}

# Add all files
Write-Host "📁 Adding files to Git..." -ForegroundColor Yellow
git add .

# Check if there are changes to commit
$stagedChanges = git diff --staged --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "⚠️  No changes to commit" -ForegroundColor Yellow
} else {
    Write-Host "💾 Committing changes..." -ForegroundColor Yellow
    git commit -m "feat: initial HRMS SaaS platform implementation

- Complete employee lifecycle management
- GPS-based attendance tracking with geofencing  
- Comprehensive payroll processing with tax management
- Leave management with approval workflows
- Performance management with 360° reviews
- Benefits administration with open enrollment
- Expense management with receipt handling
- Asset management for IT equipment tracking
- Document management with digital signatures
- Onboarding management with structured workflows
- Compliance management with regulatory tracking
- Real-time reporting and analytics
- Multi-tenant SaaS architecture
- Enterprise security with JWT and RBAC
- Docker containerization support
- Comprehensive API documentation"
}

# Check if remote origin exists
$remoteOrigin = git remote get-url origin 2>$null
if ($remoteOrigin) {
    Write-Host "✅ Remote origin already configured" -ForegroundColor Green
    
    # Ask if user wants to push
    $pushConfirm = Read-Host "🚀 Push to existing repository? (y/n)"
    if ($pushConfirm -eq "y" -or $pushConfirm -eq "Y") {
        Write-Host "📤 Pushing to GitHub..." -ForegroundColor Yellow
        
        # Get current branch name
        $currentBranch = git rev-parse --abbrev-ref HEAD
        
        # Push to remote
        git push -u origin $currentBranch
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Successfully pushed to GitHub!" -ForegroundColor Green
            Write-Host "🌐 Your repository is now available on GitHub" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to push to GitHub. Please check your credentials and try again." -ForegroundColor Red
        }
    }
} else {
    Write-Host "⚙️  Remote origin not configured" -ForegroundColor Yellow
    $repoUrl = Read-Host "🔗 Enter your GitHub repository URL (e.g., https://github.com/username/hrms-saas.git)"
    
    if ($repoUrl) {
        Write-Host "🔗 Adding remote origin..." -ForegroundColor Yellow
        git remote add origin $repoUrl
        
        # Set main as default branch
        git branch -M main
        
        Write-Host "📤 Pushing to GitHub..." -ForegroundColor Yellow
        git push -u origin main
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Successfully pushed to GitHub!" -ForegroundColor Green
            Write-Host "🌐 Your repository is now available at: $repoUrl" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to push to GitHub. Please check your credentials and repository URL." -ForegroundColor Red
            Write-Host "💡 You may need to:" -ForegroundColor Cyan
            Write-Host "   1. Create the repository on GitHub first" -ForegroundColor White
            Write-Host "   2. Set up SSH keys or personal access token" -ForegroundColor White
            Write-Host "   3. Check repository permissions" -ForegroundColor White
        }
    } else {
        Write-Host "⚠️  No repository URL provided. Skipping remote setup." -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. 🌐 Visit your GitHub repository" -ForegroundColor White
Write-Host "2. ⚙️  Set up repository settings (description, topics, etc.)" -ForegroundColor White
Write-Host "3. 📚 Review and update README.md if needed" -ForegroundColor White
Write-Host "4. 🏷️  Create releases for version management" -ForegroundColor White
Write-Host "5. 👥 Add collaborators if working in a team" -ForegroundColor White
Write-Host "6. 🔒 Set up branch protection rules" -ForegroundColor White
Write-Host "7. 🤖 Configure GitHub Actions for CI/CD" -ForegroundColor White
Write-Host ""
Write-Host "✨ Repository Topics to Add:" -ForegroundColor Cyan
Write-Host "   hrms, saas, fastapi, postgresql, redis, docker, python, hr-management," -ForegroundColor White
Write-Host "   payroll, attendance, performance-management, benefits, compliance" -ForegroundColor White
Write-Host ""
Write-Host "🎉 HRMS SaaS is ready for GitHub!" -ForegroundColor Green
