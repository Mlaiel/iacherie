/**
 * 🃏 Card Component Template - Enterprise Card System
 * ==================================================
 * 
 * © 2025 Fahed Mlaiel <mlaiel@live.de>
 * TOUS DROITS RÉSERVÉS - Propriété Intellectuelle Protégée
 * 
 * Enterprise-grade card components with various layouts,
 * interactive features, loading states, and accessibility.
 */

import React, { useState, useCallback, forwardRef } from 'react';

// ========================================
// 📝 TYPE DEFINITIONS
// ========================================

interface CardProps {
  children?: React.ReactNode;
  title?: React.ReactNode;
  subtitle?: React.ReactNode;
  description?: React.ReactNode;
  image?: string | React.ReactNode;
  imageAlt?: string;
  imagePosition?: 'top' | 'left' | 'right' | 'background';
  actions?: React.ReactNode;
  badges?: BadgeProps[];
  variant?: 'default' | 'outlined' | 'elevated' | 'filled';
  size?: 'small' | 'medium' | 'large';
  clickable?: boolean;
  hoverable?: boolean;
  loading?: boolean;
  disabled?: boolean;
  selected?: boolean;
  borderRadius?: 'none' | 'small' | 'medium' | 'large' | 'full';
  shadow?: 'none' | 'small' | 'medium' | 'large';
  padding?: 'none' | 'small' | 'medium' | 'large';
  width?: string | number;
  height?: string | number;
  onClick?: () => void;
  onDoubleClick?: () => void;
  onMouseEnter?: () => void;
  onMouseLeave?: () => void;
  className?: string;
  style?: React.CSSProperties;
  testId?: string;
}

interface BadgeProps {
  label: string;
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info';
  size?: 'small' | 'medium';
  position?: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right';
}

interface ProductCardProps extends Omit<CardProps, 'children'> {
  name: string;
  price: number | string;
  originalPrice?: number | string;
  currency?: string;
  rating?: number;
  reviewCount?: number;
  inStock?: boolean;
  discount?: number;
  category?: string;
  onAddToCart?: () => void;
  onAddToWishlist?: () => void;
}

interface ProfileCardProps extends Omit<CardProps, 'children'> {
  name: string;
  role?: string;
  company?: string;
  avatar: string;
  location?: string;
  email?: string;
  phone?: string;
  socialLinks?: SocialLink[];
  stats?: Stat[];
  onConnect?: () => void;
  onMessage?: () => void;
}

interface SocialLink {
  platform: string;
  url: string;
  icon?: React.ReactNode;
}

interface Stat {
  label: string;
  value: string | number;
  icon?: React.ReactNode;
}

interface StatsCardProps extends Omit<CardProps, 'children'> {
  title: string;
  value: string | number;
  change?: number;
  changeLabel?: string;
  trend?: 'up' | 'down' | 'neutral';
  icon?: React.ReactNode;
  color?: string;
  format?: 'number' | 'currency' | 'percentage';
  currency?: string;
}

// ========================================
// 🎨 CARD STYLES
// ========================================

