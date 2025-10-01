/**
 * 🎨 NAVIGATION COMPONENT TEMPLATE - FRONTEND EXPERT IMPLEMENTATION
 * =================================================================
 * 
 * Enterprise-grade navigation component template with:
 * - TypeScript support with strict typing
 * - Multi-level navigation support
 * - Responsive design and mobile hamburger menu
 * - Active state management and breadcrumbs
 * - Search integration and mega menu
 * - Keyboard navigation and accessibility
 * - Animation and smooth transitions
 * - User authentication integration
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
  ReactNode,
  KeyboardEvent,
  MouseEvent
} from 'react';
import styled, { css, keyframes } from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

interface NavigationItem {
  id: string;
  label: string;
  href?: string;
  icon?: ReactNode;
  badge?: string | number;
  disabled?: boolean;
  children?: NavigationItem[];
  onClick?: (item: NavigationItem) => void;
  target?: '_blank' | '_self' | '_parent' | '_top';
  megaMenu?: MegaMenuConfig;
}

interface MegaMenuConfig {
  sections: MegaMenuSection[];
  width?: 'full' | 'auto';
  columns?: number;
}

interface MegaMenuSection {
  title?: string;
  items: NavigationItem[];
  featured?: boolean;
  description?: string;
  image?: string;
}

interface NavigationProps {
  items: NavigationItem[];
  logo?: ReactNode;
  logoHref?: string;
  onLogoClick?: () => void;
  activeItem?: string;
  variant?: 'horizontal' | 'vertical' | 'sidebar';
  position?: 'static' | 'fixed' | 'sticky';
  size?: 'small' | 'medium' | 'large';
  theme?: 'light' | 'dark' | 'primary';
  showSearch?: boolean;
  searchPlaceholder?: string;
  onSearch?: (query: string) => void;
  user?: UserInfo;
  showUserMenu?: boolean;
  userMenuItems?: NavigationItem[];
  notifications?: NotificationItem[];
  showNotifications?: boolean;
  mobileBreakpoint?: number;
  collapsible?: boolean;
  collapsed?: boolean;
  onCollapse?: (collapsed: boolean) => void;
  className?: string;
  style?: React.CSSProperties;
}

interface UserInfo {
  name: string;
  email?: string;
  avatar?: string;
  role?: string;
}

interface NotificationItem {
  id: string;
  title: string;
  message: string;
  timestamp: Date;
  read: boolean;
  type?: 'info' | 'success' | 'warning' | 'error';
  action?: () => void;
}

// ============================================================================
// ANIMATIONS
// ============================================================================

const slideDown = keyframes`
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
`;

const slideRight = keyframes`
  from {
    opacity: 0;
    transform: translateX(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
`;

const fadeIn = keyframes`
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
`;

// ============================================================================
// STYLED COMPONENTS
// ============================================================================

const NavigationContainer = styled.nav<{
  variant: 'horizontal' | 'vertical' | 'sidebar';
  position: 'static' | 'fixed' | 'sticky';
  theme: 'light' | 'dark' | 'primary';
  size: 'small' | 'medium' | 'large';
  collapsed?: boolean;
}>`
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  z-index: 1000;
  
  ${({ position }) => {
    switch (position) {
      case 'fixed':
        return css`
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
        `;
      case 'sticky':
        return css`
          position: sticky;
          top: 0;
        `;
      default:
        return css`
          position: static;
        `;
    }
  }}
  
  ${({ theme }) => {
    switch (theme) {
      case 'dark':
        return css`
          background: #1f2937;
          color: #f9fafb;
          border-bottom: 1px solid #374151;
        `;
      case 'primary':
        return css`
          background: #3b82f6;
          color: white;
          border-bottom: 1px solid #2563eb;
        `;
      default: // light
        return css`
          background: white;
          color: #374151;
          border-bottom: 1px solid #e5e7eb;
        `;
    }
  }}
  
  ${({ variant, collapsed }) => {
    switch (variant) {
      case 'vertical':
      case 'sidebar':
        return css`
          height: 100vh;
          overflow-y: auto;
          transition: width 0.3s ease;
          
          ${collapsed ? css`
            width: 64px;
          ` : css`
            width: 280px;
          `}
        `;
      default: // horizontal
        return css`
          width: 100%;
        `;
    }
  }}
  
  ${({ size }) => {
    switch (size) {
      case 'small':
        return css`
          font-size: 13px;
          
          .nav-item {
            padding: 8px 12px;
          }
        `;
      case 'large':
        return css`
          font-size: 16px;
          
          .nav-item {
            padding: 16px 24px;
          }
        `;
      default: // medium
        return css`
          font-size: 14px;
          
          .nav-item {
            padding: 12px 16px;
          }
        `;
    }
  }}
`;

const NavigationHeader = styled.div<{ variant: 'horizontal' | 'vertical' | 'sidebar' }>`
  display: flex;
  align-items: center;
  padding: 1rem;
  
  ${({ variant }) => variant === 'horizontal' ? css`
    justify-content: space-between;
    width: 100%;
  ` : css`
    justify-content: center;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  `}
`;

const Logo = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  font-size: 1.25rem;
  cursor: pointer;
  transition: opacity 0.2s ease;
  
  &:hover {
    opacity: 0.8;
  }
`;

const NavigationContent = styled.div<{ variant: 'horizontal' | 'vertical' | 'sidebar' }>`
  display: flex;
  
  ${({ variant }) => variant === 'horizontal' ? css`
    align-items: center;
    gap: 2rem;
    flex: 1;
    justify-content: space-between;
    padding: 0 1rem;
  ` : css`
    flex-direction: column;
    padding: 1rem 0;
  `}
`;

const NavigationList = styled.ul<{ variant: 'horizontal' | 'vertical' | 'sidebar' }>`
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  
  ${({ variant }) => variant === 'horizontal' ? css`
    flex-direction: row;
    gap: 0.5rem;
  ` : css`
    flex-direction: column;
    width: 100%;
  `}
`;

const NavigationItemElement = styled.li<{
  active?: boolean;
  disabled?: boolean;
  theme: 'light' | 'dark' | 'primary';
  variant: 'horizontal' | 'vertical' | 'sidebar';
  hasChildren?: boolean;
  collapsed?: boolean;
}>`
  position: relative;
  
  ${({ variant }) => variant !== 'horizontal' && css`
    width: 100%;
  `}
  
  .nav-link {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    text-decoration: none;
    color: inherit;
    transition: all 0.2s ease;
    border-radius: 6px;
    position: relative;
    white-space: nowrap;
    
    ${({ collapsed, variant }) => collapsed && (variant === 'vertical' || variant === 'sidebar') && css`
      justify-content: center;
      
      .nav-text, .nav-badge {
        display: none;
      }
    `}
    
    &:hover {
      ${({ theme }) => {
        switch (theme) {
          case 'dark':
            return css`background: rgba(255, 255, 255, 0.1);`;
          case 'primary':
            return css`background: rgba(255, 255, 255, 0.1);`;
          default:
            return css`background: #f3f4f6;`;
        }
      }}
    }
    
    ${({ active, theme }) => active && {
      switch (theme) {
        case 'dark':
          return css`
            background: rgba(59, 130, 246, 0.2);
            color: #60a5fa;
          `;
        case 'primary':
          return css`
            background: rgba(255, 255, 255, 0.2);
            color: white;
          `;
        default:
          return css`
            background: #dbeafe;
            color: #1d4ed8;
          `;
      }
    }}
    
    ${({ disabled }) => disabled && css`
      opacity: 0.5;
      cursor: not-allowed;
      pointer-events: none;
    `}
  }
  
  .nav-icon {
    display: flex;
    align-items: center;
    font-size: 1.1em;
    min-width: 20px;
  }
  
  .nav-text {
    flex: 1;
  }
  
  .nav-badge {
    background: #ef4444;
    color: white;
    font-size: 0.75em;
    padding: 2px 6px;
    border-radius: 10px;
    min-width: 18px;
    text-align: center;
  }
  
  .nav-arrow {
    transition: transform 0.2s ease;
    font-size: 0.8em;
    
    ${({ hasChildren }) => hasChildren && css`
      &.open {
        transform: rotate(90deg);
      }
    `}
  }
`;

const SubMenu = styled(motion.ul)<{
  variant: 'horizontal' | 'vertical' | 'sidebar';
  theme: 'light' | 'dark' | 'primary';
}>`
  list-style: none;
  margin: 0;
  padding: 0;
  position: absolute;
  z-index: 1001;
  
  ${({ variant, theme }) => {
    if (variant === 'horizontal') {
      return css`
        top: 100%;
        left: 0;
        min-width: 200px;
        padding: 0.5rem 0;
        border-radius: 8px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        animation: ${slideDown} 0.2s ease-out;
        
        ${theme === 'dark' ? css`
          background: #374151;
          border: 1px solid #4b5563;
        ` : css`
          background: white;
          border: 1px solid #e5e7eb;
        `}
      `;
    } else {
      return css`
        position: static;
        padding-left: 2rem;
        animation: ${slideRight} 0.2s ease-out;
      `;
    }
  }}
`;

const MegaMenu = styled(motion.div)<{
  theme: 'light' | 'dark' | 'primary';
  width: 'full' | 'auto';
}>`
  position: absolute;
  top: 100%;
  left: 0;
  z-index: 1001;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  animation: ${slideDown} 0.3s ease-out;
  
  ${({ width }) => width === 'full' ? css`
    right: 0;
  ` : css`
    min-width: 600px;
  `}
  
  ${({ theme }) => {
    switch (theme) {
      case 'dark':
        return css`
          background: #374151;
          border: 1px solid #4b5563;
          color: #f9fafb;
        `;
      case 'primary':
        return css`
          background: #1e40af;
          border: 1px solid #1d4ed8;
          color: white;
        `;
      default:
        return css`
          background: white;
          border: 1px solid #e5e7eb;
          color: #374151;
        `;
    }
  }}
`;

const MegaMenuGrid = styled.div<{ columns: number }>`
  display: grid;
  grid-template-columns: repeat(${({ columns }) => columns}, 1fr);
  gap: 2rem;
`;

const MegaMenuSection = styled.div<{ featured?: boolean }>`
  ${({ featured }) => featured && css`
    grid-column: span 2;
    padding: 1rem;
    background: rgba(59, 130, 246, 0.1);
    border-radius: 8px;
  `}
`;

const MegaMenuTitle = styled.h4`
  margin: 0 0 1rem 0;
  font-size: 1.1em;
  font-weight: 600;
  color: inherit;
`;

const SearchContainer = styled.div<{ theme: 'light' | 'dark' | 'primary' }>`
  position: relative;
  display: flex;
  align-items: center;
  
  .search-input {
    padding: 8px 12px 8px 36px;
    border: 1px solid transparent;
    border-radius: 6px;
    font-size: 14px;
    transition: all 0.2s ease;
    width: 240px;
    
    ${({ theme }) => {
      switch (theme) {
        case 'dark':
          return css`
            background: rgba(255, 255, 255, 0.1);
            color: white;
            
            &::placeholder {
              color: rgba(255, 255, 255, 0.6);
            }
            
            &:focus {
              background: rgba(255, 255, 255, 0.2);
              border-color: #60a5fa;
            }
          `;
        case 'primary':
          return css`
            background: rgba(255, 255, 255, 0.2);
            color: white;
            
            &::placeholder {
              color: rgba(255, 255, 255, 0.7);
            }
            
            &:focus {
              background: rgba(255, 255, 255, 0.3);
              border-color: white;
            }
          `;
        default:
          return css`
            background: #f9fafb;
            color: #374151;
            
            &::placeholder {
              color: #9ca3af;
            }
            
            &:focus {
              background: white;
              border-color: #3b82f6;
              box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
            }
          `;
      }
    }}
    
    &:focus {
      outline: none;
    }
  }
  
  .search-icon {
    position: absolute;
    left: 12px;
    color: inherit;
    opacity: 0.6;
  }
`;

const UserMenu = styled.div`
  position: relative;
  display: flex;
  align-items: center;
  gap: 1rem;
`;

const UserInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 6px;
  transition: background 0.2s ease;
  
  &:hover {
    background: rgba(255, 255, 255, 0.1);
  }
`;

const Avatar = styled.img`
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
`;

const UserDetails = styled.div`
  display: flex;
  flex-direction: column;
  text-align: left;
  
  .user-name {
    font-weight: 500;
    font-size: 14px;
  }
  
  .user-role {
    font-size: 12px;
    opacity: 0.8;
  }
`;

const NotificationBell = styled.button<{ hasUnread?: boolean }>`
  position: relative;
  background: none;
  border: none;
  color: inherit;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 6px;
  transition: background 0.2s ease;
  
  &:hover {
    background: rgba(255, 255, 255, 0.1);
  }
  
  ${({ hasUnread }) => hasUnread && css`
    &::after {
      content: '';
      position: absolute;
      top: 6px;
      right: 6px;
      width: 8px;
      height: 8px;
      background: #ef4444;
      border-radius: 50%;
    }
  `}
`;

const MobileMenuButton = styled.button`
  display: none;
  background: none;
  border: none;
  color: inherit;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 6px;
  transition: background 0.2s ease;
  
  &:hover {
    background: rgba(255, 255, 255, 0.1);
  }
  
  @media (max-width: 768px) {
    display: block;
  }
`;

const MobileOverlay = styled(motion.div)`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 999;
  
  @media (min-width: 769px) {
    display: none;
  }
`;

const MobileMenu = styled(motion.div)<{ theme: 'light' | 'dark' | 'primary' }>`
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  width: 280px;
  z-index: 1000;
  overflow-y: auto;
  
  ${({ theme }) => {
    switch (theme) {
      case 'dark':
        return css`
          background: #1f2937;
          color: #f9fafb;
        `;
      case 'primary':
        return css`
          background: #3b82f6;
          color: white;
        `;
      default:
        return css`
          background: white;
          color: #374151;
        `;
    }
  }}
  
  @media (min-width: 769px) {
    display: none;
  }
`;

const CollapseButton = styled.button`
  background: none;
  border: none;
  color: inherit;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 6px;
  transition: all 0.2s ease;
  
  &:hover {
    background: rgba(255, 255, 255, 0.1);
  }
`;

// ============================================================================
// MAIN NAVIGATION COMPONENT
// ============================================================================

export const Navigation: React.FC<NavigationProps> = ({
  items = [],
  logo,
  logoHref,
  onLogoClick,
  activeItem,
  variant = 'horizontal',
  position = 'static',
  size = 'medium',
  theme = 'light',
  showSearch = false,
  searchPlaceholder = 'Search...',
  onSearch,
  user,
  showUserMenu = false,
  userMenuItems = [],
  notifications = [],
  showNotifications = false,
  mobileBreakpoint = 768,
  collapsible = false,
  collapsed = false,
  onCollapse,
  className,
  style,
  ...props
}) => {
  const [openItems, setOpenItems] = useState<Set<string>>(new Set());
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [notificationMenuOpen, setNotificationMenuOpen] = useState(false);

  const navRef = useRef<HTMLElement>(null);

  // Handle item click
  const handleItemClick = useCallback((item: NavigationItem, event?: MouseEvent) => {
    if (item.disabled) return;

    if (item.children && item.children.length > 0) {
      event?.preventDefault();
      setOpenItems(prev => {
        const newSet = new Set(prev);
        if (newSet.has(item.id)) {
          newSet.delete(item.id);
        } else {
          newSet.add(item.id);
        }
        return newSet;
      });
    } else {
      item.onClick?.(item);
      if (variant === 'horizontal') {
        setIsMobileMenuOpen(false);
      }
    }
  }, [variant]);

  // Handle keyboard navigation
  const handleKeyDown = useCallback((event: KeyboardEvent, item: NavigationItem) => {
    switch (event.key) {
      case 'Enter':
      case ' ':
        event.preventDefault();
        handleItemClick(item);
        break;
      case 'Escape':
        setOpenItems(new Set());
        setUserMenuOpen(false);
        setNotificationMenuOpen(false);
        break;
    }
  }, [handleItemClick]);

  // Handle search
  const handleSearch = useCallback((query: string) => {
    setSearchQuery(query);
    onSearch?.(query);
  }, [onSearch]);

  // Close menus on outside click
  useEffect(() => {
    const handleClickOutside = (event: Event) => {
      if (navRef.current && !navRef.current.contains(event.target as Node)) {
        setOpenItems(new Set());
        setUserMenuOpen(false);
        setNotificationMenuOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Close mobile menu on resize
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth > mobileBreakpoint) {
        setIsMobileMenuOpen(false);
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [mobileBreakpoint]);

  // Render navigation item
  const renderNavigationItem = useCallback((item: NavigationItem, level = 0) => {
    const isOpen = openItems.has(item.id);
    const isActive = activeItem === item.id;
    const hasChildren = item.children && item.children.length > 0;
    const hasMegaMenu = item.megaMenu && item.megaMenu.sections.length > 0;

    return (
      <NavigationItemElement
        key={item.id}
        active={isActive}
        disabled={item.disabled}
        theme={theme}
        variant={variant}
        hasChildren={hasChildren}
        collapsed={collapsed}
        className="nav-item"
      >
        <a
          href={item.href}
          className="nav-link"
          target={item.target}
          onClick={(e) => handleItemClick(item, e)}
          onKeyDown={(e) => handleKeyDown(e, item)}
          tabIndex={item.disabled ? -1 : 0}
          role="menuitem"
          aria-expanded={hasChildren ? isOpen : undefined}
          aria-haspopup={hasChildren ? 'menu' : undefined}
        >
          {item.icon && (
            <span className="nav-icon">
              {item.icon}
            </span>
          )}
          
          <span className="nav-text">
            {item.label}
          </span>
          
          {item.badge && (
            <span className="nav-badge">
              {item.badge}
            </span>
          )}
          
          {hasChildren && (
            <span className={`nav-arrow ${isOpen ? 'open' : ''}`}>
              ▶
            </span>
          )}
        </a>

        {/* Sub Menu */}
        <AnimatePresence>
          {hasChildren && isOpen && (
            <SubMenu
              variant={variant}
              theme={theme}
              role="menu"
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.2 }}
            >
              {item.children!.map(child => renderNavigationItem(child, level + 1))}
            </SubMenu>
          )}
        </AnimatePresence>

        {/* Mega Menu */}
        <AnimatePresence>
          {hasMegaMenu && isOpen && variant === 'horizontal' && (
            <MegaMenu
              theme={theme}
              width={item.megaMenu!.width || 'auto'}
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.3 }}
            >
              <MegaMenuGrid columns={item.megaMenu!.columns || 3}>
                {item.megaMenu!.sections.map((section, index) => (
                  <MegaMenuSection key={index} featured={section.featured}>
                    {section.title && (
                      <MegaMenuTitle>{section.title}</MegaMenuTitle>
                    )}
                    {section.description && (
                      <p style={{ margin: '0 0 1rem 0', opacity: 0.8 }}>
                        {section.description}
                      </p>
                    )}
                    <NavigationList variant="vertical">
                      {section.items.map(sectionItem => renderNavigationItem(sectionItem, level + 1))}
                    </NavigationList>
                  </MegaMenuSection>
                ))}
              </MegaMenuGrid>
            </MegaMenu>
          )}
        </AnimatePresence>
      </NavigationItemElement>
    );
  }, [openItems, activeItem, theme, variant, collapsed, handleItemClick, handleKeyDown]);

  // Render search
  const renderSearch = () => {
    if (!showSearch) return null;

    return (
      <SearchContainer theme={theme}>
        <svg className="search-icon" width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
          <path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z"/>
        </svg>
        <input
          type="text"
          className="search-input"
          placeholder={searchPlaceholder}
          value={searchQuery}
          onChange={(e) => handleSearch(e.target.value)}
        />
      </SearchContainer>
    );
  };

  // Render user menu
  const renderUserMenu = () => {
    if (!showUserMenu || !user) return null;

    const unreadNotifications = notifications.filter(n => !n.read).length;

    return (
      <UserMenu>
        {showNotifications && (
          <NotificationBell
            hasUnread={unreadNotifications > 0}
            onClick={() => setNotificationMenuOpen(!notificationMenuOpen)}
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
              <path d="M10 2C7.794 2 6 3.794 6 6v4c0 .36-.152.693-.4.933L4 12.667V14h12v-1.333l-1.6-1.734A1.2 1.2 0 0114 10V6c0-2.206-1.794-4-4-4zM8 16h4c0 1.1-.9 2-2 2s-2-.9-2-2z"/>
            </svg>
            {unreadNotifications > 0 && (
              <span style={{
                position: 'absolute',
                top: '4px',
                right: '4px',
                background: '#ef4444',
                color: 'white',
                fontSize: '10px',
                padding: '2px 4px',
                borderRadius: '8px',
                minWidth: '16px',
                textAlign: 'center'
              }}>
                {unreadNotifications}
              </span>
            )}
          </NotificationBell>
        )}

        <UserInfo onClick={() => setUserMenuOpen(!userMenuOpen)}>
          {user.avatar ? (
            <Avatar src={user.avatar} alt={user.name} />
          ) : (
            <div style={{
              width: '32px',
              height: '32px',
              borderRadius: '50%',
              background: '#e5e7eb',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#6b7280',
              fontWeight: '500'
            }}>
              {user.name.charAt(0).toUpperCase()}
            </div>
          )}
          
          <UserDetails>
            <span className="user-name">{user.name}</span>
            {user.role && <span className="user-role">{user.role}</span>}
          </UserDetails>
          
          <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
            <path d="M4.5 6L8 9.5L11.5 6H4.5Z" />
          </svg>
        </UserInfo>

        {/* User Menu Dropdown */}
        <AnimatePresence>
          {userMenuOpen && (
            <SubMenu
              variant="horizontal"
              theme={theme}
              style={{ right: 0, left: 'auto', minWidth: '200px' }}
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
            >
              {userMenuItems.map(item => renderNavigationItem(item))}
            </SubMenu>
          )}
        </AnimatePresence>
      </UserMenu>
    );
  };

  const navigationContent = (
    <>
      {/* Main Navigation */}
      <NavigationList variant={variant} role="menubar">
        {items.map(item => renderNavigationItem(item))}
      </NavigationList>

      {/* Right Side Content for Horizontal Layout */}
      {variant === 'horizontal' && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          {renderSearch()}
          {renderUserMenu()}
        </div>
      )}
    </>
  );

  return (
    <>
      <NavigationContainer
        ref={navRef}
        className={className}
        style={style}
        variant={variant}
        position={position}
        theme={theme}
        size={size}
        collapsed={collapsed}
        role="navigation"
        {...props}
      >
        {/* Header */}
        <NavigationHeader variant={variant}>
          {/* Logo */}
          {logo && (
            <Logo onClick={onLogoClick}>
              {logoHref ? (
                <a href={logoHref} style={{ color: 'inherit', textDecoration: 'none' }}>
                  {logo}
                </a>
              ) : (
                logo
              )}
            </Logo>
          )}

          {/* Collapse Button for Sidebar */}
          {collapsible && (variant === 'vertical' || variant === 'sidebar') && (
            <CollapseButton onClick={() => onCollapse?.(!collapsed)}>
              <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                <path d="M3 5h14M3 10h14M3 15h14" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              </svg>
            </CollapseButton>
          )}

          {/* Mobile Menu Button */}
          {variant === 'horizontal' && (
            <MobileMenuButton onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                <path d="M3 6h18M3 12h18M3 18h18" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              </svg>
            </MobileMenuButton>
          )}
        </NavigationHeader>

        {/* Navigation Content */}
        {variant === 'horizontal' ? (
          <NavigationContent variant={variant}>
            {navigationContent}
          </NavigationContent>
        ) : (
          <NavigationContent variant={variant}>
            {/* Search for Vertical Layouts */}
            {!collapsed && renderSearch()}
            {navigationContent}
            {/* User Menu for Vertical Layouts */}
            {!collapsed && renderUserMenu()}
          </NavigationContent>
        )}
      </NavigationContainer>

      {/* Mobile Menu */}
      <AnimatePresence>
        {isMobileMenuOpen && variant === 'horizontal' && (
          <>
            <MobileOverlay
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsMobileMenuOpen(false)}
            />
            <MobileMenu
              theme={theme}
              initial={{ x: -280 }}
              animate={{ x: 0 }}
              exit={{ x: -280 }}
              transition={{ type: 'tween', duration: 0.3 }}
            >
              <NavigationHeader variant="vertical">
                {logo}
              </NavigationHeader>
              <NavigationContent variant="vertical">
                {renderSearch()}
                <NavigationList variant="vertical">
                  {items.map(item => renderNavigationItem(item))}
                </NavigationList>
                {renderUserMenu()}
              </NavigationContent>
            </MobileMenu>
          </>
        )}
      </AnimatePresence>
    </>
  );
};

