#!/bin/bash
# Audio Processing Automation - Professional Audio Processing & Mastering
# Author: Fahed Mlaiel (mlaiel@live.de)
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
# Description: Advanced audio processing with DEMUCS separation, EBU R128 normalization, and multi-format conversion
# Usage: ./audio_processing_automation.sh [--profile musician|comedian|podcaster] [--input FILE/DIR] [--format wav|flac|mp3|opus]

set -euo pipefail

# ═══════════════════════════════════════════════════════════════════
# 🎨 ANSI COLOR CODES & STYLING
# ═══════════════════════════════════════════════════════════════════
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly WHITE='\033[1;37m'
readonly BOLD='\033[1m'
readonly NC='\033[0m' # No Color

# ═══════════════════════════════════════════════════════════════════
# 📋 CONFIGURATION & GLOBALS
# ═══════════════════════════════════════════════════════════════════
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
readonly LOG_DIR="/tmp/desktop_logs"
readonly AUDIO_LOG="${LOG_DIR}/audio_processing.log"
readonly WORK_DIR="/tmp/audio_processing"
readonly OUTPUT_DIR="${WORK_DIR}/output"
readonly TEMP_DIR="${WORK_DIR}/temp"

# Default configuration
CREATOR_PROFILE="musician"
INPUT_PATH=""
OUTPUT_FORMAT="wav"
ENABLE_DEMUCS=true
ENABLE_NORMALIZATION=true
ENABLE_MASTERING=true
PARALLEL_PROCESSING=true
QUALITY_PRESET="high"

# Audio processing presets
declare -A QUALITY_PRESETS=(
    ["low"]="16bit_44khz"
    ["medium"]="24bit_48khz"
    ["high"]="24bit_96khz"
    ["studio"]="32bit_192khz"
)

# ═══════════════════════════════════════════════════════════════════
# 🛠️ UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case "$level" in
        "INFO")  echo -e "${CYAN}[INFO]${NC} ${timestamp} - $message" | tee -a "$AUDIO_LOG" ;;
        "WARN")  echo -e "${YELLOW}[WARN]${NC} ${timestamp} - $message" | tee -a "$AUDIO_LOG" ;;
        "ERROR") echo -e "${RED}[ERROR]${NC} ${timestamp} - $message" | tee -a "$AUDIO_LOG" ;;
        "SUCCESS") echo -e "${GREEN}[SUCCESS]${NC} ${timestamp} - $message" | tee -a "$AUDIO_LOG" ;;
        *) echo -e "${WHITE}[$level]${NC} ${timestamp} - $message" | tee -a "$AUDIO_LOG" ;;
    esac
}

