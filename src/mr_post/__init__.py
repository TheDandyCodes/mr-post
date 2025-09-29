"""
Mr. Post - AI-powered writing assistant

A multi-microservice system with:
- Frontend (FastHTML + DaisyUI)
- Agents (Writer + Reviewer)
- Storage (User management + posts)
"""

__version__ = "0.1.0"

def main():
    print("Welcome to Mr. Post!")
    print("This is a multi-microservice AI writing assistant.")
    print()
    print("Services:")
    print("- Frontend: http://localhost:8000")
    print("- Storage API: http://localhost:8001")
    print("- Agents API: http://localhost:8002")
    print()
    print("Use 'docker-compose up' to start all services")
    print("Or run individual services:")
    print("- python -m services.frontend.main")
    print("- python -m services.storage.main")
    print("- python -m services.agents.main")


if __name__ == "__main__":
    main()
