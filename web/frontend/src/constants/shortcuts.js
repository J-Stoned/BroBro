/**
 * Enhancement 7: Keyboard Shortcuts
 * Centralized keyboard shortcuts configuration
 */

export const SHORTCUTS = {
  // Global shortcuts (work everywhere)
  global: {
    SEARCH: {
      key: 'k',
      modifiers: ['meta', 'ctrl'], // meta = Cmd on Mac, Ctrl on Windows
      description: 'Open search',
      action: 'openSearch'
    },
    COMMAND_PALETTE: {
      key: '/',
      modifiers: ['meta', 'ctrl'],
      description: 'Open command palette',
      action: 'openCommandPalette'
    },
    SETTINGS: {
      key: ',',
      modifiers: ['meta', 'ctrl'],
      description: 'Open settings',
      action: 'openSettings'
    },
    ESCAPE: {
      key: 'Escape',
      modifiers: [],
      description: 'Close modals/panels',
      action: 'closeModal'
    },
    HELP: {
      key: '?',
      modifiers: ['shift'],
      description: 'Show keyboard shortcuts help',
      action: 'showHelp'
    }
  },

  // Workflow builder shortcuts
  workflow: {
    NEW_WORKFLOW: {
      key: 'n',
      modifiers: ['meta', 'ctrl'],
      description: 'Create new workflow',
      action: 'newWorkflow'
    },
    SAVE_WORKFLOW: {
      key: 's',
      modifiers: ['meta', 'ctrl'],
      description: 'Save workflow',
      action: 'saveWorkflow'
    },
    TEST_WORKFLOW: {
      key: 't',
      modifiers: ['meta', 'ctrl'],
      description: 'Test workflow',
      action: 'testWorkflow'
    },
    VALIDATE_WORKFLOW: {
      key: 'v',
      modifiers: ['meta', 'ctrl'],
      description: 'Validate workflow',
      action: 'validateWorkflow'
    },
    DUPLICATE_NODE: {
      key: 'd',
      modifiers: ['meta', 'ctrl'],
      description: 'Duplicate selected node',
      action: 'duplicateNode'
    },
    DELETE_NODE: {
      key: 'Delete',
      modifiers: [],
      description: 'Delete selected node',
      action: 'deleteNode'
    },
    UNDO: {
      key: 'z',
      modifiers: ['meta', 'ctrl'],
      description: 'Undo',
      action: 'undo'
    },
    REDO: {
      key: 'z',
      modifiers: ['meta', 'ctrl', 'shift'],
      description: 'Redo',
      action: 'redo'
    },
    COPY_NODE: {
      key: 'c',
      modifiers: ['meta', 'ctrl'],
      description: 'Copy selected node',
      action: 'copyNode'
    },
    PASTE_NODE: {
      key: 'v',
      modifiers: ['meta', 'ctrl'],
      description: 'Paste node',
      action: 'pasteNode'
    },
    SELECT_ALL: {
      key: 'a',
      modifiers: ['meta', 'ctrl'],
      description: 'Select all nodes',
      action: 'selectAll'
    },
    ADD_NODE: {
      key: ' ',
      modifiers: [],
      description: 'Add new node',
      action: 'addNode'
    },
    ZOOM_IN: {
      key: '+',
      modifiers: ['meta', 'ctrl'],
      description: 'Zoom in',
      action: 'zoomIn'
    },
    ZOOM_OUT: {
      key: '-',
      modifiers: ['meta', 'ctrl'],
      description: 'Zoom out',
      action: 'zoomOut'
    },
    FIT_VIEW: {
      key: '0',
      modifiers: ['meta', 'ctrl'],
      description: 'Fit view to canvas',
      action: 'fitView'
    }
  },

  // Search shortcuts
  search: {
    FOCUS_SEARCH: {
      key: 'k',
      modifiers: ['meta', 'ctrl'],
      description: 'Focus search bar',
      action: 'focusSearch'
    },
    NEXT_RESULT: {
      key: 'ArrowDown',
      modifiers: [],
      description: 'Next search result',
      action: 'nextResult'
    },
    PREV_RESULT: {
      key: 'ArrowUp',
      modifiers: [],
      description: 'Previous search result',
      action: 'prevResult'
    },
    SELECT_RESULT: {
      key: 'Enter',
      modifiers: [],
      description: 'Select highlighted result',
      action: 'selectResult'
    },
    NEXT_SECTION: {
      key: 'Tab',
      modifiers: [],
      description: 'Next result section',
      action: 'nextSection'
    }
  },

  // Navigation shortcuts
  navigation: {
    GO_TO_WORKFLOWS: {
      key: '1',
      modifiers: ['meta', 'ctrl'],
      description: 'Go to Workflows',
      action: 'goToWorkflows'
    },
    GO_TO_SEARCH: {
      key: '2',
      modifiers: ['meta', 'ctrl'],
      description: 'Go to Search',
      action: 'goToSearch'
    },
    GO_TO_ANALYTICS: {
      key: '3',
      modifiers: ['meta', 'ctrl'],
      description: 'Go to Analytics',
      action: 'goToAnalytics'
    },
    GO_TO_TEMPLATES: {
      key: '4',
      modifiers: ['meta', 'ctrl'],
      description: 'Go to Templates',
      action: 'goToTemplates'
    }
  }
};

/**
 * Get all shortcuts as flat array
 */
export function getAllShortcuts() {
  const all = [];

  Object.entries(SHORTCUTS).forEach(([category, shortcuts]) => {
    Object.entries(shortcuts).forEach(([name, shortcut]) => {
      all.push({
        ...shortcut,
        name,
        category
      });
    });
  });

  return all;
}

/**
 * Format shortcut for display
 */
export function formatShortcut(shortcut) {
  const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
  const modKeys = [];

  if (shortcut.modifiers.includes('meta') || shortcut.modifiers.includes('ctrl')) {
    modKeys.push(isMac ? '⌘' : 'Ctrl');
  }
  if (shortcut.modifiers.includes('shift')) {
    modKeys.push(isMac ? '⇧' : 'Shift');
  }
  if (shortcut.modifiers.includes('alt')) {
    modKeys.push(isMac ? '⌥' : 'Alt');
  }

  const key = shortcut.key.length === 1 ? shortcut.key.toUpperCase() : shortcut.key;

  return [...modKeys, key].join(' + ');
}
