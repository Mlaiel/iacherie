/**
 * 🎨 REACT LAZY LOADING TEMPLATE - FRONTEND EXPERT IMPLEMENTATION
 * ===============================================================
 * 
 * Enterprise-grade React lazy loading template with:
 * - TypeScript support with strict typing
 * - Code splitting and dynamic imports
 * - Loading states and error handling
 * - Intersection Observer for lazy components
 * - Image lazy loading with optimization
 * - Route-level code splitting
 * - Progressive loading strategies
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
  Suspense, 
  lazy, 
  useState, 
  useEffect, 
  useRef, 
  useCallback,
  ReactNode,
  ComponentType,
  LazyExoticComponent,
  RefObject
} from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

interface LazyComponentProps {
  fallback?: ReactNode;
  onLoad?: () => void;
  onError?: (error: Error) => void;
  delay?: number;
  timeout?: number;
}

interface LazyImageProps {
  src: string;
  alt: string;
  placeholder?: string;
  className?: string;
  style?: React.CSSProperties;
  onLoad?: () => void;
  onError?: () => void;
  threshold?: number;
  rootMargin?: string;
  blur?: boolean;
  fade?: boolean;
}

interface IntersectionLazyProps {
  children: ReactNode;
  threshold?: number;
  rootMargin?: string;
  triggerOnce?: boolean;
  fallback?: ReactNode;
  className?: string;
}

interface LazyRouteProps {
  component: () => Promise<{ default: ComponentType<any> }>;
  loading?: ReactNode;
  error?: ReactNode;
  timeout?: number;
}

interface ProgressiveImageProps extends Omit<LazyImageProps, 'src'> {
  lowQualitySrc: string;
  highQualitySrc: string;
  sizes?: string;
  srcSet?: string;
}

// ============================================================================
// LOADING COMPONENTS
// ============================================================================

const DefaultLoadingSpinner: React.FC = () => (
  <div
    style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      padding: '2rem',
      minHeight: '200px'
    }}
  >
    <motion.div
      animate={{ rotate: 360 }}
      transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
      style={{
        width: '40px',
        height: '40px',
        border: '4px solid #f3f3f3',
        borderTop: '4px solid #3498db',
        borderRadius: '50%'
      }}
    />
  </div>
);

const SkeletonLoader: React.FC<{ 
  width?: string | number; 
  height?: string | number; 
  rows?: number;
}> = ({ 
  width = '100%', 
  height = '20px', 
  rows = 1 
}) => (
  <div style={{ width }}>
    {Array.from({ length: rows }).map((_, index) => (
      <motion.div
        key={index}
        animate={{ opacity: [0.5, 1, 0.5] }}
        transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
        style={{
          height,
          backgroundColor: '#e2e8f0',
          borderRadius: '4px',
          marginBottom: rows > 1 ? '8px' : '0'
        }}
      />
    ))}
  </div>
);

const CardSkeleton: React.FC = () => (
  <div
    style={{
      padding: '1rem',
      border: '1px solid #e2e8f0',
      borderRadius: '8px',
      backgroundColor: '#f8f9fa'
    }}
  >
    <SkeletonLoader height="120px" />
    <div style={{ marginTop: '1rem' }}>
      <SkeletonLoader height="24px" width="80%" />
      <div style={{ marginTop: '0.5rem' }}>
        <SkeletonLoader height="16px" rows={2} />
      </div>
    </div>
  </div>
);

// ============================================================================
// LAZY COMPONENT WRAPPER
// ============================================================================

export function createLazyComponent<T extends ComponentType<any>>(
  importFunction: () => Promise<{ default: T }>,
  options: LazyComponentProps = {}
): LazyExoticComponent<T> {
  const { delay = 0, timeout = 10000 } = options;

  const LazyComponent = lazy(async () => {
    // Add artificial delay if specified
    if (delay > 0) {
      await new Promise(resolve => setTimeout(resolve, delay));
    }

    // Race between import and timeout
    const importPromise = importFunction();
    const timeoutPromise = new Promise<never>((_, reject) => {
      setTimeout(() => reject(new Error('Component load timeout')), timeout);
    });

    try {
      const module = await Promise.race([importPromise, timeoutPromise]);
      options.onLoad?.();
      return module;
    } catch (error) {
      options.onError?.(error as Error);
      throw error;
    }
  });

  return LazyComponent;
}

// ============================================================================
// LAZY IMAGE COMPONENT
// ============================================================================

export const LazyImage: React.FC<LazyImageProps> = ({
  src,
  alt,
  placeholder,
  className,
  style,
  onLoad,
  onError,
  threshold = 0.1,
  rootMargin = '50px',
  blur = true,
  fade = true
}) => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [isInView, setIsInView] = useState(false);
  const [hasError, setHasError] = useState(false);
  const imgRef = useRef<HTMLImageElement>(null);

  // Intersection Observer for lazy loading
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsInView(true);
          observer.disconnect();
        }
      },
      { threshold, rootMargin }
    );

    if (imgRef.current) {
      observer.observe(imgRef.current);
    }

    return () => observer.disconnect();
  }, [threshold, rootMargin]);

  const handleLoad = () => {
    setIsLoaded(true);
    onLoad?.();
  };

  const handleError = () => {
    setHasError(true);
    onError?.();
  };

  const imageStyle: React.CSSProperties = {
    ...style,
    transition: fade ? 'opacity 0.3s ease' : undefined,
    opacity: isLoaded ? 1 : 0,
    filter: !isLoaded && blur ? 'blur(5px)' : undefined
  };

  return (
    <div className={className} style={{ position: 'relative', overflow: 'hidden' }}>
      {/* Placeholder */}
      {placeholder && !isLoaded && !hasError && (
        <img
          src={placeholder}
          alt=""
          style={{
            ...imageStyle,
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            opacity: 1,
            filter: blur ? 'blur(5px)' : undefined
          }}
        />
      )}

      {/* Main image */}
      {isInView && !hasError && (
        <img
          ref={imgRef}
          src={src}
          alt={alt}
          style={imageStyle}
          onLoad={handleLoad}
          onError={handleError}
        />
      )}

      {/* Error state */}
      {hasError && (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: '#f1f1f1',
            color: '#666',
            height: '200px',
            ...style
          }}
        >
          <span>Failed to load image</span>
        </div>
      )}

      {/* Loading state */}
      {!isLoaded && !hasError && isInView && (
        <div
          style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            zIndex: 1
          }}
        >
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
            style={{
              width: '20px',
              height: '20px',
              border: '2px solid #f3f3f3',
              borderTop: '2px solid #3498db',
              borderRadius: '50%'
            }}
          />
        </div>
      )}
    </div>
  );
};

