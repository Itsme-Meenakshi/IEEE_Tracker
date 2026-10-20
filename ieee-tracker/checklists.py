"""Checklist templates for every event type.

Each item is (phase, title, due_offset_days) where the offset is relative to the
event date (negative = before the event, positive = after).
Mode-specific items (online / offline) are appended automatically.
"""

PHASES = ["Planning", "Pre-event", "Event day", "Post-event"]

EVENT_TYPES = {
    "hackathon": "Hackathon",
    "workshop": "Hands-on Workshop",
    "talk": "Talk Session",
    "inauguration": "Inauguration",
    "flagship": "Flagship Event",
    "competition": "Competition",
    "panel": "Panel Discussion",
    "orientation": "Orientation",
    "webinar": "Webinar",
    "conference": "Conference",
    "exhibition": "Exhibition",
}

MODES = ["online", "offline", "hybrid"]

# ---------- common to every event ----------
COMMON_START = [
    ("Planning", "Finalise event concept, objectives and target audience", -30),
    ("Planning", "Fix date, time and duration; check clash with academic calendar/exams", -28),
    ("Planning", "Form organising committee and assign responsibilities", -28),
    ("Planning", "Prepare tentative budget and get approval.", -25),
    ("Planning", "Take permission from Branch Counsellor /Chapter Advisor / Principal", -21),
    ("Pre-event", "Give for poster, registration Google Form, content and get it approved.", -14),
    ("Pre-event", "Release poster on social media, WhatsApp groups and campus channels", -12),
    ("Pre-event", "Send invitations (guests, faculty, other societies, IEEE officials)", -10),
    ("Pre-event", "Prepare certificates (participation / winners / speakers) and get them verified", -4),
    ("Pre-event", "Send reminder to registered participants", -1),
    ("Pre-event", "Send reminder to Speaker/Resource Persons", -1),
    ("Event day", "Take attendance (sign sheet / form / platform report)", 0),
    ("Event day", "Photographs and videos coverage", 0),
    ("Post-event", "Distribute certificates", 3),
    ("Post-event", "Collect feedback form responses", 3),
    ("Post-event", "Send thank-you messages to speakers, guests and volunteers", 2),
    ("Post-event", "Prepare event report with photos and attendance", 5),
    ("Post-event", "Submit report in Drive", 7),
    ("Post-event", "Settle expenses and submit bills / budget report", 10),
    ("Post-event", "Post highlights on social media", 2),
    ("Post-event", "Update IEEE vTools", 10),
]

# ---------- mode extras ----------
ONLINE = [
    ("Pre-event", "Prepare Digital memento / token of appreciation for the speaker", -3),
    ("Planning", "Choose platform (Google Meet / Zoom / Teams / YouTube Live)", -21),
    ("Pre-event", "Create meeting/webinar link and test it", -3),
    ("Pre-event", "Share joining link and instructions with participants", -1),
    ("Event day", "Record the session", 0),
    ("Event day", "Share links to feedback form and resources in chat", 0),
    ("Post-event", "Download attendance report from platform", 1),
    ("Post-event", "Share recording / resources with attendees", 3),
]

OFFLINE = [
    ("Pre-event", "Prepare memento / token of appreciation for the speaker", -3),
    ("Planning", "Book venue (hall / lab / auditorium) and get written confirmation", -21),
    ("Pre-event", "Arrange seating, projector, mic, sound system and extension boards", -3),
    ("Pre-event", "Arrange refreshments / snacks / water", -2),
    ("Pre-event", "Print banners, standees, name tags and sign sheets", -3),
    ("Pre-event", "Get duty leave / attendance permission letters for volunteers & participants", -5),
    ("Event day", "Set up venue and registration desk before start time", 0),
    ("Event day", "Volunteers briefed and in position", 0),
    ("Post-event", "Return borrowed equipment and clean up the venue", 1),
]

HYBRID_EXTRA = [
    ("Pre-event", "Test live-streaming / hybrid camera and audio setup", -2),
    ("Event day", "Assign a volunteer to moderate online participants", 0),
]

