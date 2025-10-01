/**
 * 🌐 Vue Component Template - IA Chéries Creator Economy
 * 
 * @fileoverview Template enterprise pour composants Vue.js
 * @version 1.0.0
 * @author Fahed Mlaiel <mlaiel@live.de>
 * 
 * ⚠️ PROPRIÉTÉ INTELLECTUELLE PROTÉGÉE
 * © 2025 Fahed Mlaiel - Tous droits réservés
 * Utilisation commerciale interdite sans autorisation écrite
 */

<template>
  <div
    :class="[
      'vue-component-template',
      `vue-component-template--${variant}`,
      `vue-component-template--${size}`,
      {
        'vue-component-template--loading': loading,
        'vue-component-template--disabled': disabled,
        'vue-component-template--error': hasError
      }
    ]"
    :data-testid="testId"
    :aria-label="ariaLabel"
    :aria-describedby="hasError ? `${componentId}-error` : undefined"
    role="region"
  >
    <!-- Header avec titre et actions -->
    <header
      v-if="title || hasHeaderSlot"
      class="vue-component-template__header"
    >
      <div class="vue-component-template__title-section">
        <h2
          v-if="title"
          :id="`${componentId}-title`"
          class="vue-component-template__title"
        >
          {{ title }}
        </h2>
        
        <div
          v-if="subtitle"
          class="vue-component-template__subtitle"
        >
          {{ subtitle }}
        </div>
      </div>

      <div
        v-if="hasHeaderSlot"
        class="vue-component-template__header-actions"
      >
        <slot name="header" />
      </div>
    </header>

    <!-- Loading State -->
    <div
      v-if="loading"
      class="vue-component-template__loading"
      :aria-live="'polite'"
    >
      <div class="vue-component-template__spinner">
        <svg
          class="vue-component-template__spinner-icon"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <circle
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            stroke-width="2"
            fill="none"
            stroke-linecap="round"
            stroke-dasharray="31.416"
            stroke-dashoffset="31.416"
          />
        </svg>
      </div>
      <span class="vue-component-template__loading-text">
        {{ loadingText || 'Loading...' }}
      </span>
    </div>

    <!-- Error State -->
    <div
      v-else-if="hasError"
      :id="`${componentId}-error`"
      class="vue-component-template__error"
      role="alert"
      :aria-live="'assertive'"
    >
      <div class="vue-component-template__error-icon">
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path
            d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"
            stroke="currentColor"
            stroke-width="2"
            fill="none"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
        </svg>
      </div>
      
      <div class="vue-component-template__error-content">
        <h3 class="vue-component-template__error-title">
          {{ errorTitle || 'An error occurred' }}
        </h3>
        <p class="vue-component-template__error-message">
          {{ errorMessage || 'Please try again later.' }}
        </p>
        
        <button
          v-if="showRetryButton"
          class="vue-component-template__retry-button"
          @click="handleRetry"
          :disabled="retrying"
        >
          {{ retrying ? 'Retrying...' : 'Retry' }}
        </button>
      </div>
    </div>

    <!-- Main Content -->
    <main
      v-else
      class="vue-component-template__content"
      :tabindex="focusable ? 0 : undefined"
      @keydown="handleKeydown"
    >
      <!-- Content Slots -->
      <slot
        name="content"
        :data="componentData"
        :methods="componentMethods"
      >
        <!-- Default Content -->
        <div class="vue-component-template__default-content">
          <p>{{ content || 'Component content goes here' }}</p>
        </div>
      </slot>
    </main>

    <!-- Accessibility Live Region -->
    <div
      class="vue-component-template__live-region"
      aria-live="polite"
      aria-atomic="true"
    >
      {{ liveMessage }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, useSlots } from 'vue';
import { nanoid } from 'nanoid';

// ============================================================================
// INTERFACES & TYPES
// ============================================================================

interface ComponentItem {
  id: string;
  title?: string;
  name?: string;
  description?: string;
  metadata?: Record<string, any>;
  [key: string]: any;
}

interface ComponentData {
  items: ComponentItem[];
  selectedItems: ComponentItem[];
}

// ============================================================================
// PROPS
// ============================================================================

interface Props {
  testId?: string;
  title?: string;
  subtitle?: string;
  ariaLabel?: string;
  content?: string;
  loading?: boolean;
  disabled?: boolean;
  variant?: 'default' | 'primary' | 'secondary' | 'success' | 'warning' | 'error';
  size?: 'small' | 'medium' | 'large';
  errorTitle?: string;
  errorMessage?: string;
  showRetryButton?: boolean;
  loadingText?: string;
  focusable?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
  size: 'medium',
  showRetryButton: true,
  focusable: false
});

