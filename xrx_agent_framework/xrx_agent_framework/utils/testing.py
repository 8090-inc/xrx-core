from .llm import json_fixer, initialize_async_llm_client
import os
import yaml 
import json
import openai

# set up llm
LLM_CLIENT = initialize_async_llm_client()
LLM_MODEL_ID = os.environ.get('LLM_MODEL_ID', '')
test_on = os.environ.get('TREE_TEST_RUNNER_ON', 'false').lower() == 'true'

testPrompt =  '''\
You are an expert at answering questions about a particular task, based on certain information 
about the results of the task execution.

## Task Information
When attempting to answer the questions listed under 'Audits', you should reference the 
following piece of JSON containing information about the results of the task execution:

{taskData}

## Audits
These are the questions you should answer about the task. These are all yes or no questions:

{audits}

## Output Format
You must return a perfectly formatted JSON object which can be serialized with the following keys:
- 'success': This should be TRUE if you have determined that the task succeeded, and FALSE otherwise.
- 'reason': A string explaining why the task succeeded or failed.
- 'audits': If there are no audits listed above under 'Audits', make this an empty array. Otherwise, 
   for each audit listed above under 'Audits', return a perfectly formatted JSON object which 
   can be serialized with the following keys: 
    -'text': This should be the exact text of the audit, with no modifications.
    -'success': This should be TRUE if the audit can be answered in the affirmative, and FALSE otherwise. 
    -'reason': A string explaining why the audit succeeded or failed.
'''

# claude wrote this; if there's a better way to do it in the standard library I can't remember it
def deep_merge(dict1, dict2):
    merged = dict1.copy()  # Make a copy to avoid modifying the original

    for key, value in dict2.items():
        if key in merged:
            # If both values are dictionaries, recursively merge them
            if isinstance(value, dict) and isinstance(merged[key], dict):
                merged[key] = deep_merge(merged[key], value)
            # If both values are lists, concatenate them
            elif isinstance(value, list) and isinstance(merged[key], list):
                merged[key] = merged[key] + value
            # Otherwise, value from dict2 overwrites value from dict1
            else:
                merged[key] = value
        else:
            # Key not in dict1, just add it
            merged[key] = value

    return merged

def readYaml(file_path):
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
    return data

def get_sibling_file(current_file_path: str, sibling_filename: str) -> str:
    directory = os.path.dirname(os.path.abspath(current_file_path))
    return os.path.join(directory, sibling_filename)

# note: not truthy! just something that can be construed as true. 
# this is because the LLM doesn't return 'true' in a consistent
# format
def is_truish(val):
    return val == 'true' or val == 'True' or val == True

def genPrompt(taskData, audits):
    testPrompt2 = testPrompt.replace('{taskData}', json.dumps(taskData))
    return testPrompt2.replace('{audits}', ''.join([f"- {audit}\n" for audit in audits]))

class TestResult():
    def __init__(self, succeeded, reason, audits, fullResponse):
        self.succeeded = succeeded
        self.reason = reason
        self.audits = audits
        self.fullResponse = fullResponse