// ============================================================================
// PROGRESSIVE IMAGE COMPONENT
// ============================================================================

export const ProgressiveImage: React.FC<ProgressiveImageProps> = ({
  lowQualitySrc,
  highQualitySrc,
  alt,
  sizes,
  srcSet,
  className,
  style,
  onLoad,
  onError,
  threshold = 0.1,
  rootMargin = '50px'
}) => {
  const [isLowQualityLoaded, setIsLowQualityLoaded] = useState(false);
  const [isHighQualityLoaded, setIsHighQualityLoaded] = useState(false);
  const [isInView, setIsInView] = useState(false);
  const imgRef = useRef<HTMLDivElement>(null);

  // Intersection Observer
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsInView(true);
          observer.disconnect();
        }
      },
      { threshold, rootMargin }
    );

    if (imgRef.current) {
      observer.observe(imgRef.current);
    }

    return () => observer.disconnect();
  }, [threshold, rootMargin]);

  return (
    <div ref={imgRef} className={className} style={{ ...style, position: 'relative' }}>
      {isInView && (
        <>
          {/* Low quality image */}
          <img
            src={lowQualitySrc}
            alt=""
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              filter: 'blur(5px)',
              opacity: isLowQualityLoaded && !isHighQualityLoaded ? 1 : 0,
              transition: 'opacity 0.3s ease'
            }}
            onLoad={() => setIsLowQualityLoaded(true)}
          />

          {/* High quality image */}
          <img
            src={highQualitySrc}
            srcSet={srcSet}
            sizes={sizes}
            alt={alt}
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              opacity: isHighQualityLoaded ? 1 : 0,
              transition: 'opacity 0.3s ease'
            }}
            onLoad={() => {
              setIsHighQualityLoaded(true);
              onLoad?.();
            }}
            onError={onError}
          />
        </>
      )}
    </div>
  );
};

