# Quickstart
Use poetry to install the dependencies:

    $ poetry install

then activate and run the tests via vscode or the cli:

    $ poetry shell
    $ pytest

# Architecture



# WIP
- make a prototype of an in-memory version of a todo list
  - handle basic state manipulation, with undo/redo

# Backlog
## Todos
- I want lists that are backlogs of projects so that I can plan what to work on during planning.
- I want a quick view of planned items for the day/week so that I can work on them.
- I want tag a todo with a tag and subtag as first class ability e.g. `#house.garage.garendingcorner`
- I want to be able to set a priorty of backlog items so that the most critical can be viewed first
- I want a way to add an estimated cost to a task so that we can estimate the total cost of a project or tag or subtag
- I want an guided daily weekly and monthly review process so both of us so that we don't have to think about the process steps as we do the review and we can go FAST and not miss anything
- I want to track purchases for things like gym, baby that are expensive so that we can plan for them.....can the just be done the same as regular todo? or do we need a special distiction for them.
- Hide projects that are not currently priority, except for the weekly review

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
- I want to be able to view older versions of the list so that I can see what was done in the past
- I want an easy way to backup the list so that I can recover from a mistake
- I want to view a historical list of projects archived tasks so that I can see what was done in the past
- I want to view a global list of timestamped actions so that I can undo or redo actions

## General
- review cadence for high level life goals, things like "be a good parent" or "be a good spouse", "stay healthy"
- review cadence for lists of things like "places to eat" or "vacation spots"

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
    - effort `hours:2.5`
    - type `type:[checklist|todo|ref|checklist.onetime]`


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