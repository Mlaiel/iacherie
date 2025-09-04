/**
 * Animation Library
 */

interface AnimationOptions {
  duration?: number;
  easing?: string;
  delay?: number;
  iterations?: number;
  direction?: 'normal' | 'reverse' | 'alternate' | 'alternate-reverse';
  fillMode?: 'none' | 'forwards' | 'backwards' | 'both';
}

class Animator {
  private element: HTMLElement;
  private animations: Animation[] = [];

  constructor(element: HTMLElement) {
    this.element = element;
  }

  fadeIn(options: AnimationOptions = {}): Promise<void> {
    return this.animate([
      { opacity: 0 },
      { opacity: 1 }
    ], {
      duration: 300,
      ...options
    });
  }

  fadeOut(options: AnimationOptions = {}): Promise<void> {
    return this.animate([
      { opacity: 1 },
      { opacity: 0 }
    ], {
      duration: 300,
      ...options
    });
  }

  slideIn(direction: 'left' | 'right' | 'up' | 'down' = 'left', options: AnimationOptions = {}): Promise<void> {
    const transforms = {
      left: ['translateX(-100%)', 'translateX(0)'],
      right: ['translateX(100%)', 'translateX(0)'],
      up: ['translateY(-100%)', 'translateY(0)'],
      down: ['translateY(100%)', 'translateY(0)']
    };

    return this.animate([
      { transform: transforms[direction][0] },
      { transform: transforms[direction][1] }
    ], {
      duration: 300,
      ...options
    });
  }

  scale(from: number, to: number, options: AnimationOptions = {}): Promise<void> {
    return this.animate([
      { transform: `scale(${from})` },
      { transform: `scale(${to})` }
    ], {
      duration: 300,
      ...options
    });
  }

  rotate(degrees: number, options: AnimationOptions = {}): Promise<void> {
    return this.animate([
      { transform: 'rotate(0deg)' },
      { transform: `rotate(${degrees}deg)` }
    ], {
      duration: 300,
      ...options
    });
  }

  private animate(keyframes: Keyframe[], options: AnimationOptions): Promise<void> {
    const animation = this.element.animate(keyframes, {
      duration: options.duration || 300,
      easing: options.easing || 'ease',
      delay: options.delay || 0,
      iterations: options.iterations || 1,
      direction: options.direction || 'normal',
      fill: options.fillMode || 'both'
    });

    this.animations.push(animation);

    return new Promise((resolve) => {
      animation.addEventListener('finish', () => {
        const index = this.animations.indexOf(animation);
        if (index > -1) {
          this.animations.splice(index, 1);
        }
        resolve();
      });
    });
  }

  stop(): void {
    this.animations.forEach(animation => animation.cancel());
    this.animations = [];
  }

  pause(): void {
    this.animations.forEach(animation => animation.pause());
  }

  resume(): void {
    this.animations.forEach(animation => animation.play());
  }

  static create(element: HTMLElement): Animator {
    return new Animator(element);
  }
}

export { Animator };
export default Animator;
