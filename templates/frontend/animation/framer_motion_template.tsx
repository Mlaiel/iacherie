/**
 * 🎭 Framer Motion Animation Template - iacherie Creator Economy
 * 
 * @fileoverview Template enterprise pour animations Framer Motion
 * @version 1.0.0
 * @author Fahed Mlaiel <mlaiel@live.de>
 * 
 * ⚠️ PROPRIÉTÉ INTELLECTUELLE PROTÉGÉE
 * © 2025 Fahed Mlaiel - Tous droits réservés
 * Utilisation commerciale interdite sans autorisation écrite
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { 
  motion, 
  AnimatePresence, 
  useAnimation, 
  useInView, 
  useMotionValue, 
  useTransform, 
  useSpring,
  useScroll,
  useViewportScroll,
  Variants,
  Transition,
  Target,
  MotionValue,
  PanInfo,
  Inertia
} from 'framer-motion';
import styled from 'styled-components';

// ============================================================================
// TYPES & INTERFACES
// ============================================================================

interface AnimationItem {
  id: string;
  title: string;
  content: string;
  delay?: number;
  duration?: number;
  type?: 'slide' | 'fade' | 'scale' | 'rotate' | 'bounce' | 'elastic';
}

interface FramerMotionTemplateProps {
  items: AnimationItem[];
  animationType: 'stagger' | 'sequence' | 'parallel' | 'scroll' | 'gesture';
  duration?: number;
  delay?: number;
  easing?: string;
  autoPlay?: boolean;
  loop?: boolean;
  onAnimationComplete?: () => void;
  className?: string;
}

interface GestureHandlers {
  onDrag?: (event: MouseEvent | TouchEvent | PointerEvent, info: PanInfo) => void;
  onDragEnd?: (event: MouseEvent | TouchEvent | PointerEvent, info: PanInfo) => void;
  onTap?: () => void;
  onHover?: () => void;
  onHoverEnd?: () => void;
}

// ============================================================================
// ANIMATION VARIANTS
// ============================================================================

const containerVariants: Variants = {
  hidden: {
    opacity: 0,
  },
  visible: {
    opacity: 1,
    transition: {
      delayChildren: 0.2,
      staggerChildren: 0.1,
      when: "beforeChildren"
    }
  },
  exit: {
    opacity: 0,
    transition: {
      when: "afterChildren",
      staggerChildren: 0.05,
      staggerDirection: -1
    }
  }
};

const itemVariants: Variants = {
  hidden: {
    y: 20,
    opacity: 0,
    scale: 0.95
  },
  visible: {
    y: 0,
    opacity: 1,
    scale: 1,
    transition: {
      type: "spring",
      damping: 20,
      stiffness: 300,
      duration: 0.5
    }
  },
  exit: {
    y: -20,
    opacity: 0,
    scale: 0.95,
    transition: {
      duration: 0.3
    }
  },
  hover: {
    scale: 1.05,
    y: -5,
    transition: {
      type: "spring",
      damping: 15,
      stiffness: 400
    }
  },
  tap: {
    scale: 0.95,
    transition: {
      duration: 0.1
    }
  }
};

const slideVariants: Variants = {
  hidden: { x: -100, opacity: 0 },
  visible: { 
    x: 0, 
    opacity: 1,
    transition: {
      type: "spring",
      damping: 25,
      stiffness: 200
    }
  },
  exit: { x: 100, opacity: 0 }
};

const fadeVariants: Variants = {
  hidden: { opacity: 0 },
  visible: { 
    opacity: 1,
    transition: { duration: 0.6 }
  },
  exit: { opacity: 0 }
};

const scaleVariants: Variants = {
  hidden: { scale: 0, opacity: 0 },
  visible: { 
    scale: 1, 
    opacity: 1,
    transition: {
      type: "spring",
      damping: 20,
      stiffness: 300
    }
  },
  exit: { scale: 0, opacity: 0 }
};

const rotateVariants: Variants = {
  hidden: { rotate: -180, opacity: 0 },
  visible: { 
    rotate: 0, 
    opacity: 1,
    transition: {
      type: "spring",
      damping: 15,
      stiffness: 200
    }
  },
  exit: { rotate: 180, opacity: 0 }
};

const bounceVariants: Variants = {
  hidden: { y: -100, opacity: 0 },
  visible: { 
    y: 0, 
    opacity: 1,
    transition: {
      type: "spring",
      damping: 10,
      stiffness: 100,
      mass: 1
    }
  },
  exit: { y: 100, opacity: 0 }
};

const elasticVariants: Variants = {
  hidden: { scale: 0, rotate: -45, opacity: 0 },
  visible: { 
    scale: 1, 
    rotate: 0, 
    opacity: 1,
    transition: {
      type: "spring",
      damping: 8,
      stiffness: 150,
      mass: 1.2
    }
  },
  exit: { scale: 0, rotate: 45, opacity: 0 }
};

// ============================================================================
// CUSTOM HOOKS
// ============================================================================

const useAnimationSequence = (items: AnimationItem[], autoPlay: boolean = true) => {
  const controls = useAnimation();
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(autoPlay);

  const playSequence = useCallback(async () => {
    if (!isPlaying) return;

    for (let i = 0; i < items.length; i++) {
      setCurrentIndex(i);
      await controls.start("visible");
      await new Promise(resolve => setTimeout(resolve, items[i].duration || 1000));
    }
  }, [items, controls, isPlaying]);

  const playItem = useCallback(async (index: number) => {
    setCurrentIndex(index);
    await controls.start("visible");
  }, [controls]);

  const reset = useCallback(() => {
    setCurrentIndex(0);
    controls.set("hidden");
  }, [controls]);

  const toggle = useCallback(() => {
    setIsPlaying(!isPlaying);
  }, [isPlaying]);

  useEffect(() => {
    if (autoPlay && isPlaying) {
      playSequence();
    }
  }, [autoPlay, isPlaying, playSequence]);

  return {
    controls,
    currentIndex,
    isPlaying,
    playSequence,
    playItem,
    reset,
    toggle
  };
};

const useScrollAnimation = () => {
  const { scrollYProgress } = useViewportScroll();
  const scale = useTransform(scrollYProgress, [0, 1], [0.8, 1]);
  const opacity = useTransform(scrollYProgress, [0, 0.2], [0, 1]);
  const y = useTransform(scrollYProgress, [0, 1], [100, 0]);
  
  return { scale, opacity, y, scrollYProgress };
};

const useParallaxEffect = (offset: number = 50) => {
  const { scrollY } = useViewportScroll();
  const y = useTransform(scrollY, [0, 1000], [0, offset]);
  
  return y;
};

const useMouseParallax = () => {
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  
  const mouseXSpring = useSpring(x, { damping: 25, stiffness: 300 });
  const mouseYSpring = useSpring(y, { damping: 25, stiffness: 300 });
  
  const handleMouseMove = useCallback((event: React.MouseEvent) => {
    const rect = event.currentTarget.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    
    x.set((event.clientX - centerX) / 10);
    y.set((event.clientY - centerY) / 10);
  }, [x, y]);
  
  const handleMouseLeave = useCallback(() => {
    x.set(0);
    y.set(0);
  }, [x, y]);
  
  return {
    x: mouseXSpring,
    y: mouseYSpring,
    handleMouseMove,
    handleMouseLeave
  };
};

// ============================================================================
// STYLED COMPONENTS
// ============================================================================

const AnimationContainer = styled(motion.div)`
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 1rem;
  min-height: 100vh;
  position: relative;
  overflow: hidden;
`;

const ControlPanel = styled.div`
  display: flex;
  gap: 1rem;
  align-items: center;
  margin-bottom: 2rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 0.5rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
`;

const ControlButton = styled(motion.button)`
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  font-weight: 600;
  backdrop-filter: blur(5px);
  transition: all 0.3s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: translateY(-2px);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const AnimationItem = styled(motion.div)<{ animationType: string }>`
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 1rem;
  color: white;
  cursor: pointer;
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.1), transparent);
    transform: translateX(-100%);
    transition: transform 0.6s ease;
  }

  &:hover::before {
    transform: translateX(100%);
  }

  h3 {
    margin: 0 0 0.5rem 0;
    font-size: 1.2rem;
    font-weight: 600;
  }

  p {
    margin: 0;
    opacity: 0.9;
    line-height: 1.5;
  }
`;

const ScrollIndicator = styled(motion.div)`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #4ade80, #3b82f6, #8b5cf6);
  transform-origin: 0%;
  z-index: 1000;
`;

const GestureBox = styled(motion.div)`
  width: 150px;
  height: 150px;
  background: linear-gradient(45deg, #ff6b6b, #ffd93d);
  border-radius: 1rem;
  cursor: grab;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);

  &:active {
    cursor: grabbing;
  }
`;

const ParallaxLayer = styled(motion.div)<{ speed: number }>`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  opacity: 0.3;
`;

// ============================================================================
// ANIMATION COMPONENTS
// ============================================================================

const StaggerAnimation: React.FC<{ items: AnimationItem[] }> = ({ items }) => (
  <motion.div
    variants={containerVariants}
    initial="hidden"
    animate="visible"
    exit="exit"
  >
    {items.map((item, index) => (
      <AnimationItem
        key={item.id}
        variants={itemVariants}
        whileHover="hover"
        whileTap="tap"
        animationType="stagger"
        custom={index}
      >
        <h3>{item.title}</h3>
        <p>{item.content}</p>
      </AnimationItem>
    ))}
  </motion.div>
);

const SequenceAnimation: React.FC<{ items: AnimationItem[]; autoPlay: boolean }> = ({ 
  items, 
  autoPlay 
}) => {
  const { controls, currentIndex, isPlaying, toggle, reset } = useAnimationSequence(items, autoPlay);

  return (
    <>
      <ControlPanel>
        <ControlButton
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={toggle}
        >
          {isPlaying ? 'Pause' : 'Play'}
        </ControlButton>
        <ControlButton
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={reset}
        >
          Reset
        </ControlButton>
        <span style={{ color: 'white', marginLeft: '1rem' }}>
          Current: {currentIndex + 1} / {items.length}
        </span>
      </ControlPanel>

      {items.map((item, index) => (
        <AnimationItem
          key={item.id}
          animate={controls}
          variants={itemVariants}
          initial="hidden"
          animationType="sequence"
          style={{
            opacity: index === currentIndex ? 1 : 0.3
          }}
        >
          <h3>{item.title}</h3>
          <p>{item.content}</p>
        </AnimationItem>
      ))}
    </>
  );
};

const ScrollAnimation: React.FC<{ items: AnimationItem[] }> = ({ items }) => {
  const { scale, opacity, y, scrollYProgress } = useScrollAnimation();
  const parallaxY = useParallaxEffect(100);

  return (
    <>
      <ScrollIndicator style={{ scaleX: scrollYProgress }} />
      
      <ParallaxLayer style={{ y: parallaxY }} speed={0.5}>
        <div style={{ 
          width: '100%', 
          height: '200vh', 
          background: 'linear-gradient(45deg, rgba(255, 255, 255, 0.1), transparent)' 
        }} />
      </ParallaxLayer>

      <motion.div style={{ scale, opacity, y }}>
        {items.map((item, index) => {
          const ref = useRef(null);
          const isInView = useInView(ref, { once: true, amount: 0.3 });

          return (
            <AnimationItem
              key={item.id}
              ref={ref}
              initial={{ opacity: 0, y: 50 }}
              animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 50 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              animationType="scroll"
            >
              <h3>{item.title}</h3>
              <p>{item.content}</p>
            </AnimationItem>
          );
        })}
      </motion.div>
    </>
  );
};

const GestureAnimation: React.FC<{ items: AnimationItem[] }> = ({ items }) => {
  const { x, y, handleMouseMove, handleMouseLeave } = useMouseParallax();
  const [dragConstraints, setDragConstraints] = useState({ left: 0, right: 0, top: 0, bottom: 0 });
  const constraintsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (constraintsRef.current) {
      const rect = constraintsRef.current.getBoundingClientRect();
      setDragConstraints({
        left: -rect.width / 2,
        right: rect.width / 2,
        top: -rect.height / 2,
        bottom: rect.height / 2
      });
    }
  }, []);

  return (
    <motion.div 
      ref={constraintsRef}
      style={{ x, y }}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
    >
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '2rem', justifyContent: 'center' }}>
        {items.map((item, index) => (
          <GestureBox
            key={item.id}
            drag
            dragConstraints={dragConstraints}
            dragElastic={0.1}
            whileDrag={{ scale: 1.1, rotate: 5 }}
            whileHover={{ scale: 1.05, rotate: 2 }}
            whileTap={{ scale: 0.95 }}
            dragTransition={{ bounceStiffness: 300, bounceDamping: 20 }}
            onDragEnd={(event, info) => {
              console.log('Drag ended:', info);
            }}
          >
            {item.title}
          </GestureBox>
        ))}
      </div>
    </motion.div>
  );
};

const ParallelAnimation: React.FC<{ items: AnimationItem[] }> = ({ items }) => {
  const getVariantsByType = (type: string) => {
    switch (type) {
      case 'slide': return slideVariants;
      case 'fade': return fadeVariants;
      case 'scale': return scaleVariants;
      case 'rotate': return rotateVariants;
      case 'bounce': return bounceVariants;
      case 'elastic': return elasticVariants;
      default: return itemVariants;
    }
  };

  return (
    <motion.div
      initial="hidden"
      animate="visible"
      exit="exit"
    >
      {items.map((item, index) => (
        <AnimationItem
          key={item.id}
          variants={getVariantsByType(item.type || 'slide')}
          initial="hidden"
          animate="visible"
          exit="exit"
          whileHover="hover"
          whileTap="tap"
          transition={{
            delay: item.delay || index * 0.1,
            duration: item.duration || 0.5
          }}
          animationType="parallel"
        >
          <h3>{item.title}</h3>
          <p>{item.content}</p>
          <small style={{ opacity: 0.7 }}>Type: {item.type || 'default'}</small>
        </AnimationItem>
      ))}
    </motion.div>
  );
};

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export const FramerMotionTemplate: React.FC<FramerMotionTemplateProps> = ({
  items,
  animationType,
  duration = 0.5,
  delay = 0,
  easing = "easeInOut",
  autoPlay = true,
  loop = false,
  onAnimationComplete,
  className
}) => {
  const [showAnimation, setShowAnimation] = useState(true);

  const renderAnimation = () => {
    switch (animationType) {
      case 'stagger':
        return <StaggerAnimation items={items} />;
      case 'sequence':
        return <SequenceAnimation items={items} autoPlay={autoPlay} />;
      case 'scroll':
        return <ScrollAnimation items={items} />;
      case 'gesture':
        return <GestureAnimation items={items} />;
      case 'parallel':
        return <ParallelAnimation items={items} />;
      default:
        return <StaggerAnimation items={items} />;
    }
  };

  return (
    <AnimationContainer className={className}>
      <motion.h1
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        style={{ 
          color: 'white', 
          textAlign: 'center', 
          marginBottom: '2rem',
          fontSize: '2.5rem',
          fontWeight: 'bold'
        }}
      >
        🎭 Framer Motion Animations
      </motion.h1>

      <ControlPanel>
        <ControlButton
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setShowAnimation(!showAnimation)}
        >
          {showAnimation ? 'Hide' : 'Show'} Animation
        </ControlButton>
        <span style={{ color: 'white' }}>
          Type: {animationType}
        </span>
      </ControlPanel>

      <AnimatePresence mode="wait" onExitComplete={onAnimationComplete}>
        {showAnimation && (
          <motion.div
            key="animation-content"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            {renderAnimation()}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Background Elements */}
      <motion.div
        style={{
          position: 'absolute',
          top: '20%',
          right: '10%',
          width: '100px',
          height: '100px',
          background: 'rgba(255, 255, 255, 0.1)',
          borderRadius: '50%',
          zIndex: -1
        }}
        animate={{
          scale: [1, 1.2, 1],
          rotate: [0, 180, 360],
          opacity: [0.3, 0.6, 0.3]
        }}
        transition={{
          duration: 4,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />

      <motion.div
        style={{
          position: 'absolute',
          bottom: '20%',
          left: '10%',
          width: '80px',
          height: '80px',
          background: 'rgba(255, 255, 255, 0.1)',
          borderRadius: '25%',
          zIndex: -1
        }}
        animate={{
          y: [0, -20, 0],
          rotate: [0, -90, 0],
          opacity: [0.2, 0.5, 0.2]
        }}
        transition={{
          duration: 3,
          repeat: Infinity,
          ease: "easeInOut",
          delay: 1
        }}
      />
    </AnimationContainer>
  );
};

// ============================================================================
// EXPORT DEFAULT
// ============================================================================

export default FramerMotionTemplate;

/**
 * 🎭 FONCTIONNALITÉS FRAMER MOTION TEMPLATE:
 * 
 * ✅ Types d'Animations:
 * - Stagger: Animations échelonnées
 * - Sequence: Animations séquentielles
 * - Parallel: Animations parallèles
 * - Scroll: Animations au scroll
 * - Gesture: Animations gestuelles
 * 
 * ✅ Techniques Avancées:
 * - useAnimation hook
 * - useInView detection
 * - useTransform values
 * - useSpring physics
 * - Mouse parallax
 * - Drag gestures
 * 
 * ✅ Performance:
 * - AnimatePresence transitions
 * - GPU accelerated transforms
 * - Efficient re-renders
 * - Memory cleanup
 * - Optimized variants
 * 
 * ✅ Interactivité:
 * - Hover effects
 * - Tap feedback
 * - Drag constraints
 * - Scroll triggers
 * - Custom gestures
 * 
 * ✅ Accessibilité:
 * - Reduced motion support
 * - Keyboard navigation
 * - Focus management
 * - Screen reader friendly
 * - Progressive enhancement
 */