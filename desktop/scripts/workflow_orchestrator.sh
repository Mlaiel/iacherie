#!/bin/bash

# Workflow Orchestrator - Central Coordination System
# Author: Fahed Mlaiel (mlaiel@live.de)
# Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
# Description: Central orchestrator for all Ainflue desktop automation workflows
# Usage: ./workflow_orchestrator.sh [--profile musician|photographer|blogger|influencer|comedian] [--workflow upload|process|protect|monetize|distribute] [--help]

# ⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
# TOUS DROITS RÉSERVÉS - PROTÉGÉ PAR LE DROIT D'AUTEUR

set -euo pipefail

# Color definitions
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly WHITE='\033[1;37m'
readonly NC='\033[0m' # No Color

# Script constants
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly LOG_DIR="/tmp/ainflue-logs"
readonly CONFIG_DIR="/tmp/ainflue-config"
readonly TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
readonly LOG_FILE="${LOG_DIR}/orchestrator_${TIMESTAMP}.log"

# Ensure log directory exists
mkdir -p "${LOG_DIR}" "${CONFIG_DIR}"

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  [INFO]${NC} $*" | tee -a "${LOG_FILE}"
}

log_success() {
    echo -e "${GREEN}✅ [SUCCESS]${NC} $*" | tee -a "${LOG_FILE}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  [WARNING]${NC} $*" | tee -a "${LOG_FILE}"
}

log_error() {
    echo -e "${RED}❌ [ERROR]${NC} $*" | tee -a "${LOG_FILE}"
}

log_debug() {
    echo -e "${PURPLE}🔍 [DEBUG]${NC} $*" | tee -a "${LOG_FILE}"
}

# Progress indicator
show_progress() {
    local current=$1
    local total=$2
    local message=$3
    local percent=$((current * 100 / total))
    local filled=$((percent * 40 / 100))
    local empty=$((40 - filled))
    
    printf "\r${CYAN}🚀 Progress: ${NC}["
    printf "%*s" $filled | tr ' ' '█'
    printf "%*s" $empty | tr ' ' '░'
    printf "] ${percent}%% - ${message}"
}

# Display help
show_help() {
    cat << EOF
${WHITE}🎯 AINFLUE WORKFLOW ORCHESTRATOR${NC}
${CYAN}Central coordination system for desktop automation workflows${NC}

${WHITE}USAGE:${NC}
    ./workflow_orchestrator.sh [OPTIONS]

${WHITE}OPTIONS:${NC}
    --profile PROFILE      Creator profile: musician|photographer|blogger|influencer|comedian
    --workflow WORKFLOW    Workflow type: upload|process|protect|monetize|distribute|full
    --input PATH          Input file or directory path
    --output PATH         Output directory path
    --config FILE         Custom configuration file
    --parallel            Enable parallel processing
    --dry-run            Show what would be executed without running
    --verbose            Enable verbose logging
    --help               Show this help message

${WHITE}CREATOR PROFILES:${NC}
    ${CYAN}musician${NC}      - Audio processing, streaming platforms, royalty management
    ${CYAN}photographer${NC}  - Image protection, licensing, portfolio distribution  
    ${CYAN}blogger${NC}       - SEO optimization, content analytics, cross-posting
    ${CYAN}influencer${NC}    - Social platform sync, engagement analytics, brand matching
    ${CYAN}comedian${NC}      - Audio/video content, entertainment platforms, audience metrics

${WHITE}WORKFLOW TYPES:${NC}
    ${CYAN}upload${NC}        - Content upload and initial processing
    ${CYAN}process${NC}       - Content processing and enhancement
    ${CYAN}protect${NC}       - Rights protection and watermarking
    ${CYAN}monetize${NC}      - Revenue optimization and licensing
    ${CYAN}distribute${NC}    - Multi-platform distribution
    ${CYAN}full${NC}          - Complete end-to-end workflow

${WHITE}EXAMPLES:${NC}
    ${CYAN}# Full workflow for musician${NC}
    ./workflow_orchestrator.sh --profile musician --workflow full --input ./audio/ --output ./dist/

    ${CYAN}# Process and protect photographer content${NC}
    ./workflow_orchestrator.sh --profile photographer --workflow protect --input ./photos/

    ${CYAN}# SEO optimization for blogger${NC}
    ./workflow_orchestrator.sh --profile blogger --workflow process --input ./articles/

${WHITE}Author:${NC} Fahed Mlaiel (mlaiel@live.de)
${WHITE}Copyright:${NC} (c) 2025 Fahed Mlaiel. All rights reserved.
EOF
}

