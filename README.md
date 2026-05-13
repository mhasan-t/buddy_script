# BuddyScript - Social Media API

## Quick Start

### 1. Setup Environment

```bash
cp .env.example .env
# Edit .env with your database and Redis settings
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run docker containers

```
docker compose -d up
```

### 4. Run Migrations

```bash
python manage.py migrate
```

### 5. Start Development Server

```bash
python manage.py runserver
```

### 6. Access the API

- **API Endpoints**: http://localhost:8000/api/
- **Swagger UI**: http://localhost:8000/api/docs/swagger/
- **ReDoc**: http://localhost:8000/api/docs/redoc/

## Project Structure

```
buddyscript/
├── buddyscript/              # Main Django project
│   ├── settings.py           # Configuration
│   ├── urls.py               # Root URL routing
│   ├── wsgi.py
│   └── asgi.py
├── core/                     # Core app
│   ├── models/               # Data models
│   │   ├── base.py
│   │   ├── user.py
│   │   ├── post.py
│   │   ├── comment.py
│   │   ├── reaction.py
│   │   ├── refresh_token_record.py
│   │   ├── post_image.py
│   │   └── __init__.py
│   ├── serializers/          # DRF serializers
│   │   ├── user.py
│   │   ├── post.py
│   │   ├── comment.py
│   │   ├── reaction.py
│   │   ├── post_image.py
│   │   └── __init__.py
│   ├── views/                # API views and viewsets
│   │   ├── user_views.py
│   │   ├── posts_views.py
│   │   ├── comment_views.py
│   │   ├── reaction_views.py
│   │   └── __init__.py
│   ├── urls.py               # API routing
│   ├── permissions.py        # Custom permissions
│   ├── pagination.py         # Pagination classes
│   ├── migrations/           # Django migrations
│   └── admin.py
├── manage.py
├── requirements.txt
├── .env.example
├── API.md                    # API documentation
└── test_api.py               # Test client
```

## API Routes

### Authentication

- `POST /api/auth/signup/` - Register new user
- `POST /api/auth/login/` - Get access and refresh tokens
- `POST /api/auth/refresh/` - Refresh access token
- `POST /api/auth/logout/` - Revoke current refresh token
- `POST /api/auth/logout-all/` - Revoke all refresh tokens for the user
- `GET /api/user/me/` - Retrieve current authenticated user

### Posts

- `GET /api/posts/recent/` - Get recent public posts with comments (cached 10s)
- `GET /api/posts/` - List authenticated user's posts
- `GET /api/posts/{id}/` - Retrieve a post
- `POST /api/posts/` - Create a post
- `PATCH /api/posts/{id}/` - Update a post (author only)
- `DELETE /api/posts/{id}/` - Delete a post (author only)

### Comments

- `GET /api/posts/{post_id}/comments/` - Get top-level comments for a post (cached 3s when no cursor)
- `GET /api/comments/` - List all comments
- `GET /api/comments/{id}/` - Retrieve a comment
- `POST /api/comments/` - Create a comment or reply
- `PATCH /api/comments/{id}/` - Update a comment (author only)
- `DELETE /api/comments/{id}/` - Delete a comment (author only)
- `GET /api/comments/{comment_id}/replies/` - List replies to a comment

### Reactions

- `POST /api/reactions/` - Create or update a reaction
- `DELETE /api/reactions/{id}/` - Delete a reaction

## Testing

Run the comprehensive API test client:

```bash
python test_api.py
```

This will:

1. Sign up a new user
2. Log in and get JWT tokens
3. Create a post
4. Get recent posts
5. Add comments and replies
6. Add reactions
7. Verify counts are updated

## Database Models

### User

- UUID primary key
- Email (unique)
- First/Last name
- Django auth fields (password, is_staff, is_active, etc.)
- Timestamps

### Post

- UUID primary key
- User (ForeignKey with CASCADE)
- Content (text)
- Image URL
- Public/private flag
- Reaction count
- Comment count
- Timestamps with indexes on user, public status, and creation date

### Comment

- UUID primary key
- Post (ForeignKey with CASCADE)
- User (ForeignKey)
- Parent (self-ForeignKey for replies, null for top-level)
- Content (required text)
- Reaction count
- Reply count
- Indexes on post, parent, and creation date

### Reaction

- UUID primary key
- Author (User ForeignKey with CASCADE)
- Content Type (for polymorphic relations)
- Object ID (UUID)
- Reaction type (default: "like")
- Timestamps
- Unique constraint: (author, content_type, object_id)

## Development

### Create Superuser

```bash
python manage.py createsuperuser
```

### Access Admin Panel

http://localhost:8000/admin/

### Make Migrations After Model Changes

```bash
python manage.py makemigrations
python manage.py migrate
```
