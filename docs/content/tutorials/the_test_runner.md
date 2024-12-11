- you use the tree runner to build a tree of nodes (nodes are also referred to as tasks); the structure of the tree is arbitrary

- each task can succeed or fail

- each task has

  - a stage (and optionally a substage) - this identifies the type of the task. The stage/substage is used to look up audit questions in the config file. These can be arbitrary
  - task data - this is an arbitrary object which is used to provide context to the LLM when it's asked to answer audit questions about the task. This is the only information the LLM will have about the task when answering the questions
  - a compositive flag - this indicates whether the task is compositive (see below). By default, tasks are not compositive

- the success or failure of a task is calculated like this:

  - a compositive task simply succeeds if all of its child tasks succeed, and fails otherwise. The LLM is not consulted to determine whether the task has succeeded or failed. Task data is ignored for compositive tasks.
  - to evaluate the success of a non-compositive task, the LLM is asked a series of audit questions about the task data attached to the task. Audit questions are fetched from configuration based on the stage & substage of the task. If all of the audit questions are answered in the affirmative, the task succeeds, otherwise it fails. A non-compositive task may succeed even if some of its children have failed.
