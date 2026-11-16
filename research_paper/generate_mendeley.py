#!/usr/bin/env python3
"""
NexusOps Mendeley & Reference Library Generator
Generates:
1. references.bib (BibTeX format with full metadata and Mendeley annotations)
2. references.ris (Universal RIS format for 1-click import into Mendeley)
3. MENDELEY_LIBRARY.md (Annotated bibliography and thematic literature guide)
"""

import os
import json

import os
import json

entries = [
    {
        "key": "panko1998",
        "type": "article",
        "ris_type": "JOUR",
        "author": "Panko, Raymond R.",
        "title": "What We Know About Spreadsheet Errors",
        "journal": "Journal of End User Computing",
        "year": "1998",
        "volume": "10",
        "number": "2",
        "pages": "15--21",
        "doi": "10.4018/joeuc.1998040102",
        "url": "https://doi.org/10.4018/joeuc.1998040102",
        "category": "Enterprise SaaS Vulnerabilities & Human Error",
        "abstract": "This paper reviews empirical research on errors in spreadsheets. In field audits of operational spreadsheets, an average of 88% of 102 spreadsheets contained errors. Human error rates in formula creation and data entry consistently fall between 1% and 5% across diverse operational contexts.",
        "keywords": "human error, software quality, operational spreadsheets, risk assessment, error rates",
        "highlights": "Pioneered empirical analysis of human error rates in software-like data configurations, demonstrating an unavoidable 1% to 5% baseline developer omission rate. In NexusOps, this baseline provides the empirical justification that relying exclusively on developers to remember tenant WHERE clauses will inevitably lead to cross-tenant data leaks."
    },
    {
        "key": "powell2009",
        "type": "article",
        "ris_type": "JOUR",
        "author": "Powell, Stephen G. and Baker, Kenneth R. and Lawson, Barry",
        "title": "Errors in Operational Spreadsheets",
        "journal": "Journal of Organizational and End User Computing",
        "year": "2009",
        "volume": "21",
        "number": "3",
        "pages": "24--36",
        "doi": "10.4018/joeuc.2009070102",
        "url": "https://doi.org/10.4018/joeuc.2009070102",
        "category": "Enterprise SaaS Vulnerabilities & Human Error",
        "abstract": "We report the results of a comprehensive audit of operational spreadsheets in corporate environments. The study analyzes error rates, error categories, and financial materiality, finding that informal testing and code review fail to catch over half of logic errors.",
        "keywords": "spreadsheet audit, software inspection, operational risk, developer oversight, defect density",
        "highlights": "Demonstrates that manual inspection and peer code review alone fail to catch systematic omissions in repetitive operational structures. Cited in NexusOps to substantiate that manual peer review is mathematically incapable of preventing cross-tenant filter omissions over sustained agile development cycles."
    },
    {
        "key": "chong2006",
        "type": "techreport",
        "ris_type": "RPRT",
        "author": "Chong, Frederick and Carraro, Gianpaolo and Wolter, Roger",
        "title": "Multi-Tenant Data Architecture",
        "institution": "Microsoft Corporation",
        "journal": "MSDN Library Whitepaper",
        "year": "2006",
        "url": "https://learn.microsoft.com/en-us/previous-versions/msp-n-p/aa479086(v=msdn.10)",
        "category": "Multi-Tenancy Architecture & Schema Models",
        "abstract": "This seminal architectural guide defines the four SaaS multi-tenancy maturity levels. It contrasts Separate Database (isolated silos), Separate Schema (schema-per-tenant), and Shared Database / Shared Schema (pooled) models, analyzing the tradeoffs between cost, consolidation density, isolation strength, and schema maintenance.",
        "keywords": "multi-tenancy, SaaS architecture, database partitioning, shared schema, resource consolidation",
        "highlights": "Established the canonical three-tier database multi-tenancy taxonomy: Separate Database, Separate Schema, and Shared Schema. NexusOps builds upon Chong's pooled shared-schema paradigm to deliver maximum tenant density and hardware amortization while solving the isolation vulnerabilities identified in this foundational paper."
    },
    {
        "key": "aulbach2008",
        "type": "inproceedings",
        "ris_type": "CONF",
        "author": "Aulbach, Stefan and Grust, Torsten and Jacobs, Dean and Kemper, Alfons and Rittinger, Jan",
        "title": "Multi-Tenant Databases for Software as a Service: Schema-Mapping Techniques",
        "booktitle": "Proceedings of the 2008 ACM SIGMOD International Conference on Management of Data",
        "year": "2008",
        "pages": "1195--1206",
        "doi": "10.1145/1376616.1376736",
        "url": "https://doi.org/10.1145/1376616.1376736",
        "category": "Multi-Tenancy Architecture & Schema Models",
        "abstract": "In multi-tenant SaaS, hosting tenants on a shared relational database minimizes operating costs. This paper proposes and benchmarks schema-mapping techniques including Universal Tables, Chunk Folding, and Pivot Tables. Chunk Folding decomposes logical tenant tables into chunks mapped to physical relational tables, achieving high tenant density and low query overhead.",
        "keywords": "schema mapping, chunk folding, shared database, multi-tenancy, relational consolidation",
        "highlights": "Introduced Chunk Folding and demonstrated that shared-table relational consolidation achieves up to 10x higher tenant density per gigabyte of RAM compared to isolated schemas. NexusOps adopts Aulbach's shared-table model but replaces complex chunk-folding indirection with composite B-tree primary keys and native PostgreSQL Row-Level Security."
    },
    {
        "key": "armbrust2010",
        "type": "article",
        "ris_type": "JOUR",
        "author": "Armbrust, Michael and Fox, Armando and Griffith, Rean and Joseph, Anthony D. and Katz, Randy and Konwinski, Andy and Lee, Gunho and Patterson, David and Rabkin, Ariel and Stoica, Ion and Zaharia, Matei",
        "title": "A View of Cloud Computing",
        "journal": "Communications of the ACM",
        "year": "2010",
        "volume": "53",
        "number": "4",
        "pages": "50--58",
        "doi": "10.1145/1721654.1721672",
        "url": "https://doi.org/10.1145/1721654.1721672",
        "category": "Cloud Economics & Resource Consolidation",
        "abstract": "This landmark paper defines cloud computing and identifies the economic and technical drivers behind the shift to cloud infrastructure. It highlights the elasticity of resources, statistical multiplexing across workloads, and the imperative for multi-tenant resource sharing to minimize operational expenditure.",
        "keywords": "cloud computing, statistical multiplexing, elasticity, resource sharing, multi-tenancy",
        "highlights": "Outlined the core economic imperative of cloud computing: statistical multiplexing of hardware across multiple tenants is essential to achieve economies of scale. NexusOps directly addresses Armbrust's challenge of securely sharing underlying database instances without allowing one tenant to breach another's operational boundary."
    },
    {
        "key": "owasp2021",
        "type": "misc",
        "ris_type": "ELEC",
        "author": "{OWASP Foundation}",
        "title": "OWASP Top 10:2021 Web Application Security Risks",
        "year": "2021",
        "url": "https://owasp.org/Top10/",
        "category": "Enterprise SaaS Vulnerabilities & Threat Landscape",
        "abstract": "The OWASP Top 10:2021 represents the consensus standard for web application security awareness. Category A01:2021 (Broken Access Control) advanced to the number-one position, with 94% of tested applications exhibiting some form of broken access control, leading to unauthorized cross-tenant data exposure.",
        "keywords": "broken access control, web security, OWASP Top 10, application security, vulnerability assessment",
        "highlights": "Designates Broken Access Control (A01:2021) as the single most critical security threat to modern web and cloud applications. NexusOps provides a formal structural remedy by ensuring that even if application-level access control fails, the database engine enforces isolation via forced RLS."
    },
    {
        "key": "owaspapi2023",
        "type": "misc",
        "ris_type": "ELEC",
        "author": "{OWASP Foundation}",
        "title": "OWASP API Security Top 10:2023",
        "year": "2023",
        "url": "https://owasp.org/www-project-api-security/",
        "category": "Enterprise SaaS Vulnerabilities & Threat Landscape",
        "abstract": "The OWASP API Security Top 10 focuses on the vulnerabilities inherent in microservice and REST APIs. API1:2023 (Broken Object Level Authorization / BOLA) remains the most severe and prevalent vulnerability, where attackers substitute record identifiers in HTTP requests to access data belonging to other tenants.",
        "keywords": "API security, BOLA, IDOR, authorization bypass, object-level authorization",
        "highlights": "Identifies Broken Object Level Authorization (BOLA/IDOR) as the primary attack vector against RESTful APIs. NexusOps eliminates BOLA vulnerabilities at the architectural level: even if an attacker manipulates record IDs in an HTTP parameter, PostgreSQL's RLS engine drops or rejects the query because the tenant GUC does not match."
    },
    {
        "key": "verizon2023",
        "type": "techreport",
        "ris_type": "RPRT",
        "author": "{Verizon}",
        "title": "2023 Data Breach Investigations Report (DBIR)",
        "institution": "Verizon Business",
        "year": "2023",
        "url": "https://www.verizon.com/business/resources/reports/dbir/",
        "category": "Enterprise SaaS Vulnerabilities & Threat Landscape",
        "abstract": "Analyzing 16,312 security incidents and 5,199 confirmed breaches across the globe, the 2023 DBIR reveals that 74% of all breaches involve the human element, including errors, privilege abuse, and misconfigurations. Internal misconfigurations represent a rapidly accelerating vector in cloud-hosted multi-tenant databases.",
        "keywords": "data breach, DBIR, human factor, cloud misconfiguration, incident response",
        "highlights": "Empirically established that 74% of enterprise data breaches stem from human error and configuration drift. Cited in NexusOps to demonstrate why software engineering workflows require automated CI/CD AST guardrails rather than manual developer diligence."
    },
    {
        "key": "ibm2023",
        "type": "techreport",
        "ris_type": "RPRT",
        "author": "{IBM Security and Ponemon Institute}",
        "title": "Cost of a Data Breach Report 2023",
        "institution": "IBM Security",
        "year": "2023",
        "url": "https://www.ibm.com/reports/data-breach",
        "category": "Enterprise SaaS Vulnerabilities & Threat Landscape",
        "abstract": "The 2023 report establishes that the global average cost of a data breach reached $4.45 million, an all-time high. Breaches involving shared cloud environments required an average of 292 days to identify and contain, 28 days longer than on-premises incidents.",
        "keywords": "cost of breach, cloud data breach, financial loss, mean time to identify, Ponemon",
        "highlights": "Quantifies the severe financial impact of multi-tenant cloud breaches ($4.45M average cost). Emphasizes that multi-tenant database cross-leaks are exceptionally difficult to detect post-hoc, validating NexusOps's proactive fail-closed kernel architecture."
    },
    {
        "key": "saltzer1975",
        "type": "article",
        "ris_type": "JOUR",
        "author": "Saltzer, Jerome H. and Schroeder, Michael D.",
        "title": "The Protection of Information in Computer Systems",
        "journal": "Proceedings of the IEEE",
        "year": "1975",
        "volume": "63",
        "number": "9",
        "pages": "1278--1308",
        "doi": "10.1109/PROC.1975.9939",
        "url": "https://doi.org/10.1109/PROC.1975.9939",
        "category": "Database Security & Access Control Foundations",
        "abstract": "This classic paper establishes the foundational principles of computer security: Economy of Mechanism, Fail-Safe Defaults, Complete Mediation, Open Design, Separation of Privilege, Least Privilege, Least Common Mechanism, and Psychological Acceptability. It outlines access control matrix models and capabilities.",
        "keywords": "computer security, access control, fail-safe defaults, complete mediation, defense in depth",
        "highlights": "Articulated the foundational principles of computer security: Fail-Safe Defaults (fail-closed) and Complete Mediation. NexusOps directly translates Saltzer-Schroeder to multi-tenant databases: connections without an active tenant context default to an empty visibility set (fail-closed), and RLS mediates every query."
    },
    {
        "key": "aws2020",
        "type": "techreport",
        "ris_type": "RPRT",
        "author": "{Amazon Web Services}",
        "title": "SaaS Tenant Isolation Strategies: Isolating Resources in a Multi-Tenant Environment",
        "institution": "Amazon Web Services",
        "year": "2020",
        "url": "https://docs.aws.amazon.com/whitepapers/latest/saas-tenant-isolation-strategies/saas-tenant-isolation-strategies.html",
        "category": "Multi-Tenancy Architecture & Schema Models",
        "abstract": "This AWS Architecture Center whitepaper outlines prescriptive strategies for tenant isolation across SaaS environments. It contrasts siloed isolation (dedicated infrastructure) with pooled isolation (shared infrastructure) and emphasizes that pooled models require programmatic isolation boundaries enforced at the persistence tier.",
        "keywords": "AWS, SaaS isolation, pooled architecture, tenant context, cloud architecture",
        "highlights": "Prescribes that pooled multi-tenant architectures must enforce programmatic, runtime isolation boundaries to eliminate developer single-point-of-failure reliance. Directly cited in NexusOps to benchmark our dual-layer isolation model against AWS enterprise cloud standards."
    },
    {
        "key": "postgresql17docs",
        "type": "manual",
        "ris_type": "COMP",
        "author": "{PostgreSQL Global Development Group}",
        "title": "PostgreSQL 17 Documentation: Row Security Policies",
        "organization": "PostgreSQL Global Development Group",
        "year": "2024",
        "url": "https://www.postgresql.org/docs/17/ddl-rowsecurity.html",
        "category": "Database Security & Access Control Foundations",
        "abstract": "Official technical reference documentation for PostgreSQL Row-Level Security (RLS). Details CREATE POLICY syntax, USING and WITH CHECK evaluation phases, ENABLE/FORCE ROW LEVEL SECURITY table alterations, and the interactions between superuser bypass and non-superuser application roles.",
        "keywords": "PostgreSQL 17, Row-Level Security, RLS, CREATE POLICY, FORCE ROW LEVEL SECURITY",
        "highlights": "The definitive specification for PostgreSQL RLS. In NexusOps, this serves as the engine reference for configuring `ENABLE ROW LEVEL SECURITY`, `FORCE ROW LEVEL SECURITY`, and applying `WITH CHECK` clauses to prevent cross-tenant writes."
    },
    {
        "key": "postgresql17notes",
        "type": "misc",
        "ris_type": "ELEC",
        "author": "{PostgreSQL Global Development Group}",
        "title": "PostgreSQL 17 Release Notes: Query Planning and Executor Improvements",
        "year": "2024",
        "url": "https://www.postgresql.org/docs/17/release-17.html",
        "category": "Database Security & Access Control Foundations",
        "abstract": "Release documentation covering core engine enhancements in PostgreSQL 17, specifically planner optimizations for parameterized and generic query plans, One-Time Filter index evaluation, B-tree search improvements, and stability optimizations in session settings.",
        "keywords": "PostgreSQL 17, query optimizer, One-Time Filter, STABLE functions, index scan",
        "highlights": "Documents query planner enhancements in PostgreSQL 17 that enable STABLE functions like `current_setting()` to be evaluated once at query startup rather than per-row, explaining why NexusOps achieves near-zero RLS execution overhead."
    },
    {
        "key": "bezemer2010",
        "type": "inproceedings",
        "ris_type": "CONF",
        "author": "Bezemer, Cor-Paul and Zaidman, Andy",
        "title": "Multi-Tenant SaaS Applications: Maintenance Dream or Nightmare?",
        "booktitle": "Proceedings of the Joint ERCIM Workshop on Software Evolution (EVOL) and International Workshop on Principles of Software Evolution (IWPSE)",
        "year": "2010",
        "pages": "88--92",
        "doi": "10.1145/1862372.1862393",
        "url": "https://doi.org/10.1145/1862372.1862393",
        "category": "Multi-Tenancy Architecture & Schema Models",
        "abstract": "This study analyzes software maintenance trade-offs in multi-tenant SaaS. While centralized updates and shared infrastructure drastically reduce administrative overhead, schema evolution and cross-tenant regressions pose significant risks that necessitate robust automated validation tooling.",
        "keywords": "software maintenance, SaaS evolution, multi-tenancy testing, regression risk, schema migration",
        "highlights": "Identified the operational paradox of SaaS: centralized upgrades eliminate client-side patching but create catastrophic single-point regression risks during schema migrations. Cited in NexusOps to motivate our build-time AST catalog guardrails."
    },
    {
        "key": "kabbedijk2015",
        "type": "article",
        "ris_type": "JOUR",
        "author": "Kabbedijk, Jaap and Bezemer, Cor-Paul and Jansen, Slinger and Zaidman, Andy",
        "title": "Defining Multi-Tenancy: A Systematic Mapping Study on the Academic and the Industrial Perspective",
        "journal": "Journal of Systems and Software",
        "year": "2015",
        "volume": "100",
        "pages": "139--148",
        "doi": "10.1016/j.jss.2014.10.034",
        "url": "https://doi.org/10.1016/j.jss.2014.10.034",
        "category": "Multi-Tenancy Architecture & Schema Models",
        "abstract": "Through a systematic mapping study of 74 academic papers and industrial frameworks, this paper reconciles divergent definitions of multi-tenancy. It defines a multi-dimensional taxonomy encompassing tenant variability, degree of resource sharing, and configuration independence.",
        "keywords": "multi-tenancy taxonomy, systematic mapping, SaaS classification, architectural sharing",
        "highlights": "Provides the definitive taxonomy categorizing multi-tenant software systems by degree of resource sharing across application, database, and hardware layers. NexusOps anchors its architectural claims in Kabbedijk's Class 4 (fully shared) multi-tenancy model."
    },
    {
        "key": "jacobs2007",
        "type": "inproceedings",
        "ris_type": "CONF",
        "author": "Jacobs, Dean and Aulbach, Stefan",
        "title": "Ruminations on Multi-Tenant Databases",
        "booktitle": "Proceedings of the BTW Conference",
        "year": "2007",
        "pages": "514--521",
        "category": "Multi-Tenancy Architecture & Schema Models",
        "abstract": "Explores the fundamental database requirements of multi-tenant enterprise applications. It details how shared relational databases must satisfy security isolation, tenant-specific schema extensions, performance predictability, and administrative autonomy.",
        "keywords": "multi-tenant database, relational pooling, performance isolation, schema extension",
        "highlights": "Articulated that multi-tenant databases require structural defenses that prevent inadvertent cross-tenant data retrieval during ad-hoc reporting and native query execution. Directly referenced in NexusOps's problem formulation."
    },
    {
        "key": "weissman2009",
        "type": "inproceedings",
        "ris_type": "CONF",
        "author": "Weissman, Craig D. and Bobrowski, Steve",
        "title": "The Design of the Force.com Multitenant Internet Application Development Platform",
        "booktitle": "Proceedings of the 2009 ACM SIGMOD International Conference on Management of Data",
        "year": "2009",
        "pages": "889--896",
        "doi": "10.1145/1559845.1559942",
        "url": "https://doi.org/10.1145/1559845.1559942",
        "category": "Multi-Tenancy Architecture & Schema Models",
        "abstract": "Details the architecture of Salesforce's Force.com platform, which hosts hundreds of thousands of corporate tenants on a shared relational database. The engine stores logical tenant structures in a universal metadata catalog and utilizes a custom query-rewrite engine to enforce tenant scoping.",
        "keywords": "Force.com, Salesforce, metadata architecture, query rewrite, multi-tenant database",
        "highlights": "Presents Salesforce's proprietary multi-tenant architecture, which relies on a specialized metadata engine to rewrite SQL ASTs. NexusOps shows that standard PostgreSQL RLS combined with ORM filters achieves equivalent enterprise isolation using commodity open-source technologies."
    },
    {
        "key": "guo2007",
        "type": "inproceedings",
        "ris_type": "CONF",
        "author": "Guo, C. J. and Sun, W. and Huang, Y. and Wang, Z. H. and Gao, B.",
        "title": "A Framework for Native Multi-Tenancy Application Development and Management",
        "booktitle": "Proceedings of the 9th IEEE International Conference on E-Commerce Technology",
        "year": "2007",
        "pages": "551--558",
        "doi": "10.1109/CEC-EEE.2007.4",
        "url": "https://doi.org/10.1109/CEC-EEE.2007.4",
        "category": "Multi-Tenancy Architecture & Schema Models",
        "abstract": "Presents an end-to-end framework for native multi-tenant enterprise applications. It partitions multi-tenancy requirements into data architecture, business logic execution, and administration, proving that true native multi-tenancy requires pervasive tenant context propagation.",
        "keywords": "native multi-tenancy, enterprise framework, tenant context, SaaS middleware",
        "highlights": "Formalized that native multi-tenancy requires isolating data, performance, and operational boundaries independently. Cited in NexusOps to define the scope of tenant non-interference."
    },
    {
        "key": "krebs2012",
        "type": "inproceedings",
        "ris_type": "CONF",
        "author": "Krebs, Rouven and Momm, Christof and Kounev, Samuel",
        "title": "Architectural Concerns in Multi-Tenant SaaS Applications",
        "booktitle": "Proceedings of the 2nd International Conference on Cloud Computing and Services Science (CLOSER)",
        "year": "2012",
        "pages": "426--431",
        "category": "Multi-Tenancy Architecture & Schema Models",
        "abstract": "Analyzes architectural challenges in multi-tenant SaaS systems, focusing on the tension between high resource sharing and strict isolation guarantees. It identifies the major failure domains: data confidentiality, performance interference (noisy neighbors), and administrative privilege escalation.",
        "keywords": "SaaS architecture, noisy neighbor, performance isolation, security failure domain",
        "highlights": "Demonstrated that shared-schema multi-tenancy creates distinct failure domains across data confidentiality, performance predictability, and administrative rights. NexusOps directly addresses these failure domains via dual-layer isolation and composite indexing."
    },
    {
        "key": "schiller2011",
        "type": "inproceedings",
        "ris_type": "CONF",
        "author": "Schiller, Oliver and Schiller, Benjamin and Brodt, Andreas and Mitschang, Bernhard",
        "title": "Native Support of Multi-Tenancy in RDBMS for Software as a Service",
        "booktitle": "Proceedings of the 14th International Conference on Extending Database Technology (EDBT)",
        "year": "2011",
        "pages": "117--128",
        "doi": "10.1145/1951365.1951381",
        "url": "https://doi.org/10.1145/1951365.1951381",
        "category": "Multi-Tenancy Architecture & Schema Models",
        "abstract": "Advocates for pushing multi-tenancy awareness directly into the relational database engine kernel rather than relying on application middleware. Proposes engine-level tenant identifier handling and shows dramatic performance and security improvements over application-only filtering.",
        "keywords": "EDBT, database engine, native multi-tenancy, kernel access control, RDBMS extension",
        "highlights": "Pioneered the concept of pushing multi-tenancy into the database engine. NexusOps validates Schiller's vision by leveraging modern PostgreSQL Row-Level Security as the native engine enforcement layer."
    },
    {
        "key": "narasayya2022",
        "type": "inproceedings",
        "ris_type": "CONF",
        "author": "Narasayya, Vivek and Chaudhuri, Surajit",
        "title": "Multi-Tenant Cloud Data Services: State-of-the-Art, Challenges and Opportunities",
        "booktitle": "Proceedings of the 2022 ACM SIGMOD International Conference on Management of Data",
        "year": "2022",
        "pages": "2465--2473",
        "doi": "10.1145/3514221.3526058",
        "url": "https://doi.org/10.1145/3514221.3526058",
        "category": "Multi-Tenancy Architecture & Schema Models",
        "abstract": "A comprehensive survey of multi-tenant cloud data services across major hyperscalers (Azure SQL, AWS Aurora, Google Spanner). Analyzes key technical challenges including tenant placement, serverless auto-scaling, fine-grained access control, and SLA enforcement in shared database pools.",
        "keywords": "cloud data services, SIGMOD 2022 survey, tenant placement, fine-grained access control",
        "highlights": "Provides a modern review of hyperscaler multi-tenant architectures, highlighting that fine-grained database-tier access control is the central open challenge in shared cloud database services."
    },
    {
        "key": "hibernate2025",
        "type": "manual",
        "ris_type": "COMP",
        "author": "{Red Hat, Inc.}",
        "title": "Hibernate ORM 7.0 User Guide: Multi-Tenancy",
        "organization": "Red Hat, Inc.",
        "year": "2025",
        "url": "https://docs.jboss.org/hibernate/orm/7.0/userguide/html_single/Hibernate_User_Guide.html",
        "category": "Frameworks, Microservices & Token Security",
        "abstract": "Official user guide for Hibernate ORM 7.0 detailing native multi-tenancy capabilities, specifically @TenantId entity annotations, discriminator column filtering, CurrentTenantIdentifierResolver, and the limitations of AST rewriting when executing native SQL queries.",
        "keywords": "Hibernate ORM 7.0, @TenantId, multi-tenancy discriminator, AST rewriting, JPA",
        "highlights": "The authoritative reference for Hibernate 7.0's `@TenantId` discriminator filtering. In NexusOps, this constitutes Layer 1 (Application Filtering), whose known limitations with unmapped native SQL queries motivate the addition of Layer 2 (PostgreSQL RLS)."
    },
    {
        "key": "stonebraker1974",
        "type": "inproceedings",
        "ris_type": "CONF",
        "author": "Stonebraker, Michael and Wong, Eugene",
        "title": "Access Control in a Relational Data Base Management System by Query Modification",
        "booktitle": "Proceedings of the 1974 ACM SIGFIDET Workshop on Data Description, Access and Control",
        "year": "1974",
        "pages": "180--186",
        "doi": "10.1145/800297.811537",
        "url": "https://doi.org/10.1145/800297.811537",
        "category": "Database Security & Access Control Foundations",
        "abstract": "Seminal paper introducing query modification (query rewriting) in the INGRES database system to enforce access control. Instead of checking security rules at the application layer, the database engine modifies the user query tree to include security qualification predicates.",
        "keywords": "query modification, INGRES, access control, relational database security, view rewriting",
        "highlights": "The foundational origin of modern Row-Level Security: Stonebraker and Wong proved that access control predicates injected into the relational query tree by the DBMS engine guarantee complete mediation regardless of client intent."
    },
    {
        "key": "sandhu1996",
        "type": "article",
        "ris_type": "JOUR",
        "author": "Sandhu, Ravi S. and Coyne, Edward J. and Feinstein, Hal L. and Youman, Charles E.",
        "title": "Role-Based Access Control Models",
        "journal": "IEEE Computer",
        "year": "1996",
        "volume": "29",
        "number": "2",
        "pages": "38--47",
        "doi": "10.1109/2.485845",
        "url": "https://doi.org/10.1109/2.485845",
        "category": "Database Security & Access Control Foundations",
        "abstract": "Introduces the RBAC96 family of conceptual models for Role-Based Access Control. Defines RBAC0 (core permissions), RBAC1 (role hierarchies), RBAC2 (constraints and separation of duty), and RBAC3 (consolidated model), providing the theoretical foundation for enterprise role management.",
        "keywords": "RBAC96, role-based access control, security models, separation of duty, permission assignment",
        "highlights": "Established the canonical RBAC96 framework. NexusOps integrates RBAC principles within each tenant boundary, ensuring that tenant scoping operates orthogonally to user role assignments."
    },
    {
        "key": "ferraiolo2001",
        "type": "article",
        "ris_type": "JOUR",
        "author": "Ferraiolo, David F. and Sandhu, Ravi and Gavrila, Serban and Kuhn, D. Richard and Chandramouli, Ramaswamy",
        "title": "Proposed NIST Standard for Role-Based Access Control",
        "journal": "ACM Transactions on Information and System Security",
        "year": "2001",
        "volume": "4",
        "number": "3",
        "pages": "224--274",
        "doi": "10.1145/501978.501980",
        "url": "https://doi.org/10.1145/501978.501980",
        "category": "Database Security & Access Control Foundations",
        "abstract": "Proposes the unified NIST standard for Role-Based Access Control (RBAC), formalizing mathematical specifications for core RBAC, hierarchical RBAC, static separation of duty (SSD), and dynamic separation of duty (DSD).",
        "keywords": "NIST RBAC, access control standard, separation of duty, dynamic authorization",
        "highlights": "Formal NIST standard defining dynamic role constraints. NexusOps uses this framework to separate application roles (`nexusops_app`) from migration roles (`nexusops_owner`) and administrative roles (`nexusops_platform`)."
    },
    {
        "key": "goguen1982",
        "type": "inproceedings",
        "ris_type": "CONF",
        "author": "Goguen, Joseph A. and Meseguer, José",
        "title": "Security Policies and Security Models",
        "booktitle": "Proceedings of the 1982 IEEE Symposium on Security and Privacy",
        "year": "1982",
        "pages": "11--20",
        "doi": "10.1109/SP.1982.10014",
        "url": "https://doi.org/10.1109/SP.1982.10014",
        "category": "Database Security & Access Control Foundations",
        "abstract": "Seminal work formalizing the mathematical concept of Non-Interference in computer security models. Proves that a system is secure if the actions of high-security users produce zero observable change in the system states or outputs visible to low-security users.",
        "keywords": "non-interference, security models, formal verification, information flow, state machine",
        "highlights": "Invented the formal concept of Non-Interference in computer security. NexusOps establishes Theorem 1 as a direct mathematical proof of Goguen-Meseguer non-interference across recycled pooled database connections."
    },
    {
        "key": "richardson2018",
        "type": "book",
        "ris_type": "BOOK",
        "author": "Richardson, Chris",
        "title": "Microservices Patterns: With Examples in Java",
        "publisher": "Manning Publications",
        "address": "Shelter Island, NY, USA",
        "year": "2018",
        "isbn": "9781617294549",
        "category": "Frameworks, Microservices & Token Security",
        "abstract": "Comprehensive architectural guide covering microservice decomposition patterns, data management with Sagas, CQRS, domain event publishing, and the trade-offs of microservices versus modular monoliths in enterprise systems.",
        "keywords": "microservices patterns, modular monolith, transactional outbox, domain-driven design",
        "highlights": "Demonstrates the severe operational and transactional penalties of distributed microservices (distributed sagas, two-phase commits). Used in NexusOps to justify adopting a Modular Monolith architecture that preserves local ACID transactions."
    },
    {
        "key": "newman2019",
        "type": "book",
        "ris_type": "BOOK",
        "author": "Newman, Sam",
        "title": "Monolith to Microservices: Evolutionary Patterns to Transform Your Monolith",
        "publisher": "O'Reilly Media",
        "address": "Sebastopol, CA, USA",
        "year": "2019",
        "isbn": "9781492047841",
        "category": "Frameworks, Microservices & Token Security",
        "abstract": "Provides concrete patterns for decomposing monolithic systems into microservices, warning against premature microservice distribution and advocating modular monolithic architectures for enterprise operational simplicity.",
        "keywords": "monolith decomposition, modular architecture, service boundaries, migration patterns",
        "highlights": "Warns against premature distributed decomposition in early-to-mid stage enterprise SaaS platforms. NexusOps adopts Newman's modular monolith guidance via Spring Modulith compile-time package enforcement."
    },
    {
        "key": "dragoni2017",
        "type": "incollection",
        "ris_type": "CHAP",
        "author": "Dragoni, Nicola and Giallorenzo, Saverio and Lluch Lafuente, Alberto and Mazzara, Manuel and Montesi, Fabrizio and Mustafin, Ruslan and Safina, Larisa",
        "title": "Microservices: Yesterday, Today, and Tomorrow",
        "booktitle": "Present and Ulterior Software Engineering",
        "editor": "Mazzara, Manuel and Meyer, Bertrand",
        "publisher": "Springer",
        "address": "Cham, Switzerland",
        "year": "2017",
        "pages": "195--216",
        "doi": "10.1007/978-3-319-67425-4_12",
        "url": "https://doi.org/10.1007/978-3-319-67425-4_12",
        "category": "Frameworks, Microservices & Token Security",
        "abstract": "An extensive survey tracing the evolution of microservices from service-oriented architectures (SOA). Contrasts distributed microservices against monolithic structures in terms of deployment complexity, network serialization costs, and failure recovery.",
        "keywords": "microservices survey, SOA, service boundaries, network serialization, system evolution",
        "highlights": "Analyzes the high performance tax imposed by network serialization and RPC hops in distributed microservices. NexusOps references this study to justify keeping domain boundaries within an in-process modular architecture."
    },
    {
        "key": "jones2015",
        "type": "techreport",
        "ris_type": "RPRT",
        "author": "Jones, Michael and Bradley, John and Sakimura, Nat",
        "title": "JSON Web Token (JWT)",
        "institution": "Internet Engineering Task Force",
        "type": "RFC",
        "number": "7519",
        "year": "2015",
        "doi": "10.17487/RFC7519",
        "url": "https://www.rfc-editor.org/info/rfc7519",
        "category": "Frameworks, Microservices & Token Security",
        "abstract": "RFC 7519 defines a compact, URL-safe means of representing claims to be transferred between two parties. Details JWT structure (header, payload, signature), cryptographic signing methods, and claims processing rules.",
        "keywords": "JWT, RFC 7519, JSON claims, cryptographic signature, token authentication",
        "highlights": "Standard specification for JSON Web Tokens. In NexusOps, JWTs signed with RS256 carry the immutable `tid` (tenant ID) claim, ensuring that tenant context originates strictly from authenticated identity credentials."
    },
    {
        "key": "lodderstedt2025",
        "type": "techreport",
        "ris_type": "RPRT",
        "author": "Lodderstedt, Torsten and Bradley, John and Labunets, Andrey and Fett, Daniel",
        "title": "Best Current Practice for OAuth 2.0 Security",
        "institution": "Internet Engineering Task Force",
        "type": "RFC",
        "number": "9700",
        "year": "2025",
        "doi": "10.17487/RFC9700",
        "url": "https://www.rfc-editor.org/info/rfc9700",
        "category": "Frameworks, Microservices & Token Security",
        "abstract": "RFC 9700 updates the OAuth 2.0 security architecture to address modern threat vectors. Mandates rotating refresh tokens, sender-constrained tokens, defense against CSRF and token leakage, and deprecates the implicit grant flow.",
        "keywords": "OAuth 2.0 security, RFC 9700, refresh token rotation, token replay protection",
        "highlights": "The contemporary IETF Best Current Practice for OAuth 2.0. NexusOps implements RFC 9700 recommendations including short-lived 15-minute access tokens and rotating httpOnly refresh tokens backed by Redis blocklists."
    },
    {
        "key": "hanley1983",
        "type": "article",
        "ris_type": "JOUR",
        "author": "Hanley, James A. and Lippman-Hand, Abby",
        "title": "If Nothing Goes Wrong, Is Everything All Right? Interpreting Zero Numerators",
        "journal": "JAMA: The Journal of the American Medical Association",
        "year": "1983",
        "volume": "249",
        "number": "13",
        "pages": "1743--1745",
        "doi": "10.1001/jama.1983.03330370053031",
        "url": "https://doi.org/10.1001/jama.1983.03330370053031",
        "category": "Rigorous Benchmarking & Statistical Equivalence",
        "abstract": "Presents the statistical derivation and practical application of the Rule-of-Three. When zero adverse events occur in a sample of N independent trials, the 95% upper confidence bound on the true event probability is approximately 3/N.",
        "keywords": "Rule of Three, zero numerators, binomial confidence interval, upper bound, statistical risk",
        "highlights": "Provides the mathematical derivation of the Rule-of-Three for zero-numerator events ($p_{95%} < 3/N$). Used in NexusOps to establish a rigorous 95% upper confidence bound of $3 \times 10^{-6}$ (0.0003%) on cross-tenant leakage across $1,000,000$ empirical transactions."
    },
    {
        "key": "georges2007",
        "type": "inproceedings",
        "ris_type": "CONF",
        "author": "Georges, Andy and Buytaert, Dries and Eeckhout, Lieven",
        "title": "Statistically Rigorous Java Performance Evaluation",
        "booktitle": "Proceedings of the 22nd ACM SIGPLAN Conference on Object-Oriented Programming Systems, Languages, and Applications (OOPSLA)",
        "year": "2007",
        "pages": "57--76",
        "doi": "10.1145/1297027.1297033",
        "url": "https://doi.org/10.1145/1297027.1297033",
        "category": "Rigorous Benchmarking & Statistical Equivalence",
        "abstract": "Exposes widespread flaws in Java and JVM performance evaluations, including inadequate warm-up, non-deterministic JIT compilation, and benchmark non-independence. Proposes statistically rigorous evaluation guidelines utilizing confidence intervals and ANOVA.",
        "keywords": "Java benchmarking, JVM performance, JIT warm-up, statistical rigor, confidence interval",
        "highlights": "Established standard methodologies for JVM and managed runtime benchmarking: mandatory warm-up periods, independent VM invocations, and confidence intervals. NexusOps adopts Georges's warm-up and iteration guidelines."
    },
    {
        "key": "kalibera2013",
        "type": "inproceedings",
        "ris_type": "CONF",
        "author": "Kalibera, Tomas and Jones, Richard",
        "title": "Rigorous Benchmarking in Reasonable Time",
        "booktitle": "Proceedings of the 2013 International Symposium on Memory Management (ISMM)",
        "year": "2013",
        "pages": "63--74",
        "doi": "10.1145/2464157.2464160",
        "url": "https://doi.org/10.1145/2464157.2464160",
        "category": "Rigorous Benchmarking & Statistical Equivalence",
        "abstract": "Presents statistical techniques for detecting and controlling non-determinism, correlation, and run-order dependencies in systems benchmarks. Demonstrates that randomizing benchmark run order is essential to prevent false conclusions.",
        "keywords": "benchmarking methodology, run-order effects, system non-determinism, randomized paired testing",
        "highlights": "Demonstrates that system benchmarks are susceptible to hidden run-order bias and non-deterministic memory alignment. Mandates randomized paired execution, which NexusOps implements across all $n=30$ workload iterations."
    },
    {
        "key": "mytkowicz2009",
        "type": "inproceedings",
        "ris_type": "CONF",
        "author": "Mytkowicz, Todd and Diwan, Amer and Hauswirth, Matthias and Sweeney, Peter F.",
        "title": "Producing Wrong Data Without Doing Anything Obviously Wrong!",
        "booktitle": "Proceedings of the 14th International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS)",
        "year": "2009",
        "pages": "265--276",
        "doi": "10.1145/1508244.1508275",
        "url": "https://doi.org/10.1145/1508244.1508275",
        "category": "Rigorous Benchmarking & Statistical Equivalence",
        "abstract": "Shows that computer systems benchmarking is plagued by measurement bias caused by trivial environment changes, such as Unix environment variable sizes and linking order, shifting cache layouts by up to 15%. Recommends setup randomization.",
        "keywords": "measurement bias, benchmark validity, cache alignment, ASPLOS, experimental error",
        "highlights": "Proved that trivial environment variations cause up to 15% performance fluctuations due to cache alignment. Cited in NexusOps to substantiate our dedicated host isolation, CPU affinity pinning, and table vacuuming protocols."
    },
    {
        "key": "schuirmann1987",
        "type": "article",
        "ris_type": "JOUR",
        "author": "Schuirmann, Donald J.",
        "title": "A Comparison of the Two One-Sided Tests Procedure and the Power Approach for Assessing the Equivalence of Average Bioavailability",
        "journal": "Journal of Pharmacokinetics and Biopharmaceutics",
        "year": "1987",
        "volume": "15",
        "number": "6",
        "pages": "657--680",
        "doi": "10.1007/BF01068419",
        "url": "https://doi.org/10.1007/BF01068419",
        "category": "Rigorous Benchmarking & Statistical Equivalence",
        "abstract": "Pioneered the Two One-Sided Tests (TOST) statistical procedure for testing whether the difference between two treatments falls within an acceptable equivalence margin [\\theta_L, \\theta_U], demonstrating that failing to reject a null difference is invalid proof of equivalence.",
        "keywords": "TOST, equivalence testing, two one-sided tests, statistical power, equivalence margin",
        "highlights": "Formulated the Two One-Sided Tests (TOST) procedure to rigorously prove that two systems are statistically equivalent within predefined bounds. NexusOps uses Schuirmann's TOST to demonstrate that Dual-Layer RLS is statistically equivalent to Filter-Only baselines within a $± 10%$ corridor ($p < 0.05$)."
    },
    {
        "key": "lakens2018",
        "type": "article",
        "ris_type": "JOUR",
        "author": "Lakens, Daniël and Scheel, Anne M. and Isager, Peder M.",
        "title": "Equivalence Testing for Psychological Research: A Tutorial",
        "journal": "Advances in Methods and Practices in Psychological Science",
        "year": "2018",
        "volume": "1",
        "number": "2",
        "pages": "259--269",
        "doi": "10.1177/2515245918770963",
        "url": "https://doi.org/10.1177/2515245918770963",
        "category": "Rigorous Benchmarking & Statistical Equivalence",
        "abstract": "A comprehensive practical tutorial on equivalence testing using TOST. Details log-ratio transformation for ratio metrics, Cohen's d effect sizes, power calculations, and methods for avoiding false negative assertions in empirical comparisons.",
        "keywords": "equivalence testing tutorial, TOST, log-transformed ratios, Cohen's d, statistical equivalence",
        "highlights": "Provides the modern mathematical methodology for equivalence testing using log-transformed ratios ($z_i = \\ln(\\text{Throughput}_{\\text{Dual}, i} / \\text{Throughput}_{\\text{Base}, i})$). Directly followed in NexusOps's experimental evaluation."
    },
    {
        "key": "curino2010",
        "type": "article",
        "ris_type": "JOUR",
        "author": "Curino, Carlo and Jones, Evan P. C. and Zhang, Yang and Madden, Samuel",
        "title": "Relational Cloud: A Database-as-a-Service for the Cloud",
        "journal": "CIDR",
        "year": "2011",
        "pages": "235--240",
        "url": "http://cidrdb.org/cidr2011/Papers/CIDR11_Paper35.pdf",
        "category": "Multi-Tenancy Architecture & Schema Models",
        "abstract": "Articulates the vision and architecture for Relational Cloud, an elastic database-as-a-service. Identifies multi-tenant workload consolidation, automatic schema partitioning, transactional security, and performance isolation as core requirements for cloud relational databases.",
        "keywords": "Relational Cloud, database as a service, DBaaS, workload consolidation, multi-tenant partitioning",
        "highlights": "Visionary paper establishing that cloud relational database consolidation requires pairing workload performance predictability with hard security guarantees. NexusOps fulfills this vision on modern PostgreSQL."
    },
    {
        "key": "poonawala2026nexusops",
        "type": "article",
        "ris_type": "JOUR",
        "author": "Poonawala, Ibrahim and Mandhare, Varad and Shinde, Tanmay and Kerketta, Reetika",
        "title": "Dual-Layer Tenant Isolation in Shared-Schema SaaS: Combining ORM Filters with PostgreSQL Row-Level Security",
        "journal": "IEEE Transactions on Cloud Computing",
        "year": "2026",
        "volume": "XX",
        "number": "X",
        "pages": "1--16",
        "url": "https://github.com/Varadha9/multi-tenant-saas-platform",
        "category": "NexusOps Core Publication",
        "abstract": "Shared-schema multi-tenancy maximizes hardware consolidation and operational efficiency in SaaS platforms, but exposes systems to cross-tenant data leaks if application-level filtering fails. We present NexusOps, an enterprise SaaS platform implementing a dual-layer isolation architecture pairing Hibernate ORM filters with PostgreSQL forced Row-Level Security (RLS) under transaction-scoped session configuration (SET LOCAL). NexusOps enforces zero cross-tenant leakage across three automated guardrails: build-time schema AST inspection, eager database role validation ensuring the application role lacks BYPASSRLS, and transaction-lifecycle hooks preventing connection-pool session bleeding. We formalize tenant non-interference under recycled connection pools and evaluate the architecture across 1,000,000 records using a paired empirical benchmark harness (n = 30 runs per workload) with Two One-Sided Tests (TOST) for statistical equivalence. Forced RLS incurs bounded engine overhead between 2.3% and 8.8% over an application-filtered baseline across read, write, paginated, and join workloads, while preserving sub-millisecond median latencies (0.72-2.99 ms) and robust p99 tail bounds. Fault-injection tests against eight isolation mutants achieve a 100% detection rate.",
        "keywords": "Multi-Tenancy, Row-Level Security, Database Security, Software-as-a-Service, Hibernate ORM, PostgreSQL, Access Control, Defense-in-Depth, Empirical Benchmarking, TOST Equivalence",
        "highlights": "Core publication introducing the NexusOps dual-layer isolation architecture. Key highlights: (1) Theorem 1 formal proof of non-interference under recycled connection pools; (2) Properties 1-5 formal access guarantees; (3) Three automated CI/CD guardrails (AST inspector, eager role guard, ScopedValue/transaction hook); (4) 100% kill rate across 8 fault-injection isolation mutants; (5) Empirical evaluation over 1,000,000 records with n=30 paired runs proving RLS overhead is bounded between 2.3% and 8.8%; (6) TOST statistical equivalence within +/-10% corridor (p < 0.05); (7) Zero leaks across 10^6 requests (Hanley Rule-of-Three upper bound p_95% < 3x10^-6)."
    }
]



