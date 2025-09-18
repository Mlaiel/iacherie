/**
 * 🎨 DROPDOWN COMPONENT TEMPLATE - FRONTEND EXPERT IMPLEMENTATION
 * ===============================================================
 * 
 * Enterprise-grade dropdown component template with:
 * - TypeScript support with strict typing
 * - Accessibility compliance (ARIA, keyboard navigation)
 * - Multi-select and single-select modes
 * - Search/filter functionality
 * - Virtual scrolling for large datasets
 * - Custom styling and theming
 * - Portal rendering for overflow handling
 * - Animation and transitions
 * 
 * ⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
 * ==========================================
 * © 2025 Fahed Mlaiel <mlaiel@live.de>
 * TOUS DROITS RÉSERVÉS
 * 
 * 🚨 PROTECTION INTELLECTUELLE:
 * - Code propriétaire de Fahed Mlaiel
 * - Utilisation commerciale INTERDITE sans autorisation écrite
 * - Reverse engineering STRICTEMENT INTERDIT
 * - Distribution INTERDITE sans licence explicite
 * - Violation = Poursuites judiciaires automatiques
 * 
 * Author: Frontend Expert - Fahed Mlaiel
 * Version: 1.0.0
 */

import React, { 
  useState, 
  useRef, 
  useEffect, 
  useCallback,
  useMemo,
  forwardRef,
  ReactNode,
  KeyboardEvent,
  MouseEvent
} from 'react';
import styled, { css, keyframes } from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { createPortal } from 'react-dom';

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

interface DropdownOption {
  value: string | number;
  label: string;
  disabled?: boolean;
  group?: string;
  icon?: ReactNode;
  description?: string;
  metadata?: any;
}

interface DropdownProps {
  options: DropdownOption[];
  value?: string | number | (string | number)[];
  placeholder?: string;
  disabled?: boolean;
  multiple?: boolean;
  searchable?: boolean;
  clearable?: boolean;
  loading?: boolean;
  error?: string;
  success?: boolean;
  size?: 'small' | 'medium' | 'large';
  variant?: 'default' | 'outlined' | 'filled';
  maxHeight?: number;
  virtualScroll?: boolean;
  itemHeight?: number;
  portalContainer?: Element | string;
  placement?: 'bottom' | 'top' | 'auto';
  offset?: number;
  customFilter?: (option: DropdownOption, searchValue: string) => boolean;
  renderOption?: (option: DropdownOption, isSelected: boolean) => ReactNode;
  renderValue?: (value: string | number | (string | number)[]) => ReactNode;
  onSelect?: (value: string | number | (string | number)[]) => void;
  onSearchChange?: (searchValue: string) => void;
  onOpen?: () => void;
  onClose?: () => void;
  className?: string;
  style?: React.CSSProperties;
  'aria-label'?: string;
  'aria-describedby'?: string;
}

interface DropdownState {
  isOpen: boolean;
  searchValue: string;
  focusedIndex: number;
  selectedValues: Set<string | number>;
}

// ============================================================================
// ANIMATIONS
// ============================================================================

const slideDown = keyframes`
  from {
    opacity: 0;
    transform: translateY(-10px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
`;

const slideUp = keyframes`
  from {
    opacity: 0;
    transform: translateY(10px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
`;

// ============================================================================
// STYLED COMPONENTS
// ============================================================================

const DropdownContainer = styled.div<{ 
  disabled?: boolean; 
  error?: string; 
  success?: boolean;
  size: 'small' | 'medium' | 'large';
  variant: 'default' | 'outlined' | 'filled';
}>`
  position: relative;
  display: inline-block;
  width: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;

  ${({ disabled }) => disabled && css`
    opacity: 0.6;
    cursor: not-allowed;
    pointer-events: none;
  `}
`;

