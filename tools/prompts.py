# library of mcp prompt templates that guide the agent through common docker workflows

from server import mcp


@mcp.prompt(description="Read the Docker SDK for Python documentation for a section before writing code that uses it.")
def lookup_docker_docs(section: str) -> str:
    """
    Ask the agent to consult the Docker SDK for Python documentation for a specific section.

    args: section: str - SDK section name (e.g. "containers", "images", "swarm")
    returns: str - A prompt instructing the agent to read the docker-docs resource and summarize the API
    """
    return (
        f"Read the MCP resource `docker-docs://{section}` and summarize the public methods, their signatures, "
        f"and return types. Highlight anything that is easy to misuse (parameters that look similar, surprising "
        f"defaults, methods that return iterators vs. lists). Do not assume any method exists unless it is "
        f"present in that resource."
    )


@mcp.prompt(description="Verify that a specific Docker SDK method exists before relying on it.")
def verify_docker_method(method: str, section: str) -> str:
    """
    Ask the agent to verify a method of the `docker` module against the live SDK docs.

    args: method: str - The method name to verify (e.g. "containers.run")
    args: section: str - The SDK section to check (e.g. "containers")
    returns: str - A prompt instructing the agent to confirm the method's signature from the docs
    """
    return (
        f"Read the MCP resource `docker-docs://{section}` and confirm whether `{method}` exists. "
        f"If it does, quote its full signature, list each parameter with its type, and describe the return value. "
        f"If it does not exist, say so explicitly and suggest the closest documented alternative."
    )


@mcp.prompt(description="Deploy a containerized application end-to-end: image, network, volume, container.")
def deploy_container(image: str, name: str) -> str:
    """
    Generate a step-by-step plan for deploying a container with supporting resources.

    args: image: str - The image reference to deploy (e.g. "nginx:1.27")
    args: name: str - The container name to assign
    returns: str - A prompt instructing the agent to walk through deployment using the MCP tools
    """
    return (
        f"Deploy the image `{image}` as a container named `{name}` using the docker MCP tools. Follow this order:\n"
        f"1. Call `pull_image` to ensure the image is present locally.\n"
        f"2. Decide whether the workload needs a dedicated network or named volume; create them with "
        f"`create_network` / `create_volume` if so.\n"
        f"3. Call `run_container` with sensible defaults: `detach=True`, a restart policy, and any port or volume "
        f"mappings the image requires.\n"
        f"4. Verify the container reached the running state with `list_containers` and `container_logs`.\n"
        f"Report the final container ID and any resources you created. Stop and ask before destroying existing "
        f"resources that share the same name."
    )


@mcp.prompt(description="Troubleshoot a misbehaving container by gathering logs, state, and stats.")
def troubleshoot_container(container: str) -> str:
    """
    Generate a diagnostic plan for an unhealthy or failing container.

    args: container: str - Container name or ID to investigate
    returns: str - A prompt instructing the agent to gather logs, inspect state, and propose a fix
    """
    return (
        f"Diagnose what is wrong with container `{container}`:\n"
        f"1. Use `get_container` to read its current state, exit code, and restart count.\n"
        f"2. Use `container_logs` (with `tail=200`) to capture recent stdout/stderr.\n"
        f"3. If the container is running, use `container_stats` for CPU/memory pressure and `container_top` "
        f"for the process tree.\n"
        f"4. If a config file or process check is needed, use `exec_in_container`.\n"
        f"Summarize the root cause in one paragraph, then propose a concrete fix (config change, image bump, "
        f"resource limit) before making any changes."
    )


@mcp.prompt(description="Replace a running container with a new image while preserving its configuration.")
def migrate_container(container: str, new_image: str) -> str:
    """
    Generate a plan for swapping a container's image without losing its configuration.

    args: container: str - Existing container name or ID
    args: new_image: str - The new image reference to deploy
    returns: str - A prompt instructing the agent to perform a safe migration
    """
    return (
        f"Migrate container `{container}` to image `{new_image}` without losing its configuration:\n"
        f"1. Use `get_container` to capture the current name, env vars, mounts, ports, network, and restart "
        f"policy.\n"
        f"2. Use `pull_image` to fetch `{new_image}`.\n"
        f"3. Use `stop_container` followed by `remove_container` on the old container.\n"
        f"4. Use `run_container` to start a new container with the captured config but the new image.\n"
        f"5. Verify with `list_containers` and `container_logs` that the replacement is healthy.\n"
        f"Show the captured config back to the user before recreating the container."
    )


@mcp.prompt(description="Reclaim disk space by pruning unused docker resources.")
def clean_environment(scope: str = "stopped") -> str:
    """
    Generate a plan for safely pruning unused docker resources.

    args: scope: str - "stopped" (default) for containers + dangling images, or "all" to also prune networks and volumes
    returns: str - A prompt instructing the agent to inventory and prune unused resources
    """
    base = (
        "Reclaim docker disk usage safely:\n"
        "1. Use `df` to show current disk usage so the user sees a before/after.\n"
        "2. Use `prune_containers` to remove stopped containers.\n"
        "3. Use `prune_images` (without `filters={'dangling': False}`) to remove dangling images only.\n"
    )
    if scope == "all":
        base += (
            "4. Use `prune_networks` to remove unused user-defined networks.\n"
            "5. Use `prune_volumes` ONLY after explicitly confirming with the user — volumes can hold "
            "irreplaceable data.\n"
        )
    base += "Report the total space reclaimed at the end."
    return base


@mcp.prompt(description="Inspect every docker resource that shares a label.")
def inspect_stack(label: str) -> str:
    """
    Generate a plan for inspecting all resources tagged with a given label.

    args: label: str - Label key or key=value pair to filter on (e.g. "com.example.app=web")
    returns: str - A prompt instructing the agent to enumerate containers, networks, and volumes by label
    """
    return (
        f"Enumerate every docker resource carrying the label `{label}`:\n"
        f"1. `list_containers(all=True, filters={{'label': '{label}'}})` for containers.\n"
        f"2. `list_networks(filters={{'label': '{label}'}})` for networks.\n"
        f"3. `list_volumes(filters={{'label': '{label}'}})` for volumes.\n"
        f"Render the result as a single table grouped by resource type, with name, ID, and creation time. "
        f"Do not modify anything."
    )


@mcp.prompt(description="Plan a multi-container application from an informal description.")
def plan_compose_stack(description: str) -> str:
    """
    Generate a plan for translating an informal app description into docker resources.

    args: description: str - Free-form description of the app to deploy (e.g. "wordpress + mysql with a shared volume")
    returns: str - A prompt instructing the agent to design and deploy the stack with MCP tools
    """
    return (
        f"Design a multi-container deployment for: {description}\n\n"
        f"First, before calling any tool, produce a plan that lists:\n"
        f"- Each container (image, name, role, exposed ports)\n"
        f"- Networks (name, driver, which containers attach)\n"
        f"- Volumes (name, mount path inside each container)\n"
        f"- Any required env vars or secrets (use `create_secret` for swarm, env for plain containers)\n"
        f"- Startup order if dependencies exist\n\n"
        f"Wait for the user to approve the plan, then create the resources in dependency order using "
        f"`create_network`, `create_volume`, `pull_image`, and `run_container`. End with `list_containers` "
        f"showing the running stack."
    )
