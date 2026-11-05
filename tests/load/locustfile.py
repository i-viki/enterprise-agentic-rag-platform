from locust import HttpUser, task, between
import uuid

class EnterpriseRagUser(HttpUser):
    wait_time = between(0.5, 2.0)

    @task(3)
    def query_cognition(self):
        payload = {
            "prompt": "What is the domestic flight reimbursement limit under corporate travel policy?",
            "thread_id": f"thread-locust-{uuid.uuid4().hex[:8]}",
            "user_id": "locust-load-tester",
            "tenant_id": "tenant-enterprise-prod",
            "clearance_level": 1,
            "user_roles": ["EMPLOYEE"]
        }
        self.client.post("/api/v1/cognition/query", json=payload)

    @task(1)
    def health_check(self):
        self.client.get("/actuator/health")

