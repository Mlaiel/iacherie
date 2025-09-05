#!/bin/bash
# Workflow Orchestrator - Central Desktop Scripts Coordinator
# Author: Fahed Mlaiel (mlaiel@live.de)
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
# Description: Orchestrates complete workflows for Upload→Processing→Protection→SEO→Collaboration→Monetization→Distribution
# Usage: ./workflow_orchestrator.sh [--profile musician|photographer|blogger|influencer|comedian] [--workflow upload|process|full]

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
readonly WORKFLOW_LOG="${LOG_DIR}/workflow_orchestrator.log"
readonly PID_FILE="/tmp/workflow_orchestrator.pid"

# Default configuration
CREATOR_PROFILE="musician"
WORKFLOW_TYPE="full"
CONTENT_TYPE=""
PLATFORMS=""
PARALLEL_JOBS=4

# ═══════════════════════════════════════════════════════════════════
# 🛠️ UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case "$level" in
        "INFO")  echo -e "${CYAN}[INFO]${NC} ${timestamp} - $message" | tee -a "$WORKFLOW_LOG" ;;
        "WARN")  echo -e "${YELLOW}[WARN]${NC} ${timestamp} - $message" | tee -a "$WORKFLOW_LOG" ;;
        "ERROR") echo -e "${RED}[ERROR]${NC} ${timestamp} - $message" | tee -a "$WORKFLOW_LOG" ;;
        "SUCCESS") echo -e "${GREEN}[SUCCESS]${NC} ${timestamp} - $message" | tee -a "$WORKFLOW_LOG" ;;
        *) echo -e "${WHITE}[$level]${NC} ${timestamp} - $message" | tee -a "$WORKFLOW_LOG" ;;
    esac
}

show_header() {
    echo -e "${PURPLE}${BOLD}"
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║                    🎯 AINFLUE WORKFLOW ORCHESTRATOR             ║"
    echo "║                                                                  ║"
    echo "║        Central Desktop Scripts Automation Coordinator           ║"
    echo "║                                                                  ║"
    echo "║  © 2025 Fahed Mlaiel - Advanced IA/ML Systems Architecture      ║"
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
    
    printf "\r${BLUE}Progress${NC}: ["
    printf "%*s" $completed | tr ' ' '█'
    printf "%*s" $((width - completed))
    printf "] ${BOLD}%d%%${NC} - %s" $percentage "$step_name"
}

