#!/bin/bash

# HRMS GitHub Repository Setup and Push Script

echo "🚀 Setting up HRMS repository for GitHub..."

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first."
    exit 1
fi

# Initialize git repository if not already initialized
if [ ! -d ".git" ]; then
    echo "📦 Initializing Git repository..."
    git init
else
    echo "✅ Git repository already initialized"
fi

# Configure git user if not set (optional)
if [ -z "$(git config user.name)" ]; then
    echo "⚙️  Git user not configured. Please set your name:"
    read -p "Enter your name: " git_name
    git config user.name "$git_name"
fi

if [ -z "$(git config user.email)" ]; then
    echo "⚙️  Git email not configured. Please set your email:"
    read -p "Enter your email: " git_email
    git config user.email "$git_email"
fi

# Add all files
echo "📁 Adding files to Git..."
git add .

# Check if there are changes to commit
if git diff --staged --quiet; then
    echo "⚠️  No changes to commit"
else
    echo "💾 Committing changes..."
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
fi

# Check if remote origin exists
if git remote get-url origin &> /dev/null; then
    echo "✅ Remote origin already configured"
    
    # Ask if user wants to push
    read -p "🚀 Push to existing repository? (y/n): " push_confirm
    if [ "$push_confirm" = "y" ] || [ "$push_confirm" = "Y" ]; then
        echo "📤 Pushing to GitHub..."
        
        # Get current branch name
        current_branch=$(git rev-parse --abbrev-ref HEAD)
        
        # Push to remote
        if git push -u origin "$current_branch"; then
            echo "✅ Successfully pushed to GitHub!"
            echo "🌐 Your repository is now available on GitHub"
        else
            echo "❌ Failed to push to GitHub. Please check your credentials and try again."
        fi
    fi
else
    echo "⚙️  Remote origin not configured"
    read -p "🔗 Enter your GitHub repository URL (e.g., https://github.com/username/hrms-saas.git): " repo_url
    
    if [ -n "$repo_url" ]; then
        echo "🔗 Adding remote origin..."
        git remote add origin "$repo_url"
        
        # Set main as default branch
        git branch -M main
        
        echo "📤 Pushing to GitHub..."
        if git push -u origin main; then
            echo "✅ Successfully pushed to GitHub!"
            echo "🌐 Your repository is now available at: $repo_url"
        else
            echo "❌ Failed to push to GitHub. Please check your credentials and repository URL."
            echo "💡 You may need to:"
            echo "   1. Create the repository on GitHub first"
            echo "   2. Set up SSH keys or personal access token"
            echo "   3. Check repository permissions"
        fi
    else
        echo "⚠️  No repository URL provided. Skipping remote setup."
    fi
fi

echo ""
echo "📋 Next Steps:"
echo "1. 🌐 Visit your GitHub repository"
echo "2. ⚙️  Set up repository settings (description, topics, etc.)"
echo "3. 📚 Review and update README.md if needed"
echo "4. 🏷️  Create releases for version management"
echo "5. 👥 Add collaborators if working in a team"
echo "6. 🔒 Set up branch protection rules"
echo "7. 🤖 Configure GitHub Actions for CI/CD"
echo ""
echo "✨ Repository Topics to Add:"
echo "   hrms, saas, fastapi, postgresql, redis, docker, python, hr-management,"
echo "   payroll, attendance, performance-management, benefits, compliance"
echo ""
echo "🎉 HRMS SaaS is ready for GitHub!"
