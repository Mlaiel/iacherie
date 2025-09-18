/**
 * @fileoverview Enterprise Creator Settings Management Template
 * @version 1.0.0
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @copyright 2025 Fahed Mlaiel - All Rights Reserved
 * @license Proprietary - Unauthorized use prohibited
 * 
 * 🚨 INTELLECTUAL PROPERTY WARNING:
 * This code is the exclusive property of Fahed Mlaiel.
 * Unauthorized copying, modification, distribution, or commercial use
 * without explicit written permission is strictly prohibited.
 * Violation will result in immediate legal action.
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import styled, { keyframes, ThemeProvider } from 'styled-components';

// ==================== INTERFACES & TYPES ====================

interface CreatorProfile {
  id: string;
  username: string;
  displayName: string;
  email: string;
  bio: string;
  website?: string;
  socialLinks: {
    twitter?: string;
    instagram?: string;
    youtube?: string;
    tiktok?: string;
    spotify?: string;
    soundcloud?: string;
  };
  avatar: string;
  coverImage: string;
  verified: boolean;
  category: string;
  location?: string;
  language: string;
  timezone: string;
}

interface PrivacySettings {
  profileVisibility: 'public' | 'private' | 'followers_only';
  showEmail: boolean;
  showLocation: boolean;
  allowDirectMessages: 'everyone' | 'followers' | 'none';
  allowCollaborationRequests: 'everyone' | 'verified_only' | 'none';
  dataProcessingConsent: boolean;
  marketingEmailsConsent: boolean;
  analyticsConsent: boolean;
}

interface NotificationSettings {
  email: {
    newFollower: boolean;
    collaborationRequest: boolean;
    contentLike: boolean;
    contentComment: boolean;
    paymentReceived: boolean;
    systemUpdates: boolean;
    marketingEmails: boolean;
  };
  push: {
    newFollower: boolean;
    collaborationRequest: boolean;
    contentInteraction: boolean;
    liveStream: boolean;
    systemAlerts: boolean;
  };
  frequency: 'instant' | 'daily' | 'weekly' | 'never';
}

interface SecuritySettings {
  twoFactorEnabled: boolean;
  loginNotifications: boolean;
  sessionTimeout: number; // in minutes
  trustedDevices: Array<{
    id: string;
    name: string;
    lastSeen: Date;
    location: string;
  }>;
  passwordLastChanged: Date;
  accountDeletionRequested?: Date;
}

interface MonetizationSettings {
  payoutMethod: 'stripe' | 'paypal' | 'bank_transfer' | 'crypto';
  payoutSchedule: 'weekly' | 'bi_weekly' | 'monthly';
  minimumPayout: number;
  currency: 'USD' | 'EUR' | 'GBP' | 'CAD';
  taxInformation: {
    taxId?: string;
    country: string;
    businessType: 'individual' | 'business';
  };
  subscriptionPlans: Array<{
    id: string;
    name: string;
    price: number;
    active: boolean;
  }>;
  contentPricing: {
    defaultPrice: number;
    premiumMultiplier: number;
    bulkDiscounts: boolean;
  };
}

interface ContentSettings {
  defaultVisibility: 'public' | 'private' | 'unlisted' | 'premium';
  contentLicensing: 'all_rights_reserved' | 'creative_commons' | 'custom';
  watermarkEnabled: boolean;
  downloadEnabled: boolean;
  commentsEnabled: boolean;
  ratingsEnabled: boolean;
  aiProcessingEnabled: boolean;
  qualitySettings: {
    uploadQuality: 'original' | 'high' | 'medium';
    processingPriority: 'standard' | 'premium';
    thumbnailGeneration: boolean;
  };
}

interface CreatorSettingsProps {
  creatorId: string;
  className?: string;
  theme?: 'light' | 'dark' | 'auto';
  onSettingsUpdate?: (section: string, settings: any) => void;
  onProfileUpdate?: (profile: CreatorProfile) => void;
  onSecurityAction?: (action: string, data?: any) => void;
}

// ==================== STYLED COMPONENTS ====================

const slideInLeft = keyframes`
  from { opacity: 0; transform: translateX(-30px); }
  to { opacity: 1; transform: translateX(0); }
`;

const fadeIn = keyframes`
  from { opacity: 0; }
  to { opacity: 1; }
`;

const success = keyframes`
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
`;

const SettingsContainer = styled.div`
  display: flex;
  gap: 32px;
  padding: 24px;
  background: ${props => props.theme.colors.background};
  min-height: 100vh;
  animation: ${fadeIn} 0.6s ease-out;

  @media (max-width: 1024px) {
    flex-direction: column;
    gap: 24px;
  }
`;

const Sidebar = styled.nav`
  width: 280px;
  flex-shrink: 0;
  background: ${props => props.theme.colors.cardBackground};
  border-radius: 20px;
  padding: 28px;
  height: fit-content;
  position: sticky;
  top: 24px;
  border: 1px solid ${props => props.theme.colors.border};
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  animation: ${slideInLeft} 0.8s ease-out;

  @media (max-width: 1024px) {
    width: 100%;
    position: static;
  }
`;

const SidebarTitle = styled.h2`
  margin: 0 0 24px 0;
  font-size: 24px;
  font-weight: 800;
  color: ${props => props.theme.colors.text};
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
`;

const NavList = styled.ul`
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const NavItem = styled.li<{ active?: boolean }>`
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 600;
  color: ${props => props.active ? 'white' : props.theme.colors.textSecondary};
  background: ${props => props.active 
    ? 'linear-gradient(135deg, #3b82f6, #2563eb)' 
    : 'transparent'
  };

  &:hover {
    background: ${props => props.active 
      ? 'linear-gradient(135deg, #3b82f6, #2563eb)' 
      : props.theme.colors.hover
    };
    color: ${props => props.active ? 'white' : props.theme.colors.text};
    transform: translateX(4px);
  }
`;

const NavIcon = styled.span`
  font-size: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
`;

const MainContent = styled.main`
  flex: 1;
  background: ${props => props.theme.colors.cardBackground};
  border-radius: 20px;
  padding: 32px;
  border: 1px solid ${props => props.theme.colors.border};
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  animation: ${slideInLeft} 0.8s ease-out 0.2s both;
`;

const ContentHeader = styled.div`
  margin-bottom: 32px;
`;

const ContentTitle = styled.h1`
  margin: 0 0 8px 0;
  font-size: 32px;
  font-weight: 800;
  color: ${props => props.theme.colors.text};
`;

const ContentDescription = styled.p`
  margin: 0;
  font-size: 16px;
  color: ${props => props.theme.colors.textSecondary};
  line-height: 1.6;
`;

const SettingsSection = styled.div`
  margin-bottom: 40px;
  
  &:last-child {
    margin-bottom: 0;
  }
`;

const SectionTitle = styled.h3`
  margin: 0 0 20px 0;
  font-size: 20px;
  font-weight: 700;
  color: ${props => props.theme.colors.text};
  display: flex;
  align-items: center;
  gap: 12px;
`;

const SectionIcon = styled.span`
  font-size: 24px;
`;

const FormGrid = styled.div<{ columns?: number }>`
  display: grid;
  grid-template-columns: repeat(${props => props.columns || 1}, 1fr);
  gap: 24px;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const FormField = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const Label = styled.label`
  font-size: 14px;
  font-weight: 600;
  color: ${props => props.theme.colors.text};
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

const Input = styled.input`
  padding: 16px;
  border: 2px solid ${props => props.theme.colors.border};
  border-radius: 12px;
  background: ${props => props.theme.colors.background};
  color: ${props => props.theme.colors.text};
  font-size: 16px;
  transition: all 0.3s ease;

  &:focus {
    outline: none;
    border-color: ${props => props.theme.colors.primary};
    box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
  }

  &::placeholder {
    color: ${props => props.theme.colors.textSecondary};
  }
`;

const TextArea = styled.textarea`
  padding: 16px;
  border: 2px solid ${props => props.theme.colors.border};
  border-radius: 12px;
  background: ${props => props.theme.colors.background};
  color: ${props => props.theme.colors.text};
  font-size: 16px;
  resize: vertical;
  min-height: 120px;
  font-family: inherit;
  transition: all 0.3s ease;

  &:focus {
    outline: none;
    border-color: ${props => props.theme.colors.primary};
    box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
  }

  &::placeholder {
    color: ${props => props.theme.colors.textSecondary};
  }
`;

const Select = styled.select`
  padding: 16px;
  border: 2px solid ${props => props.theme.colors.border};
  border-radius: 12px;
  background: ${props => props.theme.colors.background};
  color: ${props => props.theme.colors.text};
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s ease;

  &:focus {
    outline: none;
    border-color: ${props => props.theme.colors.primary};
    box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
  }
`;

const Toggle = styled.div<{ checked?: boolean }>`
  position: relative;
  width: 60px;
  height: 32px;
  background: ${props => props.checked ? props.theme.colors.primary : props.theme.colors.border};
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s ease;

  &::after {
    content: '';
    position: absolute;
    top: 4px;
    left: ${props => props.checked ? '32px' : '4px'};
    width: 24px;
    height: 24px;
    background: white;
    border-radius: 50%;
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  }
`;

const ToggleRow = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 0;
  border-bottom: 1px solid ${props => props.theme.colors.border};

  &:last-child {
    border-bottom: none;
  }
`;

const ToggleLabel = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
`;

const ToggleTitle = styled.span`
  font-size: 16px;
  font-weight: 600;
  color: ${props => props.theme.colors.text};
`;

const ToggleDescription = styled.span`
  font-size: 14px;
  color: ${props => props.theme.colors.textSecondary};
`;

const ActionButton = styled.button<{ variant?: 'primary' | 'secondary' | 'danger' | 'success' }>`
  padding: 16px 32px;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 8px;

  ${props => {
    switch (props.variant) {
      case 'primary':
        return `
          background: linear-gradient(135deg, #3b82f6, #2563eb);
          color: white;
          &:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(59, 130, 246, 0.3); }
        `;
      case 'success':
        return `
          background: linear-gradient(135deg, #22c55e, #16a34a);
          color: white;
          animation: ${success} 0.5s ease-out;
          &:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(34, 197, 94, 0.3); }
        `;
      case 'danger':
        return `
          background: linear-gradient(135deg, #ef4444, #dc2626);
          color: white;
          &:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(239, 68, 68, 0.3); }
        `;
      default:
        return `
          background: ${props.theme.colors.background};
          color: ${props.theme.colors.text};
          border: 2px solid ${props.theme.colors.border};
          &:hover { background: ${props.theme.colors.hover}; }
        `;
    }
  }}

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none !important;
    box-shadow: none !important;
  }
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 16px;
  margin-top: 32px;
  flex-wrap: wrap;
`;

const SecurityAlert = styled.div<{ type: 'info' | 'warning' | 'success' | 'error' }>`
  padding: 16px 20px;
  border-radius: 12px;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 500;

  ${props => {
    switch (props.type) {
      case 'success':
        return `background: rgba(34, 197, 94, 0.1); color: #16a34a; border-left: 4px solid #22c55e;`;
      case 'warning':
        return `background: rgba(245, 158, 11, 0.1); color: #d97706; border-left: 4px solid #f59e0b;`;
      case 'error':
        return `background: rgba(239, 68, 68, 0.1); color: #dc2626; border-left: 4px solid #ef4444;`;
      default:
        return `background: rgba(59, 130, 246, 0.1); color: #2563eb; border-left: 4px solid #3b82f6;`;
    }
  }}
`;

const DeviceCard = styled.div`
  padding: 20px;
  background: ${props => props.theme.colors.background};
  border-radius: 12px;
  border: 1px solid ${props => props.theme.colors.border};
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
`;

const DeviceInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
`;

const DeviceName = styled.span`
  font-weight: 600;
  color: ${props => props.theme.colors.text};
`;

const DeviceDetails = styled.span`
  font-size: 14px;
  color: ${props => props.theme.colors.textSecondary};
`;

// ==================== THEME ====================

const theme = {
  colors: {
    background: '#f8fafc',
    cardBackground: '#ffffff',
    text: '#1e293b',
    textSecondary: '#64748b',
    border: '#e2e8f0',
    hover: '#f1f5f9',
    primary: '#3b82f6',
    success: '#22c55e',
    error: '#ef4444',
    warning: '#f59e0b'
  }
};

// ==================== MAIN COMPONENT ====================

export const CreatorSettingsTemplate: React.FC<CreatorSettingsProps> = ({
  creatorId,
  className,
  theme: themeMode = 'light',
  onSettingsUpdate,
  onProfileUpdate,
  onSecurityAction
}) => {
  // ================ STATE MANAGEMENT ================
  const [activeSection, setActiveSection] = useState('profile');
  const [profile, setProfile] = useState<CreatorProfile>({
    id: creatorId,
    username: 'epic_creator',
    displayName: 'Epic Creator',
    email: 'creator@example.com',
    bio: 'Professional content creator specializing in epic orchestral music and cinematic soundscapes.',
    website: 'https://epiccreator.com',
    socialLinks: {
      twitter: '@epiccreator',
      instagram: '@epiccreator',
      youtube: 'epiccreator',
      spotify: 'epiccreator'
    },
    avatar: 'https://api.placeholder.pics/150x150',
    coverImage: 'https://api.placeholder.pics/1200x400',
    verified: true,
    category: 'Music & Audio',
    location: 'Los Angeles, CA',
    language: 'en',
    timezone: 'America/Los_Angeles'
  });

  const [privacy, setPrivacy] = useState<PrivacySettings>({
    profileVisibility: 'public',
    showEmail: false,
    showLocation: true,
    allowDirectMessages: 'followers',
    allowCollaborationRequests: 'verified_only',
    dataProcessingConsent: true,
    marketingEmailsConsent: false,
    analyticsConsent: true
  });

  const [notifications, setNotifications] = useState<NotificationSettings>({
    email: {
      newFollower: true,
      collaborationRequest: true,
      contentLike: false,
      contentComment: true,
      paymentReceived: true,
      systemUpdates: true,
      marketingEmails: false
    },
    push: {
      newFollower: true,
      collaborationRequest: true,
      contentInteraction: false,
      liveStream: true,
      systemAlerts: true
    },
    frequency: 'instant'
  });

  const [security, setSecurity] = useState<SecuritySettings>({
    twoFactorEnabled: true,
    loginNotifications: true,
    sessionTimeout: 30,
    trustedDevices: [
      {
        id: '1',
        name: 'MacBook Pro',
        lastSeen: new Date(),
        location: 'Los Angeles, CA'
      },
      {
        id: '2',
        name: 'iPhone 15 Pro',
        lastSeen: new Date(Date.now() - 86400000),
        location: 'Los Angeles, CA'
      }
    ],
    passwordLastChanged: new Date(Date.now() - 30 * 86400000)
  });

  const [monetization, setMonetization] = useState<MonetizationSettings>({
    payoutMethod: 'stripe',
    payoutSchedule: 'monthly',
    minimumPayout: 50,
    currency: 'USD',
    taxInformation: {
      country: 'US',
      businessType: 'individual'
    },
    subscriptionPlans: [
      { id: '1', name: 'Essential Supporter', price: 4.99, active: true },
      { id: '2', name: 'Premium Supporter', price: 14.99, active: true },
      { id: '3', name: 'Ultimate Supporter', price: 29.99, active: false }
    ],
    contentPricing: {
      defaultPrice: 9.99,
      premiumMultiplier: 2.0,
      bulkDiscounts: true
    }
  });

  const [content, setContent] = useState<ContentSettings>({
    defaultVisibility: 'public',
    contentLicensing: 'all_rights_reserved',
    watermarkEnabled: true,
    downloadEnabled: false,
    commentsEnabled: true,
    ratingsEnabled: true,
    aiProcessingEnabled: true,
    qualitySettings: {
      uploadQuality: 'original',
      processingPriority: 'premium',
      thumbnailGeneration: true
    }
  });

  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [savedSuccessfully, setSavedSuccessfully] = useState(false);

  // ================ NAVIGATION ITEMS ================
  const navigationItems = [
    { id: 'profile', label: 'Profile', icon: '👤' },
    { id: 'privacy', label: 'Privacy', icon: '🔒' },
    { id: 'notifications', label: 'Notifications', icon: '🔔' },
    { id: 'security', label: 'Security', icon: '🛡️' },
    { id: 'monetization', label: 'Monetization', icon: '💰' },
    { id: 'content', label: 'Content', icon: '📁' },
    { id: 'account', label: 'Account', icon: '⚙️' }
  ];

  // ================ EVENT HANDLERS ================
  const handleSave = useCallback(async () => {
    try {
      const currentSettings = {
        profile: activeSection === 'profile' ? profile : undefined,
        privacy: activeSection === 'privacy' ? privacy : undefined,
        notifications: activeSection === 'notifications' ? notifications : undefined,
        security: activeSection === 'security' ? security : undefined,
        monetization: activeSection === 'monetization' ? monetization : undefined,
        content: activeSection === 'content' ? content : undefined
      };

      const relevantSettings = currentSettings[activeSection as keyof typeof currentSettings];
      if (relevantSettings) {
        onSettingsUpdate?.(activeSection, relevantSettings);
        if (activeSection === 'profile') {
          onProfileUpdate?.(profile);
        }
      }

      setSavedSuccessfully(true);
      setHasUnsavedChanges(false);
      
      setTimeout(() => setSavedSuccessfully(false), 3000);
    } catch (error) {
      console.error('Failed to save settings:', error);
    }
  }, [activeSection, profile, privacy, notifications, security, monetization, content, onSettingsUpdate, onProfileUpdate]);

  const handleToggle = useCallback((section: string, field: string, value?: boolean) => {
    setHasUnsavedChanges(true);
    
    switch (section) {
      case 'privacy':
        setPrivacy(prev => ({ ...prev, [field]: value !== undefined ? value : !prev[field as keyof PrivacySettings] }));
        break;
      case 'notifications':
        if (field.includes('.')) {
          const [category, subField] = field.split('.');
          setNotifications(prev => ({
            ...prev,
            [category]: {
              ...prev[category as keyof typeof prev.email],
              [subField]: value !== undefined ? value : !prev[category as keyof typeof prev.email][subField as keyof typeof prev.email]
            }
          }));
        } else {
          setNotifications(prev => ({ ...prev, [field]: value !== undefined ? value : !prev[field as keyof NotificationSettings] }));
        }
        break;
      case 'security':
        setSecurity(prev => ({ ...prev, [field]: value !== undefined ? value : !prev[field as keyof SecuritySettings] }));
        break;
      case 'content':
        setContent(prev => ({ ...prev, [field]: value !== undefined ? value : !prev[field as keyof ContentSettings] }));
        break;
    }
  }, []);

  // ================ SECTION RENDERERS ================
  const renderProfileSection = () => (
    <SettingsSection>
      <SectionTitle>
        <SectionIcon>👤</SectionIcon>
        Profile Information
      </SectionTitle>
      
      <FormGrid columns={2}>
        <FormField>
          <Label>Username</Label>
          <Input
            type="text"
            value={profile.username}
            onChange={(e) => {
              setProfile(prev => ({ ...prev, username: e.target.value }));
              setHasUnsavedChanges(true);
            }}
            placeholder="Enter username"
          />
        </FormField>
        
        <FormField>
          <Label>Display Name</Label>
          <Input
            type="text"
            value={profile.displayName}
            onChange={(e) => {
              setProfile(prev => ({ ...prev, displayName: e.target.value }));
              setHasUnsavedChanges(true);
            }}
            placeholder="Enter display name"
          />
        </FormField>
        
        <FormField>
          <Label>Email</Label>
          <Input
            type="email"
            value={profile.email}
            onChange={(e) => {
              setProfile(prev => ({ ...prev, email: e.target.value }));
              setHasUnsavedChanges(true);
            }}
            placeholder="Enter email"
          />
        </FormField>
        
        <FormField>
          <Label>Category</Label>
          <Select
            value={profile.category}
            onChange={(e) => {
              setProfile(prev => ({ ...prev, category: e.target.value }));
              setHasUnsavedChanges(true);
            }}
          >
            <option value="Music & Audio">Music & Audio</option>
            <option value="Video & Film">Video & Film</option>
            <option value="Art & Design">Art & Design</option>
            <option value="Writing">Writing</option>
            <option value="Photography">Photography</option>
          </Select>
        </FormField>
      </FormGrid>
      
      <FormField>
        <Label>Bio</Label>
        <TextArea
          value={profile.bio}
          onChange={(e) => {
            setProfile(prev => ({ ...prev, bio: e.target.value }));
            setHasUnsavedChanges(true);
          }}
          placeholder="Tell us about yourself..."
        />
      </FormField>
      
      <FormGrid columns={2}>
        <FormField>
          <Label>Website</Label>
          <Input
            type="url"
            value={profile.website || ''}
            onChange={(e) => {
              setProfile(prev => ({ ...prev, website: e.target.value }));
              setHasUnsavedChanges(true);
            }}
            placeholder="https://yourwebsite.com"
          />
        </FormField>
        
        <FormField>
          <Label>Location</Label>
          <Input
            type="text"
            value={profile.location || ''}
            onChange={(e) => {
              setProfile(prev => ({ ...prev, location: e.target.value }));
              setHasUnsavedChanges(true);
            }}
            placeholder="City, Country"
          />
        </FormField>
      </FormGrid>
    </SettingsSection>
  );

  const renderPrivacySection = () => (
    <SettingsSection>
      <SectionTitle>
        <SectionIcon>🔒</SectionIcon>
        Privacy Settings
      </SectionTitle>
      
      <ToggleRow>
        <ToggleLabel>
          <ToggleTitle>Profile Visibility</ToggleTitle>
          <ToggleDescription>Who can see your profile</ToggleDescription>
        </ToggleLabel>
        <Select
          value={privacy.profileVisibility}
          onChange={(e) => {
            setPrivacy(prev => ({ ...prev, profileVisibility: e.target.value as any }));
            setHasUnsavedChanges(true);
          }}
          style={{ width: '200px' }}
        >
          <option value="public">Public</option>
          <option value="followers_only">Followers Only</option>
          <option value="private">Private</option>
        </Select>
      </ToggleRow>
      
      <ToggleRow>
        <ToggleLabel>
          <ToggleTitle>Show Email</ToggleTitle>
          <ToggleDescription>Display email on public profile</ToggleDescription>
        </ToggleLabel>
        <Toggle
          checked={privacy.showEmail}
          onClick={() => handleToggle('privacy', 'showEmail')}
        />
      </ToggleRow>
      
      <ToggleRow>
        <ToggleLabel>
          <ToggleTitle>Show Location</ToggleTitle>
          <ToggleDescription>Display location on public profile</ToggleDescription>
        </ToggleLabel>
        <Toggle
          checked={privacy.showLocation}
          onClick={() => handleToggle('privacy', 'showLocation')}
        />
      </ToggleRow>
      
      <ToggleRow>
        <ToggleLabel>
          <ToggleTitle>Direct Messages</ToggleTitle>
          <ToggleDescription>Who can send you direct messages</ToggleDescription>
        </ToggleLabel>
        <Select
          value={privacy.allowDirectMessages}
          onChange={(e) => {
            setPrivacy(prev => ({ ...prev, allowDirectMessages: e.target.value as any }));
            setHasUnsavedChanges(true);
          }}
          style={{ width: '200px' }}
        >
          <option value="everyone">Everyone</option>
          <option value="followers">Followers Only</option>
          <option value="none">No One</option>
        </Select>
      </ToggleRow>
    </SettingsSection>
  );

  const renderNotificationsSection = () => (
    <SettingsSection>
      <SectionTitle>
        <SectionIcon>🔔</SectionIcon>
        Notification Preferences
      </SectionTitle>
      
      <h4 style={{ margin: '24px 0 16px 0', color: theme.colors.text }}>Email Notifications</h4>
      
      <ToggleRow>
        <ToggleLabel>
          <ToggleTitle>New Followers</ToggleTitle>
          <ToggleDescription>When someone follows you</ToggleDescription>
        </ToggleLabel>
        <Toggle
          checked={notifications.email.newFollower}
          onClick={() => handleToggle('notifications', 'email.newFollower')}
        />
      </ToggleRow>
      
      <ToggleRow>
        <ToggleLabel>
          <ToggleTitle>Collaboration Requests</ToggleTitle>
          <ToggleDescription>When someone wants to collaborate</ToggleDescription>
        </ToggleLabel>
        <Toggle
          checked={notifications.email.collaborationRequest}
          onClick={() => handleToggle('notifications', 'email.collaborationRequest')}
        />
      </ToggleRow>
      
      <ToggleRow>
        <ToggleLabel>
          <ToggleTitle>Payment Received</ToggleTitle>
          <ToggleDescription>When you receive payments</ToggleDescription>
        </ToggleLabel>
        <Toggle
          checked={notifications.email.paymentReceived}
          onClick={() => handleToggle('notifications', 'email.paymentReceived')}
        />
      </ToggleRow>
      
      <h4 style={{ margin: '24px 0 16px 0', color: theme.colors.text }}>Push Notifications</h4>
      
      <ToggleRow>
        <ToggleLabel>
          <ToggleTitle>Live Streams</ToggleTitle>
          <ToggleDescription>When creators you follow go live</ToggleDescription>
        </ToggleLabel>
        <Toggle
          checked={notifications.push.liveStream}
          onClick={() => handleToggle('notifications', 'push.liveStream')}
        />
      </ToggleRow>
      
      <ToggleRow>
        <ToggleLabel>
          <ToggleTitle>System Alerts</ToggleTitle>
          <ToggleDescription>Important system notifications</ToggleDescription>
        </ToggleLabel>
        <Toggle
          checked={notifications.push.systemAlerts}
          onClick={() => handleToggle('notifications', 'push.systemAlerts')}
        />
      </ToggleRow>
    </SettingsSection>
  );

  const renderSecuritySection = () => (
    <SettingsSection>
      <SectionTitle>
        <SectionIcon>🛡️</SectionIcon>
        Security & Access
      </SectionTitle>
      
      {!security.twoFactorEnabled && (
        <SecurityAlert type="warning">
          ⚠️ Two-factor authentication is disabled. Enable it for better security.
        </SecurityAlert>
      )}
      
      <ToggleRow>
        <ToggleLabel>
          <ToggleTitle>Two-Factor Authentication</ToggleTitle>
          <ToggleDescription>Add an extra layer of security to your account</ToggleDescription>
        </ToggleLabel>
        <Toggle
          checked={security.twoFactorEnabled}
          onClick={() => handleToggle('security', 'twoFactorEnabled')}
        />
      </ToggleRow>
      
      <ToggleRow>
        <ToggleLabel>
          <ToggleTitle>Login Notifications</ToggleTitle>
          <ToggleDescription>Get notified when someone logs into your account</ToggleDescription>
        </ToggleLabel>
        <Toggle
          checked={security.loginNotifications}
          onClick={() => handleToggle('security', 'loginNotifications')}
        />
      </ToggleRow>
      
      <FormField>
        <Label>Session Timeout (minutes)</Label>
        <Input
          type="number"
          value={security.sessionTimeout}
          onChange={(e) => {
            setSecurity(prev => ({ ...prev, sessionTimeout: parseInt(e.target.value) }));
            setHasUnsavedChanges(true);
          }}
          min="5"
          max="1440"
        />
      </FormField>
      
      <div style={{ marginTop: '32px' }}>
        <h4 style={{ margin: '0 0 16px 0', color: theme.colors.text }}>Trusted Devices</h4>
        {security.trustedDevices.map((device) => (
          <DeviceCard key={device.id}>
            <DeviceInfo>
              <DeviceName>{device.name}</DeviceName>
              <DeviceDetails>
                Last seen: {device.lastSeen.toLocaleDateString()} • {device.location}
              </DeviceDetails>
            </DeviceInfo>
            <ActionButton
              variant="secondary"
              onClick={() => onSecurityAction?.('removeDevice', device.id)}
            >
              Remove
            </ActionButton>
          </DeviceCard>
        ))}
      </div>
      
      <ButtonGroup>
        <ActionButton
          variant="primary"
          onClick={() => onSecurityAction?.('changePassword')}
        >
          Change Password
        </ActionButton>
        <ActionButton
          variant="secondary"
          onClick={() => onSecurityAction?.('downloadData')}
        >
          Download My Data
        </ActionButton>
      </ButtonGroup>
    </SettingsSection>
  );

  const renderMonetizationSection = () => (
    <SettingsSection>
      <SectionTitle>
        <SectionIcon>💰</SectionIcon>
        Monetization Settings
      </SectionTitle>
      
      <FormGrid columns={2}>
        <FormField>
          <Label>Payout Method</Label>
          <Select
            value={monetization.payoutMethod}
            onChange={(e) => {
              setMonetization(prev => ({ ...prev, payoutMethod: e.target.value as any }));
              setHasUnsavedChanges(true);
            }}
          >
            <option value="stripe">Stripe</option>
            <option value="paypal">PayPal</option>
            <option value="bank_transfer">Bank Transfer</option>
            <option value="crypto">Cryptocurrency</option>
          </Select>
        </FormField>
        
        <FormField>
          <Label>Payout Schedule</Label>
          <Select
            value={monetization.payoutSchedule}
            onChange={(e) => {
              setMonetization(prev => ({ ...prev, payoutSchedule: e.target.value as any }));
              setHasUnsavedChanges(true);
            }}
          >
            <option value="weekly">Weekly</option>
            <option value="bi_weekly">Bi-weekly</option>
            <option value="monthly">Monthly</option>
          </Select>
        </FormField>
        
        <FormField>
          <Label>Minimum Payout ($)</Label>
          <Input
            type="number"
            value={monetization.minimumPayout}
            onChange={(e) => {
              setMonetization(prev => ({ ...prev, minimumPayout: parseFloat(e.target.value) }));
              setHasUnsavedChanges(true);
            }}
            min="10"
            step="10"
          />
        </FormField>
        
        <FormField>
          <Label>Currency</Label>
          <Select
            value={monetization.currency}
            onChange={(e) => {
              setMonetization(prev => ({ ...prev, currency: e.target.value as any }));
              setHasUnsavedChanges(true);
            }}
          >
            <option value="USD">USD - US Dollar</option>
            <option value="EUR">EUR - Euro</option>
            <option value="GBP">GBP - British Pound</option>
            <option value="CAD">CAD - Canadian Dollar</option>
          </Select>
        </FormField>
      </FormGrid>
      
      <h4 style={{ margin: '32px 0 16px 0', color: theme.colors.text }}>Subscription Plans</h4>
      {monetization.subscriptionPlans.map((plan) => (
        <ToggleRow key={plan.id}>
          <ToggleLabel>
            <ToggleTitle>{plan.name}</ToggleTitle>
            <ToggleDescription>${plan.price}/month</ToggleDescription>
          </ToggleLabel>
          <Toggle
            checked={plan.active}
            onClick={() => {
              setMonetization(prev => ({
                ...prev,
                subscriptionPlans: prev.subscriptionPlans.map(p =>
                  p.id === plan.id ? { ...p, active: !p.active } : p
                )
              }));
              setHasUnsavedChanges(true);
            }}
          />
        </ToggleRow>
      ))}
    </SettingsSection>
  );

  const renderContentSection = () => (
    <SettingsSection>
      <SectionTitle>
        <SectionIcon>📁</SectionIcon>
        Content Settings
      </SectionTitle>
      
      <FormGrid columns={2}>
        <FormField>
          <Label>Default Visibility</Label>
          <Select
            value={content.defaultVisibility}
            onChange={(e) => {
              setContent(prev => ({ ...prev, defaultVisibility: e.target.value as any }));
              setHasUnsavedChanges(true);
            }}
          >
            <option value="public">Public</option>
            <option value="unlisted">Unlisted</option>
            <option value="private">Private</option>
            <option value="premium">Premium Only</option>
          </Select>
        </FormField>
        
        <FormField>
          <Label>Content Licensing</Label>
          <Select
            value={content.contentLicensing}
            onChange={(e) => {
              setContent(prev => ({ ...prev, contentLicensing: e.target.value as any }));
              setHasUnsavedChanges(true);
            }}
          >
            <option value="all_rights_reserved">All Rights Reserved</option>
            <option value="creative_commons">Creative Commons</option>
            <option value="custom">Custom License</option>
          </Select>
        </FormField>
      </FormGrid>
      
      <ToggleRow>
        <ToggleLabel>
          <ToggleTitle>Watermark Protection</ToggleTitle>
          <ToggleDescription>Add watermark to prevent unauthorized use</ToggleDescription>
        </ToggleLabel>
        <Toggle
          checked={content.watermarkEnabled}
          onClick={() => handleToggle('content', 'watermarkEnabled')}
        />
      </ToggleRow>
      
      <ToggleRow>
        <ToggleLabel>
          <ToggleTitle>Enable Downloads</ToggleTitle>
          <ToggleDescription>Allow users to download your content</ToggleDescription>
        </ToggleLabel>
        <Toggle
          checked={content.downloadEnabled}
          onClick={() => handleToggle('content', 'downloadEnabled')}
        />
      </ToggleRow>
      
      <ToggleRow>
        <ToggleLabel>
          <ToggleTitle>AI Processing</ToggleTitle>
          <ToggleDescription>Use AI to enhance and analyze your content</ToggleDescription>
        </ToggleLabel>
        <Toggle
          checked={content.aiProcessingEnabled}
          onClick={() => handleToggle('content', 'aiProcessingEnabled')}
        />
      </ToggleRow>
      
      <ToggleRow>
        <ToggleLabel>
          <ToggleTitle>Comments</ToggleTitle>
          <ToggleDescription>Allow users to comment on your content</ToggleDescription>
        </ToggleLabel>
        <Toggle
          checked={content.commentsEnabled}
          onClick={() => handleToggle('content', 'commentsEnabled')}
        />
      </ToggleRow>
    </SettingsSection>
  );

  const renderAccountSection = () => (
    <SettingsSection>
      <SectionTitle>
        <SectionIcon>⚙️</SectionIcon>
        Account Management
      </SectionTitle>
      
      <SecurityAlert type="info">
        💡 Account actions are permanent and cannot be undone. Please proceed with caution.
      </SecurityAlert>
      
      <ButtonGroup>
        <ActionButton
          variant="secondary"
          onClick={() => onSecurityAction?.('exportData')}
        >
          Export Account Data
        </ActionButton>
        
        <ActionButton
          variant="secondary"
          onClick={() => onSecurityAction?.('pauseAccount')}
        >
          Pause Account
        </ActionButton>
        
        <ActionButton
          variant="danger"
          onClick={() => onSecurityAction?.('deleteAccount')}
        >
          Delete Account
        </ActionButton>
      </ButtonGroup>
      
      <div style={{ marginTop: '32px', padding: '24px', background: '#fef2f2', borderRadius: '12px', border: '1px solid #fecaca' }}>
        <h4 style={{ margin: '0 0 12px 0', color: '#dc2626' }}>Danger Zone</h4>
        <p style={{ margin: '0 0 16px 0', color: '#7f1d1d', fontSize: '14px' }}>
          Once you delete your account, there is no going back. Please be certain.
        </p>
        <ActionButton
          variant="danger"
          onClick={() => onSecurityAction?.('confirmDelete')}
        >
          I understand, delete my account
        </ActionButton>
      </div>
    </SettingsSection>
  );

  // ================ RENDER SECTION CONTENT ================
  const renderSectionContent = () => {
    switch (activeSection) {
      case 'profile':
        return renderProfileSection();
      case 'privacy':
        return renderPrivacySection();
      case 'notifications':
        return renderNotificationsSection();
      case 'security':
        return renderSecuritySection();
      case 'monetization':
        return renderMonetizationSection();
      case 'content':
        return renderContentSection();
      case 'account':
        return renderAccountSection();
      default:
        return renderProfileSection();
    }
  };

  const getSectionTitle = () => {
    const section = navigationItems.find(item => item.id === activeSection);
    return section ? section.label : 'Settings';
  };

  const getSectionDescription = () => {
    const descriptions = {
      profile: 'Manage your public profile and personal information',
      privacy: 'Control who can see your information and content',
      notifications: 'Choose what notifications you want to receive',
      security: 'Secure your account with advanced security features',
      monetization: 'Set up how you earn money from your content',
      content: 'Configure default settings for your content',
      account: 'Manage your account settings and data'
    };
    return descriptions[activeSection as keyof typeof descriptions] || '';
  };

  // ================ RENDER ================
  return (
    <ThemeProvider theme={theme}>
      <SettingsContainer className={className}>
        <Sidebar>
          <SidebarTitle>Settings</SidebarTitle>
          <NavList>
            {navigationItems.map((item) => (
              <NavItem
                key={item.id}
                active={activeSection === item.id}
                onClick={() => setActiveSection(item.id)}
              >
                <NavIcon>{item.icon}</NavIcon>
                {item.label}
              </NavItem>
            ))}
          </NavList>
        </Sidebar>

        <MainContent>
          <ContentHeader>
            <ContentTitle>{getSectionTitle()}</ContentTitle>
            <ContentDescription>{getSectionDescription()}</ContentDescription>
          </ContentHeader>

          {savedSuccessfully && (
            <SecurityAlert type="success">
              ✅ Settings saved successfully!
            </SecurityAlert>
          )}

          {renderSectionContent()}

          {hasUnsavedChanges && (
            <ButtonGroup>
              <ActionButton
                variant={savedSuccessfully ? 'success' : 'primary'}
                onClick={handleSave}
              >
                {savedSuccessfully ? '✅ Saved' : 'Save Changes'}
              </ActionButton>
              <ActionButton
                variant="secondary"
                onClick={() => {
                  setHasUnsavedChanges(false);
                  // Reset to original values logic here
                }}
              >
                Cancel
              </ActionButton>
            </ButtonGroup>
          )}
        </MainContent>
      </SettingsContainer>
    </ThemeProvider>
  );
};

// ==================== EXPORTS ====================
export default CreatorSettingsTemplate;

export type {
  CreatorSettingsProps,
  CreatorProfile,
  PrivacySettings,
  NotificationSettings,
  SecuritySettings,
  MonetizationSettings,
  ContentSettings
};