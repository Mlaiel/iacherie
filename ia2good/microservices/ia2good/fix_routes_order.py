#!/usr/bin/env python3
"""Script to reorder volunteer routes to fix FastAPI route conflicts"""

# Read the file
with open('/workspaces/ia2good/microservices/ia2good/api/routes/volunteers.py', 'r') as f:
    lines = f.readlines()

# Split file into sections
header = lines[0:197]  # Lines 1-197 (up to before GET /volunteers/{id})
specific_routes_me_profile = lines[400:477]  # Lines 401-477 (GET /volunteers/me/profile)
specific_routes_me_stats = lines[477:530]  # Lines 478-530 (GET /volunteers/me/stats)
specific_routes_nearby = lines[530:]  # Lines 531-end (GET /volunteers/nearby)
generic_route_and_others = lines[197:400]  # Lines 198-400 (GET/PUT /volunteers/{id} and others)

# Reorder: header + specific routes (nearby, me/*) + generic routes ({id})
reordered = (
    header + 
    ["\n"] +
    specific_routes_nearby +
    ["\n"] +
    specific_routes_me_profile +
    ["\n"] +
    specific_routes_me_stats +
    ["\n"] +
    generic_route_and_others
)

# Write back
with open('/workspaces/ia2good/microservices/ia2good/api/routes/volunteers.py', 'w') as f:
    f.writelines(reordered)

print("✅ Routes reordered successfully!")
print("New order:")
print("  1. POST /volunteers")
print("  2. GET /volunteers")
print("  3. GET /volunteers/nearby")
print("  4. GET /volunteers/me/profile")
print("  5. GET /volunteers/me/stats")
print("  6. GET /volunteers/{volunteer_id}")
print("  7. PUT /volunteers/{volunteer_id}")
print("  8. PUT /volunteers/{volunteer_id}/availability")
print("  9. POST /volunteers/{volunteer_id}/verify")
