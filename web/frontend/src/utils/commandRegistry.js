/**
 * Enhancement 7: Command Registry
 * All available commands for the Command Palette
 */

/**
 * All available commands organized by category
 */
export const COMMANDS = [
  // Navigation Commands
  {
    id: 'nav-workflows',
    title: 'Go to Workflows',
    description: 'Navigate to workflows page',
    category: 'Navigation',
    keywords: ['workflows', 'go', 'navigate', 'page'],
    action: (navigate, actions) => navigate('/workflows'),
    shortcut: '⌘1'
  },
  {
    id: 'nav-search',
    title: 'Go to Search',
    description: 'Navigate to search page',
    category: 'Navigation',
    keywords: ['search', 'find', 'go', 'navigate'],
    action: (navigate, actions) => navigate('/search'),
    shortcut: '⌘2'
  },
  {
    id: 'nav-analytics',
    title: 'Go to Analytics',
    description: 'Navigate to analytics page',
    category: 'Navigation',
    keywords: ['analytics', 'stats', 'metrics', 'go'],
    action: (navigate, actions) => navigate('/analytics'),
    shortcut: '⌘3'
  },

  // Workflow Commands
  {
    id: 'workflow-new',
    title: 'New Workflow',
    description: 'Create a new workflow',
    category: 'Workflows',
    keywords: ['new', 'create', 'workflow', 'blank'],
    action: (navigate, actions) => actions?.createWorkflow?.(),
    shortcut: '⌘N'
  },
  {
    id: 'workflow-save',
    title: 'Save Workflow',
    description: 'Save current workflow',
    category: 'Workflows',
    keywords: ['save', 'workflow'],
    action: (navigate, actions) => actions?.saveWorkflow?.(),
    shortcut: '⌘S'
  },
  {
    id: 'workflow-test',
    title: 'Test Workflow',
    description: 'Run workflow simulation',
    category: 'Workflows',
    keywords: ['test', 'simulate', 'run', 'workflow'],
    action: (navigate, actions) => actions?.testWorkflow?.(),
    shortcut: '⌘T'
  },
  {
    id: 'workflow-validate',
    title: 'Validate Workflow',
    description: 'Check workflow for errors',
    category: 'Workflows',
    keywords: ['validate', 'check', 'errors', 'workflow'],
    action: (navigate, actions) => actions?.validateWorkflow?.(),
    shortcut: '⌘⇧V'
  },
  {
    id: 'workflow-export',
    title: 'Export Workflow',
    description: 'Export workflow as JSON',
    category: 'Workflows',
    keywords: ['export', 'download', 'json', 'workflow'],
    action: (navigate, actions) => actions?.exportWorkflow?.(),
    shortcut: '⌘E'
  },
  {
    id: 'workflow-import',
    title: 'Import Workflow',
    description: 'Import workflow from JSON',
    category: 'Workflows',
    keywords: ['import', 'upload', 'load', 'workflow'],
    action: (navigate, actions) => actions?.importWorkflow?.()
  },
  {
    id: 'workflow-generate-ai',
    title: 'Generate with AI',
    description: 'Create workflow using AI',
    category: 'Workflows',
    keywords: ['ai', 'generate', 'create', 'workflow', 'assistant'],
    action: (navigate, actions) => actions?.generateWithAI?.(),
    shortcut: '⌘G'
  },
  {
    id: 'workflow-version-history',
    title: 'Version History',
    description: 'View workflow versions',
    category: 'Workflows',
    keywords: ['version', 'history', 'commits', 'git'],
    action: (navigate, actions) => actions?.showVersionHistory?.(),
    shortcut: '⌘H'
  },

  // Edit Commands
  {
    id: 'edit-undo',
    title: 'Undo',
    description: 'Undo last action',
    category: 'Edit',
    keywords: ['undo', 'revert'],
    action: (navigate, actions) => actions?.undo?.(),
    shortcut: '⌘Z'
  },
  {
    id: 'edit-redo',
    title: 'Redo',
    description: 'Redo last action',
    category: 'Edit',
    keywords: ['redo', 'repeat'],
    action: (navigate, actions) => actions?.redo?.(),
    shortcut: '⌘⇧Z'
  },
  {
    id: 'edit-copy',
    title: 'Copy Node',
    description: 'Copy selected node',
    category: 'Edit',
    keywords: ['copy', 'duplicate', 'node'],
    action: (navigate, actions) => actions?.copyNode?.(),
    shortcut: '⌘C'
  },
  {
    id: 'edit-paste',
    title: 'Paste Node',
    description: 'Paste copied node',
    category: 'Edit',
    keywords: ['paste', 'node'],
    action: (navigate, actions) => actions?.pasteNode?.(),
    shortcut: '⌘V'
  },
  {
    id: 'edit-delete',
    title: 'Delete Node',
    description: 'Delete selected node',
    category: 'Edit',
    keywords: ['delete', 'remove', 'node'],
    action: (navigate, actions) => actions?.deleteNode?.(),
    shortcut: 'Delete'
  },

  // View Commands
  {
    id: 'view-fit-screen',
    title: 'Fit to Screen',
    description: 'Fit workflow to screen',
    category: 'View',
    keywords: ['fit', 'screen', 'zoom', 'view'],
    action: (navigate, actions) => actions?.fitToScreen?.(),
    shortcut: '⌘0'
  },
  {
    id: 'view-toggle-grid',
    title: 'Toggle Grid',
    description: 'Show/hide grid',
    category: 'View',
    keywords: ['grid', 'toggle', 'show', 'hide'],
    action: (navigate, actions) => actions?.toggleGrid?.()
  },

  // Search Commands
  {
    id: 'search-open',
    title: 'Open Search',
    description: 'Open global search',
    category: 'Search',
    keywords: ['search', 'find', 'open'],
    action: (navigate, actions) => actions?.openSearch?.(),
    shortcut: '⌘K'
  },
  {
    id: 'search-commands',
    title: 'Search Commands',
    description: 'Search GHL commands',
    category: 'Search',
    keywords: ['commands', 'search', 'ghl'],
    action: (navigate, actions) => {
      navigate('/search');
      setTimeout(() => actions?.focusSearch?.(), 100);
    }
  },

  // Help Commands
  {
    id: 'help-shortcuts',
    title: 'Keyboard Shortcuts',
    description: 'Show all shortcuts',
    category: 'Help',
    keywords: ['help', 'shortcuts', 'keyboard', 'keys'],
    action: (navigate, actions) => actions?.showShortcutsHelp?.(),
    shortcut: '⇧?'
  },
  {
    id: 'help-docs',
    title: 'Documentation',
    description: 'Open documentation',
    category: 'Help',
    keywords: ['help', 'docs', 'documentation'],
    action: () => window.open('https://docs.ghlwiz.com', '_blank')
  }
];

