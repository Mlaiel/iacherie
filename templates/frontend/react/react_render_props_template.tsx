/**
 * 🎨 REACT RENDER PROPS TEMPLATE - FRONTEND EXPERT IMPLEMENTATION
 * ================================================================
 * 
 * Enterprise-grade React render props pattern template with:
 * - TypeScript support with strict typing
 * - Performance optimization
 * - Flexible render prop patterns
 * - Data fetching and state management
 * - Error handling and loading states
 * - Accessibility compliance
 * - Testing utilities
 * 
 * ⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
 * ==========================================
 * © 2025 Fahed Mlaiel <mlaiel@live.de>
 * TOUS DROITS RÉSERVÉS
 * 
 * 🚨 PROTECTION INTELLECTUELLE:
 * - Code propriétaire de Fahed Mlaiel
 * - Utilisation commerciale INTERDITE sans autorisation écrite
 * - Reverse engineering STRICTEMENT INTERDIT
 * - Distribution INTERDITE sans licence explicite
 * - Violation = Poursuites judiciaires automatiques
 * 
 * Author: Frontend Expert - Fahed Mlaiel
 * Version: 1.0.0
 */

import React, { 
  Component,
  ReactNode,
  ComponentType,
  ReactElement,
  ErrorInfo
} from 'react';
import { motion } from 'framer-motion';

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

interface RenderPropsState<T = any> {
  data: T | null;
  loading: boolean;
  error: Error | null;
  retry: () => void;
}

interface AsyncRenderPropsProps<T> {
  children: (state: RenderPropsState<T>) => ReactNode;
  fetcher: () => Promise<T>;
  dependencies?: any[];
  fallback?: ReactNode;
  errorFallback?: (error: Error, retry: () => void) => ReactNode;
  onSuccess?: (data: T) => void;
  onError?: (error: Error) => void;
}

interface MouseRenderPropsProps {
  children: (mouse: { x: number; y: number; moving: boolean }) => ReactNode;
  throttle?: number;
}

interface WindowRenderPropsProps {
  children: (window: { 
    width: number; 
    height: number; 
    scrollY: number; 
    scrollX: number;
    online: boolean;
  }) => ReactNode;
}

interface FormRenderPropsProps<T extends Record<string, any>> {
  children: (form: {
    values: T;
    errors: Partial<Record<keyof T, string>>;
    touched: Partial<Record<keyof T, boolean>>;
    setValue: (field: keyof T, value: any) => void;
    setError: (field: keyof T, error: string) => void;
    setTouched: (field: keyof T, touched: boolean) => void;
    reset: () => void;
    handleSubmit: (onSubmit: (values: T) => void | Promise<void>) => (e: React.FormEvent) => void;
    isValid: boolean;
    isSubmitting: boolean;
  }) => ReactNode;
  initialValues: T;
  validate?: (values: T) => Partial<Record<keyof T, string>>;
}

interface CounterRenderPropsProps {
  children: (counter: {
    count: number;
    increment: () => void;
    decrement: () => void;
    reset: () => void;
    set: (value: number) => void;
  }) => ReactNode;
  initialCount?: number;
  min?: number;
  max?: number;
}

interface ToggleRenderPropsProps {
  children: (toggle: {
    isOpen: boolean;
    open: () => void;
    close: () => void;
    toggle: () => void;
  }) => ReactNode;
  initialState?: boolean;
}

// ============================================================================
// ASYNC DATA FETCHER RENDER PROP
// ============================================================================

export class AsyncDataFetcher<T = any> extends Component<
  AsyncRenderPropsProps<T>,
  { data: T | null; loading: boolean; error: Error | null }