import json
import os



# -----------------------------------------------------------------------------
# 1. Generate references.bib (BibTeX)
# -----------------------------------------------------------------------------
bib_lines = []
bib_lines.append("% =============================================================================")
bib_lines.append("% NexusOps Research Library - Mendeley-Compatible BibTeX Database")
bib_lines.append("% Formatted with rich metadata: DOIs, URLs, Abstracts, Keywords, and Mendeley Notes")
bib_lines.append("% Total Entries: 39 (38 Canonical References + NexusOps Manuscript)")
bib_lines.append("% =============================================================================\n")

for e in entries:
    btype = e.get("type", "article")
    key = e["key"]
    bib_lines.append(f"@{btype}{{{key},")
    bib_lines.append(f"  author    = {{{e['author']}}},")
    bib_lines.append(f"  title     = {{{{{e['title']}}}}},")
    
    if "journal" in e:
        bib_lines.append(f"  journal   = {{{e['journal']}}},")
    elif "booktitle" in e:
        bib_lines.append(f"  booktitle = {{{e['booktitle']}}},")
    elif "institution" in e:
        bib_lines.append(f"  institution = {{{e['institution']}}},")
    elif "organization" in e:
        bib_lines.append(f"  organization = {{{e['organization']}}},")
    elif "publisher" in e:
        bib_lines.append(f"  publisher = {{{e['publisher']}}},")

    if "year" in e:
        bib_lines.append(f"  year      = {{{e['year']}}},")
    if "volume" in e:
        bib_lines.append(f"  volume    = {{{e['volume']}}},")
    if "number" in e:
        bib_lines.append(f"  number    = {{{e['number']}}},")
    if "pages" in e:
        bib_lines.append(f"  pages     = {{{e['pages']}}},")
    if "doi" in e:
        bib_lines.append(f"  doi       = {{{e['doi']}}},")
    if "url" in e:
        bib_lines.append(f"  url       = {{{e['url']}}},")
    if "address" in e:
        bib_lines.append(f"  address   = {{{e['address']}}},")
    if "editor" in e:
        bib_lines.append(f"  editor    = {{{e['editor']}}},")
    if "isbn" in e:
        bib_lines.append(f"  isbn      = {{{e['isbn']}}},")
        
    if "abstract" in e:
        bib_lines.append(f"  abstract  = {{{e['abstract']}}},")
    if "keywords" in e:
        bib_lines.append(f"  keywords  = {{{e['keywords']}}},")
    if "highlights" in e:
        clean_note = e['highlights'].replace('$', '')
        bib_lines.append(f"  annote    = {{{clean_note}}}")
        
    bib_lines.append("}\n")

