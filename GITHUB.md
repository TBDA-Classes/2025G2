# Git & GitHub Command Reference

A quick reference guide for the most useful Git commands.

---

## 📋 Basic Branch Operations

### View Branches
```bash
git branch                    # List local branches
git branch -a                 # List all branches (local + remote)
```

### Create and Switch Branches
```bash
git switch branch-name        # Switch to an existing branch
git switch -c new-branch      # Create and switch to a new branch
```

### Delete Branches
```bash
# Delete local branch
git branch -d branch-name     # Safe delete (only if merged)
git branch -D branch-name     # Force delete (even if not merged)

# Delete remote branch (on GitHub)
git push origin --delete branch-name
```

**⚠️ Note:** You cannot delete the branch you're currently on. Switch to another branch first.

---

## 🔄 Syncing with Remote

### Pull Changes
```bash
git pull                      # Pull from the current branch's remote
git pull origin main          # Pull from a specific branch on remote
```

### Push Changes
```bash
git push                      # Push to the current branch's remote
git push origin branch-name   # Push to a specific remote branch
git push -u origin branch     # Push and set upstream tracking
```

### Fetch (without merging)
https://longair.net/blog/2009/04/16/git-fetch-and-merge/
```bash
git fetch                     # Download remote changes without merging
git fetch origin              # Fetch from origin remote
```

---

## 💾 Staging & Committing

### Check Status
```bash
git status                    # See what files are modified/staged
```

### Stage Files
```bash
git add filename              # Stage a specific file
git add .                     # Stage all changes in current directory
git add -A                    # Stage all changes in entire repository
```

### Commit
```bash
git commit -m "message"       # Commit with a message
git commit -am "message"      # Stage all tracked files and commit
```

---

## 📊 Viewing History & Changes

### View Commit History
```bash
git log                       # View commit history
git log --oneline             # Compact one-line view
git log --graph --oneline     # Visual graph of branches
git log branch1..branch2      # See commits in branch2 not in branch1
git log myBranch..main        # Example ^
```

### View Changes (Diff)
```bash
git diff                      # See unstaged changes
git diff branch1 branch2      # Compare two branches
git diff branch1..branch2     # Alternative syntax
git diff --stat branch1 branch2  # Summary with file stats
git diff --name-status branch1 branch2  # Just file names and status
```

### Compare Your Branch with Main (Before Merging)
```bash
# See which files have changed
git diff --name-status your-branch origin/main

# See what changed in a specific file
git diff your-branch origin/main -- path/to/file.py

# See changes with stats (lines added/removed per file)
git diff --stat your-branch origin/main
```

### View Reflog (History of HEAD movements)
```bash
git reflog                    # See history of where HEAD has been
git reflog show branch-name   # See reflog for a specific branch
```

---

## ⏮️ Undoing Changes

### Undo Working Directory Changes
```bash
git restore filename          # Discard changes in a file
git restore .                 # Discard all changes in working directory
```

### Unstage Files
```bash
git restore --staged filename # Unstage a file
git reset HEAD filename       # Alternative way to unstage
```

### Reset to Previous State
```bash
git reset --soft HEAD~1       # Undo last commit, keep changes staged
git reset --mixed HEAD~1      # Undo last commit, keep changes unstaged (default)
  git reset --hard HEAD~1       # Undo last commit, discard all changes**
git reset --hard HEAD@{1}     # Reset to previous HEAD position (using reflog)
git reset --hard commit-hash  # Reset to a specific commit
```

**⚠️ Important:** `git reset --hard` only affects your LOCAL repository. Remote/GitHub is not affected.



## 🔐 Authentication

### Using GitHub CLI
```bash
gh auth login                 # Login to GitHub
gh auth logout                # Logout from GitHub
gh auth status                # Check authentication status
```

---

## 💡 Pro Tips

1. **Before pulling:** Always commit or stash your changes first
2. **Use reflog:** If you mess up, `git reflog` can help you recover
3. **Check status:** Run `git status` frequently to know where you are
4. **Branch early:** Create branches for new features to keep main clean
5. **Pull regularly:** Stay updated with remote changes to avoid conflicts
6. **Reset is local:** `git reset --hard` only affects your local repo, not GitHub
