# from ..parser import Tasks
import weeklyreviewtodotxt
from ..tasktoprojects import WeeklyReview, Tasks
from ..prompter import FixLegacyProjectPhase, AssignTasksToProjects



def main():
    from pathlib import Path
    projdir = Path(weeklyreviewtodotxt.__file__).parent
    tasks = Tasks()
    wr = WeeklyReview(tasks)

    with open(projdir/'tests'/'todo.txt') as f:
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
    main()
