/**
 * 🎨 CARD COMPONENT TEMPLATE - FRONTEND EXPERT IMPLEMENTATION
 * ===========================================================
 * 
 * Enterprise-grade card component template with:
 * - TypeScript support with strict typing
 * - Multiple variants and layouts
 * - Interactive states and animations
 * - Responsive design and accessibility
 * - Loading states and skeletons
 * - Action buttons and menus
 * - Media support (images, videos)
 * - Customizable header, body, and footer
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
  ReactNode, 
  MouseEvent, 
  useState,
  useRef,
  useEffect
} from 'react';
import styled, { css, keyframes } from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

interface CardProps {
  children?: ReactNode;
  variant?: 'default' | 'outlined' | 'filled' | 'elevated' | 'flat';
  size?: 'small' | 'medium' | 'large';
  layout?: 'vertical' | 'horizontal';
  clickable?: boolean;
  hoverable?: boolean;
  loading?: boolean;
  selected?: boolean;
  disabled?: boolean;
  borderRadius?: 'none' | 'small' | 'medium' | 'large' | 'full';
  shadow?: 'none' | 'small' | 'medium' | 'large';
  overflow?: 'visible' | 'hidden';
  onClick?: (event: MouseEvent<HTMLDivElement>) => void;
  onDoubleClick?: (event: MouseEvent<HTMLDivElement>) => void;
  className?: string;
  style?: React.CSSProperties;
}

interface CardHeaderProps {
  children?: ReactNode;
  title?: string;
  subtitle?: string;
  avatar?: ReactNode;
  action?: ReactNode;
  alignItems?: 'start' | 'center' | 'end';
  className?: string;
  style?: React.CSSProperties;
}

interface CardMediaProps {
  src?: string;
  alt?: string;
  type?: 'image' | 'video';
  aspectRatio?: '16:9' | '4:3' | '1:1' | '3:2' | 'auto';
  objectFit?: 'cover' | 'contain' | 'fill' | 'scale-down';
  loading?: 'lazy' | 'eager';
  placeholder?: ReactNode;
  overlay?: ReactNode;
  className?: string;
  style?: React.CSSProperties;
}

interface CardBodyProps {
  children?: ReactNode;
  padding?: 'none' | 'small' | 'medium' | 'large';
  className?: string;
  style?: React.CSSProperties;
}

interface CardFooterProps {
  children?: ReactNode;
  justifyContent?: 'start' | 'center' | 'end' | 'space-between' | 'space-around';
  alignItems?: 'start' | 'center' | 'end';
  className?: string;
  style?: React.CSSProperties;
}

interface CardActionsProps {
  children?: ReactNode;
  orientation?: 'horizontal' | 'vertical';
  spacing?: 'small' | 'medium' | 'large';
  className?: string;
  style?: React.CSSProperties;
}

interface CardSkeletonProps {
  lines?: number;
  showHeader?: boolean;
  showMedia?: boolean;
  showActions?: boolean;
  variant?: 'default' | 'outlined' | 'filled' | 'elevated' | 'flat';
  size?: 'small' | 'medium' | 'large';
}

// ============================================================================
// ANIMATIONS
// ============================================================================

const shimmer = keyframes`
  0% {
    background-position: -200px 0;
  }
  100% {
    background-position: calc(200px + 100%) 0;
  }
`;

const fadeIn = keyframes`
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
`;

const pulseGlow = keyframes`
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.4);
  }
  50% {
    box-shadow: 0 0 0 10px rgba(59, 130, 246, 0);
  }
`;

// ============================================================================
// STYLED COMPONENTS
// ============================================================================

const CardContainer = styled(motion.div)<{
  variant: 'default' | 'outlined' | 'filled' | 'elevated' | 'flat';
  size: 'small' | 'medium' | 'large';
  layout: 'vertical' | 'horizontal';
  clickable?: boolean;
  hoverable?: boolean;
  selected?: boolean;
  disabled?: boolean;
  borderRadius: 'none' | 'small' | 'medium' | 'large' | 'full';
  shadow: 'none' | 'small' | 'medium' | 'large';
  overflow: 'visible' | 'hidden';
}>`
  position: relative;
  display: flex;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  transition: all 0.2s ease;
  
  /* Layout */
  ${({ layout }) => layout === 'horizontal' ? css`
    flex-direction: row;
  ` : css`
    flex-direction: column;
  `}
  
  /* Border Radius */
  ${({ borderRadius }) => {
    switch (borderRadius) {
      case 'none':
        return css`border-radius: 0;`;
      case 'small':
        return css`border-radius: 4px;`;
      case 'large':
        return css`border-radius: 16px;`;
      case 'full':
        return css`border-radius: 9999px;`;
      default: // medium
        return css`border-radius: 8px;`;
    }
  }}
  
  /* Overflow */
  overflow: ${({ overflow }) => overflow};
  
  /* Variant Styles */
  ${({ variant, selected }) => {
    switch (variant) {
      case 'outlined':
        return css`
          background: white;
          border: 2px solid ${selected ? '#3b82f6' : '#e5e7eb'};
        `;
      case 'filled':
        return css`
          background: #f9fafb;
          border: 2px solid transparent;
        `;
      case 'elevated':
        return css`
          background: white;
          border: 1px solid #f3f4f6;
        `;
      case 'flat':
        return css`
          background: transparent;
          border: none;
        `;
      default: // default
        return css`
          background: white;
          border: 1px solid ${selected ? '#3b82f6' : '#e5e7eb'};
        `;
    }
  }}
  
  /* Shadow */
  ${({ shadow, variant }) => {
    if (variant === 'flat') return '';
    
    switch (shadow) {
      case 'small':
        return css`
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.24);
        `;
      case 'large':
        return css`
          box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        `;
      case 'none':
        return '';
      default: // medium
        return css`
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        `;
    }
  }}
  
  /* Interactive States */
  ${({ clickable, hoverable, disabled }) => {
    if (disabled) {
      return css`
        opacity: 0.6;
        cursor: not-allowed;
        pointer-events: none;
      `;
    }
    
    if (clickable || hoverable) {
      return css`
        cursor: pointer;
        
        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        }
        
        &:active {
          transform: translateY(0);
        }
      `;
    }
    
    return '';
  }}
  
  /* Selected State */
  ${({ selected }) => selected && css`
    border-color: #3b82f6;
    animation: ${pulseGlow} 2s infinite;
  `}
  
  /* Size */
  ${({ size }) => {
    switch (size) {
      case 'small':
        return css`
          min-height: 120px;
        `;
      case 'large':
        return css`
          min-height: 320px;
        `;
      default: // medium
        return css`
          min-height: 200px;
        `;
    }
  }}