show_header() {
    echo -e "${PURPLE}${BOLD}"
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║                🎵 AINFLUE AUDIO PROCESSING AUTOMATION            ║"
    echo "║                                                                  ║"
    echo "║      Professional Audio Processing & Mastering System           ║"
    echo "║                                                                  ║"
    echo "║  © 2025 Fahed Mlaiel - Advanced Audio Engineering & ML          ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

show_progress() {
    local current=$1
    local total=$2
    local step_name="$3"
    local width=50
    local percentage=$((current * 100 / total))
    local completed=$((current * width / total))
    
    printf "\r${PURPLE}Audio Progress${NC}: ["
    printf "%*s" $completed | tr ' ' '█'
    printf "%*s" $((width - completed))
    printf "] ${BOLD}%d%%${NC} - %s" $percentage "$step_name"
}

# ═══════════════════════════════════════════════════════════════════
# 🔍 ENVIRONMENT VALIDATION
# ═══════════════════════════════════════════════════════════════════
validate_audio_environment() {
    log "INFO" "🔍 Validating audio processing environment..."
    
    # Check for FFmpeg
    if ! command -v ffmpeg &> /dev/null; then
        log "ERROR" "❌ FFmpeg is required but not installed"
        return 1
    fi
    
    local ffmpeg_version=$(ffmpeg -version | head -1 | cut -d' ' -f3)
    log "INFO" "🎧 FFmpeg version: $ffmpeg_version"
    
    # Check for Python and audio libraries
    if ! command -v python3 &> /dev/null; then
        log "ERROR" "❌ Python3 is required but not installed"
        return 1
    fi
    
    # Check for SoX (Sound eXchange)
    if ! command -v sox &> /dev/null; then
        log "WARN" "⚠️ SoX not found, installing..."
        # Attempt to install SoX
        if command -v apt-get &> /dev/null; then
            sudo apt-get update && sudo apt-get install -y sox libsox-fmt-all
        elif command -v yum &> /dev/null; then
            sudo yum install -y sox
        elif command -v brew &> /dev/null; then
            brew install sox
        else
            log "ERROR" "❌ Cannot install SoX automatically"
            return 1
        fi
    fi
    
    # Validate DEMUCS installation
    if [[ "$ENABLE_DEMUCS" == "true" ]]; then
        if ! python3 -c "import demucs" 2>/dev/null; then
            log "WARN" "⚠️ DEMUCS not found, installing..."
            pip3 install demucs || {
                log "WARN" "⚠️ Failed to install DEMUCS, disabling source separation"
                ENABLE_DEMUCS=false
            }
        fi
    fi
    
    log "SUCCESS" "✅ Audio environment validated"
    return 0
}

# ═══════════════════════════════════════════════════════════════════
# 🎵 AUDIO ANALYSIS FUNCTIONS
# ═══════════════════════════════════════════════════════════════════
analyze_audio_file() {
    local input_file="$1"
    local analysis_file="${TEMP_DIR}/$(basename "$input_file" .*)_analysis.json"
    
    log "INFO" "🔍 Analyzing audio file: $(basename "$input_file")"
    
    # Extract audio metadata and technical information
    ffprobe -v quiet -print_format json -show_format -show_streams "$input_file" > "$analysis_file" 2>/dev/null || {
        log "ERROR" "❌ Failed to analyze audio file: $input_file"
        return 1
    }
    
    # Extract key metrics
    local duration=$(jq -r '.format.duration // "unknown"' "$analysis_file")
    local bitrate=$(jq -r '.format.bit_rate // "unknown"' "$analysis_file")
    local sample_rate=$(jq -r '.streams[0].sample_rate // "unknown"' "$analysis_file")
    local channels=$(jq -r '.streams[0].channels // "unknown"' "$analysis_file")
    
    log "INFO" "📊 Duration: ${duration}s, Bitrate: ${bitrate}, Sample Rate: ${sample_rate}Hz, Channels: $channels"
    
    # Analyze audio levels and peaks
    local levels_file="${TEMP_DIR}/$(basename "$input_file" .*)_levels.txt"
    ffmpeg -i "$input_file" -af "ebur128=peak=true:framelog=verbose" -f null - 2>"$levels_file" >/dev/null || {
        log "WARN" "⚠️ Failed to analyze audio levels"
    }
    
    echo "$analysis_file"
}

detect_audio_type() {
    local input_file="$1"
    local analysis_file="$2"
    
    # Detect if it's music, speech, or mixed content
    local duration=$(jq -r '.format.duration // 0' "$analysis_file")
    local sample_rate=$(jq -r '.streams[0].sample_rate // 0' "$analysis_file")
    
    # Simple heuristics for content type detection
    if [[ $(echo "$duration > 120" | bc -l 2>/dev/null || echo "0") == "1" ]]; then
        if [[ "$sample_rate" -ge 44100 ]]; then
            echo "music"
        else
            echo "speech"
        fi
    else
        echo "speech"
    fi
}

# ═══════════════════════════════════════════════════════════════════
# 🎛️ AUDIO PROCESSING FUNCTIONS
# ═══════════════════════════════════════════════════════════════════
apply_source_separation() {
    local input_file="$1"
    local output_dir="$2"
    
    if [[ "$ENABLE_DEMUCS" != "true" ]]; then
        log "INFO" "⏭️ Source separation disabled"
        return 0
    fi
    
    log "INFO" "🎵 Applying DEMUCS source separation..."
    show_progress 2 8 "Source Separation"
    
    local demucs_output="${output_dir}/separated"
    mkdir -p "$demucs_output"
    
    # Run DEMUCS separation
    python3 -m demucs.separate \
        --name htdemucs \
        --out "$demucs_output" \
        "$input_file" 2>/dev/null || {
        log "WARN" "⚠️ Source separation failed, continuing with original file"
        return 0
    }
    
    log "SUCCESS" "✅ Source separation completed"
    
    # List separated components
    local separated_dir=$(find "$demucs_output" -name "htdemucs" -type d | head -1)
    if [[ -d "$separated_dir" ]]; then
        log "INFO" "🎵 Separated components:"
        find "$separated_dir" -name "*.wav" -exec basename {} \; | while read -r component; do
            log "INFO" "   - $component"
        done
    fi
}

apply_ebu_normalization() {
    local input_file="$1"
    local output_file="$2"
    local target_lufs="$3"
    
    log "INFO" "📢 Applying EBU R128 normalization (Target: ${target_lufs} LUFS)..."
    show_progress 3 8 "EBU R128 Normalization"
    
    # First pass: measure loudness
    local measurement_log="${TEMP_DIR}/$(basename "$input_file" .*)_loudness.txt"
    ffmpeg -i "$input_file" -af "ebur128=peak=true" -f null - 2>"$measurement_log" >/dev/null || {
        log "ERROR" "❌ Failed to measure loudness"
        return 1
    }
    
    # Extract measured loudness
    local measured_lufs=$(grep "I:" "$measurement_log" | tail -1 | grep -o "\-\?[0-9]\+\.[0-9]\+ LUFS" | cut -d' ' -f1 || echo "-23.0")
    log "INFO" "📊 Measured loudness: ${measured_lufs} LUFS"
    
    # Calculate gain adjustment
    local gain_adjustment=$(echo "$target_lufs - $measured_lufs" | bc -l 2>/dev/null || echo "0")
    
    if [[ $(echo "$gain_adjustment > 0.1" | bc -l 2>/dev/null || echo "0") == "1" || $(echo "$gain_adjustment < -0.1" | bc -l 2>/dev/null || echo "0") == "1" ]]; then
        log "INFO" "🔧 Applying gain adjustment: ${gain_adjustment} dB"
        
        # Second pass: apply normalization
        ffmpeg -i "$input_file" \
            -af "loudnorm=I=${target_lufs}:TP=-1:LRA=7:measured_I=${measured_lufs}:measured_TP=0:measured_LRA=7:measured_thresh=-34:offset=${gain_adjustment}" \
            -c:a pcm_s24le \
            "$output_file" -y >/dev/null 2>&1 || {
            log "ERROR" "❌ Failed to apply normalization"
            return 1
        }
    else
        log "INFO" "✅ Audio already within target range, copying..."
        cp "$input_file" "$output_file"
    fi
    
    log "SUCCESS" "✅ EBU R128 normalization completed"
}

apply_mastering_chain() {
    local input_file="$1"
    local output_file="$2"
    local audio_type="$3"
    
    if [[ "$ENABLE_MASTERING" != "true" ]]; then
        log "INFO" "⏭️ Mastering disabled"
        cp "$input_file" "$output_file"
        return 0
    fi
    
    log "INFO" "🎚️ Applying mastering chain for $audio_type content..."
    show_progress 4 8 "Audio Mastering"
    
    local mastering_chain=""
    
    case "$audio_type" in
        "music")
            # Music mastering chain
            mastering_chain="highpass=f=20,lowpass=f=20000,compand=0.1,0.3:-90/-90,-60/-40,-30/-20,-20/-10:6:0:-90:0.2,acompressor=threshold=-12dB:ratio=3:attack=1ms:release=100ms,adeclick,denoise=nr=12"
            ;;
        "speech")
            # Speech/podcast mastering chain
            mastering_chain="highpass=f=80,lowpass=f=8000,compand=0.1,0.3:-90/-90,-45/-30,-25/-15,-15/-8:3:0:-90:0.1,acompressor=threshold=-18dB:ratio=2:attack=5ms:release=50ms,deesser,noisereduce"
            ;;
        *)
            # Generic mastering chain
            mastering_chain="highpass=f=40,lowpass=f=15000,compand=0.1,0.3:-90/-90,-50/-35,-25/-18,-15/-10:4:0:-90:0.15,acompressor=threshold=-15dB:ratio=2.5:attack=2ms:release=75ms"
            ;;
    esac
    
    # Apply mastering chain
    ffmpeg -i "$input_file" \
        -af "$mastering_chain" \
        -c:a pcm_s24le \
        "$output_file" -y >/dev/null 2>&1 || {
        log "ERROR" "❌ Failed to apply mastering chain"
        return 1
    }
    
    log "SUCCESS" "✅ Mastering chain applied"
}

