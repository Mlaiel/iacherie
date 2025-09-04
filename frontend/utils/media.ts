/**
 * Media Utilities
 */

export const getMediaDimensions = (file: File): Promise<{ width: number; height: number }> => {
  return new Promise((resolve, reject) => {
    if (file.type.startsWith('image/')) {
      const img = new Image();
      img.onload = () => resolve({ width: img.width, height: img.height });
      img.onerror = reject;
      img.src = URL.createObjectURL(file);
    } else if (file.type.startsWith('video/')) {
      const video = document.createElement('video');
      video.onloadedmetadata = () => resolve({ width: video.videoWidth, height: video.videoHeight });
      video.onerror = reject;
      video.src = URL.createObjectURL(file);
    } else {
      reject(new Error('Unsupported media type'));
    }
  });
};

export const getMediaDuration = (file: File): Promise<number> => {
  return new Promise((resolve, reject) => {
    if (file.type.startsWith('video/') || file.type.startsWith('audio/')) {
      const media = file.type.startsWith('video/') 
        ? document.createElement('video') 
        : document.createElement('audio');
      
      media.onloadedmetadata = () => resolve(media.duration);
      media.onerror = reject;
      media.src = URL.createObjectURL(file);
    } else {
      reject(new Error('File is not audio or video'));
    }
  });
};

export const createThumbnail = (videoFile: File, timeInSeconds = 1): Promise<string> => {
  return new Promise((resolve, reject) => {
    const video = document.createElement('video');
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d')!;

    video.onloadedmetadata = () => {
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      video.currentTime = timeInSeconds;
    };

    video.onseeked = () => {
      ctx.drawImage(video, 0, 0);
      const dataURL = canvas.toDataURL('image/jpeg', 0.8);
      URL.revokeObjectURL(video.src);
      resolve(dataURL);
    };

    video.onerror = reject;
    video.src = URL.createObjectURL(videoFile);
  });
};

export const extractFrames = (videoFile: File, frameCount = 10): Promise<string[]> => {
  return new Promise((resolve, reject) => {
    const video = document.createElement('video');
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d')!;
    const frames: string[] = [];

    video.onloadedmetadata = () => {
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      
      const interval = video.duration / frameCount;
      let currentFrame = 0;

      const extractFrame = () => {
        if (currentFrame >= frameCount) {
          URL.revokeObjectURL(video.src);
          resolve(frames);
          return;
        }

        video.currentTime = currentFrame * interval;
      };

      video.onseeked = () => {
        ctx.drawImage(video, 0, 0);
        frames.push(canvas.toDataURL('image/jpeg', 0.8));
        currentFrame++;
        extractFrame();
      };

      extractFrame();
    };

    video.onerror = reject;
    video.src = URL.createObjectURL(videoFile);
  });
};