`;

const CardHeaderContainer = styled.div<{
  alignItems: 'start' | 'center' | 'end';
}>`
  display: flex;
  align-items: ${({ alignItems }) => {
    switch (alignItems) {
      case 'start':
        return 'flex-start';
      case 'end':
        return 'flex-end';
      default:
        return 'center';
    }
  }};
  padding: 1rem 1rem 0.5rem 1rem;
  gap: 0.75rem;
`;

const CardHeaderContent = styled.div`
  flex: 1;
  min-width: 0;
`;

const CardTitle = styled.h3`
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #111827;
  line-height: 1.4;
`;

const CardSubtitle = styled.p`
  margin: 0.25rem 0 0 0;
  font-size: 0.875rem;
  color: #6b7280;
  line-height: 1.4;
`;

const CardAvatar = styled.div`
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const CardAction = styled.div`
  flex-shrink: 0;
  display: flex;
  align-items: center;
`;

const CardMediaContainer = styled.div<{
  aspectRatio: '16:9' | '4:3' | '1:1' | '3:2' | 'auto';
}>`
  position: relative;
  overflow: hidden;
  
  ${({ aspectRatio }) => {
    if (aspectRatio === 'auto') return '';
    
    const ratios = {
      '16:9': '56.25%',
      '4:3': '75%',
      '1:1': '100%',
      '3:2': '66.67%'
    };
    
    return css`
      width: 100%;
      height: 0;
      padding-bottom: ${ratios[aspectRatio]};
    `;
  }}
`;

const CardMedia = styled.img<{
  objectFit: 'cover' | 'contain' | 'fill' | 'scale-down';
  aspectRatio: '16:9' | '4:3' | '1:1' | '3:2' | 'auto';
}>`
  width: 100%;
  height: ${({ aspectRatio }) => aspectRatio === 'auto' ? 'auto' : '100%'};
  object-fit: ${({ objectFit }) => objectFit};
  transition: transform 0.3s ease;
  
  ${({ aspectRatio }) => aspectRatio !== 'auto' && css`
    position: absolute;
    top: 0;
    left: 0;
  `}
  
  &:hover {
    transform: scale(1.05);
  }
`;

