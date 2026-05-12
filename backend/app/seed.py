from .models import Question


TRACK_PREFIX = {
    "AI Engineer": "AIE",
    "AI Solution Architect": "AISA",
}

SECTION_DIFFICULTY = {
    "business": 1,
    "functional": 2,
    "technical": 3,
}

QUESTION_BANK = {
    "AI Engineer": {
        "business": [
            (
                "A product team wants to add generative AI to reduce support handling time. What is the strongest first decision?",
                "Define measurable outcomes, risk boundaries, ownership, and a pilot tied to support workflow metrics.",
                [
                    "Select the model with the highest benchmark score and measure value after launch.",
                    "Build a broad assistant for every support topic so coverage is maximized early.",
                    "Let support agents experiment freely, then formalize governance if adoption grows.",
                ],
            ),
            (
                "A business sponsor asks for AI automation in a regulated process. What response best protects delivery value?",
                "Map value, controls, human review points, audit needs, and success measures before implementation.",
                [
                    "Automate the easiest steps first and add controls once the model is stable.",
                    "Require legal approval only at production release so the pilot can move faster.",
                    "Use generic productivity metrics because regulated workflows are hard to quantify.",
                ],
            ),
            (
                "Leadership wants to compare three AI use cases. Which ranking approach is strongest?",
                "Score each use case by business value, feasibility, risk, data readiness, and adoption effort.",
                [
                    "Prioritize the most visible executive request because sponsorship reduces delivery friction.",
                    "Prioritize the use case with the largest available dataset regardless of operational value.",
                    "Prioritize the lowest-risk proof of concept even if it has limited business impact.",
                ],
            ),
            (
                "A pilot is successful technically but has low user adoption. What should the engineer do next?",
                "Review workflow fit, change readiness, incentives, usability, and handoff design with users.",
                [
                    "Tune prompts and model settings before revisiting the operating workflow.",
                    "Move to production because technical success proves the solution is ready.",
                    "Add more dashboards so leaders can enforce use of the AI capability.",
                ],
            ),
            (
                "A team needs a business case for an AI coding assistant. What evidence is most credible?",
                "Baseline cycle time, defect rates, review quality, adoption patterns, and measured productivity change.",
                [
                    "Vendor ROI claims combined with developer sentiment after a short demo.",
                    "The number of generated code suggestions accepted by developers in isolation.",
                    "A general assumption that coding assistants improve throughput by a fixed percentage.",
                ],
            ),
            (
                "An AI feature may reduce manual review effort but also changes accountability. What is the best framing?",
                "Clarify decision rights, exception ownership, escalation rules, and measurable operating impact.",
                [
                    "Describe the feature as decision support and leave accountability unchanged by default.",
                    "Shift accountability to the model output because review effort is the target reduction.",
                    "Focus the business case on labor savings and leave ownership for training materials.",
                ],
            ),
            (
                "A stakeholder asks to launch an AI chatbot before the data is clean. What is the strongest answer?",
                "Launch only within validated content boundaries and track gaps, risk, and escalation quality.",
                [
                    "Launch broadly with a disclaimer because user feedback will identify content gaps.",
                    "Delay all AI work until every source system has been fully modernized.",
                    "Use a larger model to compensate for incomplete and inconsistent source content.",
                ],
            ),
            (
                "A team must decide whether an AI workflow is ready for scale. Which signal matters most?",
                "Stable business outcomes, safe exception handling, monitored quality, and clear operating ownership.",
                [
                    "A successful demo with a senior stakeholder and a backlog of requested enhancements.",
                    "A high offline accuracy score without measuring workflow behavior in production-like use.",
                    "A low infrastructure cost estimate and a model vendor with enterprise support.",
                ],
            ),
        ],
        "functional": [
            (
                "An AI workflow routes customer requests to specialists. What design choice is strongest?",
                "Define user roles, routing criteria, fallback paths, feedback capture, and exception ownership.",
                [
                    "Let the model infer routing rules from historical tickets without documenting workflow states.",
                    "Route everything through one review queue first so the model has fewer decisions to make.",
                    "Use the same workflow for every request type to simplify training and reporting.",
                ],
            ),
            (
                "A process includes AI-generated recommendations. What makes the functional design production-ready?",
                "Users can see rationale, override outputs, flag issues, and complete clear handoffs.",
                [
                    "The recommendation appears in the primary interface with no extra clicks.",
                    "The model output is confident enough that manual override is rare in testing.",
                    "The process removes review steps for high-volume cases before exceptions are understood.",
                ],
            ),
            (
                "A team is mapping an AI-enabled intake process. What should be captured beyond happy path steps?",
                "Input quality checks, exception states, user decisions, escalations, and feedback loops.",
                [
                    "Only the steps with direct model calls, because other steps stay mostly unchanged.",
                    "The future-state automation path first, with manual recovery documented after launch.",
                    "The UI screens and labels, because workflow design can be inferred from the interface.",
                ],
            ),
            (
                "Users distrust an AI summary feature. What functional change most directly improves trust?",
                "Show source references, confidence cues, edit history, and a clear approval workflow.",
                [
                    "Make summaries shorter so users can scan them faster during busy workflows.",
                    "Use more authoritative wording to signal that the output is system generated.",
                    "Hide low-confidence details so the output feels cleaner and less uncertain.",
                ],
            ),
            (
                "An AI assistant supports recruiters during screening. Which functional guardrail is strongest?",
                "Separate evidence extraction, recommendation, human decision, and audit capture in the workflow.",
                [
                    "Rank candidates automatically but require the recruiter to click approve before sending.",
                    "Use broad fit scores because detailed evidence can slow down high-volume recruiting.",
                    "Let recruiters edit generated rationale without preserving the original model output.",
                ],
            ),
            (
                "A workflow has frequent model uncertainty. What is the best design response?",
                "Create explicit uncertainty handling with review queues, missing-data prompts, and escalation rules.",
                [
                    "Raise the confidence threshold until fewer uncertain cases reach the user.",
                    "Ask users to retry the prompt when the model does not provide a clear answer.",
                    "Send uncertain items to the same final approval step used for normal outputs.",
                ],
            ),
            (
                "A business process spans sales and delivery teams. What functional design keeps AI adoption stable?",
                "Align handoffs, shared definitions, ownership boundaries, and cross-team feedback loops.",
                [
                    "Optimize the workflow for the team with the largest user base first.",
                    "Create separate AI tools for each team so local adoption can move faster.",
                    "Use email notifications between teams because existing habits reduce training needs.",
                ],
            ),
            (
                "A team wants to add AI-generated next steps to client meeting notes. What is the strongest workflow pattern?",
                "Require owner, due date, source context, review status, and CRM handoff for each next step.",
                [
                    "Generate a long action list so the customer success team can choose what matters.",
                    "Send the summary directly to the CRM because human review slows down the process.",
                    "Only capture next steps that the model labels as high confidence.",
                ],
            ),
        ],
        "technical": [
            (
                "A production AI service uses a hosted model API. What implementation pattern is strongest?",
                "Use retries, rate-limit handling, secrets management, tracing, evaluation, and safe fallbacks.",
                [
                    "Call the model directly from the browser to reduce backend latency and simplify deployment.",
                    "Store prompt templates in code only so changes are reviewed through normal pull requests.",
                    "Rely on vendor uptime and manually inspect failures during early production usage.",
                ],
            ),
            (
                "A retrieval system returns inconsistent answers. What is the best technical investigation?",
                "Inspect chunking, embeddings, retrieval ranking, source quality, prompt grounding, and eval cases.",
                [
                    "Increase temperature so the model can reason around weak retrieved context.",
                    "Replace the vector database before checking source documents and retrieval behavior.",
                    "Add more instructions to the system prompt telling the model to be accurate.",
                ],
            ),
            (
                "An AI endpoint handles sensitive customer data. What should be included before release?",
                "Authentication, authorization, encryption, logging controls, data minimization, and retention policy.",
                [
                    "A disclaimer in the UI explaining that users should avoid entering sensitive data.",
                    "A larger context window so fewer customer details need to be summarized manually.",
                    "Developer-only access during beta, then security hardening after product validation.",
                ],
            ),
            (
                "A model prompt change improves average score but worsens edge cases. What is the strongest next step?",
                "Use a regression evaluation set, compare slices, and gate release on critical scenario quality.",
                [
                    "Ship the prompt because the average score is the most reliable quality indicator.",
                    "Ask reviewers to manually check examples after the prompt reaches production.",
                    "Reduce the prompt complexity because edge cases often indicate overfitting.",
                ],
            ),
            (
                "An AI workflow needs auditability. Which technical design supports it best?",
                "Persist inputs, retrieved sources, prompts, model version, output, user action, and timestamps.",
                [
                    "Store only final outputs because raw prompts and sources increase compliance exposure.",
                    "Log user actions but avoid model metadata since vendors already track usage.",
                    "Capture screenshots of completed workflow pages for high-risk transactions.",
                ],
            ),
            (
                "A team needs to control cost for an AI feature. What is the strongest engineering approach?",
                "Measure token usage, cache safe responses, route by task complexity, and set budget alerts.",
                [
                    "Use the cheapest model for all requests until customer complaints indicate quality issues.",
                    "Limit user access to the feature without instrumenting request-level usage patterns.",
                    "Shorten all prompts aggressively even if context quality and answer reliability drop.",
                ],
            ),
            (
                "A service must decide between fine-tuning and retrieval-augmented generation. What factor matters most?",
                "Whether the need is changing factual context versus learned style, classification, or task behavior.",
                [
                    "Whether fine-tuning sounds more advanced to stakeholders than retrieval-based design.",
                    "Whether the team already has a vector database available in the cloud environment.",
                    "Whether the base model can answer at least one sample correctly without added context.",
                ],
            ),
            (
                "An AI feature is failing silently for some users. What production signal should be added first?",
                "Structured telemetry for request path, latency, model errors, fallback use, and output quality flags.",
                [
                    "A weekly export of user comments so product managers can summarize recurring issues.",
                    "A larger timeout so transient model delays are less visible to end users.",
                    "A manual support inbox for users to report when generated content seems wrong.",
                ],
            ),
        ],
    },
    "AI Solution Architect": {
        "business": [
            (
                "An enterprise wants an AI platform strategy. What should the architect align first?",
                "Business priorities, risk appetite, governance, operating model, and platform decision criteria.",
                [
                    "A preferred cloud vendor and model catalog before business priorities become constrained.",
                    "The fastest pilot use case so leadership can see progress before governance discussions.",
                    "A single enterprise model standard to reduce future architecture variation.",
                ],
            ),
            (
                "Executives want AI transformation across multiple departments. What portfolio approach is strongest?",
                "Create a value-risk-feasibility portfolio with reusable platform patterns and accountable sponsors.",
                [
                    "Let each department choose tools independently so adoption is not slowed by central design.",
                    "Begin with the department that has the largest budget because funding lowers delivery risk.",
                    "Require every department to use the same workflow template for consistency.",
                ],
            ),
            (
                "A proposed AI solution has strong ROI but high compliance uncertainty. What is the best recommendation?",
                "Stage delivery with risk controls, compliance review, measurable gates, and scoped release boundaries.",
                [
                    "Approve the business case because high ROI justifies resolving compliance issues later.",
                    "Reject the initiative until all compliance interpretations are completely settled.",
                    "Move the workload to a private environment so compliance concerns are automatically reduced.",
                ],
            ),
            (
                "A board asks how AI architecture supports strategy. Which answer is strongest?",
                "It translates strategic goals into governed capabilities, reusable patterns, and measurable outcomes.",
                [
                    "It selects modern tools that make the organization competitive in emerging technology.",
                    "It centralizes model access so teams can experiment without duplicating infrastructure.",
                    "It reduces manual work by replacing legacy applications with AI-native interfaces.",
                ],
            ),
            (
                "An AI roadmap has too many isolated pilots. What should the architect do?",
                "Group pilots into capability themes with shared data, controls, architecture, and success measures.",
                [
                    "Fund the pilots with the most enthusiastic teams because they will generate momentum.",
                    "Pause all pilots until an enterprise platform is fully designed and procured.",
                    "Consolidate pilots by vendor to simplify procurement and support contracts.",
                ],
            ),
            (
                "A client wants to buy an AI suite quickly. What due diligence matters most?",
                "Assess fit against outcomes, data boundaries, integration, governance, extensibility, and exit risk.",
                [
                    "Compare feature lists and vendor demos because suite capabilities are the main adoption driver.",
                    "Prioritize the suite with the broadest roadmap to avoid custom development.",
                    "Select the vendor already used elsewhere because procurement and security reviews will be easier.",
                ],
            ),
            (
                "A transformation sponsor wants all AI value attributed to headcount reduction. What is the strongest response?",
                "Broaden value to quality, speed, risk reduction, capacity, customer experience, and adoption.",
                [
                    "Accept the savings model because financial benefits are easiest to defend to executives.",
                    "Focus only on productivity metrics and avoid qualitative benefits that are harder to prove.",
                    "Exclude operational risk benefits because they are not direct revenue or cost reduction.",
                ],
            ),
            (
                "An architecture review board needs approval criteria for AI solutions. What criteria are strongest?",
                "Business value, risk classification, data governance, integration fit, operating support, and eval evidence.",
                [
                    "Model provider, estimated cost, user interface quality, and projected implementation timeline.",
                    "Whether the solution uses approved vendors and avoids custom code where possible.",
                    "Whether the delivery team can demonstrate the model answering sample questions correctly.",
                ],
            ),
        ],
        "functional": [
            (
                "A solution spans CRM, meeting notes, and follow-up workflows. What architecture artifact is most useful?",
                "A cross-system process map showing roles, data handoffs, exception paths, and system ownership.",
                [
                    "A component diagram only, because integration points define the functional behavior.",
                    "A user story list grouped by system so each team can build independently.",
                    "A data dictionary first, then workflow behavior can be inferred from field definitions.",
                ],
            ),
            (
                "A department wants an AI assistant embedded in existing work. What should the architect validate?",
                "Where the assistant changes decisions, tasks, approvals, escalations, and user accountability.",
                [
                    "Whether the assistant can answer common questions in a demo environment.",
                    "Whether the interface matches the current brand and page layout closely.",
                    "Whether users prefer chat, buttons, or both when interacting with the model.",
                ],
            ),
            (
                "A workflow has several user groups with different permissions. What design is strongest?",
                "Model outputs, actions, data visibility, and escalation paths are role-aware end to end.",
                [
                    "The same AI output is shown to all users, while the UI hides restricted buttons.",
                    "Access is managed mainly through training users on what they should not view.",
                    "Sensitive cases are excluded from AI until the workflow has enough usage data.",
                ],
            ),
            (
                "A client wants AI-generated CRM updates from calls. What functional requirement is critical?",
                "Extract contacts, decisions, needs, risks, next steps, owners, dates, and source evidence for review.",
                [
                    "Generate a polished executive summary because that is what CRM users read first.",
                    "Capture the full transcript inside CRM so downstream users can search everything.",
                    "Auto-close tasks that the model believes were resolved during the meeting.",
                ],
            ),
            (
                "A solution needs adoption across sales and delivery. What functional alignment reduces friction?",
                "Shared definitions for stage, owner, commitment, risk, follow-up, and customer priority.",
                [
                    "Separate dashboards for each team so they can interpret AI output locally.",
                    "A common AI prompt reused by all teams to standardize generated text.",
                    "More required fields so each team has enough data for its own reporting.",
                ],
            ),
            (
                "An AI process produces recommendations that affect customer commitments. What workflow control is strongest?",
                "Require human confirmation with visible evidence, impact, owner, and escalation route.",
                [
                    "Allow automatic recommendations but delay customer notification until the next sync.",
                    "Let the model decide low-risk commitments and reserve human approval for high-value accounts.",
                    "Display a confidence score and assume users will challenge low-confidence recommendations.",
                ],
            ),
            (
                "A solution must support continuous improvement. What should be designed into the workflow?",
                "User feedback taxonomy, defect capture, retraining/eval triggers, and ownership for remediation.",
                [
                    "A free-text feedback box because structured feedback can slow down user adoption.",
                    "Monthly stakeholder interviews instead of in-product feedback to reduce UI clutter.",
                    "Model temperature controls so users can tune answers when they dislike output quality.",
                ],
            ),
            (
                "A target-state process introduces AI triage. What is the best way to reduce process ambiguity?",
                "Define entry criteria, triage labels, confidence thresholds, manual review, and outcome reporting.",
                [
                    "Let labels evolve organically based on the most common model outputs during pilot.",
                    "Use broad labels first because precise labels can make early adoption harder.",
                    "Ask users to manually reclassify anything they disagree with after completion.",
                ],
            ),
        ],
        "technical": [
            (
                "An enterprise AI architecture must integrate multiple systems. What pattern is strongest?",
                "Use clear APIs/events, identity controls, data contracts, observability, and environment strategy.",
                [
                    "Connect systems through direct database reads so the AI layer has full context quickly.",
                    "Use one central prompt service and let each app format data however it can.",
                    "Start with manual exports because integration can be automated after value is proven.",
                ],
            ),
            (
                "A client asks whether to use public cloud AI services or self-hosted models. What should drive the answer?",
                "Data sensitivity, latency, cost, control, skills, compliance, scale, and lifecycle operations.",
                [
                    "The architecture team's preferred stack because consistency lowers delivery complexity.",
                    "Whether self-hosting appears safer to executives regardless of operating maturity.",
                    "The option with the lowest proof-of-concept cost in the first month.",
                ],
            ),
            (
                "An AI architecture needs governance at runtime. Which capability is most important?",
                "Policy enforcement for data access, model use, logging, evaluation, approvals, and drift response.",
                [
                    "A static architecture review before launch and periodic manual check-ins afterward.",
                    "A central model registry without workflow-level audit and policy controls.",
                    "A security questionnaire completed by every vendor used in the solution.",
                ],
            ),
            (
                "A platform must support multiple AI use cases. What architecture choice improves reuse?",
                "Shared services for identity, prompt/config management, retrieval, evals, telemetry, and secrets.",
                [
                    "A single large application that contains all use cases to prevent duplicated code.",
                    "Separate vendor platforms for each team so they can move independently.",
                    "One enterprise prompt template that every use case adapts through variables.",
                ],
            ),
            (
                "A solution requires reliable grounding in enterprise knowledge. What is the strongest technical design?",
                "Governed ingestion, metadata, access-aware retrieval, source citations, and regression evaluation.",
                [
                    "Upload documents into a vector index and depend on similarity search for grounding.",
                    "Use a larger context window to include more documents in each request.",
                    "Have the model summarize source systems nightly into a single reference document.",
                ],
            ),
            (
                "A production AI platform needs release management. What should be versioned together?",
                "Prompts, tools, retrieval config, model version, eval sets, policies, and deployment artifacts.",
                [
                    "Application code and model name only, because prompts are business content.",
                    "Vendor release notes and support tickets, because managed services handle runtime changes.",
                    "Database schema and UI components, while AI configuration stays editable by admins.",
                ],
            ),
            (
                "An AI solution must meet enterprise resilience requirements. What design is strongest?",
                "Use graceful degradation, queues/timeouts, retry policy, fallback workflows, and operational runbooks.",
                [
                    "Increase API timeouts so users wait through most transient model provider issues.",
                    "Fail closed for every AI request so no user sees an incomplete or uncertain result.",
                    "Route all failures to engineering because business users should not manage recovery.",
                ],
            ),
            (
                "A client wants to avoid vendor lock-in. What architecture choice helps most without over-engineering?",
                "Abstract model calls, standardize data contracts, retain evaluations, and keep prompts/config portable.",
                [
                    "Avoid managed AI services entirely so every component can be replaced internally.",
                    "Use two vendors for every request so switching later is already validated.",
                    "Build a custom model from scratch because owned models eliminate dependency risk.",
                ],
            ),
        ],
    },
}


