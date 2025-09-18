/**
 * 🃏 Card Component Template - UI Component Templates
 * =================================================
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

import React, { useState, useRef, useCallback } from 'react';
import styled, { css, keyframes } from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';

// ================================
// TYPES & INTERFACES
// ================================

export interface CardAction {
  id: string;
  label: string;
  icon?: React.ReactNode;
  onClick?: (action: CardAction, event: React.MouseEvent) => void;
  disabled?: boolean;
  loading?: boolean;
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  size?: 'small' | 'medium' | 'large';
}

export interface CardProps {
  title?: React.ReactNode;
  subtitle?: React.ReactNode;
  children?: React.ReactNode;
  cover?: React.ReactNode;
  avatar?: React.ReactNode;
  actions?: CardAction[];
  extra?: React.ReactNode;
  variant?: 'default' | 'bordered' | 'shadow' | 'elevated' | 'minimal' | 'glass';
  size?: 'small' | 'medium' | 'large';
  hoverable?: boolean;
  clickable?: boolean;
  loading?: boolean;
  selected?: boolean;
  disabled?: boolean;
  direction?: 'vertical' | 'horizontal';
  width?: string | number;
  height?: string | number;
  padding?: string | number;
  borderRadius?: string | number;
  background?: string;
  headerStyle?: React.CSSProperties;
  bodyStyle?: React.CSSProperties;
  actionsStyle?: React.CSSProperties;
  className?: string;
  style?: React.CSSProperties;
  onClick?: (event: React.MouseEvent) => void;
  onDoubleClick?: (event: React.MouseEvent) => void;
  onHover?: (hovering: boolean) => void;
  'data-testid'?: string;
}

export interface CardSectionProps {
  children: React.ReactNode;
  className?: string;
  style?: React.CSSProperties;
}

// ================================
// ANIMATIONS
// ================================

const fadeIn = keyframes`
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
`;

const scaleIn = keyframes`
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
`;

const shimmer = keyframes`
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
`;

const pulse = keyframes`
  0% { opacity: 1; }
  50% { opacity: 0.7; }
  100% { opacity: 1; }
`;

const glow = keyframes`
  0%, 100% { box-shadow: 0 0 5px rgba(59, 130, 246, 0.3); }
  50% { box-shadow: 0 0 20px rgba(59, 130, 246, 0.6); }
`;

// ================================
// STYLED COMPONENTS
// ================================

const CardContainer = styled(motion.div)<{
  variant: string;
  size: string;
  hoverable?: boolean;
  clickable?: boolean;
  selected?: boolean;
  disabled?: boolean;
  direction: string;
  width?: string | number;
  height?: string | number;
  customPadding?: string | number;
  customBorderRadius?: string | number;
  customBackground?: string;
}>`
  position: relative;
  display: flex;
  flex-direction: ${({ direction }) => direction === 'horizontal' ? 'row' : 'column'};
  border-radius: ${({ customBorderRadius }) => 
    customBorderRadius 
      ? typeof customBorderRadius === 'number' 
        ? `${customBorderRadius}px` 
        : customBorderRadius
      : '12px'
  };
  overflow: hidden;
  transition: all 0.3s ease;
  background: ${({ customBackground, variant }) => {
    if (customBackground) return customBackground;
    
    switch (variant) {
      case 'glass':
        return 'rgba(255, 255, 255, 0.1)';
      case 'minimal':
        return 'transparent';
      default:
        return '#ffffff';
    }
  }};
  
  ${({ width }) => width && css`
    width: ${typeof width === 'number' ? `${width}px` : width};
  `}
  
  ${({ height }) => height && css`
    height: ${typeof height === 'number' ? `${height}px` : height};
  `}
  
  ${({ variant }) => {
    switch (variant) {
      case 'bordered':
        return css`
          border: 1px solid rgba(0, 0, 0, 0.1);
        `;
      case 'shadow':
        return css`
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        `;
      case 'elevated':
        return css`
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        `;
      case 'glass':
        return css`
          backdrop-filter: blur(10px);
          border: 1px solid rgba(255, 255, 255, 0.2);
          box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        `;
      case 'minimal':
        return css`
          border: none;
          box-shadow: none;
        `;
      default:
        return css`
          border: 1px solid rgba(0, 0, 0, 0.06);
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        `;
    }
  }}
  
  ${({ size, customPadding }) => {
    if (customPadding) {
      return css`
        padding: ${typeof customPadding === 'number' ? `${customPadding}px` : customPadding};
      `;
    }
    
    switch (size) {
      case 'small':
        return css`
          font-size: 0.875rem;
          
          .card-header {
            padding: 12px 16px;
          }
          
          .card-body {
            padding: 16px;
          }
          
          .card-actions {
            padding: 12px 16px;
          }
        `;
      case 'large':
        return css`
          font-size: 1.125rem;
          
          .card-header {
            padding: 24px 32px;
          }
          
          .card-body {
            padding: 32px;
          }
          
          .card-actions {
            padding: 24px 32px;
          }
        `;
      default:
        return css`
          font-size: 1rem;
          
          .card-header {
            padding: 16px 24px;
          }
          
          .card-body {
            padding: 24px;
          }
          
          .card-actions {
            padding: 16px 24px;
          }
        `;
    }
  }}
  
  ${({ hoverable, clickable }) => (hoverable || clickable) && css`
    cursor: pointer;
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
      
      .card-cover img {
        transform: scale(1.05);
      }
    }
  `}
  
  ${({ selected }) => selected && css`
    border-color: #3b82f6;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
    animation: ${glow} 2s ease-in-out infinite;
  `}
  
  ${({ disabled }) => disabled && css`
    opacity: 0.6;
    pointer-events: none;
    filter: grayscale(50%);
  `}
  
  ${({ direction }) => direction === 'horizontal' && css`
    .card-cover {
      width: 200px;
      flex-shrink: 0;
    }
    
    .card-content {
      flex: 1;
      display: flex;
      flex-direction: column;
    }
  `}
`;

const CardCover = styled.div`
  position: relative;
  overflow: hidden;
  width: 100%;
  
  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.3s ease;
  }
  
  .cover-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(
      to bottom,
      transparent 0%,
      rgba(0, 0, 0, 0.1) 50%,
      rgba(0, 0, 0, 0.3) 100%
    );
    display: flex;
    align-items: flex-end;
    padding: 16px;
    color: white;
    opacity: 0;
    transition: opacity 0.3s ease;
  }
  
  &:hover .cover-overlay {
    opacity: 1;
  }
`;

const CardHeader = styled.div<{ hasAvatar?: boolean; customStyle?: React.CSSProperties }>`
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  
  ${({ customStyle }) => customStyle && css`
    ${customStyle as any}
  `}
  
  .card-meta {
    display: flex;
    align-items: center;
    gap: 12px;
    flex: 1;
    min-width: 0;
  }
  
  .card-avatar {
    flex-shrink: 0;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    overflow: hidden;
    
    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
  }
  
  .card-title-section {
    flex: 1;
    min-width: 0;
  }
  
  .card-title {
    margin: 0;
    font-size: 1.125em;
    font-weight: 600;
    line-height: 1.3;
    color: #111827;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  
  .card-subtitle {
    margin: 4px 0 0 0;
    font-size: 0.875em;
    color: #6b7280;
    line-height: 1.4;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  
  .card-extra {
    flex-shrink: 0;
    margin-left: 12px;
  }
`;

const CardBody = styled.div<{ customStyle?: React.CSSProperties }>`
  flex: 1;
  color: #374151;
  line-height: 1.6;
  
  ${({ customStyle }) => customStyle && css`
    ${customStyle as any}
  `}
  
  p:first-child {
    margin-top: 0;
  }
  
  p:last-child {
    margin-bottom: 0;
  }
`;

const CardActions = styled.div<{ customStyle?: React.CSSProperties }>`
  display: flex;
  align-items: center;
  gap: 8px;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
  
  ${({ customStyle }) => customStyle && css`
    ${customStyle as any}
  `}
  
  &.actions-end {
    justify-content: flex-end;
  }
  
  &.actions-center {
    justify-content: center;
  }
  
  &.actions-between {
    justify-content: space-between;
  }
`;

const CardAction = styled.button<{
  variant: string;
  size: string;
  loading?: boolean;
}>`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  
  ${({ size }) => {
    switch (size) {
      case 'small':
        return css`
          padding: 6px 12px;
          font-size: 0.75rem;
        `;
      case 'large':
        return css`
          padding: 12px 20px;
          font-size: 1rem;
        `;
      default:
        return css`
          padding: 8px 16px;
          font-size: 0.875rem;
        `;
    }
  }}
  
  ${({ variant }) => {
    switch (variant) {
      case 'primary':
        return css`
          background: #3b82f6;
          color: white;
          
          &:hover:not(:disabled) {
            background: #2563eb;
            transform: translateY(-1px);
          }
        `;
      case 'secondary':
        return css`
          background: #f3f4f6;
          color: #374151;
          
          &:hover:not(:disabled) {
            background: #e5e7eb;
          }
        `;
      case 'ghost':
        return css`
          background: transparent;
          color: #6b7280;
          
          &:hover:not(:disabled) {
            background: #f3f4f6;
            color: #374151;
          }
        `;
      case 'danger':
        return css`
          background: #ef4444;
          color: white;
          
          &:hover:not(:disabled) {
            background: #dc2626;
            transform: translateY(-1px);
          }
        `;
      default:
        return css`
          background: #f3f4f6;
          color: #374151;
          
          &:hover:not(:disabled) {
            background: #e5e7eb;
          }
        `;
    }
  }}
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }
  
  ${({ loading }) => loading && css`
    pointer-events: none;
    
    &::before {
      content: '';
      position: absolute;
      width: 14px;
      height: 14px;
      border: 2px solid transparent;
      border-top-color: currentColor;
      border-radius: 50%;
      animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
      to { transform: rotate(360deg); }
    }
  `}
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
  z-index: 10;
  border-radius: inherit;
`;

const LoadingSkeleton = styled.div`
  .skeleton-line {
    height: 16px;
    background: linear-gradient(
      90deg,
      #f0f0f0 25%,
      #e0e0e0 50%,
      #f0f0f0 75%
    );
    background-size: 200% 100%;
    animation: ${shimmer} 1.5s infinite;
    border-radius: 4px;
    margin-bottom: 8px;
    
    &.title {
      height: 20px;
      width: 70%;
    }
    
    &.subtitle {
      height: 14px;
      width: 50%;
    }
    
    &.content {
      width: 100%;
      
      &:nth-child(2) { width: 90%; }
      &:nth-child(3) { width: 80%; }
    }
  }
  
  .skeleton-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: linear-gradient(
      90deg,
      #f0f0f0 25%,
      #e0e0e0 50%,
      #f0f0f0 75%
    );
    background-size: 200% 100%;
    animation: ${shimmer} 1.5s infinite;
  }
`;

// ================================
// SUB COMPONENTS
// ================================

export const CardHeader: React.FC<CardSectionProps> = ({ children, className, style }) => (
  <div className={`card-header ${className || ''}`} style={style}>
    {children}
  </div>
);

export const CardBody: React.FC<CardSectionProps> = ({ children, className, style }) => (
  <div className={`card-body ${className || ''}`} style={style}>
    {children}
  </div>
);

export const CardActions: React.FC<CardSectionProps> = ({ children, className, style }) => (
  <div className={`card-actions ${className || ''}`} style={style}>
    {children}
  </div>
);

// ================================
// MAIN COMPONENT
// ================================

export const Card: React.FC<CardProps> = ({
  title,
  subtitle,
  children,
  cover,
  avatar,
  actions = [],
  extra,
  variant = 'default',
  size = 'medium',
  hoverable = false,
  clickable = false,
  loading = false,
  selected = false,
  disabled = false,
  direction = 'vertical',
  width,
  height,
  padding,
  borderRadius,
  background,
  headerStyle,
  bodyStyle,
  actionsStyle,
  className,
  style,
  onClick,
  onDoubleClick,
  onHover,
  'data-testid': testId,
}) => {
  const [isHovering, setIsHovering] = useState(false);
  const cardRef = useRef<HTMLDivElement>(null);
  
  const handleMouseEnter = useCallback(() => {
    setIsHovering(true);
    onHover?.(true);
  }, [onHover]);
  
  const handleMouseLeave = useCallback(() => {
    setIsHovering(false);
    onHover?.(false);
  }, [onHover]);
  
  const handleClick = useCallback((event: React.MouseEvent) => {
    if (disabled) return;
    onClick?.(event);
  }, [onClick, disabled]);
  
  const handleDoubleClick = useCallback((event: React.MouseEvent) => {
    if (disabled) return;
    onDoubleClick?.(event);
  }, [onDoubleClick, disabled]);
  
  const handleActionClick = useCallback((action: CardAction, event: React.MouseEvent) => {
    event.stopPropagation();
    if (action.disabled || action.loading) return;
    action.onClick?.(action, event);
  }, []);
  
  const renderActions = () => {
    if (actions.length === 0) return null;
    
    return (
      <CardActions className="card-actions" style={actionsStyle}>
        {actions.map((action) => (
          <CardAction
            key={action.id}
            variant={action.variant || 'secondary'}
            size={action.size || size}
            loading={action.loading}
            disabled={action.disabled}
            onClick={(e) => handleActionClick(action, e)}
          >
            {action.loading ? null : action.icon && <span>{action.icon}</span>}
            {action.label}
          </CardAction>
        ))}
      </CardActions>
    );
  };
  
  const renderLoadingSkeleton = () => (
    <LoadingSkeleton>
      <div className="card-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {avatar && <div className="skeleton-avatar" />}
          <div style={{ flex: 1 }}>
            <div className="skeleton-line title" />
            {subtitle && <div className="skeleton-line subtitle" />}
          </div>
        </div>
      </div>
      
      <div className="card-body">
        <div className="skeleton-line content" />
        <div className="skeleton-line content" />
        <div className="skeleton-line content" />
      </div>
      
      {actions.length > 0 && (
        <div className="card-actions">
          <div className="skeleton-line" style={{ width: '80px', height: '32px' }} />
          <div className="skeleton-line" style={{ width: '60px', height: '32px' }} />
        </div>
      )}
    </LoadingSkeleton>
  );
  
  const hasHeader = title || subtitle || avatar || extra;
  const hasContent = children || loading;
  const hasActions = actions.length > 0;
  
  return (
    <CardContainer
      ref={cardRef}
      variant={variant}
      size={size}
      hoverable={hoverable}
      clickable={clickable || !!onClick}
      selected={selected}
      disabled={disabled}
      direction={direction}
      width={width}
      height={height}
      customPadding={padding}
      customBorderRadius={borderRadius}
      customBackground={background}
      className={className}
      style={style}
      onClick={handleClick}
      onDoubleClick={handleDoubleClick}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      data-testid={testId}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={
        hoverable || clickable
          ? {
              y: -4,
              transition: { duration: 0.2 },
            }
          : undefined
      }
    >
      {cover && (
        <CardCover className="card-cover">
          {cover}
          <div className="cover-overlay">
            <div>
              {title && <h3 style={{ margin: 0, fontSize: '1.25rem' }}>{title}</h3>}
              {subtitle && <p style={{ margin: 0, opacity: 0.9 }}>{subtitle}</p>}
            </div>
          </div>
        </CardCover>
      )}
      
      <div className={direction === 'horizontal' ? 'card-content' : ''}>
        {hasHeader && (
          <CardHeader className="card-header" style={headerStyle}>
            <div className="card-meta">
              {avatar && <div className="card-avatar">{avatar}</div>}
              
              {(title || subtitle) && (
                <div className="card-title-section">
                  {title && <h3 className="card-title">{title}</h3>}
                  {subtitle && <p className="card-subtitle">{subtitle}</p>}
                </div>
              )}
            </div>
            
            {extra && <div className="card-extra">{extra}</div>}
          </CardHeader>
        )}
        
        {hasContent && (
          <CardBody className="card-body" style={bodyStyle}>
            {loading ? renderLoadingSkeleton() : children}
          </CardBody>
        )}
        
        {hasActions && renderActions()}
      </div>
      
      {loading && !children && (
        <LoadingOverlay>
          <div style={{ textAlign: 'center' }}>
            <div style={{ marginBottom: '8px', fontSize: '24px' }}>⏳</div>
            <div>Loading...</div>
          </div>
        </LoadingOverlay>
      )}
    </CardContainer>
  );
};

// ================================
// UTILITY COMPONENTS
// ================================

export const SimpleCard: React.FC<Partial<CardProps>> = (props) => (
  <Card variant="minimal" size="small" {...props} />
);

export const BorderedCard: React.FC<Partial<CardProps>> = (props) => (
  <Card variant="bordered" hoverable {...props} />
);

export const ElevatedCard: React.FC<Partial<CardProps>> = (props) => (
  <Card variant="elevated" hoverable {...props} />
);

export const GlassCard: React.FC<Partial<CardProps>> = (props) => (
  <Card variant="glass" hoverable {...props} />
);

export const ProductCard: React.FC<Partial<CardProps>> = (props) => (
  <Card
    variant="shadow"
    hoverable
    clickable
    actions={[
      { id: 'add-to-cart', label: 'Add to Cart', variant: 'primary' },
      { id: 'view-details', label: 'View', variant: 'ghost' },
    ]}
    {...props}
  />
);

export const ProfileCard: React.FC<Partial<CardProps>> = (props) => (
  <Card
    variant="bordered"
    hoverable
    direction="horizontal"
    actions={[
      { id: 'message', label: 'Message', variant: 'primary' },
      { id: 'follow', label: 'Follow', variant: 'secondary' },
    ]}
    {...props}
  />
);

// ================================
// EXPORTS
// ================================

export default Card;

export type {
  CardProps,
  CardAction,
  CardSectionProps,
};

/**
 * 🃏 Example Usage:
 * 
 * ```tsx
 * // Basic Card
 * <Card
 *   title="Card Title"
 *   subtitle="Card subtitle"
 *   actions={[
 *     { id: 'save', label: 'Save', variant: 'primary' },
 *     { id: 'cancel', label: 'Cancel', variant: 'secondary' }
 *   ]}
 * >
 *   <p>Card content goes here...</p>
 * </Card>
 * 
 * // Product Card with Cover
 * <Card
 *   cover={<img src="/product.jpg" alt="Product" />}
 *   title="Product Name"
 *   subtitle="$99.99"
 *   hoverable
 *   clickable
 *   actions={[
 *     { id: 'buy', label: 'Buy Now', variant: 'primary', icon: '🛒' },
 *     { id: 'wishlist', label: 'Wishlist', variant: 'ghost', icon: '❤️' }
 *   ]}
 * >
 *   <p>Product description...</p>
 * </Card>
 * 
 * // Profile Card with Avatar
 * <Card
 *   avatar={<img src="/avatar.jpg" alt="User" />}
 *   title="John Doe"
 *   subtitle="Software Engineer"
 *   extra={<button>•••</button>}
 *   variant="elevated"
 *   direction="horizontal"
 * >
 *   <p>Bio information...</p>
 * </Card>
 * ```
 */