// ============================================================================
// INTERSECTION LAZY COMPONENT
// ============================================================================

export const IntersectionLazy: React.FC<IntersectionLazyProps> = ({
  children,
  threshold = 0.1,
  rootMargin = '50px',
  triggerOnce = true,
  fallback,
  className
}) => {
  const [isInView, setIsInView] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsInView(true);
          if (triggerOnce) {
            observer.disconnect();
          }
        } else if (!triggerOnce) {
          setIsInView(false);
        }
      },
      { threshold, rootMargin }
    );

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => observer.disconnect();
  }, [threshold, rootMargin, triggerOnce]);

  return (
    <div ref={ref} className={className}>
      <AnimatePresence mode="wait">
        {isInView ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            {children}
          </motion.div>
        ) : (
          fallback && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              {fallback}
            </motion.div>
          )
        )}
      </AnimatePresence>
    </div>
  );
};

// ============================================================================
// LAZY ROUTE COMPONENT
// ============================================================================

export const LazyRoute: React.FC<LazyRouteProps> = ({
  component,
  loading = <DefaultLoadingSpinner />,
  error = <div>Failed to load component</div>,
  timeout = 10000
}) => {
  const [hasError, setHasError] = useState(false);

  const LazyComponent = lazy(async () => {
    try {
      const timeoutPromise = new Promise<never>((_, reject) => {
        setTimeout(() => reject(new Error('Component load timeout')), timeout);
      });

      const module = await Promise.race([component(), timeoutPromise]);
      setHasError(false);
      return module;
    } catch (err) {
      setHasError(true);
      throw err;
    }
  });

  if (hasError) {
    return <>{error}</>;
  }

  return (
    <Suspense fallback={loading}>
      <LazyComponent />
    </Suspense>
  );
};

// ============================================================================
// LAZY LIST COMPONENT
// ============================================================================

interface LazyListProps<T> {
  items: T[];
  renderItem: (item: T, index: number) => ReactNode;
  itemHeight?: number;
  containerHeight?: number;
  overscan?: number;
  threshold?: number;
  loading?: ReactNode;
}

export function LazyList<T>({
  items,
  renderItem,
  itemHeight = 100,
  containerHeight = 400,
  overscan = 5,
  threshold = 0.1,
  loading = <SkeletonLoader />
}: LazyListProps<T>) {
  const [visibleRange, setVisibleRange] = useState({ start: 0, end: 10 });
  const containerRef = useRef<HTMLDivElement>(null);
  const [loadedItems, setLoadedItems] = useState<Set<number>>(new Set());

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const handleScroll = () => {
      const scrollTop = container.scrollTop;
      const start = Math.floor(scrollTop / itemHeight);
      const visibleCount = Math.ceil(containerHeight / itemHeight);
      const end = start + visibleCount;

      setVisibleRange({
        start: Math.max(0, start - overscan),
        end: Math.min(items.length, end + overscan)
      });
    };

    container.addEventListener('scroll', handleScroll);
    handleScroll(); // Initial calculation

    return () => container.removeEventListener('scroll', handleScroll);
  }, [items.length, itemHeight, containerHeight, overscan]);

  // Intersection observer for individual items
  const observeItem = useCallback((node: HTMLDivElement | null, index: number) => {
    if (!node) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !loadedItems.has(index)) {
          setLoadedItems(prev => new Set(prev).add(index));
        }
      },
      { threshold }
    );

    observer.observe(node);

    return () => observer.disconnect();
  }, [threshold, loadedItems]);

  const totalHeight = items.length * itemHeight;

  return (
    <div
      ref={containerRef}
      style={{
        height: containerHeight,
        overflow: 'auto',
        position: 'relative'
      }}
    >
      <div style={{ height: totalHeight, position: 'relative' }}>
        {Array.from(
          { length: visibleRange.end - visibleRange.start },
          (_, i) => {
            const index = visibleRange.start + i;
            const item = items[index];
            if (!item) return null;

            return (
              <div
                key={index}
                ref={(node) => observeItem(node, index)}
                style={{
                  position: 'absolute',
                  top: index * itemHeight,
                  left: 0,
                  right: 0,
                  height: itemHeight
                }}
              >
                {loadedItems.has(index) ? renderItem(item, index) : loading}
              </div>
            );
          }
        )}
      </div>
    </div>
  );
}

