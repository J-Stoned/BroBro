/**
 * Enhancement 7: Keyboard Shortcut Manager
 * Centralized keyboard event handling with context switching
 */

class KeyboardShortcutManager {
  constructor() {
    this.shortcuts = new Map(); // context -> array of shortcuts
    this.currentContext = 'global';
    this.enabled = true;
    this.boundHandler = null;
  }

  /**
   * Start listening for keyboard events
   */
  start() {
    if (this.boundHandler) {
      return; // Already started
    }

    this.boundHandler = this.handleKeyDown.bind(this);
    document.addEventListener('keydown', this.boundHandler, true);
  }

  /**
   * Stop listening for keyboard events
   */
  stop() {
    if (this.boundHandler) {
      document.removeEventListener('keydown', this.boundHandler, true);
      this.boundHandler = null;
    }
  }

  /**
   * Handle keydown events
   */
  handleKeyDown(event) {
    if (!this.enabled) {
      return;
    }

    // Don't handle shortcuts when typing in inputs (except Escape)
    const target = event.target;
    const isInput = target.tagName === 'INPUT' ||
                    target.tagName === 'TEXTAREA' ||
                    target.isContentEditable;

    if (isInput && event.key !== 'Escape') {
      return;
    }

    // Build key combination
    const combination = {
      key: event.key,
      meta: event.metaKey,
      ctrl: event.ctrlKey,
      shift: event.shiftKey,
      alt: event.altKey
    };

    // Find matching shortcut
    const matched = this.findMatchingShortcut(combination);

    if (matched) {
      event.preventDefault();
      event.stopPropagation();

      try {
        matched.handler(event);
      } catch (error) {
        console.error('Shortcut handler error:', error);
      }
    }
  }

  /**
   * Find a shortcut that matches the key combination
   */
  findMatchingShortcut(combination) {
    // Try current context first
    const contextShortcuts = this.shortcuts.get(this.currentContext) || [];
    let match = this.matchShortcut(combination, contextShortcuts);

    if (match) {
      return match;
    }

    // Fall back to global shortcuts
    if (this.currentContext !== 'global') {
      const globalShortcuts = this.shortcuts.get('global') || [];
      return this.matchShortcut(combination, globalShortcuts);
    }

    return null;
  }

  /**
   * Check if a combination matches any shortcut in the list
   */
  matchShortcut(combination, shortcuts) {
    return shortcuts.find(shortcut => {
      // Key must match (case-insensitive)
      if (shortcut.key.toLowerCase() !== combination.key.toLowerCase()) {
        return false;
      }

      // Check modifiers
      const hasMeta = shortcut.modifiers.includes('meta') || shortcut.modifiers.includes('ctrl');
      const hasShift = shortcut.modifiers.includes('shift');
      const hasAlt = shortcut.modifiers.includes('alt');

      // Meta/Ctrl are treated as equivalent (cross-platform)
      const metaMatch = hasMeta
        ? (combination.meta || combination.ctrl)
        : !combination.meta && !combination.ctrl;

      const shiftMatch = hasShift ? combination.shift : !combination.shift;
      const altMatch = hasAlt ? combination.alt : !combination.alt;

      return metaMatch && shiftMatch && altMatch;
    });
  }

  /**
   * Register a shortcut
   * @param {string} context - Context name (e.g., 'global', 'workflow', 'search')
   * @param {object} shortcut - Shortcut config with key and modifiers
   * @param {function} handler - Handler function to call
   * @param {string} id - Unique identifier for this shortcut
   */
  registerShortcut(context, shortcut, handler, id = null) {
    if (!this.shortcuts.has(context)) {
      this.shortcuts.set(context, []);
    }

    const shortcuts = this.shortcuts.get(context);

    // Remove existing shortcut with same ID if provided
    if (id) {
      const existingIndex = shortcuts.findIndex(s => s.id === id);
      if (existingIndex >= 0) {
        shortcuts.splice(existingIndex, 1);
      }
    }

    shortcuts.push({
      ...shortcut,
      handler,
      id: id || `${context}-${shortcut.key}-${Date.now()}`
    });
  }

  /**
   * Unregister a shortcut by ID
   */
  unregisterShortcut(context, id) {
    const shortcuts = this.shortcuts.get(context);
    if (!shortcuts) return;

    const index = shortcuts.findIndex(s => s.id === id);
    if (index >= 0) {
      shortcuts.splice(index, 1);
    }
  }

  /**
   * Set the current context
   * @param {string} context - Context name
   */
  setContext(context) {
    this.currentContext = context;
  }

  /**
   * Get the current context
   */
  getContext() {
    return this.currentContext;
  }

  /**
   * Clear all shortcuts in a context
   * @param {string} context - Context to clear
   */
  clearContext(context) {
    this.shortcuts.delete(context);
  }

  /**
   * Enable shortcut handling
   */
  enable() {
    this.enabled = true;
  }

  /**
   * Disable shortcut handling temporarily
   */
  disable() {
    this.enabled = false;
  }

  /**
   * Check if shortcuts are enabled
   */
  isEnabled() {
    return this.enabled;
  }

  /**
   * Get all shortcuts for a context
   */
  getShortcuts(context) {
    return this.shortcuts.get(context) || [];
  }

  /**
   * Get all contexts
   */
  getAllContexts() {
    return Array.from(this.shortcuts.keys());
  }
}

// Singleton instance
export const shortcutManager = new KeyboardShortcutManager();
