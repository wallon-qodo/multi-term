# Claude Multi-Terminal Documentation

Welcome to the documentation for Claude Multi-Terminal!

## 📚 Documentation Index

### For Users

1. **[USER-GUIDE.md](USER-GUIDE.md)** - Complete user guide
   - Comprehensive documentation (30+ pages)
   - Getting started tutorials
   - Modal system explained
   - Best practices
   - Common workflows
   - Advanced features
   - Troubleshooting
   - **Start here if you're new**

2. **[QUICK-REFERENCE.md](QUICK-REFERENCE.md)** - Quick reference card
   - One-page cheat sheet
   - Essential keyboard shortcuts
   - Common patterns
   - Quick troubleshooting
   - **Keep this open while working**

### For Developers

3. **[ARCHITECTURE.md](../ARCHITECTURE.md)** - System architecture (if exists)
4. **[CONTRIBUTING.md](../CONTRIBUTING.md)** - Contribution guidelines (if exists)

## 🚀 Quick Start

### First Time Users

```bash
# 1. Read the quick start section
head -100 USER-GUIDE.md

# 2. Launch the app
cd ~/claude-multi-terminal
source venv/bin/activate
python3 -m claude_multi_terminal

# 3. Keep quick reference handy
cat QUICK-REFERENCE.md
```

### Experienced Users

```bash
# Quick reference for keyboard shortcuts
cat QUICK-REFERENCE.md | grep "KEY"

# Find specific topics in user guide
grep -n "Focus Mode" USER-GUIDE.md
grep -n "Best Practices" USER-GUIDE.md
```

## 📖 What to Read When

### **Just Getting Started?**
→ Read: **USER-GUIDE.md** sections 1-3 (Overview, Getting Started, Modal System)

### **Want to Be Efficient?**
→ Read: **USER-GUIDE.md** section 6 (Best Practices)
→ Keep: **QUICK-REFERENCE.md** open

### **Forgotten a Shortcut?**
→ Check: **QUICK-REFERENCE.md** Essential Keys table

### **Trying Advanced Features?**
→ Read: **USER-GUIDE.md** section 8 (Advanced Features)

### **Something Not Working?**
→ Check: **USER-GUIDE.md** section 11 (Troubleshooting)
→ Or: **QUICK-REFERENCE.md** Troubleshooting section

## 🎯 Learning Path

### Day 1: Basics
```
1. Launch app
2. Learn NORMAL → INSERT → send
3. Try copying text (VISUAL mode)
4. Switch between panes (Tab)
5. Try Focus mode (F11)
```

### Day 2: Workspaces
```
1. Switch workspaces (Ctrl+1-9)
2. Organize by project
3. Practice quick switching
```

### Day 3: Workflows
```
1. Follow a common workflow from USER-GUIDE.md
2. Try parallel development
3. Use Focus mode for concentration
```

### Week 1: Advanced
```
1. Explore session persistence
2. Try smart context features
3. Use knowledge search
4. Optimize token usage
```

## 🔍 Search Tips

### Find in Documentation

```bash
# Search all docs
grep -r "keyword" .

# Search user guide
grep -n "Focus Mode" USER-GUIDE.md

# Find keyboard shortcuts
grep "Ctrl+" QUICK-REFERENCE.md
```

### Find in Code

```bash
# Search Python files
grep -r "class.*App" ../claude_multi_terminal/

# Find specific feature
grep -r "focus_mode" ../claude_multi_terminal/
```

## 💡 Tips

1. **Start Simple**
   - Don't try to learn everything at once
   - Master NORMAL → INSERT → send first
   - Add features gradually

2. **Print Quick Reference**
   - Keep QUICK-REFERENCE.md visible
   - Or print it out
   - Reduces looking up shortcuts

3. **Practice Shortcuts**
   - Muscle memory takes ~3 days
   - Force yourself to use keyboard
   - Mouse is slower (proven)

4. **Read Best Practices**
   - USER-GUIDE.md section 6
   - Based on actual usage patterns
   - Will save you time

## 🆘 Getting Help

### In Order of Speed

1. **Quick Reference** - Fastest
   - Check QUICK-REFERENCE.md
   - Common issues listed

2. **User Guide** - Comprehensive
   - Check troubleshooting section
   - Search for your issue

3. **Knowledge Base** - Past Solutions
   ```bash
   knowledge-assistant search "your issue"
   ```

4. **GitHub Issues** - Community Help
   - Search existing issues
   - Create new issue if needed

## 📝 Documentation Maintenance

### For Contributors

When updating docs:

1. **Keep USER-GUIDE.md comprehensive**
   - Add new features
   - Update troubleshooting
   - Add examples

2. **Keep QUICK-REFERENCE.md concise**
   - Only essential info
   - Must fit on one page
   - Update shortcuts

3. **Keep README.md current**
   - Update file list
   - Maintain links
   - Version numbers

## 🔗 Related Resources

- **Main README:** `../README.md` - Project overview
- **Knowledge System:** `~/.claude/docs/KNOWLEDGE-*.md`
- **Context System:** `~/.claude/docs/SMART-CONTEXT.md`
- **Learning System:** `~/.claude/docs/LEARNING-*.md`

## 📊 Documentation Stats

- **USER-GUIDE.md:** ~30 pages, comprehensive
- **QUICK-REFERENCE.md:** 1 page, essential
- **Total:** ~31 pages of documentation
- **Last Updated:** February 2026

## ✨ What's Next?

After mastering the UI:

1. Explore **Smart Context** system
2. Use **Knowledge Synthesis** for past solutions
3. Try **Codebase Indexing** for faster development
4. Enable **Learning Integration** for continuous improvement

All documented in `~/.claude/docs/`

---

**Happy learning!** 🚀

Questions? Check USER-GUIDE.md or create a GitHub issue.
