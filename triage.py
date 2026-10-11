import json
from dotenv import load_dotenv
from pydantic import ValidationError
from Core.models import TriageResult
from Core.prompts import SYSTEM_PROMPT
from datetime import date
import anthropic

load_dotenv()
client = anthropic.Anthropic()
today = date.today()
system_prompt = SYSTEM_PROMPT.format(current_date=today)

with open("Data/dispute_cases.json") as f:
    data = json.load(f)

triage_tool = {
    "name": "submit_triage_result",
    "description": "returns result based on json schema",
    "input_schema": TriageResult.model_json_schema()
}

tools = [triage_tool]


def triage_case(case):
    deadline = date.fromisoformat(case["response_deadline"])
    days_until_deadline = (deadline - today).days
    case["response_deadline"] = deadline.isoformat()
    case["days_until_deadline"] = days_until_deadline
    case_json = json.dumps(case)

    message = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=2048,
        system=system_prompt,
        tools=tools,
        tool_choice={"type": "tool", "name": "submit_triage_result"},
        messages=[{"role": "user", "content": case_json}]
    )

    result = None
    for block in message.content:
        if block.type == "tool_use":
            try:
                result = TriageResult.model_validate(block.input)
            except ValidationError as e:
                print(e)
    return result

