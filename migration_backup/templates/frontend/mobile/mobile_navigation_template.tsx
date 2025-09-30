/**
 * 📱 Mobile Navigation Template - Enterprise Component
 * ==================================================
 * 
 * © 2025 Fahed Mlaiel <mlaiel@live.de>
 * TOUS DROITS RÉSERVÉS
 * 
 * @author Fahed Mlaiel
 * @role Lead Dev IA + Mobile Expert + UI/UX Specialist + Performance Engineer
 * @description Enterprise mobile navigation with gesture support, PWA integration,
 *              bottom navigation, floating action button, and touch-optimized interface
 */

import React, { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import styled, { ThemeProvider, keyframes } from 'styled-components';
import { motion, AnimatePresence, PanInfo, useDragControls } from 'framer-motion';

// ===========================
// 🎨 STYLED COMPONENTS & ANIMATIONS
// ===========================

const slideUp = keyframes`
  from { transform: translateY(100%); }
  to { transform: translateY(0); }
`;

const fadeIn = keyframes`
  from { opacity: 0; }
  to { opacity: 1; }
`;

const bounce = keyframes`
  0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-8px); }
  60% { transform: translateY(-4px); }
`;

const MobileContainer = styled.div`
  position: relative;
  width: 100%;
  height: 100vh;
  background: #f8fafc;
  overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
`;

const TopBar = styled(motion.div)`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 60px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(226, 232, 240, 0.8);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  z-index: 1000;
  animation: ${slideUp} 0.4s ease-out;
`;

const MenuButton = styled(motion.button)`
  width: 44px;
  height: 44px;
  border: none;
  background: none;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  color: #64748b;
  font-size: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    background: rgba(102, 126, 234, 0.1);
    color: #667eea;
  }
  
  &:active {
    transform: scale(0.95);
  }
`;

const TopBarTitle = styled.h1`
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
  flex: 1;
  text-align: center;
`;

const NotificationButton = styled(motion.button)`
  position: relative;
  width: 44px;
  height: 44px;
  border: none;
  background: none;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  color: #64748b;
  font-size: 20px;
  cursor: pointer;
  
  &:active {
    transform: scale(0.95);
  }
`;

const NotificationBadge = styled.div`
  position: absolute;
  top: 8px;
  right: 8px;
  width: 16px;
  height: 16px;
  background: #ef4444;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 600;
  color: white;
  animation: ${bounce} 2s infinite;
`;

const MainContent = styled.div`
  margin-top: 60px;
  margin-bottom: 80px;
  padding: 16px;
  min-height: calc(100vh - 140px);
`;

const SideMenu = styled(motion.div)`
  position: fixed;
  top: 0;
  left: 0;
  width: 280px;
  height: 100vh;
  background: white;
  box-shadow: 4px 0 20px rgba(0, 0, 0, 0.15);
  z-index: 2000;
  overflow-y: auto;
`;

const MenuOverlay = styled(motion.div)`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1999;
`;

const MenuHeader = styled.div`
  padding: 32px 24px 24px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
`;

const UserInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
`;

const UserAvatar = styled.img`
  width: 48px;
  height: 48px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid rgba(255, 255, 255, 0.3);
`;

const UserDetails = styled.div`
  flex: 1;
`;

const UserName = styled.div`
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 2px;
`;

const UserRole = styled.div`
  font-size: 14px;
  opacity: 0.8;
`;

const MenuStats = styled.div`
  display: flex;
  gap: 16px;
  font-size: 12px;
`;

const StatItem = styled.div`
  text-align: center;
  
  .value {
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 2px;
  }
  
  .label {
    opacity: 0.8;
  }
`;

const MenuItems = styled.div`
  padding: 24px 0;
`;

const MenuItem = styled(motion.a)<{ active?: boolean }>`
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 24px;
  color: ${props => props.active ? '#667eea' : '#64748b'};
  text-decoration: none;
  font-size: 16px;
  font-weight: ${props => props.active ? '600' : '500'};
  border-right: 3px solid ${props => props.active ? '#667eea' : 'transparent'};
  background: ${props => props.active ? 'rgba(102, 126, 234, 0.05)' : 'transparent'};
  transition: all 0.3s ease;
`;

const MenuIcon = styled.div`
  font-size: 20px;
  width: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const BottomNavigation = styled(motion.div)`
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 80px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-top: 1px solid rgba(226, 232, 240, 0.8);
  display: flex;
  align-items: center;
  justify-content: space-around;
  padding: 8px 16px;
  z-index: 1000;
  animation: ${slideUp} 0.4s ease-out;
`;

const NavItem = styled(motion.button)<{ active?: boolean }>`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  border: none;
  background: none;
  padding: 8px 12px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 60px;
  
  ${props => props.active && `
    background: rgba(102, 126, 234, 0.1);
  `}
`;

const NavIcon = styled.div<{ active?: boolean }>`
  font-size: 24px;
  color: ${props => props.active ? '#667eea' : '#94a3b8'};
  transition: all 0.3s ease;
`;

const NavLabel = styled.div<{ active?: boolean }>`
  font-size: 12px;
  font-weight: ${props => props.active ? '600' : '500'};
  color: ${props => props.active ? '#667eea' : '#94a3b8'};
  transition: all 0.3s ease;
`;

const FloatingActionButton = styled(motion.button)`
  position: fixed;
  bottom: 100px;
  right: 20px;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  border: none;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  font-size: 24px;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
  cursor: pointer;
  z-index: 1001;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const FABMenu = styled(motion.div)`
  position: fixed;
  bottom: 170px;
  right: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  z-index: 1002;
`;

const FABMenuItem = styled(motion.button)`
  width: 48px;
  height: 48px;
  border-radius: 50%;
  border: none;
  background: white;
  color: #667eea;
  font-size: 20px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const SwipeIndicator = styled(motion.div)`
  position: absolute;
  top: 50%;
  right: 8px;
  transform: translateY(-50%);
  width: 3px;
  height: 24px;
  background: rgba(102, 126, 234, 0.3);
  border-radius: 2px;
`;

const PullToRefresh = styled(motion.div)`
  position: absolute;
  top: -60px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
`;

// ===========================
// 🎯 INTERFACES & TYPES
// ===========================

interface NavigationItem {
  id: string;
  label: string;
  icon: string;
  href?: string;
  badge?: number;
  active?: boolean;
}

interface MenuItemType {
  id: string;
  label: string;
  icon: string;
  href?: string;
  active?: boolean;
  badge?: number;
  divider?: boolean;
}

interface User {
  id: string;
  name: string;
  role: string;
  avatar: string;
  stats: {
    followers: number;
    content: number;
    revenue: number;
  };
}

interface FABAction {
  id: string;
  icon: string;
  label: string;
  action: () => void;
}

interface MobileNavigationProps {
  title?: string;
  user?: User;
  navigationItems: NavigationItem[];
  menuItems: MenuItemType[];
  fabActions?: FABAction[];
  notifications?: number;
  onMenuItemClick?: (item: MenuItemType) => void;
  onNavItemClick?: (item: NavigationItem) => void;
  onNotificationClick?: () => void;
  enablePullToRefresh?: boolean;
  onRefresh?: () => Promise<void>;
  theme?: any;
  children?: React.ReactNode;
}

// ===========================
// 🚀 MAIN COMPONENT
// ===========================

export const MobileNavigationTemplate: React.FC<MobileNavigationProps> = ({
  title = 'Ainflue',
  user,
  navigationItems,
  menuItems,
  fabActions = [],
  notifications = 0,
  onMenuItemClick,
  onNavItemClick,
  onNotificationClick,
  enablePullToRefresh = true,
  onRefresh,
  theme = defaultTheme,
  children
}) => {
  const [showSideMenu, setShowSideMenu] = useState(false);
  const [showFABMenu, setShowFABMenu] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [pullDistance, setPullDistance] = useState(0);
  
  const dragControls = useDragControls();
  const menuRef = useRef<HTMLDivElement>(null);

  // Handle menu item click
  const handleMenuItemClick = useCallback((item: MenuItemType) => {
    setShowSideMenu(false);
    onMenuItemClick?.(item);
  }, [onMenuItemClick]);

  // Handle navigation item click
  const handleNavItemClick = useCallback((item: NavigationItem) => {
    onNavItemClick?.(item);
  }, [onNavItemClick]);

  // Handle pull to refresh
  const handleDrag = useCallback((event: any, info: PanInfo) => {
    if (info.offset.y > 0 && window.scrollY === 0) {
      const distance = Math.min(info.offset.y, 100);
      setPullDistance(distance);
    }
  }, []);

  const handleDragEnd = useCallback(async (event: any, info: PanInfo) => {
    if (info.offset.y > 80 && window.scrollY === 0 && enablePullToRefresh && onRefresh) {
      setIsRefreshing(true);
      try {
        await onRefresh();
      } finally {
        setIsRefreshing(false);
        setPullDistance(0);
      }
    } else {
      setPullDistance(0);
    }
  }, [enablePullToRefresh, onRefresh]);

  // Format numbers
  const formatNumber = useCallback((num: number): string => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
  }, []);

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setShowSideMenu(false);
      }
    };

    if (showSideMenu) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [showSideMenu]);

  // Animation variants
  const menuVariants = {
    hidden: { x: '-100%' },
    visible: {
      x: 0,
      transition: {
        type: "spring",
        stiffness: 100,
        damping: 20
      }
    }
  };

  const fabMenuVariants = {
    hidden: { opacity: 0, scale: 0.8 },
    visible: {
      opacity: 1,
      scale: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const fabItemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  return (
    <ThemeProvider theme={theme}>
      <MobileContainer>
        {/* Top Bar */}
        <TopBar
          initial={{ y: -60 }}
          animate={{ y: 0 }}
          transition={{ type: "spring", stiffness: 100 }}
        >
          <MenuButton
            onClick={() => setShowSideMenu(true)}
            whileTap={{ scale: 0.95 }}
          >
            ☰
          </MenuButton>
          
          <TopBarTitle>{title}</TopBarTitle>
          
          <NotificationButton
            onClick={onNotificationClick}
            whileTap={{ scale: 0.95 }}
          >
            🔔
            {notifications > 0 && (
              <NotificationBadge>
                {notifications > 99 ? '99+' : notifications}
              </NotificationBadge>
            )}
          </NotificationButton>
        </TopBar>

        {/* Pull to Refresh Indicator */}
        <AnimatePresence>
          {pullDistance > 0 && (
            <PullToRefresh
              initial={{ opacity: 0, y: -20 }}
              animate={{
                opacity: pullDistance / 80,
                y: Math.min(pullDistance - 60, 0)
              }}
            >
              <div style={{ fontSize: '24px' }}>
                {isRefreshing ? '⟳' : '↓'}
              </div>
              <div style={{ fontSize: '12px', color: '#64748b' }}>
                {isRefreshing ? 'Refreshing...' : 'Pull to refresh'}
              </div>
            </PullToRefresh>
          )}
        </AnimatePresence>

        {/* Main Content */}
        <MainContent
          as={motion.div}
          drag="y"
          dragConstraints={{ top: 0, bottom: 0 }}
          dragElastic={0.2}
          onDrag={handleDrag}
          onDragEnd={handleDragEnd}
          style={{ y: pullDistance * 0.5 }}
        >
          {children || (
            <div style={{ textAlign: 'center', padding: '60px 20px', color: '#64748b' }}>
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>📱</div>
              <h2>Mobile Navigation Template</h2>
              <p>Your content goes here. This template includes responsive navigation, side menu, and mobile-optimized interactions.</p>
            </div>
          )}
        </MainContent>

        {/* Bottom Navigation */}
        <BottomNavigation
          initial={{ y: 80 }}
          animate={{ y: 0 }}
          transition={{ type: "spring", stiffness: 100, delay: 0.2 }}
        >
          {navigationItems.map((item) => (
            <NavItem
              key={item.id}
              active={item.active}
              onClick={() => handleNavItemClick(item)}
              whileTap={{ scale: 0.95 }}
            >
              <NavIcon active={item.active}>
                {item.icon}
                {item.badge && item.badge > 0 && (
                  <div style={{
                    position: 'absolute',
                    top: '-4px',
                    right: '-4px',
                    background: '#ef4444',
                    color: 'white',
                    borderRadius: '10px',
                    fontSize: '10px',
                    padding: '2px 6px',
                    minWidth: '16px',
                    textAlign: 'center'
                  }}>
                    {item.badge > 99 ? '99+' : item.badge}
                  </div>
                )}
              </NavIcon>
              <NavLabel active={item.active}>{item.label}</NavLabel>
            </NavItem>
          ))}
        </BottomNavigation>

        {/* Floating Action Button */}
        {fabActions.length > 0 && (
          <>
            <FloatingActionButton
              onClick={() => setShowFABMenu(!showFABMenu)}
              whileTap={{ scale: 0.95 }}
              animate={{ rotate: showFABMenu ? 45 : 0 }}
            >
              +
            </FloatingActionButton>

            <AnimatePresence>
              {showFABMenu && (
                <FABMenu
                  variants={fabMenuVariants}
                  initial="hidden"
                  animate="visible"
                  exit="hidden"
                >
                  {fabActions.map((action) => (
                    <FABMenuItem
                      key={action.id}
                      variants={fabItemVariants}
                      onClick={() => {
                        action.action();
                        setShowFABMenu(false);
                      }}
                      whileTap={{ scale: 0.95 }}
                      title={action.label}
                    >
                      {action.icon}
                    </FABMenuItem>
                  ))}
                </FABMenu>
              )}
            </AnimatePresence>
          </>
        )}

        {/* Side Menu */}
        <AnimatePresence>
          {showSideMenu && (
            <>
              <MenuOverlay
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                onClick={() => setShowSideMenu(false)}
              />
              <SideMenu
                ref={menuRef}
                variants={menuVariants}
                initial="hidden"
                animate="visible"
                exit="hidden"
              >
                {user && (
                  <MenuHeader>
                    <UserInfo>
                      <UserAvatar src={user.avatar} alt={user.name} />
                      <UserDetails>
                        <UserName>{user.name}</UserName>
                        <UserRole>{user.role}</UserRole>
                      </UserDetails>
                    </UserInfo>
                    <MenuStats>
                      <StatItem>
                        <div className="value">{formatNumber(user.stats.followers)}</div>
                        <div className="label">Followers</div>
                      </StatItem>
                      <StatItem>
                        <div className="value">{formatNumber(user.stats.content)}</div>
                        <div className="label">Content</div>
                      </StatItem>
                      <StatItem>
                        <div className="value">${formatNumber(user.stats.revenue)}</div>
                        <div className="label">Revenue</div>
                      </StatItem>
                    </MenuStats>
                  </MenuHeader>
                )}

                <MenuItems>
                  {menuItems.map((item, index) => (
                    <MenuItem
                      key={item.id}
                      active={item.active}
                      onClick={() => handleMenuItemClick(item)}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.05 }}
                    >
                      <MenuIcon>{item.icon}</MenuIcon>
                      {item.label}
                      {item.badge && item.badge > 0 && (
                        <div style={{
                          marginLeft: 'auto',
                          background: '#ef4444',
                          color: 'white',
                          borderRadius: '12px',
                          fontSize: '12px',
                          padding: '4px 8px',
                          minWidth: '20px',
                          textAlign: 'center'
                        }}>
                          {item.badge > 99 ? '99+' : item.badge}
                        </div>
                      )}
                    </MenuItem>
                  ))}
                </MenuItems>
              </SideMenu>
            </>
          )}
        </AnimatePresence>
      </MobileContainer>
    </ThemeProvider>
  );
};

