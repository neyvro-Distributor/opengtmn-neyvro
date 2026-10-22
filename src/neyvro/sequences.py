"""Declarative multichannel sequence compiler and deterministic runtime."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from hashlib import sha256
from threading import RLock
from typing import Any, Callable, Iterable

CONTRACTS = ("neyvro_create_campaign_draft", "neyvro_propose_campaign", "neyvro_get_campaign", "neyvro_pause_campaign", "neyvro_get_campaign_status")
CHANNELS = {"email", "linkedin_assisted", "authorized_social"}
PRECONDITIONS = {"sender_available", "recipient_eligible", "approval_current"}
STOP_CONDITIONS = {"reply", "unsubscribe", "hard_bounce", "meeting_booked", "customer_cancelled"}


class CampaignState(StrEnum):
    DRAFT = "DRAFT"
    PROPOSED = "PROPOSED"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    SCHEDULED = "SCHEDULED"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"


@dataclass(frozen=True)
class SequenceStep:
    step_id: str
    channel: str
    recipient: dict[str, str]
    sender: dict[str, str]
    message: dict[str, str]
    scheduled_time: datetime
    preconditions: tuple[str, ...]
    stop_conditions: tuple[str, ...]
    approval_version: str


@dataclass(frozen=True)
class CampaignSpec:
    campaign_id: str
    tenant_id: str
    approval_version: str
    steps: tuple[SequenceStep, ...]
    timezone: str = "UTC"
    version: str = "1"


@dataclass(frozen=True)
class Eligibility:
    sender_available: bool = False
    recipient_eligible: bool = False
    approval_current: bool = False
    reason: str | None = None


@dataclass(frozen=True)
class CompiledSequence:
    campaign_id: str
    state: CampaignState
    jobs: tuple[dict[str, Any], ...]
    transitions: tuple[dict[str, str], ...]


@dataclass
class CampaignRuntime:
    spec: CampaignSpec
    state: CampaignState = CampaignState.DRAFT
    stop_reason: str | None = None
    approval_version: str | None = None
    dispatched_jobs: set[str] = field(default_factory=set)
    processed_events: set[str] = field(default_factory=set)
    _lock: RLock = field(default_factory=RLock, repr=False)

    def transition(self, target: CampaignState, *, approval_version: str | None = None) -> dict[str, Any]:
        with self._lock:
            allowed = {
                CampaignState.DRAFT: {CampaignState.PROPOSED},
                CampaignState.PROPOSED: {CampaignState.PENDING_APPROVAL},
                CampaignState.PENDING_APPROVAL: {CampaignState.APPROVED, CampaignState.CANCELLED},
                CampaignState.APPROVED: {CampaignState.SCHEDULED, CampaignState.CANCELLED},
                CampaignState.SCHEDULED: {CampaignState.RUNNING, CampaignState.PAUSED, CampaignState.CANCELLED, CampaignState.FAILED},
                CampaignState.RUNNING: {CampaignState.PAUSED, CampaignState.COMPLETED, CampaignState.CANCELLED, CampaignState.FAILED},
                CampaignState.PAUSED: {CampaignState.SCHEDULED, CampaignState.CANCELLED},
            }
            if target not in allowed.get(self.state, set()):
                return {"status": "blocked", "state": self.state.value, "reason": f"invalid transition to {target.value}"}
            if target == CampaignState.APPROVED:
                if approval_version != self.spec.approval_version:
                    return {"status": "blocked", "state": self.state.value, "reason": "approval version is missing, stale, or revoked"}
                self.approval_version = approval_version
            self.state = target
            return {"status": "ok", "state": self.state.value}

    def handle_event(self, event: str, event_id: str) -> dict[str, Any]:
        with self._lock:
            if event_id in self.processed_events:
                return {"status": "duplicate_event", "state": self.state.value}
            self.processed_events.add(event_id)
            if event not in STOP_CONDITIONS:
                return {"status": "ignored", "state": self.state.value}
            if self.state in {CampaignState.COMPLETED, CampaignState.CANCELLED}:
                return {"status": "already_stopped", "state": self.state.value}
            self.stop_reason = event
            self.state = CampaignState.CANCELLED
            return {"status": "stopped", "state": self.state.value, "reason": event}

    def dispatch(self, step_id: str, eligibility: Eligibility, *, job_id: str | None = None) -> dict[str, Any]:
        with self._lock:
            step = next((item for item in self.spec.steps if item.step_id == step_id), None)
            if step is None:
                return {"status": "not_found", "state": self.state.value}
            if self.state not in {CampaignState.SCHEDULED, CampaignState.RUNNING}:
                return {"status": "blocked", "state": self.state.value, "reason": "campaign is not dispatchable"}
            if not eligibility.sender_available or not eligibility.recipient_eligible or not eligibility.approval_current:
                return {"status": "blocked", "state": self.state.value, "reason": eligibility.reason or "eligibility or approval recheck failed"}
            if step.approval_version != self.spec.approval_version or self.approval_version != self.spec.approval_version:
                return {"status": "blocked", "state": self.state.value, "reason": "approval version revoked or stale"}
            deterministic_job = job_id or _job_id(self.spec, step)
            if deterministic_job in self.dispatched_jobs:
                return {"status": "duplicate_job", "state": self.state.value, "job_id": deterministic_job}
            self.dispatched_jobs.add(deterministic_job)
            self.state = CampaignState.RUNNING
            return {"status": "dispatched_to_authorized_backend", "state": self.state.value, "job_id": deterministic_job, "external_send_executed": False}


def _job_id(spec: CampaignSpec, step: SequenceStep) -> str:
    raw = "|".join((spec.tenant_id, spec.campaign_id, spec.version, step.step_id, step.recipient.get("buyer_id", ""), step.approval_version))
    return "job-" + sha256(raw.encode("utf-8")).hexdigest()[:20]


def compile_sequence(spec: CampaignSpec) -> CompiledSequence:
    """Validate and compile data-only steps into deterministic jobs and transitions."""
    if not spec.steps:
        raise ValueError("campaign must contain at least one step")
    seen: set[str] = set()
    jobs: list[dict[str, Any]] = []
    for step in spec.steps:
        if step.step_id in seen:
            raise ValueError(f"duplicate step_id: {step.step_id}")
        seen.add(step.step_id)
        if step.channel not in CHANNELS:
            raise ValueError(f"unsupported channel: {step.channel}")
        invalid_pre = set(step.preconditions) - PRECONDITIONS
        invalid_stop = set(step.stop_conditions) - STOP_CONDITIONS
        if invalid_pre:
            raise ValueError(f"unsupported precondition(s): {sorted(invalid_pre)}")
        if invalid_stop:
            raise ValueError(f"unsupported stop condition(s): {sorted(invalid_stop)}")
        if step.approval_version != spec.approval_version:
            raise ValueError(f"step {step.step_id} has stale approval version")
        jobs.append({"job_id": _job_id(spec, step), "step_id": step.step_id, "channel": step.channel, "scheduled_time": step.scheduled_time.isoformat(), "preconditions": list(step.preconditions), "stop_conditions": list(step.stop_conditions), "approval_version": step.approval_version})
    jobs.sort(key=lambda item: (item["scheduled_time"], item["step_id"]))
    transitions = tuple({"from": source.value, "to": target.value} for source, targets in ((CampaignState.DRAFT, (CampaignState.PROPOSED,)), (CampaignState.PROPOSED, (CampaignState.PENDING_APPROVAL,)), (CampaignState.PENDING_APPROVAL, (CampaignState.APPROVED,)), (CampaignState.APPROVED, (CampaignState.SCHEDULED,)), (CampaignState.SCHEDULED, (CampaignState.RUNNING,)), (CampaignState.RUNNING, (CampaignState.COMPLETED,)),) for target in targets)
    return CompiledSequence(spec.campaign_id, CampaignState.DRAFT, tuple(jobs), transitions)


def schedule_compiled(runtime: CampaignRuntime, scheduler: Callable[[dict[str, Any]], dict[str, Any]] | None = None) -> dict[str, Any]:
    """Submit deterministic jobs to an injected scheduler, never to an arbitrary callable from a model."""
    compiled = compile_sequence(runtime.spec)
    if runtime.state != CampaignState.SCHEDULED:
        return {"status": "blocked", "reason": "campaign must be SCHEDULED before scheduler submission", "jobs": []}
    if scheduler is None:
        return {"status": "disabled", "reason": "Neyvro scheduler adapter is not configured", "jobs": list(compiled.jobs), "external_send_executed": False}
    return {"status": "scheduled", "jobs": [scheduler(job) for job in compiled.jobs], "external_send_executed": False}


def safe_contract(name: str, payload: dict[str, Any], transport: Callable[[str, dict[str, Any]], dict[str, Any]] | None = None) -> dict[str, Any]:
    """Call an injected campaign adapter, otherwise remain disabled and non-sending."""
    if name not in CONTRACTS:
        raise ValueError(f"unknown campaign contract: {name}")
    if transport is None:
        return {"status": "disabled", "contract": name, "reason": "Neyvro campaign/scheduler adapter is not configured", "data": None, "external_send_executed": False}
    result = transport(name, payload)
    result["external_send_executed"] = False
    return result
