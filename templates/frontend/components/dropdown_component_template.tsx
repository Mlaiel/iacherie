/**
 * 📋 Dropdown Component Template - Enterprise Dropdown/Select
 * ==========================================================
 * 
 * © 2025 Fahed Mlaiel <mlaiel@live.de>
 * TOUS DROITS RÉSERVÉS - Propriété Intellectuelle Protégée
 * 
 * Enterprise-grade dropdown and select components with advanced features:
 * multi-select, search, virtualization, accessibility, and keyboard navigation.
 * 
 * AVERTISSEMENT LÉGAL:
 * - Code propriétaire de Fahed Mlaiel
 * - Utilisation commerciale INTERDITE sans autorisation écrite
 * - Reverse engineering STRICTEMENT INTERDIT
 * - Distribution INTERDITE sans licence explicite
 * - Violation = Poursuites judiciaires automatiques
 */

import React, { 
  useState, 
  useEffect, 
  useRef, 
  useCallback, 
  useMemo,
  forwardRef,
  useImperativeHandle
} from 'react';

// ========================================
// 📝 TYPE DEFINITIONS
// ========================================

interface DropdownOption {
  value: string | number;
  label: string;
  disabled?: boolean;
  description?: string;
  icon?: React.ReactNode;
  group?: string;
  metadata?: Record<string, any>;
}

interface DropdownProps {
  options: DropdownOption[];
  value?: string | number | (string | number)[];
  defaultValue?: string | number | (string | number)[];
  placeholder?: string;
  multiple?: boolean;
  searchable?: boolean;
  clearable?: boolean;
  disabled?: boolean;
  loading?: boolean;
  error?: string;
  maxHeight?: string;
  maxSelections?: number;
  minSelections?: number;
  virtual?: boolean;
  itemHeight?: number;
  onChange?: (value: string | number | (string | number)[] | null) => void;
  onSearch?: (query: string) => void;
  onOpen?: () => void;
  onClose?: () => void;
  onClear?: () => void;
  renderOption?: (option: DropdownOption, isSelected: boolean) => React.ReactNode;
  renderValue?: (values: DropdownOption[]) => React.ReactNode;
  className?: string;
  dropdownClassName?: string;
  optionClassName?: string;
  size?: 'small' | 'medium' | 'large';
  variant?: 'default' | 'outlined' | 'filled';
  testId?: string;
}

interface DropdownRef {
  open: () => void;
  close: () => void;
  toggle: () => void;
  focus: () => void;
  clear: () => void;
  getValue: () => string | number | (string | number)[] | null;
}

// ========================================
// 🎨 STYLED COMPONENTS & THEME
// ========================================

const getDropdownStyles = (
  size: string,
  variant: string,
  isOpen: boolean,
  hasError: boolean,
  disabled: boolean
) => ({
  trigger: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    width: '100%',
    padding: size === 'small' ? '0.375rem 0.75rem' : 
             size === 'large' ? '0.75rem 1rem' : '0.5rem 0.75rem',
    fontSize: size === 'small' ? '0.875rem' : 
              size === 'large' ? '1.125rem' : '1rem',
    lineHeight: '1.5',
    color: disabled ? '#9CA3AF' : '#374151',
    backgroundColor: variant === 'filled' ? '#F3F4F6' : '#FFFFFF',
    border: variant === 'outlined' ? 
      `2px solid ${hasError ? '#EF4444' : isOpen ? '#3B82F6' : '#D1D5DB'}` :
      variant === 'filled' ? 'none' : `1px solid ${hasError ? '#EF4444' : '#D1D5DB'}`,
    borderRadius: '0.375rem',
    cursor: disabled ? 'not-allowed' : 'pointer',
    transition: 'all 0.2s ease-in-out',
    outline: 'none',
    minHeight: size === 'small' ? '2rem' : 
               size === 'large' ? '3rem' : '2.5rem',
    opacity: disabled ? 0.5 : 1,
    ...(isOpen && !disabled && {
      borderColor: '#3B82F6',
      boxShadow: '0 0 0 3px rgba(59, 130, 246, 0.1)'
    })
  } as React.CSSProperties,

  dropdown: {
    position: 'absolute' as const,
    top: '100%',
    left: 0,
    right: 0,
    zIndex: 1000,
    marginTop: '0.25rem',
    backgroundColor: '#FFFFFF',
    border: '1px solid #D1D5DB',
    borderRadius: '0.375rem',
    boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    overflow: 'hidden'
  } as React.CSSProperties,

  search: {
    width: '100%',
    padding: '0.5rem 0.75rem',
    border: 'none',
    borderBottom: '1px solid #E5E7EB',
    fontSize: '0.875rem',
    outline: 'none',
    backgroundColor: '#F9FAFB'
  } as React.CSSProperties,

  optionsList: {
    maxHeight: '200px',
    overflowY: 'auto' as const,
    padding: '0.25rem 0'
  } as React.CSSProperties,

  option: {
    display: 'flex',
    alignItems: 'center',
    padding: '0.5rem 0.75rem',
    fontSize: '0.875rem',
    cursor: 'pointer',
    transition: 'background-color 0.15s ease-in-out',
    borderBottom: '1px solid transparent'
  } as React.CSSProperties,

  loading: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '1rem',
    color: '#6B7280',
    fontSize: '0.875rem'
  } as React.CSSProperties
});

