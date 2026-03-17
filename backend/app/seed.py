from .models import Question
def build_questions():
    items=[]
    tracks=["AI Engineer","AI Solution Architect"]
    sections=[("business",1),("functional",2),("technical",3)]
    for track in tracks:
        prefix="AIE" if track=="AI Engineer" else "AISA"
        for level in range(1,11):
            for section,difficulty in sections:
                for i in range(1,9):
                    if track=="AI Engineer":
                        if section=="business":
                            qt=f"[{track} L{level}] Business Question {i}: Which option best reflects a sound business decision when introducing AI into an operating model?"; oa="Adopt AI everywhere immediately without prioritization"; ob="Tie AI use cases to measurable business outcomes, operating impact, and governance needs"; oc="Ignore adoption planning and change management"; od="Choose tools first and define the business case later"
                        elif section=="functional":
                            qt=f"[{track} L{level}] Functional Question {i}: Which option best reflects a strong functional workflow design for an AI-enabled process?"; oa="Remove human review from all exception paths"; ob="Design clear workflow steps, handoffs, exception handling, and user responsibilities"; oc="Assume users will adapt without process design"; od="Skip functional requirements if the model is strong"
                        else:
                            qt=f"[{track} L{level}] Technical Question {i}: Which option best reflects a strong technical approach for building an AI capability?"; oa="Deploy without observability, testing, or access controls"; ob="Use APIs, monitoring, security, and evaluation patterns suitable for production"; oc="Avoid architecture decisions until after go-live"; od="Ignore model and infrastructure tradeoffs"
                    else:
                        if section=="business":
                            qt=f"[{track} L{level}] Business Question {i}: Which option best reflects strong architecture leadership in an AI business case?"; oa="Focus only on technology and ignore business value"; ob="Connect business priorities, risk, governance, and platform decisions"; oc="Avoid executive alignment and process ownership"; od="Treat AI as a standalone experiment with no operating model"
                        elif section=="functional":
                            qt=f"[{track} L{level}] Functional Question {i}: Which option best reflects good solution architecture across user workflows?"; oa="Skip functional process mapping"; ob="Align workflows, exception paths, roles, and target-state behavior"; oc="Let the model define the process by itself"; od="Remove control points from sensitive workflows"
                        else:
                            qt=f"[{track} L{level}] Technical Question {i}: Which option best reflects strong AI solution architecture?"; oa="Choose tools without considering integration, security, and scale"; ob="Design for architecture fit, controls, extensibility, and operational support"; oc="Ignore platform constraints and data boundaries"; od="Skip environment strategy and deployment planning"
                    items.append(Question(question_code=f"{prefix}-L{level}-{section[:3].upper()}-Q{i:03d}", track=track, level=level, section=section, difficulty=difficulty, weight=1.0, question_text=qt, option_a=oa, option_b=ob, option_c=oc, option_d=od, correct_option="B", active=True))
    return items
