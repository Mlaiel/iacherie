/**
 * 📊 Table Component Template - UI Component Templates
 * ===================================================
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

import React, { useState, useMemo, useCallback, useRef, useEffect } from 'react';
import styled, { css, keyframes } from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';

// ================================
// TYPES & INTERFACES
// ================================

export interface Column<T = any> {
  key: string;
  title: string;
  dataIndex?: string;
  width?: number | string;
  fixed?: 'left' | 'right';
  sortable?: boolean;
  filterable?: boolean;
  resizable?: boolean;
  render?: (value: any, record: T, index: number) => React.ReactNode;
  sorter?: (a: T, b: T) => number;
  filters?: FilterOption[];
  filterDropdown?: React.ReactNode;
  onFilter?: (value: any, record: T) => boolean;
  align?: 'left' | 'center' | 'right';
  ellipsis?: boolean;
  className?: string;
}

export interface FilterOption {
  text: string;
  value: any;
}

export interface SortConfig {
  key: string;
  direction: 'asc' | 'desc';
}

export interface TableProps<T = any> {
  columns: Column<T>[];
  dataSource: T[];
  rowKey?: string | ((record: T) => string);
  loading?: boolean;
  pagination?: PaginationConfig | false;
  scroll?: { x?: number | string; y?: number | string };
  size?: 'small' | 'middle' | 'large';
  bordered?: boolean;
  showHeader?: boolean;
  title?: React.ReactNode;
  footer?: React.ReactNode;
  expandable?: ExpandableConfig<T>;
  rowSelection?: RowSelectionConfig<T>;
  rowClassName?: string | ((record: T, index: number) => string);
  onRow?: (record: T, index: number) => React.HTMLAttributes<HTMLTableRowElement>;
  onChange?: (pagination: any, filters: any, sorter: any) => void;
  locale?: TableLocale;
  empty?: React.ReactNode;
  sticky?: boolean;
  virtualScroll?: boolean;
  className?: string;
  'data-testid'?: string;
}

export interface PaginationConfig {
  current?: number;
  pageSize?: number;
  total?: number;
  showSizeChanger?: boolean;
  showQuickJumper?: boolean;
  showTotal?: (total: number, range: [number, number]) => React.ReactNode;
  onChange?: (page: number, pageSize: number) => void;
  position?: 'topLeft' | 'topCenter' | 'topRight' | 'bottomLeft' | 'bottomCenter' | 'bottomRight';
}

export interface ExpandableConfig<T> {
  expandedRowKeys?: string[];
  defaultExpandedRowKeys?: string[];
  expandRowByClick?: boolean;
  expandIcon?: (props: { expanded: boolean; onExpand: () => void; record: T }) => React.ReactNode;
  expandedRowRender?: (record: T, index: number) => React.ReactNode;
  onExpand?: (expanded: boolean, record: T) => void;
  onExpandedRowsChange?: (expandedKeys: string[]) => void;
}

export interface RowSelectionConfig<T> {
  type?: 'checkbox' | 'radio';
  selectedRowKeys?: string[];
  onChange?: (selectedRowKeys: string[], selectedRows: T[]) => void;
  onSelect?: (record: T, selected: boolean, selectedRows: T[]) => void;
  onSelectAll?: (selected: boolean, selectedRows: T[], changeRows: T[]) => void;
  getCheckboxProps?: (record: T) => { disabled?: boolean; name?: string };
  fixed?: boolean;
  columnWidth?: number | string;
  renderCell?: (checked: boolean, record: T, index: number, originNode: React.ReactNode) => React.ReactNode;
}

export interface TableLocale {
  filterTitle?: string;
  filterConfirm?: string;
  filterReset?: string;
  filterEmptyText?: string;
  emptyText?: string;
  selectAll?: string;
  selectInvert?: string;
  triggerDesc?: string;
  triggerAsc?: string;
  cancelSort?: string;
}

// ================================
// ANIMATIONS
// ================================

const fadeIn = keyframes`
  from { opacity: 0; }
  to { opacity: 1; }
`;

const slideIn = keyframes`
  from { transform: translateY(-10px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
`;

const shimmer = keyframes`
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
`;

// ================================
// STYLED COMPONENTS
// ================================

const TableContainer = styled.div<{ 
  size: string; 
  bordered?: boolean; 
  sticky?: boolean;
}>`
  position: relative;
  background: #ffffff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  
  ${({ bordered }) => bordered && css`
    border: 1px solid rgba(0, 0, 0, 0.06);
  `}
  
  ${({ sticky }) => sticky && css`
    position: sticky;
    top: 0;
    z-index: 100;
  `}
`;

const TableWrapper = styled.div<{ scroll?: { x?: any; y?: any } }>`
  ${({ scroll }) => scroll?.x && css`
    overflow-x: auto;
    min-width: ${typeof scroll.x === 'number' ? `${scroll.x}px` : scroll.x};
  `}
  
  ${({ scroll }) => scroll?.y && css`
    max-height: ${typeof scroll.y === 'number' ? `${scroll.y}px` : scroll.y};
    overflow-y: auto;
  `}
`;

const StyledTable = styled.table<{ size: string }>`
  width: 100%;
  border-collapse: collapse;
  border-spacing: 0;
  table-layout: fixed;
  
  ${({ size }) => {
    switch (size) {
      case 'small':
        return css`
          font-size: 0.875rem;
          
          th, td {
            padding: 8px 12px;
          }
        `;
      case 'large':
        return css`
          font-size: 1.125rem;
          
          th, td {
            padding: 20px 24px;
          }
        `;
      default:
        return css`
          font-size: 1rem;
          
          th, td {
            padding: 16px;
          }
        `;
    }
  }}
`;

const TableHeader = styled.thead`
  background: #fafafa;
  
  th {
    background: #fafafa;
    color: #262626;
    font-weight: 600;
    text-align: left;
    border-bottom: 1px solid rgba(0, 0, 0, 0.06);
    position: relative;
    
    &.sortable {
      cursor: pointer;
      user-select: none;
      
      &:hover {
        background: #f0f0f0;
      }
    }
    
    &.fixed-left {
      position: sticky;
      left: 0;
      z-index: 10;
      box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
    }
    
    &.fixed-right {
      position: sticky;
      right: 0;
      z-index: 10;
      box-shadow: -2px 0 8px rgba(0, 0, 0, 0.1);
    }
  }
`;

const TableBody = styled.tbody`
  tr {
    transition: background-color 0.2s ease;
    
    &:hover {
      background: #fafafa;
    }
    
    &.selected {
      background: #e6f7ff;
    }
    
    &.expanded {
      background: #f9f9f9;
    }
  }
  
  td {
    border-bottom: 1px solid rgba(0, 0, 0, 0.06);
    vertical-align: middle;
    position: relative;
    
    &.fixed-left {
      position: sticky;
      left: 0;
      z-index: 5;
      background: inherit;
      box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
    }
    
    &.fixed-right {
      position: sticky;
      right: 0;
      z-index: 5;
      background: inherit;
      box-shadow: -2px 0 8px rgba(0, 0, 0, 0.1);
    }
  }
`;

const SortIcon = styled.span<{ direction?: 'asc' | 'desc' }>`
  display: inline-flex;
  flex-direction: column;
  margin-left: 8px;
  
  &::before,
  &::after {
    content: '';
    width: 0;
    height: 0;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
  }
  
  &::before {
    border-bottom: 4px solid ${({ direction }) => 
      direction === 'asc' ? '#1890ff' : 'rgba(0, 0, 0, 0.25)'};
    margin-bottom: 2px;
  }
  
  &::after {
    border-top: 4px solid ${({ direction }) => 
      direction === 'desc' ? '#1890ff' : 'rgba(0, 0, 0, 0.25)'};
  }
`;

const FilterIcon = styled.button`
  background: none;
  border: none;
  color: rgba(0, 0, 0, 0.45);
  cursor: pointer;
  padding: 4px;
  margin-left: 8px;
  border-radius: 4px;
  transition: all 0.2s ease;
  
  &:hover {
    color: #1890ff;
    background: rgba(24, 144, 255, 0.1);
  }
  
  &.active {
    color: #1890ff;
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
  z-index: 1000;
`;

const LoadingSkeleton = styled.div`
  height: 20px;
  background: linear-gradient(
    90deg,
    #f0f0f0 25%,
    #e0e0e0 50%,
    #f0f0f0 75%
  );
  background-size: 200% 100%;
  animation: ${shimmer} 1.5s infinite;
  border-radius: 4px;
  margin: 4px 0;
`;

const EmptyState = styled.div`
  padding: 40px 20px;
  text-align: center;
  color: rgba(0, 0, 0, 0.45);
  
  .empty-icon {
    font-size: 48px;
    margin-bottom: 16px;
    opacity: 0.5;
  }
  
  .empty-text {
    font-size: 16px;
    line-height: 1.5;
  }
`;

const ResizeHandle = styled.div`
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  width: 4px;
  background: transparent;
  cursor: col-resize;
  user-select: none;
  
  &:hover,
  &.resizing {
    background: #1890ff;
  }
`;

const ExpandIcon = styled.button<{ expanded: boolean }>`
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s ease;
  transform: ${({ expanded }) => expanded ? 'rotate(90deg)' : 'rotate(0deg)'};
  
  &:hover {
    background: rgba(0, 0, 0, 0.04);
  }
  
  &::after {
    content: '▶';
    display: block;
    font-size: 12px;
    color: rgba(0, 0, 0, 0.45);
  }
`;

const CheckboxCell = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  
  input[type="checkbox"],
  input[type="radio"] {
    margin: 0;
    cursor: pointer;
  }
`;

// ================================
// CUSTOM HOOKS
// ================================

const useTableSort = <T,>(data: T[], columns: Column<T>[]) => {
  const [sortConfig, setSortConfig] = useState<SortConfig | null>(null);
  
  const sortedData = useMemo(() => {
    if (!sortConfig) return data;
    
    const { key, direction } = sortConfig;
    const column = columns.find(col => col.key === key);
    
    return [...data].sort((a, b) => {
      if (column?.sorter) {
        const result = column.sorter(a, b);
        return direction === 'desc' ? -result : result;
      }
      
      const aValue = column?.dataIndex ? a[column.dataIndex] : a[key];
      const bValue = column?.dataIndex ? b[column.dataIndex] : b[key];
      
      if (aValue < bValue) return direction === 'desc' ? 1 : -1;
      if (aValue > bValue) return direction === 'desc' ? -1 : 1;
      return 0;
    });
  }, [data, sortConfig, columns]);
  
  const handleSort = useCallback((key: string) => {
    setSortConfig(current => {
      if (!current || current.key !== key) {
        return { key, direction: 'asc' };
      }
      if (current.direction === 'asc') {
        return { key, direction: 'desc' };
      }
      return null;
    });
  }, []);
  
  return { sortedData, sortConfig, handleSort };
};

const useTableFilter = <T,>(data: T[], columns: Column<T>[]) => {
  const [filters, setFilters] = useState<Record<string, any>>({});
  
  const filteredData = useMemo(() => {
    return data.filter(record => {
      return Object.entries(filters).every(([key, value]) => {
        if (!value || (Array.isArray(value) && value.length === 0)) return true;
        
        const column = columns.find(col => col.key === key);
        if (column?.onFilter) {
          return column.onFilter(value, record);
        }
        
        const recordValue = column?.dataIndex ? record[column.dataIndex] : record[key];
        
        if (Array.isArray(value)) {
          return value.includes(recordValue);
        }
        
        return String(recordValue).toLowerCase().includes(String(value).toLowerCase());
      });
    });
  }, [data, filters, columns]);
  
  const handleFilter = useCallback((key: string, value: any) => {
    setFilters(current => ({
      ...current,
      [key]: value
    }));
  }, []);
  
  return { filteredData, filters, handleFilter };
};

const useTableSelection = <T,>(
  data: T[],
  rowKey: string | ((record: T) => string),
  config?: RowSelectionConfig<T>
) => {
  const [selectedKeys, setSelectedKeys] = useState<string[]>(
    config?.selectedRowKeys || []
  );
  
  const getRowKey = useCallback((record: T) => {
    return typeof rowKey === 'function' ? rowKey(record) : record[rowKey];
  }, [rowKey]);
  
  const handleSelect = useCallback((record: T, selected: boolean) => {
    const key = getRowKey(record);
    const newSelectedKeys = selected
      ? [...selectedKeys, key]
      : selectedKeys.filter(k => k !== key);
    
    setSelectedKeys(newSelectedKeys);
    
    const selectedRows = data.filter(item => 
      newSelectedKeys.includes(getRowKey(item))
    );
    
    config?.onChange?.(newSelectedKeys, selectedRows);
    config?.onSelect?.(record, selected, selectedRows);
  }, [selectedKeys, data, getRowKey, config]);
  
  const handleSelectAll = useCallback((selected: boolean) => {
    const allKeys = data.map(getRowKey);
    const newSelectedKeys = selected ? allKeys : [];
    
    setSelectedKeys(newSelectedKeys);
    
    const selectedRows = selected ? data : [];
    config?.onChange?.(newSelectedKeys, selectedRows);
    config?.onSelectAll?.(selected, selectedRows, data);
  }, [data, getRowKey, config]);
  
  return {
    selectedKeys,
    selectedRows: data.filter(item => selectedKeys.includes(getRowKey(item))),
    handleSelect,
    handleSelectAll,
    isSelected: (record: T) => selectedKeys.includes(getRowKey(record)),
    isAllSelected: selectedKeys.length === data.length && data.length > 0,
    isIndeterminate: selectedKeys.length > 0 && selectedKeys.length < data.length,
  };
};

// ================================
// MAIN COMPONENT
// ================================

export const Table: React.FC<TableProps> = ({
  columns,
  dataSource,
  rowKey = 'key',
  loading = false,
  pagination,
  scroll,
  size = 'middle',
  bordered = false,
  showHeader = true,
  title,
  footer,
  expandable,
  rowSelection,
  rowClassName,
  onRow,
  onChange,
  locale,
  empty,
  sticky = false,
  virtualScroll = false,
  className,
  'data-testid': testId,
}) => {
  const tableRef = useRef<HTMLTableElement>(null);
  const [expandedKeys, setExpandedKeys] = useState<string[]>(
    expandable?.defaultExpandedRowKeys || []
  );
  
  // Data processing hooks
  const { sortedData, sortConfig, handleSort } = useTableSort(dataSource, columns);
  const { filteredData, filters, handleFilter } = useTableFilter(sortedData, columns);
  const selection = useTableSelection(filteredData, rowKey, rowSelection);
  
  // Get final processed data
  const processedData = filteredData;
  
  // Handle row expansion
  const handleExpand = useCallback((record: any) => {
    const key = typeof rowKey === 'function' ? rowKey(record) : record[rowKey];
    const newExpandedKeys = expandedKeys.includes(key)
      ? expandedKeys.filter(k => k !== key)
      : [...expandedKeys, key];
    
    setExpandedKeys(newExpandedKeys);
    expandable?.onExpand?.(!expandedKeys.includes(key), record);
    expandable?.onExpandedRowsChange?.(newExpandedKeys);
  }, [expandedKeys, expandable, rowKey]);
  
  // Render cell content
  const renderCellContent = (
    column: Column,
    record: any,
    index: number
  ) => {
    const value = column.dataIndex ? record[column.dataIndex] : record[column.key];
    
    if (column.render) {
      return column.render(value, record, index);
    }
    
    if (column.ellipsis && typeof value === 'string') {
      return (
        <div
          style={{
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
          }}
          title={value}
        >
          {value}
        </div>
      );
    }
    
    return value;
  };
  
  // Render table header
  const renderHeader = () => (
    <TableHeader>
      <tr>
        {rowSelection && (
          <th style={{ width: rowSelection.columnWidth || 60 }}>
            {rowSelection.type !== 'radio' && (
              <CheckboxCell>
                <input
                  type="checkbox"
                  checked={selection.isAllSelected}
                  ref={(input) => {
                    if (input) input.indeterminate = selection.isIndeterminate;
                  }}
                  onChange={(e) => selection.handleSelectAll(e.target.checked)}
                />
              </CheckboxCell>
            )}
          </th>
        )}
        
        {expandable && (
          <th style={{ width: 50 }}></th>
        )}
        
        {columns.map((column) => (
          <th
            key={column.key}
            style={{
              width: column.width,
              textAlign: column.align || 'left',
            }}
            className={`
              ${column.sortable ? 'sortable' : ''}
              ${column.fixed ? `fixed-${column.fixed}` : ''}
            `}
            onClick={() => column.sortable && handleSort(column.key)}
          >
            <div style={{ display: 'flex', alignItems: 'center' }}>
              {column.title}
              
              {column.sortable && (
                <SortIcon
                  direction={
                    sortConfig?.key === column.key ? sortConfig.direction : undefined
                  }
                />
              )}
              
              {column.filterable && (
                <FilterIcon
                  className={filters[column.key] ? 'active' : ''}
                  onClick={(e) => {
                    e.stopPropagation();
                    // Filter logic would go here
                  }}
                  title="Filter"
                >
                  🔍
                </FilterIcon>
              )}
            </div>
            
            {column.resizable && <ResizeHandle />}
          </th>
        ))}
      </tr>
    </TableHeader>
  );
  
  // Render table body
  const renderBody = () => (
    <TableBody>
      {loading ? (
        // Loading skeleton
        Array.from({ length: 5 }).map((_, index) => (
          <tr key={index}>
            {rowSelection && <td><LoadingSkeleton /></td>}
            {expandable && <td><LoadingSkeleton /></td>}
            {columns.map((column) => (
              <td key={column.key}>
                <LoadingSkeleton />
              </td>
            ))}
          </tr>
        ))
      ) : processedData.length === 0 ? (
        // Empty state
        <tr>
          <td colSpan={columns.length + (rowSelection ? 1 : 0) + (expandable ? 1 : 0)}>
            <EmptyState>
              {empty || (
                <>
                  <div className="empty-icon">📋</div>
                  <div className="empty-text">
                    {locale?.emptyText || 'No data'}
                  </div>
                </>
              )}
            </EmptyState>
          </td>
        </tr>
      ) : (
        // Data rows
        processedData.map((record, index) => {
          const key = typeof rowKey === 'function' ? rowKey(record) : record[rowKey];
          const isExpanded = expandedKeys.includes(key);
          const isSelected = selection.isSelected(record);
          
          const rowProps = onRow?.(record, index) || {};
          const rowClass = typeof rowClassName === 'function' 
            ? rowClassName(record, index)
            : rowClassName;
          
          return (
            <React.Fragment key={key}>
              <tr
                {...rowProps}
                className={`
                  ${rowClass || ''}
                  ${isSelected ? 'selected' : ''}
                  ${isExpanded ? 'expanded' : ''}
                `}
              >
                {rowSelection && (
                  <td>
                    <CheckboxCell>
                      <input
                        type={rowSelection.type || 'checkbox'}
                        checked={isSelected}
                        onChange={(e) => selection.handleSelect(record, e.target.checked)}
                        {...(rowSelection.getCheckboxProps?.(record) || {})}
                      />
                    </CheckboxCell>
                  </td>
                )}
                
                {expandable && (
                  <td>
                    {expandable.expandIcon ? (
                      expandable.expandIcon({
                        expanded: isExpanded,
                        onExpand: () => handleExpand(record),
                        record,
                      })
                    ) : (
                      <ExpandIcon
                        expanded={isExpanded}
                        onClick={() => handleExpand(record)}
                      />
                    )}
                  </td>
                )}
                
                {columns.map((column) => (
                  <td
                    key={column.key}
                    style={{
                      textAlign: column.align || 'left',
                    }}
                    className={`
                      ${column.fixed ? `fixed-${column.fixed}` : ''}
                      ${column.className || ''}
                    `}
                  >
                    {renderCellContent(column, record, index)}
                  </td>
                ))}
              </tr>
              
              {isExpanded && expandable?.expandedRowRender && (
                <tr className="expanded-row">
                  <td
                    colSpan={
                      columns.length + (rowSelection ? 1 : 0) + (expandable ? 1 : 0)
                    }
                    style={{ padding: 0 }}
                  >
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.2 }}
                      style={{ overflow: 'hidden' }}
                    >
                      <div style={{ padding: '16px' }}>
                        {expandable.expandedRowRender(record, index)}
                      </div>
                    </motion.div>
                  </td>
                </tr>
              )}
            </React.Fragment>
          );
        })
      )}
    </TableBody>
  );
  
  return (
    <TableContainer
      size={size}
      bordered={bordered}
      sticky={sticky}
      className={className}
      data-testid={testId}
    >
      {title && (
        <div style={{ padding: '16px', borderBottom: '1px solid rgba(0, 0, 0, 0.06)' }}>
          {title}
        </div>
      )}
      
      <TableWrapper scroll={scroll}>
        <StyledTable ref={tableRef} size={size}>
          {showHeader && renderHeader()}
          {renderBody()}
        </StyledTable>
      </TableWrapper>
      
      {footer && (
        <div style={{ padding: '16px', borderTop: '1px solid rgba(0, 0, 0, 0.06)' }}>
          {footer}
        </div>
      )}
      
      {loading && (
        <LoadingOverlay>
          <div style={{ textAlign: 'center' }}>
            <div style={{ marginBottom: '8px' }}>🔄</div>
            <div>Loading...</div>
          </div>
        </LoadingOverlay>
      )}
    </TableContainer>
  );
};

// ================================
// UTILITY COMPONENTS
// ================================

export const SimpleTable: React.FC<Partial<TableProps>> = (props) => (
  <Table size="small" bordered={false} {...props} />
);

export const DataTable: React.FC<Partial<TableProps>> = (props) => (
  <Table 
    size="middle" 
    bordered 
    pagination={{ pageSize: 10, showSizeChanger: true }}
    {...props} 
  />
);

export const AdvancedTable: React.FC<Partial<TableProps>> = (props) => (
  <Table
    size="middle"
    bordered
    sticky
    pagination={{ pageSize: 20, showSizeChanger: true, showQuickJumper: true }}
    rowSelection={{ type: 'checkbox' }}
    {...props}
  />
);

// ================================
// EXPORTS
// ================================

export default Table;

export type {
  TableProps,
  Column,
  PaginationConfig,
  RowSelectionConfig,
  ExpandableConfig,
  FilterOption,
  SortConfig,
  TableLocale,
};

/**
 * 📊 Example Usage:
 * 
 * ```tsx
 * const columns = [
 *   {
 *     key: 'name',
 *     title: 'Name',
 *     dataIndex: 'name',
 *     sortable: true,
 *     filterable: true,
 *   },
 *   {
 *     key: 'age',
 *     title: 'Age',
 *     dataIndex: 'age',
 *     sortable: true,
 *     align: 'center',
 *   },
 *   {
 *     key: 'actions',
 *     title: 'Actions',
 *     render: (_, record) => (
 *       <Button onClick={() => handleEdit(record)}>
 *         Edit
 *       </Button>
 *     ),
 *   },
 * ];
 * 
 * const dataSource = [
 *   { key: '1', name: 'John Doe', age: 30 },
 *   { key: '2', name: 'Jane Smith', age: 25 },
 * ];
 * 
 * <Table
 *   columns={columns}
 *   dataSource={dataSource}
 *   pagination={{ pageSize: 10 }}
 *   rowSelection={{ type: 'checkbox' }}
 * />
 * ```
 */