const CardVideo = styled.video<{
  objectFit: 'cover' | 'contain' | 'fill' | 'scale-down';
  aspectRatio: '16:9' | '4:3' | '1:1' | '3:2' | 'auto';
}>`
  width: 100%;
  height: ${({ aspectRatio }) => aspectRatio === 'auto' ? 'auto' : '100%'};
  object-fit: ${({ objectFit }) => objectFit};
  
  ${({ aspectRatio }) => aspectRatio !== 'auto' && css`
    position: absolute;
    top: 0;
    left: 0;
  `}
`;

const MediaOverlay = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  opacity: 0;
  transition: opacity 0.3s ease;
  
  &:hover {
    opacity: 1;
  }
`;

const MediaPlaceholder = styled.div<{
  aspectRatio: '16:9' | '4:3' | '1:1' | '3:2' | 'auto';
}>`
  width: 100%;
  height: ${({ aspectRatio }) => aspectRatio === 'auto' ? '200px' : '100%'};
  background: #f3f4f6;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #9ca3af;
  font-size: 2rem;
  
  ${({ aspectRatio }) => aspectRatio !== 'auto' && css`
    position: absolute;
    top: 0;
    left: 0;
  `}
`;

const CardBodyContainer = styled.div<{
  padding: 'none' | 'small' | 'medium' | 'large';
}>`
  flex: 1;
  
  ${({ padding }) => {
    switch (padding) {
      case 'none':
        return css`padding: 0;`;
      case 'small':
        return css`padding: 0.5rem;`;
      case 'large':
        return css`padding: 2rem;`;
      default: // medium
        return css`padding: 1rem;`;
    }
  }}
`;

const CardFooterContainer = styled.div<{
  justifyContent: 'start' | 'center' | 'end' | 'space-between' | 'space-around';
  alignItems: 'start' | 'center' | 'end';
}>`
  display: flex;
  padding: 0.5rem 1rem 1rem 1rem;
  
  justify-content: ${({ justifyContent }) => {
    switch (justifyContent) {
      case 'start':
        return 'flex-start';
      case 'end':
        return 'flex-end';
      default:
        return justifyContent;
    }
  }};
  
  align-items: ${({ alignItems }) => {
    switch (alignItems) {
      case 'start':
        return 'flex-start';
      case 'end':
        return 'flex-end';
      default:
        return 'center';
    }
  }};
`;

const CardActionsContainer = styled.div<{
  orientation: 'horizontal' | 'vertical';
  spacing: 'small' | 'medium' | 'large';
}>`
  display: flex;
  
  flex-direction: ${({ orientation }) => orientation === 'vertical' ? 'column' : 'row'};
  
  ${({ spacing, orientation }) => {
    const gaps = {
      small: '0.5rem',
      medium: '1rem',
      large: '1.5rem'
    };
    
    return css`
      gap: ${gaps[spacing]};
    `;
  }}
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
  z-index: 1;
`;

const LoadingSpinner = styled.div`
  width: 32px;
  height: 32px;
  border: 3px solid #e5e7eb;
  border-top: 3px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const SkeletonLine = styled.div<{ width?: string; height?: string }>`
  height: ${({ height }) => height || '1rem'};
  width: ${({ width }) => width || '100%'};
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200px 100%;
  animation: ${shimmer} 1.5s infinite;
  border-radius: 4px;
  margin-bottom: 0.5rem;
  
  &:last-child {
    margin-bottom: 0;
  }
`;

const SkeletonAvatar = styled.div`
  width: 40px;
  height: 40px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200px 100%;
  animation: ${shimmer} 1.5s infinite;
  border-radius: 50%;
`;

const SkeletonMedia = styled.div<{ aspectRatio: '16:9' | '4:3' | '1:1' | '3:2' | 'auto' }>`
  width: 100%;
  height: ${({ aspectRatio }) => aspectRatio === 'auto' ? '200px' : '100%'};
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200px 100%;
  animation: ${shimmer} 1.5s infinite;
  
  ${({ aspectRatio }) => aspectRatio !== 'auto' && css`
    position: absolute;
    top: 0;
    left: 0;
  `}
`;

