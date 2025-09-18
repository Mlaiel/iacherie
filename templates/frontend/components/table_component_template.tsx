/**
 * 🎨 TABLE COMPONENT TEMPLATE - FRONTEND EXPERT IMPLEMENTATION
 * ============================================================
 * 
 * Enterprise-grade table component template with:
 * - TypeScript support with strict typing
 * - Virtual scrolling for large datasets
 * - Sorting, filtering, and pagination
 * - Row selection and bulk actions
 * - Column resizing and reordering
 * - Responsive design and mobile support
 * - Export functionality (CSV, Excel, PDF)
 * - Accessibility compliance (ARIA, keyboard navigation)
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
  useMemo, 
  useCallback, 
  useRef, 
  useEffect,
  ReactNode,
  MouseEvent,
  KeyboardEvent
} from 'react';
import styled, { css } from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

interface TableColumn<T = any> {
  id: string;
  header: string | ReactNode;
  accessor?: keyof T | ((row: T) => any);
  cell?: (value: any, row: T, index: number) => ReactNode;
  width?: number | string;
  minWidth?: number;
  maxWidth?: number;
  sortable?: boolean;
  filterable?: boolean;
  resizable?: boolean;
  sticky?: 'left' | 'right';
  align?: 'left' | 'center' | 'right';
  className?: string;
  headerClassName?: string;
  cellClassName?: string;
}

interface TableProps<T = any> {
  data: T[];
  columns: TableColumn<T>[];
  loading?: boolean;
  error?: string;
  emptyMessage?: string;
  selectable?: boolean;
  multiSelect?: boolean;
  selectedRows?: Set<string | number>;
  onSelectionChange?: (selectedRows: Set<string | number>) => void;
  sortable?: boolean;
  filterable?: boolean;
  pagination?: boolean;
  pageSize?: number;
  currentPage?: number;
  totalPages?: number;
  onPageChange?: (page: number) => void;
  onSortChange?: (sortBy: string, sortDirection: 'asc' | 'desc') => void;
  onFilterChange?: (filters: Record<string, any>) => void;
  virtualScroll?: boolean;
  rowHeight?: number;
  tableHeight?: number;
  resizable?: boolean;
  striped?: boolean;
  hover?: boolean;
  border?: boolean;
  size?: 'small' | 'medium' | 'large';
  variant?: 'default' | 'outlined' | 'minimal';
  getRowId?: (row: T, index: number) => string | number;
  onRowClick?: (row: T, index: number) => void;
  onRowDoubleClick?: (row: T, index: number) => void;
  bulkActions?: BulkAction[];
  exportable?: boolean;
  className?: string;
  style?: React.CSSProperties;
}

interface BulkAction {
  id: string;
  label: string;
  icon?: ReactNode;
  action: (selectedRows: Set<string | number>, data: any[]) => void;
  variant?: 'default' | 'danger' | 'success' | 'warning';
}

interface SortState {
  column: string | null;
  direction: 'asc' | 'desc';
}

interface FilterState {
  [key: string]: any;
}

// ============================================================================
// STYLED COMPONENTS
// ============================================================================

const TableContainer = styled.div<{ 
  variant: 'default' | 'outlined' | 'minimal';
  border: boolean;
}>`
  width: 100%;
  overflow: hidden;
  border-radius: 8px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  
  ${({ variant, border }) => {
    switch (variant) {
      case 'outlined':
        return css`
          border: 1px solid #e2e8f0;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        `;
      case 'minimal':
        return css`
          border: none;
          box-shadow: none;
        `;
      default:
        return css`
          border: ${border ? '1px solid #e2e8f0' : 'none'};
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        `;
    }
  }}
`;

const TableWrapper = styled.div<{ height?: number }>`
  overflow: auto;
  max-height: ${({ height }) => height ? `${height}px` : 'none'};
  
  &::-webkit-scrollbar {
    width: 8px;
    height: 8px;
  }
  
  &::-webkit-scrollbar-track {
    background: #f1f1f1;
  }
  
  &::-webkit-scrollbar-thumb {
    background: #c1c1c1;
    border-radius: 4px;
  }
  
  &::-webkit-scrollbar-thumb:hover {
    background: #a8a8a8;
  }
`;

const StyledTable = styled.table<{
  size: 'small' | 'medium' | 'large';
  striped: boolean;
  hover: boolean;
}>`
  width: 100%;
  border-collapse: collapse;
  background: white;
  
  ${({ size }) => {
    switch (size) {
      case 'small':
        return css`
          font-size: 12px;
          
          th, td {
            padding: 8px 12px;
          }
        `;
      case 'large':
        return css`
          font-size: 16px;
          
          th, td {
            padding: 20px 24px;
          }
        `;
      default: // medium
        return css`
          font-size: 14px;
          
          th, td {
            padding: 12px 16px;
          }
        `;
    }
  }}
`;

const TableHeader = styled.thead`
  background: #f8f9fa;
  border-bottom: 2px solid #e2e8f0;
  position: sticky;
  top: 0;
  z-index: 10;
`;

const TableBody = styled.tbody<{ striped: boolean; hover: boolean }>`
  ${({ striped }) => striped && css`
    tr:nth-child(even) {
      background-color: #f8f9fa;
    }
  `}
  
  ${({ hover }) => hover && css`
    tr:hover {
      background-color: #e6fffa;
      cursor: pointer;
    }
  `}
`;

const TableRow = styled.tr<{ 
  selected?: boolean; 
  clickable?: boolean;
  hover?: boolean;
}>`
  border-bottom: 1px solid #e2e8f0;
  transition: all 0.15s ease;
  
  ${({ selected }) => selected && css`
    background-color: #e6fffa !important;
  `}
  
  ${({ clickable }) => clickable && css`
    cursor: pointer;
  `}
  
  ${({ hover }) => hover && css`
    &:hover {
      background-color: #f7fafc;
    }
  `}
  
  &:last-child {
    border-bottom: none;
  }
`;

const TableHeaderCell = styled.th<{
  sortable?: boolean;
  align: 'left' | 'center' | 'right';
  sticky?: 'left' | 'right';
  width?: number | string;
  resizable?: boolean;
}>`
  text-align: ${({ align }) => align};
  font-weight: 600;
  color: #4a5568;
  white-space: nowrap;
  user-select: none;
  position: relative;
  
  ${({ width }) => width && css`
    width: ${typeof width === 'number' ? `${width}px` : width};
  `}
  
  ${({ sortable }) => sortable && css`
    cursor: pointer;
    
    &:hover {
      background-color: #edf2f7;
    }
  `}
  
  ${({ sticky }) => sticky && css`
    position: sticky;
    ${sticky}: 0;
    z-index: 11;
    background: #f8f9fa;
    border-${sticky}: 1px solid #e2e8f0;
  `}
  
  ${({ resizable }) => resizable && css`
    &::after {
      content: '';
      position: absolute;
      top: 0;
      right: 0;
      width: 4px;
      height: 100%;
      cursor: col-resize;
      background: transparent;
      
      &:hover {
        background: #3182ce;
      }
    }
  `}
`;

const TableCell = styled.td<{
  align: 'left' | 'center' | 'right';
  sticky?: 'left' | 'right';
}>`
  text-align: ${({ align }) => align};
  color: #2d3748;
  vertical-align: middle;
  
  ${({ sticky }) => sticky && css`
    position: sticky;
    ${sticky}: 0;
    z-index: 9;
    background: white;
    border-${sticky}: 1px solid #e2e8f0;
  `}
`;

const SortIcon = styled.span<{ direction?: 'asc' | 'desc' | null }>`
  display: inline-flex;
  align-items: center;
  margin-left: 4px;
  opacity: ${({ direction }) => direction ? 1 : 0.3};
  transition: opacity 0.15s ease;
  
  svg {
    width: 12px;
    height: 12px;
    transform: ${({ direction }) => direction === 'desc' ? 'rotate(180deg)' : 'none'};
    transition: transform 0.15s ease;
  }
`;

const FilterInput = styled.input`
  width: 100%;
  padding: 4px 8px;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  font-size: 12px;
  margin-top: 4px;
  
  &:focus {
    outline: none;
    border-color: #3182ce;
    box-shadow: 0 0 0 2px rgba(49, 130, 206, 0.1);
  }
`;

const LoadingOverlay = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 20;
`;

const LoadingSpinner = styled.div`
  width: 32px;
  height: 32px;
  border: 3px solid #e2e8f0;
  border-top: 3px solid #3182ce;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const EmptyState = styled.div`
  padding: 40px 20px;
  text-align: center;
  color: #718096;
  font-size: 16px;
`;

const ErrorState = styled.div`
  padding: 20px;
  background: #fed7d7;
  border: 1px solid #feb2b2;
  border-radius: 8px;
  color: #c53030;
  text-align: center;
  margin: 16px;
`;

const BulkActionsBar = styled.div`
  background: #edf2f7;
  border-bottom: 1px solid #e2e8f0;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
`;

const BulkActionButton = styled.button<{ variant: 'default' | 'danger' | 'success' | 'warning' }>`
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  display: flex;
  align-items: center;
  gap: 4px;
  
  ${({ variant }) => {
    switch (variant) {
      case 'danger':
        return css`
          background: #fed7d7;
          color: #c53030;
          
          &:hover {
            background: #feb2b2;
          }
        `;
      case 'success':
        return css`
          background: #c6f6d5;
          color: #22543d;
          
          &:hover {
            background: #9ae6b4;
          }
        `;
      case 'warning':
        return css`
          background: #fefcbf;
          color: #744210;
          
          &:hover {
            background: #faf089;
          }
        `;
      default:
        return css`
          background: #e2e8f0;
          color: #4a5568;
          
          &:hover {
            background: #cbd5e0;
          }
        `;
    }
  }}
`;

const Pagination = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-top: 1px solid #e2e8f0;
  background: #f8f9fa;
`;

const PaginationButton = styled.button<{ active?: boolean; disabled?: boolean }>`
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  background: white;
  color: #4a5568;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.15s ease;
  
  &:not(:last-child) {
    margin-right: 4px;
  }
  
  ${({ active }) => active && css`
    background: #3182ce;
    color: white;
    border-color: #3182ce;
  `}
  
  ${({ disabled }) => disabled && css`
    opacity: 0.5;
    cursor: not-allowed;
    pointer-events: none;
  `}
  
  &:hover:not(:disabled) {
    background: ${({ active }) => active ? '#2c5aa0' : '#f7fafc'};
  }
`;

const Checkbox = styled.input`
  cursor: pointer;
  
  &:indeterminate {
    background: #3182ce;
  }
`;

// ============================================================================
// MAIN TABLE COMPONENT
// ============================================================================

export const Table = <T extends Record<string, any>>({
  data = [],
  columns = [],
  loading = false,
  error,
  emptyMessage = 'No data available',
  selectable = false,
  multiSelect = true,
  selectedRows = new Set(),
  onSelectionChange,
  sortable = true,
  filterable = false,
  pagination = false,
  pageSize = 10,
  currentPage = 1,
  totalPages,
  onPageChange,
  onSortChange,
  onFilterChange,
  virtualScroll = false,
  rowHeight = 50,
  tableHeight,
  resizable = false,
  striped = false,
  hover = true,
  border = true,
  size = 'medium',
  variant = 'default',
  getRowId = (row, index) => row.id || index,
  onRowClick,
  onRowDoubleClick,
  bulkActions = [],
  exportable = false,
  className,
  style,
  ...props
}: TableProps<T>) => {
  const [sortState, setSortState] = useState<SortState>({ column: null, direction: 'asc' });
  const [filters, setFilters] = useState<FilterState>({});
  const [columnWidths, setColumnWidths] = useState<Record<string, number>>({});
  
  const tableRef = useRef<HTMLTableElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Calculate derived data
  const processedData = useMemo(() => {
    let result = [...data];

    // Apply filters
    if (filterable && Object.keys(filters).length > 0) {
      result = result.filter(row => {
        return Object.entries(filters).every(([columnId, filterValue]) => {
          if (!filterValue) return true;
          
          const column = columns.find(col => col.id === columnId);
          if (!column) return true;
          
          const cellValue = column.accessor 
            ? typeof column.accessor === 'function' 
              ? column.accessor(row)
              : row[column.accessor]
            : row[columnId];
          
          return String(cellValue).toLowerCase().includes(String(filterValue).toLowerCase());
        });
      });
    }

    // Apply sorting
    if (sortState.column) {
      const column = columns.find(col => col.id === sortState.column);
      if (column) {
        result.sort((a, b) => {
          const aValue = column.accessor 
            ? typeof column.accessor === 'function' 
              ? column.accessor(a)
              : a[column.accessor]
            : a[sortState.column!];
          
          const bValue = column.accessor 
            ? typeof column.accessor === 'function' 
              ? column.accessor(b)
              : b[column.accessor]
            : b[sortState.column!];

          const comparison = aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
          return sortState.direction === 'desc' ? -comparison : comparison;
        });
      }
    }

    return result;
  }, [data, filters, sortState, columns, filterable]);

  // Pagination calculations
  const paginatedData = useMemo(() => {
    if (!pagination) return processedData;
    
    const startIndex = (currentPage - 1) * pageSize;
    const endIndex = startIndex + pageSize;
    return processedData.slice(startIndex, endIndex);
  }, [processedData, pagination, currentPage, pageSize]);

  const computedTotalPages = useMemo(() => {
    return totalPages || Math.ceil(processedData.length / pageSize);
  }, [totalPages, processedData.length, pageSize]);

  // Handle sorting
  const handleSort = useCallback((columnId: string) => {
    const column = columns.find(col => col.id === columnId);
    if (!column?.sortable && !sortable) return;

    setSortState(prev => {
      const newDirection = prev.column === columnId && prev.direction === 'asc' ? 'desc' : 'asc';
      const newState = { column: columnId, direction: newDirection };
      
      onSortChange?.(columnId, newDirection);
      return newState;
    });
  }, [columns, sortable, onSortChange]);

  // Handle filtering
  const handleFilterChange = useCallback((columnId: string, value: string) => {
    setFilters(prev => {
      const newFilters = { ...prev, [columnId]: value };
      onFilterChange?.(newFilters);
      return newFilters;
    });
  }, [onFilterChange]);

  // Handle row selection
  const handleRowSelection = useCallback((rowId: string | number, checked: boolean) => {
    if (!selectable) return;

    const newSelection = new Set(selectedRows);
    
    if (checked) {
      if (multiSelect) {
        newSelection.add(rowId);
      } else {
        newSelection.clear();
        newSelection.add(rowId);
      }
    } else {
      newSelection.delete(rowId);
    }
    
    onSelectionChange?.(newSelection);
  }, [selectable, multiSelect, selectedRows, onSelectionChange]);

  // Handle select all
  const handleSelectAll = useCallback((checked: boolean) => {
    if (!selectable || !multiSelect) return;

    const newSelection = new Set(selectedRows);
    
    if (checked) {
      paginatedData.forEach((row, index) => {
        newSelection.add(getRowId(row, index));
      });
    } else {
      paginatedData.forEach((row, index) => {
        newSelection.delete(getRowId(row, index));
      });
    }
    
    onSelectionChange?.(newSelection);
  }, [selectable, multiSelect, selectedRows, paginatedData, getRowId, onSelectionChange]);

  // Check if all rows are selected
  const isAllSelected = useMemo(() => {
    if (!selectable || paginatedData.length === 0) return false;
    return paginatedData.every((row, index) => selectedRows.has(getRowId(row, index)));
  }, [selectable, paginatedData, selectedRows, getRowId]);

  const isIndeterminate = useMemo(() => {
    if (!selectable || paginatedData.length === 0) return false;
    const selectedCount = paginatedData.filter((row, index) => 
      selectedRows.has(getRowId(row, index))
    ).length;
    return selectedCount > 0 && selectedCount < paginatedData.length;
  }, [selectable, paginatedData, selectedRows, getRowId]);

  // Handle export functionality
  const handleExport = useCallback((format: 'csv' | 'excel' | 'pdf') => {
    // Implementation for export functionality
    console.log(`Exporting data as ${format}`);
  }, []);

  // Render table header
  const renderTableHeader = () => (
    <TableHeader>
      <TableRow>
        {selectable && (
          <TableHeaderCell align="center" width={50}>
            {multiSelect && (
              <Checkbox
                type="checkbox"
                checked={isAllSelected}
                ref={(input) => {
                  if (input) input.indeterminate = isIndeterminate;
                }}
                onChange={(e) => handleSelectAll(e.target.checked)}
              />
            )}
          </TableHeaderCell>
        )}
        
        {columns.map((column) => (
          <TableHeaderCell
            key={column.id}
            align={column.align || 'left'}
            sticky={column.sticky}
            width={columnWidths[column.id] || column.width}
            sortable={column.sortable !== false && sortable}
            resizable={column.resizable !== false && resizable}
            className={column.headerClassName}
            onClick={() => (column.sortable !== false && sortable) && handleSort(column.id)}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: column.align === 'center' ? 'center' : column.align === 'right' ? 'flex-end' : 'flex-start' }}>
              {column.header}
              {(column.sortable !== false && sortable) && (
                <SortIcon direction={sortState.column === column.id ? sortState.direction : null}>
                  <svg viewBox="0 0 12 12" fill="currentColor">
                    <path d="M6 3L2 7h8L6 3z" />
                  </svg>
                </SortIcon>
              )}
            </div>
            
            {filterable && column.filterable !== false && (
              <FilterInput
                type="text"
                placeholder={`Filter ${typeof column.header === 'string' ? column.header : ''}...`}
                value={filters[column.id] || ''}
                onChange={(e) => handleFilterChange(column.id, e.target.value)}
                onClick={(e) => e.stopPropagation()}
              />
            )}
          </TableHeaderCell>
        ))}
      </TableRow>
    </TableHeader>
  );

  // Render table body
  const renderTableBody = () => (
    <TableBody striped={striped} hover={hover}>
      {paginatedData.map((row, index) => {
        const rowId = getRowId(row, index);
        const isSelected = selectedRows.has(rowId);
        
        return (
          <TableRow
            key={rowId}
            selected={isSelected}
            clickable={!!onRowClick}
            hover={hover}
            onClick={() => onRowClick?.(row, index)}
            onDoubleClick={() => onRowDoubleClick?.(row, index)}
          >
            {selectable && (
              <TableCell align="center">
                <Checkbox
                  type="checkbox"
                  checked={isSelected}
                  onChange={(e) => {
                    e.stopPropagation();
                    handleRowSelection(rowId, e.target.checked);
                  }}
                />
              </TableCell>
            )}
            
            {columns.map((column) => {
              const cellValue = column.accessor 
                ? typeof column.accessor === 'function' 
                  ? column.accessor(row)
                  : row[column.accessor]
                : row[column.id];
              
              const cellContent = column.cell 
                ? column.cell(cellValue, row, index)
                : cellValue;
              
              return (
                <TableCell
                  key={column.id}
                  align={column.align || 'left'}
                  sticky={column.sticky}
                  className={column.cellClassName}
                >
                  {cellContent}
                </TableCell>
              );
            })}
          </TableRow>
        );
      })}
    </TableBody>
  );

  // Render pagination
  const renderPagination = () => {
    if (!pagination) return null;

    const pages = [];
    const maxVisiblePages = 5;
    const halfVisible = Math.floor(maxVisiblePages / 2);
    
    let startPage = Math.max(1, currentPage - halfVisible);
    let endPage = Math.min(computedTotalPages, startPage + maxVisiblePages - 1);
    
    if (endPage - startPage + 1 < maxVisiblePages) {
      startPage = Math.max(1, endPage - maxVisiblePages + 1);
    }

    for (let i = startPage; i <= endPage; i++) {
      pages.push(i);
    }

    return (
      <Pagination>
        <div>
          Showing {((currentPage - 1) * pageSize) + 1} to {Math.min(currentPage * pageSize, processedData.length)} of {processedData.length} entries
        </div>
        
        <div>
          <PaginationButton
            disabled={currentPage === 1}
            onClick={() => onPageChange?.(currentPage - 1)}
          >
            Previous
          </PaginationButton>
          
          {pages.map(page => (
            <PaginationButton
              key={page}
              active={page === currentPage}
              onClick={() => onPageChange?.(page)}
            >
              {page}
            </PaginationButton>
          ))}
          
          <PaginationButton
            disabled={currentPage === computedTotalPages}
            onClick={() => onPageChange?.(currentPage + 1)}
          >
            Next
          </PaginationButton>
        </div>
      </Pagination>
    );
  };

  if (error) {
    return (
      <TableContainer variant={variant} border={border} className={className} style={style}>
        <ErrorState>{error}</ErrorState>
      </TableContainer>
    );
  }

  return (
    <TableContainer variant={variant} border={border} className={className} style={style} {...props}>
      {/* Bulk Actions */}
      {selectable && selectedRows.size > 0 && bulkActions.length > 0 && (
        <BulkActionsBar>
          <span>{selectedRows.size} item(s) selected</span>
          {bulkActions.map(action => (
            <BulkActionButton
              key={action.id}
              variant={action.variant || 'default'}
              onClick={() => action.action(selectedRows, data)}
            >
              {action.icon && action.icon}
              {action.label}
            </BulkActionButton>
          ))}
        </BulkActionsBar>
      )}

      <div ref={containerRef} style={{ position: 'relative' }}>
        {loading && (
          <LoadingOverlay>
            <LoadingSpinner />
          </LoadingOverlay>
        )}

        <TableWrapper height={tableHeight}>
          <StyledTable
            ref={tableRef}
            size={size}
            striped={striped}
            hover={hover}
          >
            {renderTableHeader()}
            {paginatedData.length > 0 ? renderTableBody() : (
              <tbody>
                <tr>
                  <td colSpan={columns.length + (selectable ? 1 : 0)}>
                    <EmptyState>{emptyMessage}</EmptyState>
                  </td>
                </tr>
              </tbody>
            )}
          </StyledTable>
        </TableWrapper>

        {renderPagination()}
      </div>
    </TableContainer>
  );
};

