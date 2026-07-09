# Project Brief — Task/Project Management API

A small Trello/Jira-style backend: **Projects** contain **Tasks**, tasks have **Comments** and **Tags**, and tasks can be assigned to multiple project members. JSON API only (DRF), JWT auth. Target scope ~8–10 hours, similar depth to the booking project — but it deliberately exercises muscles that one didn't: many-to-many relationships, three-level nesting, file uploads, list reordering, and bulk operations.

Write this spec out in your own words before building. Don't read solutions first — build hour by hour (see `ROADMAP.md`) and come back only when genuinely stuck on something specific.

## Roles
- `member` — normal user. Can be added to projects.
- Project-level roles (per membership, not global): `owner`, `admin`, `member`.
  - **owner**: created the project; can delete it, manage members, everything.
  - **admin**: manage tasks and members, cannot delete the project.
  - **member**: create/edit tasks and comments within the project.

Global role is just the authenticated user; the interesting permissions live at the **project membership** level. This is the key difference from the booking project's flat staff/admin roles.

## Models
- **User** — Django user (or a thin profile). JWT auth.
- **Project** — `name`, `description`, `owner` (FK User), `created_at`, `is_archived`.
- **Membership** — through-model linking `user` ↔ `project` with a `role` field (`owner`/`admin`/`member`) and `joined_at`. A user belongs to a project *only* via a Membership.
- **Task** — `project` (FK), `title`, `description`, `status` (`todo`/`in_progress`/`done`), `priority`, `assignees` (M2M to User), `tags` (M2M to Tag), `position` (int, for kanban ordering), `due_date`, `created_by`, timestamps.
- **Tag** — `name`, `project` (FK) — tags are scoped to a project, `unique_together(project, name)`.
- **Comment** — `task` (FK), `author` (FK), `body`, `created_at`.
- **Attachment** — `task` (FK), `file` (upload), `uploaded_by`, `uploaded_at`. Validate type + size.
- **ActivityLog** — `project` (FK), `actor`, `verb`, `target` (string/GenericFK if ambitious), `created_at`. Written by signals, same pattern as your old `BookingStatusLog`.

## Endpoints (rough)
- `POST /auth/register`, `POST /auth/token`, `POST /auth/token/refresh`, `GET /me/`
- `Projects`: list (only projects you're a member of), create, retrieve, update, delete (owner only), archive.
- `Members`: `GET/POST /projects/{id}/members/`, `DELETE /projects/{id}/members/{userId}/` — nested under project.
- `Tasks`: full CRUD, nested or filtered by project. Support filtering, search, ordering.
- `Comments`: nested under task — `GET/POST /tasks/{id}/comments/`.
- `Tags`: CRUD scoped to project.
- `Attachments`: `POST /tasks/{id}/attachments/` (multipart), delete.
- `Activity feed`: `GET /projects/{id}/activity/`.

## Business rules to enforce (the meat)
1. A task's `assignees` must all be **members of that task's project**. Reject otherwise — this is your equivalent of the old overlap-validation rule.
2. Only project `owner` can delete the project or remove/demote the owner. Only `owner`/`admin` can add or remove members.
3. `status` transitions are constrained, not free-for-all: `todo → in_progress → done`, and `done → in_progress` to reopen. No jumping `todo → done` directly (decide the rule and enforce it in the serializer).
4. Tags and comments/tasks are always scoped to their project — a user can't attach a tag from project A to a task in project B.
5. Attachments: whitelist extensions (e.g. pdf/png/jpg/docx), cap file size, validate in the serializer.
6. `position` lets clients reorder tasks within a column. Provide a clean way to reorder (e.g. a `PATCH /tasks/{id}/move/` action taking a new position/status) without corrupting the ordering.
7. Bulk update: `PATCH /tasks/bulk/` to change status/assignee on several tasks at once — needs a `many=True` serializer shape.

## Cross-cutting requirements
- **Permissions**: write custom permission classes at the project-membership level. Don't inline the checks in views.
- **Serialization**: nested reads (task shows tags, assignee names, comment count) but guard write/leak of private fields. Use different serializers for read vs write where it helps.
- **Filtering / search / ordering / pagination** on task and project lists (`django-filter` + DRF filters).
- **Throttling** on the comment-create and attachment-upload endpoints.
- **Signals** write to `ActivityLog` on task create, status change, and member add.
- **OpenAPI** via `drf-spectacular`; make sure `manage.py spectacular` generates cleanly.
- **Tests last** — see roadmap.
