"""
Reviewer agent for evaluating and improving post content
"""
import os
from typing import Dict, Any
import openai
from .base_agent import BaseAgent

class ReviewerAgent(BaseAgent):
    """Agent responsible for reviewing and improving post content"""
    
    def __init__(self):
        super().__init__(
            agent_id="reviewer_001", 
            name="Content Reviewer",
            description="AI agent that reviews and provides feedback on post content"
        )
        self.openai_client = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY", "demo-key")
        )
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Review post content and provide feedback and improvements
        
        Args:
            input_data: Contains post_content, preferences, and other context
            
        Returns:
            Dictionary with review feedback and improved content
        """
        post_content = input_data.get("post_content", "")
        preferences = input_data.get("preferences", {})
        original_idea = input_data.get("original_idea", "")
        
        # Build review prompt
        prompt = self._build_review_prompt(post_content, preferences, original_idea)
        
        try:
            # For demonstration, we'll provide mock feedback
            # In production, you would call the OpenAI API
            if os.getenv("OPENAI_API_KEY") and os.getenv("OPENAI_API_KEY") != "demo-key":
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an expert content reviewer and editor."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1200,
                    temperature=0.3
                )
                
                review_response = response.choices[0].message.content
                feedback, improved_content = self._parse_review_response(review_response, post_content)
            else:
                # Demo review for development
                feedback, improved_content = self._generate_demo_review(post_content, preferences)
            
            return {
                "success": True,
                "feedback": feedback,
                "improved_content": improved_content,
                "agent_id": self.agent_id,
                "metadata": {
                    "review_criteria": [
                        "clarity_and_structure",
                        "engagement_level", 
                        "target_audience_alignment",
                        "grammar_and_style",
                        "call_to_action_effectiveness"
                    ],
                    "original_content_length": len(post_content),
                    "improved_content_length": len(improved_content)
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "agent_id": self.agent_id,
                "feedback": None,
                "improved_content": None
            }
    
    def _build_review_prompt(self, content: str, preferences: Dict[str, Any], original_idea: str) -> str:
        """Build a prompt for reviewing content"""
        
        writing_style = preferences.get("writing_style", "professional")
        tone = preferences.get("tone", "neutral")
        target_audience = preferences.get("target_audience", "general")
        
        prompt = f"""
Please review the following post content and provide detailed feedback and an improved version.

Original idea: {original_idea}

Current post content:
{content}

Review criteria:
- Writing style should be: {writing_style}
- Tone should be: {tone}  
- Target audience: {target_audience}
- Grammar and clarity
- Engagement and readability
- Structure and flow
- Call-to-action effectiveness

Please provide:
1. FEEDBACK: Detailed feedback on what works well and what could be improved
2. IMPROVED_CONTENT: An enhanced version of the post that addresses the feedback

Format your response as:
FEEDBACK:
[Your detailed feedback here]

IMPROVED_CONTENT:  
[The improved version of the post here]
"""
        
        return prompt
    
    def _parse_review_response(self, review_response: str, original_content: str) -> tuple[str, str]:
        """Parse the review response to extract feedback and improved content"""
        
        parts = review_response.split("IMPROVED_CONTENT:")
        
        if len(parts) >= 2:
            feedback = parts[0].replace("FEEDBACK:", "").strip()
            improved_content = parts[1].strip()
        else:
            # Fallback if format is not as expected
            feedback = review_response
            improved_content = original_content
        
        return feedback, improved_content
    
    def _generate_demo_review(self, content: str, preferences: Dict[str, Any]) -> tuple[str, str]:
        """Generate demo review feedback when OpenAI API is not available"""
        
        # Analyze content for demo feedback
        word_count = len(content.split())
        has_hashtags = "#" in content
        has_call_to_action = any(phrase in content.lower() for phrase in ["what do you think", "let me know", "share your thoughts", "comment below"])
        
        # Generate feedback
        feedback_points = []
        
        if word_count < 50:
            feedback_points.append("• Consider expanding the content to provide more value to readers")
        elif word_count > 600:
            feedback_points.append("• Content is quite lengthy - consider breaking it into sections or shortening for better engagement")
        else:
            feedback_points.append("• Good length - appropriate for the target audience")
        
        if has_hashtags:
            feedback_points.append("• Great use of hashtags for discoverability")
        else:
            feedback_points.append("• Consider adding relevant hashtags to improve discoverability")
        
        if has_call_to_action:
            feedback_points.append("• Excellent call-to-action that encourages engagement")
        else:
            feedback_points.append("• Consider adding a call-to-action to encourage reader engagement")
        
        # Check for structure
        if "##" in content or "###" in content:
            feedback_points.append("• Well-structured with clear headings")
        else:
            feedback_points.append("• Consider adding section headings for better readability")
        
        feedback = f"""**Overall Assessment:** The post shows good potential and addresses the core idea effectively.

**Strengths:**
{chr(10).join([point for point in feedback_points if "Great" in point or "Excellent" in point or "Good" in point or "Well" in point])}

**Areas for Improvement:**
{chr(10).join([point for point in feedback_points if "Consider" in point or "lengthy" in point])}

**Recommendations:**
• Ensure the tone matches the intended {preferences.get('tone', 'neutral')} style
• Verify alignment with {preferences.get('target_audience', 'general')} audience expectations
• Check for any grammatical errors or unclear phrasing"""
        
        # Generate improved content (minor enhancements for demo)
        improved_content = content
        
        # Add hashtags if missing
        if not has_hashtags:
            improved_content += "\n\n#content #ideas #discussion"
        
        # Add call-to-action if missing
        if not has_call_to_action:
            if improved_content.endswith("#content #ideas #discussion"):
                improved_content = improved_content.replace("#content #ideas #discussion", 
                                                          "What are your thoughts on this? I'd love to hear your perspective!\n\n#content #ideas #discussion")
            else:
                improved_content += "\n\nWhat are your thoughts on this? I'd love to hear your perspective!"
        
        return feedback, improved_content