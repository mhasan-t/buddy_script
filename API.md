## API Documentation

### Interactive Docs

- **Swagger UI**: `http://localhost:8000/api/docs/swagger/`
- **ReDoc**: `http://localhost:8000/api/docs/redoc/`
- **Schema**: `http://localhost:8000/api/schema/`

## Authentication

All endpoints except signup/login require JWT authentication.

### Headers

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

## Endpoints

### 1. Authentication

#### Sign Up

```http
POST /api/auth/signup/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepass123",
  "first_name": "John",
  "last_name": "Doe"
}

Response: 201 Created
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe"
}
```

#### Login

```http
POST /api/auth/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepass123"
}

Response: 200 OK
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Refresh Token

```http
POST /api/auth/refresh/
Content-Type: application/json

{
  "refresh": "<refresh_token>"
}

Response: 200 OK
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 2. Recent Public Posts

Get paginated feed of recent public posts with latest 2 comments each.

**Features:**

- Cursor-based pagination
- Cached for 30 seconds
- Returns latest 2 comments per post
- Protected route (requires authentication)

```http
GET /api/posts/recent/?cursor=<optional_cursor>
Authorization: Bearer <access_token>

Response: 200 OK
{
  "count": 42,
  "next": "http://localhost:8000/api/posts/recent/?cursor=cD0yODI=",
  "previous": null,
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "user": {
        "id": "660e8400-e29b-41d4-a716-446655440001",
        "first_name": "John",
        "last_name": "Doe",
        "email": "user@example.com"
      },
      "content": "Hello, world!",
      "image_url": "https://example.com/image.jpg",
      "is_public": true,
      "reaction_count": 5,
      "comment_count": 2,
      "created_at": "2026-05-10T12:00:00Z",
      "updated_at": "2026-05-10T12:05:00Z",
      "latest_comments": [
        {
          "id": "770e8400-e29b-41d4-a716-446655440002",
          "user": {
            "id": "880e8400-e29b-41d4-a716-446655440003",
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane@example.com"
          },
          "content": "Great post!",
          "created_at": "2026-05-10T12:10:00Z"
        }
      ]
    }
  ]
}
```

### 3. Posts (CRUD)

#### Create Post

```http
POST /api/posts/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "content": "My new post",
  "image_url": "https://example.com/image.jpg",
  "is_public": true
}

Response: 201 Created
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user": {...},
  "content": "My new post",
  "image_url": "https://example.com/image.jpg",
  "is_public": true,
  "reaction_count": 0,
  "comment_count": 0,
  "created_at": "2026-05-10T12:00:00Z",
  "updated_at": "2026-05-10T12:00:00Z"
}
```

#### List User Posts

```http
GET /api/posts/
Authorization: Bearer <access_token>

Response: 200 OK
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [...]
}
```

#### Retrieve Post

```http
GET /api/posts/{post_id}/
Authorization: Bearer <access_token>

Response: 200 OK
{...}
```

#### Update Post (Author Only)

```http
PATCH /api/posts/{post_id}/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "content": "Updated content",
  "is_public": false
}

Response: 200 OK
{...}
```

#### Delete Post (Author Only)

```http
DELETE /api/posts/{post_id}/
Authorization: Bearer <access_token>

Response: 204 No Content
```

### 4. Comments (CRUD + Replies)

#### Create Comment or Reply

```http
POST /api/comments/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "post": "550e8400-e29b-41d4-a716-446655440000",
  "content": "Great post!",
  "parent": null  # Omit for regular comments, provide parent comment ID for replies
}

Response: 201 Created
{
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "post": "550e8400-e29b-41d4-a716-446655440000",
  "parent": null,
  "user": {...},
  "content": "Great post!",
  "reaction_count": 0,
  "reply_count": 0,
  "created_at": "2026-05-10T12:10:00Z",
  "updated_at": "2026-05-10T12:10:00Z"
}
```

#### Get Post Comments

Cached for 10 seconds.

```http
GET /api/posts/{post_id}/comments/
Authorization: Bearer <access_token>

Response: 200 OK
[
  {
    "id": "770e8400-e29b-41d4-a716-446655440002",
    "post": "550e8400-e29b-41d4-a716-446655440000",
    "parent": null,
    "user": {...},
    "content": "Great post!",
    "reaction_count": 1,
    "reply_count": 1,
    "created_at": "2026-05-10T12:10:00Z",
    "updated_at": "2026-05-10T12:10:00Z"
  }
]
```

#### List Comments

Filter by post_id query parameter.

```http
GET /api/comments/?post_id={post_id}
Authorization: Bearer <access_token>

Response: 200 OK
{...}
```

#### Update Comment (Author Only)

```http
PATCH /api/comments/{comment_id}/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "content": "Updated comment"
}

Response: 200 OK
{...}
```

#### Delete Comment (Author Only)

On deletion, automatically decreases parent comment's `reply_count` or post's `comment_count`.

```http
DELETE /api/comments/{comment_id}/
Authorization: Bearer <access_token>

Response: 204 No Content
```

### 5. Reactions

React to posts or comments. Creating a reaction with the same target from the same author replaces the reaction type.

#### Create/Update Reaction

```http
POST /api/reactions/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "target_type": "post",  # "post" or "comment"
  "target_id": "550e8400-e29b-41d4-a716-446655440000",
  "reaction_type": "like"
}

Response: 201 Created (if new) or 200 OK (if updating)
{
  "id": "990e8400-e29b-41d4-a716-446655440004",
  "author": {...},
  "target_type": "post",
  "target_id": "550e8400-e29b-41d4-a716-446655440000",
  "target": "post",
  "reaction_type": "like",
  "created_at": "2026-05-10T12:20:00Z",
  "updated_at": "2026-05-10T12:20:00Z"
}
```

#### Delete Reaction

On deletion, automatically decreases the target's `reaction_count`.

```http
DELETE /api/reactions/{reaction_id}/
Authorization: Bearer <access_token>

Response: 204 No Content
```

## Caching

- **Recent Posts**: 30 seconds TTL
- **Post Comments**: 10 seconds TTL

Caches are automatically invalidated when content changes.

## Performance Optimizations

1. **Database**:
    - Select related (user, parent) to reduce queries
    - Prefetch related (comments) for efficient retrieval
    - Indexed on frequently queried fields

2. **Caching**:
    - Redis-backed caching for public post feed
    - Cache invalidation on content changes

3. **Pagination**:
    - Cursor-based pagination for scalable feeds
    - Prevents performance degradation on large datasets

4. **Transactions**:
    - Atomic operations for comment creation/deletion
    - Ensures consistency when updating counts

## Error Responses

```json
{
	"detail": "Not found."
}
```

```json
{
	"field": ["Error message"]
}
```

Common status codes:

- `200 OK` - Successful GET
- `201 Created` - Successful POST
- `204 No Content` - Successful DELETE
- `400 Bad Request` - Validation error
- `401 Unauthorized` - Missing/invalid token
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found

## Example Usage (Python)

See `test_api.py` for a complete test client implementation.

```bash
python test_api.py
```
