/*
 * Owner: Fahed Mlaiel
 * Contact: mlaiel@live.de
 * Notice: Attribution to Fahed Mlaiel is mandatory in all copies, forks, and derivatives.
 */

import { CaseReport, VolunteerProfile, VolunteerActivity, Badge } from './types';

export const sampleCases: CaseReport[] = [
  {
    id: 'case-sample-1',
    type: 'homeless',
    location: { lat: 40.7128, lng: -74.0060 }, // NYC approximate
    description: 'Person needs warm blanket and food. Sitting near subway entrance, appears to have been there for several hours.',
    urgency: 'high',
    status: 'open',
    reportedAt: new Date(Date.now() - 30 * 60 * 1000).toISOString(), // 30 minutes ago
    tags: ['food', 'blanket', 'shelter']
  },
  {
    id: 'case-sample-2',
    type: 'animal',
    location: { lat: 40.7589, lng: -73.9851 }, // Central Park area
    description: 'Injured dog with what appears to be a limp. Friendly but seems scared. Needs veterinary attention.',
    urgency: 'medium',
    status: 'in-progress',
    reportedAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), // 2 hours ago
    tags: ['veterinary', 'injured', 'rescue']
  },
  {
    id: 'case-sample-3',
    type: 'homeless',
    location: { lat: 40.7505, lng: -73.9934 }, // Times Square area
    description: 'Elderly person needs assistance finding shelter for the night. Has medication but no place to store it safely.',
    urgency: 'medium',
    status: 'helped',
    reportedAt: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(), // 4 hours ago
    helpedAt: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(), // 1 hour ago
    helpedBy: 'Local Volunteer',
    tags: ['shelter', 'elderly', 'medication']
  },
  {
    id: 'case-sample-4',
    type: 'animal',
    location: { lat: 40.7282, lng: -73.7949 }, // Queens area
    description: 'Group of kittens found in abandoned building. Need food, water, and rescue. Mother cat not present.',
    urgency: 'high',
    status: 'open',
    reportedAt: new Date(Date.now() - 45 * 60 * 1000).toISOString(), // 45 minutes ago
    tags: ['kittens', 'rescue', 'abandoned', 'food']
  },
  {
    id: 'case-sample-5',
    type: 'homeless',
    location: { lat: 40.6782, lng: -73.9442 }, // Brooklyn area
    description: 'Young person with backpack needs information about local youth services and a meal.',
    urgency: 'low',
    status: 'open',
    reportedAt: new Date(Date.now() - 20 * 60 * 1000).toISOString(), // 20 minutes ago
    tags: ['youth', 'information', 'food', 'services']
  }
];

export const sampleBadges: Badge[] = [
  {
    id: 'first-help',
    name: 'First Helper',
    description: 'Helped your first person in need',
    icon: '🌟',
    earnedAt: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
    category: 'milestone'
  },
  {
    id: 'animal-friend',
    name: 'Animal Friend',
    description: 'Helped 10+ animals in need',
    icon: '🐾',
    earnedAt: new Date(Date.now() - 20 * 24 * 60 * 60 * 1000).toISOString(),
    category: 'skill'
  },
  {
    id: 'dedicated-helper',
    name: 'Dedicated Helper',
    description: 'Helped someone in need 50+ times',
    icon: '❤️',
    earnedAt: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(),
    category: 'milestone'
  },
  {
    id: 'fast-responder',
    name: 'Fast Responder',
    description: 'Average response time under 30 minutes',
    icon: '⚡',
    earnedAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
    category: 'skill'
  }
]

