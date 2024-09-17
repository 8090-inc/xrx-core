---
sidebar_position: 8
---

# Creating your own Widgets

This guide explains how widgets are processed from the agent to the front-end and how you can create your own custom widgets. 

> **Note:** This guide is for the application `Shopify App` however it can be adapted for other applications including any app you write yourself as long as you follow the same pattern and output formats specified below.

## Information Flow Details

### Agent Generation

The agent generates a widget output in the `Widget` class located in the `shopify-app/reasoning/app/agent/graph/nodes/widget.py` file. This method matches the tool used by the agent to a specific widget type and creates a widget output dictionary in the following format:

```python
widget_output = {
    'type': 'widget-type-name',
    'details': json.dumps(tool_output),
    'available-tools': [
        {
            'tool': 'tool-name',
            'arguments': [
                'arg1',
                'arg2',
            ],
        },
    ]
}
```

The 'tool-name' in the 'available-tools' array corresponds to user actions that can be taken on the widget output. These tools represent the next possible actions a user can perform based on the current widget data. These actions are represented as more tools. For example, in a `product_list` tool might spawn a widget which has an `available-tools` array which contains a `view_product_details` tool which the user can click on to view more information about the product.

### Executor Processing

The `run_agent` function in `shopify-app/reasoning/app/agent/executor.py` processes the widget output. It formats the widget data and includes it in the response stream in the following format:

```json
{
    "messages": "<messages from agent>",
    "session": "<session for shopify and front end>",
    "node": "Widget",
    "output": "<widget output from step 1>",
    "reason": "<reason for widget output>"
}
```
It is important to note that this "node": "Widget" key value pair is extremely important to the orchestrator and front-end to know that the output is a widget which must be rendered.

### Orchestrator Handling

The orchestrator (`orchestrator/src/Session.ts`) receives the widget data and passes it to the front-end:

```typescript
if(type === 'Widget') {
    this.server.log.debug(`Received from Agent:${agentResponse}`);
    this.server.log.debug('Not sending to TTS');
    this.textResponse('agent', agentResponse, 'widget');
}
```

`agentResponse` is the response from the "output" key from executor which includes the widget data in JSON format.

### Front-end Rendering

The front-end (`shopify-app/nextjs-client/src/app/page.tsx`) receives the widget data and renders it via a switch statement. The `renderWidget` function processes the widget data and returns the appropriate JSX based on the widget type. For example:

```typescript
switch (widget.type) {
    case 'shopify-product-list':
    return (
        <div className="widget" id="product-list">
        <h2>Products</h2>
        <table>
            <thead>
            <tr>
                <th></th>
                <th>Title</th>
                <th>Options</th>
                <th>Action</th>
            </tr>
            </thead>
            <tbody>
            {Object.entries(details).map(([productId, product]: [string, any]) => (
                <tr key={productId}>
                <td><img src={`https://placehold.co/100x100?text=${encodeURIComponent(product.product_title)}`} alt={product.product_title} /></td>
                <td>{product.product_title}</td>
                <td>{product.options.map((opt: any) => opt.option_title).join(', ')}</td>
                <td>
                    <div className="button-container">
                    {loadingButtons[`details-${productId}`] ? (
                        <HashLoader size={20} color={"#F15950"} />
                    ) : (
                        <button className="widget-button" onClick={(event) => showDetails(event.target, parseInt(productId))}>View Details</button>
                    )}
                    </div>
                </td>
                </tr>
            ))}
            </tbody>
        </table>
        </div>
    );
```

The `details` variable above maps to the `agentResponse` variable from the orchestrator.

## Creating Custom Widgets

To create your own custom widgets, you'll need to modify code in several places:

1. **Agent Widget Generation**:
   In `reasoning/shopify-agent/app/agent/graph/nodes/widget.py`, add a new case to the `match_widget_to_tool` function:

   ```python
   elif tool == 'your_new_tool':
       widget_output = {
           'type': 'your-new-widget-type',
           'details': json.dumps(tool_output),
           'available-tools': [
               {
                   'tool': 'next_possible_tool',
                   'arguments': ['arg1', 'arg2'],
               },
           ]
       }
   ```

2. **Executor Processing**:
   Ensure that the `run_agent` function in `shopify-app/reasoning/app/agent/executor.py` can handle your new widget type. The existing code should work for new widgets as long as they follow the standard format.

3. **Front-end Widget Rendering**:
   In `shopify-app/nextjs-client/src/app/page.tsx`, add a new case to the `renderWidget` function:

   ```typescript
   case 'your-new-widget-type':
     return (
       <div className="widget" id="your-new-widget">
         <h2>Your New Widget</h2>
         <table>
           <thead>
             <tr>
               {/* Add your table headers */}
             </tr>
           </thead>
           <tbody>
             {Object.entries(details).map(([itemId, item]: [string, any]) => (
               <tr key={itemId}>
                 {/* Add your table cells */}
                 <td>
                   <div className="button-container">
                     {loadingButtons[`action-${itemId}`] ? (
                       <HashLoader size={20} color={"#F15950"} />
                     ) : (
                       <button className="widget-button" onClick={(event) => handleAction(event.target, itemId)}>Action</button>
                     )}
                   </div>
                 </td>
               </tr>
             ))}
           </tbody>
         </table>
       </div>
     );
   ```

4. **Add New Tool (if necessary)**:
   If your widget requires a new tool, add it to `shopify-app/reasoning/app/agent/tools/shopify.py`:

   ```python
   @observability_decorator(name="your_new_tool")
   def your_new_tool(arg1: str, arg2: int) -> dict:
       """
       Docstring describing your new tool...
       """
       try:
           # Your tool logic here
           return result_dict
       except Exception as e:
           raise e
   ```

5. **Update Agent Logic (if necessary)**:
   If your widget requires new agent logic, update the relevant files in the `shopify-app/reasoning/app/agent/` directory.

## Using a Custom Reasoning Agent

When using a custom reasoning agent, you can still leverage the existing widget system as long as your agent's output follows the JSON format provided by the executor. This format is crucial for the orchestrator and front-end to properly handle and render the widgets.

To ensure compatibility:

1. Your custom agent should output widget data in the following format:

```json
{
    "messages": "<messages from agent>",
    "session": "<session for shopify and front end>",
    "node": "Widget",
    "output": {
        "type": "your-widget-type",
        "details": "<JSON string of widget details>",
        "available-tools": [
            {
                "tool": "tool-name",
                "arguments": ["arg1", "arg2"]
            }
        ]
    },
    "reason": "<reason for widget output>"
}
```

2. Ensure that the "node" key is set to "Widget" for any widget output. This is crucial for the orchestrator to recognize the output as a widget.

3. The "output" object should contain the widget type, details, and available tools, following the structure shown above.

4. The "tool-name" in the "available-tools" array corresponds to user actions that can be taken on the widget output. These tools represent the next possible actions a user can perform based on the current widget data. For example:

   - In a product list widget, a tool named "view_product_details" might correspond to a "View Details" button for each product.
   - In an order summary widget, a tool named "confirm_order" could map to a "Confirm Order" button.

   When implementing your custom widget in the front-end, you'll need to create appropriate UI elements (like buttons) that trigger these tool actions when clicked.

As long as your custom agent adheres to this format, the existing orchestrator and front-end components will be able to process and render the widgets without requiring additional modifications. This allows for flexibility in creating custom reasoning agents while still leveraging the established widget rendering system.

The mapping between tool names and user actions provides a powerful way to create interactive widgets that can trigger further actions in your agent, allowing for a dynamic and responsive user experience.
