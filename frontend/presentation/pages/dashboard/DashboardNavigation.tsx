'use client';

import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { 
  HomeIcon,
  ShieldCheckIcon,
  ChartBarIcon,
  UsersIcon,
  CurrencyDollarIcon,
  CloudArrowUpIcon,
  FolderIcon,
  CogIcon
} from '@heroicons/react/24/outline';
import { DASHBOARD_NAVIGATION } from '@/dashboard';

// Map icon names to actual icons
const iconMap = {
  HomeIcon,
  ShieldCheckIcon,
  ChartBarIcon,
  UsersIcon,
  CurrencyDollarIcon,
  CloudArrowUpIcon,
  FolderIcon,
  CogIcon,
} as const;

export function DashboardNavigation() {
  const pathname = usePathname();

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <div className="flex-shrink-0 flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">
                Ainflue Dashboard
              </h1>
            </div>
          </div>
          
          <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
            {DASHBOARD_NAVIGATION.map((item) => {
              const IconComponent = iconMap[item.icon as keyof typeof iconMap];
              const isActive = pathname === item.href;
              
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors duration-200 ${ 
                    isActive
                      ? 'border-primary-500 text-primary-600'
                      : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                  }`}
                  title={item.description}
                >
                  {IconComponent && (
                    <IconComponent className="mr-2 h-4 w-4" />
                  )}
                  {item.name}
                </Link>
              );
            })}
          </div>
        </div>
      </div>
    </nav>
  );
}