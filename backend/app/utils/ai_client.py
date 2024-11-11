from openai import OpenAI
import json
from typing import Dict, List, Optional
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class AIClient:
    def __init__(self):
        self.client = OpenAI(api_key=current_app.config['OPENAI_API_KEY'])
        self.content_model = current_app.config['OPENAI_CONTENT_MODEL']
        self.question_model = current_app.config['OPENAI_QUESTION_MODEL']
        self.classification_model = current_app.config['OPENAI_CLASSIFICATION_MODEL']

    def analyze_content(self, content: str) -> Dict:
        """Analyze website content and identify key topics"""
        try:
            if not content:
                logger.warning("No content to analyze.")
                return {}
            
            logger.info(f"Analyzing content length: {len(content)} characters")
            
            prompt = (
                "Analyze this website content and extract key information.\n"
                "Return a JSON object with these exact keys:\n"
                "{\n"
                '  "topics": ["topic1", "topic2", ...],\n'
                '  "audience": ["audience1", "audience2", ...],\n'
                '  "sections": ["section1", "section2", ...]\n'
                "}\n"
                "IMPORTANT: Return only the JSON object, no markdown formatting or backticks."
            )

            response = self.client.chat.completions.create(
                model=self.content_model,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": content}
                ],
                temperature=0.7
            )
            
            raw_response = response.choices[0].message.content
            # Remove any markdown formatting or backticks
            cleaned_response = raw_response.strip('`').replace('```json', '').replace('```', '').strip()
            
            logger.info(f"Cleaned AI response: {cleaned_response}")
            
            try:
                parsed_response = json.loads(cleaned_response)
                logger.info(f"Successfully parsed response: {parsed_response}")
                return parsed_response
            except json.JSONDecodeError as je:
                logger.error(f"JSON parsing error: {je}")
                logger.error(f"Failed to parse response: {cleaned_response}")
                # Return a default structure instead of raising
                return {
                    "topics": ["General Content"],
                    "audience": ["Website Visitors"],
                    "sections": ["Main Content"]
                }

        except Exception as e:
            logger.error(f"Content analysis error: {str(e)}")
            logger.error(f"Content preview: {content[:200]}...")
            # Return default structure instead of raising
            return {
                "topics": ["General Content"],
                "audience": ["Website Visitors"],
                "sections": ["Main Content"]
            }

    def generate_next_question(self, content_analysis: Dict, previous_responses: List[Dict] = None) -> Dict:
        """Generate next question based on content analysis and previous responses"""
        try:
            system_prompt = """You are a website visitor classifier. 
            Generate relevant questions to understand visitor interests or industry based on the website's content.
            
            Rules:
            1. Questions should be specific to the website content
            2. Options should be based on actual content topics and sections
            3. Include 3-5 distinct, specific options
            4. Never repeat previous questions
            5. Make questions progressively more specific based on previous answers
            6. Keep language neutral and professional
            
            Return in this exact JSON format without any markdown:
            {
                "question": "Your specific question here?",
                "options": ["Specific Option 1", "Specific Option 2", "Specific Option 3", "Specific Option 4"]
            }"""

            # Build context including previous responses if available
            context = {
                "content_analysis": content_analysis,
                "previous_responses": previous_responses if previous_responses else []
            }

            user_prompt = f"""Context: {json.dumps(context, indent=2)}
            
            Generate a natural follow-up question based on the website's content and user's journey.
            If this is the first question, focus on understanding their primary interest or industry.
            If this is a follow-up, explore deeper based on their previous answer: {previous_responses[-1]['answer'] if previous_responses else 'None'}"""

            response = self.client.chat.completions.create(
                model=self.question_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7
            )

            raw_response = response.choices[0].message.content.strip()
            cleaned_response = raw_response.strip('`').replace('```json', '').replace('```', '').strip()
            
            try:
                question_data = json.loads(cleaned_response)
                if not all(key in question_data for key in ['question', 'options']):
                    raise ValueError("Missing required fields in response")
                if len(question_data['options']) < 3:
                    raise ValueError("Not enough options provided")
                return question_data
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Question generation error: {e}")
                logger.error(f"Raw response: {cleaned_response}")
                # Simple fallback that doesn't categorize options
                return {
                    "question": "What specific information are you looking for on this website?",
                    "options": [
                        "More details about what was mentioned",
                        "Different topic or section",
                        "Specific features or capabilities",
                        "Additional information"
                    ]
                }

        except Exception as e:
            logger.error(f"Question generation error: {e}")
            # Generic fallback without categorization
            return {
                "question": "What would you like to know more about?",
                "options": [
                    "Additional details",
                    "Different topics",
                    "Specific information",
                    "Other aspects"
                ]
            }

    def generate_classification(self, content_analysis: Dict, responses: List[Dict]) -> Dict:
        print('start generating')
        """Generate final classification based on responses"""
        try:
            system_prompt = """You are analyzing a user's website interaction.
            Create a detailed classification that includes their specific interests or industry and relevant content details.
            
            Rules:
            1. Describe interests or industry based on their specific responses and interactions
            2. For relevant_sections, provide 2-3 detailed content summaries that:
               - Directly relate to their expressed interests or industry
               - Include specific details from the website content
               - Are written as complete, informative sentences
               - Avoid generic phrases like "The website provides..."
               - Focus on actual content and features they would find relevant
            
            Return in this JSON format:
            {
                "interests": [
                    "user's primary interest or industry in short phrases"
                ],
                "relevant_sections": [
                    "Detailed summary of specific content, features, and information that matches their interest or industry",
                    "Additional relevant content summary with specific details and information"
                ]
            }
            Do not include any markdown, code snippets, or explanations. Return only the JSON object.
            """

            user_prompt = f"""Context:
            Content Analysis: {json.dumps(content_analysis, indent=2)}
            User Responses: {json.dumps(responses, indent=2)}
            
            Create a focused classification that:
            1. Accurately describes their specific interests or industry based on their responses
            2. Provides detailed summaries of the most relevant content
            3. Includes specific features, capabilities, or information they would find valuable
            
            Write content summaries as informative sentences that directly describe the relevant information."""

            response = self.client.chat.completions.create(
                model=self.content_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7
            )

            raw_response = response.choices[0].message.content.strip()
            logger.info(f"Raw classification response: {raw_response}")
            cleaned_response = raw_response.strip('`').replace('```json', '').replace('```', '').strip()
            
            try:
                classification = json.loads(cleaned_response)
                # Validate the quality of the response
                if not self._is_valid_classification(classification):
                    raise ValueError("Classification doesn't meet quality standards")
                print("classification")
                print(classification)
                return classification
            except Exception as e:
                logger.error(f"Classification error: {e}")
                return self._generate_focused_classification(content_analysis, responses)

        except Exception as e:
            logger.error(f"Classification generation error: {e}")
            return self._generate_focused_classification(content_analysis, responses)

    def _is_valid_classification(self, classification: Dict) -> bool:
        """Validate classification quality"""
        if not all(key in classification for key in ['interests', 'relevant_sections']):
            return False
            
        # Check for generic phrases
        generic_phrases = ['the website provides', 'information about', 'contains information']
        for section in classification['relevant_sections']:
            if any(phrase in section.lower() for phrase in generic_phrases):
                return False
                
        # Ensure sections are detailed enough
        if any(len(section) < 50 for section in classification['relevant_sections']):
            return False
                
        return True

    def _generate_focused_classification(self, content_analysis: Dict, responses: List[Dict]) -> Dict:
        """Generate a focused classification with specific content summaries"""
        print('focused')
        try:
            # Extract the main topic of interest from responses
            main_interest = responses[-1]['answer']
            
            # Find the most relevant content sections
            relevant_content = []
            sections = content_analysis.get('sections', [])
            
            # Create detailed summaries based on matching content
            for section in sections:
                content = section.get('content', '') if isinstance(section, dict) else str(section)
                if any(keyword.lower() in content.lower() for keyword in main_interest.split()):
                    summary = content.strip()
                    if len(summary) > 50:  # Ensure it's a substantial summary
                        relevant_content.append(summary)
                
            # If we found relevant content, use it; otherwise, create a general summary
            if relevant_content:
                return {
                    "interests": [
                        f"Focused interest or industry in {main_interest} and its specific capabilities"
                    ],
                    "relevant_sections": [
                        f"{summary[:200]}..." for summary in relevant_content[:2]
                    ]
                }
                
            return {
                "interests": [
                    f"Interest or industry in {main_interest} features and functionality"
                ],
                "relevant_sections": [
                    "Latest features include advanced performance capabilities and innovative technology integrations.",
                    "Comprehensive functionality offering enhanced user experience and productivity improvements."
                ]
            }
                
        except Exception as e:
            logger.error(f"Focused classification error: {e}")
            return {
                "interests": [
                    "Interest or industry in specific product features and capabilities"
                ],
                "relevant_sections": [
                    "Advanced features and capabilities designed for optimal performance.",
                    "Integrated functionality providing enhanced user experience."
                ]
            }

    def should_generate_classification(self, content_analysis: Dict, responses: List[Dict]) -> bool:
        """Determine if we have enough specific information to generate a classification"""
        try:
            prompt = """Analyze these user responses and determine if we have enough specific information 
            to generate a meaningful classification of their interests or industry.
            
            Return true only if:
            1. Responses show clear interest or industry in specific topics
            2. We have enough context to identify relevant content sections
            3. Additional questions would not significantly improve understanding
            
            Return only 'true' or 'false'"""

            response = self.client.chat.completions.create(
                model=self.question_model,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": json.dumps({
                        "content_analysis": content_analysis,
                        "responses": responses
                    })}
                ],
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip().lower() == 'true'
        except Exception as e:
            logger.error(f"Classification decision error: {e}")
            return len(responses) >= 2  # Default to true if we have at least 2 responsesp
