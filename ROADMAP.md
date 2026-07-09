# Roadmap — Task/Project Management API

Hour-by-hour build order. Finish each hour's slice and commit before moving on. Try everything yourself first; the whole point of this project is minimal help. When stuck, read the DRF docs, then your own `PROJECT_BRIEF.md`, then me — and only with a specific question and your attempt in hand.

## Hour 1 — Scaffolding & models
- New project + app(s). Install DRF, simplejwt, django-filter, drf-spectacular.
- Write all models: Project, Membership (through-model), Task, Tag, Comment, Attachment, ActivityLog.
- `makemigrations` + `migrate`, register everything in admin.
- Checkpoint: `manage.py check` clean, objects creatable in admin.

## Hour 2 — Auth
- JWT register/login/refresh, `GET /me/`.
- Make sure `role` and other sensitive fields are read-only on `/me/`.
- Checkpoint: get tokens for two different users via curl/Postman.

## Hour 3 — Projects & memberships
- Project CRUD. List returns only projects the user is a member of.
- Auto-create an `owner` Membership when a project is created.
- Member add/remove endpoints with owner/admin-only permission.
- Checkpoint: user A creates a project, adds user B; B now sees it, a stranger doesn't.

## Hour 4 — Tasks (core CRUD + custom permissions)
- Task CRUD scoped to project. Write the custom membership-based permission class here.
- Enforce: only project members can create/see tasks in that project.
- Checkpoint: non-member gets 403/404; member gets full access.

## Hour 5 — Relationships & validation
- Wire up M2M: `assignees` and `tags`.
- Enforce rule #1 (assignees must be project members) and rule #4 (tag scoping) in the serializer.
- Enforce constrained status transitions (rule #3).
- Checkpoint: assigning a non-member is rejected; illegal status jump is rejected.

## Hour 6 — Comments, attachments, ordering
- Nested comments under task.
- Attachment upload (multipart) with extension + size validation.
- `move`/reorder action for `position`.
- Throttle comment-create and attachment-upload.
- Checkpoint: upload a valid + invalid file; reorder tasks; both behave.

## Hour 7 — Signals, activity feed, bulk ops
- Signals writing to ActivityLog on task create, status change, member add. Use `getattr(instance, "_previous_status", None)` with a default — don't repeat the fragile pattern from last time.
- Activity feed endpoint.
- Bulk task update (`many=True`).
- Checkpoint: change a task status → an ActivityLog row appears; bulk-update 3 tasks in one call.

## Hour 8 — Filtering, docs, polish
- Filtering/search/ordering/pagination on tasks and projects.
- `drf-spectacular` schema — run `manage.py spectacular` and fix any errors (custom actions/permissions are the usual culprits).
- Tidy status codes and error messages.
- Checkpoint: schema generates clean; filters work.

## Hour 9–10 — Tests
Write meaningful tests, not coverage padding. Prioritize the three trickiest areas:
1. The permission matrix (member vs admin vs owner vs non-member across each action).
2. The validations (assignee-must-be-member, status-transition rules, tag scoping, file validation).
3. The status-change signal writing to ActivityLog.

## Stretch (only if cruising)
- Comment mentions (`@user`) that notify via a Celery task.
- Per-project webhooks on task completion.
- Saved filters / "my tasks across all projects" view.
