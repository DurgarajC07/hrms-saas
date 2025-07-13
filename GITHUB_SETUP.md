# GitHub Push Instructions for HRMS SaaS

## 🚀 Quick Setup (For Windows - Laragon Environment)

### Option 1: Using PowerShell Script (Recommended)

```powershell
# Navigate to project directory
cd c:\laragon\www\hrms

# Make PowerShell script executable and run
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\git-setup.ps1
```

### Option 2: Using Git Bash (Linux-style)

```bash
# Navigate to project directory
cd /c/laragon/www/hrms

# Make script executable and run
chmod +x git-setup.sh
./git-setup.sh
```

### Option 3: Manual Git Commands

```bash
# Initialize repository
git init

# Configure git (if not already done)
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Add all files
git add .

# Commit with descriptive message
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

# Add remote repository
git remote add origin https://github.com/yourusername/hrms-saas.git

# Set main branch and push
git branch -M main
git push -u origin main
```

## 📋 Before Pushing to GitHub

### 1. Create GitHub Repository

1. Go to [GitHub](https://github.com)
2. Click "New repository"
3. Repository name: `hrms-saas`
4. Description: `Enterprise HRMS SaaS Platform built with FastAPI`
5. Set to Public or Private as needed
6. **DO NOT** initialize with README, .gitignore, or license (we already have these)
7. Click "Create repository"

### 2. Prepare Your Environment

```bash
# Ensure you're in the project directory
cd c:\laragon\www\hrms

# Check git status
git status

# Verify all files are ready
ls -la
```

### 3. Environment Cleanup

Ensure these files/folders are NOT committed (they're in .gitignore):

- `.env` (contains secrets)
- `venv/` or `env/` (virtual environment)
- `__pycache__/` (Python cache)
- `*.log` (log files)
- `.coverage` (test coverage)

## 🔑 Authentication Setup

### Option 1: Personal Access Token (Recommended)

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate new token (classic)
3. Select scopes: `repo`, `workflow`
4. Copy the token
5. Use token as password when git prompts

### Option 2: SSH Keys

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your.email@example.com"

# Add to SSH agent
ssh-add ~/.ssh/id_ed25519

# Copy public key to GitHub
cat ~/.ssh/id_ed25519.pub
# Paste this in GitHub Settings → SSH and GPG keys

# Use SSH URL for remote
git remote set-url origin git@github.com:yourusername/hrms-saas.git
```

## 📊 Repository Configuration

### Recommended Repository Settings

1. **Description**: `Enterprise HRMS SaaS Platform - Complete HR management solution with employee lifecycle, payroll, attendance, performance reviews, and compliance tracking`

2. **Topics** (helps with discovery):

   ```
   hrms, saas, fastapi, postgresql, redis, docker, python,
   hr-management, payroll, attendance, performance-management,
   benefits, compliance, api, rest-api, async, multi-tenant
   ```

3. **Branch Protection Rules**:

   - Require pull request reviews before merging
   - Require status checks to pass before merging
   - Require branches to be up to date before merging
   - Include administrators in restrictions

4. **GitHub Pages** (for documentation):
   - Source: Deploy from a branch
   - Branch: `main`
   - Folder: `/docs`

## 🤖 CI/CD Setup

The repository includes GitHub Actions workflows:

### Automatic Workflows

- **CI/CD Pipeline** (`.github/workflows/ci-cd.yml`)

  - Runs tests on push/PR
  - Security scanning
  - Docker image building
  - Automated deployment

- **Security Audit** (`.github/workflows/security.yml`)
  - Weekly security scans
  - Dependency vulnerability checks

### Required Secrets

Add these in Repository Settings → Secrets and variables → Actions:

```bash
# Docker Hub credentials (for image publishing)
DOCKER_USERNAME=your-docker-username
DOCKER_PASSWORD=your-docker-password

# Slack notifications (optional)
SLACK_WEBHOOK=your-slack-webhook-url

# Database credentials for testing
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost/hrms_test
REDIS_URL=redis://localhost:6379

# JWT secrets for testing
SECRET_KEY=your-test-secret-key
JWT_SECRET_KEY=your-test-jwt-secret
```

## 📱 After Pushing

### 1. Verify Repository

- Check all files are present
- Verify README displays correctly
- Confirm GitHub Actions are running

### 2. Create First Release

```bash
# Tag the initial release
git tag -a v1.0.0 -m "Initial HRMS SaaS platform release"
git push origin v1.0.0
```

### 3. Set Up Project Board (Optional)

1. Go to Projects tab
2. Create new project
3. Add columns: Backlog, In Progress, Review, Done
4. Link to issues and PRs

### 4. Enable Security Features

1. Go to Settings → Security & analysis
2. Enable:
   - Dependency graph
   - Dependabot alerts
   - Dependabot security updates
   - Code scanning alerts

## 🔄 Regular Workflow

### Daily Development

```bash
# Pull latest changes
git pull origin main

# Create feature branch
git checkout -b feature/new-feature

# Make changes, add, commit
git add .
git commit -m "feat: add new feature"

# Push branch
git push origin feature/new-feature

# Create PR on GitHub
```

### Release Process

```bash
# Update version in relevant files
# Update CHANGELOG.md
# Create release tag
git tag -a v1.1.0 -m "Release v1.1.0"
git push origin v1.1.0
```

## 🆘 Troubleshooting

### Common Issues

1. **Permission Denied**

   ```bash
   # Fix SSH permissions
   chmod 600 ~/.ssh/id_ed25519
   chmod 644 ~/.ssh/id_ed25519.pub
   ```

2. **Large Files**

   ```bash
   # If you have large files, use Git LFS
   git lfs track "*.pdf"
   git lfs track "*.zip"
   git add .gitattributes
   ```

3. **Authentication Failed**

   - Use personal access token instead of password
   - Check token permissions
   - Verify repository access rights

4. **Merge Conflicts**
   ```bash
   git pull origin main
   # Resolve conflicts in files
   git add .
   git commit -m "resolve: merge conflicts"
   git push
   ```

## 🎉 Success!

Once pushed successfully, your HRMS SaaS platform will be available at:
`https://github.com/yourusername/hrms-saas`

The repository includes:

- ✅ Complete codebase with all HR modules
- ✅ Comprehensive documentation
- ✅ Docker deployment configuration
- ✅ CI/CD pipelines
- ✅ Security scanning
- ✅ Issue and PR templates
- ✅ Contributing guidelines

Your enterprise HRMS platform is now ready for collaboration and deployment! 🚀
