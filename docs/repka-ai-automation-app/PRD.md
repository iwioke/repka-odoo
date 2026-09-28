# PRD: Repka AI Automation app

## Problem and users
Managers need a clear place to find and run the existing CLI demonstrations; the catalogue also contains ideas that are not executable. Primary users are local demo operators and reviewers, not production Odoo users.

## Goals and scope
Provide a responsive local dashboard with search, category filters, readable details, safe DEMO execution, authentic JSON output, error handling and ephemeral run history. Show all 23 catalogue entries and distinguish the four executable demos from blocked future ideas. No Odoo connection, live mode, ML claim, persistent user data or production action is in scope.

## Requirements and data
Discover catalogue rows and scenario folders at request time; take runnable status only from the engine registry plus the existence of a scenario README, example input and run.py. Use README sections for implemented scenario details. Future entries derive from the catalogue and future-ideas table. The default input is the checked-in synthetic example; optional custom JSON must be explicitly provided, size-limited and never retained. Display output returned by the actual runner. Do not create sample results or statistics. No additional runtime dependencies beyond Python 3.9+.

## Success metrics and acceptance
The dashboard displays 23 items, four runnable DEMOs and dynamic categories. All four runners complete via the API with output equal to their CLI output; invalid input fails without leaking server internals; blocked and live runs are rejected. Users can complete search → details → run → result → history → next run on desktop and tablet. History is in process memory only and resets on restart.

## Risks and open questions
The application has no authentication; bind it to loopback only. Browser input may contain sensitive data, so do not persist it or use real production records. Production hosting, roles, data retention, approved Odoo API, service authentication and live-mode permissions remain unanswered and block deployment beyond local demos. Source catalogue rows may change format; parsing fails visibly rather than inventing metadata.
