/**
 * 🏗️ Header Layout Template - Enterprise Component
 * ===============================================
 * 
 * © 2025 Fahed Mlaiel <mlaiel@live.de>
 * TOUS DROITS RÉSERVÉS
 * 
 * @author Fahed Mlaiel
 * @role Lead Dev IA + Frontend Architect + UI/UX Expert + Performance Engineer
 * @description Enterprise header layout with responsive navigation, user profile,
 *              notifications, search, and multi-level navigation support
 */

import React, { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import styled, { ThemeProvider, keyframes } from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';

// ===========================
// 🎨 STYLED COMPONENTS & ANIMATIONS
// ===========================

const slideDown = keyframes`
  from { transform: translateY(-100%); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
`;

const fadeIn = keyframes`
  from { opacity: 0; }
  to { opacity: 1; }
`;

const pulse = keyframes`
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
`;

const HeaderContainer = styled(motion.header)`
  position: sticky;
  top: 0;
  z-index: 1000;
  width: 100%;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(226, 232, 240, 0.8);
  box-shadow: 0 4px 32px rgba(0, 0, 0, 0.08);
  animation: ${slideDown} 0.6s ease-out;
`;

const HeaderContent = styled.div`
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 72px;
  
  @media (max-width: 768px) {
    padding: 0 16px;
    height: 64px;
  }
`;

const LogoSection = styled(motion.div)`
  display: flex;
  align-items: center;
  gap: 16px;
  cursor: pointer;
`;

const Logo = styled.img`
  height: 40px;
  width: auto;
  
  @media (max-width: 768px) {
    height: 32px;
  }
`;

const LogoText = styled.h1`
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0;
  
  @media (max-width: 768px) {
    font-size: 20px;
  }
`;

const Navigation = styled.nav`
  display: flex;
  align-items: center;
  gap: 32px;
  
  @media (max-width: 1024px) {
    display: none;
  }
`;

const NavItem = styled(motion.a)<{ active?: boolean }>`
  position: relative;
  font-size: 16px;
  font-weight: ${props => props.active ? '600' : '500'};
  color: ${props => props.active ? '#667eea' : '#64748b'};
  text-decoration: none;
  padding: 8px 16px;
  border-radius: 8px;
  transition: all 0.3s ease;
  cursor: pointer;
  
  &:hover {
    color: #667eea;
    background: rgba(102, 126, 234, 0.08);
  }
  
  ${props => props.active && `
    &::after {
      content: '';
      position: absolute;
      bottom: -8px;
      left: 50%;
      transform: translateX(-50%);
      width: 24px;
      height: 3px;
      background: linear-gradient(135deg, #667eea, #764ba2);
      border-radius: 2px;
    }
  `}
`;

const DropdownMenu = styled(motion.div)`
  position: absolute;
  top: 100%;
  left: 0;
  background: white;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
  border: 1px solid rgba(226, 232, 240, 0.8);
  min-width: 240px;
  z-index: 1001;
`;

const DropdownItem = styled.a`
  display: block;
  padding: 12px 16px;
  color: #64748b;
  text-decoration: none;
  border-radius: 8px;
  transition: all 0.3s ease;
  font-size: 14px;
  
  &:hover {
    background: rgba(102, 126, 234, 0.08);
    color: #667eea;
  }
`;

const SearchSection = styled.div`
  position: relative;
  flex: 1;
  max-width: 400px;
  margin: 0 32px;
  
  @media (max-width: 768px) {
    display: none;
  }
`;

const SearchInput = styled.input`
  width: 100%;
  padding: 12px 16px 12px 48px;
  border: 2px solid rgba(226, 232, 240, 0.8);
  border-radius: 24px;
  font-size: 14px;
  background: rgba(248, 250, 252, 0.8);
  transition: all 0.3s ease;
  
  &:focus {
    outline: none;
    border-color: #667eea;
    background: white;
    box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
  }
  
  &::placeholder {
    color: #94a3b8;
  }
`;

const SearchIcon = styled.div`
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
  font-size: 16px;
`;

const SearchResults = styled(motion.div)`
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border-radius: 12px;
  border: 1px solid rgba(226, 232, 240, 0.8);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
  margin-top: 8px;
  max-height: 400px;
  overflow-y: auto;
  z-index: 1002;
`;

const SearchResultItem = styled.div`
  padding: 12px 16px;
  border-bottom: 1px solid rgba(226, 232, 240, 0.5);
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    background: rgba(102, 126, 234, 0.05);
  }
  
  &:last-child {
    border-bottom: none;
  }
`;

const ActionsSection = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
`;

const NotificationButton = styled(motion.button)`
  position: relative;
  padding: 12px;
  border: none;
  background: rgba(102, 126, 234, 0.08);
  border-radius: 12px;
  color: #667eea;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    background: rgba(102, 126, 234, 0.15);
    transform: translateY(-1px);
  }
`;

const NotificationBadge = styled.div`
  position: absolute;
  top: 6px;
  right: 6px;
  width: 18px;
  height: 18px;
  background: #ef4444;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 600;
  color: white;
  animation: ${pulse} 2s infinite;
`;

const UserProfile = styled(motion.div)`
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    background: rgba(102, 126, 234, 0.08);
  }
