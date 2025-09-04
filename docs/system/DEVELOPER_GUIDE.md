# Developer Guide — Système 46 Agents IA (Qualité Industrielle)

**Propriétaire :** Fahed Mlaiel <mlaiel@live.de>  
**Version :** 2.0.0 - Guide Développeur Complet  
**Date :** 13 Août 2025  

## ⚠️ PROTECTION LÉGALE STRICTE

**Cette architecture et tous les concepts sont la propriété intellectuelle exclusive de Fahed Mlaiel. Toute utilisation, réplication ou analyse non autorisée du code, de l'architecture ou du concept produit est strictement interdite et sera poursuivie en justice.**

**Pour licences et collaborations : mlaiel@live.de**

---

## 🎯 1) Portée et Objectifs - Système 46 Agents

Ce module fournit un système d'agents IA de qualité industrielle pour la plateforme IA-Influencer-Agent, orchestrant la chaîne de valeur complète des créateurs :

**Upload → Traitement IA → Protection Droits → SEO → Matching Collaboration → Distribution Multi-Plateformes → Monétisation**

### Objectifs de Conception
- **Fiabilité et sécurité** par défaut (timeouts, limites, circuit breaker, arrêt gracieux)
- **Observabilité prioritaire** (métriques Prometheus, snapshots santé)  
- **Sécurité et conformité** (chiffrement, isolation tenant, gestion droits)
- **Élastique et efficace** (pooling, scaling dynamique, conscience ressources)
- **Extensible et maintenable** (contrats clairs, câblage basé registre)

## 2) Core contracts (inputs/outputs)
- AgentRequest (backend/ai_agents/base.py)
  - Fields: request_id, user_id, tenant_id, action, data, metadata, priority, timeout, headers, source_ip, user_agent
- AgentResponse (backend/ai_agents/base.py)
  - Fields: success, request_id, data, message, error, error_code, warnings, timestamp, agent_type, agent_version, execution_time, resource_usage, trace_id

Validation
- Requests must define action
- Tenant validation hook in BaseAgent._validate_tenant_access
- Data validation per agent via _validate_request_data

## 3) Architecture overview
- Base Agent: BaseAgent (metrics, limits, circuit breaker, async, security hooks)
- Orchestration: AgentManager (pools, routing, priority, load‑balancing, health, dynamic scaling, recovery)
- Business pipeline: BusinessWorkflowOrchestrator (end‑to‑end flow coordination)
- Public API: backend/ai_agents/index.py (bootstrap/shutdown/route/workflow)
- Core agents: content, protection, seo, collaboration, distribution, monetization
- Advanced protection: fingerprinting (A/V/I/T), similarity, watermarking, web monitoring

Data flow
- App calls bootstrap() → pools registered → agents initialized
- Requests routed by agent_manager.process_request() according to rules or default action mapping
- Workflow orchestrator executes multi-stage pipeline and delegates to agents

## 4) Configuration and environment
Configuration is sourced from core.config.settings. Ensure the following environment variables are set in runtime environments:
- Redis
  - REDIS_HOST (string)
  - REDIS_PORT (int)
  - REDIS_PASSWORD (string, optional)
- Database
  - Managed by core.database.get_db_session; configure per your DB layer (DSN/URL/env)
- Agent limits (per-agent config dict)
  - max_requests_per_minute (int)
  - circuit_breaker_threshold (int)
  - circuit_breaker_recovery (seconds)
  - max_memory_mb (int)
- Pool strategies (via AgentManager or during pool registration)
  - min_instances, max_instances, strategy (fixed_size | dynamic_scaling | priority_based)

Security of secrets
- Provide secrets via environment variables or secret stores; never hard-code
- Prefer runtime-injected configuration in container orchestration

## 5) Lifecycle: bootstrap and shutdown
High-level API (index.py)
```python
from IA_Influencer_Agent.backend.ai_agents.index import bootstrap, shutdown
ok = await bootstrap()
# ... serve app ...
await shutdown()
```

Agents are initialized lazily through AgentManager.pool registration populated by initialize_agent_system(). Shutdown drains active requests, closes DB/Redis.

## 6) Request routing and actions
- Custom routing rules can be added via AgentManager.add_routing_rule(condition, target_agent_type, priority_boost)
- Default action→agent mapping is implemented in AgentManager._get_default_agent_type() (e.g. analyze_content → content_agent; generate_fingerprint → protection_agent)

Example
```python
from IA_Influencer_Agent.backend.ai_agents import agent_manager
agent_manager.add_routing_rule(
    condition="action == 'distribute_content' and 'spotify' in data.get('platforms', [])",
    target_agent_type='distribution_agent',
    priority_boost=1,
)
```

