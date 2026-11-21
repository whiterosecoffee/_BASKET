# Scheduler-ready instruction (not an installed schedule)

Controller creates exactly one initial hourly trigger, pinned to the existing
authorized persistent workstation session using its private routing identity.
Do not place session identifiers or workstation paths in public scheduler examples.
If routing to that exact session cannot be verified, park and report the gap;
do not create a cloud replacement or another worker. No scheduler was created here.

Prompt for the controller to bind to the private session target:

> Resume the existing Handoff owner on the authorized workstation and scoped
> branch. Verify actual hostname/environment, ownership and filesystem access.
> If offline, inaccessible, stale or conflicting, park without alternate execution.
> Read the latest private ownership claim and objectives-status.json, then refresh
> the canonical GitHub record and only new available conversation material after
> the verified watermark. Keep persisted coverage and unknown ranges separate.
> Coalesce if this owner is active. Pending approval is not inactivity. Duplicate
> wakes and unchanged blockers cause no retry. Evaluate one bounded next action
> using the existing handoff_loop library; continue only in this same authorized
> session/branch/scope. Persist through reread, exclusive lock/CAS, atomic replace
> and readback. Reuse the existing conversation_closeout procedure when needed.
> Never archive, spawn a replacement or transfer ownership automatically. Transfer
> readiness requires verified old-writer retirement and replacement acknowledgement
> of branch, scope, data access and outstanding task. Report scheduling, dispatch,
> execution, publication, acceptance and delivery separately with evidence.

Suggested cadence: `RRULE:FREQ=HOURLY`, exact schedule. The controller must obtain
the automation ID and verify its target; a returned schedule ID proves scheduling
only. First manual bounded wake must show same-session receipt, verified host,
checkpoint reread and a coalesce/no-change or one scoped action receipt. Scheduler
creation without that receipt does not prove execution. Do not duplicate a schedule.