convert_audio_format() {
    local input_file="$1"
    local output_file="$2"
    local format="$3"
    local quality="$4"
    
    log "INFO" "🔄 Converting to $format format ($quality quality)..."
    show_progress 5 8 "Format Conversion"
    
    local codec_params=""
    local file_extension=""
    
    case "$format" in
        "wav")
            codec_params="-c:a pcm_s24le"
            file_extension="wav"
            ;;
        "flac")
            codec_params="-c:a flac -compression_level 8"
            file_extension="flac"
            ;;
        "mp3")
            case "$quality" in
                "high") codec_params="-c:a libmp3lame -b:a 320k" ;;
                "medium") codec_params="-c:a libmp3lame -b:a 192k" ;;
                "low") codec_params="-c:a libmp3lame -b:a 128k" ;;
                *) codec_params="-c:a libmp3lame -b:a 192k" ;;
            esac
            file_extension="mp3"
            ;;
        "opus")
            case "$quality" in
                "high") codec_params="-c:a libopus -b:a 128k" ;;
                "medium") codec_params="-c:a libopus -b:a 96k" ;;
                "low") codec_params="-c:a libopus -b:a 64k" ;;
                *) codec_params="-c:a libopus -b:a 96k" ;;
            esac
            file_extension="opus"
            ;;
        *)
            log "ERROR" "❌ Unsupported format: $format"
            return 1
            ;;
    esac
    
    # Apply format conversion
    local final_output="${output_file%.*}.${file_extension}"
    ffmpeg -i "$input_file" $codec_params "$final_output" -y >/dev/null 2>&1 || {
        log "ERROR" "❌ Failed to convert to $format"
        return 1
    }
    
    log "SUCCESS" "✅ Converted to $format: $(basename "$final_output")"
}

