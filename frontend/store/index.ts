/**
 * Redux Store Configuration
 * 
 * Configures the Redux store with media and collaboration slices
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import { configureStore } from '@reduxjs/toolkit';
import mediaReducer from './media.slice';
import collaborationReducer from './collaboration.slice';

export const store = configureStore({
  reducer: {
    media: mediaReducer,
    collaboration: collaborationReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE'],
        ignoredPaths: ['media.files', 'collaboration.projects'],
      },
    }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

export default store;