// ============================================================================
// USAGE EXAMPLES
// ============================================================================

export const LazyLoadingExamples: React.FC = () => {
  // Example lazy components
  const LazyDashboard = createLazyComponent(
    () => import('./Dashboard').catch(() => ({ default: () => <div>Dashboard</div> })),
    {
      delay: 1000,
      onLoad: () => console.log('Dashboard loaded'),
      onError: (error) => console.error('Dashboard failed to load:', error)
    }
  );

  const sampleItems = Array.from({ length: 1000 }, (_, i) => ({
    id: i,
    title: `Item ${i}`,
    description: `Description for item ${i}`
  }));

  return (
    <div className="lazy-loading-examples">
      <h2>Lazy Loading Examples</h2>

      {/* Lazy Component with Suspense */}
      <section>
        <h3>Lazy Component</h3>
        <Suspense fallback={<DefaultLoadingSpinner />}>
          <LazyDashboard />
        </Suspense>
      </section>

      {/* Lazy Images */}
      <section>
        <h3>Lazy Images</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
          {Array.from({ length: 6 }).map((_, i) => (
            <LazyImage
              key={i}
              src={`https://picsum.photos/300/200?random=${i}`}
              alt={`Random image ${i}`}
              placeholder="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='200'%3E%3Crect width='100%25' height='100%25' fill='%23cccccc'/%3E%3C/svg%3E"
              style={{ width: '100%', height: '200px', objectFit: 'cover' }}
            />
          ))}
        </div>
      </section>

      {/* Progressive Images */}
      <section>
        <h3>Progressive Images</h3>
        <ProgressiveImage
          lowQualitySrc="https://picsum.photos/50/30?random=1"
          highQualitySrc="https://picsum.photos/800/600?random=1"
          alt="Progressive loading example"
          style={{ width: '100%', height: '300px' }}
        />
      </section>

      {/* Intersection Lazy */}
      <section>
        <h3>Intersection Lazy Loading</h3>
        {Array.from({ length: 5 }).map((_, i) => (
          <IntersectionLazy
            key={i}
            fallback={<CardSkeleton />}
            className="mb-4"
          >
            <div
              style={{
                padding: '2rem',
                margin: '1rem 0',
                backgroundColor: '#f8f9fa',
                borderRadius: '8px',
                border: '1px solid #e9ecef'
              }}
            >
              <h4>Lazy Loaded Content {i + 1}</h4>
              <p>This content was loaded when it came into view.</p>
            </div>
          </IntersectionLazy>
        ))}
      </section>

      {/* Lazy List */}
      <section>
        <h3>Lazy Virtual List</h3>
        <LazyList
          items={sampleItems}
          renderItem={(item) => (
            <div
              style={{
                padding: '1rem',
                borderBottom: '1px solid #eee',
                height: '100px',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center'
              }}
            >
              <h4>{item.title}</h4>
              <p>{item.description}</p>
            </div>
          )}
          itemHeight={100}
          containerHeight={400}
        />
      </section>
    </div>
  );
};

// ============================================================================
// EXPORTS
// ============================================================================

export {
  DefaultLoadingSpinner,
  SkeletonLoader,
  CardSkeleton
};

export default {
  createLazyComponent,
  LazyImage,
  ProgressiveImage,
  IntersectionLazy,
  LazyRoute,
  LazyList,
  LazyLoadingExamples
};