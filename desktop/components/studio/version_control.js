/**
 * Ainflue Desktop - Version Control System
 * 
 * Git-like version control for creative projects
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

const { EventEmitter } = require('events');
const fs = require('fs').promises;
const path = require('path');
const crypto = require('crypto');

class VersionControl extends EventEmitter {
  constructor() {
    super();
    this.repository = null;
    this.currentBranch = 'main';
    this.uncommittedChanges = new Map();
    this.commits = new Map();
    this.branches = new Map();
    this.tags = new Map();
    this.remotes = new Map();
    this.workingDirectory = null;
    this.repositoryPath = null;
    
    this.initializeBranches();
  }

  /**
   * Initialize repository with default branch
   */
  async initializeRepository(projectPath, projectName) {
    try {
      this.workingDirectory = projectPath;
      this.repositoryPath = path.join(projectPath, '.ainflue');
      
      // Create repository structure
      await fs.mkdir(this.repositoryPath, { recursive: true });
      await fs.mkdir(path.join(this.repositoryPath, 'objects'), { recursive: true });
      await fs.mkdir(path.join(this.repositoryPath, 'refs'), { recursive: true });
      await fs.mkdir(path.join(this.repositoryPath, 'refs', 'heads'), { recursive: true });
      await fs.mkdir(path.join(this.repositoryPath, 'refs', 'tags'), { recursive: true });

      this.repository = {
        name: projectName,
        created: new Date(),
        path: projectPath,
        currentBranch: this.currentBranch,
        head: null
      };

      // Create initial commit
      const initialCommit = await this.createCommit('Initial commit', [], 'system');
      this.repository.head = initialCommit.hash;

      // Save repository metadata
      await this.saveRepositoryMetadata();

      this.emit('repositoryInitialized', this.repository);
      return true;
    } catch (error) {
      this.emit('error', new Error(`Failed to initialize repository: ${error.message}`));
      return false;
    }
  }

  /**
   * Initialize default branches
   */
  initializeBranches() {
    this.branches.set('main', {
      name: 'main',
      created: new Date(),
      lastCommit: null,
      isDefault: true,
      protected: true
    });
  }

  /**
   * Load existing repository
   */
  async loadRepository(projectPath) {
    try {
      this.workingDirectory = projectPath;
      this.repositoryPath = path.join(projectPath, '.ainflue');

      // Check if repository exists
      const metadataPath = path.join(this.repositoryPath, 'metadata.json');
      await fs.access(metadataPath);

      // Load repository metadata
      const metadataContent = await fs.readFile(metadataPath, 'utf8');
      this.repository = JSON.parse(metadataContent);

      // Load commits
      await this.loadCommits();
      
      // Load branches
      await this.loadBranches();

      // Load tags
      await this.loadTags();

      this.emit('repositoryLoaded', this.repository);
      return true;
    } catch (error) {
      this.emit('error', new Error(`Failed to load repository: ${error.message}`));
      return false;
    }
  }

  /**
   * Stage files for commit
   */
  async stageFiles(filePaths) {
    try {
      const stagedFiles = [];

      for (const filePath of filePaths) {
        const fullPath = path.resolve(this.workingDirectory, filePath);
        
        // Check if file exists
        await fs.access(fullPath);
        
        // Calculate file hash
        const content = await fs.readFile(fullPath);
        const hash = this.calculateHash(content);
        
        // Store file object
        await this.storeFileObject(hash, content);
        
        const fileInfo = {
          path: filePath,
          hash,
          size: content.length,
          staged: new Date(),
          status: 'added'
        };

        this.uncommittedChanges.set(filePath, fileInfo);
        stagedFiles.push(fileInfo);
      }

      this.emit('filesStaged', stagedFiles);
      return stagedFiles;
    } catch (error) {
      this.emit('error', new Error(`Failed to stage files: ${error.message}`));
      return [];
    }
  }

  /**
   * Unstage files
   */
  unstageFiles(filePaths) {
    const unstagedFiles = [];

    for (const filePath of filePaths) {
      if (this.uncommittedChanges.has(filePath)) {
        const fileInfo = this.uncommittedChanges.get(filePath);
        this.uncommittedChanges.delete(filePath);
        unstagedFiles.push(fileInfo);
      }
    }

    this.emit('filesUnstaged', unstagedFiles);
    return unstagedFiles;
  }

  /**
   * Create commit
   */
  async createCommit(message, author = 'User', coAuthors = []) {
    try {
      if (this.uncommittedChanges.size === 0) {
        throw new Error('No changes to commit');
      }

      const commitHash = this.generateCommitHash();
      const parentCommits = this.repository.head ? [this.repository.head] : [];
      
      const commit = {
        hash: commitHash,
        message: message.trim(),
        author: {
          name: author,
          timestamp: new Date()
        },
        coAuthors,
        parents: parentCommits,
        branch: this.currentBranch,
        files: Array.from(this.uncommittedChanges.values()),
        tree: this.createTreeFromChanges(),
        stats: this.calculateCommitStats()
      };

      // Store commit
      this.commits.set(commitHash, commit);
      await this.saveCommit(commit);

      // Update branch head
      const branch = this.branches.get(this.currentBranch);
      branch.lastCommit = commitHash;
      this.branches.set(this.currentBranch, branch);

      // Update repository head
      this.repository.head = commitHash;

      // Clear staged changes
      this.uncommittedChanges.clear();

      // Save repository state
      await this.saveRepositoryMetadata();
      await this.saveBranches();

      this.emit('commitCreated', commit);
      return commit;
    } catch (error) {
      this.emit('error', new Error(`Failed to create commit: ${error.message}`));
      return null;
    }
  }

  /**
   * Create branch
   */
  async createBranch(branchName, fromCommit = null) {
    try {
      if (this.branches.has(branchName)) {
        throw new Error(`Branch '${branchName}' already exists`);
      }

      const sourceCommit = fromCommit || this.repository.head;
      if (!sourceCommit) {
        throw new Error('No commits to branch from');
      }

      const branch = {
        name: branchName,
        created: new Date(),
        lastCommit: sourceCommit,
        isDefault: false,
        protected: false,
        description: `Branch created from ${sourceCommit.slice(0, 8)}`
      };

      this.branches.set(branchName, branch);
      await this.saveBranches();

      this.emit('branchCreated', branch);
      return branch;
    } catch (error) {
      this.emit('error', new Error(`Failed to create branch: ${error.message}`));
      return null;
    }
  }

  /**
   * Switch branch
   */
  async switchBranch(branchName) {
    try {
      if (!this.branches.has(branchName)) {
        throw new Error(`Branch '${branchName}' does not exist`);
      }

      if (this.uncommittedChanges.size > 0) {
        throw new Error('Cannot switch branch with uncommitted changes');
      }

      const branch = this.branches.get(branchName);
      this.currentBranch = branchName;
      this.repository.currentBranch = branchName;
      this.repository.head = branch.lastCommit;

      // Checkout files for this branch
      await this.checkoutBranch(branch);

      await this.saveRepositoryMetadata();

      this.emit('branchSwitched', { from: this.currentBranch, to: branchName });
      return true;
    } catch (error) {
      this.emit('error', new Error(`Failed to switch branch: ${error.message}`));
      return false;
    }
  }

  /**
   * Merge branch
   */
  async mergeBranch(sourceBranch, targetBranch = null, message = null) {
    try {
      const target = targetBranch || this.currentBranch;
      
      if (!this.branches.has(sourceBranch) || !this.branches.has(target)) {
        throw new Error('Source or target branch does not exist');
      }

      if (sourceBranch === target) {
        throw new Error('Cannot merge branch into itself');
      }

      const sourceCommit = this.branches.get(sourceBranch).lastCommit;
      const targetCommit = this.branches.get(target).lastCommit;

      // Check for conflicts
      const conflicts = await this.detectMergeConflicts(sourceCommit, targetCommit);
      if (conflicts.length > 0) {
        this.emit('mergeConflicts', conflicts);
        return { success: false, conflicts };
      }

      // Create merge commit
      const mergeMessage = message || `Merge branch '${sourceBranch}' into ${target}`;
      const mergeCommit = await this.createMergeCommit(mergeMessage, sourceCommit, targetCommit);

      // Update target branch
      const targetBranchData = this.branches.get(target);
      targetBranchData.lastCommit = mergeCommit.hash;
      this.branches.set(target, targetBranchData);

      await this.saveBranches();

      this.emit('branchMerged', {
        source: sourceBranch,
        target,
        commit: mergeCommit
      });

      return { success: true, commit: mergeCommit };
    } catch (error) {
      this.emit('error', new Error(`Failed to merge branch: ${error.message}`));
      return { success: false, error: error.message };
    }
  }

  /**
   * Create tag
   */
  async createTag(tagName, message = null, commitHash = null) {
    try {
      if (this.tags.has(tagName)) {
        throw new Error(`Tag '${tagName}' already exists`);
      }

      const targetCommit = commitHash || this.repository.head;
      if (!targetCommit) {
        throw new Error('No commit to tag');
      }

      const tag = {
        name: tagName,
        message: message || `Tag ${tagName}`,
        commit: targetCommit,
        created: new Date(),
        tagger: 'User'
      };

      this.tags.set(tagName, tag);
      await this.saveTags();

      this.emit('tagCreated', tag);
      return tag;
    } catch (error) {
      this.emit('error', new Error(`Failed to create tag: ${error.message}`));
      return null;
    }
  }

  /**
   * Get commit history
   */
  getCommitHistory(limit = 50, branch = null) {
    const targetBranch = branch || this.currentBranch;
    const branchData = this.branches.get(targetBranch);
    
    if (!branchData || !branchData.lastCommit) {
      return [];
    }

    const history = [];
    let currentCommit = this.commits.get(branchData.lastCommit);
    let count = 0;

    while (currentCommit && count < limit) {
      history.push(currentCommit);
      
      // Follow parent chain
      if (currentCommit.parents.length > 0) {
        currentCommit = this.commits.get(currentCommit.parents[0]);
      } else {
        break;
      }
      
      count++;
    }

    return history;
  }

  /**
   * Get file history
   */
  getFileHistory(filePath, limit = 20) {
    const history = [];
    const allCommits = Array.from(this.commits.values())
      .sort((a, b) => new Date(b.author.timestamp) - new Date(a.author.timestamp));

    for (const commit of allCommits) {
      const fileInCommit = commit.files.find(f => f.path === filePath);
      if (fileInCommit) {
        history.push({
          commit: commit.hash,
          message: commit.message,
          author: commit.author,
          file: fileInCommit
        });

        if (history.length >= limit) break;
      }
    }

    return history;
  }

  /**
   * Compare commits
   */
  compareCommits(commit1Hash, commit2Hash) {
    const commit1 = this.commits.get(commit1Hash);
    const commit2 = this.commits.get(commit2Hash);

    if (!commit1 || !commit2) {
      throw new Error('One or both commits not found');
    }

    const changes = {
      added: [],
      modified: [],
      deleted: [],
      moved: []
    };

    // Create file maps
    const files1 = new Map(commit1.files.map(f => [f.path, f]));
    const files2 = new Map(commit2.files.map(f => [f.path, f]));

    // Find added and modified files
    for (const [path, file2] of files2) {
      if (!files1.has(path)) {
        changes.added.push(file2);
      } else {
        const file1 = files1.get(path);
        if (file1.hash !== file2.hash) {
          changes.modified.push({
            path,
            before: file1,
            after: file2
          });
        }
      }
    }

    // Find deleted files
    for (const [path, file1] of files1) {
      if (!files2.has(path)) {
        changes.deleted.push(file1);
      }
    }

    return {
      commit1: commit1Hash,
      commit2: commit2Hash,
      changes,
      stats: {
        filesChanged: changes.added.length + changes.modified.length + changes.deleted.length,
        additions: changes.added.length,
        modifications: changes.modified.length,
        deletions: changes.deleted.length
      }
    };
  }

  /**
   * Revert commit
   */
  async revertCommit(commitHash, message = null) {
    try {
      const commit = this.commits.get(commitHash);
      if (!commit) {
        throw new Error('Commit not found');
      }

      // Create reverse changes
      const reverseChanges = new Map();
      
      for (const file of commit.files) {
        // For a revert, we need to restore the previous version
        const previousVersion = await this.getPreviousFileVersion(file.path, commitHash);
        
        if (previousVersion) {
          reverseChanges.set(file.path, {
            path: file.path,
            hash: previousVersion.hash,
            size: previousVersion.size,
            staged: new Date(),
            status: 'modified'
          });
        } else {
          // File was added in the commit, so delete it
          reverseChanges.set(file.path, {
            path: file.path,
            hash: null,
            size: 0,
            staged: new Date(),
            status: 'deleted'
          });
        }
      }

      // Stage reverse changes
      this.uncommittedChanges = reverseChanges;

      // Create revert commit
      const revertMessage = message || `Revert "${commit.message}"`;
      const revertCommit = await this.createCommit(revertMessage, 'System');

      this.emit('commitReverted', { original: commit, revert: revertCommit });
      return revertCommit;
    } catch (error) {
      this.emit('error', new Error(`Failed to revert commit: ${error.message}`));
      return null;
    }
  }

  /**
   * Get status of working directory
   */
  async getStatus() {
    const status = {
      branch: this.currentBranch,
      staged: Array.from(this.uncommittedChanges.values()),
      unstaged: [],
      untracked: [],
      clean: this.uncommittedChanges.size === 0
    };

    // Check for unstaged and untracked files
    try {
      const files = await this.getWorkingDirectoryFiles();
      const lastCommit = this.commits.get(this.repository.head);
      const trackedFiles = new Set(lastCommit ? lastCommit.files.map(f => f.path) : []);

      for (const file of files) {
        if (!trackedFiles.has(file.path) && !this.uncommittedChanges.has(file.path)) {
          status.untracked.push(file);
        }
      }
    } catch (error) {
      // Handle error silently
    }

    return status;
  }

  /**
   * Calculate hash for content
   */
  calculateHash(content) {
    return crypto.createHash('sha256').update(content).digest('hex');
  }

  /**
   * Generate commit hash
   */
  generateCommitHash() {
    const timestamp = Date.now().toString();
    const random = Math.random().toString();
    return crypto.createHash('sha256').update(timestamp + random).digest('hex');
  }

  /**
   * Create tree structure from changes
   */
  createTreeFromChanges() {
    const tree = {};
    
    for (const [path, file] of this.uncommittedChanges) {
      const parts = path.split('/');
      let current = tree;
      
      for (let i = 0; i < parts.length - 1; i++) {
        if (!current[parts[i]]) {
          current[parts[i]] = {};
        }
        current = current[parts[i]];
      }
      
      current[parts[parts.length - 1]] = {
        hash: file.hash,
        size: file.size,
        type: 'file'
      };
    }
    
    return tree;
  }

  /**
   * Calculate commit statistics
   */
  calculateCommitStats() {
    const files = Array.from(this.uncommittedChanges.values());
    
    return {
      filesChanged: files.length,
      additions: files.filter(f => f.status === 'added').length,
      modifications: files.filter(f => f.status === 'modified').length,
      deletions: files.filter(f => f.status === 'deleted').length,
      totalSize: files.reduce((sum, f) => sum + f.size, 0)
    };
  }

  /**
   * Store file object
   */
  async storeFileObject(hash, content) {
    const objectPath = path.join(this.repositoryPath, 'objects', hash);
    await fs.writeFile(objectPath, content);
  }

  /**
   * Save commit to disk
   */
  async saveCommit(commit) {
    const commitPath = path.join(this.repositoryPath, 'objects', commit.hash);
    await fs.writeFile(commitPath, JSON.stringify(commit, null, 2));
  }

  /**
   * Save repository metadata
   */
  async saveRepositoryMetadata() {
    const metadataPath = path.join(this.repositoryPath, 'metadata.json');
    await fs.writeFile(metadataPath, JSON.stringify(this.repository, null, 2));
  }

  /**
   * Save branches
   */
  async saveBranches() {
    const branchesPath = path.join(this.repositoryPath, 'refs', 'branches.json');
    const branchesData = Object.fromEntries(this.branches);
    await fs.writeFile(branchesPath, JSON.stringify(branchesData, null, 2));
  }

  /**
   * Save tags
   */
  async saveTags() {
    const tagsPath = path.join(this.repositoryPath, 'refs', 'tags.json');
    const tagsData = Object.fromEntries(this.tags);
    await fs.writeFile(tagsPath, JSON.stringify(tagsData, null, 2));
  }

  /**
   * Load commits from disk
   */
  async loadCommits() {
    try {
      const objectsPath = path.join(this.repositoryPath, 'objects');
      const files = await fs.readdir(objectsPath);
      
      for (const file of files) {
        try {
          const filePath = path.join(objectsPath, file);
          const content = await fs.readFile(filePath, 'utf8');
          const data = JSON.parse(content);
          
          // Check if it's a commit object (has message and author)
          if (data.message && data.author) {
            this.commits.set(file, data);
          }
        } catch (error) {
          // Skip non-JSON files
        }
      }
    } catch (error) {
      // Objects directory doesn't exist yet
    }
  }

  /**
   * Load branches from disk
   */
  async loadBranches() {
    try {
      const branchesPath = path.join(this.repositoryPath, 'refs', 'branches.json');
      const content = await fs.readFile(branchesPath, 'utf8');
      const branchesData = JSON.parse(content);
      
      this.branches = new Map(Object.entries(branchesData));
    } catch (error) {
      // Branches file doesn't exist yet, use defaults
    }
  }

  /**
   * Load tags from disk
   */
  async loadTags() {
    try {
      const tagsPath = path.join(this.repositoryPath, 'refs', 'tags.json');
      const content = await fs.readFile(tagsPath, 'utf8');
      const tagsData = JSON.parse(content);
      
      this.tags = new Map(Object.entries(tagsData));
    } catch (error) {
      // Tags file doesn't exist yet
    }
  }

  /**
   * Get working directory files
   */
  async getWorkingDirectoryFiles() {
    const files = [];
    
    const scanDirectory = async (dir, basePath = '') => {
      const entries = await fs.readdir(dir, { withFileTypes: true });
      
      for (const entry of entries) {
        if (entry.name.startsWith('.')) continue; // Skip hidden files
        
        const entryPath = path.join(dir, entry.name);
        const relativePath = path.join(basePath, entry.name);
        
        if (entry.isDirectory()) {
          await scanDirectory(entryPath, relativePath);
        } else {
          const stats = await fs.stat(entryPath);
          files.push({
            path: relativePath,
            size: stats.size,
            modified: stats.mtime
          });
        }
      }
    };
    
    try {
      await scanDirectory(this.workingDirectory);
    } catch (error) {
      // Handle directory scan errors
    }
    
    return files;
  }

  /**
   * Get all branches
   */
  getAllBranches() {
    return Array.from(this.branches.values());
  }

  /**
   * Get all tags
   */
  getAllTags() {
    return Array.from(this.tags.values());
  }

  /**
   * Get repository statistics
   */
  getRepositoryStatistics() {
    return {
      totalCommits: this.commits.size,
      totalBranches: this.branches.size,
      totalTags: this.tags.size,
      currentBranch: this.currentBranch,
      uncommittedChanges: this.uncommittedChanges.size,
      lastCommit: this.repository.head ? this.commits.get(this.repository.head) : null
    };
  }
}

module.exports = VersionControl;