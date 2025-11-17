import os
import json
from typing import Dict, Optional, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

class EmailClassifier:
    """LLM-based email classifier for understanding emails and determining actions"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the email classifier"""
        if api_key:
            os.environ['OPENAI_API_KEY'] = api_key
        elif 'OPENAI_API_KEY' not in os.environ:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.3,
            max_tokens=1500
        )
    
    def classify_email(self, email_data: Dict, available_categories: List[Dict]) -> Dict:
        """
        Classify an email and determine the appropriate action
        
        Args:
            email_data: Dictionary containing email information (subject, body, sender, etc.)
            available_categories: List of available categories with their actions
        
        Returns:
            Dictionary with classification results including category, confidence, justification, and action
        """
        subject = email_data.get('subject', '')
        body = email_data.get('body', '')
        sender = email_data.get('sender', '')
        
        # Build category information for the prompt
        categories_info = []
        for cat in available_categories:
            categories_info.append(
                f"- {cat['name']}: {cat['description']} "
                f"(Keywords: {cat.get('keywords', 'N/A')}, "
                f"Action: {cat['action_type']} -> {cat.get('target', 'N/A')})"
            )
        
        categories_text = '\n'.join(categories_info)
        
        # Create classification prompt
        system_prompt = """You are an expert email classifier. Your task is to:
1. Analyze the email content (subject, body, sender)
2. Classify it into one of the predefined categories
3. Determine the appropriate action to take
4. Provide a clear justification for your classification

Be precise and consider the context, tone, and intent of the email."""
        
        user_prompt = f"""Analyze the following email and classify it:

**Email Subject:** {subject}
**Email From:** {sender}
**Email Body:**
{body[:2000]}  # Limit body length

**Available Categories:**
{categories_text}

Please provide a JSON response with the following structure:
{{
    "category": "Category Name (must match exactly one from the list above)",
    "confidence": 0.0-1.0,
    "justification": "Brief explanation of why this email matches this category. Include specific keywords or phrases that led to this classification.",
    "intent": "The main intent or purpose of this email",
    "action_type": "forward|update_hr|add_calendar|create_ticket|auto_reply",
    "action_name": "Human-readable action name",
    "target": "Target for the action (email address, system name, etc.)",
    "requires_manual_review": false
}}

Important:
- The category name MUST match exactly one from the available categories
- Confidence should reflect how certain you are (0.0 = uncertain, 1.0 = very certain)
- Justification should be specific and mention key phrases/words from the email
- If the email doesn't clearly fit any category, use "General Inquiry" with lower confidence
- Set requires_manual_review to true if the email is ambiguous or requires human judgment

Return ONLY valid JSON, no additional text."""
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm.invoke(messages)
            result_text = response.content
            
            # Parse JSON response
            classification = self._parse_response(result_text)
            
            # Validate category
            category_names = [cat['name'] for cat in available_categories]
            if classification['category'] not in category_names:
                # Try to find closest match or default to General Inquiry
                classification['category'] = self._find_closest_category(
                    classification['category'], 
                    category_names
                ) or 'General Inquiry'
                classification['confidence'] = min(classification.get('confidence', 0.5), 0.7)
                classification['requires_manual_review'] = True
            
            return classification
            
        except Exception as e:
            print(f"Error classifying email: {str(e)}")
            # Return default classification
            return {
                'category': 'General Inquiry',
                'confidence': 0.3,
                'justification': f'Classification error: {str(e)}',
                'intent': 'Unknown',
                'action_type': 'auto_reply',
                'action_name': 'Auto Reply',
                'target': 'auto',
                'requires_manual_review': True
            }
    
    def _parse_response(self, response_text: str) -> Dict:
        """Parse LLM response JSON"""
        try:
            # Try to extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                parsed = json.loads(json_str)
                
                # Ensure all required keys exist
                return {
                    'category': parsed.get('category', 'General Inquiry'),
                    'confidence': float(parsed.get('confidence', 0.5)),
                    'justification': parsed.get('justification', 'No justification provided'),
                    'intent': parsed.get('intent', 'Unknown'),
                    'action_type': parsed.get('action_type', 'auto_reply'),
                    'action_name': parsed.get('action_name', 'Auto Reply'),
                    'target': parsed.get('target', 'auto'),
                    'requires_manual_review': parsed.get('requires_manual_review', False)
                }
        except Exception as e:
            print(f"Error parsing response: {str(e)}")
        
        # Return default if parsing fails
        return {
            'category': 'General Inquiry',
            'confidence': 0.3,
            'justification': 'Failed to parse classification response',
            'intent': 'Unknown',
            'action_type': 'auto_reply',
            'action_name': 'Auto Reply',
            'target': 'auto',
            'requires_manual_review': True
        }
    
    def _find_closest_category(self, category_name: str, available_categories: List[str]) -> Optional[str]:
        """Find the closest matching category name"""
        category_lower = category_name.lower()
        
        # Try exact match (case-insensitive)
        for cat in available_categories:
            if cat.lower() == category_lower:
                return cat
        
        # Try partial match
        for cat in available_categories:
            if category_lower in cat.lower() or cat.lower() in category_lower:
                return cat
        
        return None
    
    def generate_auto_reply(self, email_data: Dict, classification: Dict) -> str:
        """Generate an auto-reply message based on email and classification"""
        subject = email_data.get('subject', '')
        category = classification.get('category', '')
        
        prompt = f"""Generate a professional, helpful auto-reply email for the following:

**Original Subject:** {subject}
**Category:** {category}
**Intent:** {classification.get('intent', 'Unknown')}

Create a brief, professional auto-reply that:
1. Acknowledges receipt of the email
2. Provides appropriate information or next steps based on the category
3. Is friendly but concise
4. Includes a note that a human will review if needed

Return ONLY the email body text, no subject line or headers."""
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return response.content.strip()
        except Exception as e:
            print(f"Error generating auto-reply: {str(e)}")
            return f"Thank you for your email regarding '{subject}'. We have received your message and will review it shortly. If this requires immediate attention, please contact us directly."