with open('references.bib', 'w') as f:
    f.write("\n".join(bib_lines))
print(f"Generated references.bib with {len(entries)} entries.")

# -----------------------------------------------------------------------------
# 2. Generate references.ris (Universal RIS format for 1-click Mendeley import)
# -----------------------------------------------------------------------------
ris_lines = []
for e in entries:
    rtype = e.get("ris_type", "JOUR")
    ris_lines.append(f"TY  - {rtype}")
    
    # Authors
    raw_authors = e["author"]
    # Handle {OWASP Foundation} or standard author strings
    raw_authors = raw_authors.replace("{", "").replace("}", "")
    for author in raw_authors.split(" and "):
        ris_lines.append(f"AU  - {author.strip()}")
        
    ris_lines.append(f"TI  - {e['title']}")
    
    pub = e.get("journal") or e.get("booktitle") or e.get("institution") or e.get("publisher") or ""
    if pub:
        ris_lines.append(f"T2  - {pub}")
        ris_lines.append(f"JO  - {pub}")
        
    if "year" in e:
        ris_lines.append(f"PY  - {e['year']}")
    if "volume" in e:
        ris_lines.append(f"VL  - {e['volume']}")
    if "number" in e:
        ris_lines.append(f"IS  - {e['number']}")
    if "pages" in e:
        parts = e["pages"].split("--")
        ris_lines.append(f"SP  - {parts[0].strip()}")
        if len(parts) > 1:
            ris_lines.append(f"EP  - {parts[1].strip()}")
    if "doi" in e:
        ris_lines.append(f"DO  - {e['doi']}")
    if "url" in e:
        ris_lines.append(f"UR  - {e['url']}")
    if "abstract" in e:
        ris_lines.append(f"AB  - {e['abstract']}")
    if "keywords" in e:
        for kw in e["keywords"].split(","):
            ris_lines.append(f"KW  - {kw.strip()}")
    if "highlights" in e:
        clean_note = e['highlights'].replace('$', '')
        ris_lines.append(f"N1  - Key Highlights & NexusOps Synthesis: {clean_note}")
    if "key" in e:
        ris_lines.append(f"ID  - {e['key']}")
    if e["key"] == "poonawala2026nexusops":
        ris_lines.append("L1  - main.pdf")
        
    ris_lines.append("ER  - \n")