# ---------- type specific ----------
TYPE_ITEMS = {
    "hackathon": [
        ("Planning", "Decide theme, tracks and problem statements and Agenda", -28),
        ("Planning", "Define team size, eligibility and rules & regulations", -25),
        ("Planning", "Identify and approach sponsors / prize partners", -25),
        ("Planning", "Finalise judging criteria and invite judges / mentors", -18),
        ("Pre-event", "Open team registration form and shortlist teams", -10),
        ("Pre-event", "Arrange Wi-Fi, power strips and 24/48-hour logistics", -5),
        ("Pre-event", "Arrange food, water and rest area for participants", -4),
        ("Pre-event", "Set up submission platform (Devfolio / GitHub / Google Form)", -5),
        ("Event day", "Opening briefing: rules, timeline and judging criteria", 0),
        ("Event day", "Mentoring rounds and mid-evaluation", 0),
        ("Event day", "Final presentations and judging", 0),
        ("Event day", "Prize distribution and valedictory", 0),
        ("Post-event", "Publish results and winner list", 1),
        ("Post-event", "Collect project submissions / repos and share with sponsors", 4),
    ],
    "workshop": [
        ("Planning", "Finalise topic, syllabus and prerequisites", -25),
        ("Planning", "Invite and confirm resource person; share expectations", -21),
        ("Pre-event", "Cap registrations; confirm seats / lab capacity", -7),
        ("Pre-event", "Prepare hands-on material, datasets, slides and installation guide", -5),
        ("Pre-event", "Ask participants to install required software / bring laptops", -3),
        ("Pre-event", "Test labs / systems and software beforehand", -2),
        ("Event day", "Distribute / share materials and credentials", 0),
        ("Event day", "Volunteers assisting participants during the hands-on session", 0),
        ("Event day", "Hands-on task / mini-assessment completed", 0),
        ("Post-event", "Share slides, code and resources with participants", 2),
        ("Post-event", "Give resource person a token of appreciation / honorarium process", 5),
    ],
    "talk": [
        ("Planning", "Select topic and speaker; send invitation letter", -25),
        ("Planning", "Get speaker's bio, photo and talk title", -14),
        ("Pre-event", "Prepare speaker introduction / welcome script", -3),
        ("Pre-event", "Assign emcee, welcome speaker, vote of thanks, and moderator", -5),
        ("Pre-event", "Prepare memento / token of appreciation for the speaker", -3),
        ("Event day", "Receive and host the speaker; confirm AV setup", 0),
        ("Event day", "Q&A session moderated", 0),
        ("Post-event", "Send thank-you mail to speaker with photos", 2),
    ],
    "inauguration": [
        ("Planning", "Invite Chief Guest and Guest of Honour; get confirmation", -25),
        ("Planning", "Invite IEEE Kerala Section / Student Activities officials", -21),
        ("Planning", "Prepare programme schedule and script", -10),
        ("Pre-event", "Prepare invitation cards / e-invites", -12),
        ("Pre-event", "Prepare stage, lamp, flowers, banner and mementos", -3),
        ("Pre-event", "Plan the society's activity calendar / action plan to present", -7),
        ("Pre-event", "Assign emcee, prayer/welcome, felicitation and vote of thanks", -5),
        ("Event day", "Welcome and receive dignitaries", 0),
        ("Event day", "Lamp lighting, inauguration and announcement of EB members", 0),
        ("Post-event", "Send thank-you letters to guests", 2),
        ("Post-event", "Share media coverage / press release", 2),
    ],
    "flagship": [
        ("Planning", "Define flagship vision, sub-events and timeline", -45),
        ("Planning", "Prepare detailed budget and sponsorship deck", -40),
        ("Planning", "Approach sponsors and track confirmations", -35),
        ("Planning", "Form core team and sub-committees (tech, design, PR, logistics, hospitality)", -40),
        ("Planning", "Get institute-level approval and calendar slot", -35),
        ("Pre-event", "Launch website / registration portal/ posters and content", -21),
        ("Pre-event", "Publicity campaign and teasers on social media", -21),
        ("Pre-event", "Invite chief guest, speakers and judges", -21),
        ("Pre-event", "Arrange accommodation / travel / hospitality for guests", -7),
        ("Pre-event", "Prepare printed schedule, ID cards and Goodies", -5),
        ("Pre-event", "Final coordination meeting with all sub-committees", -2),
        ("Event day", "Registration desk and participant help-desk running", 0),
        ("Event day", "Sub-event coordinators ready and on schedule", 0),
        ("Event day", "Valedictory and prize distribution", 0),
        ("Post-event", "Sponsor acknowledgements and deliverables sent", 5),
        ("Post-event", "Core team review / lessons-learned meeting", 7),
    ],
    "competition": [
        ("Planning", "Define competition format, rounds and rules", -25),
        ("Planning", "Set eligibility, team size and registration fee (if any)", -21),
        ("Planning", "Finalise judging criteria and invite judges", -18),
        ("Planning", "Arrange prizes and sponsorship", -18),
        ("Pre-event", "Publish rulebook and problem statements / question set", -10),
        ("Pre-event", "Open registrations and shortlist participants", -10),
        ("Pre-event", "Prepare scoresheets / quiz platform / evaluation tools", -3),
        ("Event day", "Conduct rounds as per schedule", 0),
        ("Event day", "Verify scores and finalise results", 0),
        ("Event day", "Prize distribution", 0),
        ("Post-event", "Publish results and winners list", 1),
        ("Post-event", "Handle result queries / appeals", 3),
    ],
    "panel": [
        ("Planning", "Fix discussion theme and key questions", -21),
        ("Planning", "Invite panelists and a moderator; confirm participation", -21),
        ("Pre-event", "Share question outline and format with panelists", -7),
        ("Pre-event", "Collect panelist bios and photos for poster", -10),
        ("Pre-event", "Collect audience questions in advance (form)", -4),
        ("Event day", "Panelist seating, mics and name placards ready", 0),
        ("Event day", "Moderated discussion and audience Q&A", 0),
        ("Post-event", "Share key takeaways summary", 3),
    ],
    "orientation": [
        ("Planning", "Prepare society introduction presentation", -14),
        ("Pre-event", "Prepare membership benefits and IEEE membership process sheet", -7),
        ("Pre-event", "Prepare upcoming events / action plan slides", -7),
        ("Pre-event", "Create interest / volunteer sign-up form", -7),
        ("Event day", "Introduce executive committee and activities", 0),
        ("Event day", "Collect interest forms / new member details", 0),
        ("Post-event", "Add interested students to society WhatsApp / mailing group", 2),
        ("Post-event", "Follow up on IEEE membership registrations", 7),
    ],
    "webinar": [
        ("Planning", "Fix topic and invite speaker", -21),
        ("Pre-event", "Collect speaker bio, photo and title for poster", -10),
        ("Pre-event", "Set up registration and auto-reminder emails", -7),
        ("Event day", "Moderator manages chat and Q&A", 0),
        ("Post-event", "Upload recording (YouTube / Drive) and share link", 2),
    ],
    "conference": [
        ("Planning", "Define conference theme, tracks and committees", -90),
        ("Planning", "Prepare Call for Papers and review process", -75),
        ("Planning", "Set up paper submission system (EasyChair / CMT / form)", -70),
        ("Planning", "Form technical programme committee and reviewers", -70),
        ("Planning", "Prepare budget, sponsorship and registration fee structure", -70),
        ("Pre-event", "Release CFP and publicise across institutions", -60),
        ("Pre-event", "Complete review and send acceptance notifications", -25),
        ("Pre-event", "Collect camera-ready papers and presenter registration", -15),
        ("Pre-event", "Prepare conference schedule, proceedings and keynote logistics", -7),
        ("Pre-event", "Arrange accommodation / travel / hospitality", -7),
        ("Event day", "Paper presentation sessions and session chairs", 0),
        ("Event day", "Keynote and valedictory", 0),
        ("Post-event", "Publish proceedings / submit to IEEE Xplore (if applicable)", 30),
        ("Post-event", "Send best paper awards and participation certificates", 5),
    ],
    "exhibition": [
        ("Planning", "Define exhibition theme and categories", -25),
        ("Planning", "Call for project / stall registrations", -21),
        ("Pre-event", "Allot stalls / tables and prepare layout map", -5),
        ("Pre-event", "Arrange power supply, tables, display boards and safety measures", -3),
        ("Pre-event", "Plan visitor flow, signage and volunteers per zone", -3),
        ("Pre-event", "Invite judges / guests / visitors from other departments", -10),
        ("Event day", "Setup, inspection and judging walk-through", 0),
        ("Event day", "Announce best exhibit / awards", 0),
        ("Post-event", "Dismantle stalls and clear the venue", 1),
    ],
}


def build_checklist(event_type: str, mode: str):
    """Return the tailored list of (phase, title, offset) for a type + mode."""
    items = list(COMMON_START)
    if mode == "online":
        items += ONLINE
    elif mode == "offline":
        items += OFFLINE
    else:
        items += ONLINE + OFFLINE + HYBRID_EXTRA
    items += TYPE_ITEMS.get(event_type, [])

    # Online events don't need physical-venue-only common items
    if mode == "online":
        skip = {
            "Photographs and videos coverage",
        }
        items = [i for i in items if i[1] not in skip]
        items.append(("Event day", "Screenshots of the session with participants visible", 0))

    order = {p: n for n, p in enumerate(PHASES)}
    items.sort(key=lambda i: (order[i[0]], i[2]))
    return items
