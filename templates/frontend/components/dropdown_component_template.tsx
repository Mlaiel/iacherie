/**
 * 🎯 Dropdown Component Template - UI Component Templates
 * =====================================================
 * 
 * © 2025 Fahed Mlaiel <mlaiel@live.de>
 * TOUS DROITS RÉSERVÉS
 * 
 * 🚨 PROTECTION INTELLECTUELLE:
 * - Code propriétaire de Fahed Mlaiel
 * - Utilisation commerciale INTERDITE sans autorisation écrite
 * - Reverse engineering STRICTEMENT INTERDIT
 * - Distribution INTERDITE sans licence explicite
 * - Violation = Poursuites judiciaires automatiques
 */

import React, { useState, useRef, useEffect, useCallback } from 'react';
import styled, { css, keyframes } from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';

// ================================
// TYPES & INTERFACES
// ================================

export interface DropdownOption {
  value: string | number;
  label: string;
  disabled?: boolean;
  icon?: React.ReactNode;
  group?: string;
  metadata?: Record<string, any>;
}

export interface DropdownProps {
  options: DropdownOption[];
  value?: string | number | (string | number)[];
  onChange?: (value: string | number | (string | number)[]) => void;
  placeholder?: string;
  disabled?: boolean;
  multiple?: boolean;
  searchable?: boolean;
  clearable?: boolean;
  loading?: boolean;
  error?: string;
  required?: boolean;
  size?: 'small' | 'medium' | 'large';
  variant?: 'default' | 'minimal' | 'bordered' | 'filled';
  position?: 'bottom' | 'top' | 'auto';
  maxHeight?: number;
  renderOption?: (option: DropdownOption) => React.ReactNode;
  renderSelection?: (option: DropdownOption) => React.ReactNode;
  onSearch?: (query: string) => void;
  onFocus?: () => void;
  onBlur?: () => void;
  className?: string;
  'data-testid'?: string;
}

// ================================
// ANIMATIONS
// ================================

const fadeIn = keyframes`
  from { opacity: 0; transform: translateY(-8px); }
  to { opacity: 1; transform: translateY(0); }
`;

const slideDown = keyframes`
  from { opacity: 0; transform: scaleY(0.95) translateY(-10px); }
  to { opacity: 1; transform: scaleY(1) translateY(0); }
`;

// ================================
// STYLED COMPONENTS
// ================================

const DropdownContainer = styled.div<{ size: string; error?: string }>`
  position: relative;
  display: inline-block;
  min-width: 200px;
  width: 100%;
  
  ${({ size }) => {
    switch (size) {
      case 'small':
        return css`font-size: 0.875rem;`;
      case 'large':
        return css`font-size: 1.125rem;`;
      default:
        return css`font-size: 1rem;`;
    }
  }}
`;

const DropdownTrigger = styled.button<{
  variant: string;
  size: string;
  isOpen: boolean;
  hasError?: boolean;
  disabled?: boolean;
}>`
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: ${({ size }) => {
    switch (size) {
      case 'small': return '8px 12px';
      case 'large': return '16px 20px';
      default: return '12px 16px';
    }
  }};
  border: 2px solid ${({ hasError, theme }) => 
    hasError ? '#ef4444' : 'rgba(0, 0, 0, 0.1)'};
  border-radius: 8px;
  background: ${({ variant, theme }) => {
    switch (variant) {
      case 'filled': return 'rgba(0, 0, 0, 0.05)';
      case 'minimal': return 'transparent';
      default: return '#ffffff';
    }
  }};
  color: ${({ theme }) => theme?.colors?.text || '#333333'};
  font-size: inherit;
  font-family: inherit;
  cursor: ${({ disabled }) => disabled ? 'not-allowed' : 'pointer'};
  opacity: ${({ disabled }) => disabled ? 0.6 : 1};
  transition: all 0.2s ease;

  &:hover:not(:disabled) {
    border-color: ${({ theme }) => theme?.colors?.primary || '#3b82f6'};
    box-shadow: 0 0 0 3px ${({ theme }) => 
      theme?.colors?.primary ? `${theme.colors.primary}20` : '#3b82f620'};
  }

  &:focus {
    outline: none;
    border-color: ${({ theme }) => theme?.colors?.primary || '#3b82f6'};
    box-shadow: 0 0 0 3px ${({ theme }) => 
      theme?.colors?.primary ? `${theme.colors.primary}20` : '#3b82f620'};
  }

  ${({ variant }) => variant === 'minimal' && css`
    border: none;
    border-bottom: 2px solid rgba(0, 0, 0, 0.1);
    border-radius: 0;
    padding-left: 0;
    padding-right: 0;
  `}
`;

