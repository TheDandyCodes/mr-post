"""
Writer agent for generating post content
"""
import os
from typing import Dict, Any
import openai
from .base_agent import BaseAgent

class WriterAgent(BaseAgent):
    """Agent responsible for writing posts based on user ideas and preferences"""
    
    def __init__(self):
        super().__init__(
            agent_id="writer_001",
            name="Content Writer",
            description="AI agent that creates engaging posts from user ideas"
        )
        self.openai_client = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY", "demo-key")  # Use demo key for development
        )
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user idea and preferences to generate a post
        
        Args:
            input_data: Contains user_idea, preferences, and other context
            
        Returns:
            Dictionary with generated content and metadata
        """
        user_idea = input_data.get("user_idea", "")
        preferences = input_data.get("preferences", {})
        
        # Build prompt based on user preferences
        prompt = self._build_writing_prompt(user_idea, preferences)
        
        try:
            # For demonstration, we'll use a simple response
            # In production, you would call the OpenAI API
            if os.getenv("OPENAI_API_KEY") and os.getenv("OPENAI_API_KEY") != "demo-key":
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a skilled content writer who creates engaging posts."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1000,
                    temperature=0.7
                )
                content = response.choices[0].message.content
            else:
                # Demo response for development
                content = self._generate_demo_content(user_idea, preferences)
            
            return {
                "success": True,
                "content": content,
                "agent_id": self.agent_id,
                "metadata": {
                    "writing_style": preferences.get("writing_style", "professional"),
                    "tone": preferences.get("tone", "neutral"),
                    "target_audience": preferences.get("target_audience", "general"),
                    "post_length": preferences.get("post_length", "medium"),
                    "original_idea": user_idea
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "agent_id": self.agent_id,
                "content": None
            }
    
    def _build_writing_prompt(self, user_idea: str, preferences: Dict[str, Any]) -> str:
        """Build a writing prompt based on user preferences"""
        
        writing_style = preferences.get("writing_style", "professional")
        tone = preferences.get("tone", "neutral")
        target_audience = preferences.get("target_audience", "general")
        post_length = preferences.get("post_length", "medium")
        creativity_level = preferences.get("ai_creativity_level", "balanced")
        
        # Length mapping
        length_mapping = {
            "short": "Write a concise post (100-200 words)",
            "medium": "Write a medium-length post (300-500 words)", 
            "long": "Write a comprehensive post (600-800 words)"
        }
        
        prompt = f"""
Create a {writing_style} post with a {tone} tone for a {target_audience} audience.

User's idea: {user_idea}

Requirements:
- {length_mapping.get(post_length, "Write a medium-length post")}
- Style: {writing_style}
- Tone: {tone}
- Target audience: {target_audience}
- Creativity level: {creativity_level}

The post should be engaging, well-structured, and ready for publication. Include relevant hashtags if appropriate.
"""
        
        return prompt
    
    def _generate_demo_content(self, user_idea: str, preferences: Dict[str, Any]) -> str:
        """Generate demo content when OpenAI API is not available"""
        
        writing_style = preferences.get("writing_style", "professional")
        tone = preferences.get("tone", "neutral")
        post_length = preferences.get("post_length", "medium")
        
        # Simple template-based content generation for demo
        if post_length == "short":
            content = f"""💡 {user_idea}

This is an interesting concept that deserves attention. Here are some key points to consider:

• First important aspect of this idea
• Second valuable insight  
• Third compelling reason why this matters

What are your thoughts on this? Let me know in the comments!

#ideas #content #discussion"""
        
        elif post_length == "long":
            content = f"""# Exploring: {user_idea}

## Introduction
This topic has been on my mind lately, and I wanted to share some thoughts with you all.

## Key Insights
When we think about "{user_idea}", several important aspects come to light:

### First Perspective
This idea challenges us to think differently about conventional approaches. It opens up new possibilities for innovation and growth.

### Second Consideration  
From another angle, we need to consider the practical implications and how this could impact our daily lives or work.

### Third Dimension
Finally, there's the broader context to consider - how does this fit into the bigger picture?

## Conclusion
{user_idea} represents an opportunity for meaningful change and growth. By exploring these concepts together, we can better understand their potential impact.

What's your take on this? I'd love to hear your perspectives in the comments below.

#innovation #ideas #discussion #growth #insights"""
        
        else:  # medium
            content = f"""🚀 Let's dive into: {user_idea}

I've been thinking about this concept and wanted to share some insights with you.

## Why This Matters
This idea is particularly relevant because it addresses something many of us encounter. It offers a fresh perspective on familiar challenges.

## Key Takeaways
Here are the main points worth considering:

1. **First insight**: This approach could change how we think about the problem
2. **Second point**: It provides practical benefits that we can implement
3. **Third consideration**: The long-term implications are worth exploring

## Moving Forward
The beauty of ideas like this is that they invite us to question assumptions and explore new possibilities. Whether you're just starting to think about this or you're already deep into exploration, there's value in continuing the conversation.

What resonates with you about this idea? Share your thoughts below!

#ideas #innovation #discussion #insights"""
        
        # Adjust tone
        if tone == "friendly":
            content = content.replace("Let's dive into:", "Hey everyone! Let's chat about:")
            content = content.replace("I've been thinking", "I've been pondering")
        elif tone == "formal":
            content = content.replace("Let's dive into:", "An analysis of:")
            content = content.replace("Hey everyone!", "Colleagues,")
        
        return content