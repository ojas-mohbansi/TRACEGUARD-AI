# TraceGuard AI - SaaS Roadmap & Monetization Strategy

## 1. Subscription Tier Model

TraceGuard AI is architected for extensible future monetization through configurable workspace subscription tiers:

| Feature / Quota | Free Community | Professional | Team Enterprise |
|-----------------|:--------------:|:------------:|:---------------:|
| Monthly Price | $0 / month | $49 / month | $199 / month |
| Active Workspace Members | 1 user | 5 users | Unlimited |
| Daily Traffic Simulations | 50 runs | 500 runs | Unlimited |
| Uploaded Datasets Quota | 5 datasets | 50 datasets | Unlimited |
| Max Upload File Size | 10 MB | 100 MB | 1 GB |
| Detection Engines | All 3 (FSM, ML, Hybrid) | All 3 | All 3 + Custom Models |
| Alert History Retention | 7 days | 90 days | 365 days + S3 export |
| Real-time WebSocket Monitoring | Standard | Priority channel | Dedicated socket pool |
| Role-Based Access Control (RBAC) | Viewer/Owner | Full 4-Tier RBAC | Full 4-Tier + SAML/SSO |

---

## 2. Technical Roadmap for Future Phases

### Phase 4: Monetization Integration
- Stripe Billing integration via webhook listeners (`/api/billing/webhook`).
- Customer portal for invoice retrieval and card management.
- Dynamic rate-limiting and soft-quota notifications via in-app banners.

### Phase 5: High-Throughput Packet Ingestion
- Real PCAP upload and parsing using Scapy / DPDK.
- Kafka / RabbitMQ message bus for decoupling high-rate ingress traffic from inference workers.
- Redis caching for live state-machine transition counters.

### Phase 6: Distributed Detection Swarms
- Clustered Isolation Forest inference across worker nodes.
- Custom user-defined FSM state machines via YAML/JSON configuration.
