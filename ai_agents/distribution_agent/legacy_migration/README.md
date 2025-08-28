"""
Legacy Migration Helper - Transition Guide

This directory contains legacy files from the old distribution_agent architecture.
These files are preserved for migration purposes and will be gradually integrated
into the new ultra-advanced architecture.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

MIGRATION PLAN:
==============

1. PLATFORM ADAPTERS (PRIORITY: HIGH)
   - Files: *_adapter.py (discord, facebook, instagram, linkedin, pinterest, spotify, tiktok, twitch, twitter, youtube)
   - Action: Migrate to new adapters/ directory using BasePlatformAdapter interface
   - Timeline: Immediate

2. PLATFORM REGISTRY (PRIORITY: HIGH)  
   - Files: platform_registry.py
   - Action: Integrate with new core/distribution_engine.py platform management
   - Timeline: Next sprint

3. ROUTING & OPTIMIZATION (PRIORITY: MEDIUM)
   - Files: platform_router.py, content_optimizer.py
   - Action: Integrate with intelligence/intelligence_engine.py
   - Timeline: Week 2

4. ANALYTICS & MODELS (PRIORITY: MEDIUM)
   - Files: analytics_collector.py, distribution_models.py, distribution_schemas.py
   - Action: Merge with new core architecture
   - Timeline: Week 3

5. SCHEDULING (PRIORITY: LOW)
   - Files: distribution_scheduler.py
   - Action: Integrate with core/orchestrator.py
   - Timeline: Week 4

COMPATIBILITY NOTES:
===================
- All legacy files use old naming conventions
- May contain deprecated dependencies
- Some functionality already implemented in new architecture
- Preserve useful business logic during migration

INTEGRATION STRATEGY:
====================
1. Extract reusable components
2. Adapt to new interfaces
3. Update imports and dependencies  
4. Maintain backward compatibility
5. Test thoroughly before removal

For migration assistance, contact: mlaiel@live.de
"""
