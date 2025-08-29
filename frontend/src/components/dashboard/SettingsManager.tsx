/**
 * Settings Manager - Platform settings and user preferences
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import React from 'react';
import { 
  CogIcon, 
  UserIcon,
  BellIcon,
  ShieldCheckIcon,
  GlobeAltIcon,
  KeyIcon,
  DevicePhoneMobileIcon,
  ComputerDesktopIcon,
  EnvelopeIcon
} from '@heroicons/react/24/outline';

interface UserProfile {
  name: string;
  email: string;
  avatar?: string;
  plan: 'free' | 'pro' | 'enterprise';
  joinDate: string;
}

interface NotificationSettings {
  email: boolean;
  push: boolean;
  sms: boolean;
  violations: boolean;
  revenue: boolean;
  uploads: boolean;
}

interface SecuritySettings {
  twoFactorEnabled: boolean;
  loginNotifications: boolean;
  deviceTracking: boolean;
  sessionTimeout: number;
}

const SettingsManager: React.FC = () => {
  const [activeTab, setActiveTab] = React.useState('profile');
  const [profile, setProfile] = React.useState<UserProfile>({
    name: 'John Doe',
    email: 'john@example.com',
    plan: 'pro',
    joinDate: '2023-06-15'
  });
  const [notifications, setNotifications] = React.useState<NotificationSettings>({
    email: true,
    push: true,
    sms: false,
    violations: true,
    revenue: true,
    uploads: false
  });
  const [security, setSecurity] = React.useState<SecuritySettings>({
    twoFactorEnabled: true,
    loginNotifications: true,
    deviceTracking: true,
    sessionTimeout: 30
  });
  const [loading, setLoading] = React.useState(false);

  const tabs = [
    { id: 'profile', name: 'Profile', icon: UserIcon },
    { id: 'notifications', name: 'Notifications', icon: BellIcon },
    { id: 'security', name: 'Security', icon: ShieldCheckIcon },
    { id: 'preferences', name: 'Preferences', icon: CogIcon },
    { id: 'api', name: 'API Keys', icon: KeyIcon }
  ];

  const handleSave = async () => {
    setLoading(true);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    setLoading(false);
    // Show success message
  };

  const handleNotificationChange = (key: keyof NotificationSettings) => {
    setNotifications(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const handleSecurityChange = (key: keyof SecuritySettings, value: boolean | number) => {
    setSecurity(prev => ({ ...prev, [key]: value }));
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Settings Manager</h1>
        <p className="text-gray-600">Manage your account settings and preferences</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Settings Navigation */}
        <div className="lg:col-span-1">
          <nav className="bg-white rounded-lg shadow-md p-4">
            <ul className="space-y-1">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <li key={tab.id}>
                    <button
                      onClick={() => setActiveTab(tab.id)}
                      className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                        activeTab === tab.id
                          ? 'bg-blue-100 text-blue-700'
                          : 'text-gray-700 hover:bg-gray-100'
                      }`}
                    >
                      <Icon className="h-5 w-5 mr-3" />
                      {tab.name}
                    </button>
                  </li>
                );
              })}
            </ul>
          </nav>
        </div>

        {/* Settings Content */}
        <div className="lg:col-span-3 bg-white rounded-lg shadow-md p-6">
          {activeTab === 'profile' && (
            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Profile Settings</h2>
              
              <div className="space-y-6">
                {/* Avatar Section */}
                <div className="flex items-center space-x-6">
                  <div className="w-20 h-20 bg-gradient-to-r from-blue-400 to-purple-400 rounded-full flex items-center justify-center text-white text-2xl font-bold">
                    {profile.name.split(' ').map(n => n[0]).join('')}
                  </div>
                  <div>
                    <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors text-sm">
                      Change Avatar
                    </button>
                    <p className="text-sm text-gray-500 mt-1">JPG, PNG or GIF. Max size 2MB.</p>
                  </div>
                </div>

                {/* Basic Info */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
                    <input 
                      type="text" 
                      value={profile.name}
                      onChange={(e) => setProfile(prev => ({ ...prev, name: e.target.value }))}
                      className="w-full border border-gray-300 rounded-md px-3 py-2"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
                    <input 
                      type="email" 
                      value={profile.email}
                      onChange={(e) => setProfile(prev => ({ ...prev, email: e.target.value }))}
                      className="w-full border border-gray-300 rounded-md px-3 py-2"
                    />
                  </div>
                </div>

                {/* Plan Info */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="font-medium text-gray-900 mb-2">Current Plan</h3>
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="text-lg font-semibold capitalize text-blue-600">{profile.plan}</span>
                      <p className="text-sm text-gray-600">Member since {new Date(profile.joinDate).toLocaleDateString()}</p>
                    </div>
                    <button className="bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700 transition-colors text-sm">
                      Upgrade Plan
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'notifications' && (
            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Notification Settings</h2>
              
              <div className="space-y-6">
                {/* Notification Channels */}
                <div>
                  <h3 className="font-medium text-gray-900 mb-4">Notification Channels</h3>
                  <div className="space-y-3">
                    <label className="flex items-center justify-between">
                      <div className="flex items-center">
                        <EnvelopeIcon className="h-5 w-5 text-gray-400 mr-3" />
                        <span className="text-sm text-gray-700">Email Notifications</span>
                      </div>
                      <input 
                        type="checkbox" 
                        checked={notifications.email}
                        onChange={() => handleNotificationChange('email')}
                        className="toggle"
                      />
                    </label>
                    <label className="flex items-center justify-between">
                      <div className="flex items-center">
                        <DevicePhoneMobileIcon className="h-5 w-5 text-gray-400 mr-3" />
                        <span className="text-sm text-gray-700">Push Notifications</span>
                      </div>
                      <input 
                        type="checkbox" 
                        checked={notifications.push}
                        onChange={() => handleNotificationChange('push')}
                        className="toggle"
                      />
                    </label>
                    <label className="flex items-center justify-between">
                      <div className="flex items-center">
                        <DevicePhoneMobileIcon className="h-5 w-5 text-gray-400 mr-3" />
                        <span className="text-sm text-gray-700">SMS Notifications</span>
                      </div>
                      <input 
                        type="checkbox" 
                        checked={notifications.sms}
                        onChange={() => handleNotificationChange('sms')}
                        className="toggle"
                      />
                    </label>
                  </div>
                </div>

                {/* Notification Types */}
                <div>
                  <h3 className="font-medium text-gray-900 mb-4">Notification Types</h3>
                  <div className="space-y-3">
                    <label className="flex items-center justify-between">
                      <div>
                        <span className="text-sm font-medium text-gray-700">Copyright Violations</span>
                        <p className="text-xs text-gray-500">Get notified when violations are detected</p>
                      </div>
                      <input 
                        type="checkbox" 
                        checked={notifications.violations}
                        onChange={() => handleNotificationChange('violations')}
                        className="toggle"
                      />
                    </label>
                    <label className="flex items-center justify-between">
                      <div>
                        <span className="text-sm font-medium text-gray-700">Revenue Updates</span>
                        <p className="text-xs text-gray-500">Monthly revenue reports and milestones</p>
                      </div>
                      <input 
                        type="checkbox" 
                        checked={notifications.revenue}
                        onChange={() => handleNotificationChange('revenue')}
                        className="toggle"
                      />
                    </label>
                    <label className="flex items-center justify-between">
                      <div>
                        <span className="text-sm font-medium text-gray-700">Upload Status</span>
                        <p className="text-xs text-gray-500">Content upload and processing updates</p>
                      </div>
                      <input 
                        type="checkbox" 
                        checked={notifications.uploads}
                        onChange={() => handleNotificationChange('uploads')}
                        className="toggle"
                      />
                    </label>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'security' && (
            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Security Settings</h2>
              
              <div className="space-y-6">
                {/* Two-Factor Authentication */}
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-medium text-gray-900">Two-Factor Authentication</h3>
                      <p className="text-sm text-gray-600">Add an extra layer of security to your account</p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-green-600 font-medium">Enabled</span>
                      <button className="text-red-600 hover:text-red-700 text-sm font-medium">
                        Disable
                      </button>
                    </div>
                  </div>
                </div>

                {/* Security Options */}
                <div className="space-y-4">
                  <label className="flex items-center justify-between">
                    <div>
                      <span className="text-sm font-medium text-gray-700">Login Notifications</span>
                      <p className="text-xs text-gray-500">Get notified of new login attempts</p>
                    </div>
                    <input 
                      type="checkbox" 
                      checked={security.loginNotifications}
                      onChange={(e) => handleSecurityChange('loginNotifications', e.target.checked)}
                      className="toggle"
                    />
                  </label>
                  
                  <label className="flex items-center justify-between">
                    <div>
                      <span className="text-sm font-medium text-gray-700">Device Tracking</span>
                      <p className="text-xs text-gray-500">Track and manage logged-in devices</p>
                    </div>
                    <input 
                      type="checkbox" 
                      checked={security.deviceTracking}
                      onChange={(e) => handleSecurityChange('deviceTracking', e.target.checked)}
                      className="toggle"
                    />
                  </label>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Session Timeout (minutes)</label>
                    <select 
                      value={security.sessionTimeout}
                      onChange={(e) => handleSecurityChange('sessionTimeout', parseInt(e.target.value))}
                      className="border border-gray-300 rounded-md px-3 py-2"
                    >
                      <option value={15}>15 minutes</option>
                      <option value={30}>30 minutes</option>
                      <option value={60}>1 hour</option>
                      <option value={120}>2 hours</option>
                    </select>
                  </div>
                </div>

                {/* Password Change */}
                <div className="border-t pt-6">
                  <h3 className="font-medium text-gray-900 mb-4">Change Password</h3>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Current Password</label>
                      <input type="password" className="w-full border border-gray-300 rounded-md px-3 py-2" />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">New Password</label>
                      <input type="password" className="w-full border border-gray-300 rounded-md px-3 py-2" />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Confirm New Password</label>
                      <input type="password" className="w-full border border-gray-300 rounded-md px-3 py-2" />
                    </div>
                    <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors">
                      Update Password
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'preferences' && (
            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Preferences</h2>
              
              <div className="space-y-6">
                {/* Language & Region */}
                <div>
                  <h3 className="font-medium text-gray-900 mb-4">Language & Region</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Language</label>
                      <select className="w-full border border-gray-300 rounded-md px-3 py-2">
                        <option>English</option>
                        <option>Spanish</option>
                        <option>French</option>
                        <option>German</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Time Zone</label>
                      <select className="w-full border border-gray-300 rounded-md px-3 py-2">
                        <option>UTC-5 (EST)</option>
                        <option>UTC-8 (PST)</option>
                        <option>UTC+0 (GMT)</option>
                        <option>UTC+1 (CET)</option>
                      </select>
                    </div>
                  </div>
                </div>

                {/* Display Preferences */}
                <div>
                  <h3 className="font-medium text-gray-900 mb-4">Display</h3>
                  <div className="space-y-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Theme</label>
                      <select className="border border-gray-300 rounded-md px-3 py-2">
                        <option>Light</option>
                        <option>Dark</option>
                        <option>Auto</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Dashboard Layout</label>
                      <select className="border border-gray-300 rounded-md px-3 py-2">
                        <option>Compact</option>
                        <option>Comfortable</option>
                        <option>Spacious</option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'api' && (
            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-6">API Keys</h2>
              
              <div className="space-y-6">
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <p className="text-sm text-yellow-800">
                    <strong>Warning:</strong> Keep your API keys secure. Do not share them publicly.
                  </p>
                </div>

                <div>
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-medium text-gray-900">Your API Keys</h3>
                    <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors text-sm">
                      Generate New Key
                    </button>
                  </div>

                  <div className="space-y-3">
                    <div className="border rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium text-gray-900">Production API Key</h4>
                          <p className="text-sm text-gray-500 font-mono">ak_prod_••••••••••••••••</p>
                          <p className="text-xs text-gray-400">Created on Jan 15, 2024</p>
                        </div>
                        <div className="flex space-x-2">
                          <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">
                            Copy
                          </button>
                          <button className="text-red-600 hover:text-red-700 text-sm font-medium">
                            Revoke
                          </button>
                        </div>
                      </div>
                    </div>

                    <div className="border rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium text-gray-900">Development API Key</h4>
                          <p className="text-sm text-gray-500 font-mono">ak_dev_••••••••••••••••</p>
                          <p className="text-xs text-gray-400">Created on Jan 10, 2024</p>
                        </div>
                        <div className="flex space-x-2">
                          <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">
                            Copy
                          </button>
                          <button className="text-red-600 hover:text-red-700 text-sm font-medium">
                            Revoke
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="font-medium text-gray-900 mb-4">API Documentation</h3>
                  <p className="text-sm text-gray-600 mb-4">
                    Learn how to integrate with our API to automate your workflow.
                  </p>
                  <button className="bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700 transition-colors text-sm">
                    View Documentation
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Save Button */}
          <div className="mt-8 pt-6 border-t">
            <button 
              onClick={handleSave}
              disabled={loading}
              className={`bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition-colors ${
                loading ? 'opacity-50 cursor-not-allowed' : ''
              }`}
            >
              {loading ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsManager;