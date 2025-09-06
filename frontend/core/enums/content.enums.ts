/**
 * @fileoverview Content-related enumerations
 * @author Fahed Mlaiel <mlaiel@live.de>
 */

export enum ContentType {
  IMAGE = 'image',
  VIDEO = 'video',
  AUDIO = 'audio',
  DOCUMENT = 'document',
  MIXED_MEDIA = 'mixed_media',
}

export enum ContentStatus {
  DRAFT = 'draft',
  PROCESSING = 'processing',
  PUBLISHED = 'published',
  ARCHIVED = 'archived',
  DELETED = 'deleted',
  FLAGGED = 'flagged',
}

export enum ProcessingStage {
  UPLOAD = 'upload',
  VALIDATION = 'validation',
  FINGERPRINTING = 'fingerprinting',
  AI_ANALYSIS = 'ai_analysis',
  METADATA_EXTRACTION = 'metadata_extraction',
  QUALITY_CHECK = 'quality_check',
  OPTIMIZATION = 'optimization',
  COMPLETED = 'completed',
  FAILED = 'failed',
}

export enum ContentVisibility {
  PUBLIC = 'public',
  PRIVATE = 'private',
  UNLISTED = 'unlisted',
  COLLABORATORS_ONLY = 'collaborators_only',
}

export enum ContentCategory {
  MUSIC = 'music',
  PHOTOGRAPHY = 'photography',
  VIDEO = 'video',
  GRAPHICS = 'graphics',
  WRITING = 'writing',
  EDUCATION = 'education',
  ENTERTAINMENT = 'entertainment',
  BUSINESS = 'business',
  TECHNOLOGY = 'technology',
  LIFESTYLE = 'lifestyle',
}

export enum QualityScore {
  VERY_LOW = 1,
  LOW = 2,
  MEDIUM = 3,
  HIGH = 4,
  VERY_HIGH = 5,
}

export enum ContentFormat {
  // Image formats
  JPEG = 'jpeg',
  PNG = 'png',
  GIF = 'gif',
  WEBP = 'webp',
  SVG = 'svg',
  
  // Video formats
  MP4 = 'mp4',
  AVI = 'avi',
  MOV = 'mov',
  MKV = 'mkv',
  WEBM = 'webm',
  
  // Audio formats
  MP3 = 'mp3',
  WAV = 'wav',
  FLAC = 'flac',
  AAC = 'aac',
  OGG = 'ogg',
  
  // Document formats
  PDF = 'pdf',
  DOC = 'doc',
  DOCX = 'docx',
  TXT = 'txt',
  RTF = 'rtf',
}