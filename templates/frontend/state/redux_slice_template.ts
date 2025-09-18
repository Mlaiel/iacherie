/**
 * 🔄 REDUX SLICE TEMPLATE - ENTERPRISE STATE MANAGEMENT
 * =====================================================
 * 
 * Advanced Redux Slice Templates for Ainflue Creator Economy
 * Type-safe reducers, async thunks, RTK Query integration
 * 
 * © 2025 Fahed Mlaiel <mlaiel@live.de>
 * TOUS DROITS RÉSERVÉS
 * 
 * 🚨 PROTECTION INTELLECTUELLE:
 * - Code propriétaire de Fahed Mlaiel
 * - Utilisation commerciale INTERDITE sans autorisation écrite
 * - Reverse engineering STRICTEMENT INTERDIT
 * - Distribution INTERDITE sans licence explicite
 * - Violation = Poursuites judiciaires automatiques
 */

import { createSlice, createAsyncThunk, PayloadAction, createSelector } from '@reduxjs/toolkit';
import { persistReducer } from 'redux-persist';
import storage from 'redux-persist/lib/storage';

// Base State Interfaces
export interface BaseEntity {
  id: string;
  createdAt: string;
  updatedAt: string;
}

export interface EntityState<T extends BaseEntity> {
  entities: Record<string, T>;
  ids: string[];
  loading: boolean;
  error: string | null;
  lastFetch: number | null;
  totalCount: number;
  hasMore: boolean;
}

export interface PaginationParams {
  page: number;
  pageSize: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
  filters?: Record<string, any>;
}

export interface ApiResponse<T> {
  data: T;
  meta: {
    page: number;
    pageSize: number;
    total: number;
    hasMore: boolean;
  };
}

// Creator State Interface (Example)
export interface Creator extends BaseEntity {
  username: string;
  displayName: string;
  avatar: string;
  bio: string;
  followerCount: number;
  followingCount: number;
  contentCount: number;
  verified: boolean;
  tier: 'free' | 'premium' | 'pro' | 'enterprise';
  settings: {
    privacy: 'public' | 'private' | 'friends';
    notifications: boolean;
    analytics: boolean;
  };
  stats: {
    views: number;
    likes: number;
    shares: number;
    revenue: number;
  };
}

export interface CreatorState extends EntityState<Creator> {
  currentCreator: Creator | null;
  recommendations: string[];
  trending: string[];
  filters: {
    tier?: string;
    verified?: boolean;
    category?: string;
  };
}

