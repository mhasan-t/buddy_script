import requests
import json
from typing import Optional

BASE_URL = "http://localhost:8000/api"

class APIClient:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.access_token = None
        self.refresh_token = None

    def signup(self, email: str, password: str, first_name: str, last_name: str) -> dict:
        response = requests.post(
            f"{self.base_url}/auth/signup/",
            json={
                "email": email,
                "password": password,
                "first_name": first_name,
                "last_name": last_name,
            },
        )
        return response.json()

    def login(self, email: str, password: str) -> dict:
        response = requests.post(
            f"{self.base_url}/auth/login/",
            json={"email": email, "password": password},
        )
        data = response.json()
        self.access_token = data.get("access")
        self.refresh_token = data.get("refresh")
        return data

    def refresh_access_token(self) -> dict:
        response = requests.post(
            f"{self.base_url}/auth/refresh/",
            json={"refresh": self.refresh_token},
        )
        data = response.json()
        self.access_token = data.get("access")
        return data

    def _get_headers(self):
        headers = {"Content-Type": "application/json"}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers

    def create_post(self, content: str, image_url: Optional[str] = None, is_public: bool = True) -> dict:
        response = requests.post(
            f"{self.base_url}/posts/",
            json={
                "content": content,
                "image_url": image_url or "",
                "is_public": is_public,
            },
            headers=self._get_headers(),
        )
        return response.json()

    def get_posts(self) -> dict:
        response = requests.get(
            f"{self.base_url}/posts/",
            headers=self._get_headers(),
        )
        return response.json()

    def get_recent_posts(self, cursor: Optional[str] = None) -> dict:
        params = {}
        if cursor:
            params["cursor"] = cursor
        response = requests.get(
            f"{self.base_url}/posts/recent/",
            params=params,
            headers=self._get_headers(),
        )
        return response.json()

    def update_post(self, post_id: str, content: Optional[str] = None, image_url: Optional[str] = None) -> dict:
        data = {}
        if content:
            data["content"] = content
        if image_url:
            data["image_url"] = image_url
        response = requests.patch(
            f"{self.base_url}/posts/{post_id}/",
            json=data,
            headers=self._get_headers(),
        )
        return response.json()

    def delete_post(self, post_id: str) -> int:
        response = requests.delete(
            f"{self.base_url}/posts/{post_id}/",
            headers=self._get_headers(),
        )
        return response.status_code

    def get_post_comments(self, post_id: str) -> dict:
        response = requests.get(
            f"{self.base_url}/posts/{post_id}/comments/",
            headers=self._get_headers(),
        )
        return response.json()

    def create_comment(self, post_id: str, content: str, parent_id: Optional[str] = None) -> dict:
        data = {
            "post": post_id,
            "content": content,
        }
        if parent_id:
            data["parent"] = parent_id
        response = requests.post(
            f"{self.base_url}/comments/",
            json=data,
            headers=self._get_headers(),
        )
        return response.json()

    def update_comment(self, comment_id: str, content: str) -> dict:
        response = requests.patch(
            f"{self.base_url}/comments/{comment_id}/",
            json={"content": content},
            headers=self._get_headers(),
        )
        return response.json()

    def delete_comment(self, comment_id: str) -> int:
        response = requests.delete(
            f"{self.base_url}/comments/{comment_id}/",
            headers=self._get_headers(),
        )
        return response.status_code

    def get_comments(self, post_id: Optional[str] = None) -> dict:
        params = {}
        if post_id:
            params["post_id"] = post_id
        response = requests.get(
            f"{self.base_url}/comments/",
            params=params,
            headers=self._get_headers(),
        )
        return response.json()

    def react_to_target(self, target_type: str, target_id: str, reaction_type: str = "like") -> dict:
        response = requests.post(
            f"{self.base_url}/reactions/",
            json={
                "target_type": target_type,
                "target_id": target_id,
                "reaction_type": reaction_type,
            },
            headers=self._get_headers(),
        )
        return response.json()

    def delete_reaction(self, reaction_id: str) -> int:
        response = requests.delete(
            f"{self.base_url}/reactions/{reaction_id}/",
            headers=self._get_headers(),
        )
        return response.status_code


if __name__ == "__main__":
    client = APIClient()

    print("=== Testing API ===\n")

    print("1. Signup")
    signup_resp = client.signup("test@example.com", "password123", "John", "Doe")
    print(f"Response: {json.dumps(signup_resp, indent=2)}\n")

    print("2. Login")
    login_resp = client.login("test@example.com", "password123")
    print(f"Access Token: {login_resp.get('access')[:20]}...\n")

    print("3. Create Post")
    post_resp = client.create_post("Hello, this is my first post!", is_public=True)
    post_id = post_resp.get("id")
    print(f"Created Post ID: {post_id}\n")

    print("4. Get Recent Posts (with latest 2 comments)")
    recent_posts = client.get_recent_posts()
    print(f"Recent Posts: {json.dumps(recent_posts, indent=2)}\n")

    print("5. Create Comment on Post")
    comment_resp = client.create_comment(post_id, "Great post!")
    comment_id = comment_resp.get("id")
    print(f"Created Comment ID: {comment_id}\n")

    print("6. Create Reply to Comment")
    reply_resp = client.create_comment(post_id, "Thanks for the feedback!", parent_id=comment_id)
    print(f"Created Reply ID: {reply_resp.get('id')}\n")

    print("7. Get Post Comments")
    post_comments = client.get_post_comments(post_id)
    print(f"Post Comments: {json.dumps(post_comments, indent=2)}\n")

    print("8. React to Post")
    reaction_resp = client.react_to_target("post", post_id, "like")
    reaction_id = reaction_resp.get("id")
    print(f"Created Reaction ID: {reaction_id}\n")

    print("9. React to Comment")
    comment_reaction = client.react_to_target("comment", comment_id, "like")
    print(f"Created Comment Reaction: {json.dumps(comment_reaction, indent=2)}\n")

    print("10. Get Updated Post (with reaction count)")
    updated_post = client.get_posts()
    print(f"Posts: {json.dumps(updated_post, indent=2)}\n")

    print("=== All tests completed ===")
