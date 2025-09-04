# Hypermindz Crew

Welcome to the **Hypermindz Crew** project, powered by [crewAI](https://crewai.com). This template is developed and maintained by **Hypermindz** to streamline the creation and management of AI agents for our **Agent Registry Platform**. It provides a solid foundation for building multi-agent AI systems, enabling agents to collaborate on complex tasks through a powerful, extensible framework.

## Installation

Ensure you have Python >=3.10 <=3.13 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling, offering a seamless setup and execution experience.

First, if you haven't already, install uv:

```bash
pip install uv
```

Next, navigate to your project directory and install the dependencies:

```bash
uv sync
```

Then activate the virtual environment:

- **On Windows:**

  ```bash
  .venv\Scripts\activate
  ```

- **On Linux/macOS:**

  ```bash
  source .venv/bin/activate
  ```

## Setup

Before running the project, make sure to:

1. **Add your `OPENAI_API_KEY` to a `.env` file** in the project root directory. This is necessary for the agents to interact with OpenAI models.

```env
OPENAI_API_KEY=your_openai_key_here
```

2. (Optional) You can also define any other environment variables required by your agents or tools in this file.

## Customizing

You can fully customize your crew:

- Modify `src/hypermindz/config/agents.yaml` to define your agents
- Modify `src/hypermindz/config/tasks.yaml` to define your tasks
- Modify `src/hypermindz/crew.py` to add your own logic, tools, and specific arguments
- Modify `src/hypermindz/main.py` to add custom inputs for your agents and tasks
- **Create custom tools** and integrate them into your agents via `crew.py` for expanded capabilities

## Running the Project

To kickstart your crew of AI agents and begin task execution, run this from the root folder of your project:

```bash
crewai run
```

This command initializes the Hypermindz Crew, assembling the agents and assigning them tasks as defined in your configuration.

This example, unmodified, will create a `report.md` file in the root folder with the results of a research task on LLMs.

## Understanding Your Crew

The Hypermindz Crew is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks defined in `config/tasks.yaml`, leveraging their collective skills to accomplish complex objectives. The `config/agents.yaml` file outlines the capabilities and configurations of each agent.

## Support

For support, questions, or feedback regarding the Hypermindz Crew or crewAI:
- Visit our [documentation](https://agenticregistry.ai/docs)
- Visit our [website](https://agenticregistry.ai)
- 

Let’s create wonders together with the power and simplicity of Hypermindz.
