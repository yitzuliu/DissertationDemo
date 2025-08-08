## State Tracker Step Consistency – Thin Guard (Do Not Block Real-Time Perception)

Status: Proposal (Planned change, not implemented)
Owners: State Tracker / VLM Fallback subsystem
Last updated: 2025-08-08

### Context
The current state update logic includes a conservative consistency check that blocks large forward jumps (>3 steps) to avoid misclassification from a single noisy observation. While protective, this may occasionally delay legitimate updates when the environment clearly indicates a new step or task.

This proposal aligns with the product direction: prioritize immediate real-time perception and only add a thin guard where it prevents obvious errors, without getting in the way of fluid task resumption or restarts.

### Goals
- Keep real-time perception primary: high-confidence observations update immediately.
- Add a minimal “thin guard” only for ambiguous (medium-confidence) forward jumps.
- Preserve fast task switching and task restarts (backward jumps always allowed).
- Keep the system simple; avoid complex activity timers or multi-task concurrency.

### Non-Goals
- Multi-task parallel tracking (we keep a single `current_state`).
- Aggressive memory/window changes (sliding window config stays as-is unless future data suggests otherwise).
- Overriding VLM fallback behavior (low confidence still routes to fallback).

### Design Overview
We introduce a thin guard in the consistency check that only applies to medium-confidence forward jumps that exceed a small threshold. High-confidence updates fully trust the environment. Backward jumps, restarts, or missing recent records are always allowed to update.

### Decision Rules (effective intent)
- Confidence levels (updated to reflect practical model ranges):
  - HIGH ≥ 0.65  (deployments may tune within 0.60–0.65 if needed)
  - MEDIUM 0.40–0.65
  - LOW < 0.40

- Routing (unchanged):
  - LOW: do not update state; route answers via VLM fallback.
  - HIGH/MEDIUM that pass consistency: update state; template answers via QueryProcessor + RAG.

- Thin Guard for step consistency:
  - HIGH: no restriction. Update immediately, any step jump allowed.
  - MEDIUM:
    - If no recent records for the same task: allow update (treat as reasonable).
    - If new step ≤ last step (backward/restart): allow update.
    - If forward jump ≤ 2 steps: allow update.
    - If forward jump > 2 steps: require two consecutive matching observations within a short TTL before updating (debounce). Until confirmed, record as observation only.

### Parameters (tunable, initial defaults)
- high_confidence_threshold: 0.65 (default; tunable within 0.60–0.65 based on model behavior)
- medium_confidence_threshold: 0.40 (existing)
- max_forward_jump_without_confirmation: 2
- consecutive_confirmations_required: 2
- confirmation_ttl_seconds: 10 (time window for counting consecutive matches)
- sliding_window: unchanged (current default size and memory limits)

### Data Structures (minimal, optional)
- `pending_state_candidate` (optional):
  - shape: { task_id: str, step_index: int, first_seen_ts: datetime, count: int }
  - cleared when confirmed, expired (TTL), or a non-matching update occurs.

### Pseudocode (illustrative)
```python
confidence_level = determine_confidence(similarity)

if confidence_level == HIGH:
    update_state(new_task, new_step)
    clear_pending()
elif confidence_level == MEDIUM:
    if no_recent_records_for(new_task):
        update_state(new_task, new_step)
        clear_pending()
    else:
        last_step = last_recent_step_for(new_task)
        step_diff = new_step - last_step

        if new_step <= last_step:
            update_state(new_task, new_step)  # allow backward / restart
            clear_pending()
        elif step_diff <= 2:
            update_state(new_task, new_step)  # small forward jump
            clear_pending()
        else:
            if pending_matches(new_task, new_step, within=confirmation_ttl_seconds):
                increment_pending_count()
            else:
                set_pending_candidate(new_task, new_step)

            if pending_count() >= consecutive_confirmations_required:
                update_state(new_task, new_step)
                clear_pending()
            else:
                # observation only; do not update current_state yet
                pass
else:  # LOW
    # no state update; answers route to VLM fallback as today
    pass
```

### Code Touch Points (when implemented)
- File: `src/state_tracker/state_tracker.py`
  - `_check_state_consistency(...)`: adapt logic to the thin guard rules above.
  - Optionally add in-memory `pending_state_candidate` to `StateTracker`.
  - No changes to `_should_update_state` thresholds at this time (optional tuning later).

- No changes to:
  - `QueryProcessor` routing (LOW → VLM fallback; otherwise template answers).
  - Sliding window size or memory cleanup behavior.

### Rollout Plan
1) Keep current behavior (no code changes) while socializing this proposal.
2) Implement behind a feature flag (e.g., `thin_guard_enabled=true`).
3) Shadow test in dev/staging with telemetry.
4) Enable by default if metrics confirm improvements.

### Telemetry / Metrics
- Answer routing distribution (template vs. fallback) before/after.
- Time-to-correct-step after returning to a task scene.
- Frequency of large forward jumps and how often they needed confirmation.
- User-perceived correctness (manual sampling during trials).

### Risks & Mitigations
- Risk: Delayed legitimate large forward jumps at medium confidence.
  - Mitigation: TTL short (10s) and only 2 confirmations required; HIGH confidence bypasses guard.
- Risk: Added state (`pending_state_candidate`) complexity.
  - Mitigation: Keep it optional and in-memory; clear aggressively on mismatch or timeout.

### Alternatives Considered
- Remove consistency check entirely (pure perception). Rejected for now due to single-observation false positives.
- Increase thresholds only. Helps routing, but does not address medium-confidence false jumps.
- Activity/inactivity timers or multi-task parallel tracking. Out of scope for simplicity.

### Summary
This proposal preserves the product principle “real-time perception first” while adding a minimal safety net only where ambiguity is highest (medium confidence large forward jumps). High confidence remains fully real-time, backward jumps and restarts stay seamless, and VLM fallback routing is unchanged.