// ============================================================================
// CARD COMPONENTS
// ============================================================================

export const CardHeader: React.FC<CardHeaderProps> = ({
  children,
  title,
  subtitle,
  avatar,
  action,
  alignItems = 'center',
  className,
  style,
  ...props
}) => {
  if (children) {
    return (
      <CardHeaderContainer
        className={className}
        style={style}
        alignItems={alignItems}
        {...props}
      >
        {children}
      </CardHeaderContainer>
    );
  }

  return (
    <CardHeaderContainer
      className={className}
      style={style}
      alignItems={alignItems}
      {...props}
    >
      {avatar && <CardAvatar>{avatar}</CardAvatar>}
      
      <CardHeaderContent>
        {title && <CardTitle>{title}</CardTitle>}
        {subtitle && <CardSubtitle>{subtitle}</CardSubtitle>}
      </CardHeaderContent>
      
      {action && <CardAction>{action}</CardAction>}
    </CardHeaderContainer>
  );
};

export const CardMedia: React.FC<CardMediaProps> = ({
  src,
  alt,
  type = 'image',
  aspectRatio = '16:9',
  objectFit = 'cover',
  loading = 'lazy',
  placeholder,
  overlay,
  className,
  style,
  ...props
}) => {
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);

  const handleLoad = () => {
    setIsLoading(false);
  };

  const handleError = () => {
    setIsLoading(false);
    setHasError(true);
  };

  return (
    <CardMediaContainer
      className={className}
      style={style}
      aspectRatio={aspectRatio}
      {...props}
    >
      {src && !hasError ? (
        type === 'video' ? (
          <CardVideo
            src={src}
            objectFit={objectFit}
            aspectRatio={aspectRatio}
            controls
            onLoadedData={handleLoad}
            onError={handleError}
          />
        ) : (
          <CardMedia
            src={src}
            alt={alt || ''}
            objectFit={objectFit}
            aspectRatio={aspectRatio}
            loading={loading}
            onLoad={handleLoad}
            onError={handleError}
          />
        )
      ) : (
        <MediaPlaceholder aspectRatio={aspectRatio}>
          {placeholder || (hasError ? '❌' : '📷')}
        </MediaPlaceholder>
      )}
      
      {overlay && (
        <MediaOverlay>
          {overlay}
        </MediaOverlay>
      )}
    </CardMediaContainer>
  );
};

export const CardBody: React.FC<CardBodyProps> = ({
  children,
  padding = 'medium',
  className,
  style,
  ...props
}) => {
  return (
    <CardBodyContainer
      className={className}
      style={style}
      padding={padding}
      {...props}
    >
      {children}
    </CardBodyContainer>
  );
};

export const CardFooter: React.FC<CardFooterProps> = ({
  children,
  justifyContent = 'start',
  alignItems = 'center',
  className,
  style,
  ...props
}) => {
  return (
    <CardFooterContainer
      className={className}
      style={style}
      justifyContent={justifyContent}
      alignItems={alignItems}
      {...props}
    >
      {children}
    </CardFooterContainer>
  );
};

export const CardActions: React.FC<CardActionsProps> = ({
  children,
  orientation = 'horizontal',
  spacing = 'medium',
  className,
  style,
  ...props
}) => {
  return (
    <CardActionsContainer
      className={className}
      style={style}
      orientation={orientation}
      spacing={spacing}
      {...props}
    >
      {children}
    </CardActionsContainer>
  );
};

export const CardSkeleton: React.FC<CardSkeletonProps> = ({
  lines = 3,
  showHeader = true,
  showMedia = true,
  showActions = true,
  variant = 'default',
  size = 'medium',
  ...props
}) => {
  return (
    <CardContainer
      variant={variant}
      size={size}
      layout="vertical"
      borderRadius="medium"
      shadow="medium"
      overflow="hidden"
      {...props}
    >
      {showHeader && (
        <CardHeaderContainer alignItems="center">
          <SkeletonAvatar />
          <CardHeaderContent>
            <SkeletonLine width="60%" height="1.25rem" />
            <SkeletonLine width="40%" height="0.875rem" />
          </CardHeaderContent>
        </CardHeaderContainer>
      )}
      
      {showMedia && (
        <CardMediaContainer aspectRatio="16:9">
          <SkeletonMedia aspectRatio="16:9" />
        </CardMediaContainer>
      )}
      
      <CardBodyContainer padding="medium">
        {Array.from({ length: lines }).map((_, index) => (
          <SkeletonLine
            key={index}
            width={index === lines - 1 ? '75%' : '100%'}
          />
        ))}
      </CardBodyContainer>
      
      {showActions && (
        <CardFooterContainer justifyContent="space-between" alignItems="center">
          <SkeletonLine width="80px" height="32px" />
          <SkeletonLine width="60px" height="32px" />
        </CardFooterContainer>
      )}
    </CardContainer>
  );
};

