import json
import os
import uuid

from ..tools.validator import (
    validate_tool_arguments as validate_tool_call
)

from .agent import (
    execute_tool,
    parse_tool_call,
    get_tool_prompt,
    get_tool_schema,
    TOOL_REGISTRY,
)
from ..models.lm_studio import LMStudioGateway
from ..tools.project import list_projects
from services.task_planner import TaskPlan, TaskPlanner
from services.task_decomposer import TaskDecomposer
from services.task_context import build_task_context
from services.impact_verification import build_impact_verification, ImpactVerification
from services.completion_evidence import CompletionEvidenceLedger, make_evidence
from services.evidence_recovery import EvidenceRecoveryPlan, build_evidence_recovery
from services.completion_receipt import CompletionReceipt, issue_completion_receipt
from services.completion_finalization import CompletionFinalization, issue_completion_finalization
from services.completion_audit import CompletionAuditTrail
from services.completion_audit_seal import CompletionAuditSeal, issue_completion_audit_seal
from services.completion_proof import CompletionProof, issue_completion_proof
from services.completion_proof_commitment import CompletionProofCommitment, issue_completion_proof_commitment
from services.completion_release import CompletionRelease, issue_completion_release
from services.completion_dispatch import CompletionDispatch, issue_completion_dispatch
from services.completion_emission import CompletionEmission, issue_completion_emission
from services.completion_emission_audit import CompletionEmissionAuditTrail
from services.completion_emission_recovery import CompletionEmissionRecovery, inspect_completion_emission, reconcile_emitted
from services.completion_terminal_consistency import CompletionTerminalConsistency, build_terminal_consistency
from services.completion_emission_resolution import CompletionEmissionResolution, issue_resolution
from services.completion_attestation import (
    CompletionAttestation,
    build_task_identity,
    create_attestation,
    build_runtime_identity,
    build_policy_identity,
)
from services.evidence_freshness import next_change_epoch, normalize_epoch, normalize_resource_key
from .memory import (
    initialize_memory,
    create_conversation,
    update_conversation,
    add_message,
    add_action,
    list_conversations,
    get_conversation,
    resume_conversation,
    recoverable_conversations,
    set_conversation_status,
)


MAX_STEPS = 16

WORKSPACE_DIR = os.path.abspath("workspace")
PROJECTS_DIR = os.path.abspath("projects")

TRUST_FLAG_FILE = ".aziz_trusted"

# Setup 4.9: persistent conversation/task memory.
initialize_memory()


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are Aziz AI, a local autonomous coding agent.

Your job is to complete the ORIGINAL user task safely and accurately.

You operate using this cycle:

OBSERVE → ACT → OBSERVE → VERIFY → REPAIR → VERIFY → DONE

==================================================
CORE RULES
==================================================

1. Work on the EXACT project and file mentioned by the user.

2. Never invent a project name.

3. Never silently change a requested path.

4. Before modifying an existing file, READ it first.

5. Preserve the existing code and structure unless the user
   explicitly asks for structural changes.

6. Make the smallest necessary change.

7. After modifying a file, READ THE SAME FILE again.

8. Verification must be based on actual tool output.

9. Never claim something was done unless a tool result confirms it.

10. Never invent tool output.

11. Use exactly ONE action per response.

12. Never use a tool that is not in the TOOL CONTRACT.

13. Never invent argument names.

14. Use the EXACT argument names in the TOOL CONTRACT.

15. If a tool fails, inspect the actual error before continuing.

16. Do not repeat a failed destructive action.

17. Reading or listing the same resource multiple times is allowed
    when required for observation or verification.

18. Do not modify a file if it already satisfies the user's request.

19. Do not create a replacement file just because a requested file
    cannot be found.

20. If the requested resource genuinely does not exist and the
    user's request is ambiguous, use ask_user.

21. When every requirement has been verified, use final_answer.

==================================================
IMPORTANT: EXISTING FILES
==================================================

If the user says:

"Fix X. First read X."

You MUST:

1. read X
2. inspect the actual contents
3. determine what needs changing
4. modify only if necessary
5. read X again
6. verify the requested requirements
7. final_answer

If X is already correct:

DO NOT rewrite it unnecessarily.

Instead:

read X
→ determine already correct
→ read X again if verification was requested
→ final_answer

==================================================
IMPORTANT: VERIFICATION
==================================================

A successful write does NOT automatically mean the task is verified.

After:

write_file

you normally need:

read_file

Then inspect the returned content.

For example:

User requests:

"Make the heading centered."

Correct workflow:

read_file
→ write_file
→ read_file
→ verify heading/class
→ final_answer

==================================================
IMPORTANT: REPAIR
==================================================

If verification shows that the requested change is missing or wrong:

1. identify the actual problem
2. make the smallest repair
3. read the file again
4. verify again

Do NOT claim success before verification.

==================================================
SPECIAL ACTIONS
==================================================

final_answer

Use only when the task is completely verified.

Format:

{
  "action": "final_answer",
  "arguments": {
    "answer": "..."
  }
}

ask_user

Use only when clarification is genuinely necessary.

Format:

{
  "action": "ask_user",
  "arguments": {
    "question": "..."
  }
}

==================================================
PROJECT ROUTING RULE
==================================================


There are TWO separate file locations:

1. WORKSPACE
   Location: workspace/
   Tools:
   - read_file
   - write_file
   - edit_file
   - list_files
   - create_folder

2. PROJECTS
   Location: projects/
   Tools:
   - read_project_file
   - write_project_file
   - edit_project_file
   - list_project_files
   - run_project_command

CRITICAL:

If the user mentions a project by name, you MUST use project tools.

For example:

User:
"Change my_website/index.html"

Here "my_website" is a project name.

You MUST interpret this as:

project = "my_website"
path = "index.html"

You MUST use:

read_project_file
edit_project_file
read_project_file

You MUST NOT use:

read_file
write_file
edit_file
list_files

Do not confuse:

workspace/my_website/index.html

with:

projects/my_website/index.html

They are different files.

If the requested project does not exist, use list_projects to verify the available projects before doing anything else.

For an existing project file:

1. Read it using read_project_file.
2. Determine the smallest required change.
3. Use edit_project_file for a small modification.
4. Read it again using read_project_file.
5. Verify the requested change.
6. Only then return final_answer.

Never use write_project_file to rewrite an existing file when edit_project_file can make the requested change.


==================================================
PROJECT VS WORKSPACE RULES
==================================================

There are two separate locations.

WORKSPACE:
- workspace/
- Use read_file, write_file, edit_file, list_files, create_folder.
- These tools operate inside workspace/.

PROJECTS:
- projects/
- A project has a project name such as "my_website".
- If the user explicitly says "project", "my_website project",
  or refers to a known project, use project-specific tools.
- Use read_project_file to read project files.
- Use edit_project_file for small changes to existing project files.
- Use write_project_file only when creating a new project file or
  when the user explicitly requests replacing the complete file.
- Use list_project_files to inspect a project.
- Use run_project_command to execute commands inside a project.

IMPORTANT:
Never confuse workspace/my_website with projects/my_website.

If the user says:
"Fix my_website project/index.html"

interpret it as:

project = "my_website"
path = "index.html"

Use:
read_project_file
edit_project_file
read_project_file

Do NOT use:
read_file
edit_file
write_file

==================================================
EDITING RULES
==================================================

Use edit_file when making a small, localized change to an existing file.

Examples:

- Add a CSS class to an existing HTML element.
- Change one function.
- Change one variable.
- Fix one line.
- Replace a specific HTML element.

Do NOT use write_file to rewrite an entire existing file
when edit_file can safely make the requested change.

For existing files:

READ → EDIT → READ → VERIFY

If edit_file reports that the exact text was not found,
do not invent replacement content. Read the file again
and determine the correct edit.

==================================================
EDITING EXISTING FILES
==================================================

For a small change to an existing file, prefer edit_file.

Examples:

- Add a CSS class to an existing HTML element.
- Change one HTML attribute.
- Change one CSS property.
- Change one function.
- Change one variable.
- Replace one specific piece of code.

Use this workflow:

READ → EDIT → READ → VERIFY

Do NOT rewrite the entire existing file with write_file
when edit_file can safely make the requested change.

edit_file requires:

{
  "action": "edit_file",
  "arguments": {
    "path": "...",
    "old_text": "...",
    "new_text": "..."
  }
}

The old_text must come from the actual file contents.

Never invent old_text.

If edit_file reports that old_text was not found,
read the file again and determine the correct edit.


==================================================
TOOL SELECTION
==================================================

read_file:
Use ONLY for files inside workspace/.

write_file:
Use for creating or completely replacing a workspace file when appropriate.

edit_file:
Use ONLY for small, localized edits to existing files inside workspace/.

list_files:
Use to inspect files and folders inside workspace/.

create_folder:
Use to create folders inside workspace/.

read_project_file:
Use ONLY for files inside projects/<project>/.

write_project_file:
Use for creating a new file inside an existing project, or when the user explicitly asks to replace a complete project file.

edit_project_file:
Use for small, localized edits to existing project files.
Examples: add a CSS class, change an HTML attribute, change one CSS property, fix one JavaScript/Python function, or replace one specific piece of code.

list_projects:
Use to discover existing projects or verify whether a requested project exists.

list_project_files:
Use to inspect files and folders inside a project.

run_project_command:
Use to execute commands inside a specific project, such as npm install, npm run build, Python scripts, or Gradle commands.

