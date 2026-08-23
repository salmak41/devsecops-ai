from fastapi import FastAPI
from pydantic import BaseModel
from model import calculate_risk

app = FastAPI()

class PipelineData(BaseModel):
    test_pass_rate: float
    vulnerabilities: int
    build_time: float

@app.post("/predict")
def predict(data: PipelineData):
    risk, decision = calculate_risk(
        data.test_pass_rate,
        data.vulnerabilities,
        data.build_time
    )

    return {
        "risk_score": risk,
        "decision": decision
    }