// ========================================
// 🎭 DROPDOWN COMPONENT
// ========================================

export const Dropdown = forwardRef<DropdownRef, DropdownProps>(({
  options = [],
  value,
  defaultValue,
  placeholder = 'Select an option...',
  multiple = false,
  searchable = false,
  clearable = false,
  disabled = false,
  loading = false,
  error,
  maxHeight = '200px',
  maxSelections,
  minSelections,
  virtual = false,
  itemHeight = 40,
  onChange,
  onSearch,
  onOpen,
  onClose,
  onClear,
  renderOption,
  renderValue,
  className = '',
  dropdownClassName = '',
  optionClassName = '',
  size = 'medium',
  variant = 'default',
  testId = 'dropdown'
}, ref) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedValues, setSelectedValues] = useState<(string | number)[]>(() => {
    const initialValue = value !== undefined ? value : defaultValue;
    if (initialValue === null || initialValue === undefined) return [];
    return Array.isArray(initialValue) ? initialValue : [initialValue];
  });
  const [focusedIndex, setFocusedIndex] = useState(-1);

  const triggerRef = useRef<HTMLDivElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);
  const optionsRef = useRef<HTMLDivElement>(null);

  // Filtered options based on search
  const filteredOptions = useMemo(() => {
    if (!searchQuery.trim()) return options;
    
    return options.filter(option => 
      option.label.toLowerCase().includes(searchQuery.toLowerCase()) ||
      option.description?.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [options, searchQuery]);

  // Grouped options
  const groupedOptions = useMemo(() => {
    const groups: { [key: string]: DropdownOption[] } = {};
    const ungrouped: DropdownOption[] = [];

    filteredOptions.forEach(option => {
      if (option.group) {
        if (!groups[option.group]) groups[option.group] = [];
        groups[option.group].push(option);
      } else {
        ungrouped.push(option);
      }
    });

    return { groups, ungrouped };
  }, [filteredOptions]);

  // Selected options
  const selectedOptions = useMemo(() => {
    return options.filter(option => selectedValues.includes(option.value));
  }, [options, selectedValues]);

  // Update selected values when value prop changes
  useEffect(() => {
    if (value !== undefined) {
      const newValues = value === null || value === undefined ? [] :
                       Array.isArray(value) ? value : [value];
      setSelectedValues(newValues);
    }
  }, [value]);

  // Handle click outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current && 
        !dropdownRef.current.contains(event.target as Node) &&
        triggerRef.current &&
        !triggerRef.current.contains(event.target as Node)
      ) {
        handleClose();
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isOpen]);

  // Handle keyboard navigation
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (!isOpen) return;

      switch (event.key) {
        case 'Escape':
          event.preventDefault();
          handleClose();
          break;
        case 'ArrowDown':
          event.preventDefault();
          setFocusedIndex(prev => 
            prev < filteredOptions.length - 1 ? prev + 1 : 0
          );
          break;
        case 'ArrowUp':
          event.preventDefault();
          setFocusedIndex(prev => 
            prev > 0 ? prev - 1 : filteredOptions.length - 1
          );
          break;
        case 'Enter':
          event.preventDefault();
          if (focusedIndex >= 0 && focusedIndex < filteredOptions.length) {
            handleOptionSelect(filteredOptions[focusedIndex]);
          }
          break;
        case 'Tab':
          handleClose();
          break;
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown);
      return () => document.removeEventListener('keydown', handleKeyDown);
    }
  }, [isOpen, focusedIndex, filteredOptions]);

  const handleOpen = useCallback(() => {
    if (disabled) return;
    setIsOpen(true);
    setFocusedIndex(-1);
    onOpen?.();
    
    // Focus search input if searchable
    setTimeout(() => {
      if (searchable && searchInputRef.current) {
        searchInputRef.current.focus();
      }
    }, 100);
  }, [disabled, searchable, onOpen]);

  const handleClose = useCallback(() => {
    setIsOpen(false);
    setSearchQuery('');
    setFocusedIndex(-1);
    onClose?.();
  }, [onClose]);

  const handleToggle = useCallback(() => {
    if (isOpen) {
      handleClose();
    } else {
      handleOpen();
    }
  }, [isOpen, handleOpen, handleClose]);

  const handleOptionSelect = useCallback((option: DropdownOption) => {
    if (option.disabled) return;

    let newValues: (string | number)[];

    if (multiple) {
      const isSelected = selectedValues.includes(option.value);
      
      if (isSelected) {
        // Check minimum selections
        if (minSelections && selectedValues.length <= minSelections) {
          return;
        }
        newValues = selectedValues.filter(v => v !== option.value);
      } else {
        // Check maximum selections
        if (maxSelections && selectedValues.length >= maxSelections) {
          return;
        }
        newValues = [...selectedValues, option.value];
      }
    } else {
      newValues = [option.value];
      handleClose();
    }

    setSelectedValues(newValues);
    
    const finalValue = multiple ? newValues : newValues[0] || null;
    onChange?.(finalValue);
  }, [
    multiple, 
    selectedValues, 
    maxSelections, 
    minSelections, 
    onChange, 
    handleClose
  ]);

  const handleClear = useCallback((event: React.MouseEvent) => {
    event.stopPropagation();
    setSelectedValues([]);
    onChange?.(multiple ? [] : null);
    onClear?.();
  }, [multiple, onChange, onClear]);

  const handleSearchChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const query = event.target.value;
    setSearchQuery(query);
    setFocusedIndex(-1);
    onSearch?.(query);
  }, [onSearch]);

  // Expose methods via ref
  useImperativeHandle(ref, () => ({
    open: handleOpen,
    close: handleClose,
    toggle: handleToggle,
    focus: () => triggerRef.current?.focus(),
    clear: () => {
      setSelectedValues([]);
      onChange?.(multiple ? [] : null);
    },
    getValue: () => multiple ? selectedValues : selectedValues[0] || null
  }), [handleOpen, handleClose, handleToggle, selectedValues, multiple, onChange]);

  const styles = getDropdownStyles(size, variant, isOpen, !!error, disabled);

  const renderTriggerContent = () => {
    if (selectedOptions.length === 0) {
      return <span style={{ color: '#9CA3AF' }}>{placeholder}</span>;
    }

    if (renderValue) {
      return renderValue(selectedOptions);
    }

    if (multiple) {
      if (selectedOptions.length === 1) {
        return selectedOptions[0].label;
      }
      return `${selectedOptions.length} selected`;
    }

    return selectedOptions[0]?.label;
  };

  const renderOptionItem = (option: DropdownOption, index: number) => {
    const isSelected = selectedValues.includes(option.value);
    const isFocused = focusedIndex === index;

    const optionStyle = {
      ...styles.option,
      backgroundColor: isFocused ? '#EBF4FF' : 
                      isSelected ? '#DBEAFE' : 'transparent',
      color: option.disabled ? '#9CA3AF' : '#374151',
      cursor: option.disabled ? 'not-allowed' : 'pointer',
      opacity: option.disabled ? 0.5 : 1
    };

    const content = renderOption ? 
      renderOption(option, isSelected) : (
        <div style={{ display: 'flex', alignItems: 'center', width: '100%' }}>
          {multiple && (
            <input
              type="checkbox"
              checked={isSelected}
              onChange={() => {}}
              style={{ marginRight: '0.5rem' }}
              tabIndex={-1}
            />
          )}
          {option.icon && (
            <span style={{ marginRight: '0.5rem' }}>{option.icon}</span>
          )}
          <div style={{ flex: 1 }}>
            <div>{option.label}</div>
            {option.description && (
              <div style={{ 
                fontSize: '0.75rem', 
                color: '#6B7280', 
                marginTop: '0.125rem' 
              }}>
                {option.description}
              </div>
            )}
          </div>
          {!multiple && isSelected && (
            <span style={{ color: '#3B82F6' }}>✓</span>
          )}
        </div>
      );

    return (
      <div
        key={option.value}
        className={optionClassName}
        style={optionStyle}
        onClick={() => handleOptionSelect(option)}
        onMouseEnter={() => setFocusedIndex(index)}
        role="option"
        aria-selected={isSelected}
        aria-disabled={option.disabled}
      >
        {content}
      </div>
    );
  };

  const renderOptions = () => {
    if (loading) {
      return (
        <div style={styles.loading}>
          <div style={{ 
            width: '16px', 
            height: '16px', 
            border: '2px solid #E5E7EB',
            borderTopColor: '#3B82F6',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            marginRight: '0.5rem'
          }} />
          Loading...
        </div>
      );
    }

    if (filteredOptions.length === 0) {
      return (
        <div style={styles.loading}>
          {searchQuery ? 'No results found' : 'No options available'}
        </div>
      );
    }

    const { groups, ungrouped } = groupedOptions;

    return (
      <div style={{ ...styles.optionsList, maxHeight }}>
        {ungrouped.map((option, index) => renderOptionItem(option, index))}
        
        {Object.entries(groups).map(([groupName, groupOptions]) => (
          <div key={groupName}>
            <div style={{ 
              padding: '0.5rem 0.75rem',
              fontSize: '0.75rem',
              fontWeight: '600',
              color: '#6B7280',
              textTransform: 'uppercase',
              backgroundColor: '#F9FAFB',
              borderTop: '1px solid #E5E7EB'
            }}>
              {groupName}
            </div>
            {groupOptions.map((option, index) => 
              renderOptionItem(option, ungrouped.length + index)
            )}
          </div>
        ))}
      </div>
    );
  };

  return (
    <div 
      className={className}
      style={{ position: 'relative', width: '100%' }}
      data-testid={testId}
    >
      <div
        ref={triggerRef}
        style={styles.trigger}
        onClick={handleToggle}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            handleToggle();
          }
        }}
        tabIndex={disabled ? -1 : 0}
        role="combobox"
        aria-expanded={isOpen}
        aria-haspopup="listbox"
        aria-disabled={disabled}
        aria-invalid={!!error}
        aria-describedby={error ? `${testId}-error` : undefined}
      >
        <div style={{ flex: 1, minWidth: 0 }}>
          {renderTriggerContent()}
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          {clearable && selectedValues.length > 0 && !disabled && (
            <button
              type="button"
              onClick={handleClear}
              style={{
                background: 'none',
                border: 'none',
                color: '#6B7280',
                cursor: 'pointer',
                padding: '0.125rem',
                borderRadius: '0.125rem'
              }}
              aria-label="Clear selection"
            >
              ✕
            </button>
          )}
          
          <div style={{ 
            transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)',
            transition: 'transform 0.2s ease-in-out',
            color: '#6B7280'
          }}>
            ▼
          </div>
        </div>
      </div>

      {isOpen && (
        <div
          ref={dropdownRef}
          className={dropdownClassName}
          style={styles.dropdown}
          role="listbox"
          aria-multiselectable={multiple}
        >
          {searchable && (
            <input
              ref={searchInputRef}
              type="text"
              placeholder="Search..."
              value={searchQuery}
              onChange={handleSearchChange}
              style={styles.search}
              autoComplete="off"
            />
          )}
          
          <div ref={optionsRef}>
            {renderOptions()}
          </div>
        </div>
      )}

      {error && (
        <div 
          id={`${testId}-error`}
          style={{ 
            marginTop: '0.25rem',
            fontSize: '0.875rem',
            color: '#EF4444'
          }}
        >
          {error}
        </div>
      )}
    </div>
  );
});

