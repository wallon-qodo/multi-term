# Storage Configuration Guide

## Overview

All data and applications created in Claude Multi-Terminal sessions are now stored in:

```
~/Desktop/multi-claude-sessions/
```

This ensures your work is easily accessible and won't be lost when sessions end.

## Directory Structure

```
~/Desktop/multi-claude-sessions/
├── sessions/                    # Individual session working directories
│   ├── <session-id-1>/         # Session 1 workspace (where apps are created)
│   ├── <session-id-2>/         # Session 2 workspace
│   └── ...
├── history/                     # Session history backups
│   └── <timestamp>_<session-id>.json
└── workspace_state.json         # Current workspace state
```

## Where Your Applications Are Stored

When you create applications in a session, they are stored in:

```
~/Desktop/multi-claude-sessions/sessions/<session-id>/
```

**Each session has its own isolated directory.**

## Best Practices

### 1. **For Persistent Projects**

If you want to keep a project permanently, create it in a dedicated location:

```bash
# Create project in a permanent location
mkdir -p ~/Desktop/multi-claude-sessions/projects/my-app
cd ~/Desktop/multi-claude-sessions/projects/my-app

# Now work on your project - it will persist across sessions
```

### 2. **For Session-Based Work**

The default session directories are great for:
- Exploratory coding
- Temporary experiments
- Research sessions
- Quick prototypes

Each session directory is preserved even after the session ends!

### 3. **Using Git for Version Control**

Always initialize git repositories for important work:

```bash
cd ~/Desktop/multi-claude-sessions/sessions/<session-id>
git init
git add .
git commit -m "Initial commit"

# Optionally push to GitHub/GitLab
git remote add origin <your-repo-url>
git push -u origin main
```

### 4. **Organizing Your Work**

Create a projects folder for long-term work:

```bash
mkdir -p ~/Desktop/multi-claude-sessions/projects
cd ~/Desktop/multi-claude-sessions/projects
```

Then reference this path when creating new applications:
```bash
cd ~/Desktop/multi-claude-sessions/projects/my-new-app
```

## Migration from Old Location

If you have existing work in `~/.claude_multi_terminal/`, you can migrate it:

```bash
# Copy all session data
cp -r ~/.claude_multi_terminal/sessions/* ~/Desktop/multi-claude-sessions/sessions/

# Copy history
cp -r ~/.claude_multi_terminal/history/* ~/Desktop/multi-claude-sessions/history/

# Copy workspace state
cp ~/.claude_multi_terminal/workspace_state.json ~/Desktop/multi-claude-sessions/
```

## Session Directory Mapping

To find which session directory belongs to which session:

1. Look at `~/Desktop/multi-claude-sessions/workspace_state.json`
2. Find your session name
3. Note the `session_id`
4. Your work is in `~/Desktop/multi-claude-sessions/sessions/<session_id>/`

## Backup Your Work

Since everything is in one place, backing up is simple:

```bash
# Backup entire multi-claude-sessions directory
cp -r ~/Desktop/multi-claude-sessions ~/Desktop/multi-claude-sessions-backup

# Or use Time Machine / cloud sync on the folder
```

## Advantages of This Setup

✅ **Easy to Find**: All work in one visible Desktop location
✅ **Persistent**: Session directories remain after sessions end
✅ **Organized**: Clear separation between sessions, history, and state
✅ **Backup-Friendly**: Single directory to backup
✅ **Git-Friendly**: Easy to initialize git repos for projects

## Tips

1. **Name your sessions meaningfully** - Helps identify which session directory to use
2. **Use the projects/ subfolder** - For long-term work
3. **Clean up old sessions** - Periodically remove unused session directories
4. **Backup regularly** - Sync the folder to cloud storage or use Time Machine

## Troubleshooting

### Can't find my application

Check `workspace_state.json` to find the session ID, then look in:
```
~/Desktop/multi-claude-sessions/sessions/<session-id>/
```

### Session directory is empty

Make sure you're creating files in the session's working directory:
```bash
pwd  # Check current directory
cd ~/Desktop/multi-claude-sessions/sessions/<session-id>
```

### Want to move application to permanent location

```bash
# Copy from session to projects
cp -r ~/Desktop/multi-claude-sessions/sessions/<session-id>/my-app \
      ~/Desktop/multi-claude-sessions/projects/my-app
```
