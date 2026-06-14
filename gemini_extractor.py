import os
import json
import re
import google.generativeai as genai

def extract_knowledge_graph(text):
    """
    Sends the input text to Gemini 2.5 Flash and extracts structured JSON 
    representing entities and relationships.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"error": "API key not configured."}

    genai.configure(api_key=api_key)
    
    # Initialize Gemini 2.5 Flash
    model = genai.GenerativeModel('gemini-2.5-flash')

    prompt = f"""
    You are an expert Data Scientist and Linguist. Extract a Knowledge Graph from the provided text.
    Identify the main entities and the relationships between them.

    Return the result STRICTLY as a valid JSON object with two keys: 'entities' and 'relationships'.
    Do not add any markdown formatting, explanations, or text outside the JSON object.

    Format Schema:
    {{
      "entities": [
        {{"name": "EntityName", "type": "EntityType"}}
      ],
      "relationships": [
        {{"source": "EntityName1", "relation": "RELATION_TYPE", "target": "EntityName2"}}
      ]
    }}

    Text to analyze:
    "{text}"
    """

    try:
        response = model.generate_content(prompt)
        raw_text = response.text.strip()
        
        # Clean up markdown code blocks if the model includes them despite instructions
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
            
        kg_data = json.loads(raw_text.strip())
        return kg_data
        
    except json.JSONDecodeError as e:
        print(f"JSON Parsing Error: {e}\nRaw Output: {raw_text}")
        return {"error": "Failed to parse the structured data from the AI response."}
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return {"error": f"AI extraction failed: {str(e)}"}