Dropdown.displayName = 'Dropdown';

// ========================================
// 🎯 SPECIALIZED DROPDOWN VARIANTS
// ========================================

export const SingleSelect = forwardRef<DropdownRef, Omit<DropdownProps, 'multiple'>>(
  (props, ref) => <Dropdown {...props} multiple={false} ref={ref} />
);

export const MultiSelect = forwardRef<DropdownRef, Omit<DropdownProps, 'multiple'>>(
  (props, ref) => <Dropdown {...props} multiple={true} ref={ref} />
);

export const SearchableSelect = forwardRef<DropdownRef, Omit<DropdownProps, 'searchable'>>(
  (props, ref) => <Dropdown {...props} searchable={true} ref={ref} />
);

export const CreatableSelect: React.FC<DropdownProps & {
  onCreate?: (value: string) => void;
  allowCreate?: boolean;
}> = ({ onCreate, allowCreate = true, onSearch, ...props }) => {
  const [customOptions, setCustomOptions] = useState<DropdownOption[]>([]);

  const handleSearch = useCallback((query: string) => {
    onSearch?.(query);
    
    if (allowCreate && query.trim() && !props.options.some(opt => 
      opt.label.toLowerCase() === query.toLowerCase()
    )) {
      const createOption: DropdownOption = {
        value: `create:${query}`,
        label: `Create "${query}"`,
        metadata: { isCreatable: true, originalQuery: query }
      };
      setCustomOptions([createOption]);
    } else {
      setCustomOptions([]);
    }
  }, [onSearch, allowCreate, props.options]);

  const handleChange = useCallback((value: any) => {
    if (Array.isArray(value)) {
      const createValues = value.filter(v => String(v).startsWith('create:'));
      createValues.forEach(v => {
        const query = String(v).replace('create:', '');
        onCreate?.(query);
      });
      
      const realValues = value.filter(v => !String(v).startsWith('create:'));
      props.onChange?.(realValues);
    } else if (String(value).startsWith('create:')) {
      const query = String(value).replace('create:', '');
      onCreate?.(query);
    } else {
      props.onChange?.(value);
    }
  }, [onCreate, props.onChange]);

  return (
    <Dropdown
      {...props}
      options={[...props.options, ...customOptions]}
      onSearch={handleSearch}
      onChange={handleChange}
    />
  );
};

