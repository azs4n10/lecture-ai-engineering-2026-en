FAQ = {
    "environment": "Bring a laptop with Ubuntu 22.04 and ROS 2 Humble installed before the first session.",
    "robot": "Each team can borrow one TurtleBot 4, and it must be returned to the lab by 18:00 on the same day.",
    "room": "The robot lab (Room 305) is open on weekdays from 10:00 to 20:00.",
    "demo": "The final demo is held on December 18 from 13:00, and each team presents for 10 minutes.",
    "team": "Each team has three members, and team members are fixed for the whole course.",
}
FAQ_TEXT = "\n".join(f"- {v}" for v in FAQ.values())
GROUNDED = {
    "environment": (["What do I need to prepare before the first session?", "Which Ubuntu version should I install?", "What should be installed on my laptop?", "Which ROS 2 distribution is used?"], ["Ubuntu 22.04", "Humble"]),
    "robot": (["Can we borrow a robot?", "Which robot can our team use?", "When do we have to return the robot?", "How many robots can a team borrow?"], ["TurtleBot 4", "18:00"]),
    "room": (["When is the robot lab open?", "What are the lab opening hours?", "Can I use the lab on weekdays?", "Which room is the robot lab?"], ["305", "10:00"]),
    "demo": (["When is the final demo?", "How long is each team's presentation?", "What is the date of the final demo?", "What time does the final demo start?"], ["December 18", "13:00"]),
    "team": (["How many people are in a team?", "Can I change teams later?", "What is the team size?", "Are team members fixed?"], ["three"]),
}
UNGROUNDED = [
    "Who do I contact if the robot breaks?", "Is attendance taken in each session?", "Is there a rehearsal before the final demo?", "Will the slides be shared after each session?",
    "Can I use the GPU server in the lab?", "Is there a written exam?", "How are team members chosen?", "Can I bring my own robot?",
]
TEST_EXTRA_GROUNDED = {
    "environment": ["Tell me the OS and ROS version I need", "What software must be on my laptop for this course?"],
    "robot": ["By what time must the borrowed robot be returned?", "Tell me the robot lending rules"],
    "room": ["Tell me the room number and hours of the robot lab", "From what time can I enter the robot lab?"],
    "demo": ["Tell me the final demo schedule", "On what day is the final presentation held?"],
    "team": ["How many members does each team have?", "Can team members be swapped during the course?"],
}
TEST_EXTRA_UNGROUNDED = [
    "How is the final demo graded?", "What should I do if my laptop cannot run ROS 2?",
    "Is there a fee for borrowing the robot?", "Who is responsible if a team member drops the course?",
]
UNGROUNDED_ANSWER = "This FAQ does not contain that information. Confirmation from the course organizers is needed."
