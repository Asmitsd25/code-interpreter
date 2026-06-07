from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from io import StringIO
import sys
import traceback
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodeRequest(BaseModel):
    code: str

class CodeResponse(BaseModel):
    error: List[int]
    result: str

def execute_python_code(code: str):
    old_stdout = sys.stdout
    sys.stdout = StringIO()

    try:
        exec(code)
        output = sys.stdout.getvalue()
        return {
            "success": True,
            "output": output
        }

    except Exception:
        output = traceback.format_exc()
        return {
            "success": False,
            "output": output
        }

    finally:
        sys.stdout = old_stdout

def analyze_error(traceback_text: str):
    import re

    matches = re.findall(
        r'File "<string>", line (\d+)',
        traceback_text
    )

    return [int(x) for x in matches]

@app.post("/code-interpreter")
async def code_interpreter(req: CodeRequest):

    result = execute_python_code(req.code)

    if result["success"]:
        return {
            "error": [],
            "result": result["output"]
        }

    return {
        "error": analyze_error(result["output"]),
        "result": result["output"]
    }