const DropdownIcon = styled.div<{ isOpen: boolean }>`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  transition: transform 0.2s ease;
  transform: ${({ isOpen }) => isOpen ? 'rotate(180deg)' : 'rotate(0deg)'};
  
  &::after {
    content: '';
    width: 0;
    height: 0;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 4px solid currentColor;
  }
`;

const DropdownList = styled(motion.div)<{ maxHeight: number; position: string }>`
  position: absolute;
  ${({ position }) => position === 'top' ? 'bottom: 100%' : 'top: 100%'};
  left: 0;
  right: 0;
  z-index: 1000;
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  max-height: ${({ maxHeight }) => maxHeight}px;
  overflow-y: auto;
  margin-top: ${({ position }) => position === 'top' ? '0' : '4px'};
  margin-bottom: ${({ position }) => position === 'top' ? '4px' : '0'};
`;

const DropdownOption = styled.button<{ 
  isSelected: boolean; 
  isHighlighted: boolean;
  disabled?: boolean;
}>`
  width: 100%;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  border: none;
  background: ${({ isSelected, isHighlighted }) => {
    if (isSelected) return '#3b82f6';
    if (isHighlighted) return 'rgba(59, 130, 246, 0.1)';
    return 'transparent';
  }};
  color: ${({ isSelected }) => isSelected ? '#ffffff' : '#333333'};
  font-size: inherit;
  font-family: inherit;
  text-align: left;
  cursor: ${({ disabled }) => disabled ? 'not-allowed' : 'pointer'};
  opacity: ${({ disabled }) => disabled ? 0.5 : 1};
  transition: all 0.15s ease;

  &:hover:not(:disabled) {
    background: ${({ isSelected }) => 
      isSelected ? '#2563eb' : 'rgba(59, 130, 246, 0.1)'};
  }

  &:first-child {
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
  }

  &:last-child {
    border-bottom-left-radius: 8px;
    border-bottom-right-radius: 8px;
  }
`;

const SearchInput = styled.input`
  width: 100%;
  padding: 12px 16px;
  border: none;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  background: transparent;
  font-size: inherit;
  font-family: inherit;

  &:focus {
    outline: none;
    border-bottom-color: #3b82f6;
  }

  &::placeholder {
    color: rgba(0, 0, 0, 0.5);
  }
`;

const MultipleSelection = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  min-height: 24px;
`;

const SelectionTag = styled.span`
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  background: #3b82f6;
  color: #ffffff;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 500;

  button {
    background: none;
    border: none;
    color: inherit;
    cursor: pointer;
    padding: 0;
    margin-left: 4px;
    width: 16px;
    height: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    transition: background 0.15s ease;

    &:hover {
      background: rgba(255, 255, 255, 0.2);
    }
  }
`;

const ErrorMessage = styled.div`
  color: #ef4444;
  font-size: 0.875rem;
  margin-top: 4px;
`;

const LoadingSpinner = styled.div`
  width: 16px;
  height: 16px;
  border: 2px solid rgba(0, 0, 0, 0.1);
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;

  @keyframes spin {
    to { transform: rotate(360deg); }
  }