export const sampleVolunteerProfiles: VolunteerProfile[] = [
  {
    id: 'volunteer-1',
    name: 'Sarah Chen',
    email: 'sarah.chen@example.com',
    bio: 'Registered nurse with 8 years of experience. Passionate about helping vulnerable populations and providing medical care to those who need it most.',
    joinedAt: new Date(Date.now() - 365 * 24 * 60 * 60 * 1000).toISOString(),
    skills: ['Medical Care', 'First Aid', 'Mental Health Support', 'Crisis Intervention'],
    availableHours: {
      days: ['monday', 'tuesday', 'wednesday', 'friday', 'saturday'],
      startTime: '08:00',
      endTime: '18:00'
    },
    preferences: {
      maxDistance: 15,
      preferredCategories: ['homeless', 'animal'],
      notificationSettings: {
        enabled: true,
        radius: 15,
        categories: ['homeless', 'animal'],
        urgencyLevels: ['medium', 'high'],
        quietHours: {
          enabled: true,
          start: '22:00',
          end: '07:00'
        }
      }
    },
    verification: {
      isVerified: true,
      verifiedAt: new Date(Date.now() - 350 * 24 * 60 * 60 * 1000).toISOString(),
      verificationMethod: 'government-id'
    },
    stats: {
      totalCasesHelped: 127,
      totalReports: 45,
      totalHoursVolunteered: 340,
      peopleHelped: 89,
      animalsHelped: 38,
      activeStreakDays: 23,
      averageResponseTime: 25,
      mostActiveCategory: 'homeless',
      badges: [sampleBadges[0], sampleBadges[2], sampleBadges[3]],
      rating: 4.8,
      reviewCount: 67
    }
  },
  {
    id: 'volunteer-2',
    name: 'Marcus Rodriguez',
    email: 'marcus.r@example.com',
    bio: 'Veterinary technician who volunteers in my free time. Especially dedicated to helping stray and injured animals find safety and medical care.',
    joinedAt: new Date(Date.now() - 180 * 24 * 60 * 60 * 1000).toISOString(),
    skills: ['Veterinary Care', 'Animal Handling', 'Emergency Response', 'Spanish Translation'],
    availableHours: {
      days: ['thursday', 'friday', 'saturday', 'sunday'],
      startTime: '14:00',
      endTime: '20:00'
    },
    preferences: {
      maxDistance: 20,
      preferredCategories: ['animal'],
      notificationSettings: {
        enabled: true,
        radius: 20,
        categories: ['animal'],
        urgencyLevels: ['low', 'medium', 'high'],
        quietHours: {
          enabled: false,
          start: '23:00',
          end: '06:00'
        }
      }
    },
    verification: {
      isVerified: true,
      verifiedAt: new Date(Date.now() - 160 * 24 * 60 * 60 * 1000).toISOString(),
      verificationMethod: 'email'
    },
    stats: {
      totalCasesHelped: 84,
      totalReports: 23,
      totalHoursVolunteered: 195,
      peopleHelped: 12,
      animalsHelped: 72,
      activeStreakDays: 15,
      averageResponseTime: 18,
      mostActiveCategory: 'animal',
      badges: [sampleBadges[0], sampleBadges[1], sampleBadges[3]],
      rating: 4.9,
      reviewCount: 43
    }
  },
  {
    id: 'volunteer-3',
    name: 'Emily Johnson',
    email: 'emily.j@example.com',
    bio: 'Social worker committed to supporting homeless individuals and families. I believe everyone deserves dignity and compassion.',
    joinedAt: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString(),
    skills: ['Social Work', 'Counseling', 'Resource Navigation', 'Crisis Support'],
    availableHours: {
      days: ['monday', 'wednesday', 'friday', 'sunday'],
      startTime: '10:00',
      endTime: '16:00'
    },
    preferences: {
      maxDistance: 10,
      preferredCategories: ['homeless'],
      notificationSettings: {
        enabled: true,
        radius: 10,
        categories: ['homeless'],
        urgencyLevels: ['medium', 'high'],
        quietHours: {
          enabled: true,
          start: '21:00',
          end: '08:00'
        }
      }
    },
    verification: {
      isVerified: false,
      verificationMethod: 'phone'
    },
    stats: {
      totalCasesHelped: 42,
      totalReports: 18,
      totalHoursVolunteered: 98,
      peopleHelped: 39,
      animalsHelped: 3,
      activeStreakDays: 8,
      averageResponseTime: 35,
      mostActiveCategory: 'homeless',
      badges: [sampleBadges[0]],
      rating: 4.6,
      reviewCount: 21
    }
  }
];

// Function to add sample data for testing (dev only)
export function addSampleData(setCases: (cases: CaseReport[]) => void): void {
  if (process.env.NODE_ENV === 'development') {
    setCases(sampleCases);
  }
}