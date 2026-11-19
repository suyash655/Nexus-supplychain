from config import GEMINI_API_KEY, GROQ_API_KEY
from google import genai
from groq import Groq

groq_client = Groq(api_key=GROQ_API_KEY)
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

def call_llm(prompt: str, system_prompt: str = "") -> str:
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )
        return response.choices[0].message.content

    except Exception as e:
        print(f"Groq failed: {e}, falling back to Gemini")
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"{system_prompt}\n\n{prompt}"
        )
        return response.text