## 7) Pooling and dynamic scaling
- AgentPool per agent_type: min_instances, max_instances, strategy
- Dynamic scaling logic monitors CPU/memory load and active requests to scale up/down within bounds
- Recovery flow replaces unhealthy agents when possible

Tuning tips
- Increase min_instances for low-latency hot paths
- Cap max_instances to control resource usage
- Use priority boosts for critical paths

## 8) Observability
Prometheus metrics (BaseAgent)
- agent_requests_total{agent_type,status}
- agent_request_duration_seconds{agent_type}
- agent_active_connections{agent_type}

Health
- Agent.get_health_status() returns status, uptime, metrics, resource usage
- AgentManager.get_system_status() aggregates pools/agents and request stats

Optional integrations
- Export metrics endpoint via your web framework
- Optionally add OpenTelemetry traces around agent processing

## 9) Error handling, timeouts, limits
- Request-level timeouts via AgentRequest.timeout
- Rate limiting per client (user_id/source_ip) in BaseAgent._check_rate_limits
- Circuit breaker blocks processing on repeated failures until recovery timeout
- Resource guards raise ResourceLimitError on high CPU/memory

Operational guidance
- Keep timeouts realistic to avoid zombie workloads
- Monitor error_rate in AgentMetrics

## 10) Security and compliance
- Tenant access validation hook: BaseAgent._validate_tenant_access
- Encryption utilities: security layer (ContentEncryption)
- Rights management and DMCA workflows: protection agent stack
- Auditability: use logs + metrics for forensic insight
- GDPR/readiness: respect tenant boundaries and data minimization

Hard rules
- Professional English naming across public APIs and code
- Never embed secrets in code

## 11) Persistence and caching
- Database sessions: async retrieval via core.database.get_db_session
- Redis: async client (redis.asyncio) used in BaseAgent for caching/queues
- Always close sessions/clients on shutdown

## 12) Extensibility: adding a new agent
1) Create subpackage backend/ai_agents/<your_agent>/ with __init__.py and implementation class extending BaseAgent
2) Register in AGENT_REGISTRY within backend/ai_agents/__init__.py
3) Optionally provide a specialized manager and register it in MANAGER_REGISTRY
4) Expose any public helpers in your subpackage __all__

Minimal example (synchronous shape, real logic required):
```python
# backend/ai_agents/my_agent/my_agent.py
from ..base import BaseAgent, AgentRequest, AgentResponse

class MyAgent(BaseAgent):
    async def _load_models_and_resources(self):
        # load models/resources
        return
    def get_required_config_keys(self):
        return []
    async def process(self, request: AgentRequest) -> AgentResponse:
        # implement business logic
        return AgentResponse(success=True, data={"ok": True})
```

Register
```python
# backend/ai_agents/__init__.py
from .my_agent.my_agent import MyAgent
AGENT_REGISTRY['my_agent'] = MyAgent
```

## 13) Deployment reference
Containers
- Provide REDIS_* and DB settings via environment
- Health probes should hit the service route that reflects AgentManager.get_system_status()
- Use resource requests/limits appropriate to expected pool sizes

Kubernetes (guidelines)
- Horizontal scaling at the pod level complements internal agent pools
- Configure liveness/readiness probes and Prometheus scraping annotations
- Externalize secrets via Secrets/ConfigMaps

## 14) Performance tuning
- Increase min_instances for hot traffic; reduce request timeout for short operations
- Prefer batch processing for heavy workloads when feasible
- Ensure Redis and DB pools are sized to avoid connection thrash
- Consider CPU pinning and memory limits aligned with expected concurrency

## 15) Runbooks (operations)
Incident: surge latency
- Check agent_active_connections and average_response_time
- Scale up pools or increase min_instances

Incident: elevated error_rate
- Inspect circuit breaker status; review recent exceptions and resource usage
- Trigger agent recovery by restarting the pool or node

Incident: memory pressure
- Lower max_instances; increase memory limit or optimize processing footprint

## 16) Versioning and releases
- Follow semantic versioning per agent when changing contracts/behavior
- Document changes at module level (CHANGELOG in subpackages where applicable)

## 17) Legal/IP notice
This module, its architecture, and the concept are exclusive IP of Fahed Mlaiel. Any unauthorized use, copying, distribution, reverse engineering, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing.

## 18) Quick references
- Public API: backend/ai_agents/index.py
- Orchestrator: backend/ai_agents/content_agent/business_workflow.py
- Manager: backend/ai_agents/agent_manager.py
- Base contracts: backend/ai_agents/base.py