// ============================================================================
// MAIN CARD COMPONENT
// ============================================================================

export const Card: React.FC<CardProps> = ({
  children,
  variant = 'default',
  size = 'medium',
  layout = 'vertical',
  clickable = false,
  hoverable = false,
  loading = false,
  selected = false,
  disabled = false,
  borderRadius = 'medium',
  shadow = 'medium',
  overflow = 'hidden',
  onClick,
  onDoubleClick,
  className,
  style,
  ...props
}) => {
  const cardRef = useRef<HTMLDivElement>(null);

  const handleClick = (event: MouseEvent<HTMLDivElement>) => {
    if (!disabled && onClick) {
      onClick(event);
    }
  };

  const handleDoubleClick = (event: MouseEvent<HTMLDivElement>) => {
    if (!disabled && onDoubleClick) {
      onDoubleClick(event);
    }
  };

  return (
    <CardContainer
      ref={cardRef}
      className={className}
      style={style}
      variant={variant}
      size={size}
      layout={layout}
      clickable={clickable}
      hoverable={hoverable}
      selected={selected}
      disabled={disabled}
      borderRadius={borderRadius}
      shadow={shadow}
      overflow={overflow}
      onClick={handleClick}
      onDoubleClick={handleDoubleClick}
      whileHover={
        (clickable || hoverable) && !disabled
          ? { y: -4, boxShadow: '0 8px 25px rgba(0, 0, 0, 0.15)' }
          : undefined
      }
      whileTap={
        (clickable || hoverable) && !disabled
          ? { y: 0 }
          : undefined
      }
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      {...props}
    >
      {loading && (
        <LoadingOverlay>
          <LoadingSpinner />
        </LoadingOverlay>
      )}
      
      {children}
    </CardContainer>
  );
};

// ============================================================================
// USAGE EXAMPLES
// ============================================================================