`;

const UserAvatar = styled.img`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid rgba(102, 126, 234, 0.3);
  
  @media (max-width: 768px) {
    width: 32px;
    height: 32px;
  }
`;

const UserInfo = styled.div`
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  
  @media (max-width: 768px) {
    display: none;
  }
`;

const UserName = styled.div`
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  line-height: 1.2;
`;

const UserRole = styled.div`
  font-size: 12px;
  color: #64748b;
  line-height: 1.2;
`;

const MobileMenuButton = styled(motion.button)`
  display: none;
  padding: 8px;
  border: none;
  background: none;
  color: #64748b;
  cursor: pointer;
  border-radius: 8px;
  
  &:hover {
    background: rgba(102, 126, 234, 0.08);
    color: #667eea;
  }
  
  @media (max-width: 1024px) {
    display: block;
  }
`;

const MobileMenu = styled(motion.div)`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 2000;
  display: none;
  
  @media (max-width: 1024px) {
    display: flex;
  }
`;

const MobileMenuContent = styled(motion.div)`
  background: white;
  width: 80%;
  max-width: 320px;
  height: 100%;
  padding: 24px;
  box-shadow: 4px 0 20px rgba(0, 0, 0, 0.15);
`;

const MobileNavItem = styled.a`
  display: block;
  padding: 16px 0;
  color: #64748b;
  text-decoration: none;
  font-size: 16px;
  font-weight: 500;
  border-bottom: 1px solid rgba(226, 232, 240, 0.5);
  transition: color 0.3s ease;
  
  &:hover {
    color: #667eea;
  }
`;

const MegaMenu = styled(motion.div)`
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border-bottom: 1px solid rgba(226, 232, 240, 0.8);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  padding: 32px;
  z-index: 1001;
`;

const MegaMenuGrid = styled.div`
  max-width: 1400px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 32px;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: 24px;
  }
`;

const MegaMenuSection = styled.div`
  h3 {
    font-size: 16px;
    font-weight: 600;
    color: #1e293b;
    margin: 0 0 16px 0;
  }
`;

const MegaMenuItem = styled.a`
  display: block;
  padding: 8px 0;
  color: #64748b;
  text-decoration: none;
  font-size: 14px;
  transition: color 0.3s ease;
  
  &:hover {
    color: #667eea;
  }
