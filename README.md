# Quickstart
Use poetry to install the dependencies:

    $ poetry install

Install pre-commit hooks:

    $ poetry run pre-commit install --hook-type pre-commit --hook-type pre-push

then activate and run the tests via vscode or the cli:

    $ poetry shell
    $ pytest

Interactively code with the python API in the `scratch.ipynb` notebook. This should include many examples.

Run the webapp (FastAPI) UI

    $ uvicorn insync.app:app --reload --reload-dir insync --reload-include='*.css' --reload-include='*.html

# Deployment
Production startup command should use gunicon with uvicorn, as it is a production ready ASGI server, whearas uvicorn is just a development server.

  $ gunicorn -w 1 -k uvicorn.workers.UvicornWorker insync.app:app

To see what is running in the deployed file environment, start up a python file server up there:

  $ python -m http.server 8000

# WIP
- Add first class ListItemsFilter to handing filtering (completed, recurring, etc), grouping, sorting, of items
  - implement sorts for the view
  - separate ListRegistry, Commands, and ListView
- I want the sort order of uncompleted items to be the creation date
- I want the sort order of completed items to be the completion date

# Bugs
- archived items are not hidden from UI
- archived items are not greyed out

# Backlog
## IT Tedium
- css to separate files
- make db patch async
- ruff lint pre-commit hook
- ruff format pre-commit hook
- url encoding for `Project.name`s (see todo.txt template)
  - e.g. fix: `{ project.project_type.value if project.project_type.value != 'null' else '*'}`
  - This needs to be used for all user facing project names e.g. in the header for null to show *
- ensure that all endpoints sync vs async are correct
  - https://github.com/omnilib/aiosqlite
  - turn on this lint when available https://github.com/astral-sh/ruff/pull/9966
- ensure we are using uvloop in production (especially now that we gotta gunicorn)
- add effieciency to db queries, actually make it so that load doesn't get archived items (by default at least)
- configure htmx not to send headers
- batch patches to db for performance, don't wait for each one to complete before returning
  - did a benchmark with like 4000+ items saving to DB and it's not urgent, also might be harder to debug/notice if something goes wrong with persisting
- refactor `Command`s to use ABC with do/undo wrappers instead of requiring manual done asserting...
- first clas method for removing common prefixes from project names

## Todo.txt Page
- I want a gui in the todo.txt endpoint so that I can easily navigate to different list types, and names e.g. `*`, `project`, `checklist`, `todo` and `*`, `travel`, `gro`, `grocery`, etc
- I want to be able to view archived items so that I can reference them

## Checklists
- I want to be able to click into a subproject, e.g. produce so that I can focus
- I want an overall hyperlinked cookie crumb trail so that I can easily navigate up and down the project hierarchy
- I want to be able to rename a subproject so that I can curate my lists
- I want integer project parts to be sorted numerically so that they are in the correct order
- I want to be able to drag and drop a subproject so that I can easily reorder them
- I want the integer part of a project to be hidden in the UI so that it doesn't clutter the view
- I want to be able to have a heirarchy of checklists that can be checked of all at once e.g. `travel.international `
  - sections could be sorted by integer subproject e.g. `+^grocery.1.produce` `+^grocery.2.dairy`
- I want an easy way to undo an accidental action e.g. reset, completion so that I can quickly recover from mistakes.
- I want to be able to create a subproject via an initial '.' in the entry box so that I can quickly create a subproject
- I want visual feedback while designating a subproject so that I can see that it is being created.
  - Also add hint in the entry box placeholder
- I want the ability to view recently archived items so that I can reference/restore them
- I want the ability to update an item description so that I can evolve it over time

## Admin/Debug Page
- connected websockets
- undo/redo history
- database size
  - bytes of file
  - number of items
  - number of archived items
  - number of project for each type
- benchmark/profile testsuite on current data
- export/import todo.txt
- snapshots lists to view/restore
  - sqlite
  - todo.txt

