from dotenv import load_dotenv
load_dotenv()
import os
k = os.getenv("OPENAI_API_KEY")
print(repr(k))
print("starts_with_quote:", k.startswith('"') if k else False, "ends_with_quote:", k.endswith('"') if k else False)