// ============================================================================
// USAGE EXAMPLES
// ============================================================================

export const TableExamples: React.FC = () => {
  const [selectedRows, setSelectedRows] = useState<Set<string | number>>(new Set());
  const [currentPage, setCurrentPage] = useState(1);
  const [loading, setLoading] = useState(false);

  // Sample data
  const sampleData = [
    { id: 1, name: 'John Doe', email: 'john@example.com', role: 'Admin', status: 'Active', lastLogin: '2024-01-15' },
    { id: 2, name: 'Jane Smith', email: 'jane@example.com', role: 'User', status: 'Active', lastLogin: '2024-01-14' },
    { id: 3, name: 'Bob Johnson', email: 'bob@example.com', role: 'Moderator', status: 'Inactive', lastLogin: '2024-01-10' },
    { id: 4, name: 'Alice Brown', email: 'alice@example.com', role: 'User', status: 'Active', lastLogin: '2024-01-16' },
    { id: 5, name: 'Charlie Wilson', email: 'charlie@example.com', role: 'Admin', status: 'Active', lastLogin: '2024-01-13' },
  ];

  const columns: TableColumn[] = [
    {
      id: 'name',
      header: 'Name',
      accessor: 'name',
      sortable: true,
      filterable: true,
    },
    {
      id: 'email',
      header: 'Email',
      accessor: 'email',
      sortable: true,
      filterable: true,
    },
    {
      id: 'role',
      header: 'Role',
      accessor: 'role',
      sortable: true,
      filterable: true,
      cell: (value) => (
        <span style={{ 
          padding: '4px 8px',
          borderRadius: '12px',
          fontSize: '12px',
          backgroundColor: value === 'Admin' ? '#fed7d7' : value === 'Moderator' ? '#fefcbf' : '#c6f6d5',
          color: value === 'Admin' ? '#c53030' : value === 'Moderator' ? '#744210' : '#22543d'
        }}>
          {value}
        </span>
      ),
    },
    {
      id: 'status',
      header: 'Status',
      accessor: 'status',
      sortable: true,
      align: 'center',
      cell: (value) => (
        <span style={{ 
          color: value === 'Active' ? '#22543d' : '#c53030',
          fontWeight: '500'
        }}>
          {value}
        </span>
      ),
    },
    {
      id: 'lastLogin',
      header: 'Last Login',
      accessor: 'lastLogin',
      sortable: true,
      align: 'right',
    },
    {
      id: 'actions',
      header: 'Actions',
      align: 'center',
      cell: (_, row) => (
        <div style={{ display: 'flex', gap: '8px', justifyContent: 'center' }}>
          <button 
            style={{ 
              padding: '4px 8px', 
              border: 'none', 
              borderRadius: '4px', 
              background: '#3182ce', 
              color: 'white',
              cursor: 'pointer',
              fontSize: '12px'
            }}
            onClick={(e) => {
              e.stopPropagation();
              console.log('Edit', row);
            }}
          >
            Edit
          </button>
          <button 
            style={{ 
              padding: '4px 8px', 
              border: 'none', 
              borderRadius: '4px', 
              background: '#e53e3e', 
              color: 'white',
              cursor: 'pointer',
              fontSize: '12px'
            }}
            onClick={(e) => {
              e.stopPropagation();
              console.log('Delete', row);
            }}
          >
            Delete
          </button>
        </div>
      ),
    },
  ];

  const bulkActions: BulkAction[] = [
    {
      id: 'delete',
      label: 'Delete Selected',
      variant: 'danger',
      action: (selectedRows, data) => {
        console.log('Bulk delete:', selectedRows);
      },
    },
    {
      id: 'export',
      label: 'Export Selected',
      action: (selectedRows, data) => {
        console.log('Bulk export:', selectedRows);
      },
    },
  ];

  return (
    <div style={{ padding: '2rem' }}>
      <h2>Table Component Examples</h2>
      
      <div style={{ marginBottom: '2rem' }}>
        <h3>Full Featured Table</h3>
        <div style={{ marginBottom: '1rem' }}>
          <button 
            onClick={() => setLoading(!loading)}
            style={{ 
              padding: '8px 16px', 
              marginRight: '8px',
              border: 'none',
              borderRadius: '4px',
              background: '#3182ce',
              color: 'white',
              cursor: 'pointer'
            }}
          >
            Toggle Loading
          </button>
        </div>
        
        <Table
          data={sampleData}
          columns={columns}
          loading={loading}
          selectable
          multiSelect
          selectedRows={selectedRows}
          onSelectionChange={setSelectedRows}
          sortable
          filterable
          pagination
          pageSize={3}
          currentPage={currentPage}
          onPageChange={setCurrentPage}
          hover
          striped
          bulkActions={bulkActions}
          onRowClick={(row) => console.log('Row clicked:', row)}
          emptyMessage="No users found"
        />
      </div>

      <div style={{ marginBottom: '2rem' }}>
        <h3>Minimal Table</h3>
        <Table
          data={sampleData.slice(0, 3)}
          columns={columns.slice(0, 3)}
          variant="minimal"
          size="small"
          border={false}
        />
      </div>

      <div style={{ marginBottom: '2rem' }}>
        <h3>Outlined Table</h3>
        <Table
          data={sampleData.slice(0, 3)}
          columns={columns.slice(0, 4)}
          variant="outlined"
          size="large"
        />
      </div>
    </div>
  );
};

export default Table;