# Ackredit Developer Bible

This directory is the single source of truth for Ackredit development. It contains
strategic definitions, technical specifications, the current state of the project, and
the issue-backed lifecycle of bugs and proposals.

Suite-wide policy lives in `uibcdf/molsyssuite`; see [`../MOLSYSSUITE_GUIDE.md`](../MOLSYSSUITE_GUIDE.md)
and [`../AGENTS.md`](../AGENTS.md) for the ownership boundary.

## Orientation

For resuming current work, start with the **[Development checkpoint](checkpoint.md)**:
verified delivery, remaining owner issues, working-state limits and the next steps.
It links to the maintained records below rather than replacing them.

1.  **[Vision and Concept](vision.md):** What is Ackredit? What is it for? What is its differential value?
    [Architecture](architecture.md) explains declarations, sessions, captures,
    portable results and component boundaries.
2.  **[Project Status](status.md):** What is already working? What is work-in-progress? What is missing?
3.  **[Roadmap](roadmap.md):** Where are we going and what are the next milestones?
4.  **[Decision Log](decisions.md):** Why were things done this way? What decisions are still pending?
5.  **[Function-provider Contract Review](function_provider_contract_review.md):** Accepted bounded guarantees, verified 0.11.0 delivery and separate consumer handoff.
6.  **[Workflow and Standards](workflow.md):** How to contribute, code standards, and validation.

## Reporting lifecycle

7.  **[Reporting Protocol](reporting_protocol.md):** How bugs and proposals are filed, tracked and closed.
8.  **[Pending bugs](pending_bugs/README.md):** Open defects.
9.  **[Pending proposals](pending_proposals/README.md):** Open proposals.
10. **[Archive](archive/README.md):** Resolved, withdrawn and superseded records. Archive, never delete.

Every queued record starts from [`templates/report.md`](templates/report.md) and carries an
owning GitHub issue. Regenerate the indexes after any lifecycle change:

```bash
python devtools/devguide_index.py
python devtools/devguide_index.py --check
```

---
*If you are new to the project, start with [Vision and Concept](vision.md).*
