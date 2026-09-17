"""Report generation (FR-5.1, FR-5.2): weekly/monthly project reports.

Reports are assembled from task state + meeting records (completed / in progress /
blocked with reasons / decisions / open questions). The LLM is used only to smooth
wording of an already-computed structure — it can never invent progress.
Outputs: Markdown (canonical), PDF (rendered from it), scheduled email.
"""

from __future__ import annotations

from datetime import date
from uuid import UUID


async def generate_report(project_id: UUID, period_start: date, period_end: date) -> str:
    """Build the canonical Markdown report for a project and period.

    TODO(phase-3): implement assembly + wording pass + PDF export + scheduling.
    """
    raise NotImplementedError("TODO(phase-3): report generation")
