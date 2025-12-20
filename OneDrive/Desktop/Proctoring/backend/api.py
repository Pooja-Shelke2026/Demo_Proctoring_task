from fastapi import FastAPI
from pydantic import BaseModel
from db.db import insert_event

app = FastAPI()

class TabSwitchEvent(BaseModel):
    session_id: int
    start_time_ms: int
    end_time_ms: int

@app.post("/tab-switch")
def tab_switch(event: TabSwitchEvent):
    insert_event(
        event.session_id,
        "TAB_SWITCH",
        event.start_time_ms,
        event.end_time_ms,
        severity=5
    )
    return {"status": "logged"}
