"""Setup 7.23: Command Preflight."""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json

@dataclass(frozen=True)
class CommandPreflight:
    task_id: str
    commands: tuple
    allowed: tuple
    blocked: tuple
    digest: str

    def valid(self):
        payload={"task_id":self.task_id,"commands":list(self.commands),"allowed":list(self.allowed),"blocked":list(self.blocked)}
        return bool(self.digest) and self.digest == sha256(json.dumps(payload,sort_keys=True,separators=(",",":" )).encode()).hexdigest()

def _make(task_id, commands, allowed, blocked):
    values=(str(task_id),tuple(commands or ()),tuple(allowed or ()),tuple(blocked or ()))
    payload={"task_id":values[0],"commands":list(values[1]),"allowed":list(values[2]),"blocked":list(values[3])}
    digest=sha256(json.dumps(payload,sort_keys=True,separators=(",",":" )).encode()).hexdigest()
    return CommandPreflight(*values,digest)

def build_command_preflight(task_id: str, *args, **kwargs) -> CommandPreflight:
    if args:
        commands=args[0] if len(args)>0 else []
        allowed=args[1] if len(args)>1 else []
        blocked=args[2] if len(args)>2 else []
        return _make(task_id, commands, allowed, blocked)
    commands=kwargs.get("commands", [])
    scope=kwargs.get("scope", [])
    expected=kwargs.get("expected", [])
    return _make(task_id, commands, scope, expected)

def valid_command_preflight(obj) -> bool:
    return isinstance(obj, CommandPreflight) and obj.valid()
