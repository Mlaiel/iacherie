/**
 * File Utilities
 */

export const getFileExtension = (filename: string): string => {
  return filename.slice(((filename.lastIndexOf('.') - 1) >>> 0) + 2);
};

export const getFileName = (path: string): string => {
  return path.split(/[\\/]/).pop() || '';
};

export const getFileType = (filename: string): 'audio' | 'video' | 'image' | 'document' => {
  const ext = getFileExtension(filename).toLowerCase();
  
  const audioExts = ['mp3', 'wav', 'flac', 'aac', 'm4a', 'ogg'];
  const videoExts = ['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm'];
  const imageExts = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp'];
  
  if (audioExts.includes(ext)) return 'audio';
  if (videoExts.includes(ext)) return 'video';
  if (imageExts.includes(ext)) return 'image';
  return 'document';
};

export const readFileAsText = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = () => reject(reader.error);
    reader.readAsText(file);
  });
};

export const readFileAsDataURL = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = () => reject(reader.error);
    reader.readAsDataURL(file);
  });
};

export const downloadFile = (data: string, filename: string, type = 'text/plain'): void => {
  const blob = new Blob([data], { type });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};
