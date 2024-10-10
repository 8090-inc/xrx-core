import logging
import yaml

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

STATE_MACHINE_PROMPT = '''\
A flow is a graph of states that captures a certain interaction the user can have with this app. \
The description of your current flow is:

{current_flow_description}

The following is a description of your current state:

{current_state_description}

Your state captures your current objective; you should do your best to guide the \
conversation towards the objective described by your current state. \
Do not make tool calls or return responses that are inconsistent with your current state. \
Do not attempt to infer your current state apart from the description provided above.
If you have accomplished the objective of your current state, transition to the next 
appropriate state or flow using a tool call.
If the user seems like they want to do something else, you should transition to another \
state or flow, if appropriate.

If the user provides an input unrelated to the current objective, transition to the flow \
that best matches the user's intent. If no flow matches the user's intent, gently guide \
the user back to the current objective.
'''
def readFlowsYaml(file_path):
    with open(file_path, 'r') as file:
        flows_data = yaml.safe_load(file)
    return flows_data


class StateMachine():
    def __init__(self, name, attributes):
        super().__init__(name, attributes)

    @staticmethod
    def initStateMachineSessionData(session_data):
        smsd = {
            'flows': {},
            'currentFlow': '',
            'currentState': ''
        }

        session_data['stateMachine'] = smsd

        file_path = 'agent/flows.yaml'
        flows = readFlowsYaml(file_path)['flows']

        smsd['flows'] = flows
        smsd['currentFlow'] = ([flow for flow in flows if flows[flow].get('initial') == True])[0]

        states = flows[smsd['currentFlow']]['states']
        smsd['currentState'] = ([state for state in states if states[state].get('initial') == True])[0]

    @staticmethod
    def getStateMachinePrompt(input_dict):
        flows = input_dict['stateMachine']['flows']
        current_flow = input_dict['stateMachine']['currentFlow']

        states = flows[current_flow]['states']
        current_state = input_dict['stateMachine']['currentState']

        return STATE_MACHINE_PROMPT.format(
            current_flow_description=flows[current_flow]['description'],
            current_state_description=states[current_state]['description']
        )

    @staticmethod
    def getStateMachineTransitionCalls(input_dict):
        tool_calls = []

        flows = input_dict['stateMachine']['flows']
        current_flow = input_dict['stateMachine']['currentFlow']

        states = flows[current_flow]['states']
        current_state = states[input_dict['stateMachine']['currentState']]

        # generate tool calls for all the transitions out of the current state
        for target_state in current_state.get('transitions', []):
            description = f"Transition to the '{target_state}' state. " + \
                f"The new state's description is '{states[target_state]['description']}'"
            tool_calls.append(f"* state_transition_{target_state}: {description}")

        # generate tool calls to skip to the start of another flow
        for flow in flows:
            if flow != current_flow:
                description = f"Stop executing the current flow and start the '{flow}' flow instead. " + \
                    f"The new flow's description is '{flows[flow]['description']}'"
                tool_calls.append(f"* flow_transition_{flow}: {description}")

        return ''.join([f"{s}\n" for s in tool_calls])

    @staticmethod
    def executeStateTransition(input_dict, new_state):
        sm = input_dict['stateMachine']
        sm['currentState'] = new_state

    @staticmethod
    def executeFlowTransition(input_dict, new_flow):
        sm = input_dict['stateMachine']
        sm['currentFlow'] = new_flow

        flows = sm['flows']
        states = flows[new_flow]['states'] 
        sm['currentState'] = ([state for state in states if states[state].get('initial') == True])[0]