run_command:
Use for general system commands when they are not specifically associated with a project.

run_python:
Use to execute an existing Python script through the registered Python tool.

open_vscode:
Use when the user asks Aziz to open a workspace, project, or file in Visual Studio Code.

create_project:
Use when the user asks to create a new project.

==================================================
PROJECT TYPE SELECTION
==================================================

When creating a project, follow the technology explicitly requested by the user.

HTML/CSS/JavaScript:
Create a normal web project using separate files when appropriate:
- index.html
- style.css
- script.js

React:
Create a React project and use the project's package/build commands.

Kotlin:
Create a Kotlin/Android project using Kotlin and Gradle project files.

Python:
Create a Python project using appropriate Python files.

Never silently change the requested technology.
If the technology is unclear and the choice materially changes the project structure, use ask_user.

==================================================
WEBSITE CREATION RULES
==================================================

When the user asks for a website, portfolio, landing page, dashboard, or similar web project:

1. Determine the requested technology.
2. If HTML/CSS/JavaScript is requested, keep HTML, CSS, and JavaScript in separate files.
3. index.html must reference style.css with a relative stylesheet link.
4. When JavaScript is needed, index.html must reference script.js with a script tag.
5. Do not put CSS inside index.html unless the user explicitly requests inline CSS.
6. Do not put JavaScript inside index.html unless the user explicitly requests inline JavaScript.
7. For a new project, create the project first, then create its files.
8. After creation, list/read the relevant files and verify the structure and requested content.
9. For an existing project, read before editing and use edit_project_file for small changes.
10. Only use final_answer after verification from actual tool output.

==================================================
EXISTING PROJECT EDIT WORKFLOW
==================================================

For an existing project file:

READ → EDIT → READ → VERIFY → DONE

Use read_project_file first.
Use edit_project_file for a small change.
Use write_project_file only for a new file or an explicitly requested complete replacement.
After any modification, read the same file again.

If edit_project_file says old_text was not found:
1. Do not guess.
2. Read the file again.
3. Use the actual returned content to determine the correct edit.

==================================================
WORKSPACE VS PROJECT
==================================================

If the user mentions a named project such as my_website, use project tools.
Interpret:
my_website/index.html
as:
project = my_website
path = index.html

Never confuse projects/my_website with workspace/my_website.

==================================================
OUTPUT FORMAT
==================================================

When using a tool, output ONLY JSON.

When using final_answer, output ONLY JSON.

When using ask_user, output ONLY JSON.

Never output Markdown around JSON.

Never output two JSON objects.

==================================================
TOOL CONTRACT
==================================================

