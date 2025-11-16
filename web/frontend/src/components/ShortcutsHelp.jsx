/**
 * Enhancement 7: Shortcuts Help Modal
 * Display all keyboard shortcuts organized by category (Shift+?)
 */

import React, { useState } from 'react';
import { X, Search, Keyboard } from 'lucide-react';
import { SHORTCUTS, formatShortcut } from '../constants/shortcuts';
import './ShortcutsHelp.css';

export function ShortcutsHelp({ isOpen, onClose }) {
  const [searchQuery, setSearchQuery] = useState('');

  if (!isOpen) return null;

  // Flatten all shortcuts with their category
  const allShortcuts = [];
  Object.entries(SHORTCUTS).forEach(([category, shortcuts]) => {
    Object.entries(shortcuts).forEach(([name, shortcut]) => {
      allShortcuts.push({
        ...shortcut,
        category: category.charAt(0).toUpperCase() + category.slice(1),
        name
      });
    });
  });

  // Filter shortcuts based on search query
  const filteredShortcuts = searchQuery
    ? allShortcuts.filter(s =>
        s.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        formatShortcut(s).toLowerCase().includes(searchQuery.toLowerCase()) ||
        s.category.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : allShortcuts;

  // Group filtered shortcuts by category
  const groupedShortcuts = filteredShortcuts.reduce((acc, shortcut) => {
    if (!acc[shortcut.category]) {
      acc[shortcut.category] = [];
    }
    acc[shortcut.category].push(shortcut);
    return acc;
  }, {});

  // Category order
  const categoryOrder = ['Global', 'Workflow', 'Navigation', 'Search'];
  const sortedCategories = Object.keys(groupedShortcuts).sort((a, b) => {
    const aIndex = categoryOrder.indexOf(a);
    const bIndex = categoryOrder.indexOf(b);
    if (aIndex === -1) return 1;
    if (bIndex === -1) return -1;
    return aIndex - bIndex;
  });

  return (
    <div className="shortcuts-help-overlay" onClick={onClose}>
      <div className="shortcuts-help-modal" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="modal-header">
          <div className="header-left">
            <Keyboard size={24} className="header-icon" />
            <h2>Keyboard Shortcuts</h2>
          </div>
          <button className="close-button" onClick={onClose} title="Close (Esc)">
            <X size={20} />
          </button>
        </div>

        {/* Search */}
        <div className="shortcuts-search">
          <Search size={18} className="search-icon" />
          <input
            type="text"
            placeholder="Search shortcuts..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
        </div>

        {/* Content */}
        <div className="shortcuts-content">
          {sortedCategories.length > 0 ? (
            sortedCategories.map(category => (
              <div key={category} className="shortcuts-category">
                <h3 className="category-title">{category}</h3>
                <div className="shortcuts-list">
                  {groupedShortcuts[category].map((shortcut, idx) => (
                    <div key={idx} className="shortcut-item">
                      <span className="shortcut-description">{shortcut.description}</span>
                      <kbd className="shortcut-keys">{formatShortcut(shortcut)}</kbd>
                    </div>
                  ))}
                </div>
              </div>
            ))
          ) : (
            <div className="empty-state">
              <Keyboard size={48} className="empty-icon" />
              <p className="empty-title">No shortcuts found</p>
              <p className="empty-description">
                Try searching for something else
              </p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="modal-footer">
          <p className="footer-text">
            Press <kbd>Shift + ?</kbd> to toggle this help anytime
          </p>
          <p className="footer-hint">
            Use <kbd>Cmd + /</kbd> (or <kbd>Ctrl + /</kbd>) to open the Command Palette
          </p>
        </div>
      </div>
    </div>
  );
}
