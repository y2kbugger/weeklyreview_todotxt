import argparse
from pathlib import Path

from ..weeklyreviewsessiog import WeeklyReview, Tasks
from ..prompter import FixLegacyProjectPhase, AssignTasksToProjects

def main(todopath):
    tasks = Tasks()
    wr = WeeklyReview(tasks)

    with open(todopath) as f:
        tasks.add_tasks_from_file(f)

    phases = [
        FixLegacyProjectPhase(wr),
        AssignTasksToProjects(wr),
        ]

    for phase in phases:
        for relevant_task in phase:
            pass

    with open(projdir/'tests'/'todo.txt.out', 'w') as f:
        tasks.persist_task_to_file(f)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process Weekly Review items into a calendar')
    parser.add_argument('path', metavar='PATH', type=str, help='Path to todo.txt')
    args = parser.parse_args()
    main(args.path)