with open('references.ris', 'w') as f:
    f.write("\n".join(ris_lines))
print(f"Generated references.ris with {len(entries)} entries.")

# -----------------------------------------------------------------------------
# 3. Generate MENDELEY_LIBRARY.md (Annotated Guide & Highlights)
# -----------------------------------------------------------------------------
md = []
md.append("# NexusOps Mendeley Research Library & Literature Synthesis Guide\n")
md.append("This document provides a comprehensive, highlighted reference guide to all academic literature, industrial standards, and empirical studies incorporated in the NexusOps research manuscript: **\"Dual-Layer Tenant Isolation in Shared-Schema SaaS: Combining ORM Filters with PostgreSQL Row-Level Security\"**.\n")
md.append("Both **BibTeX** (`references.bib`) and **RIS** (`references.ris`) export formats are provided in this repository for seamless, one-click synchronization with **Mendeley Reference Manager**, **Mendeley Desktop**, and **Mendeley Web**.\n")
md.append("---\n")

md.append("## 🚀 Quick-Start: Importing into Mendeley in 30 Seconds\n")
md.append("You can import the entire research library into Mendeley using either of the following two native methods:\n")
md.append("### Method A: One-Click RIS Import (Recommended)\n")
md.append("1. Open **Mendeley Reference Manager** (or [Mendeley Web](https://www.mendeley.com/reference-manager/library)).\n")
md.append("2. Click on the green **`+ Add new`** button in the top-left toolbar.\n")
md.append("3. Select **`Import library` $\\rightarrow$ `RIS (*.ris)`**.\n")
md.append("4. Choose `research_paper/references.ris` from this repository.\n")
md.append("5. All 39 entries will instantaneously load with complete author metadata, abstracts, DOIs, publication years, keywords, and **highlighted analytical notes in the `Notes / Annotation` pane**.\n")
md.append("6. Drag and drop `research_paper/main.pdf` directly onto the `poonawala2026nexusops` entry to link the full 16-page paper PDF.\n\n")

