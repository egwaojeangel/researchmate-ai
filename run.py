import os
from dotenv import load_dotenv

load_dotenv()

if not os.environ.get('GROQ_API_KEY'):
    print("\n⚠️  WARNING: GROQ_API_KEY not found.")
    print("   Create a .env file with: GROQ_API_KEY=your-key-here\n")

from app import app

if __name__ == '__main__':
    print("\n" + "="*50)
    print("  ResearchMate AI")
    print("  Open: http://localhost:5000")
    print("="*50 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)