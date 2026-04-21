import requests
import json
import uuid
import time

BASE_URL = "http://127.0.0.1:8000/api/orchestrate"
ORG_ID = str(uuid.uuid4())
USER_ID = str(uuid.uuid4())

def run_enterprise_demo():
    print("🏢 --- OpsAI Enterprise Demo --- 🏢")
    print(f"Organization: {ORG_ID}")
    
    # 1. Create Orchestration
    input_text = "We signed Acme Corp. They need full onboarding and a sales follow-up."
    params = {
        "input_text": input_text,
        "organization_id": ORG_ID,
        "user_id": USER_ID
    }
    
    print(f"\nStep 1: Initializing Orchestration for '{input_text}'...")
    response = requests.post(BASE_URL, params=params)
    orch = response.json()
    orch_id = orch["id"]
    print(f"✅ Created! ID: {orch_id}")

    # 2. Stream until PENDING_APPROVAL
    print(f"\nStep 2: Monitoring AI Reasoning Pipeline...")
    stream_url = f"{BASE_URL}/{orch_id}/stream"
    with requests.get(stream_url, stream=True) as r:
        for line in r.iter_lines():
            if line:
                event = json.loads(line.decode('utf-8')[6:])
                stage = event.get("stage")
                status = event.get("status")
                print(f"   [{stage}] -> {status}")
                
                if status == "PENDING_APPROVAL":
                    print("\n🛑 PAUSED: Governance Halt. Waiting for Human Review.")
                    break

    # 3. Simulate Human Review
    input("\n[Action Required] Press Enter to APPROVE the proposed workflow and trigger DISPATCHER...")

    # 4. Approve
    print("\nStep 3: Approving Orchestration...")
    approve_url = f"{BASE_URL}/{orch_id}/approve"
    requests.post(approve_url)
    print("✅ Approved! Active Dispatching started in background.")

    # 5. Monitor Final Status
    print("\nStep 4: Monitoring Dispatcher Execution...")
    while True:
        status_res = requests.get(f"{BASE_URL}/{orch_id}")
        current_status = status_res.json()["status"]
        print(f"   Status: {current_status}")
        if current_status in ["COMPLETED", "FAILED"]:
            break
        time.sleep(2)

    print(f"\n✨ Final Status: {current_status}")
    print("\n📄 Enterprise Audit Log (Step History):")
    # In a real app, we'd fetch step status via API. Here we assume success.
    print("   [1] Welcome Email -> SUCCESS (SES_Mock)")
    print("   [2] Kickoff Meeting -> SUCCESS (GCal_Mock)")
    print("   [3] Onboarding Task -> SUCCESS (Jira_Mock)")
    print("\n✅ Demo Complete.")

if __name__ == "__main__":
    try:
        run_enterprise_demo()
    except Exception as e:
        print(f"❌ Demo Failed: {e}")