// ============================================================================
// EMITS
// ============================================================================

interface Emits {
  (e: 'retry'): void;
}

const emit = defineEmits<Emits>();

// ============================================================================
// COMPOSABLES & REFS
// ============================================================================

const slots = useSlots();

const componentId = ref(`vue-component-${nanoid(8)}`);
const retrying = ref(false);
const liveMessage = ref('');

// ============================================================================
// COMPUTED PROPERTIES
// ============================================================================

const hasError = computed(() => !!props.errorMessage);
const hasHeaderSlot = computed(() => !!slots.header);

const componentData = computed<ComponentData>(() => ({
  items: [],
  selectedItems: []
}));

const componentMethods = computed(() => ({
  setLiveMessage: (message: string) => {
    liveMessage.value = message;
    setTimeout(() => {
      liveMessage.value = '';
    }, 1000);
  }
}));

// ============================================================================
// METHODS
// ============================================================================

const handleRetry = async () => {
  retrying.value = true;
  liveMessage.value = 'Retrying...';
  
  try {
    emit('retry');
    await new Promise(resolve => setTimeout(resolve, 1000));
    liveMessage.value = 'Retry successful';
  } catch (error) {
    liveMessage.value = 'Retry failed';
  } finally {
    retrying.value = false;
  }
};

const handleKeydown = (event: KeyboardEvent) => {
  // Global component keyboard handling
  switch (event.key) {
    case 'Escape':
      liveMessage.value = 'Escaped';
      break;
  }
};

// ============================================================================
// LIFECYCLE
// ============================================================================

onMounted(() => {
  liveMessage.value = 'Component loaded';
});
</script>

<style scoped lang="scss">
.vue-component-template {
  --color-primary: #3b82f6;
  --color-secondary: #6b7280;
  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-error: #ef4444;
  --color-background: #ffffff;
  --color-surface: #f9fafb;
  --color-border: #e5e7eb;
  --color-text: #111827;
  --color-text-secondary: #6b7280;
  
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  
  &--small { padding: 0.5rem; font-size: 0.875rem; }
  &--medium { padding: 1rem; font-size: 1rem; }
  &--large { padding: 1.5rem; font-size: 1.125rem; }
  
  &--primary { border-color: var(--color-primary); }
  &--secondary { border-color: var(--color-secondary); }
  &--success { border-color: var(--color-success); }
  &--warning { border-color: var(--color-warning); }
  &--error { border-color: var(--color-error); }
  
  &--loading { opacity: 0.7; pointer-events: none; }
  &--disabled { opacity: 0.5; pointer-events: none; }
}

.vue-component-template__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--color-border);
}

.vue-component-template__title {
  margin: 0 0 0.25rem 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--color-text);
}

.vue-component-template__subtitle {
  color: var(--color-text-secondary);
  font-size: 0.875rem;
}

.vue-component-template__loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  text-align: center;
}

.vue-component-template__spinner-icon {
  width: 2rem;
  height: 2rem;
  color: var(--color-primary);
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.vue-component-template__error {
  display: flex;
  gap: 1rem;
  padding: 1.5rem;
  background: rgb(239 68 68 / 0.05);
  border: 1px solid rgb(239 68 68 / 0.2);
  border-radius: 0.5rem;
}

.vue-component-template__error-icon {
  flex-shrink: 0;
  width: 1.5rem;
  height: 1.5rem;
  color: var(--color-error);
}

.vue-component-template__error-title {
  margin: 0 0 0.25rem 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-error);
}

.vue-component-template__retry-button {
  padding: 0.25rem 1rem;
  background: var(--color-error);
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.3s;
  
  &:hover:not(:disabled) {
    background: rgb(220 38 38);
  }
  
  &:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }
}

.vue-component-template__content {
  outline: none;
  
  &:focus {
    box-shadow: inset 0 0 0 2px var(--color-primary);
  }
}

.vue-component-template__live-region {
  position: absolute;
  left: -10000px;
  width: 1px;
  height: 1px;
  overflow: hidden;
}

@media (prefers-color-scheme: dark) {
  .vue-component-template {
    --color-background: #1f2937;
    --color-surface: #374151;
    --color-border: #4b5563;
    --color-text: #f9fafb;
    --color-text-secondary: #d1d5db;
  }
}
</style>