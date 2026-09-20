(Dev_Onboarding)=
# Onboarding & Development Workflow

Welcome to the Ackredit team! This guide will help you get your environment ready for contribution.

## Setup
1.  **Clone the repo:**
    ```bash
    git clone https://github.com/uibcdf/ackredit
    cd ackredit
    ```
2.  **Environment:** We recommend using Python 3.10+. No external dependencies are required for the core, but `pytest` is needed for development.
    ```bash
    pip install pytest
    ```

## Development Cycle
1.  **Iterate:** Make your changes in `ackredit/`.
2.  **Test:** Always run the tests before committing.
    ```bash
    pytest
    ```
3.  **Document:** If you add a feature, update the relevant file in `docs/content/developer_guide/`.

## Coding Standards
-   **Type Hints:** Use them everywhere. We target Python 3.10+ and use `from __future__ import annotations`.
-   **Surgical Changes:** Keep PRs focused.
-   **No Dependencies:** Avoid adding external dependencies to `[project.dependencies]` unless absolutely necessary and discussed in `decisions.md`.

## Project Structure
-   `ackredit/core/`: The "brain". Registry, Collector, and main logic.
-   `ackredit/formats/`: Renderers for different outputs.
-   `tests/`: Where the magic is verified.