// ========================================
// 📦 EXPORTS
// ========================================

export {
  Dropdown as default,
  SingleSelect,
  MultiSelect,
  SearchableSelect,
  CreatableSelect
};

export type {
  DropdownProps,
  DropdownOption,
  DropdownRef
};

// ========================================
// 🎯 USAGE EXAMPLES
// ========================================

/*
// Basic Dropdown
<Dropdown
  options={[
    { value: 'option1', label: 'Option 1' },
    { value: 'option2', label: 'Option 2' },
    { value: 'option3', label: 'Option 3', disabled: true }
  ]}
  value={selectedValue}
  onChange={setSelectedValue}
  placeholder="Choose an option"
/>

// Multi-Select Dropdown
<MultiSelect
  options={options}
  value={selectedValues}
  onChange={setSelectedValues}
  searchable
  clearable
  maxSelections={3}
  placeholder="Select multiple options"
/>

// Searchable Dropdown with Groups
<SearchableSelect
  options={[
    { value: 'apple', label: 'Apple', group: 'Fruits' },
    { value: 'orange', label: 'Orange', group: 'Fruits' },
    { value: 'carrot', label: 'Carrot', group: 'Vegetables' },
    { value: 'broccoli', label: 'Broccoli', group: 'Vegetables' }
  ]}
  value={selectedValue}
  onChange={setSelectedValue}
  onSearch={handleSearch}
/>

// Custom Option Rendering
<Dropdown
  options={userOptions}
  renderOption={(option, isSelected) => (
    <div style={{ display: 'flex', alignItems: 'center' }}>
      <img src={option.metadata.avatar} alt="" style={{ width: 24, height: 24, marginRight: 8 }} />
      <div>
        <div>{option.label}</div>
        <div style={{ fontSize: '0.75rem', color: '#666' }}>{option.description}</div>
      </div>
      {isSelected && <span style={{ marginLeft: 'auto', color: 'green' }}>✓</span>}
    </div>
  )}
/>

// Creatable Select
<CreatableSelect
  options={existingOptions}
  value={selectedValue}
  onChange={setSelectedValue}
  onCreate={(value) => {
    const newOption = { value, label: value };
    setExistingOptions(prev => [...prev, newOption]);
    setSelectedValue(value);
  }}
  allowCreate={true}
/>

// With Error State
<Dropdown
  options={options}
  value={selectedValue}
  onChange={setSelectedValue}
  error="Please select a valid option"
  size="large"
  variant="outlined"
/>
*/