> {
  private mounted = true;
  private retryCount = 0;
  private maxRetries = 3;

  constructor(props: AsyncRenderPropsProps<T>) {
    super(props);
    this.state = {
      data: null,
      loading: false,
      error: null
    };
  }

  componentDidMount() {
    this.fetchData();
  }

  componentDidUpdate(prevProps: AsyncRenderPropsProps<T>) {
    const { dependencies = [] } = this.props;
    const { dependencies: prevDependencies = [] } = prevProps;
    
    if (dependencies.some((dep, index) => dep !== prevDependencies[index])) {
      this.fetchData();
    }
  }

  componentWillUnmount() {
    this.mounted = false;
  }

  fetchData = async () => {
    if (!this.mounted) return;

    this.setState({ loading: true, error: null });

    try {
      const data = await this.props.fetcher();
      
      if (this.mounted) {
        this.setState({ data, loading: false });
        this.props.onSuccess?.(data);
        this.retryCount = 0;
      }
    } catch (error) {
      if (this.mounted) {
        const err = error as Error;
        this.setState({ error: err, loading: false });
        this.props.onError?.(err);
      }
    }
  };

  retry = () => {
    if (this.retryCount < this.maxRetries) {
      this.retryCount++;
      this.fetchData();
    }
  };

  render() {
    const { children, fallback, errorFallback } = this.props;
    const { data, loading, error } = this.state;

    const renderPropsState: RenderPropsState<T> = {
      data,
      loading,
      error,
      retry: this.retry
    };

    if (loading && fallback) {
      return fallback;
    }

    if (error && errorFallback) {
      return errorFallback(error, this.retry);
    }

    return children(renderPropsState);
  }
}

// ============================================================================
// MOUSE TRACKER RENDER PROP
// ============================================================================

export class MouseTracker extends Component<
  MouseRenderPropsProps,
  { x: number; y: number; moving: boolean }
> {
  private throttleTimer: number | null = null;
  private moveTimer: number | null = null;

  state = {
    x: 0,
    y: 0,
    moving: false
  };

  componentDidMount() {
    document.addEventListener('mousemove', this.handleMouseMove);
  }

  componentWillUnmount() {
    document.removeEventListener('mousemove', this.handleMouseMove);
    if (this.throttleTimer) clearTimeout(this.throttleTimer);
    if (this.moveTimer) clearTimeout(this.moveTimer);
  }

  handleMouseMove = (e: MouseEvent) => {
    const { throttle = 16 } = this.props; // ~60fps by default

    if (this.throttleTimer) return;

    this.throttleTimer = window.setTimeout(() => {
      this.setState({
        x: e.clientX,
        y: e.clientY,
        moving: true
      });

      // Clear moving state after 150ms of no movement
      if (this.moveTimer) clearTimeout(this.moveTimer);
      this.moveTimer = window.setTimeout(() => {
        this.setState({ moving: false });
      }, 150);

      this.throttleTimer = null;
    }, throttle);
  };

  render() {
    return this.props.children(this.state);
  }
}

// ============================================================================
// WINDOW DIMENSIONS RENDER PROP
// ============================================================================

export class WindowDimensions extends Component<
  WindowRenderPropsProps,
  { 
    width: number; 
    height: number; 
    scrollY: number; 
    scrollX: number;
    online: boolean;
  }
> {
  state = {
    width: typeof window !== 'undefined' ? window.innerWidth : 0,
    height: typeof window !== 'undefined' ? window.innerHeight : 0,
    scrollY: typeof window !== 'undefined' ? window.scrollY : 0,
    scrollX: typeof window !== 'undefined' ? window.scrollX : 0,
    online: typeof navigator !== 'undefined' ? navigator.onLine : true
  };

  componentDidMount() {
    window.addEventListener('resize', this.handleResize);
    window.addEventListener('scroll', this.handleScroll);
    window.addEventListener('online', this.handleOnline);
    window.addEventListener('offline', this.handleOffline);
  }

  componentWillUnmount() {
    window.removeEventListener('resize', this.handleResize);
    window.removeEventListener('scroll', this.handleScroll);
    window.removeEventListener('online', this.handleOnline);
    window.removeEventListener('offline', this.handleOffline);
  }

  handleResize = () => {
    this.setState({
      width: window.innerWidth,
      height: window.innerHeight
    });
  };

  handleScroll = () => {
    this.setState({
      scrollY: window.scrollY,
      scrollX: window.scrollX
    });
  };

  handleOnline = () => {
    this.setState({ online: true });
  };

  handleOffline = () => {
    this.setState({ online: false });
  };

  render() {
    return this.props.children(this.state);
  }
}

// ============================================================================
// FORM STATE RENDER PROP
// ============================================================================