md.append("### Method B: BibTeX Import\n")
md.append("1. In Mendeley Reference Manager, click **`+ Add new`** $\\rightarrow$ **`Import library` $\\rightarrow$ `BibTeX (*.bib)`**.\n")
md.append("2. Select `research_paper/references.bib`.\n")
md.append("3. All entries and tags are imported automatically.\n\n")

md.append("### Method C: Mendeley Desktop Watched Folder Auto-Sync\n")
md.append("If using Mendeley Desktop:\n")
md.append("- Navigate to `Tools` $\\rightarrow$ `Options` $\\rightarrow$ `Watched Folders`.\n")
md.append("- Check the `research_paper/` directory to automatically synchronize new papers and bibliography modifications.\n\n")
md.append("---\n")

md.append("## 📂 Recommended Mendeley Collection (Folder) Hierarchy\n")
md.append("To mirror the taxonomy utilized in the NexusOps manuscript, organize your Mendeley library into the following six collections:\n\n")
md.append("```text\n📁 NexusOps Research Library\n├── 📁 01_Multi-Tenancy_Architecture      (Chong 2006, Aulbach 2008, Jacobs 2007, Weissman 2009, Guo 2007, Krebs 2012, Schiller 2011, Narasayya 2022, Curino 2010, AWS 2020)\n├── 📁 02_Database_Security_and_RLS       (Saltzer 1975, Stonebraker 1974, Sandhu 1996, Ferraiolo 2001, Goguen 1982, PostgreSQL 17 Docs & Notes)\n├── 📁 03_Threat_Landscape_and_Breaches   (Panko 1998, Powell 2009, OWASP Top 10 2021, OWASP API Top 10 2023, Verizon DBIR 2023, IBM Ponemon 2023, Armbrust 2010, Bezemer 2010, Kabbedijk 2015)\n├── 📁 04_Frameworks_and_Token_Security   (Hibernate ORM 7.0 2025, Richardson 2018, Newman 2019, Dragoni 2017, IETF RFC 7519 JWT, IETF RFC 9700 OAuth 2.0)\n├── 📁 05_Benchmarking_and_Statistics     (Hanley Rule-of-Three 1983, Georges OOPSLA 2007, Kalibera ISMM 2013, Mytkowicz ASPLOS 2009, Schuirmann TOST 1987, Lakens 2018)\n└── 📁 06_NexusOps_Core_Publication       (Poonawala, Mandhare, Shinde, Kerketta 2026)\n```\n\n")
md.append("---\n")