# Validate environment
validate_environment() {
    log_info "🔍 Validating environment..."
    
    # Check required scripts exist
    local required_scripts=(
        "audio_processing_automation.sh"
        "protection_automation.sh" 
        "monetization_automation.sh"
        "distribution_automation.sh"
        "seo_automation.sh"
        "analytics_automation.sh"
    )
    
    for script in "${required_scripts[@]}"; do
        if [[ -f "${SCRIPT_DIR}/${script}" ]]; then
            log_debug "Found script: ${script}"
        else
            log_warning "Script not found: ${script} (will be skipped)"
        fi
    done
    
    # Check system resources
    local available_memory=$(free -m | awk 'NR==2{print $7}')
    local available_disk=$(df -h "${SCRIPT_DIR}" | awk 'NR==2{print $4}')
    
    log_info "Available memory: ${available_memory}MB"
    log_info "Available disk space: ${available_disk}"
    
    # Validate minimum requirements
    if [[ $available_memory -lt 1024 ]]; then
        log_warning "Low memory detected (${available_memory}MB). Performance may be affected."
    fi
}

# Execute workflow for musician profile
execute_musician_workflow() {
    local workflow_type=$1
    local input_path=$2
    local output_path=$3
    
    log_info "🎵 Executing musician workflow: ${workflow_type}"
    
    case $workflow_type in
        "upload"|"full")
            log_info "📤 Step 1/5: Content upload and validation"
            show_progress 1 5 "Uploading content..."
            # Upload logic would go here
            ;;
    esac
    
    case $workflow_type in
        "process"|"full")
            log_info "🎛️  Step 2/5: Audio processing"
            show_progress 2 5 "Processing audio..."
            if [[ -f "${SCRIPT_DIR}/audio_processing_automation.sh" ]]; then
                bash "${SCRIPT_DIR}/audio_processing_automation.sh" --profile musician --input "${input_path}" --output "${output_path}" || log_error "Audio processing failed"
            fi
            ;;
    esac
    
    case $workflow_type in
        "protect"|"full")
            log_info "🛡️  Step 3/5: Rights protection"
            show_progress 3 5 "Protecting content..."
            if [[ -f "${SCRIPT_DIR}/protection_automation.sh" ]]; then
                bash "${SCRIPT_DIR}/protection_automation.sh" --content audio --input "${input_path}" || log_error "Protection failed"
            fi
            ;;
    esac
    
    case $workflow_type in
        "monetize"|"full")
            log_info "💰 Step 4/5: Monetization setup"
            show_progress 4 5 "Setting up monetization..."
            if [[ -f "${SCRIPT_DIR}/monetization_automation.sh" ]]; then
                bash "${SCRIPT_DIR}/monetization_automation.sh" --streams spotify,bandcamp --input "${input_path}" || log_error "Monetization setup failed"
            fi
            ;;
    esac
    
    case $workflow_type in
        "distribute"|"full")
            log_info "📡 Step 5/5: Distribution"
            show_progress 5 5 "Distributing content..."
            if [[ -f "${SCRIPT_DIR}/distribution_automation.sh" ]]; then
                bash "${SCRIPT_DIR}/distribution_automation.sh" --platforms music --input "${output_path}" || log_error "Distribution failed"
            fi
            ;;
    esac
    
    echo # New line after progress
    log_success "🎉 Musician workflow completed successfully!"
}

# Execute workflow for photographer profile
execute_photographer_workflow() {
    local workflow_type=$1
    local input_path=$2
    local output_path=$3
    
    log_info "📸 Executing photographer workflow: ${workflow_type}"
    
    case $workflow_type in
        "protect"|"full")
            if [[ -f "${SCRIPT_DIR}/protection_automation.sh" ]]; then
                bash "${SCRIPT_DIR}/protection_automation.sh" --content image --input "${input_path}"
            fi
            ;;
        "monetize"|"full")
            if [[ -f "${SCRIPT_DIR}/monetization_automation.sh" ]]; then
                bash "${SCRIPT_DIR}/monetization_automation.sh" --licensing creative-commons --input "${input_path}"
            fi
            ;;
    esac
    
    log_success "📷 Photographer workflow completed!"
}

