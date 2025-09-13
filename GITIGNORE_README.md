# GitIgnore Configuration for InsightHire

This document explains the `.gitignore` files configured for the InsightHire project to ensure secure and clean repository management.

## 🚨 CRITICAL SECURITY NOTES

### ⚠️ NEVER COMMIT THESE FILES:
- `serviceAccountKey.json` - Firebase service account keys
- `.env` files - Environment variables and secrets
- `*.key`, `*.pem` - SSL certificates and private keys
- Any files containing API keys or passwords

## 📁 GitIgnore Files Structure

```
InsightHire/
├── .gitignore                 # Main project gitignore
├── backend/.gitignore         # Backend-specific ignores
├── frontend/.gitignore        # Frontend-specific ignores
├── Models/.gitignore          # ML models and datasets
└── GITIGNORE_README.md        # This documentation
```

## 🔧 What's Being Ignored

### 🔐 Security & Sensitive Files
- Firebase service account keys (`serviceAccountKey.json`)
- Environment variables (`.env*`)
- API keys and secrets
- SSL certificates and private keys

### 🐍 Python Backend
- `__pycache__/` directories
- Virtual environments (`venv/`, `InsightHire/`)
- Compiled Python files (`*.pyc`)
- Log files (`*.log`, `server.log`)
- Test and debug files

### ⚛️ React Frontend
- `node_modules/` directory
- Build outputs (`build/`, `dist/`)
- Environment files (`.env*`)
- Cache files (`.cache`, `.eslintcache`)
- Log files

### 🤖 Machine Learning Models
- Model files (`*.h5`, `*.pkl`, `*.weights`)
- Dataset files (`*.csv`, `*.json`)
- Training logs and outputs
- Jupyter notebook checkpoints

### 💻 IDE & OS Files
- VSCode settings (`.vscode/`)
- PyCharm settings (`.idea/`)
- macOS files (`.DS_Store`)
- Windows files (`Thumbs.db`)
- Linux temporary files

## 🚀 Before First Commit

### 1. Remove Already Tracked Sensitive Files
If you've already committed sensitive files, remove them from git history:

```bash
# Remove serviceAccountKey.json from git history
git rm --cached serviceAccountKey.json
git rm --cached backend/serviceAccountKey.json
git rm --cached frontend/serviceAccountKey.json

# Remove any .env files
git rm --cached .env
git rm --cached backend/.env
git rm --cached frontend/.env

# Commit the removal
git commit -m "Remove sensitive files from repository"
```

### 2. Verify GitIgnore is Working
```bash
# Check what files would be committed
git status

# Check if sensitive files are ignored
git check-ignore serviceAccountKey.json
git check-ignore .env
```

## 📋 Recommended Git Workflow

### 1. Environment Setup
Create environment files for different environments:

```bash
# Backend
cp backend/.env.example backend/.env.local

# Frontend  
cp frontend/.env.example frontend/.env.local
```

### 2. Model Files Management
For large model files, consider:
- Using Git LFS (Large File Storage)
- Storing models in cloud storage (AWS S3, Google Cloud Storage)
- Using model versioning tools (MLflow, DVC)

### 3. Documentation
Keep these files in the repository:
- `README.md`
- `requirements.txt`
- `package.json`
- Configuration examples (`.env.example`)

## 🔍 Troubleshooting

### If Sensitive Files Are Still Tracked:
```bash
# Remove from git but keep locally
git rm --cached <filename>

# Add to .gitignore
echo "<filename>" >> .gitignore

# Commit changes
git add .gitignore
git commit -m "Add <filename> to gitignore"
```

### If Build Files Are Being Committed:
```bash
# Remove build directories
git rm -r --cached build/
git rm -r --cached dist/
git rm -r --cached node_modules/

# Update .gitignore if needed
# Commit changes
git add .gitignore
git commit -m "Remove build files and update gitignore"
```

## 📚 Additional Resources

- [Git Ignore Documentation](https://git-scm.com/docs/gitignore)
- [GitHub GitIgnore Templates](https://github.com/github/gitignore)
- [Firebase Security Rules](https://firebase.google.com/docs/rules)
- [Environment Variables Best Practices](https://12factor.net/config)

## ⚡ Quick Commands

```bash
# Check what's being ignored
git status --ignored

# Check specific file
git check-ignore <filename>

# Update gitignore and apply
git add .gitignore
git commit -m "Update gitignore rules"
```

---

**Remember**: Always review what you're committing before pushing to ensure no sensitive information is included!