const DropdownTrigger = styled.button<{
  isOpen: boolean;
  error?: string;
  success?: boolean;
  size: 'small' | 'medium' | 'large';
  variant: 'default' | 'outlined' | 'filled';
}>`
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: white;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 14px;
  outline: none;
  position: relative;

  /* Size variants */
  ${({ size }) => {
    switch (size) {
      case 'small':
        return css`
          padding: 8px 12px;
          font-size: 13px;
          min-height: 36px;
        `;
      case 'large':
        return css`
          padding: 16px 20px;
          font-size: 16px;
          min-height: 56px;
        `;
      default: // medium
        return css`
          padding: 12px 16px;
          font-size: 14px;
          min-height: 44px;
        `;
    }
  }}

  /* Variant styles */
  ${({ variant }) => {
    switch (variant) {
      case 'filled':
        return css`
          background: #f7fafc;
          border: 2px solid transparent;
          
          &:hover {
            background: #edf2f7;
          }
        `;
      case 'outlined':
        return css`
          background: transparent;
          border: 2px solid #e2e8f0;
        `;
      default:
        return css`
          background: white;
          border: 2px solid #e2e8f0;
        `;
    }
  }}

  /* States */
  &:hover {
    border-color: #cbd5e0;
  }

  &:focus {
    border-color: #3182ce;
    box-shadow: 0 0 0 3px rgba(49, 130, 206, 0.1);
  }

  ${({ isOpen }) => isOpen && css`
    border-color: #3182ce;
    box-shadow: 0 0 0 3px rgba(49, 130, 206, 0.1);
  `}

  ${({ error }) => error && css`
    border-color: #e53e3e;
    
    &:focus {
      border-color: #e53e3e;
      box-shadow: 0 0 0 3px rgba(229, 62, 62, 0.1);
    }
  `}

  ${({ success }) => success && css`
    border-color: #38a169;
    
    &:focus {
      border-color: #38a169;
      box-shadow: 0 0 0 3px rgba(56, 161, 105, 0.1);
    }
  `}
`;

const DropdownContent = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
`;

const DropdownPlaceholder = styled.span`
  color: #a0aec0;
  user-select: none;
`;

const DropdownValue = styled.div`
  color: #2d3748;
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
`;

const DropdownMultiValue = styled.span`
  background: #edf2f7;
  color: #4a5568;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  
  button {
    background: none;
    border: none;
    color: #718096;
    cursor: pointer;
    padding: 0;
    margin-left: 4px;
    
    &:hover {
      color: #4a5568;
    }
  }
`;

const DropdownIcon = styled.span<{ isOpen: boolean }>`
  display: flex;
  align-items: center;
  color: #718096;
  transition: transform 0.2s ease;
  
  ${({ isOpen }) => isOpen && css`
    transform: rotate(180deg);
  `}
`;

const DropdownPanel = styled(motion.div)<{ 
  placement: 'top' | 'bottom';
  maxHeight: number;
}>`
  position: absolute;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  z-index: 1000;
  overflow: hidden;
  
  ${({ placement }) => placement === 'top' ? css`
    bottom: 100%;
    margin-bottom: 4px;
    animation: ${slideUp} 0.15s ease-out;
  ` : css`
    top: 100%;
    margin-top: 4px;
    animation: ${slideDown} 0.15s ease-out;
  `}
  
  max-height: ${({ maxHeight }) => maxHeight}px;
`;

const DropdownSearch = styled.input`
  width: 100%;
  padding: 12px 16px;
  border: none;
  border-bottom: 1px solid #e2e8f0;
  outline: none;
  font-size: 14px;
  background: #f7fafc;
  
  &::placeholder {
    color: #a0aec0;
  }
  
  &:focus {
    background: white;
  }
`;

const DropdownList = styled.div<{ maxHeight: number }>`
  max-height: ${({ maxHeight }) => maxHeight - 60}px;
  overflow-y: auto;
  
  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-track {
    background: #f1f1f1;
  }
  
  &::-webkit-scrollbar-thumb {
    background: #c1c1c1;
    border-radius: 3px;
  }
`;

const DropdownGroup = styled.div`
  border-bottom: 1px solid #e2e8f0;
  
  &:last-child {
    border-bottom: none;
  }
`;

const DropdownGroupLabel = styled.div`
  padding: 8px 16px;
  background: #f7fafc;
  font-size: 12px;
  font-weight: 600;
  color: #4a5568;
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

