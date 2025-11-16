/**
 * MockContactSelector Component
 * Enhancement 5: Workflow Testing
 *
 * Displays and allows selection of mock contact personas for testing
 */

import React from 'react';
import { User, Check } from 'lucide-react';

export function MockContactSelector({ contacts, selected, onSelect, disabled }) {
  return (
    <div className="mock-contact-selector">
      <h3>
        <User size={18} />
        Select Test Contact
      </h3>

      <div className="contacts-grid">
        {contacts.map(contact => (
          <button
            key={contact.id}
            className={`contact-card ${selected?.id === contact.id ? 'selected' : ''}`}
            onClick={() => onSelect(contact)}
            disabled={disabled}
          >
            <div className="contact-header">
              <span className="contact-name">{contact.name}</span>
              {selected?.id === contact.id && (
                <Check size={16} className="check-icon" />
              )}
            </div>

            <div className="contact-persona">{contact.persona}</div>
            <div className="contact-description">{contact.description}</div>

            <div className="contact-stats">
              <div className="stat">
                <span className="stat-label">Email Open:</span>
                <span className="stat-value">
                  {(contact.email_engagement_rate * 100).toFixed(0)}%
                </span>
              </div>
              <div className="stat">
                <span className="stat-label">SMS Reply:</span>
                <span className="stat-value">
                  {(contact.sms_reply_rate * 100).toFixed(0)}%
                </span>
              </div>
            </div>

            <div className="contact-tags">
              {contact.tags.map((tag, idx) => (
                <span key={idx} className="tag">
                  {tag}
                </span>
              ))}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
