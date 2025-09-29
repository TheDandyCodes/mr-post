"""
Frontend service using FastHTML and DaisyUI
"""
from fasthtml.common import *
from starlette.responses import HTMLResponse, RedirectResponse
import httpx
import os
import json
from typing import Optional
import asyncio

# Configuration
STORAGE_SERVICE_URL = os.getenv("STORAGE_SERVICE_URL", "http://localhost:8001")
AGENTS_SERVICE_URL = os.getenv("AGENTS_SERVICE_URL", "http://localhost:8002")

# FastHTML app setup
app, rt = fast_app(
    hdrs=(
        # DaisyUI and Tailwind CSS
        Link(href="https://cdn.jsdelivr.net/npm/daisyui@4.4.20/dist/full.min.css", rel="stylesheet", type="text/css"),
        Script(src="https://cdn.tailwindcss.com"),
        # Additional styling
        Style("""
            .loading-spinner { 
                display: none; 
            }
            .loading .loading-spinner { 
                display: inline-block; 
            }
            .post-content {
                white-space: pre-wrap;
                word-wrap: break-word;
            }
            .hero-bg {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }
        """)
    )
)

# Helper functions for API calls
async def api_call(method: str, url: str, data=None, headers=None):
    """Make API calls to backend services"""
    async with httpx.AsyncClient() as client:
        try:
            if method.upper() == "GET":
                response = await client.get(url, headers=headers)
            elif method.upper() == "POST":
                response = await client.post(url, json=data, headers=headers)
            elif method.upper() == "PUT":
                response = await client.put(url, json=data, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            print(f"API call error: {e}")
            return None

def get_auth_headers(session):
    """Get authorization headers from session"""
    token = session.get("token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return None

def require_auth(session):
    """Check if user is authenticated"""
    return session.get("token") is not None

# Layout components
def base_layout(content, title="Mr. Post"):
    """Base layout with navigation"""
    return Html(
        Head(
            Title(title),
            Meta(charset="UTF-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1.0")
        ),
        Body(
            # Navigation
            Div(
                Div(
                    A("🚀 Mr. Post", href="/", cls="text-xl font-bold text-white"),
                    Div(
                        A("Dashboard", href="/dashboard", cls="btn btn-ghost text-white") if title != "Login" else None,
                        A("New Post", href="/create", cls="btn btn-primary") if title != "Login" else None,
                        A("Settings", href="/preferences", cls="btn btn-ghost text-white") if title != "Login" else None,
                        A("Logout", href="/logout", cls="btn btn-ghost text-white") if title != "Login" else None,
                        cls="flex gap-2"
                    ),
                    cls="flex justify-between items-center"
                ),
                cls="navbar bg-gradient-to-r from-blue-600 to-purple-600 px-6"
            ),
            # Main content
            Main(content, cls="min-h-screen bg-base-100"),
            # Footer
            Footer(
                Div(
                    P("© 2024 Mr. Post - AI-Powered Writing Assistant", cls="text-center text-gray-600"),
                    cls="py-6"
                ),
                cls="bg-base-200"
            ),
            cls="min-h-screen flex flex-col"
        )
    )

def hero_section():
    """Hero section for landing page"""
    return Div(
        Div(
            Div(
                H1("Transform Your Ideas Into Engaging Posts", cls="text-5xl font-bold text-white mb-6"),
                P("AI-powered writing assistant that turns your thoughts into compelling content with the help of our writer and reviewer agents.", 
                  cls="text-xl text-white/90 mb-8 max-w-2xl"),
                Div(
                    A("Get Started", href="/register", cls="btn btn-primary btn-lg mr-4"),
                    A("Login", href="/login", cls="btn btn-outline btn-lg text-white border-white hover:bg-white hover:text-purple-600"),
                    cls="flex gap-4"
                ),
                cls="text-center"
            ),
            cls="hero-content"
        ),
        cls="hero min-h-screen hero-bg"
    )

# Routes
@rt("/")
def home(session):
    """Landing page"""
    if require_auth(session):
        return RedirectResponse("/dashboard", status_code=302)
    
    content = Div(
        hero_section(),
        # Features section
        Div(
            Div(
                H2("How It Works", cls="text-3xl font-bold text-center mb-12"),
                Div(
                    # Step 1
                    Div(
                        Div("1", cls="text-3xl font-bold text-primary mb-4"),
                        H3("Share Your Idea", cls="text-xl font-semibold mb-2"),
                        P("Tell us what you want to write about. Just describe your idea in a few words or sentences."),
                        cls="card bg-base-100 shadow-lg p-6 text-center"
                    ),
                    # Step 2
                    Div(
                        Div("2", cls="text-3xl font-bold text-primary mb-4"),
                        H3("AI Writer Creates Content", cls="text-xl font-semibold mb-2"),
                        P("Our AI writer agent transforms your idea into engaging, well-structured content tailored to your preferences."),
                        cls="card bg-base-100 shadow-lg p-6 text-center"
                    ),
                    # Step 3
                    Div(
                        Div("3", cls="text-3xl font-bold text-primary mb-4"),
                        H3("AI Reviewer Improves It", cls="text-xl font-semibold mb-2"),
                        P("Our reviewer agent analyzes the content and provides improvements for clarity, engagement, and effectiveness."),
                        cls="card bg-base-100 shadow-lg p-6 text-center"
                    ),
                    cls="grid grid-cols-1 md:grid-cols-3 gap-8"
                ),
                cls="max-w-6xl mx-auto px-6"
            ),
            cls="py-20 bg-base-200"
        )
    )
    
    return base_layout(content, "Mr. Post - AI Writing Assistant")

@rt("/register")
def register_page():
    """Registration page"""
    content = Div(
        Div(
            Div(
                H2("Create Your Account", cls="text-3xl font-bold text-center mb-8"),
                Form(
                    Div(
                        Label("Email", cls="label"),
                        Input(type="email", name="email", cls="input input-bordered w-full", required=True),
                        cls="form-control mb-4"
                    ),
                    Div(
                        Label("Username", cls="label"),
                        Input(type="text", name="username", cls="input input-bordered w-full", required=True),
                        cls="form-control mb-4"
                    ),
                    Div(
                        Label("Password", cls="label"),
                        Input(type="password", name="password", cls="input input-bordered w-full", required=True),
                        cls="form-control mb-6"
                    ),
                    Button("Create Account", type="submit", cls="btn btn-primary w-full"),
                    action="/register", method="post"
                ),
                Div(
                    P("Already have an account? ", A("Login here", href="/login", cls="link link-primary")),
                    cls="text-center mt-6"
                ),
                cls="card bg-base-100 shadow-2xl p-8 w-full max-w-md"
            ),
            cls="flex justify-center items-center"
        ),
        cls="min-h-screen bg-base-200 py-20"
    )
    
    return base_layout(content, "Register")

@rt("/register", methods=["POST"])
async def register_user(email: str, username: str, password: str, session):
    """Handle user registration"""
    user_data = {
        "email": email,
        "username": username,
        "password": password
    }
    
    result = await api_call("POST", f"{STORAGE_SERVICE_URL}/auth/register", user_data)
    
    if result:
        # Auto-login after registration
        login_data = {"email": email, "password": password}
        login_result = await api_call("POST", f"{STORAGE_SERVICE_URL}/auth/login", login_data)
        
        if login_result:
            session["token"] = login_result["access_token"]
            session["user"] = login_result["user"]
            return RedirectResponse("/dashboard", status_code=302)
    
    # Registration failed
    return RedirectResponse("/register?error=Registration failed", status_code=302)

@rt("/login")
def login_page():
    """Login page"""
    content = Div(
        Div(
            Div(
                H2("Welcome Back", cls="text-3xl font-bold text-center mb-8"),
                Form(
                    Div(
                        Label("Email", cls="label"),
                        Input(type="email", name="email", cls="input input-bordered w-full", required=True),
                        cls="form-control mb-4"
                    ),
                    Div(
                        Label("Password", cls="label"),
                        Input(type="password", name="password", cls="input input-bordered w-full", required=True),
                        cls="form-control mb-6"
                    ),
                    Button("Login", type="submit", cls="btn btn-primary w-full"),
                    action="/login", method="post"
                ),
                Div(
                    P("Don't have an account? ", A("Register here", href="/register", cls="link link-primary")),
                    cls="text-center mt-6"
                ),
                cls="card bg-base-100 shadow-2xl p-8 w-full max-w-md"
            ),
            cls="flex justify-center items-center"
        ),
        cls="min-h-screen bg-base-200 py-20"
    )
    
    return base_layout(content, "Login")

@rt("/login", methods=["POST"]) 
async def login_user(email: str, password: str, session):
    """Handle user login"""
    login_data = {"email": email, "password": password}
    
    result = await api_call("POST", f"{STORAGE_SERVICE_URL}/auth/login", login_data)
    
    if result and "access_token" in result:
        session["token"] = result["access_token"]
        session["user"] = result["user"]
        return RedirectResponse("/dashboard", status_code=302)
    
    return RedirectResponse("/login?error=Invalid credentials", status_code=302)

@rt("/logout")
def logout(session):
    """Logout user"""
    session.clear()
    return RedirectResponse("/", status_code=302)

@rt("/dashboard")
async def dashboard(session):
    """User dashboard"""
    if not require_auth(session):
        return RedirectResponse("/login", status_code=302)
    
    headers = get_auth_headers(session)
    posts = await api_call("GET", f"{STORAGE_SERVICE_URL}/posts", headers=headers)
    
    if not posts:
        posts = []
    
    content = Div(
        Div(
            Div(
                H1("Your Posts", cls="text-3xl font-bold mb-6"),
                A("Create New Post", href="/create", cls="btn btn-primary mb-6"),
                
                # Posts grid
                Div(
                    *[
                        Div(
                            Div(
                                H3(post["title"], cls="card-title text-lg"),
                                P(post["original_idea"][:100] + "..." if len(post.get("original_idea", "")) > 100 else post.get("original_idea", ""), 
                                  cls="text-gray-600 mb-4"),
                                Div(
                                    Span(post["status"].title(), cls=f"badge badge-{'success' if post['status'] == 'completed' else 'warning' if post['status'] == 'processing' else 'info'}"),
                                    Span(f"Created: {post['created_at'][:10]}", cls="text-sm text-gray-500"),
                                    cls="flex justify-between items-center mb-4"
                                ),
                                Div(
                                    A("View", href=f"/posts/{post['id']}", cls="btn btn-sm btn-outline"),
                                    A("Edit", href=f"/posts/{post['id']}/edit", cls="btn btn-sm btn-primary") if post["status"] != "processing" else None,
                                    cls="flex gap-2"
                                ),
                                cls="card-body"
                            ),
                            cls="card bg-base-100 shadow-lg"
                        ) for post in posts
                    ] if posts else [
                        Div(
                            Div(
                                H3("No posts yet", cls="text-xl text-gray-600 text-center"),
                                P("Create your first post to get started!", cls="text-gray-500 text-center mb-4"),
                                A("Create Post", href="/create", cls="btn btn-primary"),
                                cls="text-center py-12"
                            ),
                            cls="card bg-base-100 shadow-lg col-span-full"
                        )
                    ],
                    cls="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
                ),
                cls="max-w-7xl mx-auto px-6"
            ),
            cls="py-12"
        )
    )
    
    return base_layout(content, "Dashboard")

@rt("/create")
async def create_post_page(session):
    """Create new post page"""
    if not require_auth(session):
        return RedirectResponse("/login", status_code=302)
    
    headers = get_auth_headers(session)
    preferences = await api_call("GET", f"{STORAGE_SERVICE_URL}/preferences", headers=headers)
    
    content = Div(
        Div(
            Div(
                H1("Create New Post", cls="text-3xl font-bold mb-8"),
                Form(
                    Div(
                        Label("Post Title", cls="label label-text font-semibold"),
                        Input(type="text", name="title", cls="input input-bordered w-full", required=True, placeholder="Enter a catchy title for your post"),
                        cls="form-control mb-6"
                    ),
                    Div(
                        Label("Your Idea", cls="label label-text font-semibold"),
                        Textarea(name="original_idea", cls="textarea textarea-bordered w-full h-32", required=True, 
                                placeholder="Describe your idea, topic, or what you want to write about..."),
                        cls="form-control mb-6"
                    ),
                    Div(
                        Label("Writing Preferences", cls="label label-text font-semibold mb-2"),
                        Div(
                            Div(
                                Label("Style:", cls="label label-text"),
                                Select(
                                    Option("Professional", value="professional", selected=preferences and preferences.get("writing_style") == "professional"),
                                    Option("Casual", value="casual", selected=preferences and preferences.get("writing_style") == "casual"),
                                    Option("Creative", value="creative", selected=preferences and preferences.get("writing_style") == "creative"),
                                    Option("Academic", value="academic", selected=preferences and preferences.get("writing_style") == "academic"),
                                    name="writing_style", cls="select select-bordered w-full"
                                ),
                                cls="form-control"
                            ),
                            Div(
                                Label("Tone:", cls="label label-text"),
                                Select(
                                    Option("Neutral", value="neutral", selected=preferences and preferences.get("tone") == "neutral"),
                                    Option("Friendly", value="friendly", selected=preferences and preferences.get("tone") == "friendly"),
                                    Option("Formal", value="formal", selected=preferences and preferences.get("tone") == "formal"),
                                    Option("Humorous", value="humorous", selected=preferences and preferences.get("tone") == "humorous"),
                                    name="tone", cls="select select-bordered w-full"
                                ),
                                cls="form-control"
                            ),
                            Div(
                                Label("Length:", cls="label label-text"),
                                Select(
                                    Option("Short (100-200 words)", value="short", selected=preferences and preferences.get("post_length") == "short"),
                                    Option("Medium (300-500 words)", value="medium", selected=preferences and preferences.get("post_length") == "medium"),
                                    Option("Long (600-800 words)", value="long", selected=preferences and preferences.get("post_length") == "long"),
                                    name="post_length", cls="select select-bordered w-full"
                                ),
                                cls="form-control"
                            ),
                            cls="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6"
                        )
                    ),
                    Div(
                        Button("Create & Process with AI", type="submit", cls="btn btn-primary btn-lg"),
                        A("Cancel", href="/dashboard", cls="btn btn-outline btn-lg ml-4"),
                        cls="flex gap-4"
                    ),
                    action="/create", method="post"
                ),
                cls="card bg-base-100 shadow-2xl p-8 max-w-4xl mx-auto"
            ),
            cls="py-12 px-6"
        )
    )
    
    return base_layout(content, "Create Post")

@rt("/create", methods=["POST"])
async def create_post(title: str, original_idea: str, writing_style: str, tone: str, post_length: str, session):
    """Handle post creation"""
    if not require_auth(session):
        return RedirectResponse("/login", status_code=302)
    
    headers = get_auth_headers(session)
    
    # Create post in storage
    post_data = {
        "title": title,
        "original_idea": original_idea
    }
    
    post_result = await api_call("POST", f"{STORAGE_SERVICE_URL}/posts", post_data, headers)
    
    if not post_result:
        return RedirectResponse("/create?error=Failed to create post", status_code=302)
    
    post_id = post_result["id"]
    
    # Start AI processing workflow
    preferences = {
        "writing_style": writing_style,
        "tone": tone,
        "post_length": post_length
    }
    
    workflow_data = {
        "user_idea": original_idea,
        "preferences": preferences,
        "post_id": post_id,
        "token": session["token"]
    }
    
    workflow_result = await api_call("POST", f"{AGENTS_SERVICE_URL}/process-post", workflow_data)
    
    return RedirectResponse(f"/posts/{post_id}", status_code=302)

@rt("/posts/{post_id}")
async def view_post(post_id: int, session):
    """View individual post"""
    if not require_auth(session):
        return RedirectResponse("/login", status_code=302)
    
    headers = get_auth_headers(session)
    post = await api_call("GET", f"{STORAGE_SERVICE_URL}/posts/{post_id}", headers=headers)
    
    if not post:
        return RedirectResponse("/dashboard?error=Post not found", status_code=302)
    
    content = Div(
        Div(
            Div(
                # Header
                Div(
                    H1(post["title"], cls="text-4xl font-bold mb-2"),
                    Div(
                        Span(post["status"].title(), cls=f"badge badge-lg badge-{'success' if post['status'] == 'completed' else 'warning' if post['status'] in ['processing', 'written', 'reviewing'] else 'info'}"),
                        Span(f"Created: {post['created_at'][:10]}", cls="text-gray-600"),
                        cls="flex items-center gap-4 mb-6"
                    ),
                    A("← Back to Dashboard", href="/dashboard", cls="btn btn-outline mb-6"),
                    cls="mb-8"
                ),
                
                # Original Idea
                Div(
                    H2("Original Idea", cls="text-2xl font-bold mb-4"),
                    Div(post.get("original_idea", "No original idea available"), cls="prose max-w-none bg-base-200 p-6 rounded-lg"),
                    cls="mb-8"
                ),
                
                # Writer Output
                Div(
                    H2("AI Writer Output", cls="text-2xl font-bold mb-4"),
                    Div(
                        Pre(post.get("writer_output", "Content is being generated..."), cls="post-content bg-base-200 p-6 rounded-lg") if post.get("writer_output") 
                        else Div(
                            Div(cls="loading loading-spinner loading-lg"),
                            P("AI is writing your post...", cls="ml-4"),
                            cls="flex items-center justify-center py-12 bg-base-200 rounded-lg"
                        ),
                        cls="prose max-w-none"
                    ),
                    cls="mb-8"
                ) if post["status"] in ["written", "reviewing", "reviewed", "completed"] or post.get("writer_output") else None,
                
                # Reviewer Feedback
                Div(
                    H2("AI Reviewer Feedback", cls="text-2xl font-bold mb-4"),
                    Div(
                        Pre(post.get("reviewer_feedback", "Waiting for review..."), cls="post-content bg-base-200 p-6 rounded-lg") if post.get("reviewer_feedback")
                        else Div(
                            Div(cls="loading loading-spinner loading-lg"),
                            P("AI is reviewing your post...", cls="ml-4"),
                            cls="flex items-center justify-center py-12 bg-base-200 rounded-lg"
                        ),
                        cls="prose max-w-none"
                    ),
                    cls="mb-8"
                ) if post["status"] in ["reviewing", "reviewed", "completed"] or post.get("reviewer_feedback") else None,
                
                # Final Content
                Div(
                    H2("Final Content", cls="text-2xl font-bold mb-4"),
                    Div(
                        Pre(post.get("final_content", "Final content will appear here..."), cls="post-content bg-success/10 p-6 rounded-lg border-2 border-success/20"),
                        cls="prose max-w-none"
                    ),
                    Div(
                        Button("Copy to Clipboard", cls="btn btn-outline", onclick="copyToClipboard()"),
                        Button("Download", cls="btn btn-primary ml-2", onclick="downloadContent()"),
                        cls="mt-4"
                    ),
                    cls="mb-8"
                ) if post["status"] == "completed" and post.get("final_content") else None,
                
                # Actions
                Div(
                    A("Edit Post", href=f"/posts/{post_id}/edit", cls="btn btn-primary mr-2") if post["status"] != "processing" else None,
                    Button("Refresh Status", cls="btn btn-outline", onclick="window.location.reload()") if post["status"] in ["processing", "written", "reviewing"] else None,
                    cls="mt-8"
                ),
                
                cls="max-w-6xl mx-auto px-6"
            ),
            cls="py-12"
        ),
        # JavaScript for copy and download functionality
        Script("""
        function copyToClipboard() {
            const content = document.querySelector('.prose .post-content').textContent;
            navigator.clipboard.writeText(content).then(() => {
                alert('Content copied to clipboard!');
            });
        }
        
        function downloadContent() {
            const content = document.querySelector('.prose .post-content').textContent;
            const blob = new Blob([content], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'post-content.txt';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
        
        // Auto-refresh for posts in progress
        if (window.location.href.includes('/posts/')) {
            const status = document.querySelector('.badge').textContent.toLowerCase();
            if (['processing', 'written', 'reviewing'].includes(status)) {
                setTimeout(() => window.location.reload(), 5000);
            }
        }
        """)
    )
    
    return base_layout(content, f"Post: {post['title']}")

@rt("/preferences")
async def preferences_page(session):
    """User preferences page"""
    if not require_auth(session):
        return RedirectResponse("/login", status_code=302)
    
    headers = get_auth_headers(session)
    preferences = await api_call("GET", f"{STORAGE_SERVICE_URL}/preferences", headers=headers)
    
    # Set defaults if no preferences found
    if not preferences:
        preferences = {
            "writing_style": "professional",
            "tone": "neutral",
            "target_audience": "general",
            "post_length": "medium",
            "ai_creativity_level": "balanced"
        }
    
    content = Div(
        Div(
            Div(
                H1("Writing Preferences", cls="text-3xl font-bold mb-8"),
                P("Set your default writing preferences. These will be used as defaults when creating new posts.", cls="text-gray-600 mb-8"),
                
                Form(
                    Div(
                        Div(
                            Label("Writing Style", cls="label label-text font-semibold"),
                            Select(
                                Option("Professional", value="professional", selected=preferences.get("writing_style") == "professional"),
                                Option("Casual", value="casual", selected=preferences.get("writing_style") == "casual"),
                                Option("Creative", value="creative", selected=preferences.get("writing_style") == "creative"),
                                Option("Academic", value="academic", selected=preferences.get("writing_style") == "academic"),
                                name="writing_style", cls="select select-bordered w-full"
                            ),
                            P("Choose the overall style of your writing", cls="text-sm text-gray-500 mt-1"),
                            cls="form-control mb-4"
                        ),
                        
                        Div(
                            Label("Tone", cls="label label-text font-semibold"),
                            Select(
                                Option("Neutral", value="neutral", selected=preferences.get("tone") == "neutral"),
                                Option("Friendly", value="friendly", selected=preferences.get("tone") == "friendly"),
                                Option("Formal", value="formal", selected=preferences.get("tone") == "formal"),
                                Option("Humorous", value="humorous", selected=preferences.get("tone") == "humorous"),
                                name="tone", cls="select select-bordered w-full"
                            ),
                            P("Select the tone that matches your personality", cls="text-sm text-gray-500 mt-1"),
                            cls="form-control mb-4"
                        ),
                        
                        cls="grid grid-cols-1 md:grid-cols-2 gap-6"
                    ),
                    
                    Div(
                        Div(
                            Label("Target Audience", cls="label label-text font-semibold"),
                            Select(
                                Option("General Public", value="general", selected=preferences.get("target_audience") == "general"),
                                Option("Professionals", value="professionals", selected=preferences.get("target_audience") == "professionals"),
                                Option("Students", value="students", selected=preferences.get("target_audience") == "students"),
                                Option("Experts", value="experts", selected=preferences.get("target_audience") == "experts"),
                                name="target_audience", cls="select select-bordered w-full"
                            ),
                            P("Who is your typical audience?", cls="text-sm text-gray-500 mt-1"),
                            cls="form-control mb-4"
                        ),
                        
                        Div(
                            Label("Default Post Length", cls="label label-text font-semibold"),
                            Select(
                                Option("Short (100-200 words)", value="short", selected=preferences.get("post_length") == "short"),
                                Option("Medium (300-500 words)", value="medium", selected=preferences.get("post_length") == "medium"),
                                Option("Long (600-800 words)", value="long", selected=preferences.get("post_length") == "long"),
                                name="post_length", cls="select select-bordered w-full"
                            ),
                            P("Your preferred post length", cls="text-sm text-gray-500 mt-1"),
                            cls="form-control mb-4"
                        ),
                        
                        cls="grid grid-cols-1 md:grid-cols-2 gap-6"
                    ),
                    
                    Div(
                        Label("AI Creativity Level", cls="label label-text font-semibold"),
                        Select(
                            Option("Conservative (Stick to facts)", value="conservative", selected=preferences.get("ai_creativity_level") == "conservative"),
                            Option("Balanced (Mix of facts and creativity)", value="balanced", selected=preferences.get("ai_creativity_level") == "balanced"),
                            Option("Creative (More innovative and unique)", value="creative", selected=preferences.get("ai_creativity_level") == "creative"),
                            name="ai_creativity_level", cls="select select-bordered w-full"
                        ),
                        P("How creative should the AI be when writing your posts?", cls="text-sm text-gray-500 mt-1"),
                        cls="form-control mb-6"
                    ),
                    
                    Div(
                        Button("Save Preferences", type="submit", cls="btn btn-primary btn-lg"),
                        A("Cancel", href="/dashboard", cls="btn btn-outline btn-lg ml-4"),
                        cls="flex gap-4"
                    ),
                    
                    action="/preferences", method="post"
                ),
                cls="card bg-base-100 shadow-2xl p-8 max-w-4xl mx-auto"
            ),
            cls="py-12 px-6"
        )
    )
    
    return base_layout(content, "Preferences")

@rt("/preferences", methods=["POST"])
async def save_preferences(writing_style: str, tone: str, target_audience: str, post_length: str, ai_creativity_level: str, session):
    """Save user preferences"""
    if not require_auth(session):
        return RedirectResponse("/login", status_code=302)
    
    headers = get_auth_headers(session)
    
    preferences_data = {
        "writing_style": writing_style,
        "tone": tone,
        "target_audience": target_audience,
        "post_length": post_length,
        "ai_creativity_level": ai_creativity_level,
        "topics_of_interest": []  # Can be extended later
    }
    
    result = await api_call("PUT", f"{STORAGE_SERVICE_URL}/preferences", preferences_data, headers)
    
    if result:
        return RedirectResponse("/dashboard?success=Preferences saved", status_code=302)
    else:
        return RedirectResponse("/preferences?error=Failed to save preferences", status_code=302)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)