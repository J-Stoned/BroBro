/**
 * Enhancement 7: Command Palette Component
 * Quick command launcher with fuzzy search (Cmd+/ or Ctrl+/)
 */

import React, { useState, useEffect, useRef } from 'react';
import { Search, X, ChevronRight, Clock, Command } from 'lucide-react';
import { searchCommands, getRecentCommands, addToRecent } from '../utils/commandRegistry';
import { useNavigate } from 'react-router-dom';
import './CommandPalette.css';

export function CommandPalette({ isOpen, onClose, actions = {} }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [recentCommands, setRecentCommands] = useState([]);
  const inputRef = useRef(null);
  const resultsContainerRef = useRef(null);
  const navigate = useNavigate();

  // Load recent commands and focus input when opened
  useEffect(() => {
    if (isOpen) {
      setRecentCommands(getRecentCommands(5));
      setTimeout(() => inputRef.current?.focus(), 100);
      setResults(searchCommands(''));
      setSelectedIndex(0);
    } else {
      // Reset state when closed
      setQuery('');
      setResults([]);
      setSelectedIndex(0);
    }
  }, [isOpen]);

  // Update search results when query changes
  useEffect(() => {
    const searchResults = searchCommands(query);
    setResults(searchResults);
    setSelectedIndex(0);
  }, [query]);

  // Handle keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (!isOpen) return;

      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault();
          setSelectedIndex(prev => (prev < results.length - 1 ? prev + 1 : prev));
          break;

        case 'ArrowUp':
          e.preventDefault();
          setSelectedIndex(prev => (prev > 0 ? prev - 1 : 0));
          break;

        case 'Enter':
          e.preventDefault();
          if (results[selectedIndex]) {
            executeCommand(results[selectedIndex]);
          }
          break;

        case 'Escape':
          e.preventDefault();
          onClose();
          break;

        default:
          break;
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, results, selectedIndex, onClose]);

  // Scroll selected item into view
  useEffect(() => {
    if (resultsContainerRef.current) {
      const selectedElement = resultsContainerRef.current.querySelector('.command-item.selected');
      if (selectedElement) {
        selectedElement.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
      }
    }
  }, [selectedIndex]);

  /**
   * Execute a command
   */
  const executeCommand = (command) => {
    // Add to recent commands
    addToRecent(command.id);

    try {
      // Execute the command action
      command.action(navigate, actions);
    } catch (error) {
      console.error('Command execution error:', error);
    }

    // Close the palette
    onClose();
  };

  if (!isOpen) return null;

  // Group results by category
  const groupedResults = results.reduce((acc, cmd) => {
    if (!acc[cmd.category]) {
      acc[cmd.category] = [];
    }
    acc[cmd.category].push(cmd);
    return acc;
  }, {});

  const hasResults = results.length > 0;
  const showRecent = !query && recentCommands.length > 0;

  return (
    <div className="command-palette-overlay" onClick={onClose}>
      <div className="command-palette" onClick={(e) => e.stopPropagation()}>
        {/* Search Input */}
        <div className="palette-search">
          <Search size={20} className="search-icon" />
          <input
            ref={inputRef}
            type="text"
            placeholder="Type a command or search..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="search-input"
          />
          <button className="close-button" onClick={onClose} title="Close (Esc)">
            <X size={18} />
          </button>
        </div>

        {/* Recent Commands */}
        {showRecent && (
          <div className="recent-section">
            <div className="section-header">
              <Clock size={14} />
              <span>Recent</span>
            </div>
            <div className="commands-list">
              {recentCommands.map(cmd => (
                <CommandItem
                  key={cmd.id}
                  command={cmd}
                  isSelected={false}
                  onClick={() => executeCommand(cmd)}
                />
              ))}
            </div>
          </div>
        )}

        {/* Search Results */}
        {hasResults && (
          <div className="results-section" ref={resultsContainerRef}>
            {Object.entries(groupedResults).map(([category, commands]) => (
              <div key={category} className="category-group">
                <div className="category-header">{category}</div>
                <div className="commands-list">
                  {commands.map(cmd => {
                    const globalIndex = results.indexOf(cmd);
                    return (
                      <CommandItem
                        key={cmd.id}
                        command={cmd}
                        isSelected={globalIndex === selectedIndex}
                        onClick={() => executeCommand(cmd)}
                      />
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Empty State */}
        {!hasResults && query && (
          <div className="empty-state">
            <Command size={48} className="empty-icon" />
            <p className="empty-title">No commands found</p>
            <p className="empty-description">Try searching for "{query.split(' ')[0]}"</p>
          </div>
        )}

        {/* Footer */}
        <div className="palette-footer">
          <div className="footer-hint">
            <kbd>↑</kbd>
            <kbd>↓</kbd>
            <span>Navigate</span>
          </div>
          <div className="footer-hint">
            <kbd>↵</kbd>
            <span>Execute</span>
          </div>
          <div className="footer-hint">
            <kbd>Esc</kbd>
            <span>Close</span>
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * Individual command item
 */
function CommandItem({ command, isSelected, onClick }) {
  return (
    <button
      className={`command-item ${isSelected ? 'selected' : ''}`}
      onClick={onClick}
      onMouseEnter={(e) => e.currentTarget.scrollIntoView({ block: 'nearest', behavior: 'smooth' })}
    >
      <div className="command-content">
        <div className="command-title">{command.title}</div>
        {command.description && (
          <div className="command-description">{command.description}</div>
        )}
      </div>
      <div className="command-right">
        {command.shortcut && (
          <div className="command-shortcut">{command.shortcut}</div>
        )}
        {isSelected && <ChevronRight size={16} className="command-arrow" />}
      </div>
    </button>
  );
}