const getCardStyles = (
  variant: string,
  size: string,
  clickable: boolean,
  hoverable: boolean,
  disabled: boolean,
  selected: boolean,
  borderRadius: string,
  shadow: string,
  padding: string
) => {
  const borderRadiusMap = {
    none: '0',
    small: '0.25rem',
    medium: '0.5rem',
    large: '1rem',
    full: '9999px'
  };

  const shadowMap = {
    none: 'none',
    small: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
    medium: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    large: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)'
  };

  const paddingMap = {
    none: '0',
    small: '0.75rem',
    medium: '1rem',
    large: '1.5rem'
  };

  return {
    card: {
      borderRadius: borderRadiusMap[borderRadius as keyof typeof borderRadiusMap] || borderRadiusMap.medium,
      boxShadow: shadowMap[shadow as keyof typeof shadowMap] || shadowMap.small,
      transition: 'all 0.2s ease-in-out',
      position: 'relative' as const,
      overflow: 'hidden',
      ...(variant === 'default' && {
        backgroundColor: '#ffffff',
        border: '1px solid #e5e7eb'
      }),
      ...(variant === 'outlined' && {
        backgroundColor: '#ffffff',
        border: '2px solid #e5e7eb'
      }),
      ...(variant === 'elevated' && {
        backgroundColor: '#ffffff',
        border: 'none',
        boxShadow: shadowMap.large
      }),
      ...(variant === 'filled' && {
        backgroundColor: '#f9fafb',
        border: '1px solid #e5e7eb'
      }),
      ...(selected && {
        borderColor: '#3b82f6',
        boxShadow: '0 0 0 3px rgba(59, 130, 246, 0.1)'
      }),
      ...(disabled && {
        opacity: 0.6,
        cursor: 'not-allowed'
      }),
      ...(clickable && !disabled && {
        cursor: 'pointer'
      }),
      ...(hoverable && !disabled && {
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: shadowMap.large
        }
      })
    },

    content: {
      padding: paddingMap[padding as keyof typeof paddingMap] || paddingMap.medium
    },

    header: {
      marginBottom: '1rem'
    },

    title: {
      fontSize: size === 'small' ? '1rem' : 
                size === 'large' ? '1.5rem' : '1.25rem',
      fontWeight: '600',
      color: '#111827',
      margin: '0 0 0.25rem 0',
      lineHeight: '1.4'
    },

    subtitle: {
      fontSize: size === 'small' ? '0.75rem' : '0.875rem',
      color: '#6b7280',
      margin: '0 0 0.5rem 0'
    },

    description: {
      fontSize: size === 'small' ? '0.875rem' : '1rem',
      color: '#374151',
      lineHeight: '1.5',
      margin: '0'
    },

    image: {
      width: '100%',
      height: 'auto',
      display: 'block'
    },

    imageContainer: {
      overflow: 'hidden',
      borderRadius: 'inherit'
    },

    actions: {
      display: 'flex',
      gap: '0.5rem',
      marginTop: '1rem',
      alignItems: 'center'
    },

    badge: {
      position: 'absolute' as const,
      fontSize: '0.75rem',
      fontWeight: '500',
      padding: '0.25rem 0.5rem',
      borderRadius: '0.25rem',
      zIndex: 10
    },

    loading: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '2rem'
    },

    skeleton: {
      backgroundColor: '#e5e7eb',
      borderRadius: '0.25rem',
      animation: 'pulse 1.5s ease-in-out infinite'
    }
  };
};

// ========================================
// 🃏 BASE CARD COMPONENT
// ========================================