class TaskNode():
    def __init__(self, userGoal=None):
        self._children = []
        self._userGoal = userGoal

    def spawnChild(self):
        if hasattr(self, "_closed"):
            raise Exception("This node has already had close() called on it. " +
                "Children may not be spawned from a closed node.")

        child = TaskNode()
        self._children.append(child)

        return child

    # TODO(mprast): maybe find a cleaner way to handle the root case
    def setTaskNodeDetails(self, compositive, stage, substage, taskData):
        if not test_on:
            return
        if (getattr(self, "_stage", "") != "root" and (compositive is None)):
            raise Exception("The first positional argument of setTaskNodeDetails (compositive) must be set!")

        if (getattr(self, "_stage", "") != "root" and not stage):
            raise Exception("The second positional argument of setTaskNodeDetails (stage) must be set!")

        if compositive is not None:
            self._compositive = compositive

        if stage:
            self._stage = stage

        self._substage = substage

        self._taskData = taskData
        
        if (self._userGoal):
            self._taskData['userGoal'] = self._userGoal

    ## this should be called after all children have been spawned. writing taskNode.close()
    ## is basically a way to assert two things:
    ##
    ## 1) This statement will always be hit before the test is actually run
    ## 2) By the time the statement is hit, taskNode will have all the children it will 
    ## ever have
    ##
    ## The point is to blow up early if children are added to this taskNode in a way 
    ## that's different from what the programmer expected (as opposed to producing
    ## garbled test results)
    def close(self):
        if not test_on:
            return

        if (not hasattr(self, "_taskData")):
            raise Exception("Task data has not been provided for this taskNode. Task data " +
                "must be provided for a node before it can be closed.")

        self._closed = True

    async def _runTest(self, testConfig, llm):
        if not hasattr(self, "_closed"):
            raise Exception(f"A taskNode for stage '{self._stage}', substage '{self._substage}' " +
                "has not been closed. Every taskNode must be closed with _closed before it can " +
                "be tested.")

        for child in self._children:
            await child._runTest(testConfig, llm)

        if self._compositive:
            reasonPrefix = "This node fails if any of its children fail, and"

            if any([not result.succeeded for child._result in self.children]):
                succeeded = False
                reason = f"{reasonPrefix} one or more of its children failed."
            else:
                succeeded = True
                reason = f"{reasonPrefix} none of its children failed."

            self._result = TestResult(succeeded, reason, [], None)
        else:
            auditKey = "-".join([s for s in [self._stage, self._substage] if s])
            auditStages = testConfig["audits"]["stages"]
            auditQuestions = testConfig["audits"]["stages"].get(auditKey, [])

            response = await self._runAudits(self._taskData, auditQuestions, llm)

            # for now, we'll say that the task succeeds if and only if 
            # every audit succeeds. we do ask the LLM to say whether 
            # it thinks the task has succeeded, but that's just to
            # prime it to generate the 'reason' field correctly
            succeeded = all([is_truish(a['success']) for a in response["audits"]])
            reason = response["reason"] if not succeeded else ""

            # TODO(mprast): change this if it ends up being too confusing
            response["success"] = succeeded
            response["reason"] = reason

            self._result = TestResult(succeeded, reason, auditQuestions, response)

        self._tested = True

    async def _runAudits(self, taskData, audits, llm):
        # create the messages format
        input_messages = [
            {
                "role": "system",
                "content": genPrompt(taskData, audits)
            }, {
                "role": "user",
                "content": '<awaiting your next JSON response>'
            }
        ]

        try:
            response = await llm.chat.completions.create(
                model=LLM_MODEL_ID,
                messages=input_messages,
                temperature=0.9,
                response_format={ "type": "json_object" },
            )
            llm_output = json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            llm_output = await json_fixer(response.choices[0].message.content)
        except openai.BadRequestError as e:
            if e.code == 'json_validate_failed':
                llm_output = await json_fixer(e.response.json()['error']['failed_generation'])
            else:
                raise e

        return llm_output

    def toDict(self, simple):
        node_dict = self.__dict__.copy()

        if '_children' in node_dict:
            node_dict['_children'] = [child.toDict(simple) for child in self._children]

        if '_result' in node_dict:
            node_dict['_result'] = self._result.__dict__

        if simple:
            simple_dict = {}
            simple_dict['stage'] = node_dict['_stage']
            simple_dict['taskData'] = node_dict['_taskData']
            simple_dict['succeeded'] = node_dict['_result']['succeeded']
            simple_dict['reason'] = node_dict['_result']['reason']
            simple_dict['audits'] = node_dict['_result']['fullResponse']['audits']
            simple_dict['children'] = node_dict['_children']

            node_dict = simple_dict

        return node_dict 

    def toString(self, simple=False):
        return json.dumps(self.toDict(simple))

class TreeTestRunner():
    def loadConfig(self, path):
        loadedConfig = readYaml(path)
        if "imports" in loadedConfig["audits"]:
            for import_file in loadedConfig["audits"]["imports"]:
                import_config = readYaml(get_sibling_file(path, import_file))
                loadedConfig["audits"] = deep_merge(loadedConfig["audits"], import_config["audits"])

        self._testConfig = loadedConfig

    def trackTest(self, testName, rootCompositive):
        if not hasattr(self, "_testConfig"):
            raise Exception("No test config has been loaded into this TreeTestRunner - " + 
                "please load config using loadConfig before running any tests!")

        if hasattr(self, "root"):
            raise Exception("This TreeTestRunner is already tracking a test by the name of " +
                f"{self._testName} A single runner cannot be used to initialize two tests. " +
                "If you would like to initialize a new test, please create a new " +
                "TreeTestRunner.")

        self._testName = testName
        root = TaskNode(self._testConfig["userGoal"])
        root._stage = "root"
        root._compositive = rootCompositive
        self.root = root
        
        return root

    async def runTest(self):
        if not test_on:
            return

        llm = LLM_CLIENT

        if not hasattr(self, "root"):
            raise Exception("This TreeTestRunner is not currently tracking a test.")

        if hasattr(self, "root") and hasattr(self.root, "_tested"):
            raise Exception("The test tracked by this TreeTestRunner has already been run.")

        await self.root._runTest(self._testConfig, llm)