// ============================================================================
// USAGE EXAMPLES
// ============================================================================

export const NavigationExamples: React.FC = () => {
  const [activeItem, setActiveItem] = useState('dashboard');
  const [collapsed, setCollapsed] = useState(false);

  const sampleItems: NavigationItem[] = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      href: '/dashboard',
      icon: '📊',
      onClick: (item) => setActiveItem(item.id)
    },
    {
      id: 'products',
      label: 'Products',
      icon: '📦',
      badge: '12',
      children: [
        { id: 'products-list', label: 'All Products', href: '/products' },
        { id: 'products-add', label: 'Add Product', href: '/products/add' },
        { id: 'products-categories', label: 'Categories', href: '/products/categories' },
      ]
    },
    {
      id: 'orders',
      label: 'Orders',
      href: '/orders',
      icon: '🛒',
      badge: '5',
      onClick: (item) => setActiveItem(item.id)
    },
    {
      id: 'customers',
      label: 'Customers',
      href: '/customers',
      icon: '👥',
      onClick: (item) => setActiveItem(item.id)
    },
    {
      id: 'analytics',
      label: 'Analytics',
      href: '/analytics',
      icon: '📈',
      disabled: true
    }
  ];

  const userMenuItems: NavigationItem[] = [
    { id: 'profile', label: 'Profile', href: '/profile', icon: '👤' },
    { id: 'settings', label: 'Settings', href: '/settings', icon: '⚙️' },
    { id: 'logout', label: 'Logout', href: '/logout', icon: '🚪' }
  ];

  const sampleUser: UserInfo = {
    name: 'John Doe',
    email: 'john@example.com',
    role: 'Administrator',
    avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=32&h=32&fit=crop&crop=face'
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem', minHeight: '100vh' }}>
      <h2 style={{ padding: '1rem' }}>Navigation Component Examples</h2>
      
      {/* Horizontal Navigation */}
      <div style={{ marginBottom: '2rem' }}>
        <h3 style={{ padding: '0 1rem' }}>Horizontal Navigation</h3>
        <Navigation
          items={sampleItems}
          logo={<span style={{ fontSize: '1.5rem' }}>🚀 IA Chéries</span>}
          logoHref="/"
          activeItem={activeItem}
          variant="horizontal"
          position="sticky"
          theme="primary"
          showSearch
          showUserMenu
          user={sampleUser}
          userMenuItems={userMenuItems}
          showNotifications
          notifications={[
            {
              id: '1',
              title: 'New Order',
              message: 'You have received a new order',
              timestamp: new Date(),
              read: false,
              type: 'info'
            }
          ]}
        />
      </div>

      {/* Content Area */}
      <div style={{ flex: 1, padding: '1rem', background: '#f9fafb' }}>
        <h3>Content Area</h3>
        <p>Active Item: {activeItem}</p>
        <p>This is where your main content would go.</p>
      </div>

      {/* Sidebar Navigation */}
      <div style={{ position: 'fixed', top: '200px', right: '20px', zIndex: 1000 }}>
        <h4>Sidebar Example</h4>
        <div style={{ width: collapsed ? '64px' : '280px', height: '400px', border: '1px solid #e5e7eb', borderRadius: '8px', overflow: 'hidden' }}>
          <Navigation
            items={sampleItems}
            logo={collapsed ? '🚀' : <span>🚀 IA Chéries</span>}
            activeItem={activeItem}
            variant="sidebar"
            theme="dark"
            collapsible
            collapsed={collapsed}
            onCollapse={setCollapsed}
            showUserMenu={!collapsed}
            user={sampleUser}
            userMenuItems={userMenuItems}
          />
        </div>
        <button 
          onClick={() => setCollapsed(!collapsed)}
          style={{ 
            marginTop: '8px',
            padding: '8px 16px',
            border: 'none',
            borderRadius: '4px',
            background: '#3b82f6',
            color: 'white',
            cursor: 'pointer'
          }}
        >
          Toggle Collapse
        </button>
      </div>
    </div>
  );
};

export default Navigation;