export const Card = forwardRef<HTMLDivElement, CardProps>(({
  children,
  title,
  subtitle,
  description,
  image,
  imageAlt = '',
  imagePosition = 'top',
  actions,
  badges = [],
  variant = 'default',
  size = 'medium',
  clickable = false,
  hoverable = true,
  loading = false,
  disabled = false,
  selected = false,
  borderRadius = 'medium',
  shadow = 'small',
  padding = 'medium',
  width,
  height,
  onClick,
  onDoubleClick,
  onMouseEnter,
  onMouseLeave,
  className = '',
  style = {},
  testId = 'card'
}, ref) => {
  const [isHovered, setIsHovered] = useState(false);

  const styles = getCardStyles(
    variant, size, clickable, hoverable, disabled, selected,
    borderRadius, shadow, padding
  );

  const handleMouseEnter = useCallback(() => {
    setIsHovered(true);
    onMouseEnter?.();
  }, [onMouseEnter]);

  const handleMouseLeave = useCallback(() => {
    setIsHovered(false);
    onMouseLeave?.();
  }, [onMouseLeave]);

  const cardStyle = {
    ...styles.card,
    ...(width && { width }),
    ...(height && { height }),
    ...(isHovered && hoverable && !disabled && {
      transform: 'translateY(-2px)',
      boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)'
    }),
    ...style
  };

  const renderImage = () => {
    if (!image) return null;

    const imageElement = typeof image === 'string' ? (
      <img
        src={image}
        alt={imageAlt}
        style={styles.image}
        loading="lazy"
      />
    ) : image;

    return (
      <div style={styles.imageContainer}>
        {imageElement}
      </div>
    );
  };

  const renderBadges = () => {
    return badges.map((badge, index) => {
      const badgeColors = {
        primary: { backgroundColor: '#3b82f6', color: '#ffffff' },
        secondary: { backgroundColor: '#6b7280', color: '#ffffff' },
        success: { backgroundColor: '#10b981', color: '#ffffff' },
        warning: { backgroundColor: '#f59e0b', color: '#ffffff' },
        error: { backgroundColor: '#ef4444', color: '#ffffff' },
        info: { backgroundColor: '#06b6d4', color: '#ffffff' }
      };

      const positions = {
        'top-left': { top: '0.5rem', left: '0.5rem' },
        'top-right': { top: '0.5rem', right: '0.5rem' },
        'bottom-left': { bottom: '0.5rem', left: '0.5rem' },
        'bottom-right': { bottom: '0.5rem', right: '0.5rem' }
      };

      return (
        <div
          key={index}
          style={{
            ...styles.badge,
            ...badgeColors[badge.variant || 'primary'],
            ...positions[badge.position || 'top-right'],
            fontSize: badge.size === 'small' ? '0.625rem' : '0.75rem'
          }}
        >
          {badge.label}
        </div>
      );
    });
  };

  const renderContent = () => {
    if (loading) {
      return (
        <div style={styles.loading}>
          <div style={{
            width: '24px',
            height: '24px',
            border: '2px solid #e5e7eb',
            borderTopColor: '#3b82f6',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite'
          }} />
        </div>
      );
    }

    return (
      <div style={styles.content}>
        {(title || subtitle) && (
          <div style={styles.header}>
            {title && <h3 style={styles.title}>{title}</h3>}
            {subtitle && <p style={styles.subtitle}>{subtitle}</p>}
          </div>
        )}

        {description && <p style={styles.description}>{description}</p>}
        {children}

        {actions && (
          <div style={styles.actions}>
            {actions}
          </div>
        )}
      </div>
    );
  };

  return (
    <div
      ref={ref}
      className={className}
      style={cardStyle}
      onClick={disabled ? undefined : onClick}
      onDoubleClick={disabled ? undefined : onDoubleClick}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      data-testid={testId}
      role={clickable ? 'button' : undefined}
      tabIndex={clickable && !disabled ? 0 : undefined}
      aria-disabled={disabled}
      aria-selected={selected}
    >
      {renderBadges()}
      
      {imagePosition === 'top' && renderImage()}
      
      <div style={{
        display: imagePosition === 'left' || imagePosition === 'right' ? 'flex' : 'block',
        flexDirection: imagePosition === 'left' ? 'row' : imagePosition === 'right' ? 'row-reverse' : undefined,
        gap: imagePosition === 'left' || imagePosition === 'right' ? '1rem' : undefined
      }}>
        {(imagePosition === 'left' || imagePosition === 'right') && (
          <div style={{ flex: '0 0 auto', width: '40%' }}>
            {renderImage()}
          </div>
        )}
        
        <div style={{ flex: 1 }}>
          {renderContent()}
        </div>
      </div>
      
      {imagePosition === 'background' && image && (
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundImage: typeof image === 'string' ? `url(${image})` : undefined,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          opacity: 0.1,
          zIndex: -1
        }} />
      )}
    </div>
  );
});

Card.displayName = 'Card';

// ========================================
// 🛍️ PRODUCT CARD
// ========================================

export const ProductCard: React.FC<ProductCardProps> = ({
  name,
  price,
  originalPrice,
  currency = '$',
  rating,
  reviewCount,
  inStock = true,
  discount,
  category,
  image,
  imageAlt,
  onAddToCart,
  onAddToWishlist,
  ...cardProps
}) => {
  const formatPrice = (amount: number | string) => {
    return `${currency}${amount}`;
  };

  const renderRating = () => {
    if (!rating) return null;

    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
        <div style={{ display: 'flex', gap: '0.125rem' }}>
          {[1, 2, 3, 4, 5].map((star) => (
            <span
              key={star}
              style={{
                color: star <= rating ? '#fbbf24' : '#e5e7eb',
                fontSize: '0.875rem'
              }}
            >
              ★
            </span>
          ))}
        </div>
        {reviewCount && (
          <span style={{ fontSize: '0.875rem', color: '#6b7280' }}>
            ({reviewCount})
          </span>
        )}
      </div>
    );
  };

  const badges = [];
  
  if (discount) {
    badges.push({
      label: `-${discount}%`,
      variant: 'error' as const,
      position: 'top-left' as const
    });
  }
  
  if (!inStock) {
    badges.push({
      label: 'Out of Stock',
      variant: 'secondary' as const,
      position: 'top-right' as const
    });
  }

  return (
    <Card
      {...cardProps}
      image={image}
      imageAlt={imageAlt || name}
      badges={badges}
      title={name}
      subtitle={category}
      actions={
        <div style={{ display: 'flex', width: '100%', flexDirection: 'column', gap: '0.5rem' }}>
          {renderRating()}
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
            <span style={{ fontSize: '1.25rem', fontWeight: '700', color: '#111827' }}>
              {formatPrice(price)}
            </span>
            {originalPrice && (
              <span style={{ 
                fontSize: '1rem', 
                color: '#6b7280',
                textDecoration: 'line-through'
              }}>
                {formatPrice(originalPrice)}
              </span>
            )}
          </div>

          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button
              onClick={onAddToCart}
              disabled={!inStock}
              style={{
                flex: 1,
                padding: '0.5rem 1rem',
                backgroundColor: inStock ? '#3b82f6' : '#9ca3af',
                color: '#ffffff',
                border: 'none',
                borderRadius: '0.375rem',
                fontWeight: '500',
                cursor: inStock ? 'pointer' : 'not-allowed',
                transition: 'background-color 0.2s ease'
              }}
            >
              {inStock ? '🛒 Add to Cart' : 'Out of Stock'}
            </button>
            
            {onAddToWishlist && (
              <button
                onClick={onAddToWishlist}
                style={{
                  padding: '0.5rem',
                  backgroundColor: 'transparent',
                  border: '1px solid #d1d5db',
                  borderRadius: '0.375rem',
                  cursor: 'pointer',
                  fontSize: '1.25rem'
                }}
                title="Add to wishlist"
              >
                ♡
              </button>
            )}
          </div>
        </div>
      }
    />
  );
};