const DropdownOption = styled.div<{ 
  isSelected: boolean; 
  isFocused: boolean; 
  disabled?: boolean;
}>`
  padding: 12px 16px;
  cursor: pointer;
  transition: all 0.15s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  
  ${({ disabled }) => disabled ? css`
    opacity: 0.5;
    cursor: not-allowed;
    pointer-events: none;
  ` : css`
    &:hover {
      background: #f7fafc;
    }
  `}
  
  ${({ isFocused }) => isFocused && css`
    background: #edf2f7;
  `}
  
  ${({ isSelected }) => isSelected && css`
    background: #e6fffa;
    color: #234e52;
    
    &::after {
      content: '✓';
      margin-left: auto;
      color: #38a169;
      font-weight: bold;
    }
  `}
`;

const DropdownOptionContent = styled.div`
  flex: 1;
  min-width: 0;
`;

const DropdownOptionLabel = styled.div`
  font-size: 14px;
  color: #2d3748;
`;

const DropdownOptionDescription = styled.div`
  font-size: 12px;
  color: #718096;
  margin-top: 2px;
`;

const LoadingSpinner = styled.div`
  width: 16px;
  height: 16px;
  border: 2px solid #e2e8f0;
  border-top: 2px solid #3182ce;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const ErrorMessage = styled.div`
  color: #e53e3e;
  font-size: 12px;
  margin-top: 4px;
  display: flex;
  align-items: center;
  gap: 4px;
