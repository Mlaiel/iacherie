/**
 * 📊 Table Component Template - Enterprise Data Table
 * ===================================================
 * 
 * © 2025 Fahed Mlaiel <mlaiel@live.de>
 * TOUS DROITS RÉSERVÉS - Propriété Intellectuelle Protégée
 * 
 * Enterprise-grade data table with advanced features:
 * sorting, filtering, pagination, virtualization, selection, export functionality.
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
  useMemo, 
  useCallback, 
  useRef,
  forwardRef,
  useImperativeHandle
} from 'react';

// ========================================
// 📝 TYPE DEFINITIONS
// ========================================

interface TableColumn<T = any> {
  key: string;
  title: string;
  dataIndex?: keyof T;
  width?: number | string;
  minWidth?: number;
  maxWidth?: number;
  sortable?: boolean;
  filterable?: boolean;
  filterType?: 'text' | 'select' | 'date' | 'number' | 'boolean';
  filterOptions?: Array<{ label: string; value: any }>;
  fixed?: 'left' | 'right';
  align?: 'left' | 'center' | 'right';
  ellipsis?: boolean;
  render?: (value: any, record: T, index: number) => React.ReactNode;
  renderHeader?: () => React.ReactNode;
  onHeaderClick?: () => void;
  className?: string;
  headerClassName?: string;
}

interface TableRow<T = any> {
  id: string | number;
  data: T;
  selected?: boolean;
  disabled?: boolean;
  className?: string;
  style?: React.CSSProperties;
}

interface TableProps<T = any> {
  columns: TableColumn<T>[];
  data: T[];
  rowKey?: keyof T | ((record: T) => string | number);
  loading?: boolean;
  pagination?: PaginationConfig | false;
  selection?: SelectionConfig<T>;
  scroll?: { x?: number | string; y?: number | string };
  size?: 'small' | 'medium' | 'large';
  bordered?: boolean;
  striped?: boolean;
  hoverable?: boolean;
  sortable?: boolean;
  filterable?: boolean;
  resizable?: boolean;
  virtual?: boolean;
  itemHeight?: number;
  expandable?: ExpandableConfig<T>;
  summary?: (data: T[]) => React.ReactNode;
  emptyText?: React.ReactNode;
  locale?: TableLocale;
  onRow?: (record: T, index: number) => TableRowProps;
  onHeaderRow?: (columns: TableColumn<T>[], index: number) => TableHeaderRowProps;
  onChange?: (pagination: PaginationConfig, filters: Record<string, any>, sorter: SorterConfig) => void;
  onSelectionChange?: (selectedRowKeys: (string | number)[], selectedRows: T[]) => void;
  onExpand?: (expanded: boolean, record: T) => void;
  onResize?: (columnIndex: number, width: number) => void;
  className?: string;
  tableClassName?: string;
  headerClassName?: string;
  bodyClassName?: string;
  testId?: string;
}

interface PaginationConfig {
  current?: number;
  pageSize?: number;
  total?: number;
  showSizeChanger?: boolean;
  showQuickJumper?: boolean;
  showTotal?: (total: number, range: [number, number]) => React.ReactNode;
  pageSizeOptions?: string[];
  position?: 'top' | 'bottom' | 'both';
}

interface SelectionConfig<T = any> {
  type?: 'checkbox' | 'radio';
  selectedRowKeys?: (string | number)[];
  selections?: SelectionItem[];
  onSelect?: (record: T, selected: boolean, selectedRows: T[], nativeEvent: Event) => void;
  onSelectAll?: (selected: boolean, selectedRows: T[], changeRows: T[]) => void;
  getCheckboxProps?: (record: T) => CheckboxProps;
  columnWidth?: number | string;
  columnTitle?: React.ReactNode;
  fixed?: boolean;
}

interface ExpandableConfig<T = any> {
  expandedRowKeys?: (string | number)[];
  defaultExpandedRowKeys?: (string | number)[];
  expandedRowRender?: (record: T, index: number, indent: number, expanded: boolean) => React.ReactNode;
  expandRowByClick?: boolean;
  expandIcon?: (props: ExpandIconProps<T>) => React.ReactNode;
  indentSize?: number;
  rowExpandable?: (record: T) => boolean;
  columnWidth?: number | string;
  columnTitle?: React.ReactNode;
  fixed?: boolean;
}

interface SorterConfig {
  field?: string;
  order?: 'ascend' | 'descend' | null;
  column?: TableColumn;
}

interface TableLocale {
  filterTitle?: string;
  filterConfirm?: string;
  filterReset?: string;
  emptyText?: string;
  selectAll?: string;
  selectInvert?: string;
  sortTitle?: string;
}

interface TableRowProps {
  onClick?: (event: React.MouseEvent<HTMLTableRowElement>) => void;
  onDoubleClick?: (event: React.MouseEvent<HTMLTableRowElement>) => void;
  onContextMenu?: (event: React.MouseEvent<HTMLTableRowElement>) => void;
  onMouseEnter?: (event: React.MouseEvent<HTMLTableRowElement>) => void;
  onMouseLeave?: (event: React.MouseEvent<HTMLTableRowElement>) => void;
  className?: string;
  style?: React.CSSProperties;
}

interface TableHeaderRowProps {
  onClick?: (event: React.MouseEvent<HTMLTableRowElement>) => void;
  className?: string;
  style?: React.CSSProperties;
}

interface SelectionItem {
  key: string;
  text: React.ReactNode;
  onSelect?: (currentPageData: any[]) => void;
}

interface CheckboxProps {
  disabled?: boolean;
  indeterminate?: boolean;
}

interface ExpandIconProps<T> {
  prefixCls: string;
  expanded: boolean;
  onExpand: (record: T, event: React.MouseEvent<HTMLElement>) => void;
  record: T;
  expandable: boolean;
}

interface TableRef<T = any> {
  scrollTo: (config: { index?: number; key?: string; top?: number }) => void;
  getSelectedRows: () => T[];
  clearSelection: () => void;
  expandAll: () => void;
  collapseAll: () => void;
  refresh: () => void;
  exportData: (format?: 'csv' | 'json' | 'xlsx') => void;
}

// ========================================
// 🎨 TABLE STYLES
// ========================================

const getTableStyles = (size: string, bordered: boolean, striped: boolean, hoverable: boolean) => ({
  container: {
    position: 'relative' as const,
    overflow: 'auto',
    backgroundColor: '#ffffff'
  },

  table: {
    width: '100%',
    borderCollapse: 'collapse' as const,
    fontSize: size === 'small' ? '0.875rem' : size === 'large' ? '1rem' : '0.9375rem',
    lineHeight: '1.5',
    color: '#374151'
  },

  thead: {
    backgroundColor: '#f9fafb',
    borderBottom: bordered ? '2px solid #e5e7eb' : '1px solid #e5e7eb'
  },

  th: {
    padding: size === 'small' ? '0.5rem 0.75rem' : 
             size === 'large' ? '1rem 1.25rem' : '0.75rem 1rem',
    textAlign: 'left' as const,
    fontWeight: '600',
    color: '#374151',
    backgroundColor: '#f9fafb',
    borderRight: bordered ? '1px solid #e5e7eb' : 'none',
    position: 'relative' as const,
    whiteSpace: 'nowrap' as const
  },

  tbody: {
    backgroundColor: '#ffffff'
  },

  tr: {
    borderBottom: '1px solid #e5e7eb',
    ...(striped && {
      '&:nth-child(even)': {
        backgroundColor: '#f9fafb'
      }
    }),
    ...(hoverable && {
      '&:hover': {
        backgroundColor: '#f3f4f6'
      }
    })
  },

  td: {
    padding: size === 'small' ? '0.5rem 0.75rem' : 
             size === 'large' ? '1rem 1.25rem' : '0.75rem 1rem',
    borderRight: bordered ? '1px solid #e5e7eb' : 'none',
    verticalAlign: 'top' as const
  },

  loading: {
    position: 'absolute' as const,
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(255, 255, 255, 0.8)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 10
  },

  empty: {
    textAlign: 'center' as const,
    padding: '2rem',
    color: '#6b7280'
  },

  pagination: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '1rem 0',
    borderTop: '1px solid #e5e7eb'
  }
});

// ========================================
// 📊 TABLE COMPONENT
// ========================================

export const Table = forwardRef<TableRef, TableProps>(({
  columns = [],
  data = [],
  rowKey = 'id',
  loading = false,
  pagination = false,
  selection,
  scroll,
  size = 'medium',
  bordered = false,
  striped = false,
  hoverable = true,
  sortable = true,
  filterable = true,
  resizable = false,
  virtual = false,
  itemHeight = 48,
  expandable,
  summary,
  emptyText = 'No data',
  locale = {},
  onRow,
  onHeaderRow,
  onChange,
  onSelectionChange,
  onExpand,
  onResize,
  className = '',
  tableClassName = '',
  headerClassName = '',
  bodyClassName = '',
  testId = 'table'
}, ref) => {
  // State management
  const [sortConfig, setSortConfig] = useState<SorterConfig>({});
  const [filterConfig, setFilterConfig] = useState<Record<string, any>>({});
  const [selectedRowKeys, setSelectedRowKeys] = useState<(string | number)[]>(
    selection?.selectedRowKeys || []
  );
  const [expandedRowKeys, setExpandedRowKeys] = useState<(string | number)[]>(
    expandable?.expandedRowKeys || expandable?.defaultExpandedRowKeys || []
  );
  const [currentPage, setCurrentPage] = useState(pagination ? pagination.current || 1 : 1);
  const [pageSize, setPageSize] = useState(pagination ? pagination.pageSize || 10 : 10);
  const [columnWidths, setColumnWidths] = useState<Record<string, number>>({});

  const tableRef = useRef<HTMLTableElement>(null);
  const headerRef = useRef<HTMLTableSectionElement>(null);
  const bodyRef = useRef<HTMLTableSectionElement>(null);

  // Get row key
  const getRowKey = useCallback((record: any, index: number): string | number => {
    if (typeof rowKey === 'function') {
      return rowKey(record);
    }
    return record[rowKey] || index;
  }, [rowKey]);

  // Filtered and sorted data
  const processedData = useMemo(() => {
    let result = [...data];

    // Apply filters
    Object.entries(filterConfig).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        const column = columns.find(col => col.key === key);
        if (column) {
          result = result.filter(record => {
            const recordValue = column.dataIndex ? record[column.dataIndex] : record[key];
            
            if (column.filterType === 'text') {
              return String(recordValue).toLowerCase().includes(String(value).toLowerCase());
            } else if (column.filterType === 'select') {
              return recordValue === value;
            } else if (column.filterType === 'number') {
              return Number(recordValue) === Number(value);
            } else if (column.filterType === 'boolean') {
              return Boolean(recordValue) === Boolean(value);
            }
            
            return true;
          });
        }
      }
    });

    // Apply sorting
    if (sortConfig.field && sortConfig.order) {
      const column = columns.find(col => col.key === sortConfig.field);
      if (column) {
        result.sort((a, b) => {
          const aValue = column.dataIndex ? a[column.dataIndex] : a[sortConfig.field!];
          const bValue = column.dataIndex ? b[column.dataIndex] : b[sortConfig.field!];
          
          if (aValue < bValue) return sortConfig.order === 'ascend' ? -1 : 1;
          if (aValue > bValue) return sortConfig.order === 'ascend' ? 1 : -1;
          return 0;
        });
      }
    }

    return result;
  }, [data, filterConfig, sortConfig, columns]);

  // Paginated data
  const paginatedData = useMemo(() => {
    if (!pagination) return processedData;
    
    const start = (currentPage - 1) * pageSize;
    const end = start + pageSize;
    return processedData.slice(start, end);
  }, [processedData, pagination, currentPage, pageSize]);

  // Selected rows
  const selectedRows = useMemo(() => {
    return processedData.filter(record => 
      selectedRowKeys.includes(getRowKey(record, 0))
    );
  }, [processedData, selectedRowKeys, getRowKey]);

  // Handle sorting
  const handleSort = useCallback((column: TableColumn) => {
    if (!column.sortable) return;

    const newSortConfig: SorterConfig = {
      field: column.key,
      column
    };

    if (sortConfig.field === column.key) {
      // Cycle through: ascend -> descend -> null
      if (sortConfig.order === 'ascend') {
        newSortConfig.order = 'descend';
      } else if (sortConfig.order === 'descend') {
        newSortConfig.order = null;
        newSortConfig.field = undefined;
      } else {
        newSortConfig.order = 'ascend';
      }
    } else {
      newSortConfig.order = 'ascend';
    }

    setSortConfig(newSortConfig);
    onChange?.(
      pagination ? { current: currentPage, pageSize, total: processedData.length } : {} as any,
      filterConfig,
      newSortConfig
    );
  }, [sortConfig, pagination, currentPage, pageSize, processedData.length, filterConfig, onChange]);

  // Handle filtering
  const handleFilter = useCallback((columnKey: string, value: any) => {
    const newFilterConfig = { ...filterConfig, [columnKey]: value };
    setFilterConfig(newFilterConfig);
    setCurrentPage(1); // Reset to first page when filtering
    
    onChange?.(
      pagination ? { current: 1, pageSize, total: processedData.length } : {} as any,
      newFilterConfig,
      sortConfig
    );
  }, [filterConfig, pagination, pageSize, processedData.length, sortConfig, onChange]);

  // Handle selection
  const handleRowSelect = useCallback((record: any, selected: boolean) => {
    const key = getRowKey(record, 0);
    let newSelectedKeys: (string | number)[];

    if (selection?.type === 'radio') {
      newSelectedKeys = selected ? [key] : [];
    } else {
      newSelectedKeys = selected 
        ? [...selectedRowKeys, key]
        : selectedRowKeys.filter(k => k !== key);
    }

    setSelectedRowKeys(newSelectedKeys);
    
    const newSelectedRows = processedData.filter(r => 
      newSelectedKeys.includes(getRowKey(r, 0))
    );
    
    onSelectionChange?.(newSelectedKeys, newSelectedRows);
    selection?.onSelect?.(record, selected, newSelectedRows, {} as Event);
  }, [selection, selectedRowKeys, getRowKey, processedData, onSelectionChange]);

  // Handle select all
  const handleSelectAll = useCallback((selected: boolean) => {
    const currentPageKeys = paginatedData.map((record, index) => getRowKey(record, index));
    let newSelectedKeys: (string | number)[];

    if (selected) {
      // Add all current page keys
      newSelectedKeys = [...new Set([...selectedRowKeys, ...currentPageKeys])];
    } else {
      // Remove all current page keys
      newSelectedKeys = selectedRowKeys.filter(k => !currentPageKeys.includes(k));
    }

    setSelectedRowKeys(newSelectedKeys);
    
    const newSelectedRows = processedData.filter(r => 
      newSelectedKeys.includes(getRowKey(r, 0))
    );
    
    onSelectionChange?.(newSelectedKeys, newSelectedRows);
    selection?.onSelectAll?.(selected, newSelectedRows, paginatedData);
  }, [paginatedData, selectedRowKeys, getRowKey, processedData, onSelectionChange, selection]);

  // Handle expand
  const handleExpand = useCallback((record: any, expanded: boolean) => {
    const key = getRowKey(record, 0);
    let newExpandedKeys: (string | number)[];

    if (expanded) {
      newExpandedKeys = [...expandedRowKeys, key];
    } else {
      newExpandedKeys = expandedRowKeys.filter(k => k !== key);
    }

    setExpandedRowKeys(newExpandedKeys);
    onExpand?.(expanded, record);
  }, [expandedRowKeys, getRowKey, onExpand]);

  // Handle pagination
  const handlePageChange = useCallback((page: number, size?: number) => {
    setCurrentPage(page);
    if (size !== undefined) {
      setPageSize(size);
    }
    
    onChange?.(
      { current: page, pageSize: size || pageSize, total: processedData.length },
      filterConfig,
      sortConfig
    );
  }, [pageSize, processedData.length, filterConfig, sortConfig, onChange]);

  // Export data function
  const exportData = useCallback((format: 'csv' | 'json' | 'xlsx' = 'csv') => {
    const exportRows = selectedRows.length > 0 ? selectedRows : processedData;
    
    if (format === 'csv') {
      const headers = columns.map(col => col.title).join(',');
      const rows = exportRows.map(record => 
        columns.map(col => {
          const value = col.dataIndex ? record[col.dataIndex] : record[col.key];
          return `"${String(value).replace(/"/g, '""')}"`;
        }).join(',')
      );
      
      const csvContent = [headers, ...rows].join('\n');
      const blob = new Blob([csvContent], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      
      const link = document.createElement('a');
      link.href = url;
      link.download = `table-export-${Date.now()}.csv`;
      link.click();
      
      URL.revokeObjectURL(url);
    } else if (format === 'json') {
      const jsonContent = JSON.stringify(exportRows, null, 2);
      const blob = new Blob([jsonContent], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      
      const link = document.createElement('a');
      link.href = url;
      link.download = `table-export-${Date.now()}.json`;
      link.click();
      
      URL.revokeObjectURL(url);
    }
  }, [selectedRows, processedData, columns]);

  // Imperative handle
  useImperativeHandle(ref, () => ({
    scrollTo: (config) => {
      if (config.top !== undefined && bodyRef.current) {
        bodyRef.current.scrollTop = config.top;
      }
    },
    getSelectedRows: () => selectedRows,
    clearSelection: () => {
      setSelectedRowKeys([]);
      onSelectionChange?.([], []);
    },
    expandAll: () => {
      const allKeys = processedData.map((record, index) => getRowKey(record, index));
      setExpandedRowKeys(allKeys);
    },
    collapseAll: () => {
      setExpandedRowKeys([]);
    },
    refresh: () => {
      // Force re-render
      setCurrentPage(1);
    },
    exportData
  }), [selectedRows, onSelectionChange, processedData, getRowKey, exportData]);

  const styles = getTableStyles(size, bordered, striped, hoverable);

  // Render header cell
  const renderHeaderCell = (column: TableColumn, index: number) => {
    const isSorted = sortConfig.field === column.key;
    const sortOrder = isSorted ? sortConfig.order : null;

    return (
      <th
        key={column.key}
        className={`${headerClassName} ${column.headerClassName || ''}`}
        style={{
          ...styles.th,
          width: columnWidths[column.key] || column.width,
          minWidth: column.minWidth,
          maxWidth: column.maxWidth,
          textAlign: column.align || 'left',
          ...(column.fixed && {
            position: 'sticky',
            [column.fixed]: 0,
            zIndex: 1
          })
        }}
        onClick={() => column.sortable && handleSort(column)}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span>
            {column.renderHeader ? column.renderHeader() : column.title}
          </span>
          
          {column.sortable && (
            <div style={{ marginLeft: '0.5rem', display: 'flex', flexDirection: 'column' }}>
              <span style={{ 
                color: sortOrder === 'ascend' ? '#3b82f6' : '#9ca3af',
                fontSize: '0.75rem',
                lineHeight: '1'
              }}>
                ▲
              </span>
              <span style={{ 
                color: sortOrder === 'descend' ? '#3b82f6' : '#9ca3af',
                fontSize: '0.75rem',
                lineHeight: '1'
              }}>
                ▼
              </span>
            </div>
          )}
        </div>
        
        {column.filterable && (
          <div style={{ marginTop: '0.5rem' }}>
            {column.filterType === 'select' ? (
              <select
                value={filterConfig[column.key] || ''}
                onChange={(e) => handleFilter(column.key, e.target.value)}
                style={{ width: '100%', padding: '0.25rem', fontSize: '0.875rem' }}
              >
                <option value="">All</option>
                {column.filterOptions?.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            ) : (
              <input
                type={column.filterType === 'number' ? 'number' : 'text'}
                placeholder={`Filter ${column.title}`}
                value={filterConfig[column.key] || ''}
                onChange={(e) => handleFilter(column.key, e.target.value)}
                style={{ width: '100%', padding: '0.25rem', fontSize: '0.875rem' }}
                onClick={(e) => e.stopPropagation()}
              />
            )}
          </div>
        )}
      </th>
    );
  };

  // Render data cell
  const renderDataCell = (column: TableColumn, record: any, index: number) => {
    const value = column.dataIndex ? record[column.dataIndex] : record[column.key];
    const content = column.render ? column.render(value, record, index) : value;

    return (
      <td
        key={column.key}
        className={column.className}
        style={{
          ...styles.td,
          width: columnWidths[column.key] || column.width,
          minWidth: column.minWidth,
          maxWidth: column.maxWidth,
          textAlign: column.align || 'left',
          ...(column.ellipsis && {
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap'
          }),
          ...(column.fixed && {
            position: 'sticky',
            [column.fixed]: 0,
            backgroundColor: '#ffffff',
            zIndex: 1
          })
        }}
      >
        {content}
      </td>
    );
  };

  // Render selection column
  const renderSelectionColumn = () => {
    if (!selection) return null;

    const allSelected = paginatedData.length > 0 && 
      paginatedData.every(record => selectedRowKeys.includes(getRowKey(record, 0)));
    const indeterminate = selectedRowKeys.length > 0 && !allSelected;

    return (
      <th
        style={{
          ...styles.th,
          width: selection.columnWidth || 50,
          textAlign: 'center'
        }}
      >
        {selection.type !== 'radio' && (
          <input
            type="checkbox"
            checked={allSelected}
            ref={(input) => {
              if (input) input.indeterminate = indeterminate;
            }}
            onChange={(e) => handleSelectAll(e.target.checked)}
          />
        )}
      </th>
    );
  };

  // Render row
  const renderRow = (record: any, index: number) => {
    const key = getRowKey(record, index);
    const isSelected = selectedRowKeys.includes(key);
    const isExpanded = expandedRowKeys.includes(key);
    const rowProps = onRow?.(record, index) || {};

    return (
      <React.Fragment key={key}>
        <tr
          {...rowProps}
          className={`${rowProps.className || ''} ${record.className || ''}`}
          style={{
            ...styles.tr,
            ...rowProps.style,
            ...record.style,
            ...(isSelected && {
              backgroundColor: '#e0f2fe'
            })
          }}
        >
          {selection && (
            <td style={{ ...styles.td, textAlign: 'center' }}>
              <input
                type={selection.type || 'checkbox'}
                name={selection.type === 'radio' ? 'table-selection' : undefined}
                checked={isSelected}
                onChange={(e) => handleRowSelect(record, e.target.checked)}
                disabled={selection.getCheckboxProps?.(record)?.disabled}
              />
            </td>
          )}
          
          {expandable && (
            <td style={{ ...styles.td, textAlign: 'center' }}>
              <button
                onClick={() => handleExpand(record, !isExpanded)}
                style={{ 
                  background: 'none', 
                  border: 'none', 
                  cursor: 'pointer',
                  transform: isExpanded ? 'rotate(90deg)' : 'rotate(0deg)',
                  transition: 'transform 0.2s'
                }}
              >
                ▶
              </button>
            </td>
          )}
          
          {columns.map((column, colIndex) => renderDataCell(column, record, index))}
        </tr>
        
        {expandable && isExpanded && expandable.expandedRowRender && (
          <tr>
            <td 
              colSpan={columns.length + (selection ? 1 : 0) + (expandable ? 1 : 0)}
              style={{ padding: 0, border: 'none' }}
            >
              <div style={{ padding: '1rem', backgroundColor: '#f9fafb' }}>
                {expandable.expandedRowRender(record, index, 1, true)}
              </div>
            </td>
          </tr>
        )}
      </React.Fragment>
    );
  };

  return (
    <div className={className} data-testid={testId}>
      <div style={styles.container}>
        {scroll?.y ? (
          <div style={{ maxHeight: scroll.y, overflowY: 'auto' }}>
            <table 
              ref={tableRef}
              className={tableClassName}
              style={{ ...styles.table, minWidth: scroll?.x }}
            >
              <thead ref={headerRef} style={styles.thead}>
                <tr>
                  {selection && renderSelectionColumn()}
                  {expandable && <th style={{ ...styles.th, width: 50, textAlign: 'center' }}>Expand</th>}
                  {columns.map((column, index) => renderHeaderCell(column, index))}
                </tr>
              </thead>
            </table>
            
            <div style={{ maxHeight: scroll.y, overflowY: 'auto' }}>
              <table style={{ ...styles.table, minWidth: scroll?.x }}>
                <tbody ref={bodyRef} className={bodyClassName} style={styles.tbody}>
                  {paginatedData.length > 0 ? (
                    paginatedData.map((record, index) => renderRow(record, index))
                  ) : (
                    <tr>
                      <td 
                        colSpan={columns.length + (selection ? 1 : 0) + (expandable ? 1 : 0)}
                        style={styles.empty}
                      >
                        {emptyText}
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <table 
            ref={tableRef}
            className={tableClassName}
            style={{ ...styles.table, minWidth: scroll?.x }}
          >
            <thead ref={headerRef} style={styles.thead}>
              <tr>
                {selection && renderSelectionColumn()}
                {expandable && <th style={{ ...styles.th, width: 50, textAlign: 'center' }}>Expand</th>}
                {columns.map((column, index) => renderHeaderCell(column, index))}
              </tr>
            </thead>
            <tbody ref={bodyRef} className={bodyClassName} style={styles.tbody}>
              {paginatedData.length > 0 ? (
                paginatedData.map((record, index) => renderRow(record, index))
              ) : (
                <tr>
                  <td 
                    colSpan={columns.length + (selection ? 1 : 0) + (expandable ? 1 : 0)}
                    style={styles.empty}
                  >
                    {emptyText}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        )}

        {summary && (
          <div style={{ borderTop: '2px solid #e5e7eb', padding: '1rem' }}>
            {summary(processedData)}
          </div>
        )}

        {loading && (
          <div style={styles.loading}>
            <div style={{ 
              width: '32px', 
              height: '32px', 
              border: '3px solid #f3f4f6',
              borderTopColor: '#3b82f6',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite'
            }} />
          </div>
        )}
      </div>

      {pagination && (
        <div style={styles.pagination}>
          <div>
            {pagination.showTotal && 
              pagination.showTotal(
                processedData.length, 
                [(currentPage - 1) * pageSize + 1, Math.min(currentPage * pageSize, processedData.length)]
              )
            }
          </div>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            {pagination.showSizeChanger && (
              <select
                value={pageSize}
                onChange={(e) => handlePageChange(1, Number(e.target.value))}
                style={{ padding: '0.25rem' }}
              >
                {(pagination.pageSizeOptions || ['10', '20', '50', '100']).map(size => (
                  <option key={size} value={size}>{size} / page</option>
                ))}
              </select>
            )}
            
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <button
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={currentPage <= 1}
                style={{ 
                  padding: '0.5rem 0.75rem',
                  border: '1px solid #d1d5db',
                  backgroundColor: '#ffffff',
                  cursor: currentPage <= 1 ? 'not-allowed' : 'pointer',
                  opacity: currentPage <= 1 ? 0.5 : 1
                }}
              >
                Previous
              </button>
              
              <span style={{ padding: '0 1rem' }}>
                Page {currentPage} of {Math.ceil(processedData.length / pageSize)}
              </span>
              
              <button
                onClick={() => handlePageChange(currentPage + 1)}
                disabled={currentPage >= Math.ceil(processedData.length / pageSize)}
                style={{ 
                  padding: '0.5rem 0.75rem',
                  border: '1px solid #d1d5db',
                  backgroundColor: '#ffffff',
                  cursor: currentPage >= Math.ceil(processedData.length / pageSize) ? 'not-allowed' : 'pointer',
                  opacity: currentPage >= Math.ceil(processedData.length / pageSize) ? 0.5 : 1
                }}
              >
                Next
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
});

Table.displayName = 'Table';

// ========================================
// 📦 EXPORTS
// ========================================

export { Table as default };

export type {
  TableProps,
  TableColumn,
  TableRow,
  PaginationConfig,
  SelectionConfig,
  ExpandableConfig,
  SorterConfig,
  TableRef
};

// ========================================
// 🎯 USAGE EXAMPLES
// ========================================

/*
// Basic Table
<Table
  columns={[
    { key: 'name', title: 'Name', dataIndex: 'name', sortable: true },
    { key: 'age', title: 'Age', dataIndex: 'age', sortable: true },
    { key: 'email', title: 'Email', dataIndex: 'email', filterable: true }
  ]}
  data={userData}
  pagination={{ pageSize: 10, showSizeChanger: true }}
/>

// Table with Selection
<Table
  columns={columns}
  data={data}
  selection={{
    type: 'checkbox',
    selectedRowKeys: selectedKeys,
    onSelect: (record, selected, selectedRows) => {
      console.log('Row selected:', record, selected);
    },
    onSelectAll: (selected, selectedRows, changeRows) => {
      console.log('Select all:', selected, selectedRows);
    }
  }}
  onSelectionChange={(keys, rows) => setSelectedKeys(keys)}
/>

// Table with Custom Rendering
<Table
  columns={[
    {
      key: 'avatar',
      title: 'Avatar',
      render: (value, record) => (
        <img src={record.avatar} alt="" style={{ width: 32, height: 32, borderRadius: '50%' }} />
      )
    },
    {
      key: 'name',
      title: 'Name',
      dataIndex: 'name',
      render: (value, record) => (
        <div>
          <div style={{ fontWeight: 'bold' }}>{value}</div>
          <div style={{ fontSize: '0.875rem', color: '#666' }}>{record.title}</div>
        </div>
      )
    },
    {
      key: 'actions',
      title: 'Actions',
      render: (value, record) => (
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button onClick={() => editUser(record)}>Edit</button>
          <button onClick={() => deleteUser(record)}>Delete</button>
        </div>
      )
    }
  ]}
  data={users}
/>

// Expandable Table
<Table
  columns={columns}
  data={data}
  expandable={{
    expandedRowRender: (record) => (
      <div>
        <h4>Details for {record.name}</h4>
        <p>Additional information...</p>
      </div>
    ),
    rowExpandable: (record) => record.hasDetails
  }}
/>

// Table with Export
const tableRef = useRef();

<div>
  <div style={{ marginBottom: '1rem' }}>
    <button onClick={() => tableRef.current?.exportData('csv')}>
      Export CSV
    </button>
    <button onClick={() => tableRef.current?.exportData('json')}>
      Export JSON
    </button>
  </div>
  
  <Table
    ref={tableRef}
    columns={columns}
    data={data}
    selection={{ type: 'checkbox' }}
  />
</div>
*/