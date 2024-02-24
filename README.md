# Quickstart
Use poetry to install the dependencies:

    $ poetry install

then activate and run the tests via vscode or the cli:

    $ poetry shell
    $ pytest



# WIP
- reread api and tests to understand the starting point i'm at
# Backlog
## Todos
- I want lists that are backlogs of projects so that I can plan what to work on during planning.
- I want a quick view of planned items for the day/week so that I can work on them.
- I want tag a todo with a tag and subtag as first class ability e.g. `#house.garage.garendingcorner`
- I want to be able to set a priorty of backlog items so that the most critical can be viewed first
- I want a way to add an estimated cost to a task so that we can estimate the total cost of a project or tag or subtag
- I want an guided daily weekly and monthly review process so both of us so that we don't have to think about the process steps as we do the review and we can go FAST and not miss anything
- I want to track purchases for things like gym, baby that are expensive so that we can plan for them.....can the just be done the same as regular todo? or do we need a special distiction for them.

## Checklists
- I want a way to have an eternal checklists that can be checked off but also reset
- As a user I want to safety check before resetting a list so that it doesn't accidentally get reset
- I want to be able to have a heiracry of checklists that can be checked of all at once e.g. `travel.international `
- I want a way to capture new items to the eternal checklist
- I want a way to add "one time" items that don't need be added to the eternal checklist
  - one time can be default with a star or other method to make it permanent
- I want a way to archive an item from the eternal list
  - move from checklist to checklist.archived ?

## Reference
- I want a list type that doesn't have the concept of required completion, but as a reference. e.g. places to eat. vacation spot. These don't end up in up in reviews, but can be referenced specifically.

## System
- I want to be able to at _least_ read while offline so that I can look at lists while internet unavailble
- I want the ability to smartly merge edits after multiple users make offline edits so that when sara and I both check off items we don't have problems
- I want capture to be easy as possible so that I can quickly add items to the list. I want to delay organization until later.

# Legacy backlog
- Have to handle creation date somehow --> maybe new tasks could always inherit from existing task..there are not that many cases for creating new tasks.
- add (1/23) type counted to show progress for each step
- add ability to can cycle or entire step (choice = s,ss)
- Fix Legacy Project should check for duplicate prj: tags
- Options can have choices
- Add explain command which prints description (autoadd like Skip)
- prompt reprompts when non-integer choice is picked
- make all commands explain the action being done a la "Skipping"
- can we make it use readline or similar for tag entry.
- can we make it automatch on char entry, without require return after each one.
- global option of quit just like skip
- global option to print all tasks
- global options to itemize changes so far.
- Tedium
  - lint for unused import, etc
  - Move main to bin

# Brainstorm
- working memory
  - each task has a guid
  - pure python objects
  - pandas dataframes
  - sqlite db
- persistence
  - backup of sqlitedb
  - git history in todo.txt
- client app
  - only viewing one "file" of todo.txt at a time
    - or is it one `#project` tag at a time
- do I enforce one `#project` tag per line?
  - pros: simpifies parsing, indexing, and display and UI complexity
  - cons: can't slice in to dimensions, might not really be important

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
- map our concepts to todo.txt
  - priorty `(A) `
  - context `@home` `@car`
  - project: `+house`
  - simpletask extensions
    - due-date `due:2020-01-01`
    - threshold `t:2024-12-31`
    - hidden `h:1`
  - our extensions
    - project-tree `+house.garage`
    - cost `$:100`
    - type `type:[checklist|todo|ref|checklist.onetime]`

# Guided Weekly Review
## Preparation
Use git to snapshot before so changes can be reviewed or reverted.

## Update Legacy Projects
1. Review `@@@project` missing a `prj:codename` to add a `prj` tag.
  - Options
    - Auto (show preview)
    - Manual

## Tasks to Projects
Ensure all open "daily review" tasks are associated with a project

1. List out all items missing a `prj:codename`
  - Options
    - Assign to a project
    - Assign to new project (Create a project for it)
    - Turn into a project (no input)

## Curate projects
1. Ensure all projects have a priority
2. Ensure all projects have a unique `prj:codename`
3. Curate Projects
  - Options
    - Refine project priorities.
    - Rename projects

## Plan tasks
1. Assign all tasks to take on the priority of it's `prj:codename` parent
  - Automatic, but give summary and ask for confirmation
2. Ensure all `A` or `B` projects have at least one task
  - Show existing tasks for each
  - Options
    - Add task
    - Next project (only if there is at least on task)


# Guided Weekly Planning
Assign hours to tasks
1. For each `A` or `B` task prompt to add or change time estimate

## Plan week
1. Assign task to days of week
  - Continuously show hour many hours are assign to each day
  - We can interactively move these around until an appropriate amount is assign to each day.
2. Save it out to make threshold match the assigned day.

# Other Stuff/Future Reviews:
- review for places
- break some of the non-todos out to their own files...
  - maybe this would elimiate need for @^ or @~
  - It should also help reduce tag proliferation
- tag curation assistant (combine/eliminate/add) tags
