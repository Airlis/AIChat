from openai import OpenAI, OpenAIError
from flask import current_app

def analyze_content(content):
    if not content:
        print("No content to analyze.")
        return []
    client = OpenAI(api_key=current_app.config['OPENAI_API_KEY'])

    prompt = f"SAnalyze the following website content and list the top 5 interests or industries that visitors might have:\n\n{content}\n\nProvide the interests as a comma-separated list."

    try:
        response = client.chat.completions.create(
            model='gpt-4o',
            messages=[
                {
                    "role": "system",
                    "content": "You analyze website content and extract key interests or industries relevant to visitors.",
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            max_tokens=150,
            temperature=0.5,
        )

        topics_text = response.choices[0].message.content.strip()
        topics = [topic.strip() for topic in topics_text.split(',')]
        return topics
    except OpenAIError as e:
        print(f"OpenAI API error: {e}")
        return []


def generate_questions(topics):
    if not topics:
        print("No topics provided for question generation.")
        return []
    client = OpenAI(api_key=current_app.config['OPENAI_API_KEY'])
    questions = []
    for topic in topics:
        prompt = (
            f"Create a question to determine if a visitor is interested in '{topic}'.\n"
            "The question should be clear, direct, and answerable with 'Yes' or 'No'.\n"
            "Example:\n"
            f"Are you interested in {topic}?\n"
        )

        try:
            response = client.chat.completions.create(
                model='gpt-4o',
                messages=[
                    {
                        "role": "system",
                        "content": "You create questions to determine if a website visitor is interested in specific topics.",
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                max_tokens=200,
                temperature=0.7,
            )
        

            text = response.choices[0].message.content.strip()
            question_text, options = parse_question_and_options(text)
            questions.append({
                'questionText': question_text,
                'options': options
            })
        except OpenAIError as e:
            print(f"OpenAI API error: {e}")
            questions.append("")
    return questions

def parse_question_and_options(text):
    question_text = text.strip()
    options = [{'text': 'Yes'}, {'text': 'No'}]
    return question_text, options

def generate_classification(answers):
    client = OpenAI(api_key=current_app.config['OPENAI_API_KEY'])
    prompt = "Based on the following user answers, classify the user's interest:\n\n"
    for index, answer in answers.items():
        prompt += f"Question {index}: {answer}\n"
    prompt += "\nProvide a concise classification."

    try:
        response = client.chat.completions.create(
            model='gpt-4o',
            messages=[
                {
                    "role": "system",
                    "content": "You are an assistant that classifies user interests based on their answers to questions."
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            max_tokens=100,
            temperature=0.5,
        )

        classification = response.choices[0].message.content.strip()

        return classification
    except OpenAIError as e:
        print(f"OpenAI API error: {e}")
        return ""