# ═══════════════════════════════════════════════════════════════════
# 🎯 PROFILE-SPECIFIC PROCESSING
# ═══════════════════════════════════════════════════════════════════
configure_musician_profile() {
    log "INFO" "🎵 Configuring for MUSICIAN profile"
    ENABLE_DEMUCS=true
    ENABLE_NORMALIZATION=true
    ENABLE_MASTERING=true
    TARGET_LUFS="-14"  # Music streaming standard
    QUALITY_PRESET="high"
}

configure_comedian_profile() {
    log "INFO" "🎭 Configuring for COMEDIAN profile" 
    ENABLE_DEMUCS=false  # Usually not needed for comedy/speech
    ENABLE_NORMALIZATION=true
    ENABLE_MASTERING=true
    TARGET_LUFS="-18"  # Speech/podcast standard
    QUALITY_PRESET="medium"
}

configure_podcaster_profile() {
    log "INFO" "🎙️ Configuring for PODCASTER profile"
    ENABLE_DEMUCS=false
    ENABLE_NORMALIZATION=true
    ENABLE_MASTERING=true
    TARGET_LUFS="-16"  # Podcast standard
    QUALITY_PRESET="medium"
}

# ═══════════════════════════════════════════════════════════════════
# 🏭 BATCH PROCESSING
# ═══════════════════════════════════════════════════════════════════
process_single_file() {
    local input_file="$1"
    local output_dir="$2"
    
    log "INFO" "🎵 Processing: $(basename "$input_file")"
    
    # Create temporary files
    local basename_no_ext=$(basename "$input_file" | sed 's/\.[^.]*$//')
    local temp_file1="${TEMP_DIR}/${basename_no_ext}_temp1.wav"
    local temp_file2="${TEMP_DIR}/${basename_no_ext}_temp2.wav"
    local temp_file3="${TEMP_DIR}/${basename_no_ext}_temp3.wav"
    local final_output="${output_dir}/${basename_no_ext}_processed"
    
    # Step 1: Analyze audio
    local analysis_file=$(analyze_audio_file "$input_file") || return 1
    local audio_type=$(detect_audio_type "$input_file" "$analysis_file")
    
    # Step 2: Source separation (if enabled)
    apply_source_separation "$input_file" "$output_dir" || return 1
    
    # Step 3: Convert to working format (high quality WAV)
    ffmpeg -i "$input_file" -c:a pcm_s24le -ar 48000 "$temp_file1" -y >/dev/null 2>&1 || {
        log "ERROR" "❌ Failed to convert to working format"
        return 1
    }
    
    # Step 4: Apply normalization
    apply_ebu_normalization "$temp_file1" "$temp_file2" "$TARGET_LUFS" || return 1
    
    # Step 5: Apply mastering
    apply_mastering_chain "$temp_file2" "$temp_file3" "$audio_type" || return 1
    
    # Step 6: Convert to final format
    convert_audio_format "$temp_file3" "$final_output" "$OUTPUT_FORMAT" "$QUALITY_PRESET" || return 1
    
    # Cleanup temporary files
    rm -f "$temp_file1" "$temp_file2" "$temp_file3" 2>/dev/null
    
    log "SUCCESS" "✅ Processing completed: $(basename "$input_file")"
}