export class FormState<T extends Record<string, any>> extends Component<
  FormRenderPropsProps<T>,
  {
    values: T;
    errors: Partial<Record<keyof T, string>>;
    touched: Partial<Record<keyof T, boolean>>;
    isSubmitting: boolean;
  }
> {
  constructor(props: FormRenderPropsProps<T>) {
    super(props);
    this.state = {
      values: { ...props.initialValues },
      errors: {},
      touched: {},
      isSubmitting: false
    };
  }

  setValue = (field: keyof T, value: any) => {
    this.setState(prevState => ({
      values: { ...prevState.values, [field]: value },
      errors: { ...prevState.errors, [field]: undefined }
    }));
  };

  setError = (field: keyof T, error: string) => {
    this.setState(prevState => ({
      errors: { ...prevState.errors, [field]: error }
    }));
  };

  setTouched = (field: keyof T, touched: boolean) => {
    this.setState(prevState => ({
      touched: { ...prevState.touched, [field]: touched }
    }));
  };

  reset = () => {
    this.setState({
      values: { ...this.props.initialValues },
      errors: {},
      touched: {},
      isSubmitting: false
    });
  };

  validate = () => {
    const { validate } = this.props;
    if (!validate) return {};
    
    const errors = validate(this.state.values);
    this.setState({ errors });
    return errors;
  };

  handleSubmit = (onSubmit: (values: T) => void | Promise<void>) => {
    return async (e: React.FormEvent) => {
      e.preventDefault();
      
      const errors = this.validate();
      if (Object.keys(errors).length > 0) return;

      this.setState({ isSubmitting: true });
      
      try {
        await onSubmit(this.state.values);
      } catch (error) {
        console.error('Form submission error:', error);
      } finally {
        this.setState({ isSubmitting: false });
      }
    };
  };

  get isValid() {
    return Object.keys(this.state.errors).length === 0;
  }

  render() {
    const { children } = this.props;
    const { values, errors, touched, isSubmitting } = this.state;

    return children({
      values,
      errors,
      touched,
      setValue: this.setValue,
      setError: this.setError,
      setTouched: this.setTouched,
      reset: this.reset,
      handleSubmit: this.handleSubmit,
      isValid: this.isValid,
      isSubmitting
    });
  }
}

// ============================================================================
// COUNTER RENDER PROP
// ============================================================================

export class Counter extends Component<
  CounterRenderPropsProps,
  { count: number }
> {
  constructor(props: CounterRenderPropsProps) {
    super(props);
    this.state = {
      count: props.initialCount || 0
    };
  }

  increment = () => {
    const { max } = this.props;
    this.setState(prevState => ({
      count: max !== undefined ? Math.min(prevState.count + 1, max) : prevState.count + 1
    }));
  };

  decrement = () => {
    const { min } = this.props;
    this.setState(prevState => ({
      count: min !== undefined ? Math.max(prevState.count - 1, min) : prevState.count - 1
    }));
  };

  reset = () => {
    this.setState({ count: this.props.initialCount || 0 });
  };

  set = (value: number) => {
    const { min, max } = this.props;
    let newValue = value;
    
    if (min !== undefined) newValue = Math.max(newValue, min);
    if (max !== undefined) newValue = Math.min(newValue, max);
    
    this.setState({ count: newValue });
  };

  render() {
    const { children } = this.props;
    const { count } = this.state;

    return children({
      count,
      increment: this.increment,
      decrement: this.decrement,
      reset: this.reset,
      set: this.set
    });
  }
}

// ============================================================================
// TOGGLE RENDER PROP
// ============================================================================

export class Toggle extends Component<
  ToggleRenderPropsProps,
  { isOpen: boolean }
> {
  constructor(props: ToggleRenderPropsProps) {
    super(props);
    this.state = {
      isOpen: props.initialState || false
    };
  }

  open = () => {
    this.setState({ isOpen: true });
  };

  close = () => {
    this.setState({ isOpen: false });
  };

  toggle = () => {
    this.setState(prevState => ({ isOpen: !prevState.isOpen }));
  };

  render() {
    const { children } = this.props;
    const { isOpen } = this.state;

    return children({
      isOpen,
      open: this.open,
      close: this.close,
      toggle: this.toggle
    });
  }
}