// Async Thunks Factory
export const createEntityThunks = <T extends BaseEntity>(
  entityName: string,
  apiEndpoint: string
) => {
  // Fetch entities with pagination
  const fetchEntities = createAsyncThunk(
    `${entityName}/fetchEntities`,
    async (params: PaginationParams, { rejectWithValue }) => {
      try {
        const queryParams = new URLSearchParams({
          page: params.page.toString(),
          pageSize: params.pageSize.toString(),
          ...(params.sortBy && { sortBy: params.sortBy }),
          ...(params.sortOrder && { sortOrder: params.sortOrder }),
          ...(params.filters && { filters: JSON.stringify(params.filters) }),
        });

        const response = await fetch(`${apiEndpoint}?${queryParams}`);
        
        if (!response.ok) {
          throw new Error(`Failed to fetch ${entityName}s`);
        }
        
        const data: ApiResponse<T[]> = await response.json();
        return data;
      } catch (error) {
        return rejectWithValue(error instanceof Error ? error.message : 'Unknown error');
      }
    }
  );

  // Fetch single entity
  const fetchEntity = createAsyncThunk(
    `${entityName}/fetchEntity`,
    async (id: string, { rejectWithValue }) => {
      try {
        const response = await fetch(`${apiEndpoint}/${id}`);
        
        if (!response.ok) {
          throw new Error(`Failed to fetch ${entityName}`);
        }
        
        const data: T = await response.json();
        return data;
      } catch (error) {
        return rejectWithValue(error instanceof Error ? error.message : 'Unknown error');
      }
    }
  );

  // Create entity
  const createEntity = createAsyncThunk(
    `${entityName}/createEntity`,
    async (entityData: Omit<T, keyof BaseEntity>, { rejectWithValue }) => {
      try {
        const response = await fetch(apiEndpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(entityData),
        });
        
        if (!response.ok) {
          throw new Error(`Failed to create ${entityName}`);
        }
        
        const data: T = await response.json();
        return data;
      } catch (error) {
        return rejectWithValue(error instanceof Error ? error.message : 'Unknown error');
      }
    }
  );

  // Update entity
  const updateEntity = createAsyncThunk(
    `${entityName}/updateEntity`,
    async ({ id, updates }: { id: string; updates: Partial<T> }, { rejectWithValue }) => {
      try {
        const response = await fetch(`${apiEndpoint}/${id}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(updates),
        });
        
        if (!response.ok) {
          throw new Error(`Failed to update ${entityName}`);
        }
        
        const data: T = await response.json();
        return data;
      } catch (error) {
        return rejectWithValue(error instanceof Error ? error.message : 'Unknown error');
      }
    }
  );

  // Delete entity
  const deleteEntity = createAsyncThunk(
    `${entityName}/deleteEntity`,
    async (id: string, { rejectWithValue }) => {
      try {
        const response = await fetch(`${apiEndpoint}/${id}`, {
          method: 'DELETE',
        });
        
        if (!response.ok) {
          throw new Error(`Failed to delete ${entityName}`);
        }
        
        return id;
      } catch (error) {
        return rejectWithValue(error instanceof Error ? error.message : 'Unknown error');
      }
    }
  );

  return {
    fetchEntities,
    fetchEntity,
    createEntity,
    updateEntity,
    deleteEntity,
  };
};

// Generic Entity Slice Factory
export const createEntitySlice = <T extends BaseEntity>(
  name: string,
  initialState: EntityState<T>,
  extraReducers?: (builder: any) => void
) => {
  const thunks = createEntityThunks<T>(name, `/api/${name}s`);

  const slice = createSlice({
    name,
    initialState,
    reducers: {
      // Optimistic updates
      addEntityOptimistic: (state, action: PayloadAction<T>) => {
        const entity = action.payload;
        state.entities[entity.id] = entity;
        if (!state.ids.includes(entity.id)) {
          state.ids.push(entity.id);
        }
      },
      
      updateEntityOptimistic: (state, action: PayloadAction<{ id: string; updates: Partial<T> }>) => {
        const { id, updates } = action.payload;
        if (state.entities[id]) {
          state.entities[id] = { ...state.entities[id], ...updates };
        }
      },
      
      removeEntityOptimistic: (state, action: PayloadAction<string>) => {
        const id = action.payload;
        delete state.entities[id];
        state.ids = state.ids.filter(entityId => entityId !== id);
      },
      
      // Clear state
      clearEntities: (state) => {
        state.entities = {};
        state.ids = [];
        state.error = null;
        state.lastFetch = null;
      },
      
      // Set error
      setError: (state, action: PayloadAction<string>) => {
        state.error = action.payload;
        state.loading = false;
      },
      
      // Clear error
      clearError: (state) => {
        state.error = null;
      },
    },
    extraReducers: (builder) => {
      // Fetch entities
      builder
        .addCase(thunks.fetchEntities.pending, (state) => {
          state.loading = true;
          state.error = null;
        })
        .addCase(thunks.fetchEntities.fulfilled, (state, action) => {
          state.loading = false;
          state.lastFetch = Date.now();
          
          const { data, meta } = action.payload;
          data.forEach(entity => {
            state.entities[entity.id] = entity;
            if (!state.ids.includes(entity.id)) {
              state.ids.push(entity.id);
            }
          });
          
          state.totalCount = meta.total;
          state.hasMore = meta.hasMore;
        })
        .addCase(thunks.fetchEntities.rejected, (state, action) => {
          state.loading = false;
          state.error = action.payload as string;
        });

      // Fetch single entity
      builder
        .addCase(thunks.fetchEntity.pending, (state) => {
          state.loading = true;
          state.error = null;
        })
        .addCase(thunks.fetchEntity.fulfilled, (state, action) => {
          state.loading = false;
          const entity = action.payload;
          state.entities[entity.id] = entity;
          if (!state.ids.includes(entity.id)) {
            state.ids.push(entity.id);
          }
        })
        .addCase(thunks.fetchEntity.rejected, (state, action) => {
          state.loading = false;
          state.error = action.payload as string;
        });

      // Create entity
      builder
        .addCase(thunks.createEntity.pending, (state) => {
          state.loading = true;
          state.error = null;
        })
        .addCase(thunks.createEntity.fulfilled, (state, action) => {
          state.loading = false;
          const entity = action.payload;
          state.entities[entity.id] = entity;
          state.ids.unshift(entity.id); // Add to beginning
          state.totalCount += 1;
        })
        .addCase(thunks.createEntity.rejected, (state, action) => {
          state.loading = false;
          state.error = action.payload as string;
        });

      // Update entity
      builder
        .addCase(thunks.updateEntity.pending, (state) => {
          state.loading = true;
          state.error = null;
        })
        .addCase(thunks.updateEntity.fulfilled, (state, action) => {
          state.loading = false;
          const entity = action.payload;
          state.entities[entity.id] = entity;
        })
        .addCase(thunks.updateEntity.rejected, (state, action) => {
          state.loading = false;
          state.error = action.payload as string;
        });

      // Delete entity
      builder
        .addCase(thunks.deleteEntity.pending, (state) => {
          state.loading = true;
          state.error = null;
        })
        .addCase(thunks.deleteEntity.fulfilled, (state, action) => {
          state.loading = false;
          const id = action.payload;
          delete state.entities[id];
          state.ids = state.ids.filter(entityId => entityId !== id);
          state.totalCount = Math.max(0, state.totalCount - 1);
        })
        .addCase(thunks.deleteEntity.rejected, (state, action) => {
          state.loading = false;
          state.error = action.payload as string;
        });

      // Apply extra reducers if provided
      if (extraReducers) {
        extraReducers(builder);
      }
    },
  });

  return { slice, thunks };
};

// Creator Slice Example
const creatorThunks = createEntityThunks<Creator>('creator', '/api/creators');

// Additional creator-specific thunks
export const followCreator = createAsyncThunk(
  'creator/followCreator',
  async (creatorId: string, { rejectWithValue }) => {
    try {
      const response = await fetch(`/api/creators/${creatorId}/follow`, {
        method: 'POST',
      });
      
      if (!response.ok) {
        throw new Error('Failed to follow creator');
      }
      
      return creatorId;
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Unknown error');
    }
  }
);

export const unfollowCreator = createAsyncThunk(
  'creator/unfollowCreator',
  async (creatorId: string, { rejectWithValue }) => {
    try {
      const response = await fetch(`/api/creators/${creatorId}/unfollow`, {
        method: 'POST',
      });
      
      if (!response.ok) {
        throw new Error('Failed to unfollow creator');
      }
      
      return creatorId;
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Unknown error');
    }
  }
);

// Initial state
const initialCreatorState: CreatorState = {
  entities: {},
  ids: [],
  loading: false,
  error: null,
  lastFetch: null,
  totalCount: 0,
  hasMore: true,
  currentCreator: null,
  recommendations: [],
  trending: [],
  filters: {},
};

// Creator slice
const { slice: creatorSlice, thunks } = createEntitySlice<Creator>(
  'creator',
  initialCreatorState,
  (builder) => {
    // Follow creator
    builder
      .addCase(followCreator.fulfilled, (state, action) => {
        const creatorId = action.payload;
        if (state.entities[creatorId]) {
          state.entities[creatorId].followerCount += 1;
        }
      });

    // Unfollow creator
    builder
      .addCase(unfollowCreator.fulfilled, (state, action) => {
        const creatorId = action.payload;
        if (state.entities[creatorId]) {
          state.entities[creatorId].followerCount = Math.max(0, state.entities[creatorId].followerCount - 1);
        }
      });
  }
);

// Add custom reducers to creator slice
const enhancedCreatorSlice = {
  ...creatorSlice,
  actions: {
    ...creatorSlice.actions,
    setCurrentCreator: (state: CreatorState, action: PayloadAction<Creator | null>) => {
      state.currentCreator = action.payload;
    },
    setRecommendations: (state: CreatorState, action: PayloadAction<string[]>) => {
      state.recommendations = action.payload;
    },
    setTrending: (state: CreatorState, action: PayloadAction<string[]>) => {
      state.trending = action.payload;
    },
    updateFilters: (state: CreatorState, action: PayloadAction<Partial<CreatorState['filters']>>) => {
      state.filters = { ...state.filters, ...action.payload };
    },
    clearFilters: (state: CreatorState) => {
      state.filters = {};
    },
  },
};

// Selectors
export const createEntitySelectors = <T extends BaseEntity>(name: string) => {
  const selectEntities = (state: any) => state[name].entities;
  const selectIds = (state: any) => state[name].ids;
  const selectLoading = (state: any) => state[name].loading;
  const selectError = (state: any) => state[name].error;
  const selectTotalCount = (state: any) => state[name].totalCount;
  const selectHasMore = (state: any) => state[name].hasMore;

  const selectAllEntities = createSelector(
    [selectEntities, selectIds],
    (entities, ids) => ids.map(id => entities[id])
  );

  const selectEntityById = createSelector(
    [selectEntities, (state: any, id: string) => id],
    (entities, id) => entities[id] || null
  );

  const selectEntitiesByIds = createSelector(
    [selectEntities, (state: any, ids: string[]) => ids],
    (entities, ids) => ids.map(id => entities[id]).filter(Boolean)
  );

  return {
    selectEntities,
    selectIds,
    selectLoading,
    selectError,
    selectTotalCount,
    selectHasMore,
    selectAllEntities,
    selectEntityById,
    selectEntitiesByIds,
  };
};

// Creator selectors
export const creatorSelectors = {
  ...createEntitySelectors<Creator>('creator'),
  selectCurrentCreator: (state: any) => state.creator.currentCreator,
  selectRecommendations: createSelector(
    [(state: any) => state.creator.entities, (state: any) => state.creator.recommendations],
    (entities, recommendations) => recommendations.map(id => entities[id]).filter(Boolean)
  ),
  selectTrending: createSelector(
    [(state: any) => state.creator.entities, (state: any) => state.creator.trending],
    (entities, trending) => trending.map(id => entities[id]).filter(Boolean)
  ),
  selectFilters: (state: any) => state.creator.filters,
  selectFilteredCreators: createSelector(
    [(state: any) => state.creator.entities, (state: any) => state.creator.ids, (state: any) => state.creator.filters],
    (entities, ids, filters) => {
      let filteredIds = ids;
      
      if (filters.tier) {
        filteredIds = filteredIds.filter(id => entities[id]?.tier === filters.tier);
      }
      
      if (filters.verified !== undefined) {
        filteredIds = filteredIds.filter(id => entities[id]?.verified === filters.verified);
      }
      
      return filteredIds.map(id => entities[id]);
    }
  ),
};

// Persistence configuration
const persistConfig = {
  key: 'creator',
  storage,
  whitelist: ['entities', 'ids', 'currentCreator', 'filters'], // Only persist these fields
  blacklist: ['loading', 'error'], // Don't persist these fields
};

// Export persisted reducer
export const persistedCreatorReducer = persistReducer(persistConfig, enhancedCreatorSlice.reducer);

// Export actions and thunks
export const creatorActions = {
  ...enhancedCreatorSlice.actions,
  ...thunks,
  followCreator,
  unfollowCreator,
};

// Export reducer
export const creatorReducer = enhancedCreatorSlice.reducer;

// Export all thunks
export const creatorThunks = {
  ...thunks,
  followCreator,
  unfollowCreator,
};

// Type exports
export type { Creator, CreatorState, EntityState, BaseEntity, PaginationParams, ApiResponse };

export default enhancedCreatorSlice;