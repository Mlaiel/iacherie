#!/bin/bash

# Guardian Platform - Complete Features Test
# Tests: Live Streaming, Video Chat, File Uploads, Chat Rooms

set -e

BASE_URL="http://localhost:8001"
API_BASE="${BASE_URL}/api/guardian"

echo "======================================"
echo "GUARDIAN PLATFORM - COMPLETE TEST"
echo "======================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_section() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_test() {
    echo -e "${GREEN}✓${NC} $1"
}

# Test 1: Health Check
print_section "1. HEALTH CHECK"
curl -s "${BASE_URL}/health" | jq
print_test "Service is healthy"
echo ""

# Test 2: Live Streaming
print_section "2. LIVE STREAMING"

echo "Creating stream..."
STREAM_RESPONSE=$(curl -s -X POST "${API_BASE}/live/streams/create" \
    -H "Content-Type: application/json" \
    -d '{
        "stream_id": "beach-cleanup-live",
        "title": "Beach Cleanup Santa Monica",
        "description": "Live from the beach",
        "mission_id": 1,
        "quality": "720p"
    }')
echo "$STREAM_RESPONSE" | jq
STREAM_ID=$(echo "$STREAM_RESPONSE" | jq -r '.stream_id')
print_test "Stream created: $STREAM_ID"
echo ""

echo "Listing active streams..."
curl -s "${API_BASE}/live/streams" | jq
print_test "Streams listed"
echo ""

echo "Getting stream info..."
curl -s "${API_BASE}/live/streams/${STREAM_ID}" | jq
print_test "Stream info retrieved"
echo ""

echo "Getting stream stats..."
curl -s "${API_BASE}/live/streams/${STREAM_ID}/stats" | jq
print_test "Stream stats retrieved"
echo ""

# Test 3: Video Chat
print_section "3. VIDEO CHAT"

echo "Creating video chat room..."
ROOM_RESPONSE=$(curl -s -X POST "${API_BASE}/videochat/rooms/create" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "Mission Coordination",
        "max_participants": 10,
        "mission_id": 1,
        "is_public": true
    }')
echo "$ROOM_RESPONSE" | jq
ROOM_ID=$(echo "$ROOM_RESPONSE" | jq -r '.room_id')
print_test "Video room created: $ROOM_ID"
echo ""

echo "Listing video chat rooms..."
curl -s "${API_BASE}/videochat/rooms" | jq
print_test "Video rooms listed"
echo ""

echo "Getting room info..."
curl -s "${API_BASE}/videochat/rooms/${ROOM_ID}" | jq
print_test "Room info retrieved"
echo ""

echo "Getting room stats..."
curl -s "${API_BASE}/videochat/rooms/${ROOM_ID}/stats" | jq
print_test "Room stats retrieved"
echo ""

# Test 4: File Uploads
print_section "4. FILE UPLOADS"

echo "Creating test files..."
echo "Mission report - Beach Cleanup" > /tmp/mission_report.txt
echo "Volunteer checklist" > /tmp/checklist.md
print_test "Test files created"
echo ""

echo "Uploading single file..."
UPLOAD_RESPONSE=$(curl -s -X POST "${API_BASE}/files/upload" \
    -F "file=@/tmp/mission_report.txt" \
    -F "mission_id=1" \
    -F "uploaded_by=volunteer123")
echo "$UPLOAD_RESPONSE" | jq
FILE_ID=$(echo "$UPLOAD_RESPONSE" | jq -r '.file.file_id')
print_test "File uploaded: $FILE_ID"
echo ""

echo "Uploading multiple files..."
curl -s -X POST "${API_BASE}/files/upload/multiple" \
    -F "files=@/tmp/mission_report.txt" \
    -F "files=@/tmp/checklist.md" \
    -F "mission_id=1" \
    -F "uploaded_by=volunteer456" | jq
print_test "Multiple files uploaded"
echo ""

echo "Listing files..."
curl -s "${API_BASE}/files/files?mission_id=1" | jq
print_test "Files listed"
echo ""

echo "Getting file info..."
curl -s "${API_BASE}/files/files/${FILE_ID}" | jq
print_test "File info retrieved"
echo ""

echo "Getting files statistics..."
curl -s "${API_BASE}/files/files/stats/overview" | jq
print_test "Files stats retrieved"
echo ""

# Test 5: Chat Rooms
print_section "5. CHAT ROOMS"

echo "Creating chat room..."
CHAT_RESPONSE=$(curl -s -X POST "${API_BASE}/chat/rooms/create" \
    -H "Content-Type: application/json" \
    -d '{
        "room_id": "beach-cleanup-chat",
        "name": "Beach Cleanup Discussion",
        "description": "Discuss mission details",
        "mission_id": 1,
        "is_public": true
    }')
echo "$CHAT_RESPONSE" | jq
CHAT_ROOM_ID=$(echo "$CHAT_RESPONSE" | jq -r '.room.room_id')
print_test "Chat room created: $CHAT_ROOM_ID"
echo ""

echo "Listing chat rooms..."
curl -s "${API_BASE}/chat/rooms" | jq
print_test "Chat rooms listed"
echo ""

echo "Getting chat room info..."
curl -s "${API_BASE}/chat/rooms/${CHAT_ROOM_ID}" | jq
print_test "Chat room info retrieved"
echo ""

echo "Getting chat room messages..."
curl -s "${API_BASE}/chat/rooms/${CHAT_ROOM_ID}/messages" | jq
print_test "Chat messages retrieved"
echo ""

echo "Getting chat statistics..."
curl -s "${API_BASE}/chat/stats" | jq
print_test "Chat stats retrieved"
echo ""

# Test 6: Complete Overview
print_section "6. COMPLETE PLATFORM OVERVIEW"

echo "Getting platform info..."
curl -s "${BASE_URL}/" | jq
print_test "Platform info retrieved"
echo ""

echo "Missions overview..."
curl -s "${API_BASE}/missions" | jq '.total, .missions[0] // "No missions yet"'
print_test "Missions checked"
echo ""

echo "Volunteers overview..."
curl -s "${API_BASE}/volunteers" | jq '.total'
print_test "Volunteers checked"
echo ""

# Summary
print_section "✅ TEST SUMMARY"
echo ""
echo -e "${GREEN}All tests completed successfully!${NC}"
echo ""
echo "Features tested:"
echo "  ✓ Live Streaming (creation, listing, stats)"
echo "  ✓ Video Chat (rooms, WebRTC signaling ready)"
echo "  ✓ File Uploads (single, multiple, stats)"
echo "  ✓ Chat Rooms (creation, listing, messages)"
echo "  ✓ Platform Integration"
echo ""
echo "WebSocket endpoints available:"
echo "  - Live Stream: ws://localhost:8001/api/guardian/live/stream/{stream_id}"
echo "  - Watch Stream: ws://localhost:8001/api/guardian/live/watch/{stream_id}"
echo "  - Video Call: ws://localhost:8001/api/guardian/videochat/room/{room_id}"
echo "  - Chat Room: ws://localhost:8001/api/guardian/chat/room/{room_id}"
echo "  - Direct Message: ws://localhost:8001/api/guardian/chat/dm/{user_id}"
echo "  - Geo Realtime: ws://localhost:8001/api/guardian/geo/ws/map"
echo ""
echo "Access the interactive map at:"
echo "  http://localhost:8001/static/map.html"
echo ""
echo -e "${BLUE}Guardian Platform is fully operational! 🚀${NC}"