export const CardExamples: React.FC = () => {
  const [selectedCard, setSelectedCard] = useState<string | null>(null);
  const [loadingCard, setLoadingCard] = useState<string | null>(null);

  const handleCardClick = (cardId: string) => {
    setSelectedCard(selectedCard === cardId ? null : cardId);
  };

  const handleLoadingDemo = (cardId: string) => {
    setLoadingCard(cardId);
    setTimeout(() => setLoadingCard(null), 3000);
  };

  return (
    <div style={{ padding: '2rem' }}>
      <h2>Card Component Examples</h2>
      
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', 
        gap: '2rem',
        marginBottom: '3rem'
      }}>
        {/* Basic Card */}
        <Card
          variant="default"
          clickable
          selected={selectedCard === 'basic'}
          onClick={() => handleCardClick('basic')}
        >
          <CardHeader
            title="Basic Card"
            subtitle="A simple card example"
            avatar={
              <div style={{
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                background: '#3b82f6',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                fontWeight: 'bold'
              }}>
                BC
              </div>
            }
            action={
              <button
                style={{
                  padding: '4px 8px',
                  border: 'none',
                  borderRadius: '4px',
                  background: '#e5e7eb',
                  cursor: 'pointer'
                }}
                onClick={(e) => {
                  e.stopPropagation();
                  console.log('Action clicked');
                }}
              >
                ⋯
              </button>
            }
          />
          <CardBody>
            <p>This is a basic card with a header, body, and footer. Click to select it!</p>
          </CardBody>
          <CardFooter justifyContent="space-between">
            <span style={{ fontSize: '0.875rem', color: '#6b7280' }}>
              Created 2 hours ago
            </span>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button style={{
                padding: '6px 12px',
                border: 'none',
                borderRadius: '4px',
                background: '#3b82f6',
                color: 'white',
                cursor: 'pointer',
                fontSize: '0.875rem'
              }}>
                Like
              </button>
              <button style={{
                padding: '6px 12px',
                border: '1px solid #d1d5db',
                borderRadius: '4px',
                background: 'white',
                cursor: 'pointer',
                fontSize: '0.875rem'
              }}>
                Share
              </button>
            </div>
          </CardFooter>
        </Card>

        {/* Media Card */}
        <Card variant="elevated" hoverable>
          <CardMedia
            src="https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400&h=225&fit=crop"
            alt="Office workspace"
            aspectRatio="16:9"
            overlay={
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>▶️</div>
                <div>Play Video</div>
              </div>
            }
          />
          <CardHeader
            title="Media Card"
            subtitle="Card with image and overlay"
          />
          <CardBody>
            <p>This card features an image with an overlay that appears on hover.</p>
          </CardBody>
        </Card>

        {/* Loading Card */}
        <Card
          variant="outlined"
          loading={loadingCard === 'loading'}
          clickable
          onClick={() => handleLoadingDemo('loading')}
        >
          <CardHeader
            title="Loading Demo"
            subtitle="Click to see loading state"
          />
          <CardBody>
            <p>Click this card to see the loading overlay in action.</p>
          </CardBody>
          <CardFooter>
            <button style={{
              padding: '8px 16px',
              border: 'none',
              borderRadius: '4px',
              background: '#10b981',
              color: 'white',
              cursor: 'pointer'
            }}>
              Trigger Loading
            </button>
          </CardFooter>
        </Card>

        {/* Horizontal Card */}
        <Card
          variant="filled"
          layout="horizontal"
          size="large"
          style={{ gridColumn: 'span 2' }}
        >
          <CardMedia
            src="https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?w=200&h=200&fit=crop"
            alt="Technology"
            aspectRatio="1:1"
            style={{ width: '200px', flexShrink: 0 }}
          />
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
            <CardHeader
              title="Horizontal Layout"
              subtitle="Card with horizontal media and content"
            />
            <CardBody style={{ flex: 1 }}>
              <p>This card uses a horizontal layout with media on the left and content on the right. It demonstrates how the card component can adapt to different layouts.</p>
            </CardBody>
            <CardFooter>
              <CardActions spacing="small">
                <button style={{
                  padding: '8px 16px',
                  border: 'none',
                  borderRadius: '4px',
                  background: '#3b82f6',
                  color: 'white',
                  cursor: 'pointer'
                }}>
                  Learn More
                </button>
                <button style={{
                  padding: '8px 16px',
                  border: '1px solid #d1d5db',
                  borderRadius: '4px',
                  background: 'white',
                  cursor: 'pointer'
                }}>
                  Save
                </button>
              </CardActions>
            </CardFooter>
          </div>
        </Card>

        {/* Disabled Card */}
        <Card variant="default" disabled>
          <CardHeader
            title="Disabled Card"
            subtitle="This card is disabled"
          />
          <CardBody>
            <p>This card is in a disabled state and cannot be interacted with.</p>
          </CardBody>
        </Card>

        {/* Skeleton Card */}
        <CardSkeleton
          showHeader
          showMedia
          showActions
          lines={4}
        />
      </div>

      {/* Card Variants */}
      <div style={{ marginBottom: '3rem' }}>
        <h3>Card Variants</h3>
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
          gap: '1rem'
        }}>
          {['default', 'outlined', 'filled', 'elevated', 'flat'].map(variant => (
            <Card key={variant} variant={variant as any} size="small">
              <CardBody>
                <h4 style={{ margin: '0 0 0.5rem 0', textTransform: 'capitalize' }}>
                  {variant}
                </h4>
                <p style={{ margin: 0, fontSize: '0.875rem' }}>
                  {variant} variant example
                </p>
              </CardBody>
            </Card>
          ))}
        </div>
      </div>

      {/* Card Sizes */}
      <div>
        <h3>Card Sizes</h3>
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', 
          gap: '1rem'
        }}>
          {['small', 'medium', 'large'].map(size => (
            <Card key={size} size={size as any} variant="outlined">
              <CardBody>
                <h4 style={{ margin: '0 0 0.5rem 0', textTransform: 'capitalize' }}>
                  {size}
                </h4>
                <p style={{ margin: 0, fontSize: '0.875rem' }}>
                  {size} size example
                </p>
              </CardBody>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Card;