"""

SYSTEM_PROMPT += get_tool_prompt()


# ============================================================
# MODEL
# ============================================================

model_gateway = LMStudioGateway()


def ask_model(messages):
    return model_gateway.chat(
        messages=messages,
        temperature=0.0,
    )


# ============================================================
# TOOL CONTRACTS
# ============================================================

def get_tool_contracts():

    contracts = {}

    for tool in get_tool_schema():

        arguments = {}

        for argument in tool["arguments"]:

            arguments[argument["name"]] = {
                "required": argument["required"]
            }

        contracts[tool["name"]] = arguments

    return contracts


TOOL_CONTRACTS = get_tool_contracts()


# ============================================================
# VALIDATE TOOL ARGUMENTS
# ============================================================

def validate_tool_arguments(action, arguments):
    """
    Validate a model-generated tool call using the
    centralized validator.

    final_answer and ask_user are handled by the
    agent loop itself and are not registered tools.
    """

    if action in (
        "final_answer",
        "ask_user",
    ):
        return True, ""

    if not isinstance(arguments, dict):

        return (
            False,
            "Tool arguments must be a JSON object/dictionary."
        )

    return validate_tool_call(
        action,
        arguments,
        TOOL_REGISTRY.all(),
    )


# ============================================================
# ACTION SIGNATURE
# ============================================================

def action_signature(action, arguments):

    try:

        encoded = json.dumps(
            arguments,
            sort_keys=True,
            ensure_ascii=False,
        )

    except Exception:

        encoded = str(arguments)

    return f"{action}|{encoded}"


# ============================================================
# READ-ONLY TOOLS
# ============================================================

READ_ONLY_ACTIONS = {
    "read_file",
    "read_project_file",
    "list_files",
    "list_project_files",
    "list_projects",
}


# ============================================================
# DESTRUCTIVE / MODIFYING TOOLS
# ============================================================

MODIFYING_ACTIONS = {
    "write_file",
    "edit_file",
    "create_folder",
    "create_project",
    "write_project_file",
    "edit_project_file",
}


# ============================================================
# COMMAND TOOLS
# ============================================================

EXECUTION_ACTIONS = {
    "run_command",
    "run_python",
    "run_project_command",
}


# ============================================================
# ERROR DETECTION
# ============================================================

def is_error_result(result):

    if result is None:
        return True

    text = str(result).lower()

    markers = [
        "error:",
        "error executing",
        "failed:",
        "failure:",
        "file not found",
        "folder not found",
        "project not found",
        "unknown tool",
        "exception:",
        "traceback",
        "permission denied",
        "access denied",
    ]

    return any(
        marker in text
        for marker in markers
    )


# ============================================================
# AGENT STATE
# ============================================================

class AgentState:

    def __init__(self):

        self.phase = "OBSERVE"

        self.step = 0

        self.successful_actions = []

        self.failed_actions = []

        self.last_action = None

        self.last_result = None

        self.verification_requested = False

        self.modified_resources = set()

        self.observed_resources = set()

        # Setup 4.36: post-change impact verification checklist.
        self.impact_verification = None

        # Setup 4.37: compact evidence ledger for completion claims.
        self.completion_evidence = CompletionEvidenceLedger([], "not_required", [])

        # Setup 4.38: bounded evidence-driven repair/recovery checklist.
        self.evidence_recovery = EvidenceRecoveryPlan("not_required", [], [], [])

        # Setup 4.45: final completion attestation bound to the latest audit checkpoint.
        self.completion_attestation = CompletionAttestation()

        # Setup 4.58: persisted tamper-evident receipt issued only after
        # one-time completion attestation consumption.
        self.completion_receipt = CompletionReceipt()

        # Setup 4.59: persisted finalization lock issued only after a valid receipt.
        self.completion_finalization = CompletionFinalization()

        # Setup 4.60: bounded, tamper-evident audit history for finalized completions.
        self.completion_audit = CompletionAuditTrail()

        # Setup 4.61: seal the exact verified audit-trail state used for completion.
        self.completion_audit_seal = CompletionAuditSeal()

        # Setup 4.62: immutable end-to-end proof of the verified completion chain.
        self.completion_proof = CompletionProof()

        # Setup 4.63: terminal commitment to the exact completion proof.
        self.completion_proof_commitment = CompletionProofCommitment()

        # Setup 4.64: one-time final-answer release token bound to the terminal commitment.
        self.completion_release = CompletionRelease()

        # Setup 4.65: terminal dispatch authorization bound to the consumed release.
        self.completion_dispatch = CompletionDispatch()

        # Setup 4.66: durable two-phase journal for the final answer emission boundary.
        self.completion_emission = CompletionEmission()

        # Setup 4.67: bounded append-only history of terminal answer emissions.
        self.completion_emission_audit = CompletionEmissionAuditTrail()

        # Setup 4.68: durable crash-recovery/reconciliation state for terminal emission.
        self.completion_emission_recovery = CompletionEmissionRecovery()

        # Setup 4.69: read-only end-to-end terminal consistency preflight.
        self.completion_terminal_consistency = CompletionTerminalConsistency()

        # Setup 4.70: deterministic terminal emission recovery resolution.
        self.completion_emission_resolution = CompletionEmissionResolution()

        # Setup 4.39: bind completion evidence to the latest successful change.
        self.change_epoch = 0

        # Setup 4.40: track the latest modification generation per resource so
        # unrelated changes do not invalidate evidence for every modified file.
        self.modified_generations = {}

        # Setup 4.30/4.31: resumable structured execution plan and task decomposition.
        self.plan = None
        self.current_plan_step = None

    def record_action(
        self,
        action,
        arguments,
        result,
    ):

        signature = action_signature(
            action,
            arguments,
        )

        self.last_action = signature

        self.last_result = result

        if self.plan is not None and self.current_plan_step:
            self.plan.bind_current_step(self.current_plan_step)

        if is_error_result(result):

            if self.plan is not None and self.current_plan_step:
                repair_step = self.plan.adapt_after_result(action, result)
                if repair_step is not None:
                    self.current_plan_step = repair_step.id
                    self.plan.bind_current_step(self.current_plan_step)

            self.failed_actions.append(signature)
            self.phase = "REPAIR"

        else:

            # Setup 4.45: any successful action invalidates an earlier final seal.
            self.completion_attestation = CompletionAttestation()
            # A new successful action invalidates any prior completion receipt/lock.
            self.completion_receipt = CompletionReceipt()
            self.completion_finalization = CompletionFinalization()
            self.completion_audit_seal = CompletionAuditSeal()
            self.completion_proof = CompletionProof()
            self.completion_proof_commitment = CompletionProofCommitment()
            self.completion_release = CompletionRelease()
            self.completion_dispatch = CompletionDispatch()
            self.completion_emission = CompletionEmission()
            self.completion_emission_recovery = CompletionEmissionRecovery()
            self.completion_terminal_consistency = CompletionTerminalConsistency()
            self.completion_emission_resolution = CompletionEmissionResolution()

            if self.plan is not None and self.current_plan_step:
                # One successful tool action advances the current plan checkpoint.
                # The plan remains advisory; existing verification rules still decide completion.
                self.plan.mark_completed(self.current_plan_step)
                next_step = self.plan.next_step()
                self.current_plan_step = next_step.id if next_step else None
                self.plan.bind_current_step(self.current_plan_step)

            self.successful_actions.append(
                signature
            )

            # Setup 4.39: every successful modification starts a new evidence epoch,
            # invalidating verification evidence from earlier changes.
            if action in MODIFYING_ACTIONS:
                self.change_epoch = next_change_epoch(self.change_epoch)

            # Setup 4.37/4.39: record compact evidence bound to the current change epoch.
            evidence_path = arguments.get("path") or ""
            evidence_project = arguments.get("project") or ""
            if evidence_path and evidence_project:
                evidence_path = f"{evidence_project}/{evidence_path}"
            elif evidence_project and not evidence_path:
                evidence_path = str(evidence_project)
            if action in MODIFYING_ACTIONS:
                resource_key = normalize_resource_key(evidence_path)
                if resource_key:
                    self.modified_generations[resource_key] = self.change_epoch
                self.completion_evidence.add(
                    make_evidence(action, "modification", evidence_path, result, self.change_epoch, self.modified_generations.get(resource_key, self.change_epoch))
                )
            elif action in READ_ONLY_ACTIONS:
                self.completion_evidence.add(
                    make_evidence(action, "verification", evidence_path, result, self.change_epoch)
                )
            elif action in EXECUTION_ACTIONS:
                self.completion_evidence.add(
                    make_evidence(action, "execution", evidence_path, result, self.change_epoch)
                )
            self.completion_evidence.evaluate(self.impact_verification, self.verification_requested, self.change_epoch, self.modified_generations)
            self.evidence_recovery = build_evidence_recovery(
                self.completion_evidence, self.impact_verification, self.verification_requested
            )

            if action in MODIFYING_ACTIONS:

                path = arguments.get("path") or ""
                project = arguments.get("project") or ""
                if path:
                    self.modified_resources.add(str(path))
                    if project:
                        self.modified_resources.add(f"{project}/{path}")
                elif project:
                    self.modified_resources.add(str(project))

                self.verification_requested = True
                change_plan = None
                if self.plan is not None and getattr(self.plan, "context", None) is not None:
                    change_plan = getattr(self.plan.context, "change_plan", None)
                self.impact_verification = build_impact_verification(
                    change_plan, self.modified_resources, self.observed_resources
                )
                self.completion_evidence.evaluate(self.impact_verification, self.verification_requested, self.change_epoch, self.modified_generations)
                self.evidence_recovery = build_evidence_recovery(
                    self.completion_evidence, self.impact_verification, self.verification_requested
                )
                self.phase = "VERIFY"

            elif action in READ_ONLY_ACTIONS:

                path = arguments.get("path") or ""
                project = arguments.get("project") or ""
                if path:
                    self.observed_resources.add(str(path))
                    if project:
                        self.observed_resources.add(f"{project}/{path}")
                elif project:
                    self.observed_resources.add(str(project))

                change_plan = None
                if self.plan is not None and getattr(self.plan, "context", None) is not None:
                    change_plan = getattr(self.plan.context, "change_plan", None)
                self.impact_verification = build_impact_verification(
                    change_plan, self.modified_resources, self.observed_resources
                )
                self.completion_evidence.evaluate(self.impact_verification, self.verification_requested, self.change_epoch, self.modified_generations)
                self.evidence_recovery = build_evidence_recovery(
                    self.completion_evidence, self.impact_verification, self.verification_requested
                )
                self.phase = "VERIFY"

            elif action in EXECUTION_ACTIONS:

                self.phase = "VERIFY"

    def status(self):

        return (
            f"Phase={self.phase}; "
            f"step={self.step}; "
            f"successful={len(self.successful_actions)}; "
            f"failed={len(self.failed_actions)}; "
            f"plan_step={self.current_plan_step or 'none'}; "
            f"impact_verification={getattr(self.impact_verification, 'status', 'none')}; "
            f"completion_evidence={getattr(self.completion_evidence, 'status', 'none')}; "
            f"evidence_recovery={getattr(self.evidence_recovery, 'status', 'none')}; "
            f"change_epoch={getattr(self, 'change_epoch', 0)}"
        )



# ============================================================
# SETUP 4.12: PERSISTENT AGENT STATE
# ============================================================

def _safe_state_snapshot(state):
    """Return JSON-safe state needed to continue an agent workflow."""
    return {
        "phase": getattr(state, "phase", "OBSERVE"),
        "step": int(getattr(state, "step", 0)),
        "successful_actions": list(getattr(state, "successful_actions", [])),
        "failed_actions": list(getattr(state, "failed_actions", [])),
        "last_action": getattr(state, "last_action", None),
        "last_result": getattr(state, "last_result", None),
        "verification_requested": bool(
            getattr(state, "verification_requested", False)
        ),
        "change_epoch": normalize_epoch(getattr(state, "change_epoch", 0)),
        "modified_generations": {normalize_resource_key(k): normalize_epoch(v) for k, v in getattr(state, "modified_generations", {}).items() if normalize_resource_key(k)},
        "modified_resources": sorted(
            str(x) for x in getattr(state, "modified_resources", set())
        ),
        "observed_resources": sorted(
            str(x) for x in getattr(state, "observed_resources", set())
        ),
        "impact_verification": (
            state.impact_verification.to_dict()
            if getattr(state, "impact_verification", None) is not None else None
        ),
        "completion_evidence": (
            state.completion_evidence.to_dict()
            if getattr(state, "completion_evidence", None) is not None else None
        ),
        "evidence_recovery": (
            state.evidence_recovery.to_dict()
            if getattr(state, "evidence_recovery", None) is not None else None
        ),
        "completion_attestation": (
            state.completion_attestation.to_dict()
            if getattr(state, "completion_attestation", None) is not None else None
        ),
        "completion_receipt": (
            state.completion_receipt.to_dict()
            if getattr(state, "completion_receipt", None) is not None else None
        ),
        "completion_finalization": (
            state.completion_finalization.to_dict()
            if getattr(state, "completion_finalization", None) is not None else None
        ),
        "completion_audit": (
            state.completion_audit.to_dict()
            if getattr(state, "completion_audit", None) is not None else None
        ),
        "completion_audit_seal": (
            state.completion_audit_seal.to_dict()
            if getattr(state, "completion_audit_seal", None) is not None else None
        ),
        "completion_proof": (
            state.completion_proof.to_dict()
            if getattr(state, "completion_proof", None) is not None else None
        ),
        "completion_proof_commitment": (
            state.completion_proof_commitment.to_dict()
            if getattr(state, "completion_proof_commitment", None) is not None else None
        ),
        "completion_release": (
            state.completion_release.to_dict()
            if getattr(state, "completion_release", None) is not None else None
        ),
        "completion_dispatch": (
            state.completion_dispatch.to_dict()
            if getattr(state, "completion_dispatch", None) is not None else None
        ),
        "completion_emission": (
            state.completion_emission.to_dict()
            if getattr(state, "completion_emission", None) is not None else None
        ),
        "completion_emission_audit": (
            state.completion_emission_audit.to_dict()
            if getattr(state, "completion_emission_audit", None) is not None else None
        ),
        "completion_emission_recovery": (
            state.completion_emission_recovery.to_dict()
            if getattr(state, "completion_emission_recovery", None) is not None else None
        ),
        "completion_terminal_consistency": (
            state.completion_terminal_consistency.to_dict()
            if getattr(state, "completion_terminal_consistency", None) is not None else None
        ),
        "completion_emission_resolution": (
            state.completion_emission_resolution.to_dict()
            if getattr(state, "completion_emission_resolution", None) is not None else None
        ),
        "plan": (state.plan.to_dict() if getattr(state, "plan", None) else None),
        "current_plan_step": getattr(state, "current_plan_step", None),
    }


def _restore_state_snapshot(state, snapshot):
    """Restore a previously persisted state snapshot safely."""
    if not isinstance(snapshot, dict):
        return

    state.phase = str(snapshot.get("phase", "OBSERVE"))
    state.step = int(snapshot.get("step", 0) or 0)
    state.successful_actions = list(
        snapshot.get("successful_actions", [])
    )
    state.failed_actions = list(
        snapshot.get("failed_actions", [])
    )
    state.last_action = snapshot.get("last_action")
    state.last_result = snapshot.get("last_result")
    state.verification_requested = bool(
        snapshot.get("verification_requested", False)
    )
    state.change_epoch = normalize_epoch(snapshot.get("change_epoch", 0))
    raw_generations = snapshot.get("modified_generations", {})
    state.modified_generations = {normalize_resource_key(k): normalize_epoch(v) for k, v in raw_generations.items() if normalize_resource_key(k)} if isinstance(raw_generations, dict) else {}
    state.modified_resources = set(
        str(x) for x in snapshot.get("modified_resources", [])
    )
    state.observed_resources = set(
        str(x) for x in snapshot.get("observed_resources", [])
    )
    state.impact_verification = ImpactVerification.from_dict(snapshot.get("impact_verification"))
    state.completion_evidence = CompletionEvidenceLedger.from_dict(snapshot.get("completion_evidence")) or CompletionEvidenceLedger([], "not_required", [])
    state.evidence_recovery = EvidenceRecoveryPlan.from_dict(snapshot.get("evidence_recovery")) or build_evidence_recovery(state.completion_evidence, state.impact_verification, state.verification_requested)
    state.completion_attestation = CompletionAttestation.from_dict(snapshot.get("completion_attestation")) or CompletionAttestation()
    state.completion_receipt = CompletionReceipt.from_dict(snapshot.get("completion_receipt")) or CompletionReceipt()
    state.completion_finalization = CompletionFinalization.from_dict(snapshot.get("completion_finalization")) or CompletionFinalization()
    state.completion_audit = CompletionAuditTrail.from_dict(snapshot.get("completion_audit")) or CompletionAuditTrail()
    state.completion_audit_seal = CompletionAuditSeal.from_dict(snapshot.get("completion_audit_seal")) or CompletionAuditSeal()
    state.completion_proof = CompletionProof.from_dict(snapshot.get("completion_proof")) or CompletionProof()
    state.completion_proof_commitment = CompletionProofCommitment.from_dict(snapshot.get("completion_proof_commitment")) or CompletionProofCommitment()
    state.completion_release = CompletionRelease.from_dict(snapshot.get("completion_release")) or CompletionRelease()
    state.completion_dispatch = CompletionDispatch.from_dict(snapshot.get("completion_dispatch")) or CompletionDispatch()
    state.completion_emission = CompletionEmission.from_dict(snapshot.get("completion_emission")) or CompletionEmission()
    state.completion_emission_audit = CompletionEmissionAuditTrail.from_dict(snapshot.get("completion_emission_audit")) or CompletionEmissionAuditTrail()
    state.completion_emission_recovery = CompletionEmissionRecovery.from_dict(snapshot.get("completion_emission_recovery")) or CompletionEmissionRecovery()
    state.completion_terminal_consistency = CompletionTerminalConsistency.from_dict(snapshot.get("completion_terminal_consistency")) or CompletionTerminalConsistency()
    state.completion_emission_resolution = CompletionEmissionResolution.from_dict(snapshot.get("completion_emission_resolution")) or CompletionEmissionResolution()
    state.plan = TaskPlan.from_dict(snapshot.get("plan"))
    state.current_plan_step = snapshot.get("current_plan_step")
    if state.plan is not None:
        state.plan.bind_current_step(state.current_plan_step)


def _persist_agent_state(session):
    """Persist the complete resumable agent state."""
    if not getattr(session, "conversation_id", None):
        return False
    try:
        lifecycle = "waiting_for_user" if session.waiting_for_user else "active"
        set_conversation_status(
            session.conversation_id,
            lifecycle,
            pending_question=session.pending_question,
            agent_state=_safe_state_snapshot(session.state),
        )
        return True
    except Exception:
        return False


def _restore_agent_state(session, conversation):
    """Restore persisted agent state from either a dict or JSON text."""
    snapshot = {}
    if isinstance(conversation, dict):
        snapshot = conversation.get("agent_state") or {}

    if isinstance(snapshot, str):
        try:
            snapshot = json.loads(snapshot)
        except (TypeError, ValueError):
            snapshot = {}

    _restore_state_snapshot(session.state, snapshot)


# ============================================================
# AGENT SESSION
# ============================================================

class AgentSession:

    def __init__(self):

        self.messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            }
        ]

        self.state = AgentState()

        self.original_task = None

        self.waiting_for_user = False

        # Stores the exact clarification question asked by Aziz.
        # This lets the next user message continue the same task.
        self.pending_question = None

        # Setup 4.9: stable ID for this conversation/task.
        self.conversation_id = None

        # Setup 4.12: keep a resumed session attached to its saved conversation.
        self.resumed_conversation = False
        self.planner = TaskPlanner()
        self.decomposer = TaskDecomposer()
        self.task_context = None

    def start_task(self, user_input):

        self.original_task = user_input
        self.conversation_id = str(uuid.uuid4())
        self.resumed_conversation = False

        create_conversation(
            self.conversation_id,
            user_input,
        )

        self.waiting_for_user = False
        self.pending_question = None

        self.state = AgentState()
        self.task_context = build_task_context(user_input, WORKSPACE_DIR, PROJECTS_DIR)
        self.state.plan = self.decomposer.decompose(user_input, context=self.task_context)
        next_step = self.state.plan.next_step() if self.state.plan else None
        self.state.current_plan_step = next_step.id if next_step else None
        self.state.plan.bind_current_step(self.state.current_plan_step) if self.state.plan else None

        plan_text = (
            "SETUP 4.30 EXECUTION PLAN / SETUP 4.31 TASK DECOMPOSITION PLAN / SETUP 4.33 CONTEXT-AWARE PLAN / SETUP 4.34 IMPACT / SETUP 4.35 DEPENDENCY-AWARE CHANGE PLAN / SETUP 4.36 CHANGE-IMPACT VERIFICATION\n\n"
            f"{self.state.plan.summary() if self.state.plan else 'No plan available.'}\n\n"
            "Use this plan as guidance. Do not invent tools or skip the existing verification rules. "
            "The plan is advisory; actual tool results and the original user task have priority."
        )

        self.messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": user_input,
            },
            {
                "role": "system",
                "content": plan_text,
            },
        ]

        add_message(self.conversation_id, "user", user_input)
        _persist_agent_state(self)

    def continue_task(self, user_input):
        """Continue the existing task after Aziz asked a question."""

        question = self.pending_question or "the previous clarification question"

        self.waiting_for_user = False
        self.pending_question = None
        update_conversation(
            self.conversation_id,
            status="active",
            pending_question=None,
        )

        continuation_message = (
            "USER CLARIFICATION RESPONSE\n\n"
                    f"Aziz previously asked: {question}\n\n"
                    f"The user's answer is: {user_input}\n\n"
                    "IMPORTANT: This is a continuation of the SAME ORIGINAL TASK.\n"
                    "Do not start a new task.\n"
                    "Do not ask the same question again.\n"
                    "Treat the user's answer as the answer to the previous question.\n"
                    "If the answer is the requested file content, use it EXACTLY as provided.\n"
                    "Continue the ORIGINAL USER TASK now.\n"
                    "Use the appropriate tool and verify the result before final_answer."
        )

        self.messages.append({
            "role": "user",
            "content": continuation_message,
        })
        add_message(self.conversation_id, "user", continuation_message)
        _persist_agent_state(self)


    def continue_resumed_task(self, user_input):
        """Continue a conversation restored with /resume."""
        if not self.conversation_id or not self.original_task:
            return False

        continuation = (
            "CONTINUE RESTORED CONVERSATION\n\n"
            f"ORIGINAL TASK:\n{self.original_task}\n\n"
            f"USER'S NEW INSTRUCTION:\n{user_input}\n\n"
            "IMPORTANT: Continue the restored conversation. "
            "Do not start an unrelated new task."
        )

        self.messages.append({
            "role": "user",
            "content": continuation,
        })

        # Persist the actual user instruction as part of this conversation.
        add_message(
            self.conversation_id,
            "user",
            user_input,
        )

        update_conversation(
            self.conversation_id,
            status="active",
            pending_question=None,
        )

        self.waiting_for_user = False
        self.pending_question = None
        _persist_agent_state(self)
        return True


    def recover_last_active(self):
        """Restore the most recently updated active conversation.

        Returns (ok, data/message). Completed conversations are never
        automatically reopened by this method.
        """
        try:
            active = recoverable_conversations(100)
        except Exception as e:
            return False, f"Error loading active conversations: {e}"

        if not active:
            return False, "No active conversation to recover."

        return self.resume_task(active[0]["id"])

    def resume_task(self, conversation_id):
        """Restore a saved conversation into this live AgentSession.

        Accepts either the full UUID or the short ID shown by /history.
        Restores task, transcript, and pending ask_user state.
        """
        requested_id = str(conversation_id or "").strip()
        if not requested_id:
            return False, "Conversation ID is required."

        try:
            data = resume_conversation(requested_id)

            # /history intentionally displays a short ID. Resolve it
            # against persisted conversations before declaring failure.
            if data is None and len(requested_id) < 36:
                matches = [
                    item for item in list_conversations(100)
                    if str(item.get("id", "")).lower().startswith(requested_id.lower())
                ]
                if len(matches) == 1:
                    requested_id = str(matches[0]["id"])
                    data = resume_conversation(requested_id)
                elif len(matches) > 1:
                    ids = ", ".join(str(item["id"])[:8] for item in matches[:10])
                    return False, (
                        f"Conversation ID '{conversation_id}' is ambiguous. "
                        f"Matching IDs: {ids}"
                    )
        except Exception as e:
            return False, f"Error loading conversation: {e}"

        if data is None:
            return False, f"Conversation not found: {conversation_id}"

        self.conversation_id = str(data.get("id") or requested_id)
        self.original_task = str(
            data.get("original_task") or data.get("task") or ""
        ).strip()
        self.pending_question = str(data.get("pending_question") or "").strip() or None
        self.waiting_for_user = bool(self.pending_question)
        self.resumed_conversation = True
        self.state = AgentState()

        # Setup 4.12: restore the persisted agent-state snapshot.
        _restore_agent_state(self, data)

        # Rebuild the model context from the persisted transcript.
        self.messages = [{
            "role": "system",
            "content": SYSTEM_PROMPT,
        }]

        restored = data.get("messages", [])
        if isinstance(restored, list):
            for message in restored:
                if not isinstance(message, dict):
                    continue
                role = message.get("role")
                content = message.get("content")
                if role in ("user", "assistant", "system") and content is not None:
                    self.messages.append({
                        "role": role,
                        "content": str(content),
                    })

        if not any(m.get("role") == "user" for m in self.messages):
            self.messages.append({
                "role": "user",
                "content": self.original_task,
            })

        # Normalize the restored lifecycle state. A pending question is
        # explicitly waiting; otherwise the resumed task is active.
        lifecycle = "waiting_for_user" if self.waiting_for_user else "active"
        try:
            set_conversation_status(
                self.conversation_id,
                lifecycle,
                pending_question=self.pending_question,
                agent_state=_safe_state_snapshot(self.state),
            )
        except Exception:
            pass

        return True, data


# ============================================================
# RUN AGENT
# ============================================================

def run_agent(agent_session):
    """
    Run Aziz AI on the current AgentSession.

    The AgentSession is the single source of truth for:
    - conversation messages
    - original task
    - agent state
    - ask_user continuation state
    """

    if not isinstance(agent_session, AgentSession):
        print("\nAziz: Invalid agent session.")
        return

    messages = agent_session.messages
    original_task = agent_session.original_task
    state = agent_session.state

    # Setup 4.30: initialize a plan for legacy/resumed sessions that do not
    # already contain one. Persisted plans are restored by AgentSession.
    if state.plan is None and original_task:
        agent_session.task_context = build_task_context(original_task, WORKSPACE_DIR, PROJECTS_DIR)
        state.plan = agent_session.decomposer.decompose(original_task, context=agent_session.task_context)
        next_step = state.plan.next_step()
        state.current_plan_step = next_step.id if next_step else None
        _persist_agent_state(agent_session)

    for step in range(1, MAX_STEPS + 1):

        state.step = step

        try:
            set_conversation_status(
                agent_session.conversation_id,
                "running",
                pending_question=None,
                agent_state=_safe_state_snapshot(agent_session.state),
            )
        except Exception:
            pass

        print(f"\n[Agent step {step}]")
        print(f"[State] {state.status()}")

        # ====================================================
        # ASK MODEL
        # ====================================================

        try:
            model_response = ask_model(messages)

        except Exception as e:
            print("\nERROR communicating with LM Studio:")
            print(e)

            agent_session.waiting_for_user = False
            try:
                set_conversation_status(agent_session.conversation_id, "active", agent_state=_safe_state_snapshot(agent_session.state))
            except Exception:
                pass
            return

        if not model_response:
            print("\nAziz: Empty model response.")

            agent_session.waiting_for_user = False
            return

        print("Qwen:")
        print(model_response)

        # ====================================================
        # PARSE
        # ====================================================

        tool_call = parse_tool_call(model_response)

        # ====================================================
        # NORMAL TEXT
        # ====================================================

        if tool_call is None:
            print("\nAziz:", model_response)

            agent_session.waiting_for_user = False
            try:
                set_conversation_status(agent_session.conversation_id, "active", agent_state=_safe_state_snapshot(agent_session.state))
            except Exception:
                pass
            return

        if not isinstance(tool_call, dict):
            print("\nAziz: Invalid model action.")
            return

        action = tool_call.get("action")

        arguments = tool_call.get(
            "arguments",
            {},
        )

        if not action:
            print("\nAziz: Model returned no action.")
            return

        action = str(action).strip()

        # ====================================================
        # FINAL ANSWER
        # ====================================================

        if action == "final_answer":

            # Setup 4.36: do not allow a modified task to claim completion
            # while required impact paths remain unobserved.
            impact_verification = getattr(state, "impact_verification", None)
            if getattr(state, "verification_requested", False) and impact_verification is not None and impact_verification.status in {"pending", "partial"}:
                missing = ", ".join(impact_verification.missing_paths[:12]) or "the required verification scope"
                messages.append({
                    "role": "user",
                    "content": (
                        "CHANGE-IMPACT VERIFICATION BLOCKED FINAL ANSWER.\n\n"
                        f"Still unverified: {missing}.\n"
                        "Read/test the required affected resources and inspect the actual results before using final_answer."
                    ),
                })
                print("\nAziz: Change-impact verification is incomplete; continuing verification.")
                state.phase = "VERIFY"
                continue

            # Setup 4.37: final completion must have concrete evidence for
            # every required post-change verification path.
            evidence = getattr(state, "completion_evidence", None)
            if evidence is None:
                evidence = CompletionEvidenceLedger([], "not_required", [])
                state.completion_evidence = evidence
            evidence.evaluate(impact_verification, getattr(state, "verification_requested", False), getattr(state, "change_epoch", 0), getattr(state, "modified_generations", {}))
            # Setup 4.56: derive the final answer before sealing so the
            # completion attestation is bound to the exact message returned.
            answer = ""
            if isinstance(arguments, dict):
                answer = str(arguments.get("answer", "")).strip()
            if not answer:
                answer = "The task has been completed and verified."

            # Setup 4.45: create and immediately validate a final completion seal.
            if getattr(state, "verification_requested", False) and evidence.status == "sufficient" and impact_verification is not None and impact_verification.status == "complete":
                plan_revision = getattr(getattr(state, "plan", None), "revision", 0)
                task_identity = build_task_identity(
                    getattr(self, "original_task", ""),
                    getattr(self, "conversation_id", ""),
                    plan_revision,
                )
                state.completion_attestation = create_attestation(
                    evidence,
                    impact_verification,
                    getattr(state, "change_epoch", 0),
                    getattr(state, "modified_generations", {}),
                    task_identity,
                    get_tool_schema(),
                    build_runtime_identity(model_gateway),
                    getattr(self, "task_context", None),
                    getattr(state, "plan", None),
                    getattr(state, "evidence_recovery", None),
                    build_policy_identity(MAX_STEPS),
                    getattr(state, "successful_actions", []),
                    getattr(state, "failed_actions", []),
                    getattr(getattr(getattr(state, "plan", None), "context", None), "change_plan", None),
                    answer,
                )
            else:
                state.completion_attestation = CompletionAttestation()
            if getattr(state, "verification_requested", False) and (
                evidence.status != "sufficient"
                or not state.completion_attestation.valid(
                    evidence,
                    impact_verification,
                    getattr(state, "change_epoch", 0),
                    getattr(state, "modified_generations", {}),
                    build_task_identity(
                        getattr(self, "original_task", ""),
                        getattr(self, "conversation_id", ""),
                        getattr(getattr(state, "plan", None), "revision", 0),
                    ),
                    get_tool_schema(),
                    build_runtime_identity(model_gateway),
                    getattr(self, "task_context", None),
                    getattr(state, "plan", None),
                    getattr(state, "evidence_recovery", None),
                    build_policy_identity(MAX_STEPS),
                    getattr(state, "successful_actions", []),
                    getattr(state, "failed_actions", []),
                    getattr(getattr(getattr(state, "plan", None), "context", None), "change_plan", None),
                    answer,
                )
            ):
                missing = ", ".join(evidence.missing_requirements[:8]) or "required execution evidence"
                messages.append({
                    "role": "user",
                    "content": (
                        "EVIDENCE-BASED COMPLETION BLOCKED FINAL ANSWER.\n\n"
                        f"Missing evidence: {missing}.\n"
                        "Use successful tool results and verify the affected resources before claiming completion."
                    ),
                })
                print("\nAziz: Completion evidence is insufficient; continuing verification.")
                state.phase = "VERIFY"
                continue

            # Setup 4.57: consume the validated completion attestation exactly once.
            # The consumed marker is sealed and persisted before the final answer is
            # emitted, so a restart cannot replay the same completion receipt.
            if getattr(state, "verification_requested", False):
                if not state.completion_attestation.consume():
                    messages.append({
                        "role": "user",
                        "content": (
                            "COMPLETION ATTESTATION REPLAY BLOCKED.\n\n"
                            "The completion receipt has already been consumed. "
                            "Continue with a fresh verified completion."
                        ),
                    })
                    print("\nAziz: Completion attestation replay blocked; continuing verification.")
                    state.phase = "VERIFY"
                    continue

                # Setup 4.58: issue a persistent receipt only after the consumed
                # attestation has been successfully sealed and persisted. The receipt
                # stores only cryptographic identities/digests, never raw tool output.
                task_digest = getattr(state.completion_attestation, "task_digest", "")
                answer_digest = getattr(state.completion_attestation, "answer_digest", "")
                state.completion_receipt = issue_completion_receipt(
                    state.completion_attestation,
                    getattr(self, "conversation_id", ""),
                    task_digest,
                    answer_digest,
                    getattr(state, "change_epoch", 0),
                )
                if not state.completion_receipt.valid(
                    state.completion_attestation,
                    getattr(self, "conversation_id", ""),
                    task_digest,
                    answer_digest,
                    getattr(state, "change_epoch", 0),
                ):
                    messages.append({
                        "role": "user",
                        "content": "COMPLETION RECEIPT VALIDATION BLOCKED FINAL ANSWER.\n\nThe completion receipt could not be validated after issuance. Continue verification.",
                    })
                    print("\nAziz: Completion receipt validation failed; continuing verification.")
                    state.phase = "VERIFY"
                    continue

                # Setup 4.59: create and validate a persistent finalization lock.
                # The lock is cryptographically bound to the already-consumed receipt,
                # conversation, task, answer, and change epoch.
                state.completion_finalization = issue_completion_finalization(
                    state.completion_receipt,
                    getattr(self, "conversation_id", ""),
                    task_digest,
                    answer_digest,
                    getattr(state, "change_epoch", 0),
                )
                if not state.completion_finalization.valid(
                    state.completion_receipt,
                    getattr(self, "conversation_id", ""),
                    task_digest,
                    answer_digest,
                    getattr(state, "change_epoch", 0),
                ):
                    messages.append({
                        "role": "user",
                        "content": "COMPLETION FINALIZATION LOCK BLOCKED FINAL ANSWER.\n\nThe completion finalization record could not be validated. Continue verification.",
                    })
                    print("\nAziz: Completion finalization validation failed; continuing verification.")
                    state.phase = "VERIFY"
                    continue

                # Setup 4.60: append an immutable, bounded audit record only after
                # the receipt and finalization lock both validate. The audit trail
                # stores safe identities/digests and a cryptographic hash chain, not
                # raw tool output. Duplicate finalizations are rejected.
                audit_entry = state.completion_audit.append_finalization(
                    state.completion_finalization,
                    state.completion_receipt,
                    getattr(self, "conversation_id", ""),
                    task_digest,
                    answer_digest,
                    getattr(state, "change_epoch", 0),
                )
                if audit_entry is None or not state.completion_audit.valid_latest(
                    state.completion_finalization,
                    state.completion_receipt,
                    getattr(self, "conversation_id", ""),
                    task_digest,
                    answer_digest,
                    getattr(state, "change_epoch", 0),
                ):
                    messages.append({
                        "role": "user",
                        "content": "COMPLETION AUDIT RECORD BLOCKED FINAL ANSWER.\n\nThe finalized completion could not be recorded and verified in the audit trail. Continue verification.",
                    })
                    print("\nAziz: Completion audit validation failed; continuing verification.")
                    state.phase = "VERIFY"
                    continue

                # Setup 4.61: cryptographically seal the exact audit-trail state that
                # authorized this final answer. Any later audit mutation, context change,
                # or trail tampering invalidates the seal.
                state.completion_audit_seal = issue_completion_audit_seal(
                    state.completion_audit,
                    getattr(self, "conversation_id", ""),
                    task_digest,
                    answer_digest,
                    getattr(state, "change_epoch", 0),
                )
                if not state.completion_audit_seal.valid(
                    state.completion_audit,
                    getattr(self, "conversation_id", ""),
                    task_digest,
                    answer_digest,
                    getattr(state, "change_epoch", 0),
                ):
                    messages.append({
                        "role": "user",
                        "content": "COMPLETION AUDIT SEAL BLOCKED FINAL ANSWER.\n\nThe verified audit trail could not be sealed for finalization. Continue verification.",
                    })
                    print("\nAziz: Completion audit seal validation failed; continuing verification.")
                    state.phase = "VERIFY"
                    continue

                # Setup 4.62: create one immutable proof bundle binding every
                # completion artifact that authorized the final answer.
                state.completion_proof = issue_completion_proof(
                    state.completion_attestation,
                    state.completion_receipt,
                    state.completion_finalization,
                    state.completion_audit,
                    state.completion_audit_seal,
                    getattr(self, "conversation_id", ""),
                    task_digest,
                    answer_digest,
                    getattr(state, "change_epoch", 0),
                )
                if not state.completion_proof.valid(
                    state.completion_attestation,
                    state.completion_receipt,
                    state.completion_finalization,
                    state.completion_audit,
                    state.completion_audit_seal,
                    getattr(self, "conversation_id", ""),
                    task_digest,
                    answer_digest,
                    getattr(state, "change_epoch", 0),
                ):
                    messages.append({
                        "role": "user",
                        "content": "COMPLETION PROOF BLOCKED FINAL ANSWER.\n\nThe complete completion chain could not be proven as one consistent sealed record. Continue verification.",
                    })
                    print("\nAziz: Completion proof validation failed; continuing verification.")
                    state.phase = "VERIFY"
                    continue

                # Setup 4.63: create a terminal commitment after the complete proof
                # validates. This adds one more cryptographic boundary between the
                # verified completion chain and the answer that is actually emitted.
                state.completion_proof_commitment = issue_completion_proof_commitment(
                    state.completion_proof,
                    state.completion_audit_seal,
                    state.completion_finalization,
                    state.completion_receipt,
                    getattr(self, "conversation_id", ""),
                    task_digest,
                    answer_digest,
                    getattr(state, "change_epoch", 0),
                )
                if not state.completion_proof_commitment.valid(
                    state.completion_proof,
                    state.completion_attestation,
                    state.completion_receipt,
                    state.completion_finalization,
                    state.completion_audit,
                    state.completion_audit_seal,
                    getattr(self, "conversation_id", ""),
                    task_digest,
                    answer_digest,
                    getattr(state, "change_epoch", 0),
                ):
                    messages.append({
                        "role": "user",
                        "content": "COMPLETION PROOF COMMITMENT BLOCKED FINAL ANSWER.\n\nThe terminal completion commitment could not be validated. Continue verification.",
                    })
                    print("\nAziz: Completion proof commitment validation failed; continuing verification.")
                    state.phase = "VERIFY"
                    continue

                # Setup 4.64: create a one-time release token only after the
                # terminal proof commitment has validated. Consuming this token is
                # the final authorization immediately before the answer is emitted.
                state.completion_release = issue_completion_release(
                    state.completion_proof_commitment,
                    state.completion_proof,
                    getattr(self, "conversation_id", ""),
                    task_digest,
                    answer_digest,
                    getattr(state, "change_epoch", 0),
                )
                if not state.completion_release.valid(
                    state.completion_proof_commitment,
                    state.completion_proof,
                    state.completion_attestation,
                    state.completion_receipt,
                    state.completion_finalization,
                    state.completion_audit,
                    state.completion_audit_seal,
                    getattr(self, "conversation_id", ""),
                    task_digest,
                    answer_digest,
                    getattr(state, "change_epoch", 0),
                ):
                    messages.append({
                        "role": "user",
                        "content": "COMPLETION RELEASE BLOCKED FINAL ANSWER.\n\nThe final-answer release token could not be validated. Continue verification.",
                    })
                    print("\nAziz: Completion release validation failed; continuing verification.")
                    state.phase = "VERIFY"
                    continue

                if not state.completion_release.consume():
                    messages.append({
                        "role": "user",
                        "content": "COMPLETION RELEASE BLOCKED FINAL ANSWER.\n\nThe final-answer release token could not be consumed exactly once. Continue verification.",
                    })
                    print("\nAziz: Completion release consumption failed; continuing verification.")
                    state.phase = "VERIFY"
                    continue

                if not state.completion_release.consumed_valid(
                    state.completion_proof_commitment,
                    state.completion_proof,
                    state.completion_attestation,
                    state.completion_receipt,
                    state.completion_finalization,
                    state.completion_audit,
                    state.completion_audit_seal,
                    getattr(self, "conversation_id", ""),
                    task_digest,
                    answer_digest,
                    getattr(state, "change_epoch", 0),
                ):
                    messages.append({
                        "role": "user",
                        "content": "COMPLETION RELEASE BLOCKED FINAL ANSWER.\n\nThe consumed release token failed final integrity validation. Continue verification.",
                    })
                    print("\nAziz: Consumed completion release is invalid; continuing verification.")
                    state.phase = "VERIFY"
                    continue

                # Setup 4.65: authorize terminal answer dispatch only after the one-time
                # release has been consumed and its full completion chain remains valid.
                state.completion_dispatch = issue_completion_dispatch(
                    state.completion_release,
                    state.completion_proof_commitment,
                    state.completion_proof,
                    getattr(self, "conversation_id", ""),
                    task_digest,
                    answer_digest,
                    getattr(state, "change_epoch", 0),
                )
                if not state.completion_dispatch.valid(
                    state.completion_release,
                    state.completion_proof_commitment,
                    state.completion_proof,
                    state.completion_attestation,
                    state.completion_receipt,
                    state.completion_finalization,
                    state.completion_audit,
                    state.completion_audit_seal,
                    getattr(self, "conversation_id", ""),
                    task_digest,
                    answer_digest,
                    getattr(state, "change_epoch", 0),
                ):
                    messages.append({
                        "role": "user",
                        "content": "COMPLETION DISPATCH BLOCKED FINAL ANSWER.\n\nTerminal answer dispatch authorization could not be validated. Continue verification.",
                    })
                    print("\nAziz: Terminal dispatch authorization failed; continuing verification.")
                    state.phase = "VERIFY"
                    continue

                if not state.completion_dispatch.consume():
                    messages.append({
                        "role": "user",
                        "content": "COMPLETION DISPATCH BLOCKED FINAL ANSWER.\n\nTerminal answer dispatch authorization could not be consumed exactly once. Continue verification.",
                    })
                    print("\nAziz: Terminal dispatch authorization consumption failed; continuing verification.")
                    state.phase = "VERIFY"
                    continue

                if not state.completion_dispatch.consumed_valid(
                    state.completion_release,
                    state.completion_proof_commitment,
                    state.completion_proof,
                    state.completion_attestation,
                    state.completion_receipt,
                    state.completion_finalization,
                    state.completion_audit,
                    state.completion_audit_seal,
                    getattr(self, "conversation_id", ""),
                    task_digest,
                    answer_digest,
                    getattr(state, "change_epoch", 0),
                ):
                    messages.append({
                        "role": "user",
                        "content": "COMPLETION DISPATCH BLOCKED FINAL ANSWER.\n\nConsumed terminal dispatch authorization failed final integrity validation. Continue verification.",
                    })
                    print("\nAziz: Consumed terminal dispatch authorization is invalid; continuing verification.")
                    state.phase = "VERIFY"
                    continue

                # Setup 4.66: prepare a durable two-phase emission journal.
                # Phase 1 is persisted before any answer bytes are emitted.
                state.completion_emission = issue_completion_emission(
                    state.completion_dispatch,
                    state.completion_release,
                    state.completion_proof_commitment,
                    state.completion_proof,
                    getattr(self, "conversation_id", ""),
                    task_digest,
                    answer_digest,
                    getattr(state, "change_epoch", 0),
                )
                if not state.completion_emission.valid_prepared(
                    state.completion_dispatch,
                    state.completion_release,
                    state.completion_proof_commitment,
                    state.completion_proof,
                    state.completion_attestation,
                    state.completion_receipt,
                    state.completion_finalization,
                    state.completion_audit,
                    state.completion_audit_seal,
                    getattr(self, "conversation_id", ""),
                    task_digest,
                    answer_digest,
                    getattr(state, "change_epoch", 0),
                ):
                    messages.append({
                        "role": "user",
                        "content": "COMPLETION EMISSION BLOCKED FINAL ANSWER.\n\nThe durable terminal emission journal could not be prepared and validated. Continue verification.",
                    })
                    print("\nAziz: Terminal emission journal preparation failed; continuing verification.")
                    state.phase = "VERIFY"
                    continue

                _persist_agent_state(agent_session)

            print("\nAziz:", answer)

            # Setup 4.66 phase 2: record that the already-authorized answer was emitted.
            # This marker is independently sealed and persisted after the actual output.
            if getattr(state, "completion_emission", None) is None or not state.completion_emission.mark_emitted():
                print("\nAziz: WARNING: terminal emission marker could not be committed after answer emission.")
                state.phase = "VERIFY"
                continue
            if not state.completion_emission.valid_emitted(
                state.completion_dispatch,
                state.completion_release,
                state.completion_proof_commitment,
                state.completion_proof,
                state.completion_attestation,
                state.completion_receipt,
                state.completion_finalization,
                state.completion_audit,
                state.completion_audit_seal,
                getattr(self, "conversation_id", ""),
                task_digest,
                answer_digest,
                getattr(state, "change_epoch", 0),
            ):
                print("\nAziz: WARNING: terminal emission marker failed post-output integrity validation.")
                state.phase = "VERIFY"
                continue

            # Setup 4.67: append a durable audit record for the completed terminal emission.
            # The history survives later successful actions and provides bounded replay/audit visibility.
            state.completion_emission_audit.append_emission(
                state.completion_emission,
                state.completion_dispatch,
                state.completion_release,
                state.completion_proof_commitment,
                state.completion_proof,
                getattr(self, "conversation_id", ""),
                task_digest,
                answer_digest,
                getattr(state, "change_epoch", 0),
            )
            if not state.completion_emission_audit.valid_latest(
                state.completion_emission,
                state.completion_dispatch,
                state.completion_release,
                state.completion_proof_commitment,
                state.completion_proof,
                getattr(self, "conversation_id", ""),
                task_digest,
                answer_digest,
                getattr(state, "change_epoch", 0),
            ):
                print("\nAziz: WARNING: terminal emission audit record failed integrity validation.")
                state.phase = "VERIFY"
                continue

            # Setup 4.68: reconcile the persisted two-phase emission journal with
            # the append-only audit history. This is a recovery record, not another
            # authorization token. It makes crash boundaries explicit and durable.
            latest_emission_audit = state.completion_emission_audit.latest()
            state.completion_emission_recovery = reconcile_emitted(
                state.completion_emission,
                latest_emission_audit,
                state.completion_emission_audit,
                getattr(self, "conversation_id", ""),
                task_digest,
                answer_digest,
                getattr(state, "change_epoch", 0),
            )
            if not state.completion_emission_recovery.valid() or state.completion_emission_recovery.status != "reconciled":
                print("\nAziz: WARNING: terminal emission recovery reconciliation failed.")
                state.phase = "VERIFY"
                continue

            # Setup 4.69: final read-only preflight across the entire terminal chain.
            # This does not issue or consume any token; it only blocks emission when
            # existing terminal records disagree.
            state.completion_terminal_consistency = build_terminal_consistency(
                state.completion_dispatch,
                state.completion_release,
                state.completion_proof_commitment,
                state.completion_proof,
                state.completion_attestation,
                state.completion_receipt,
                state.completion_finalization,
                state.completion_audit,
                state.completion_audit_seal,
                state.completion_emission,
                state.completion_emission_audit,
                state.completion_emission_recovery,
                getattr(self, "conversation_id", ""),
                task_digest,
                answer_digest,
                getattr(state, "change_epoch", 0),
            )
            if not state.completion_terminal_consistency.is_consistent():
                print("\nAziz: WARNING: terminal consistency preflight failed.")
                state.phase = "VERIFY"
                continue

            # Setup 4.70: resolve the reconciled recovery state into an explicit
            # terminal decision. Pending/orphaned/invalid states never finalize.
            state.completion_emission_resolution = issue_resolution(
                state.completion_emission_recovery,
                getattr(self, "conversation_id", ""),
                task_digest,
                answer_digest,
                getattr(state, "change_epoch", 0),
            )
            if (
                not state.completion_emission_resolution.valid()
                or state.completion_emission_resolution.status != "ready"
                or state.completion_emission_resolution.blocks_finalization()
            ):
                if state.completion_emission_resolution.requires_fresh_completion():
                    print("\nAziz: WARNING: terminal emission recovery is quarantined; fresh completion required.")
                else:
                    print("\nAziz: WARNING: terminal emission resolution requires verification.")
                state.phase = "VERIFY"
                continue
            _persist_agent_state(agent_session)

            agent_session.waiting_for_user = False
            add_message(agent_session.conversation_id, "assistant", model_response)
            update_conversation(
                agent_session.conversation_id,
                status="completed",
                pending_question=None,
                agent_state=_safe_state_snapshot(agent_session.state),
            )

            return

        # ====================================================
        # ASK USER
        # ====================================================

        if action == "ask_user":

            question = ""

            if isinstance(arguments, dict):
                question = str(
                    arguments.get(
                        "question",
                        "",
                    )
                ).strip()

            if not question:
                question = (
                    "I need clarification "
                    "before continuing."
                )

            print("\nAziz:", question)

            messages.append(
                {
                    "role": "assistant",
                    "content": model_response,
                }
            )

            # Pause this run but keep the complete conversation alive.
            # The next terminal input will be routed to continue_task().
            agent_session.pending_question = question
            agent_session.waiting_for_user = True

            # Persist the pause so the clarification survives a restart.
            add_message(
                agent_session.conversation_id,
                "assistant",
                model_response,
            )
            set_conversation_status(
                agent_session.conversation_id,
                "waiting_for_user",
                pending_question=question,
                agent_state=_safe_state_snapshot(agent_session.state),
            )

            return

        # ====================================================
        # VALIDATE
        # ====================================================

        valid, error = validate_tool_arguments(
            action,
            arguments,
        )

        if not valid:

            print("[Tool validation error]")
            print(error)

            messages.append(
                {
                    "role": "assistant",
                    "content": model_response,
                }
            )

            messages.append(
                {
                    "role": "user",
                    "content": (
                        "TOOL CALL REJECTED.\n\n"
                        f"Reason:\n{error}\n\n"
                        "Correct the tool call.\n"
                        "Use ONLY the exact argument names "
                        "from the TOOL CONTRACT.\n"
                        "Continue the ORIGINAL task."
                    ),
                }
            )

            state.phase = "REPAIR"

            continue

        # ====================================================
        # REPEAT DETECTION
        # ====================================================

        signature = action_signature(
            action,
            arguments,
        )

        if (
            signature in state.successful_actions
            and action not in READ_ONLY_ACTIONS
        ):

            print(
                "[Agent] Repeated non-read action blocked."
            )

            messages.append(
                {
                    "role": "assistant",
                    "content": model_response,
                }
            )

            messages.append(
                {
                    "role": "user",
                    "content": (
                        "This exact action already succeeded.\n\n"
                        "Do NOT repeat it.\n"
                        "Move to the next phase of the ORIGINAL task.\n"
                        "If a modification was made, verify it.\n"
                        "If verification is complete, use final_answer."
                    ),
                }
            )

            continue

        # ====================================================
        # DISPLAY
        # ====================================================

        print(f"[Tool] {action}")
        print(f"[Arguments] {arguments}")

        # ====================================================
        # EXECUTE
        # ====================================================

        result = execute_tool(
            action,
            arguments,
        )

        add_message(agent_session.conversation_id, "assistant", model_response)
        add_action(
            agent_session.conversation_id,
            action,
            arguments,
            result,
            not is_error_result(result),
        )

        print("[Tool result]")
        print(result)

        # ====================================================
        # UPDATE STATE
        # ====================================================

        state.record_action(
            action,
            arguments,
            result,
        )

        # Setup 4.12: persist the latest agent state after every action.
        _persist_agent_state(agent_session)

        # ====================================================
        # FEEDBACK
        # ====================================================

        messages.append(
            {
                "role": "assistant",
                "content": model_response,
            }
        )

        if is_error_result(result):

            next_instruction = (
                "TOOL FAILED.\n\n"
                "Inspect the actual error.\n"
                "Do not claim success.\n"
                "Do not repeat the failed action.\n"
                "Repair the actual problem if possible.\n"
                "If clarification is required, use ask_user."
            )

        elif action in MODIFYING_ACTIONS:

            next_instruction = (
                "MODIFICATION SUCCEEDED.\n\n"
                "Enter VERIFICATION phase.\n"
                "Read the modified resource again.\n"
                "Verify the user's exact requirements.\n"
                "If verification fails, repair it.\n"
                "If verification succeeds, use final_answer."
            )

        elif action in READ_ONLY_ACTIONS:

            next_instruction = (
                "OBSERVATION SUCCEEDED.\n\n"
                "Inspect the actual returned content.\n"
                "Determine whether the ORIGINAL task is already "
                "satisfied.\n"
                "If a modification is required, perform the smallest "
                "necessary modification.\n"
                "If modification was already made, verify it.\n"
                "Do not modify something that is already correct."
            )

        else:

            next_instruction = (
                "ACTION SUCCEEDED.\n\n"
                "Inspect the result.\n"
                "Continue the ORIGINAL task.\n"
                "Verify the result when required.\n"
                "Use final_answer only when everything is verified."
            )

        feedback_message = (
            "TOOL RESULT:\n"
            f"{result}\n\n"
            "ORIGINAL USER TASK:\n"
            f"{original_task}\n\n"
            "CURRENT AGENT STATE:\n"
            f"{state.status()}\n\n"
            "EXECUTION PLAN:\n"
            f"{state.plan.summary() if state.plan else 'No plan available.'}\n"
            f"CURRENT PLAN STEP: {state.current_plan_step or 'none'}\n\n"
            f"DEPENDENCY-AWARE CHANGE PLAN: {getattr(getattr(state, 'plan', None), 'context', None).change_plan if getattr(getattr(state, 'plan', None), 'context', None) and getattr(getattr(state, 'plan', None).context, 'change_plan', None) else 'No change plan available.'}\n\n"
            f"CHANGE-IMPACT VERIFICATION: {state.impact_verification.summary() if getattr(state, 'impact_verification', None) else 'No post-change verification checklist available.'}\n"
            f"VERIFICATION REQUIRED PATHS: {', '.join(getattr(state.impact_verification, 'required_paths', [])) if getattr(state, 'impact_verification', None) else 'none'}\n"
            f"VERIFICATION COMPLETED PATHS: {', '.join(getattr(state.impact_verification, 'completed_paths', [])) if getattr(state, 'impact_verification', None) else 'none'}\n\n"
            f"{next_instruction}\n\n"
            "Remember: use EXACT tool argument names "
            "from the TOOL CONTRACT."
        )

        messages.append({
            "role": "user",
            "content": feedback_message,
        })
        add_message(
            agent_session.conversation_id,
            "user",
            feedback_message,
        )

    # ========================================================
    # MAX STEPS
    # ========================================================

    print(
        "\nAziz: I reached the maximum number of agent "
        "steps before completing verification."
    )

# ============================================================
# TRUST
# ============================================================

def request_trust():

    if os.path.exists(
        TRUST_FLAG_FILE
    ):

        return True

    print("=" * 50)

    print(
        "  Aziz can read/write files and run commands inside:"
    )

    print(
        f"    {WORKSPACE_DIR}"
    )

    print(
        f"    {PROJECTS_DIR}"
    )

    print(
        "  It will not touch anything outside these folders."
    )

    print("=" * 50)

    print()

    print("  1. Yes, proceed")
    print("  2. No, exit")

    print()

    choice = input(
        "Choose an option (1-2): "
    ).strip()

    if choice != "1":

        print(
            "Exiting without granting trust."
        )

        return False

    try:

        with open(
            TRUST_FLAG_FILE,
            "w",
            encoding="utf-8",
        ) as f:

            f.write(
                "trusted\n"
            )

    except Exception:

        pass

    return True


# ============================================================
# SLASH COMMANDS
# ============================================================

SLASH_COMMANDS = {
    "/help": "Show this help message.",
    "/status": "Show current model, workspace, and project directories.",
    "/projects": "List existing projects.",
    "/history": "Show recent persistent Aziz tasks.",
    "/resume <id>": "Resume a saved conversation by ID.",
    "/recover": "Recover the most recently active conversation.",
    "/lifecycle": "Show recoverable conversation lifecycle states.",
    "/new": "Start a new task/conversation.",
    "/exit": "Quit Aziz.",
}


def handle_slash_command(command, session=None):

    command = command.strip().lower()

    if command == "/help":

        print()

        for name, desc in SLASH_COMMANDS.items():

            print(
                f"  {name:<10} {desc}"
            )

        print()

        return True

    if command == "/status":

        print()

        print(
            f"  Model: {model_gateway.model}"
        )

        print(
            "  Backend:    LM Studio"
        )

        print(
            f"  Workspace:  {WORKSPACE_DIR}"
        )

        print(
            f"  Projects:   {PROJECTS_DIR}"
        )

        print(
            f"  Max steps:  {MAX_STEPS}"
        )

        print()

        return True

    if command == "/projects":

        print()

        try:

            print(
                list_projects()
            )

        except Exception as e:

            print(
                f"ERROR listing projects: {e}"
            )

        print()

        return True

    if command == "/history":

        print()
        try:
            history = list_conversations(20)
            if not history:
                print("  No saved conversations yet.")
            else:
                for item in history:
                    task = item["task"].replace("\n", " ")
                    if len(task) > 90:
                        task = task[:87] + "..."
                    print(f"  [{item['status']}] {item['id'][:8]}  {task}")
        except Exception as e:
            print(f"ERROR reading history: {e}")
        print()
        return True

    if command == "/lifecycle":
        print()
        try:
            rows = recoverable_conversations(20)
            if not rows:
                print("  No recoverable conversations.")
            else:
                for item in rows:
                    print(f"  [{item['status']}] {item['id'][:8]}  {item['task'].replace(chr(10), ' ')}")
        except Exception as e:
            print(f"ERROR reading lifecycle: {e}")
        print()
        return True

    if command == "/recover":
        if session is None:
            print("\nERROR: No active agent session.\n")
            return True

        ok, result = session.recover_last_active()
        if not ok:
            print(f"\nERROR: {result}\n")
            return True

        print(f"\n[Recovered conversation] {session.conversation_id}")
        print(f"Task: {session.original_task}")
        if session.pending_question:
            print(f"Pending question: {session.pending_question}")
            print("Enter your answer to continue.")
        else:
            print("Conversation context restored. Enter your next instruction.")
        print()
        return True

    if command == "/new":
        if session is not None:
            session.__init__()
            print("\n[New conversation] Ready for a new task.\n")
        return True

    if command.startswith("/resume"):

        parts = command.split(maxsplit=1)
        if len(parts) != 2:
            print("\nUsage: /resume <conversation_id>\n")
            return True

        if session is None:
            print("\nERROR: No active agent session.\n")
            return True

        conversation_id = parts[1].strip()
        resume_result = session.resume_task(conversation_id)

        # resume_task historically returned both (ok, result), but some
        # Setup 4.12/4.13 builds returned only a boolean. Accept both forms
        # so /resume cannot crash with "cannot unpack non-iterable bool".
        if isinstance(resume_result, tuple):
            ok, result = resume_result
        else:
            ok = bool(resume_result)
            result = resume_result

        if not ok:
            print(f"\nERROR: {result}\n")
            return True

        print(f"\n[Resumed conversation] {session.conversation_id}")
        print(f"Task: {session.original_task}")
        if session.pending_question:
            print(f"Pending question: {session.pending_question}")
        else:
            print("Conversation context restored. Enter your next instruction.")
        print()
        return True

    if command in (
        "/exit",
        "exit",
        "quit",
    ):

        return True

    return False


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 50)

    print(
        "          AZIZ AI LOCAL AGENT V2"
    )

    print("=" * 50)

    print(
        f"Model: {model_gateway.model}"
    )

    print(
        "Backend: LM Studio"
    )

    print(
        "Mode: Autonomous Observe → Act → Verify → Repair"
    )

    print(
        f"Max steps: {MAX_STEPS}"
    )

    print(
        "Type '/help' for commands, 'exit' to quit."
    )

    print()

    if not request_trust():

        return

    session = AgentSession()

    while True:

        try:

            user_input = input(
                "You: "
            ).strip()

        except KeyboardInterrupt:

            print(
                "\nExiting."
            )

            break

        except EOFError:

            print(
                "\nExiting."
            )

            break

        if not user_input:

            continue

        if user_input.lower() in (
            "/exit",
            "exit",
            "quit",
        ):

            break

        if user_input.startswith("/"):

            if not handle_slash_command(
                user_input,
                session,
            ):

                print(
                    f"Unknown command: {user_input}"
                )

            continue

        # ====================================================
        # NEW TASK / ASK_USER CONTINUATION / RESUMED CONVERSATION
        # ====================================================

        if session.waiting_for_user:
            session.continue_task(
                user_input
            )

        elif session.resumed_conversation:
            # After /resume, normal input continues the saved conversation.
            session.continue_resumed_task(
                user_input
            )

        else:
            session.start_task(
                user_input
            )

        # IMPORTANT:
        # Pass the actual AgentSession, not the raw user_input.
        run_agent(
            session
        )


if __name__ == "__main__":

    main()