def rotate_options(correct, distractors, offset):
    labels = ["A", "B", "C", "D"]
    correct_index = offset % len(labels)
    ordered = [None, None, None, None]
    ordered[correct_index] = correct
    distractor_iter = iter((distractors or [])[:3])
    for index in range(len(ordered)):
        if ordered[index] is None:
            ordered[index] = next(distractor_iter)
    return ordered, labels[correct_index]


def build_questions():
    items = []
    for track, sections in QUESTION_BANK.items():
        prefix = TRACK_PREFIX[track]
        track_offset = 0 if track == "AI Engineer" else 1
        for level in range(1, 11):
            for section, questions in sections.items():
                difficulty = SECTION_DIFFICULTY[section]
                for i, (prompt, correct, distractors) in enumerate(questions, start=1):
                    options, correct_option = rotate_options(
                        correct,
                        distractors,
                        level + i + difficulty + track_offset,
                    )
                    question_text = (
                        f"[{track} L{level}] {section.title()} Scenario {i}: {prompt}"
                    )
                    items.append(
                        Question(
                            question_code=f"{prefix}-L{level}-{section[:3].upper()}-Q{i:03d}",
                            track=track,
                            level=level,
                            section=section,
                            difficulty=difficulty,
                            weight=1.0,
                            question_text=question_text,
                            option_a=options[0],
                            option_b=options[1],
                            option_c=options[2],
                            option_d=options[3],
                            correct_option=correct_option,
                            active=True,
                        )
                    )
    return items
