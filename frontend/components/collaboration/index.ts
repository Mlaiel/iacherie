/**
 * 👥 Collaboration Components - Export Index
 * 
 * @fileoverview Centralized exports for collaboration components
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @copyright 2025 Fahed Mlaiel - Propriété Intellectuelle Exclusive
 */

export { 
  default as CollaborationProvider, 
  useCollaboration 
} from './CollaborationProvider';

export { 
  default as PresenceIndicator,
  TypingIndicator,
  CollaborationStatusBar
} from './PresenceIndicator';

export type { 
  CollaboratorPresence,
  CollaborationMessage,
  ActiveUsers 
} from './CollaborationProvider';