// ========================================
// 👤 PROFILE CARD
// ========================================

export const ProfileCard: React.FC<ProfileCardProps> = ({
  name,
  role,
  company,
  avatar,
  location,
  email,
  phone,
  socialLinks = [],
  stats = [],
  onConnect,
  onMessage,
  ...cardProps
}) => {
  return (
    <Card
      {...cardProps}
      actions={
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', width: '100%' }}>
          {/* Avatar and Basic Info */}
          <div style={{ textAlign: 'center' }}>
            <img
              src={avatar}
              alt={name}
              style={{
                width: '80px',
                height: '80px',
                borderRadius: '50%',
                margin: '0 auto 1rem',
                objectFit: 'cover',
                border: '3px solid #e5e7eb'
              }}
            />
            <h3 style={{ margin: '0 0 0.25rem 0', fontSize: '1.25rem', fontWeight: '600' }}>
              {name}
            </h3>
            {role && (
              <p style={{ margin: '0 0 0.25rem 0', color: '#6b7280', fontSize: '0.875rem' }}>
                {role}
              </p>
            )}
            {company && (
              <p style={{ margin: '0 0 0.5rem 0', color: '#3b82f6', fontSize: '0.875rem' }}>
                {company}
              </p>
            )}
            {location && (
              <p style={{ margin: '0', color: '#6b7280', fontSize: '0.875rem' }}>
                📍 {location}
              </p>
            )}
          </div>

          {/* Stats */}
          {stats.length > 0 && (
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-around', 
              padding: '1rem 0',
              borderTop: '1px solid #e5e7eb',
              borderBottom: '1px solid #e5e7eb'
            }}>
              {stats.map((stat, index) => (
                <div key={index} style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '1.25rem', fontWeight: '700', color: '#111827' }}>
                    {stat.value}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '0.25rem' }}>
                    {stat.label}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Contact Info */}
          {(email || phone) && (
            <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>
              {email && <div style={{ marginBottom: '0.25rem' }}>📧 {email}</div>}
              {phone && <div>📞 {phone}</div>}
            </div>
          )}

          {/* Social Links */}
          {socialLinks.length > 0 && (
            <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem' }}>
              {socialLinks.map((link, index) => (
                <a
                  key={index}
                  href={link.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{
                    color: '#6b7280',
                    fontSize: '1.25rem',
                    transition: 'color 0.2s ease'
                  }}
                  title={link.platform}
                >
                  {link.icon || '🔗'}
                </a>
              ))}
            </div>
          )}

          {/* Action Buttons */}
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            {onConnect && (
              <button
                onClick={onConnect}
                style={{
                  flex: 1,
                  padding: '0.5rem 1rem',
                  backgroundColor: '#3b82f6',
                  color: '#ffffff',
                  border: 'none',
                  borderRadius: '0.375rem',
                  fontWeight: '500',
                  cursor: 'pointer'
                }}
              >
                Connect
              </button>
            )}
            
            {onMessage && (
              <button
                onClick={onMessage}
                style={{
                  flex: 1,
                  padding: '0.5rem 1rem',
                  backgroundColor: 'transparent',
                  color: '#3b82f6',
                  border: '1px solid #3b82f6',
                  borderRadius: '0.375rem',
                  fontWeight: '500',
                  cursor: 'pointer'
                }}
              >
                Message
              </button>
            )}
          </div>
        </div>
      }
    />
  );
};

// ========================================
// 📊 STATS CARD
// ========================================