`;

// ================================
// CUSTOM HOOKS
// ================================

const useClickOutside = (ref: React.RefObject<HTMLElement>, handler: () => void) => {
  useEffect(() => {
    const listener = (event: MouseEvent | TouchEvent) => {
      if (!ref.current || ref.current.contains(event.target as Node)) {
        return;
      }
      handler();
    };

    document.addEventListener('mousedown', listener);
    document.addEventListener('touchstart', listener);

    return () => {
      document.removeEventListener('mousedown', listener);
      document.removeEventListener('touchstart', listener);
    };
  }, [ref, handler]);
};

const useKeyboardNavigation = (
  options: DropdownOption[],
  isOpen: boolean,
  onSelect: (option: DropdownOption) => void,
  onClose: () => void
) => {
  const [highlightedIndex, setHighlightedIndex] = useState(-1);

  useEffect(() => {
    if (!isOpen) {
      setHighlightedIndex(-1);
    }
  }, [isOpen]);

  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    if (!isOpen) return;

    switch (event.key) {
      case 'ArrowDown':
        event.preventDefault();
        setHighlightedIndex((prev) => 
          prev < options.length - 1 ? prev + 1 : 0
        );
        break;
      case 'ArrowUp':
        event.preventDefault();
        setHighlightedIndex((prev) => 
          prev > 0 ? prev - 1 : options.length - 1
        );
        break;
      case 'Enter':
        event.preventDefault();
        if (highlightedIndex >= 0 && options[highlightedIndex]) {
          onSelect(options[highlightedIndex]);
        }
        break;
      case 'Escape':
        event.preventDefault();
        onClose();
        break;
    }
  }, [isOpen, options, highlightedIndex, onSelect, onClose]);

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  return highlightedIndex;
};

// ================================
// MAIN COMPONENT
// ================================

export const Dropdown: React.FC<DropdownProps> = ({
  options,
  value,
  onChange,
  placeholder = 'Select an option...',
  disabled = false,
  multiple = false,
  searchable = false,
  clearable = false,
  loading = false,
  error,
  required = false,
  size = 'medium',
  variant = 'default',
  position = 'auto',
  maxHeight = 200,
  renderOption,
  renderSelection,
  onSearch,
  onFocus,
  onBlur,
  className,
  'data-testid': testId,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [dropdownPosition, setDropdownPosition] = useState(position);
  
  const containerRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);

  // Filter options based on search query
  const filteredOptions = searchQuery
    ? options.filter(option =>
        option.label.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : options;

  // Handle click outside
  useClickOutside(containerRef, () => setIsOpen(false));

  // Handle keyboard navigation
  const highlightedIndex = useKeyboardNavigation(
    filteredOptions,
    isOpen,
    handleOptionSelect,
    () => setIsOpen(false)
  );

  // Handle option selection
  function handleOptionSelect(option: DropdownOption) {
    if (option.disabled) return;

    if (multiple) {
      const currentValues = Array.isArray(value) ? value : [];
      const newValues = currentValues.includes(option.value)
        ? currentValues.filter(v => v !== option.value)
        : [...currentValues, option.value];
      onChange?.(newValues);
    } else {
      onChange?.(option.value);
      setIsOpen(false);
    }
  }

  // Handle search
  const handleSearch = (query: string) => {
    setSearchQuery(query);
    onSearch?.(query);
  };

  // Get selected options
  const selectedOptions = options.filter(option => {
    if (multiple) {
      return Array.isArray(value) && value.includes(option.value);
    }
    return option.value === value;
  });

  // Handle clear
  const handleClear = (e: React.MouseEvent) => {
    e.stopPropagation();
    onChange?.(multiple ? [] : '');
    setSearchQuery('');
  };

  // Auto-position dropdown
  useEffect(() => {
    if (position === 'auto' && isOpen && containerRef.current) {
      const rect = containerRef.current.getBoundingClientRect();
      const spaceBelow = window.innerHeight - rect.bottom;
      const spaceAbove = rect.top;
      
      if (spaceBelow < maxHeight && spaceAbove > spaceBelow) {
        setDropdownPosition('top');
      } else {
        setDropdownPosition('bottom');
      }
    }
  }, [isOpen, position, maxHeight]);

  // Render trigger content
  const renderTriggerContent = () => {
    if (loading) {
      return (
        <>
          <span>Loading...</span>
          <LoadingSpinner />
        </>
      );
    }

    if (multiple && selectedOptions.length > 0) {
      return (
        <MultipleSelection>
          {selectedOptions.map(option => (
            <SelectionTag key={option.value}>
              {renderSelection ? renderSelection(option) : option.label}
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  handleOptionSelect(option);
                }}
                aria-label={`Remove ${option.label}`}
              >
                ×
              </button>
            </SelectionTag>
          ))}
        </MultipleSelection>
      );
    }

    if (!multiple && selectedOptions.length > 0) {
      const option = selectedOptions[0];
      return renderSelection ? renderSelection(option) : option.label;
    }

    return <span style={{ color: 'rgba(0, 0, 0, 0.5)' }}>{placeholder}</span>;
  };

  return (
    <DropdownContainer
      ref={containerRef}
      size={size}
      error={error}
      className={className}
      data-testid={testId}
    >
      <DropdownTrigger
        ref={triggerRef}
        type="button"
        variant={variant}
        size={size}
        isOpen={isOpen}
        hasError={!!error}
        disabled={disabled}
        onClick={() => !disabled && setIsOpen(!isOpen)}
        onFocus={onFocus}
        onBlur={onBlur}
        aria-expanded={isOpen}
        aria-haspopup="listbox"
        aria-required={required}
        aria-invalid={!!error}
      >
        {renderTriggerContent()}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {clearable && (multiple ? selectedOptions.length > 0 : value) && (
            <button
              type="button"
              onClick={handleClear}
              style={{
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                padding: '0',
                color: 'rgba(0, 0, 0, 0.5)',
              }}
              aria-label="Clear selection"
            >
              ×
            </button>
          )}
          <DropdownIcon isOpen={isOpen} />
        </div>
      </DropdownTrigger>

      <AnimatePresence>
        {isOpen && (
          <DropdownList
            initial={{ opacity: 0, scaleY: 0.95, y: -10 }}
            animate={{ opacity: 1, scaleY: 1, y: 0 }}
            exit={{ opacity: 0, scaleY: 0.95, y: -10 }}
            transition={{ duration: 0.15, ease: 'easeOut' }}
            maxHeight={maxHeight}
            position={dropdownPosition}
            role="listbox"
            aria-multiselectable={multiple}
          >
            {searchable && (
              <SearchInput
                type="text"
                placeholder="Search options..."
                value={searchQuery}
                onChange={(e) => handleSearch(e.target.value)}
                onClick={(e) => e.stopPropagation()}
              />
            )}
            
            {filteredOptions.length === 0 ? (
              <div style={{ padding: '12px 16px', color: 'rgba(0, 0, 0, 0.5)' }}>
                No options found
              </div>
            ) : (
              filteredOptions.map((option, index) => (
                <DropdownOption
                  key={option.value}
                  type="button"
                  isSelected={
                    multiple
                      ? Array.isArray(value) && value.includes(option.value)
                      : option.value === value
                  }
                  isHighlighted={index === highlightedIndex}
                  disabled={option.disabled}
                  onClick={() => handleOptionSelect(option)}
                  role="option"
                  aria-selected={
                    multiple
                      ? Array.isArray(value) && value.includes(option.value)
                      : option.value === value
                  }
                  aria-disabled={option.disabled}
                >
                  {option.icon && <span>{option.icon}</span>}
                  {renderOption ? renderOption(option) : option.label}
                </DropdownOption>
              ))
            )}
          </DropdownList>
        )}
      </AnimatePresence>

      {error && <ErrorMessage>{error}</ErrorMessage>}
    </DropdownContainer>
  );
};

// ================================
// VARIANTS & COMPOSITIONS
// ================================

export const SimpleDropdown: React.FC<Partial<DropdownProps>> = (props) => (
  <Dropdown variant="minimal" size="small" {...props} />
);

export const MultiSelectDropdown: React.FC<Partial<DropdownProps>> = (props) => (
  <Dropdown multiple searchable clearable {...props} />
);

export const SearchableDropdown: React.FC<Partial<DropdownProps>> = (props) => (
  <Dropdown searchable clearable {...props} />
);

// ================================
// EXPORTS
// ================================

export default Dropdown;

export type {
  DropdownProps,
  DropdownOption,
};

/**
 * 🎯 Example Usage:
 * 
 * ```tsx
 * const options = [
 *   { value: 'react', label: 'React', icon: '⚛️' },
 *   { value: 'vue', label: 'Vue.js', icon: '💚' },
 *   { value: 'angular', label: 'Angular', icon: '🅰️' },
 * ];
 * 
 * <Dropdown
 *   options={options}
 *   value={selectedValue}
 *   onChange={setSelectedValue}
 *   searchable
 *   clearable
 *   placeholder="Choose a framework..."
 * />
 * 
 * <MultiSelectDropdown
 *   options={options}
 *   value={selectedValues}
 *   onChange={setSelectedValues}
 *   placeholder="Choose frameworks..."
 * />
 * ```
 */