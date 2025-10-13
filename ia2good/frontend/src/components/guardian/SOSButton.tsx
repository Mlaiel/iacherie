import React, { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { AlertTriangle } from 'lucide-react';

interface SOSButtonProps {
  size?: 'large' | 'medium';
  onTrigger: () => void;
  onCancel?: () => void;
  countdownSeconds?: number;
}

export const SOSButton: React.FC<SOSButtonProps> = ({
  size = 'large',
  onTrigger,
  onCancel,
  countdownSeconds = 10,
}) => {
  const [isPressed, setIsPressed] = useState(false);
  const [countdown, setCountdown] = useState<number | null>(null);
  const [tapCount, setTapCount] = useState(0);
  const tapTimerRef = useRef<NodeJS.Timeout | null>(null);
  const countdownTimerRef = useRef<NodeJS.Timeout | null>(null);
  const pressTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Cleanup timers on unmount
  useEffect(() => {
    return () => {
      if (tapTimerRef.current) clearTimeout(tapTimerRef.current);
      if (countdownTimerRef.current) clearInterval(countdownTimerRef.current);
      if (pressTimerRef.current) clearTimeout(pressTimerRef.current);
    };
  }, []);

  // Handle countdown
  useEffect(() => {
    if (countdown !== null && countdown > 0) {
      countdownTimerRef.current = setTimeout(() => {
        setCountdown(countdown - 1);
      }, 1000);
    } else if (countdown === 0) {
      triggerSOS();
    }
    return () => {
      if (countdownTimerRef.current) clearTimeout(countdownTimerRef.current);
    };
  }, [countdown]);

  const triggerSOS = () => {
    // Haptic feedback - intense pattern
    if ('vibrate' in navigator) {
      navigator.vibrate([200, 100, 200, 100, 200]);
    }
    onTrigger();
    setCountdown(null);
    setIsPressed(false);
  };

  const handleTap = () => {
    // Haptic feedback - single tap
    if ('vibrate' in navigator) {
      navigator.vibrate(50);
    }

    setTapCount((prev) => prev + 1);

    // Reset tap counter after 1 second
    if (tapTimerRef.current) clearTimeout(tapTimerRef.current);
    tapTimerRef.current = setTimeout(() => {
      setTapCount(0);
    }, 1000);

    // Triple tap = instant SOS
    if (tapCount + 1 >= 3) {
      setTapCount(0);
      triggerSOS();
    }
  };

  const handlePressStart = () => {
    // Haptic feedback - press start
    if ('vibrate' in navigator) {
      navigator.vibrate(100);
    }

    setIsPressed(true);

    // Long press for 3 seconds = countdown
    pressTimerRef.current = setTimeout(() => {
      setCountdown(countdownSeconds);
    }, 3000);
  };

  const handlePressEnd = () => {
    setIsPressed(false);
    if (pressTimerRef.current) {
      clearTimeout(pressTimerRef.current);
      pressTimerRef.current = null;
    }
  };

  const handleCancelCountdown = () => {
    if ('vibrate' in navigator) {
      navigator.vibrate(50);
    }
    setCountdown(null);
    if (onCancel) onCancel();
  };

  const sizeClasses = {
    large: 'w-64 h-64 text-2xl',
    medium: 'w-32 h-32 text-xl',
  };

  if (countdown !== null) {
    return (
      <div className="flex flex-col items-center gap-4">
        <div className="relative">
          <Button
            variant="destructive"
            className={`${sizeClasses[size]} rounded-full animate-pulse shadow-2xl`}
            aria-label={`SOS countdown: ${countdown} seconds`}
          >
            <div className="flex flex-col items-center">
              <AlertTriangle className="w-16 h-16 mb-2" />
              <span className="text-6xl font-bold">{countdown}</span>
            </div>
          </Button>
          <div className="absolute inset-0 rounded-full border-8 border-red-600 animate-ping opacity-75"></div>
        </div>
        <Button
          variant="secondary"
          size="lg"
          onClick={handleCancelCountdown}
          className="text-xl px-8 py-4"
        >
          ANNULER
        </Button>
      </div>
    );
  }

  return (
    <Button
      variant="destructive"
      className={`${sizeClasses[size]} rounded-full transition-all ${
        isPressed ? 'scale-95 shadow-inner' : 'shadow-2xl hover:scale-105'
      }`}
      onClick={handleTap}
      onMouseDown={handlePressStart}
      onMouseUp={handlePressEnd}
      onMouseLeave={handlePressEnd}
      onTouchStart={handlePressStart}
      onTouchEnd={handlePressEnd}
      aria-label="SOS Emergency Button - Triple tap for instant alert, or hold for 3 seconds"
      role="button"
    >
      <div className="flex flex-col items-center">
        <AlertTriangle className={size === 'large' ? 'w-20 h-20 mb-4' : 'w-12 h-12 mb-2'} />
        <span className="font-bold">SOS</span>
        {tapCount > 0 && (
          <span className="text-sm mt-2 opacity-75">
            {3 - tapCount} taps restants
          </span>
        )}
      </div>
    </Button>
  );
};
