/**
 * Enhancement 7: Keyboard Shortcuts React Hook
 * Easy integration of keyboard shortcuts into React components
 */

import { useEffect, useRef } from 'react';
import { shortcutManager } from '../utils/keyboardShortcutManager';

/**
 * Register keyboard shortcuts for a component
 *
 * @param {string} context - Context name (e.g., 'global', 'workflow', 'search')
 * @param {object} shortcuts - Map of shortcut configs to handlers
 * @param {array} deps - Dependency array for useEffect
 *
 * @example
 * useKeyboardShortcuts('workflow', {
 *   [SHORTCUTS.workflow.SAVE]: handleSave,
 *   [SHORTCUTS.workflow.TEST]: handleTest
 * }, [handleSave, handleTest]);
 */
export function useKeyboardShortcuts(context, shortcuts, deps = []) {
  const shortcutIdsRef = useRef([]);

  useEffect(() => {
    // Start the manager if not already started
    shortcutManager.start();

    // Register all shortcuts
    const newIds = [];

    Object.entries(shortcuts).forEach(([key, handler]) => {
      // key could be a shortcut config object or just the handler
      let shortcutConfig;
      let shortcutHandler;

      if (typeof key === 'string') {
        // Key is a JSON string or needs parsing
        try {
          shortcutConfig = JSON.parse(key);
          shortcutHandler = handler;
        } catch {
          console.warn('Invalid shortcut config:', key);
          return;
        }
      } else if (typeof handler === 'function') {
        // Key is the config object, handler is the function
        shortcutConfig = key;
        shortcutHandler = handler;
      } else {
        console.warn('Invalid shortcut format');
        return;
      }

      // Validate shortcut config has required properties
      if (!shortcutConfig || !shortcutConfig.key || !shortcutConfig.modifiers) {
        console.warn('Invalid shortcut config - missing key or modifiers:', shortcutConfig);
        return;
      }

      // Generate unique ID for this shortcut
      const id = `${context}-${shortcutConfig.key}-${shortcutConfig.modifiers.join('-')}-${Date.now()}`;

      // Register the shortcut
      shortcutManager.registerShortcut(
        context,
        shortcutConfig,
        shortcutHandler,
        id
      );

      newIds.push({ context, id });
    });

    shortcutIdsRef.current = newIds;

    // Set this as the active context
    shortcutManager.setContext(context);

    // Cleanup function
    return () => {
      // Unregister all shortcuts
      shortcutIdsRef.current.forEach(({ context: ctx, id }) => {
        shortcutManager.unregisterShortcut(ctx, id);
      });

      shortcutIdsRef.current = [];
    };
  }, [context, ...deps]);
}

/**
 * Alternative hook that accepts an array of shortcut definitions
 *
 * @param {string} context - Context name
 * @param {array} shortcutDefs - Array of {config, handler} objects
 * @param {array} deps - Dependency array
 *
 * @example
 * useKeyboardShortcutsArray('workflow', [
 *   { config: SHORTCUTS.workflow.SAVE, handler: handleSave },
 *   { config: SHORTCUTS.workflow.TEST, handler: handleTest }
 * ], [handleSave, handleTest]);
 */
export function useKeyboardShortcutsArray(context, shortcutDefs, deps = []) {
  const shortcutIdsRef = useRef([]);

  useEffect(() => {
    shortcutManager.start();

    const newIds = [];

    shortcutDefs.forEach(({ config, handler }) => {
      // Validate config
      if (!config || !config.key || !config.modifiers) {
        console.warn('Invalid shortcut config in array - missing key or modifiers:', config);
        return;
      }

      const id = `${context}-${config.key}-${config.modifiers.join('-')}-${Date.now()}`;

      shortcutManager.registerShortcut(context, config, handler, id);
      newIds.push({ context, id });
    });

    shortcutIdsRef.current = newIds;
    shortcutManager.setContext(context);

    return () => {
      shortcutIdsRef.current.forEach(({ context: ctx, id }) => {
        shortcutManager.unregisterShortcut(ctx, id);
      });
      shortcutIdsRef.current = [];
    };
  }, [context, ...deps]);
}

/**
 * Hook to temporarily disable shortcuts
 * Useful for modals or dialogs
 *
 * @example
 * const [disableShortcuts, enableShortcuts] = useShortcutControl();
 *
 * useEffect(() => {
 *   if (modalOpen) {
 *     disableShortcuts();
 *   } else {
 *     enableShortcuts();
 *   }
 * }, [modalOpen]);
 */
export function useShortcutControl() {
  const disable = () => shortcutManager.disable();
  const enable = () => shortcutManager.enable();

  return [disable, enable];
}

/**
 * Hook to change the active context
 *
 * @param {string} context - Context to activate
 *
 * @example
 * useShortcutContext('workflow'); // Activate workflow shortcuts
 */
export function useShortcutContext(context) {
  useEffect(() => {
    const previousContext = shortcutManager.getContext();
    shortcutManager.setContext(context);

    return () => {
      shortcutManager.setContext(previousContext);
    };
  }, [context]);
}
