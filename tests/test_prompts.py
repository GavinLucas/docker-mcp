from tools.prompts import (
    clean_environment,
    deploy_container,
    inspect_stack,
    lookup_docker_docs,
    migrate_container,
    plan_compose_stack,
    troubleshoot_container,
    verify_docker_method,
)


def test_lookup_docker_docs_references_resource_uri():
    out = lookup_docker_docs("containers")
    assert "docker-docs://containers" in out
    assert "summarize" in out.lower()


def test_verify_docker_method_includes_method_and_section():
    out = verify_docker_method("containers.run", "containers")
    assert "containers.run" in out
    assert "docker-docs://containers" in out


def test_deploy_container_lists_steps_in_order():
    out = deploy_container("nginx:1.27", "web")
    assert "nginx:1.27" in out
    assert "web" in out
    assert out.index("pull_image") < out.index("run_container")
    assert "list_containers" in out


def test_troubleshoot_container_covers_logs_and_state():
    out = troubleshoot_container("api-1")
    assert "api-1" in out
    for tool in ("get_container", "container_logs", "container_stats", "exec_in_container"):
        assert tool in out


def test_migrate_container_preserves_config():
    out = migrate_container("api-1", "myorg/api:v2")
    assert "api-1" in out
    assert "myorg/api:v2" in out
    assert out.index("get_container") < out.index("stop_container")
    assert out.index("stop_container") < out.index("remove_container")
    assert out.index("remove_container") < out.index("run_container")


def test_clean_environment_default_scope_skips_volumes():
    out = clean_environment()
    assert "prune_containers" in out
    assert "prune_images" in out
    assert "prune_volumes" not in out


def test_clean_environment_all_scope_includes_volumes_with_warning():
    out = clean_environment("all")
    assert "prune_volumes" in out
    assert "confirm" in out.lower()


def test_inspect_stack_filters_by_label_across_resource_types():
    out = inspect_stack("com.example.app=web")
    assert "com.example.app=web" in out
    for tool in ("list_containers", "list_networks", "list_volumes"):
        assert tool in out
    assert "do not modify" in out.lower()


def test_plan_compose_stack_requires_plan_before_actions():
    out = plan_compose_stack("wordpress with mysql")
    assert "wordpress with mysql" in out
    assert out.index("plan") < out.index("create_network")
    assert "approve" in out.lower()
