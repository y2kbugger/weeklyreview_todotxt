Quickstart:
Ensure system has pipenv and pyenv
$pyenv install 3.9.0b3
$pipenv install --dev

Then whenever you want to develop

$pipenv shell
$pytest -f

Guided Weekly Review

Use git to snapshot before so changes can be reviewed or reverted.

Tasks to Projects
Ensure all open "daily review" tasks are associated with a project
1 List out all items missing a proj:codename
    Options:
        - Turn into a project
        - Assign to a project
        - Create a project for it

Curate projects
1 Ensure all projects have a priority
2 Ensure all projects have a unique proj:codename
3 Curate Projects
    Options:
    - Refine project priorities.
    - Rename projects

Plan tasks
1 Assign all tasks to take on the priority of it's proj:codename parent
    - Automatic, but give summary and ask for confirmation
2 Ensure all A or B projects have at least one task
    - Show existing tasks for each
    - Options:
        - Add task
        - Next project (only if there is at least on task)


Guided Weekly Planning

Assign hours to tasks
1 For each A or B task prompt to add or change time estimate

Plan week
1. Assign task to days of week
    - Continuously show hour many hours are assign to each day
    - We can interactively move these around until an appropriate amount is assign to each day.
2. Save it out to make threshold match the assigned day.

Future:
review for places
break some of the non-todos out to their own files...
    maybe this would elimiate need for @^ or @~
    It should also help reduce tag sprawl
tag curation assistant (combine/eliminate/add) tags

TDD
----------------
Can read in various todo.txt lines and re-persist