process_batch() {
    local input_path="$1"
    local output_dir="$2"
    
    log "INFO" "🏭 Starting batch processing..."
    show_progress 6 8 "Batch Processing"
    
    if [[ -f "$input_path" ]]; then
        # Single file processing
        process_single_file "$input_path" "$output_dir" || return 1
    elif [[ -d "$input_path" ]]; then
        # Directory processing
        local audio_files=()
        while IFS= read -r -d '' file; do
            audio_files+=("$file")
        done < <(find "$input_path" -type f \( -iname "*.wav" -o -iname "*.mp3" -o -iname "*.flac" -o -iname "*.m4a" -o -iname "*.aac" \) -print0)
        
        if [[ ${#audio_files[@]} -eq 0 ]]; then
            log "ERROR" "❌ No audio files found in directory: $input_path"
            return 1
        fi
        
        log "INFO" "📁 Found ${#audio_files[@]} audio files to process"
        
        if [[ "$PARALLEL_PROCESSING" == "true" ]] && [[ ${#audio_files[@]} -gt 1 ]]; then
            # Parallel processing
            log "INFO" "⚡ Starting parallel processing..."
            
            local max_parallel=4
            local active_jobs=0
            
            for file in "${audio_files[@]}"; do
                if [[ $active_jobs -ge $max_parallel ]]; then
                    wait -n  # Wait for any job to complete
                    ((active_jobs--))
                fi
                
                process_single_file "$file" "$output_dir" &
                ((active_jobs++))
            done
            
            # Wait for all remaining jobs to complete
            wait
        else
            # Sequential processing
            for file in "${audio_files[@]}"; do
                process_single_file "$file" "$output_dir" || {
                    log "ERROR" "❌ Failed to process: $(basename "$file")"
                    continue
                }
            done
        fi
    else
        log "ERROR" "❌ Invalid input path: $input_path"
        return 1
    fi
    
    log "SUCCESS" "✅ Batch processing completed"
}

# ═══════════════════════════════════════════════════════════════════
# 📊 QUALITY ANALYSIS
# ═══════════════════════════════════════════════════════════════════
generate_quality_report() {
    log "INFO" "📊 Generating quality analysis report..."
    show_progress 7 8 "Quality Analysis"
    
    local report_file="${OUTPUT_DIR}/quality_report_$(date +%Y%m%d_%H%M%S).md"
    
    cat > "$report_file" << EOF
# Audio Processing Quality Report

**Processing Date**: $(date '+%Y-%m-%d %H:%M:%S')
**Profile**: $CREATOR_PROFILE
**Output Format**: $OUTPUT_FORMAT
**Quality Preset**: $QUALITY_PRESET

## 🎯 Processing Configuration

### Enabled Features
- Source Separation (DEMUCS): $ENABLE_DEMUCS
- EBU R128 Normalization: $ENABLE_NORMALIZATION (Target: $TARGET_LUFS LUFS)
- Mastering Chain: $ENABLE_MASTERING
- Parallel Processing: $PARALLEL_PROCESSING

### Technical Specifications
- Sample Rate: 48kHz (processing), varies (output)
- Bit Depth: 24-bit (processing)
- Normalization Standard: EBU R128/ITU-R BS.1770
- Mastering: Content-adaptive processing chain

## 📁 Processed Files

EOF
    
    # List processed files with basic info
    find "$OUTPUT_DIR" -type f \( -name "*.wav" -o -name "*.mp3" -o -name "*.flac" -o -name "*.opus" \) | while read -r file; do
        if [[ -f "$file" ]]; then
            local file_size=$(du -h "$file" | cut -f1)
            local file_info=$(ffprobe -v quiet -print_format json -show_format "$file" 2>/dev/null)
            local duration=$(echo "$file_info" | jq -r '.format.duration // "unknown"' 2>/dev/null || echo "unknown")
            local bitrate=$(echo "$file_info" | jq -r '.format.bit_rate // "unknown"' 2>/dev/null || echo "unknown")
            
            echo "### $(basename "$file")" >> "$report_file"
            echo "- **Size**: $file_size" >> "$report_file"
            echo "- **Duration**: ${duration}s" >> "$report_file"
            echo "- **Bitrate**: ${bitrate} bps" >> "$report_file"
            echo >> "$report_file"
        fi
    done
    
    cat >> "$report_file" << EOF

## 🔧 Recommendations

Based on the processing profile and results:

### For Musicians
- Use high-quality source materials (24-bit/48kHz+)
- Consider source separation for mixing improvements
- Monitor for clipping after mastering

### For Comedians/Podcasters
- Focus on speech clarity and intelligibility
- Use noise reduction in noisy environments
- Consider stereo-to-mono conversion for speech

### Quality Assurance
- Always listen to processed outputs
- Compare loudness levels across platforms
- Verify format compatibility with target platforms

---
*Report generated by Ainflue Audio Processing Automation*
*© 2025 Fahed Mlaiel - Advanced Audio Engineering*
EOF
    
    log "SUCCESS" "✅ Quality report generated: $report_file"
}

# ═══════════════════════════════════════════════════════════════════
# 📚 HELP & USAGE
# ═══════════════════════════════════════════════════════════════════
show_help() {
    echo -e "${CYAN}${BOLD}USAGE:${NC}"
    echo "  $0 [OPTIONS]"
    echo
    echo -e "${CYAN}${BOLD}OPTIONS:${NC}"
    echo "  --profile PROFILE       Creator profile: musician|comedian|podcaster (default: musician)"
    echo "  --input PATH           Input file or directory path"
    echo "  --format FORMAT        Output format: wav|flac|mp3|opus (default: wav)"
    echo "  --quality PRESET       Quality preset: low|medium|high|studio (default: high)"
    echo "  --no-demucs           Disable DEMUCS source separation"
    echo "  --no-normalization    Disable EBU R128 normalization"
    echo "  --no-mastering        Disable mastering chain"
    echo "  --sequential          Use sequential processing (disable parallel)"
    echo "  --target-lufs LUFS    Target loudness in LUFS (overrides profile default)"
    echo "  --help                Show this help message"
    echo
    echo -e "${CYAN}${BOLD}EXAMPLES:${NC}"
    echo "  $0 --profile musician --input /path/to/song.wav --format flac"
    echo "  $0 --profile comedian --input /path/to/recordings/ --format mp3"
    echo "  $0 --profile podcaster --input episode.wav --no-demucs --target-lufs -16"
    echo
    echo -e "${CYAN}${BOLD}SUPPORTED FORMATS:${NC}"
    echo "  📥 Input:  WAV, MP3, FLAC, M4A, AAC"
    echo "  📤 Output: WAV, FLAC, MP3, OPUS"
    echo
    echo -e "${CYAN}${BOLD}PROCESSING FEATURES:${NC}"
    echo "  🎵 DEMUCS source separation (music only)"
    echo "  📢 EBU R128/ITU-R BS.1770 loudness normalization"
    echo "  🎚️ Content-adaptive mastering chain"
    echo "  ⚡ Parallel batch processing"
    echo "  📊 Quality analysis and reporting"
}

# ═══════════════════════════════════════════════════════════════════
# 🎯 MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════════
main() {
    # Create required directories
    mkdir -p "$LOG_DIR" "$WORK_DIR" "$OUTPUT_DIR" "$TEMP_DIR"
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --profile)
                CREATOR_PROFILE="$2"
                shift 2
                ;;
            --input)
                INPUT_PATH="$2"
                shift 2
                ;;
            --format)
                OUTPUT_FORMAT="$2"
                shift 2
                ;;
            --quality)
                QUALITY_PRESET="$2"
                shift 2
                ;;
            --no-demucs)
                ENABLE_DEMUCS=false
                shift
                ;;
            --no-normalization)
                ENABLE_NORMALIZATION=false
                shift
                ;;
            --no-mastering)
                ENABLE_MASTERING=false
                shift
                ;;
            --sequential)
                PARALLEL_PROCESSING=false
                shift
                ;;
            --target-lufs)
                TARGET_LUFS="$2"
                shift 2
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                log "ERROR" "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Validate required arguments
    if [[ -z "$INPUT_PATH" ]]; then
        log "ERROR" "❌ Input path is required (--input)"
        show_help
        exit 1
    fi
    
    if [[ ! -e "$INPUT_PATH" ]]; then
        log "ERROR" "❌ Input path does not exist: $INPUT_PATH"
        exit 1
    fi
    
    show_header
    
    local start_time=$(date +%s)
    
    log "INFO" "🎵 Starting Ainflue Audio Processing"
    log "INFO" "🎯 Profile: $CREATOR_PROFILE"
    log "INFO" "📁 Input: $INPUT_PATH"
    log "INFO" "🎧 Output format: $OUTPUT_FORMAT ($QUALITY_PRESET quality)"
    
    # Validate environment
    validate_audio_environment || exit 1
    
    # Configure profile-specific settings
    case "$CREATOR_PROFILE" in
        "musician") configure_musician_profile ;;
        "comedian") configure_comedian_profile ;;
        "podcaster") configure_podcaster_profile ;;
        *)
            log "ERROR" "❌ Invalid creator profile: $CREATOR_PROFILE"
            show_help
            exit 1
            ;;
    esac
    
    # Start processing
    show_progress 1 8 "Environment Setup"
    process_batch "$INPUT_PATH" "$OUTPUT_DIR" || exit 1
    
    # Generate quality report
    generate_quality_report || exit 1
    
    # Final cleanup
    show_progress 8 8 "Cleanup"
    rm -rf "$TEMP_DIR" 2>/dev/null
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    echo
    log "SUCCESS" "🎉 Audio processing completed in ${duration}s"
    echo -e "${GREEN}${BOLD}"
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║                   ✅ AUDIO PROCESSING COMPLETE                   ║"
    echo "║                                                                  ║"
    echo "║  Professional audio processing finished successfully            ║"
    echo "║  Profile: $CREATOR_PROFILE                                       ║"
    echo "║  Output: $OUTPUT_DIR                                             ║"
    echo "║  Processing time: ${duration} seconds                            ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    # Show next steps
    echo -e "${CYAN}${BOLD}NEXT STEPS:${NC}"
    echo "1. Review processed files in: $OUTPUT_DIR"
    echo "2. Check quality report for detailed analysis"
    echo "3. Test playback on target devices/platforms"
    echo "4. Proceed with protection and distribution"
}

# Execute main function with all arguments
main "$@"