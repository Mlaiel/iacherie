import { useState, useEffect } from 'react';

export const useScroll = () => {
  const [scrollPosition, setScrollPosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const updatePosition = () => {
      setScrollPosition({ x: window.pageXOffset, y: window.pageYOffset });
    };

    window.addEventListener('scroll', updatePosition);
    updatePosition();

    return () => window.removeEventListener('scroll', updatePosition);
  }, []);

  return scrollPosition;
};