## Todos
- I want lists that are backlogs of projects so that I can plan what to work on during planning.
- I want a quick view of planned items for the day/week so that I can work on them.
- I want tag a todo with a tag and subtag as first class ability e.g. `#house.garage.garendingcorner`
- I want to be able to set a priorty of backlog items so that the most critical can be viewed first
- I want a way to add an estimated cost to a task so that we can estimate the total cost of a project or tag or subtag
- I want an guided daily weekly and monthly review process so both of us so that we don't have to think about the process steps as we do the review and we can go FAST and not miss anything
- I want to track purchases for things like gym, baby that are expensive so that we can plan for them.....can the just be done the same as regular todo? or do we need a special distiction for them.
- Hide projects that are not currently priority, except for the weekly review
- review cadence for high level life goals, things like "be a good parent" or "be a good spouse", "stay healthy"
- review cadence for lists of things like "places to eat" or "vacation spots"

## Reference
- I want a list type that doesn't have the concept of required completion, but as a reference. e.g. places to eat. vacation spot. These don't end up in up in reviews, but can be referenced specifically.

## System
- todo.txt constructors so that I can write writetests more concisely, and restore from todo.txt format
- I want to view list of archived lists so that I can reference historical lists
  - an archived list is a list has only archived items
- I want an routine backups of the list in sqlite format so that I can recover from a disaster
- I want an routine backups of the list in todo.txt format so that I can recover from a disaster
- I want to be able to at _least_ read while offline so that I can look at lists while internet unavailble
- As a user I don't want a description edit to be interupted by a websocket update from another user so that I don't get frustrated.
- I want to be able to click/preview a link in a description so that I can easily navigate to the reference
- animating reordering using oob for each list element (guid based tasks?)
  - https://gist.github.com/Thomasparsley/b818e59a6733c40116816cf78f406e96
  - can still research other methods

## Capture
- I want capture to be easily as possible so that I can quickly add items to the system and delay organization.
- I want to capture photos via share images so that I can quickly capture reminders and references for later.
- I want to quickly capture notes via ok Google so that I can effortlessly capture todos.


# Architecture
 - FastAPI/Jinja backend
 - Leverage FastAPI websockets for real-time collaboration of lists
 - HTMX for dynamic parts of the UI
 - Persistence
  - Working memory only for current list and undo stack (implemented)
  - SQLite for persistance backup after, restored on startup (implemented)
  - Periodic historical snapshots
    - SQLite (not implemented)
    - todo.txt format (not implemented)
### Todo.txt
- map our concepts to todo.txt
  - completed `x`
  - priorty `(A) `
  - completion-date `2020-01-01`
  - creation-date `2020-01-01`
  - context `@home` `@car`
  - project: `+house`
  - simpletask extensions
    - due-date `due:2020-01-01`
    - threshold `t:2024-12-31`
    - hidden `h:1`
  - our extensions
    - completion_datetime `2020-01-01T21:39:27-05:00`
    - creation_datetime `2020-01-01T21:39:27-05:00`
    - archival_datetime `archived:2020-01-01T21:39:27-05:00`
    - project-tree `+house.garage`
      - and we only allow one per item
      - type prefixs
        - `+` - todo
        - `+^` - checklist
        - `+#` - reference
    - cost `$:100`
    - effort `hours:2.5`
    - recurable `rec:true`
      - could have recurrance rules, true is manual which is the only one we support for now


# Existing List Pardigms
- GTD - https://todoist.com/productivity-methods/getting-things-done
  - Capture
  - Clarify
  - Organize
  - Reflect
  - Engage
- MYN
  - Critical Now - Absolutely must be done today, review once per hour
  - Opportunity Now - Could be done in next 10 days, review once per day
  - Over the Horizon - Will do more than 10 days from now, review once per week


# Integrity checks
Ensure all `#myproject` tasks are associated with a `prjdef:1` project definition
1. All `#myproject` tags should have exactly one 'prjdef:1' item
- this allow setting a priority for a project itself
- give a place to describe the project overall

# Weekly Review
## Item Organization
Ensure all items are associated with a project

1. List out all items missing a `#myproject` tag
  - Options
    - Assign to an existing project
    - Assign to new project (Create a project for it)
    - Turn into a project (no input) `prjdef:1`

## Curate projects
1. Ensure all projects (`prjdef:1`) have a priority
2. Ensure all projects have single `#myproject` tag
3. Curate Projects
  - Options
    - Refine project priorities.
    - Rename projects

## Plan tasks
1. Ensure all `A` or `B` projects have at least one task
  - Show existing tasks for each
  - Options
    - Add task
    - Next project (only if minimum of one task is met for current project)

## Estimate Effort
Assign hours to tasks
1. For each `A` or `B` task prompt to add or change time estimates

# Daily Review
TBD