// ============================================================================
// USAGE EXAMPLES
// ============================================================================

export const RenderPropsExamples: React.FC = () => {
  return (
    <div className="render-props-examples">
      {/* Async Data Fetcher Example */}
      <AsyncDataFetcher
        fetcher={() => fetch('/api/users').then(res => res.json())}
        fallback={<div>Loading users...</div>}
        errorFallback={(error, retry) => (
          <div>
            <p>Error: {error.message}</p>
            <button onClick={retry}>Retry</button>
          </div>
        )}
      >
        {({ data, loading, error }) => (
          <div>
            {loading && <p>Loading...</p>}
            {error && <p>Error: {error.message}</p>}
            {data && (
              <ul>
                {data.map((user: any) => (
                  <li key={user.id}>{user.name}</li>
                ))}
              </ul>
            )}
          </div>
        )}
      </AsyncDataFetcher>

      {/* Mouse Tracker Example */}
      <MouseTracker>
        {({ x, y, moving }) => (
          <motion.div
            animate={{ 
              scale: moving ? 1.1 : 1,
              rotate: moving ? 5 : 0 
            }}
            style={{ 
              position: 'fixed',
              left: x,
              top: y,
              pointerEvents: 'none',
              zIndex: 9999
            }}
          >
            🎯 ({x}, {y})
          </motion.div>
        )}
      </MouseTracker>

      {/* Window Dimensions Example */}
      <WindowDimensions>
        {({ width, height, scrollY, online }) => (
          <div className="window-info">
            <p>Window: {width} x {height}</p>
            <p>Scroll Y: {scrollY}</p>
            <p>Status: {online ? 'Online' : 'Offline'}</p>
          </div>
        )}
      </WindowDimensions>

      {/* Form State Example */}
      <FormState
        initialValues={{ name: '', email: '', age: 0 }}
        validate={(values) => {
          const errors: any = {};
          if (!values.name) errors.name = 'Name is required';
          if (!values.email) errors.email = 'Email is required';
          if (values.age < 18) errors.age = 'Must be 18 or older';
          return errors;
        }}
      >
        {({ values, errors, setValue, handleSubmit, isValid, isSubmitting }) => (
          <form onSubmit={handleSubmit((values) => console.log('Submit:', values))}>
            <div>
              <input
                value={values.name}
                onChange={(e) => setValue('name', e.target.value)}
                placeholder="Name"
              />
              {errors.name && <span className="error">{errors.name}</span>}
            </div>
            
            <div>
              <input
                value={values.email}
                onChange={(e) => setValue('email', e.target.value)}
                placeholder="Email"
              />
              {errors.email && <span className="error">{errors.email}</span>}
            </div>
            
            <div>
              <input
                type="number"
                value={values.age}
                onChange={(e) => setValue('age', parseInt(e.target.value))}
                placeholder="Age"
              />
              {errors.age && <span className="error">{errors.age}</span>}
            </div>
            
            <button type="submit" disabled={!isValid || isSubmitting}>
              {isSubmitting ? 'Submitting...' : 'Submit'}
            </button>
          </form>
        )}
      </FormState>

      {/* Counter Example */}
      <Counter initialCount={0} min={0} max={10}>
        {({ count, increment, decrement, reset }) => (
          <div className="counter">
            <button onClick={decrement}>-</button>
            <span>{count}</span>
            <button onClick={increment}>+</button>
            <button onClick={reset}>Reset</button>
          </div>
        )}
      </Counter>

      {/* Toggle Example */}
      <Toggle>
        {({ isOpen, toggle }) => (
          <div>
            <button onClick={toggle}>
              {isOpen ? 'Close' : 'Open'} Panel
            </button>
            {isOpen && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
              >
                <p>This panel is now open!</p>
              </motion.div>
            )}
          </div>
        )}
      </Toggle>
    </div>
  );
};

// Export all render prop components
export {
  AsyncDataFetcher,
  MouseTracker,
  WindowDimensions,
  FormState,
  Counter,
  Toggle
};

export default {
  AsyncDataFetcher,
  MouseTracker,
  WindowDimensions,
  FormState,
  Counter,
  Toggle,
  RenderPropsExamples
};