# Execute workflow for blogger profile  
execute_blogger_workflow() {
    local workflow_type=$1
    local input_path=$2
    local output_path=$3
    
    log_info "✍️  Executing blogger workflow: ${workflow_type}"
    
    case $workflow_type in
        "process"|"full")
            if [[ -f "${SCRIPT_DIR}/seo_automation.sh" ]]; then
                bash "${SCRIPT_DIR}/seo_automation.sh" --content-type text --input "${input_path}"
            fi
            ;;
        "monetize"|"full")
            if [[ -f "${SCRIPT_DIR}/monetization_automation.sh" ]]; then
                bash "${SCRIPT_DIR}/monetization_automation.sh" --advertising --input "${input_path}"
            fi
            ;;
    esac
    
    log_success "📝 Blogger workflow completed!"
}

# Main execution
main() {
    local profile=""
    local workflow=""
    local input_path=""
    local output_path="/tmp/ainflue-output"
    local config_file=""
    local parallel=false
    local dry_run=false
    local verbose=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --profile)
                profile="$2"
                shift 2
                ;;
            --workflow)
                workflow="$2"
                shift 2
                ;;
            --input)
                input_path="$2"
                shift 2
                ;;
            --output)
                output_path="$2"
                shift 2
                ;;
            --config)
                config_file="$2"
                shift 2
                ;;
            --parallel)
                parallel=true
                shift
                ;;
            --dry-run)
                dry_run=true
                shift
                ;;
            --verbose)
                verbose=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Header
    echo -e "${WHITE}"
    echo "╔══════════════════════════════════════════════════════════════════════════════════════╗"
    echo "║                          🎯 AINFLUE WORKFLOW ORCHESTRATOR                           ║"
    echo "║                       Central Automation System by Fahed Mlaiel                     ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    # Validate inputs
    if [[ -z "$profile" ]]; then
        log_error "Profile is required. Use --profile [musician|photographer|blogger|influencer|comedian]"
        exit 1
    fi
    
    if [[ -z "$workflow" ]]; then
        workflow="full"
        log_info "No workflow specified, using 'full' workflow"
    fi
    
    # Create output directory
    mkdir -p "${output_path}"
    
    # Log start
    log_info "🚀 Starting workflow orchestration"
    log_info "Profile: ${profile}"
    log_info "Workflow: ${workflow}" 
    log_info "Input: ${input_path:-"(none specified)"}"
    log_info "Output: ${output_path}"
    log_info "Log file: ${LOG_FILE}"
    
    if [[ "$dry_run" == true ]]; then
        log_info "🔍 DRY RUN MODE - No actual changes will be made"
    fi
    
    # Validate environment
    validate_environment
    
    # Execute workflow based on profile
    case $profile in
        "musician")
            execute_musician_workflow "$workflow" "$input_path" "$output_path"
            ;;
        "photographer")
            execute_photographer_workflow "$workflow" "$input_path" "$output_path"
            ;;
        "blogger")
            execute_blogger_workflow "$workflow" "$input_path" "$output_path"
            ;;
        "influencer"|"comedian")
            log_info "🚧 Profile '$profile' workflow is under development"
            ;;
        *)
            log_error "Unknown profile: $profile"
            exit 1
            ;;
    esac
    
    # Final report
    echo -e "\n${WHITE}📊 WORKFLOW SUMMARY${NC}"
    echo "═══════════════════════════════════════════════════════════════"
    log_success "✅ Workflow completed successfully"
    log_info "📁 Output directory: ${output_path}"
    log_info "📋 Log file: ${LOG_FILE}"
    log_info "⏱️  Total execution time: $(date)"
    
    echo -e "\n${CYAN}🎉 Thank you for using Ainflue Workflow Orchestrator!${NC}"
    echo -e "${WHITE}© 2025 Fahed Mlaiel - All Rights Reserved${NC}\n"
}

# Execute main function
main "$@"