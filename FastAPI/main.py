from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, field_validator

app=FastAPI(
    title="AI Agent Management API",
    version="1.0.0"
)

# 1. request schema
class AgentCreate(BaseModel):
    name:str=Field(min_length=1,max_length=100)
    model: str=Field(min_length=1)
    temperature:float=Field(ge=0,le=2)

    @field_validator("name","model")
    @classmethod
    def validate_text(cls,value:str)->str:
        value=value.strip()
        if not value:
            raise ValueError("Value cannot be blank")
        return value

#2. response schema
class AgentResponse(AgentCreate):
    id:int

#3. In memory storage
agents: dict[int,AgentResponse]={}
next_agent_id=1

#4. health check
@app.get("/health")
def health():
    return{"status":"healthy"}


#5. create an agent
@app.post(
    "/agents",
    response_model=AgentResponse,
    status_code=status.HTTP_201_CREATED)
def create_agent(agent:AgentCreate):
    global next_agent_id
    new_agent=AgentResponse(
        id=next_agent_id,
        **agent.model_dump()
    )

    agents[next_agent_id]=new_agent
    next_agent_id+=1
    return new_agent

#6. retrive an agent
@app.get("/agents/{agent_id}",
         response_model=AgentResponse)
def get_agent(agent_id: int):
    if agent_id not in agents:
        raise HTTPException(
            status_code=404,
            detail="Agent not found"
        )

    return agents[agent_id]