`;

// ===========================
// 🎯 INTERFACES & TYPES
// ===========================

interface NavigationItem {
  id: string;
  label: string;
  href?: string;
  active?: boolean;
  dropdown?: DropdownItem[];
  megaMenu?: MegaMenuSection[];
}

interface DropdownItem {
  id: string;
  label: string;
  href: string;
  icon?: string;
}

interface MegaMenuSection {
  title: string;
  items: DropdownItem[];
}

interface User {
  id: string;
  name: string;
  email: string;
  avatar: string;
  role: string;
}

interface SearchResult {
  id: string;
  title: string;
  description: string;
  type: 'page' | 'content' | 'user';
  url: string;
}

interface HeaderLayoutProps {
  logo?: string;
  logoText?: string;
  navigation: NavigationItem[];
  user?: User;
  notifications?: number;
  onSearch?: (query: string) => Promise<SearchResult[]>;
  onNotificationClick?: () => void;
  onUserClick?: () => void;
  onLogoClick?: () => void;
  showSearch?: boolean;
  theme?: any;
}

// ===========================
// 🚀 MAIN COMPONENT
// ===========================

export const HeaderLayoutTemplate: React.FC<HeaderLayoutProps> = ({
  logo,
  logoText = 'iacherie',
  navigation,
  user,
  notifications = 0,
  onSearch,
  onNotificationClick,
  onUserClick,
  onLogoClick,
  showSearch = true,
  theme = defaultTheme
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [showSearchResults, setShowSearchResults] = useState(false);
  const [showMobileMenu, setShowMobileMenu] = useState(false);
  const [activeDropdown, setActiveDropdown] = useState<string | null>(null);
  const [activeMegaMenu, setActiveMegaMenu] = useState<string | null>(null);
  
  const searchRef = useRef<HTMLDivElement>(null);
  const dropdownTimeoutRef = useRef<NodeJS.Timeout>();

  // Handle search
  const handleSearch = useCallback(async (query: string) => {
    setSearchQuery(query);
    if (query.length >= 2 && onSearch) {
      try {
        const results = await onSearch(query);
        setSearchResults(results);
        setShowSearchResults(true);
      } catch (error) {
        console.error('Search error:', error);
        setSearchResults([]);
      }
    } else {
      setShowSearchResults(false);
      setSearchResults([]);
    }
  }, [onSearch]);

  // Handle dropdown hover with delay
  const handleDropdownEnter = useCallback((navId: string) => {
    if (dropdownTimeoutRef.current) {
      clearTimeout(dropdownTimeoutRef.current);
    }
    setActiveDropdown(navId);
    setActiveMegaMenu(null);
  }, []);

  const handleDropdownLeave = useCallback(() => {
    dropdownTimeoutRef.current = setTimeout(() => {
      setActiveDropdown(null);
    }, 150);
  }, []);

  const handleMegaMenuEnter = useCallback((navId: string) => {
    if (dropdownTimeoutRef.current) {
      clearTimeout(dropdownTimeoutRef.current);
    }
    setActiveMegaMenu(navId);
    setActiveDropdown(null);
  }, []);

  const handleMegaMenuLeave = useCallback(() => {
    dropdownTimeoutRef.current = setTimeout(() => {
      setActiveMegaMenu(null);
    }, 150);
  }, []);

  // Close search results when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setShowSearchResults(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Animation variants
  const headerVariants = {
    hidden: { y: -100, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        type: "spring",
        stiffness: 100,
        damping: 20
      }
    }
  };

  const mobileMenuVariants = {
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

  return (
    <ThemeProvider theme={theme}>
      <HeaderContainer
        variants={headerVariants}
        initial="hidden"
        animate="visible"
      >
        <HeaderContent>
          {/* Logo Section */}
          <LogoSection
            onClick={onLogoClick}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            {logo && <Logo src={logo} alt={logoText} />}
            <LogoText>{logoText}</LogoText>
          </LogoSection>

          {/* Desktop Navigation */}
          <Navigation>
            {navigation.map((item) => (
              <div
                key={item.id}
                style={{ position: 'relative' }}
                onMouseEnter={() => {
                  if (item.dropdown) handleDropdownEnter(item.id);
                  if (item.megaMenu) handleMegaMenuEnter(item.id);
                }}
                onMouseLeave={() => {
                  if (item.dropdown) handleDropdownLeave();
                  if (item.megaMenu) handleMegaMenuLeave();
                }}
              >
                <NavItem
                  href={item.href}
                  active={item.active}
                  whileHover={{ y: -1 }}
                >
                  {item.label}
                  {(item.dropdown || item.megaMenu) && (
                    <span style={{ marginLeft: '8px', fontSize: '12px' }}>▼</span>
                  )}
                </NavItem>

                {/* Dropdown Menu */}
                <AnimatePresence>
                  {item.dropdown && activeDropdown === item.id && (
                    <DropdownMenu
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      transition={{ duration: 0.2 }}
                    >
                      {item.dropdown.map((dropdownItem) => (
                        <DropdownItem
                          key={dropdownItem.id}
                          href={dropdownItem.href}
                        >
                          {dropdownItem.icon && (
                            <span style={{ marginRight: '8px' }}>{dropdownItem.icon}</span>
                          )}
                          {dropdownItem.label}
                        </DropdownItem>
                      ))}
                    </DropdownMenu>
                  )}
                </AnimatePresence>
              </div>
            ))}
          </Navigation>

          {/* Search Section */}
          {showSearch && (
            <SearchSection ref={searchRef}>
              <SearchIcon>🔍</SearchIcon>
              <SearchInput
                type="text"
                placeholder="Search content, creators, projects..."
                value={searchQuery}
                onChange={(e) => handleSearch(e.target.value)}
              />
              
              <AnimatePresence>
                {showSearchResults && searchResults.length > 0 && (
                  <SearchResults
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                  >
                    {searchResults.map((result) => (
                      <SearchResultItem key={result.id}>
                        <div style={{ fontWeight: '600', fontSize: '14px', marginBottom: '4px' }}>
                          {result.title}
                        </div>
                        <div style={{ fontSize: '12px', color: '#64748b' }}>
                          {result.description}
                        </div>
                      </SearchResultItem>
                    ))}
                  </SearchResults>
                )}
              </AnimatePresence>
            </SearchSection>
          )}

          {/* Actions Section */}
          <ActionsSection>
            {/* Notifications */}
            <NotificationButton
              onClick={onNotificationClick}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              🔔
              {notifications > 0 && (
                <NotificationBadge>
                  {notifications > 99 ? '99+' : notifications}
                </NotificationBadge>
              )}
            </NotificationButton>

            {/* User Profile */}
            {user && (
              <UserProfile
                onClick={onUserClick}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <UserAvatar src={user.avatar} alt={user.name} />
                <UserInfo>
                  <UserName>{user.name}</UserName>
                  <UserRole>{user.role}</UserRole>
                </UserInfo>
              </UserProfile>
            )}

            {/* Mobile Menu Button */}
            <MobileMenuButton
              onClick={() => setShowMobileMenu(true)}
              whileTap={{ scale: 0.95 }}
            >
              ☰
            </MobileMenuButton>
          </ActionsSection>
        </HeaderContent>

        {/* Mega Menu */}
        <AnimatePresence>
          {navigation.find(item => item.id === activeMegaMenu)?.megaMenu && (
            <MegaMenu
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              onMouseEnter={() => handleMegaMenuEnter(activeMegaMenu!)}
              onMouseLeave={handleMegaMenuLeave}
            >
              <MegaMenuGrid>
                {navigation.find(item => item.id === activeMegaMenu)?.megaMenu?.map((section, index) => (
                  <MegaMenuSection key={index}>
                    <h3>{section.title}</h3>
                    {section.items.map((item) => (
                      <MegaMenuItem key={item.id} href={item.href}>
                        {item.label}
                      </MegaMenuItem>
                    ))}
                  </MegaMenuSection>
                ))}
              </MegaMenuGrid>
            </MegaMenu>
          )}
        </AnimatePresence>
      </HeaderContainer>

      {/* Mobile Menu */}
      <AnimatePresence>
        {showMobileMenu && (
          <MobileMenu
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setShowMobileMenu(false)}
          >
            <MobileMenuContent
              variants={mobileMenuVariants}
              initial="hidden"
              animate="visible"
              exit="hidden"
              onClick={(e) => e.stopPropagation()}
            >
              <div style={{ marginBottom: '32px', paddingBottom: '16px', borderBottom: '1px solid #e2e8f0' }}>
                {user && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <UserAvatar src={user.avatar} alt={user.name} />
                    <div>
                      <UserName>{user.name}</UserName>
                      <UserRole>{user.role}</UserRole>
                    </div>
                  </div>
                )}
              </div>
              
              {navigation.map((item) => (
                <MobileNavItem key={item.id} href={item.href}>
                  {item.label}
                </MobileNavItem>
              ))}
            </MobileMenuContent>
          </MobileMenu>
        )}
      </AnimatePresence>
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
    background: '#ffffff',
    surface: '#f8fafc',
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
  shadows: {
    sm: '0 2px 8px rgba(0, 0, 0, 0.1)',
    md: '0 8px 32px rgba(0, 0, 0, 0.1)',
    lg: '0 20px 40px rgba(0, 0, 0, 0.15)',
  },
};

// ===========================
// 🧪 USAGE EXAMPLES
// ===========================

export const HeaderExamples = {
  basic: {
    navigation: [
      { id: '1', label: 'Home', href: '/', active: true },
      { id: '2', label: 'Create', href: '/create' },
      { id: '3', label: 'Explore', href: '/explore' },
      { id: '4', label: 'Analytics', href: '/analytics' }
    ],
    user: {
      id: '1',
      name: 'Alex Creator',
      email: 'alex@example.com',
      avatar: '/api/placeholder/40/40',
      role: 'Content Creator'
    }
  },
  withDropdowns: {
    navigation: [
      { id: '1', label: 'Home', href: '/', active: true },
      {
        id: '2',
        label: 'Create',
        dropdown: [
          { id: '2-1', label: 'Video Content', href: '/create/video', icon: '🎥' },
          { id: '2-2', label: 'Audio Content', href: '/create/audio', icon: '🎵' },
          { id: '2-3', label: 'Text Content', href: '/create/text', icon: '📝' }
        ]
      }
    ]
  }
};

export default HeaderLayoutTemplate;