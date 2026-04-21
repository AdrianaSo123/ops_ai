import requests
import json
import uuid
import time

def run_test():
    url = "http://127.0.0.1:8000/api/orchestrate"
    # New Phase 2 Fields
    org_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    # Prompt user for input (New in Phase 3)
    input_text = input("✍️  Enter your orchestration request: ")
    if not input_text:
        input_text = "We signed Acme Corp. They need onboarding and a kickoff meeting."
    
    payload = {
        "input_text": input_text,
        "organization_id": org_id,
        "user_id": user_id
    }
    
    print(f"\n🚀 Sending Orchestration Request: {payload['input_text']}")
    # Note: organization_id and user_id are query params in the current FastAPI implementation
    response = requests.post(url, params=payload)
    
    if response.status_code != 200:
        print(f"❌ Failed to start orchestration: {response.text}")
        return

    orchestration = response.json()
    orch_id = orchestration["id"]
    print(f"✅ Success! Orchestration ID: {orch_id}")
    print(f"📡 Listening to stream at: {url}/{orch_id}/stream\n")

    # Monitoring the initial reasoning pipeline
    stream_url = f"{url}/{orch_id}/stream"
    with requests.get(stream_url, stream=True) as r:
        for line in r.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith("data: "):
                    event_data = json.loads(decoded_line[6:])
                    stage = event_data.get("stage")
                    status = event_data.get("status")
                    print(f"[{stage}] {status}")
                    
                    if status == "PENDING_APPROVAL":
                        print("\n🛑 PAUSED: Human-in-the-loop Governance triggered.")
                        print(f"To resume this orchestration, run:")
                        print(f"curl -X POST http://127.0.0.1:8000/api/orchestrate/{orch_id}/approve")
                        break

if __name__ == "__main__":
    try:
        run_test()
    except Exception as e:
        print(f"❌ Test Client Error: {e}")
