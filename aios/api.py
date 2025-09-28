# aios/api.py
# Λ-Möbius Core – FastAPI service
from fastapi import FastAPI
from pydantic import BaseModel
from mobius_motor.core import motor_step
from mobius_motor.optimize import lambda_optimize
from mobius_motor.arbiter import phi_arbiter  # import direct, fără duplicat

app = FastAPI(title="Λ-Möbius Core API", version="0.1.0")

class StepInput(BaseModel):
    k: float
    P: float
    U: float
    theta: float

class OptimizeInput(BaseModel):
    k: float = 1.0
    P: float = 1.0
    U: float = 5.0
    theta: float
    mode: str  # "value" or "state"
    target: float | None = None
    desired_state: int | None = None

@app.post("/step")
def api_step(inp: StepInput):
    val, st = motor_step(k=inp.k, P=inp.P, U=inp.U, theta=inp.theta)
    state_desc = {1: "Λ-Wrap", 0: "Λ-Steady", -1: "Λ-Unwrap"}[st]
    return {
        "params": inp.dict(),
        "value": val,
        "state": st,
        "state_desc": state_desc,
    }

@app.post("/optimize")
def api_optimize(inp: OptimizeInput):
    if inp.mode == "value":
        res = lambda_optimize(
            initial_guess=(inp.k, inp.P, inp.U),
            theta=inp.theta,
            mode="value",
            target=inp.target,
            desired_state=inp.desired_state,
        )
    else:
        res = lambda_optimize(
            initial_guess=(inp.k, inp.P, inp.U),
            theta=inp.theta,
            mode="state",
            desired_state=inp.desired_state,
        )
    return res