validate_dependencies() {
    log "INFO" "🔍 Validating script dependencies..."
    
    local required_scripts=(
        "audio_processing_automation.sh"
        "protection_automation.sh"
        "seo_automation.sh"
        "collaboration_automation.sh"
        "monetization_automation.sh"
        "distribution_automation.sh"
        "analytics_automation.sh"
        "security_automation.sh"
    )
    
    local missing_scripts=()
    for script in "${required_scripts[@]}"; do
        if [[ ! -f "${SCRIPT_DIR}/${script}" ]]; then
            missing_scripts+=("$script")
        fi
    done
    
    if [[ ${#missing_scripts[@]} -gt 0 ]]; then
        log "ERROR" "❌ Missing required scripts: ${missing_scripts[*]}"
        return 1
    fi
    
    log "SUCCESS" "✅ All required scripts found"
    return 0
}

# ═══════════════════════════════════════════════════════════════════
# 🎯 WORKFLOW PROFILES
# ═══════════════════════════════════════════════════════════════════
configure_musician_workflow() {
    CONTENT_TYPE="audio"
    PLATFORMS="spotify,bandcamp,soundcloud,youtube"
    log "INFO" "🎵 Configured workflow for MUSICIAN profile"
}

configure_photographer_workflow() {
    CONTENT_TYPE="image"
    PLATFORMS="instagram,flickr,500px,getty"
    log "INFO" "📸 Configured workflow for PHOTOGRAPHER profile"
}

configure_blogger_workflow() {
    CONTENT_TYPE="text"
    PLATFORMS="wordpress,medium,substack,ghost"
    log "INFO" "✍️ Configured workflow for BLOGGER profile"
}

configure_influencer_workflow() {
    CONTENT_TYPE="mixed"
    PLATFORMS="instagram,tiktok,youtube,twitter"
    log "INFO" "📱 Configured workflow for INFLUENCER profile"
}

configure_comedian_workflow() {
    CONTENT_TYPE="audio,video"
    PLATFORMS="youtube,spotify,podcast,comedy_central"
    log "INFO" "🎭 Configured workflow for COMEDIAN profile"
}

# ═══════════════════════════════════════════════════════════════════
# 🚀 WORKFLOW EXECUTION PHASES
# ═══════════════════════════════════════════════════════════════════
execute_processing_phase() {
    log "INFO" "🎛️ Starting Processing Phase..."
    show_progress 1 8 "Audio/Video Processing"
    
    if [[ "$CONTENT_TYPE" == *"audio"* ]]; then
        "${SCRIPT_DIR}/audio_processing_automation.sh" --profile "$CREATOR_PROFILE" || {
            log "ERROR" "❌ Audio processing failed"
            return 1
        }
    fi
    
    log "SUCCESS" "✅ Processing phase completed"
}

execute_protection_phase() {
    log "INFO" "🛡️ Starting Protection Phase..."
    show_progress 2 8 "Rights Protection"
    
    "${SCRIPT_DIR}/protection_automation.sh" --content "$CONTENT_TYPE" || {
        log "ERROR" "❌ Protection automation failed"
        return 1
    }
    
    log "SUCCESS" "✅ Protection phase completed"
}

execute_seo_phase() {
    log "INFO" "🔍 Starting SEO Optimization Phase..."
    show_progress 3 8 "SEO Optimization"
    
    "${SCRIPT_DIR}/seo_automation.sh" --content-type "$CONTENT_TYPE" || {
        log "ERROR" "❌ SEO optimization failed"
        return 1
    }
    
    log "SUCCESS" "✅ SEO phase completed"
}

execute_collaboration_phase() {
    log "INFO" "🤝 Starting Collaboration Matching Phase..."
    show_progress 4 8 "Collaboration Matching"
    
    "${SCRIPT_DIR}/collaboration_automation.sh" --profile "$CREATOR_PROFILE" || {
        log "ERROR" "❌ Collaboration matching failed"
        return 1
    }
    
    log "SUCCESS" "✅ Collaboration phase completed"
}

execute_monetization_phase() {
    log "INFO" "💰 Starting Monetization Phase..."
    show_progress 5 8 "Revenue Monetization"
    
    "${SCRIPT_DIR}/monetization_automation.sh" --platforms "$PLATFORMS" || {
        log "ERROR" "❌ Monetization setup failed"
        return 1
    }
    
    log "SUCCESS" "✅ Monetization phase completed"
}

execute_distribution_phase() {
    log "INFO" "📡 Starting Distribution Phase..."
    show_progress 6 8 "Multi-platform Distribution"
    
    "${SCRIPT_DIR}/distribution_automation.sh" --platforms "$PLATFORMS" || {
        log "ERROR" "❌ Distribution failed"
        return 1
    }
    
    log "SUCCESS" "✅ Distribution phase completed"
}

execute_analytics_phase() {
    log "INFO" "📊 Starting Analytics Phase..."
    show_progress 7 8 "Analytics Intelligence"
    
    "${SCRIPT_DIR}/analytics_automation.sh" --profile "$CREATOR_PROFILE" || {
        log "ERROR" "❌ Analytics setup failed"
        return 1
    }
    
    log "SUCCESS" "✅ Analytics phase completed"
}

execute_security_monitoring() {
    log "INFO" "🔐 Starting Security Monitoring..."
    show_progress 8 8 "Security Monitoring"
    
    "${SCRIPT_DIR}/security_automation.sh" --monitor || {
        log "ERROR" "❌ Security monitoring failed"
        return 1
    }
    
    log "SUCCESS" "✅ Security monitoring activated"
}

# ═══════════════════════════════════════════════════════════════════
# 🎯 MAIN WORKFLOW ORCHESTRATION
# ═══════════════════════════════════════════════════════════════════
execute_full_workflow() {
    log "INFO" "🚀 Starting FULL workflow orchestration for $CREATOR_PROFILE profile"
    
    local start_time=$(date +%s)
    
    # Execute all phases in order
    execute_processing_phase || return 1
    execute_protection_phase || return 1
    execute_seo_phase || return 1
    execute_collaboration_phase || return 1
    execute_monetization_phase || return 1
    execute_distribution_phase || return 1
    execute_analytics_phase || return 1
    execute_security_monitoring || return 1
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    echo
    log "SUCCESS" "🎉 FULL workflow completed successfully in ${duration}s"
    echo -e "${GREEN}${BOLD}"
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║                    ✅ WORKFLOW COMPLETED                         ║"
    echo "║                                                                  ║"
    echo "║  All phases executed successfully for $CREATOR_PROFILE profile  ║"
    echo "║  Total execution time: ${duration} seconds                       ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# ═══════════════════════════════════════════════════════════════════
# 📚 HELP & USAGE
# ═══════════════════════════════════════════════════════════════════
show_help() {
    echo -e "${CYAN}${BOLD}USAGE:${NC}"
    echo "  $0 [OPTIONS]"
    echo
    echo -e "${CYAN}${BOLD}OPTIONS:${NC}"
    echo "  --profile PROFILE    Creator profile: musician|photographer|blogger|influencer|comedian"
    echo "  --workflow TYPE      Workflow type: upload|process|full (default: full)"
    echo "  --content-type TYPE  Content type override"
    echo "  --platforms LIST     Platform list override (comma-separated)"
    echo "  --parallel-jobs N    Number of parallel jobs (default: 4)"
    echo "  --help              Show this help message"
    echo
    echo -e "${CYAN}${BOLD}EXAMPLES:${NC}"
    echo "  $0 --profile musician --workflow full"
    echo "  $0 --profile photographer --platforms instagram,flickr"
    echo "  $0 --profile blogger --content-type text --workflow process"
    echo
    echo -e "${CYAN}${BOLD}CREATOR PROFILES:${NC}"
    echo "  🎵 musician     - Audio processing, music platforms"
    echo "  📸 photographer - Image processing, visual platforms"
    echo "  ✍️ blogger      - Text content, publishing platforms"
    echo "  📱 influencer   - Mixed content, social platforms"
    echo "  🎭 comedian     - Audio/video, entertainment platforms"
}

# ═══════════════════════════════════════════════════════════════════
# 🎯 MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════════
main() {
    # Create required directories
    mkdir -p "$LOG_DIR"
    
    # Store PID for monitoring
    echo $$ > "$PID_FILE"
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --profile)
                CREATOR_PROFILE="$2"
                shift 2
                ;;
            --workflow)
                WORKFLOW_TYPE="$2"
                shift 2
                ;;
            --content-type)
                CONTENT_TYPE="$2"
                shift 2
                ;;
            --platforms)
                PLATFORMS="$2"
                shift 2
                ;;
            --parallel-jobs)
                PARALLEL_JOBS="$2"
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
    
    show_header
    
    # Validate dependencies
    validate_dependencies || exit 1
    
    # Configure workflow based on creator profile
    case "$CREATOR_PROFILE" in
        "musician") configure_musician_workflow ;;
        "photographer") configure_photographer_workflow ;;
        "blogger") configure_blogger_workflow ;;
        "influencer") configure_influencer_workflow ;;
        "comedian") configure_comedian_workflow ;;
        *)
            log "ERROR" "❌ Invalid creator profile: $CREATOR_PROFILE"
            show_help
            exit 1
            ;;
    esac
    
    # Execute workflow
    case "$WORKFLOW_TYPE" in
        "full")
            execute_full_workflow || exit 1
            ;;
        "process")
            execute_processing_phase || exit 1
            ;;
        *)
            log "ERROR" "❌ Invalid workflow type: $WORKFLOW_TYPE"
            show_help
            exit 1
            ;;
    esac
    
    # Cleanup
    rm -f "$PID_FILE"
}

# Execute main function with all arguments
main "$@"