// ===========================
// 🎨 DEFAULT THEME
// ===========================

const defaultTheme = {
  colors: {
    primary: '#667eea',
    secondary: '#764ba2',
    background: '#f8fafc',
    surface: '#ffffff',
    text: '#1e293b',
    textSecondary: '#64748b',
    border: '#e2e8f0',
    success: '#22c55e',
    warning: '#f59e0b',
    error: '#ef4444',
  },
  spacing: {
    xs: '4px',
    sm: '8px',
    md: '16px',
    lg: '24px',
    xl: '32px',
  },
  borderRadius: {
    sm: '8px',
    md: '12px',
    lg: '16px',
    xl: '24px',
  },
};

// ===========================
// 🧪 USAGE EXAMPLES
// ===========================

export const MobileNavigationExamples = {
  basic: {
    navigationItems: [
      { id: '1', label: 'Home', icon: '🏠', active: true },
      { id: '2', label: 'Create', icon: '➕' },
      { id: '3', label: 'Explore', icon: '🔍' },
      { id: '4', label: 'Profile', icon: '👤', badge: 3 }
    ],
    menuItems: [
      { id: '1', label: 'Dashboard', icon: '📊', active: true },
      { id: '2', label: 'My Content', icon: '📁' },
      { id: '3', label: 'Analytics', icon: '📈' },
      { id: '4', label: 'Settings', icon: '⚙️' },
      { id: '5', label: 'Help', icon: '❓' }
    ],
    user: {
      id: '1',
      name: 'Alex Creator',
      role: 'Content Creator',
      avatar: '/api/placeholder/48/48',
      stats: {
        followers: 125000,
        content: 1247,
        revenue: 45600
      }
    },
    fabActions: [
      { id: '1', icon: '🎥', label: 'Record Video', action: () => console.log('Record Video') },
      { id: '2', icon: '📸', label: 'Take Photo', action: () => console.log('Take Photo') },
      { id: '3', icon: '🎵', label: 'Record Audio', action: () => console.log('Record Audio') }
    ]
  }
};

export default MobileNavigationTemplate;