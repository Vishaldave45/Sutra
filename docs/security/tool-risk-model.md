# Security Architecture: Tool Risk & Action Classification Model

> **Design Specification Only**: This document defines the conceptual security taxonomy and permission boundaries for future Sutra phases (Phase 6 Tool System, Phase 14 Security & Approvals). **No code, middleware, or tools are implemented in this phase.**

---

## 1. Objective

As a personal AI operating system designed to automate daily tasks, Sutra will eventually interact with external services (calendars, emails, messaging, files, and system commands). Uncontrolled tool execution creates significant security and privacy risks (e.g., unintended data deletion, privacy leaks, unauthorized financial transactions, prompt injection exploitation).

This document establishes the **Action Risk Taxonomy** and the **Permission Contract** that all future execution capabilities must adhere to.

---

## 2. Action Risk Taxonomy

Every executable action in Sutra will be statically categorized or dynamically evaluated into one of five risk tiers:

```text
  [ READ ] ──► [ LOW ] ──► [ MEDIUM ] ──► [ HIGH ] ──► [ CRITICAL ]
  (Lowest Risk)                                       (Highest Risk)
```

| Risk Level | Definition | Examples | Autonomous Execution | User Approval Required |
| :--- | :--- | :--- | :--- | :--- |
| **READ** | Non-mutating queries that inspect system or external state without modifying data. | Read calendar events, search emails, read local files, fetch weather, check system status. | **Allowed** (Subject to read scope policies). | **No** (Implicitly approved by user prompt). |
| **LOW** | Idempotent or trivially reversible mutating actions with low blast radius. | Create a calendar reminder, draft an email (without sending), append to a scratchpad note, create a task. | **Allowed** with notification. | **No** (Can be executed autonomously; logged in timeline). |
| **MEDIUM** | Mutating actions with external side effects or moderate blast radius that require intent confirmation. | Send an email to an existing contact, modify/reschedule a meeting, update task status, update a contact record. | **Conditional** (Allowed if explicit user instruction was given within the active turn). | **Recommended** unless explicitly pre-authorized by user policy. |
| **HIGH** | Irreversible mutations, outbound communication to new recipients, or destructive file operations. | Send emails to unknown/external addresses, delete calendar events, overwrite files, execute code in sandboxes. | **Blocked autonomously**. | **Mandatory** explicit confirmation (interactive prompt or approval token required). |
| **CRITICAL** | Actions involving irreversible data destruction, credentials, financial transactions, or system configuration changes. | Delete database/tables, purge storage buckets, transfer funds, access API keys/secrets, modify user permissions, run host root commands. | **Strictly Forbidden autonomously**. | **Mandatory Dual/Explicit Confirmation** with verification gate and audit logging. |

---

## 3. The Permission Contract

Future Tool and Execution Systems (Phase 6, Phase 14) must follow this strict sequential evaluation pipeline:

```text
                  Agent Request (Intent to act)
                               │
                               ▼
                    1. Identify Action & Tool
                               │
                               ▼
                    2. Evaluate Risk Classification
                               │
                               ▼
                    3. Check Active Security Policy
                               │
                     ┌─────────┴─────────┐
                     ▼                   ▼
           [Requires Approval]    [Pre-Approved / Safe]
                     │                   │
                     ▼                   │
            4. Solicit User              │
               Confirmation              │
                     │                   │
             ┌───────┴───────┐           │
             ▼               ▼           │
        [Rejected]      [Approved]       │
             │               │           │
             ▼               └─────┬─────┘
        Abort Action               │
                                   ▼
                            5. Execute Tool
                                   │
                                   ▼
                            6. Emit Audit Log
```

### Invariants:
1. **Never Execute Arbitrary Shell Code**: Host command execution is prohibited unless explicitly configured in an isolated, sandboxed environment.
2. **Fail-Closed Default**: If an action cannot be definitively classified, it defaults to `HIGH` risk and requires explicit user consent.
3. **No Credential Exposure**: Tools never return credentials, access tokens, or private environment variables to the model or conversation history.
4. **Immutable Audit Trail**: All actions categorized as `MEDIUM` or higher must produce an auditable trace record before and after execution.