md.append("## 🌟 NexusOps Core Paper: Highlights & Key Contributions\n\n")
nexus_entry = next(e for e in entries if e["key"] == "poonawala2026nexusops")
md.append(f"### 📄 **[{nexus_entry['key']}] {nexus_entry['title']}**\n")
md.append(f"- **Authors:** {nexus_entry['author']}\n")
md.append(f"- **Venue:** {nexus_entry['journal']}, Vol. {nexus_entry['volume']}, No. {nexus_entry['number']}, pp. {nexus_entry['pages']}, {nexus_entry['year']}\n")
md.append(f"- **Repository & Artifacts:** [{nexus_entry['url']}]({nexus_entry['url']})\n\n")
md.append(f"#### 🎯 Abstract\n> {nexus_entry['abstract']}\n\n")
md.append("#### 💡 Key Highlights & Scientific Contributions\n")
md.append("1. **Dual-Layer Defense-in-Depth Architecture:** Combines Layer 1 (Hibernate ORM `@TenantId` AST filtering) with Layer 2 (PostgreSQL forced Row-Level Security under transaction-scoped `SET LOCAL app.tenant_id = ?`). Ensures that even if application-level query scoping is completely omitted, the database engine enforces complete mediation.\n")
md.append("2. **Theorem 1 (Non-Interference under Recycled Connection Pools):** Formal inductive proof demonstrating that across arbitrary request sequences dispatched over a shared physical connection pool (HikariCP), the active visibility set is strictly non-interfering. When a transaction completes, PostgreSQL's `is_local = true` flag unconditionally flushes GUC session parameters, preventing session bleeding.\n")
md.append("3. **Properties 1–5 Formal Security Guarantees:**\n")
md.append("   - *Property 1 (Strict Non-Interference):* Visibility set $\\mathcal{R}(Q, \\tau = t) \\subseteq \\mathcal{D}(t)$ and $\\mathcal{R}(Q, t_i) \\cap \\mathcal{D}(t_j) = \\emptyset$.\n")
md.append("   - *Property 2 (Fail-Closed Execution):* Unauthenticated requests $(\\tau = \\emptyset)$ evaluate to an empty result set $(\\mathcal{R}(Q, \\emptyset) = \\emptyset)$.\n")
md.append("   - *Property 3 (Connection Context Sanitization):* Pooled connections discard residual tenant context upon transaction boundary exit.\n")
md.append("   - *Property 4 (Audit Trail Immutability):* Hardened database triggers prohibit `UPDATE`, `DELETE`, and `TRUNCATE` operations on `audit_events`.\n")
md.append("   - *Property 5 (Anti-Enumeration Uniformity):* Cross-tenant entity lookups uniformly return HTTP 404 rather than HTTP 403, preventing ID enumeration.\n")
md.append("4. **Three Automated CI/CD Guardrails:**\n")
md.append("   - *Build-Time AST Catalog Guard (`RlsCoverageIT`):* Inspects PostgreSQL system catalogs (`pg_class`, `pg_policy`) in continuous integration, failing the build in 4.2 seconds if any table lacks `FORCE ROW LEVEL SECURITY` or standard `WITH CHECK` clauses.\n")
md.append("   - *Eager Database Role Guard (`DatabaseRoleGuard`):* Verifies at startup that runtime application credentials lack `BYPASSRLS`, `rolsuper`, and DDL privileges.\n")
md.append("   - *Transaction-Scoped Connection Sanitizer (`TenantAwareConnectionProvider`):* Enforces `SET LOCAL` strictly within transaction blocks, decoupling Java 25 virtual carrier threads via `ScopedValue`.\n")
md.append("5. **100% Mutation Kill Rate:** Tested against 8 security-critical fault-injection mutants (including omitted RLS, unforced table owner exemptions, missing `WITH CHECK` clauses, and malicious bypass settings); all 8 mutants were intercepted.\n")
md.append("6. **Empirical Benchmarking (1,000,000 Records, $n = 30$ Paired Runs):**\n")
md.append("   - RLS runtime overhead is bounded between **$2.3\\%$ and $8.8\\%$** over application-only baselines.\n")
md.append("   - Median query latencies remain sub-millisecond (**0.72 ms to 2.99 ms**) with robust p99 bounds.\n")
md.append("   - **Two One-Sided Tests (TOST)** confirm statistical equivalence within a $\± 10\\%$ corridor ($p < 0.05$) across all workloads.\n")
md.append("   - **Hanley Rule-of-Three:** 0 leaks observed across $10^6$ transactions establishes a 95% upper confidence bound of $p_{95\\%} < 3 \\times 10^{-6}$ (0.0003%).\n\n")
md.append("---\n")

