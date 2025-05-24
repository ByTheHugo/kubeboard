from dotenv import load_dotenv

load_dotenv(".flaskenv")

import pytest
from app.kubernetes import k8s_load_config, k8s_get_ingresses, _k8s_filter_annotations
from os import environ
from conftest import ANNOTATIONS_TO_TEST, KUBERNETES_INGRESSES_NAMESPACE


def TP_validate_kubernetes_connectivity(logger):
    logger.info(
        "Validating that the Kubernetes API can be reached using the k8s_load_config function..."
    )
    k8s_load_config(logger)
    logger.info("Kubernetes API is accessible.")


def TP_validate_annotations_filtering(logger):
    logger.info(
        "Validating that annotations are correctly filtered using the _k8s_filter_annotations function..."
    )

    annotations = _k8s_filter_annotations(
        ANNOTATIONS_TO_TEST, environ["FLASK_K8S_ANNOTATION_PREFIX"]
    )
    for key in annotations:
        logger.debug(f"Validating annotation: {key}={annotations[key]}...")
        assert (
            annotations[key] == "success"
        ), f"Annotation not correctly filtered: {key}={annotations[key]}!"

    logger.info("All annotations was successfully filtered.")


def TP_validate_ingresses_retrieval(logger, config):
    logger.info(
        "Validating that ingresses can be retrieved using the k8s_get_ingresses function..."
    )

    # Validate that the ingresses can be retrieved successful
    ingresses = k8s_get_ingresses(
        logger,
        environ["FLASK_K8S_ANNOTATION_PREFIX"],
        config["theme"]["defaultIcons"]["ingress"],
    )
    assert len(ingresses) > 0, "No ingresses was retrieved!"
    logger.info(f"Fetched {len(ingresses)} ingress(es) from Kubernetes API.")

    # Validate that the ingresses retrieved doesn't have a "show" annotation to false
    for ingress in ingresses:
        logger.debug(
            f"Validating ingress {ingress['name']} annotations: {ingress['annotations']}"
        )

        assert (
            "annotations" in ingress
        ), f"Annotations key not found in ingress {ingress['name']}!"

        if f"{environ["FLASK_K8S_ANNOTATION_PREFIX"]}/show" in ingress["annotations"]:
            assert ingress["annotations"][
                f"{environ["FLASK_K8S_ANNOTATION_PREFIX"]}/show"
            ], f"Ingress {ingress['name']} must not be retrieved (explicit annotation)!"

    logger.info(f"All ingress(es) annotations was successfully evaluated.")


def TP_validate_ingresses_retrieval_by_namespace(logger, config):
    logger.info(
        "Validating that ingresses for a specified namespace can be retrieved using the k8s_get_ingresses function..."
    )

    # Validate that the ingresses can be retrieved successful
    ingresses = k8s_get_ingresses(
        logger,
        environ["FLASK_K8S_ANNOTATION_PREFIX"],
        config["theme"]["defaultIcons"]["ingress"],
        namespace=KUBERNETES_INGRESSES_NAMESPACE,
    )
    assert len(ingresses) > 0, "No ingresses was retrieved!"
    logger.info(f"Fetched {len(ingresses)} ingress(es) from Kubernetes API.")

    # Validate that the ingresses retrieved are in the specified namespace only
    for ingress in ingresses:
        logger.debug(
            f"Validating ingress {ingress['name']} namespace: {ingress['namespace']}"
        )
        assert (
            "namespace" in ingress
        ), f"Namespace key not found in ingress {ingress['name']}!"
        assert (
            ingress["namespace"] == KUBERNETES_INGRESSES_NAMESPACE
        ), f"Ingress {ingress['name']} is not in namespace {KUBERNETES_INGRESSES_NAMESPACE}!"


def TP_validate_ingresses_hidden_by_default_retrieval(logger, config):
    logger.info(
        "Validating that ingresses hidden by default can be retrieved using the k8s_get_ingresses function..."
    )

    ingresses = k8s_get_ingresses(
        logger,
        environ["FLASK_K8S_ANNOTATION_PREFIX"],
        config["theme"]["defaultIcons"]["ingress"],
        True,
    )
    if not len(ingresses):  # pragma: no cover
        pytest.skip("No ingress was retrieved, skipping...")

    logger.info(f"Fetched {len(ingresses)} ingress(es) from Kubernetes API.")

    # Validate that the ingresses retrieved are explicitly exposed
    for ingress in ingresses:
        logger.debug(
            f"Validating ingress {ingress['name']} annotations: {ingress['annotations']}"
        )

        assert (
            "annotations" in ingress
        ), f"Annotations key not found in ingress {ingress['name']}!"
        assert (
            f"{environ["FLASK_K8S_ANNOTATION_PREFIX"]}/show" in ingress["annotations"]
        ), f"Show annotation not found in ingress {ingress['name']}!"
        assert (
            ingress["annotations"][f"{environ["FLASK_K8S_ANNOTATION_PREFIX"]}/show"]
            == "true"
        ), f"Ingress {ingress['name']} must not be retrieved (explicit annotation)!"

    logger.info(f"All ingress(es) annotations was successfully evaluated.")
