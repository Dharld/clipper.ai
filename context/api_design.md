Here’s a **small, clean API design** you can drop in a doc.
Simple descriptions + **Data In / Data Out** with tiny JSON.

---

# ClipForge API (MVP)

Base URL: `https://api.clipforge.app`

Auth: Bearer token (future). For MVP you can skip.

---

## 1) Create Job

Start a new project and get a signed URL to upload the source video.

**POST** `/jobs/create`

**Data In**

```json
{
  "filename": "episode.mp4",
  "content_type": "video/mp4",
  "duration_hint_sec": 1800
}
```

**Data Out**

```json
{
  "project_id": "prj_123",
  "upload_url": "https://s3...signed",
  "status": "queued",
  "max_size_mb": 2048
}
```

---

## 2) Start Processing

Call after the upload finishes.

**POST** `/jobs/start`

**Data In**

```json
{ "project_id": "prj_123" }
```

**Data Out**

```json
{
  "project_id": "prj_123",
  "status": "processing"
}
```

---

## 3) Get Job Status (poll)

Returns project status and (once ready) the clip suggestions with preview links.

**GET** `/jobs/{project_id}`

**Data Out**

```json
{
  "project_id": "prj_123",
  "status": "preview_ready",        // queued | processing | preview_ready | exporting | done | failed
  "error_message": null,
  "clips": [
    {
      "id": "c1",
      "start_sec": 123.4,
      "end_sec": 156.7,
      "title": "The turning point",
      "reason": "punchy quote",
      "score": 0.86,
      "snapped_to_pause": true,
      "preview_url": "https://s3.../previews/prj_123/c1_low.mp4"
    }
  ]
}
```

---

## 4) Export Selected Clips

Cuts full-quality clips for download.

**POST** `/export`

**Data In**

```json
{
  "project_id": "prj_123",
  "clip_ids": ["c1","c3","c4"],
  "quality": "720p"
}
```

**Data Out**

```json
{
  "project_id": "prj_123",
  "status": "exporting",
  "exports": [
    { "id": "c1", "url": "https://s3.../finals/prj_123/c1.mp4" }
  ]
}
```

---

## 5) (Optional) Delete Project

Clean up DB rows and S3 objects per retention rules.

**DELETE** `/jobs/{project_id}`

**Data Out**

```json
{ "deleted": true }
```

---

## Objects (for reference)

**Clip**

```json
{
  "id": "c1",
  "start_sec": 0.0,
  "end_sec": 30.0,
  "title": "Short title",
  "reason": "why it’s good",
  "score": 0.0,
  "snapped_to_pause": true,
  "preview_url": null,
  "final_url": null,
  "state": "suggested"
}
```

**Project**

```json
{
  "project_id": "prj_123",
  "status": "processing",
  "source_video_url": "s3://uploads/prj_123/source.mp4",
  "created_at": "2025-06-01T12:00:00Z"
}
```

---

## Errors (tiny)

* `400` invalid input
* `404` not found
* `409` wrong state (e.g., export before previews)
* `500` internal error

**Error shape**

```json
{ "error": "message", "code": "bad_request" }
```

---

## Notes

* Upload is direct to S3 using `upload_url`.
* Queue events drive processing; DB is source of truth.
* Keep previews low bitrate; export on demand.
