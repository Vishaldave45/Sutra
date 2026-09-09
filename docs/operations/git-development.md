# Git Development & Operational Integrity

This document details the operational root-cause analysis, findings, and development rules regarding Git repository integrity in the Sutra workspace.

---

## 1. Issue Description

At various points during multi-command execution chains, Git returned:
```text
fatal: .git/index: index file smaller than expected
```
Investigation revealed `.git/index` had a file size of `0 bytes`.

---

## 2. Root Cause Analysis

1. **Terminal Sandbox Filesystem Boundary**:
   - The agent's default terminal execution mode operates in a sandbox with restricted permissions where write access to `.git/` can fail with:
     ```text
     fatal: Unable to create '.git/index.lock': Read-only file system
     ```
   - When a command that modifies the index (`git add`, `git commit`, `git reset`) was run sandboxed, followed by or concurrently running with background IDE watchers, partial lock operations or aborted file writes occurred.

2. **External / IDE Git Integrations**:
   - The host system runs GitKraken and VS Code Git extensions (`.git/gk/config` actively updated at `2026-09-09T13:20:01Z`).
   - Frequent automated background operations (`git fetch`, `git status -z -uall`) probe `.git/index`.
   - When any mutating Git command was interrupted or aborted during write-out of a new index, background readers encountered the zero-length or incomplete file before rename completion.

3. **Inappropriate Routine Workaround**:
   - Routine invocation of `rm .git/index && git reset --mixed HEAD` was mistakenly treated as an implementation step instead of an exceptional diagnostic recovery procedure.

---

## 3. Permanent Operational Policies & Workflow

### What NOT to Do
- **NEVER** run `rm .git/index` as a routine implementation step.
- **NEVER** run mutating Git commands (`git add`, `git commit`, `git checkout`) inside an unprivileged/restricted sandbox where `.git/` is read-only.
- **NEVER** chain speculative git commands or run concurrent mutating git operations.

### Safe Git Workflow
1. **Repository Ownership**:
   - The repository and `.git` must always be owned by the user (`vishal-dave:vishal-dave`, mode `775` for directories, `664` for files).
2. **Mutating Git Commands**:
   - Staging (`git add`) and committing (`git commit`) must be run with proper user permissions (`BypassSandbox: true` if invoking through agent commands) to prevent aborted index lock creations.
3. **Sequential Execution**:
   - Always run Git operations sequentially, checking status before staging and verifying after commit.

---

## 4. Emergency Recovery Procedure (If Corruption Occurs)

If and ONLY IF `git status` or `git fsck` reports an invalid or truncated index:
1. Check for running processes:
   ```bash
   ps aux | grep '[g]it'
   ```
2. Remove stale locks if present:
   ```bash
   rm -f .git/index.lock
   ```
3. Rebuild index from HEAD:
   ```bash
   rm .git/index
   git reset --mixed HEAD
   ```
4. Verify repository integrity:
   ```bash
   git fsck --full
   git status
   ```