export const StatsCard: React.FC<StatsCardProps> = ({
  title,
  value,
  change,
  changeLabel,
  trend,
  icon,
  color = '#3b82f6',
  format = 'number',
  currency = '$',
  ...cardProps
}) => {
  const formatValue = (val: string | number) => {
    switch (format) {
      case 'currency':
        return `${currency}${val}`;
      case 'percentage':
        return `${val}%`;
      default:
        return val;
    }
  };

  const getTrendColor = () => {
    switch (trend) {
      case 'up': return '#10b981';
      case 'down': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const getTrendIcon = () => {
    switch (trend) {
      case 'up': return '↗️';
      case 'down': return '↘️';
      default: return '➡️';
    }
  };

  return (
    <Card
      {...cardProps}
      padding="large"
      actions={
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', width: '100%' }}>
          {/* Header with icon */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <h3 style={{ 
                margin: '0 0 0.5rem 0', 
                fontSize: '0.875rem', 
                fontWeight: '500',
                color: '#6b7280',
                textTransform: 'uppercase',
                letterSpacing: '0.05em'
              }}>
                {title}
              </h3>
              <div style={{ 
                fontSize: '2rem', 
                fontWeight: '700', 
                color: '#111827',
                lineHeight: '1'
              }}>
                {formatValue(value)}
              </div>
            </div>
            
            {icon && (
              <div style={{ 
                padding: '0.75rem',
                backgroundColor: `${color}20`,
                borderRadius: '0.5rem',
                color: color,
                fontSize: '1.5rem'
              }}>
                {icon}
              </div>
            )}
          </div>

          {/* Change indicator */}
          {change !== undefined && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span style={{ 
                color: getTrendColor(),
                fontSize: '0.875rem',
                fontWeight: '500',
                display: 'flex',
                alignItems: 'center',
                gap: '0.25rem'
              }}>
                {getTrendIcon()}
                {Math.abs(change)}%
              </span>
              {changeLabel && (
                <span style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                  {changeLabel}
                </span>
              )}
            </div>
          )}
        </div>
      }
    />
  );
};

// ========================================
// 📦 EXPORTS
// ========================================

export { Card as default, ProductCard, ProfileCard, StatsCard };

export type {
  CardProps,
  ProductCardProps,
  ProfileCardProps,
  StatsCardProps,
  BadgeProps,
  SocialLink,
  Stat
};

// ========================================
// 🎯 USAGE EXAMPLES
// ========================================

/*
// Basic Card
<Card
  title="Card Title"
  subtitle="Card Subtitle"
  description="This is a description of the card content."
  actions={
    <div>
      <button>Action 1</button>
      <button>Action 2</button>
    </div>
  }
  hoverable
  clickable
  onClick={() => console.log('Card clicked')}
/>

// Product Card
<ProductCard
  name="Wireless Headphones"
  price={99.99}
  originalPrice={149.99}
  currency="$"
  rating={4.5}
  reviewCount={128}
  discount={33}
  category="Electronics"
  image="/headphones.jpg"
  inStock={true}
  onAddToCart={() => console.log('Added to cart')}
  onAddToWishlist={() => console.log('Added to wishlist')}
/>

// Profile Card
<ProfileCard
  name="John Doe"
  role="Software Engineer"
  company="Tech Corp"
  avatar="/avatar.jpg"
  location="San Francisco, CA"
  email="john@example.com"
  stats={[
    { label: 'Projects', value: 24 },
    { label: 'Followers', value: 1.2k },
    { label: 'Following', value: 483 }
  ]}
  socialLinks={[
    { platform: 'LinkedIn', url: 'https://linkedin.com/in/johndoe', icon: '💼' },
    { platform: 'GitHub', url: 'https://github.com/johndoe', icon: '💻' }
  ]}
  onConnect={() => console.log('Connect clicked')}
  onMessage={() => console.log('Message clicked')}
/>

// Stats Card
<StatsCard
  title="Total Revenue"
  value={45678}
  change={12.5}
  changeLabel="vs last month"
  trend="up"
  format="currency"
  currency="$"
  icon="💰"
  color="#10b981"
/>

// Image Card with Badges
<Card
  title="Special Offer"
  description="Limited time deal on selected items."
  image="/offer-banner.jpg"
  imagePosition="background"
  badges={[
    { label: 'Limited Time', variant: 'warning', position: 'top-left' },
    { label: 'Hot Deal', variant: 'error', position: 'top-right' }
  ]}
  variant="elevated"
  shadow="large"
/>
*/