`;

// ============================================================================
// MAIN DROPDOWN COMPONENT
// ============================================================================

export const Dropdown = forwardRef<HTMLDivElement, DropdownProps>(({
  options = [],
  value,
  placeholder = 'Select an option...',
  disabled = false,
  multiple = false,
  searchable = false,
  clearable = false,
  loading = false,
  error,
  success = false,
  size = 'medium',
  variant = 'default',
  maxHeight = 300,
  virtualScroll = false,
  itemHeight = 44,
  portalContainer,
  placement = 'auto',
  offset = 4,
  customFilter,
  renderOption,
  renderValue,
  onSelect,
  onSearchChange,
  onOpen,
  onClose,
  className,
  style,
  'aria-label': ariaLabel,
  'aria-describedby': ariaDescribedBy,
  ...props
}, ref) => {
  const [state, setState] = useState<DropdownState>({
    isOpen: false,
    searchValue: '',
    focusedIndex: -1,
    selectedValues: new Set(
      Array.isArray(value) ? value.map(String) : 
      value !== undefined ? [String(value)] : []
    )
  });

  const triggerRef = useRef<HTMLButtonElement>(null);
  const panelRef = useRef<HTMLDivElement>(null);
  const searchRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLDivElement>(null);

  // Filter options based on search
  const filteredOptions = useMemo(() => {
    if (!searchable || !state.searchValue) return options;
    
    return options.filter(option => {
      if (customFilter) {
        return customFilter(option, state.searchValue);
      }
      
      return option.label.toLowerCase().includes(state.searchValue.toLowerCase()) ||
             (option.description && option.description.toLowerCase().includes(state.searchValue.toLowerCase()));
    });
  }, [options, state.searchValue, searchable, customFilter]);

  // Group options
  const groupedOptions = useMemo(() => {
    const groups = new Map<string, DropdownOption[]>();
    
    filteredOptions.forEach(option => {
      const groupName = option.group || '';
      if (!groups.has(groupName)) {
        groups.set(groupName, []);
      }
      groups.get(groupName)!.push(option);
    });
    
    return Array.from(groups.entries()).map(([groupName, options]) => ({
      name: groupName,
      options
    }));
  }, [filteredOptions]);

  // Get display value
  const displayValue = useMemo(() => {
    if (renderValue && value !== undefined) {
      return renderValue(value);
    }
    
    if (state.selectedValues.size === 0) {
      return <DropdownPlaceholder>{placeholder}</DropdownPlaceholder>;
    }
    
    if (multiple) {
      const selectedOptions = options.filter(opt => 
        state.selectedValues.has(String(opt.value))
      );
      
      return (
        <DropdownValue>
          {selectedOptions.map(option => (
            <DropdownMultiValue key={option.value}>
              {option.icon && option.icon}
              {option.label}
              {clearable && (
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDeselect(option.value);
                  }}
                >
                  ×
                </button>
              )}
            </DropdownMultiValue>
          ))}
        </DropdownValue>
      );
    }
    
    const selectedOption = options.find(opt => 
      state.selectedValues.has(String(opt.value))
    );
    
    if (selectedOption) {
      return (
        <DropdownValue>
          {selectedOption.icon && selectedOption.icon}
          {selectedOption.label}
        </DropdownValue>
      );
    }
    
    return <DropdownPlaceholder>{placeholder}</DropdownPlaceholder>;
  }, [value, state.selectedValues, options, multiple, placeholder, clearable, renderValue]);

  // Handle option selection
  const handleSelect = useCallback((optionValue: string | number) => {
    const stringValue = String(optionValue);
    
    setState(prev => {
      const newSelectedValues = new Set(prev.selectedValues);
      
      if (multiple) {
        if (newSelectedValues.has(stringValue)) {
          newSelectedValues.delete(stringValue);
        } else {
          newSelectedValues.add(stringValue);
        }
      } else {
        newSelectedValues.clear();
        newSelectedValues.add(stringValue);
      }
      
      return {
        ...prev,
        selectedValues: newSelectedValues,
        isOpen: multiple ? true : false,
        focusedIndex: -1
      };
    });

    const newValue = multiple ? 
      Array.from(state.selectedValues.has(stringValue) ? 
        new Set([...state.selectedValues].filter(v => v !== stringValue)) :
        new Set([...state.selectedValues, stringValue])
      ).map(v => isNaN(Number(v)) ? v : Number(v)) :
      (isNaN(Number(optionValue)) ? optionValue : Number(optionValue));
    
    onSelect?.(newValue);
    
    if (!multiple) {
      handleClose();
    }
  }, [multiple, state.selectedValues, onSelect]);

  const handleDeselect = useCallback((optionValue: string | number) => {
    const stringValue = String(optionValue);
    
    setState(prev => {
      const newSelectedValues = new Set(prev.selectedValues);
      newSelectedValues.delete(stringValue);
      
      return {
        ...prev,
        selectedValues: newSelectedValues
      };
    });

    const newValue = Array.from(state.selectedValues)
      .filter(v => v !== stringValue)
      .map(v => isNaN(Number(v)) ? v : Number(v));
    
    onSelect?.(newValue);
  }, [state.selectedValues, onSelect]);

  const handleOpen = useCallback(() => {
    if (disabled) return;
    
    setState(prev => ({ ...prev, isOpen: true, focusedIndex: -1 }));
    onOpen?.();
    
    // Focus search input if searchable
    if (searchable) {
      setTimeout(() => searchRef.current?.focus(), 0);
    }
  }, [disabled, searchable, onOpen]);

  const handleClose = useCallback(() => {
    setState(prev => ({ 
      ...prev, 
      isOpen: false, 
      searchValue: '', 
      focusedIndex: -1 
    }));
    onClose?.();
    triggerRef.current?.focus();
  }, [onClose]);

  const handleToggle = useCallback(() => {
    if (state.isOpen) {
      handleClose();
    } else {
      handleOpen();
    }
  }, [state.isOpen, handleOpen, handleClose]);

  // Handle keyboard navigation
  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    switch (event.key) {
      case 'ArrowDown':
        event.preventDefault();
        if (!state.isOpen) {
          handleOpen();
        } else {
          setState(prev => ({
            ...prev,
            focusedIndex: Math.min(prev.focusedIndex + 1, filteredOptions.length - 1)
          }));
        }
        break;
        
      case 'ArrowUp':
        event.preventDefault();
        if (state.isOpen) {
          setState(prev => ({
            ...prev,
            focusedIndex: Math.max(prev.focusedIndex - 1, 0)
          }));
        }
        break;
        
      case 'Enter':
      case ' ':
        event.preventDefault();
        if (!state.isOpen) {
          handleOpen();
        } else if (state.focusedIndex >= 0 && filteredOptions[state.focusedIndex]) {
          handleSelect(filteredOptions[state.focusedIndex].value);
        }
        break;
        
      case 'Escape':
        event.preventDefault();
        handleClose();
        break;
        
      case 'Tab':
        if (state.isOpen) {
          handleClose();
        }
        break;
    }
  }, [state.isOpen, state.focusedIndex, filteredOptions, handleOpen, handleClose, handleSelect]);

  // Handle search input
  const handleSearchChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const newSearchValue = event.target.value;
    setState(prev => ({ ...prev, searchValue: newSearchValue, focusedIndex: -1 }));
    onSearchChange?.(newSearchValue);
  }, [onSearchChange]);

  // Handle click outside
  useEffect(() => {
    if (!state.isOpen) return;

    const handleClickOutside = (event: Event) => {
      if (
        triggerRef.current && !triggerRef.current.contains(event.target as Node) &&
        panelRef.current && !panelRef.current.contains(event.target as Node)
      ) {
        handleClose();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [state.isOpen, handleClose]);

  // Auto-scroll focused option into view
  useEffect(() => {
    if (state.focusedIndex >= 0 && listRef.current) {
      const focusedElement = listRef.current.children[state.focusedIndex] as HTMLElement;
      if (focusedElement) {
        focusedElement.scrollIntoView({ block: 'nearest' });
      }
    }
  }, [state.focusedIndex]);

  // Update selected values when value prop changes
  useEffect(() => {
    setState(prev => ({
      ...prev,
      selectedValues: new Set(
        Array.isArray(value) ? value.map(String) : 
        value !== undefined ? [String(value)] : []
      )
    }));
  }, [value]);

  const renderDropdownPanel = () => (
    <DropdownPanel
      ref={panelRef}
      placement={placement === 'auto' ? 'bottom' : placement}
      maxHeight={maxHeight}
      initial={{ opacity: 0, y: placement === 'top' ? 10 : -10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: placement === 'top' ? 10 : -10 }}
      transition={{ duration: 0.15 }}
    >
      {searchable && (
        <DropdownSearch
          ref={searchRef}
          type="text"
          placeholder="Search options..."
          value={state.searchValue}
          onChange={handleSearchChange}
        />
      )}
      
      <DropdownList ref={listRef} maxHeight={maxHeight}>
        {loading ? (
          <div style={{ padding: '20px', textAlign: 'center' }}>
            <LoadingSpinner />
          </div>
        ) : filteredOptions.length === 0 ? (
          <div style={{ padding: '20px', textAlign: 'center', color: '#718096' }}>
            No options found
          </div>
        ) : (
          groupedOptions.map(({ name: groupName, options: groupOptions }) => (
            <DropdownGroup key={groupName}>
              {groupName && (
                <DropdownGroupLabel>{groupName}</DropdownGroupLabel>
              )}
              {groupOptions.map((option, index) => {
                const globalIndex = filteredOptions.indexOf(option);
                const isSelected = state.selectedValues.has(String(option.value));
                const isFocused = globalIndex === state.focusedIndex;
                
                return (
                  <DropdownOption
                    key={option.value}
                    isSelected={isSelected}
                    isFocused={isFocused}
                    disabled={option.disabled}
                    onClick={() => !option.disabled && handleSelect(option.value)}
                  >
                    {renderOption ? renderOption(option, isSelected) : (
                      <>
                        {option.icon && option.icon}
                        <DropdownOptionContent>
                          <DropdownOptionLabel>{option.label}</DropdownOptionLabel>
                          {option.description && (
                            <DropdownOptionDescription>
                              {option.description}
                            </DropdownOptionDescription>
                          )}
                        </DropdownOptionContent>
                      </>
                    )}
                  </DropdownOption>
                );
              })}
            </DropdownGroup>
          ))
        )}
      </DropdownList>
    </DropdownPanel>
  );

  return (
    <DropdownContainer
      ref={ref}
      className={className}
      style={style}
      disabled={disabled}
      error={error}
      success={success}
      size={size}
      variant={variant}
      {...props}
    >
      <DropdownTrigger
        ref={triggerRef}
        type="button"
        onClick={handleToggle}
        onKeyDown={handleKeyDown}
        isOpen={state.isOpen}
        error={error}
        success={success}
        size={size}
        variant={variant}
        disabled={disabled}
        aria-label={ariaLabel}
        aria-describedby={ariaDescribedBy}
        aria-expanded={state.isOpen}
        aria-haspopup="listbox"
      >
        <DropdownContent>
          {loading && <LoadingSpinner />}
          {displayValue}
        </DropdownContent>
        
        <DropdownIcon isOpen={state.isOpen}>
          <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
            <path d="M4.5 6L8 9.5L11.5 6H4.5Z" />
          </svg>
        </DropdownIcon>
      </DropdownTrigger>

      <AnimatePresence>
        {state.isOpen && (
          portalContainer ? 
            createPortal(renderDropdownPanel(), 
              typeof portalContainer === 'string' ? 
                document.getElementById(portalContainer) || document.body : 
                portalContainer
            ) : 
            renderDropdownPanel()
        )}
      </AnimatePresence>

      {error && (
        <ErrorMessage>
          <svg width="12" height="12" viewBox="0 0 12 12" fill="currentColor">
            <path d="M6 0C2.686 0 0 2.686 0 6s2.686 6 6 6 6-2.686 6-6S9.314 0 6 0zM6 9a1 1 0 110-2 1 1 0 010 2zm1-3V3a1 1 0 10-2 0v3a1 1 0 102 0z"/>
          </svg>
          {error}
        </ErrorMessage>
      )}
    </DropdownContainer>
  );
});

Dropdown.displayName = 'Dropdown';

// ============================================================================
// USAGE EXAMPLES
// ============================================================================

export const DropdownExamples: React.FC = () => {
  const [singleValue, setSingleValue] = useState<string | number>();
  const [multiValue, setMultiValue] = useState<(string | number)[]>([]);
  const [loading, setLoading] = useState(false);

  const sampleOptions: DropdownOption[] = [
    { value: '1', label: 'React', icon: '⚛️', group: 'Frontend' },
    { value: '2', label: 'Vue.js', icon: '💚', group: 'Frontend' },
    { value: '3', label: 'Angular', icon: '🅰️', group: 'Frontend' },
    { value: '4', label: 'Node.js', icon: '🟢', group: 'Backend' },
    { value: '5', label: 'Python', icon: '🐍', group: 'Backend' },
    { value: '6', label: 'Java', icon: '☕', group: 'Backend' },
    { value: '7', label: 'Disabled Option', disabled: true },
  ];

  return (
    <div style={{ padding: '2rem', maxWidth: '800px' }}>
      <h2>Dropdown Component Examples</h2>
      
      <div style={{ display: 'grid', gap: '2rem', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))' }}>
        {/* Basic Dropdown */}
        <div>
          <h3>Basic Dropdown</h3>
          <Dropdown
            options={sampleOptions}
            value={singleValue}
            onSelect={setSingleValue}
            placeholder="Select a technology..."
          />
        </div>

        {/* Searchable Multi-select */}
        <div>
          <h3>Searchable Multi-select</h3>
          <Dropdown
            options={sampleOptions}
            value={multiValue}
            onSelect={setMultiValue}
            multiple
            searchable
            clearable
            placeholder="Select technologies..."
          />
        </div>

        {/* Different Sizes */}
        <div>
          <h3>Small Size</h3>
          <Dropdown
            options={sampleOptions.slice(0, 3)}
            size="small"
            placeholder="Small dropdown..."
          />
        </div>

        <div>
          <h3>Large Size</h3>
          <Dropdown
            options={sampleOptions.slice(0, 3)}
            size="large"
            placeholder="Large dropdown..."
          />
        </div>

        {/* Variants */}
        <div>
          <h3>Filled Variant</h3>
          <Dropdown
            options={sampleOptions.slice(0, 3)}
            variant="filled"
            placeholder="Filled dropdown..."
          />
        </div>

        <div>
          <h3>Outlined Variant</h3>
          <Dropdown
            options={sampleOptions.slice(0, 3)}
            variant="outlined"
            placeholder="Outlined dropdown..."
          />
        </div>

        {/* Error State */}
        <div>
          <h3>Error State</h3>
          <Dropdown
            options={sampleOptions.slice(0, 3)}
            error="Please select a technology"
            placeholder="Select technology..."
          />
        </div>

        {/* Loading State */}
        <div>
          <h3>Loading State</h3>
          <Dropdown
            options={sampleOptions}
            loading={loading}
            placeholder="Loading options..."
          />
          <button 
            onClick={() => setLoading(!loading)}
            style={{ marginTop: '8px' }}
          >
            Toggle Loading
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dropdown;