/**
 * Search commands by query
 * Uses fuzzy matching on title, description, and keywords
 *
 * @param {string} query - Search query
 * @returns {array} - Matching commands
 */
export function searchCommands(query) {
  if (!query || query.trim() === '') {
    return COMMANDS;
  }

  const queryLower = query.toLowerCase();
  const words = queryLower.split(/\s+/);

  return COMMANDS.filter(cmd => {
    // Check title
    if (cmd.title.toLowerCase().includes(queryLower)) {
      return true;
    }

    // Check description
    if (cmd.description && cmd.description.toLowerCase().includes(queryLower)) {
      return true;
    }

    // Check keywords
    if (cmd.keywords.some(kw => kw.toLowerCase().includes(queryLower))) {
      return true;
    }

    // Check if all words match somewhere
    return words.every(word =>
      cmd.title.toLowerCase().includes(word) ||
      cmd.description?.toLowerCase().includes(word) ||
      cmd.keywords.some(kw => kw.toLowerCase().includes(word))
    );
  }).sort((a, b) => {
    // Prioritize title matches
    const aTitle = a.title.toLowerCase().includes(queryLower);
    const bTitle = b.title.toLowerCase().includes(queryLower);

    if (aTitle && !bTitle) return -1;
    if (!aTitle && bTitle) return 1;

    return 0;
  });
}

/**
 * Get recent commands from localStorage
 *
 * @param {number} limit - Max number of recent commands
 * @returns {array} - Recent command objects
 */
export function getRecentCommands(limit = 5) {
  try {
    const recent = JSON.parse(localStorage.getItem('recentCommands') || '[]');

    return recent
      .slice(0, limit)
      .map(id => COMMANDS.find(cmd => cmd.id === id))
      .filter(Boolean); // Remove any undefined entries
  } catch (error) {
    console.error('Failed to get recent commands:', error);
    return [];
  }
}

/**
 * Add command to recent list
 *
 * @param {string} commandId - Command ID to add
 */
export function addToRecent(commandId) {
  try {
    let recent = JSON.parse(localStorage.getItem('recentCommands') || '[]');

    // Remove if already exists
    recent = recent.filter(id => id !== commandId);

    // Add to front
    recent.unshift(commandId);

    // Keep only last 10
    recent = recent.slice(0, 10);

    localStorage.setItem('recentCommands', JSON.stringify(recent));
  } catch (error) {
    console.error('Failed to save recent command:', error);
  }
}

/**
 * Get commands by category
 *
 * @returns {object} - Commands grouped by category
 */
export function getCommandsByCategory() {
  const grouped = {};

  COMMANDS.forEach(cmd => {
    if (!grouped[cmd.category]) {
      grouped[cmd.category] = [];
    }
    grouped[cmd.category].push(cmd);
  });

  return grouped;
}

/**
 * Get command by ID
 *
 * @param {string} id - Command ID
 * @returns {object|null} - Command object or null
 */
export function getCommandById(id) {
  return COMMANDS.find(cmd => cmd.id === id) || null;
}
