"""
A wrapper for lwfm workflow programming exposed as MCP tooling for interaction
in an LLM-driven agentic environment. 
"""

#pylint: disable = invalid-name, missing-function-docstring

from typing import List


from mcp.server.fastmcp.prompts.base import UserMessage
import mcp.server.stdio
from mcp.server.fastmcp import FastMCP

from lwfm.base.Workflow import Workflow
from lwfm.base.Site import Site
from lwfm.base.JobDefn import JobDefn


# ******************************************************************************
# Prompts, for the system, and for specific steps.

# Intended to be fed to the LLM as a "system prompt" describing this bundle
# of tooling holistically.
SERVICE_SYSTEM_PROMPT = """
<mcp>

Prompts:
- end_to_end_quantum_workflow 

<instructions>
You are an AI assistant tasked with helping a scientific research user construct and
execute distributed workflows. To help with access to remote compute system and for tracking these workflows to completion we utilize the lwfm library. The lwfm framework exposes a Site which provides mechanisms to autenticate against the remote Site servcie, to run jobs on the remote site and track their progress, and to manage the data produced and consumed by these jobs. Parent-child relationships between jobs are enabled and tracked - using lwfm we can set a job to run when its upstream parent completes.

For reference, lwfm is located at: https://github.com/lwfm-proj/lwfm/tree/develop 

For now, we will limit the scope of the use of lwfm by:
    - focusing only a local Site
    - since we're only using the Local site, we don't need to worry so much about authentication
    - not concerning ourselves with data management or tracking of data consumed and produced by jobs

For now we will focus on the Run functions of the Local Site.

The Site Run subsystem exposes a submit() method which takes a job definion (JobDefn) which primarily contains the entry point, which is any arbitrary command line, and a set of arguments. The submit() takes a JobContext, which can refer to a Workflow, or if this is the seminal invocation for this workflow, a bare Workflow can be passed in. A JobStatus is returned, indicating the initial status of the job. The Site then executes the JobDefn, emitting further JobStatus messages until a terminal status is reached.

In the context of the Workflow the user can also set job events which trigger on a certain job reaching a certain job status / state. When the criterium are met, the registered job definition is run on the target Site. Thus asynchronous chains of jobs are realized. The LwfManager exposes the method to set the job event handlers, as well as other utility functions.

As an AI asssitant, you will help perform the following:

0. Ensure the lwfm middleware is running. This middleware holds the event handlers and provides an interface for persistence (e.g. logging). The middleware exposes an HTTP endpoint which the LwfManager utilizes. To run the middleware on Windows, execute lwfm.ps1, and on Mac or Linux, execute lwfm.sh.

1. Engage with the user to initiate a new workflow, gathering from the user:
    a. An optional name.
    b. A description the workflow in enough detail to be able to automatically generate the necessary workflow code from the description.
    c. Any other metadata about the workflow, for example a project id or other user-specifed properties of the workflow, if any.

2. With the description, construct an appropriate workflow using the lwfm library and save
    the workflow to a folder named by the workflow id. 

3. Run the workflow by invoking the lwfm Run subsystem for the Local Site.

</instructions>
</mcp>
"""


# ******************************************************************************
# define MCP tools & prompts

# Create an MCP server instance and pass it high level guidance.
mcp = FastMCP(name="lwfm-server", instructions=SERVICE_SYSTEM_PROMPT)


@mcp.tool()
def initiate_workflow(name: str, description: str = None, metadata: dict = None) -> str:
    """
    Make a new workflow, give it a name, and provide a natural language
    description of what it intends to do. Add other optional metadata.
    Return the workflow id.
    """
    wf = Workflow(name, description)
    wf.setProps(metadata)
    return wf.getWorkflowId()

@mcp.tool()
def run_workflow(entryPoint: str, jobArgs: List[str] = None) -> str:
    """
    Run the workflow.
    """
    site = Site.getSite("local")
    site.getAuthDriver().login()
    jobDefn = JobDefn(entryPoint)
    jobDefn.setJobArgs(jobArgs)
    status = site.getRunDriver().submit(jobDefn)
    return status.getStatus()



@mcp.prompt()
def end_to_end_workflow(name: str, description: str = None) -> str:
    """
    Generates a user prompt to initiate an end to end quantum circuit 
    workflow on a target backend quantum computing platform which might be a 
    local simulator or a remote quantum computer.
    """
    MSG = f"""
    0. Make sure the lwfm middleware is running
    1. Make a new workflow called {name} which conceptually is described
    as follows: {description} and get its workflow id.
    2. With the description, construct an appropriate python script using lwfm and save
    it to a folder named by the workflow id. 
    3. Run the script.
    """
    return UserMessage(content=MSG)


# ******************************************************************************
# Run the MCP server, which listens for requests via standard input/output.

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')


# ******************************************************************************