md.append("## 📚 Highlighted Annotated Catalog of Literature (All 38 Citations)\n\n")

categories = [
    "Multi-Tenancy Architecture & Schema Models",
    "Database Security & Access Control Foundations",
    "Enterprise SaaS Vulnerabilities & Threat Landscape",
    "Frameworks, Microservices & Token Security",
    "Rigorous Benchmarking & Statistical Equivalence",
    "Cloud Economics & Resource Consolidation"
]

for cat in categories:
    cat_entries = [e for e in entries if e.get("category") == cat and e["key"] != "poonawala2026nexusops"]
    if not cat_entries:
        continue
    md.append(f"### 📂 {cat}\n")
    for e in cat_entries:
        md.append(f"#### 🏷️ `[{e['key']}]` {e['title']}\n")
        pub = e.get('journal') or e.get('booktitle') or e.get('institution') or e.get('publisher') or ''
        vol_info = f", vol. {e['volume']}, no. {e['number']}" if "volume" in e and "number" in e else ""
        pages_info = f", pp. {e['pages']}" if "pages" in e else ""
        md.append(f"- **Authors:** {e['author']}\n")
        md.append(f"- **Publication / Venue:** *{pub}* ({e['year']}){vol_info}{pages_info}\n")
        if "doi" in e:
            md.append(f"- **DOI:** [{e['doi']}](https://doi.org/{e['doi']})\n")
        if "url" in e:
            md.append(f"- **Canonical Link:** [{e['url']}]({e['url']})\n")
        md.append(f"- **Keywords / Mendeley Tags:** `{e['keywords']}`\n")
        md.append(f"- **Abstract Summary:** {e['abstract']}\n")
        md.append(f"- **💡 Key Highlights & Role in NexusOps:**\n  > {e['highlights']}\n\n")

with open('MENDELEY_LIBRARY.md', 'w') as f:
    f.write("\n".join(md))

print("Generated MENDELEY_LIBRARY.md successfully.")
