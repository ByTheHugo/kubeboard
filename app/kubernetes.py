from logging import Logger
from os import getenv
from kubernetes import client, config
from typing import List, Dict


def _k8s_filter_annotations(annotations: Dict, prefix: str) -> Dict:
    annotations_cleaned = {}
    for key, value in annotations.items():
        if key.startswith(prefix):
            annotations_cleaned[key] = value
    return annotations_cleaned


def k8s_load_config(logger: Logger) -> None:
    if getenv("KUBERNETES_SERVICE_HOST"):  # pragma: no cover
        logger.debug("Loading in-cluster Kubernetes configuration")
        config.load_incluster_config()
    else:
        logger.debug("Loading Kubernetes configuration from kubeconfig")
        config.load_kube_config()


def k8s_get_ingresses(
    logger: Logger,
    prefix: str,
    default_icon: str,
    hide_by_default=False,
    namespace=None,
) -> List[Dict]:
    # Use appropriated Kubernetes API
    networking_v1_api = client.NetworkingV1Api()

    # Retrieve Ingresses in specific namespace if specified
    ingresses_raw_list = []
    if namespace:
        logger.debug("Retrieving ingresses from namespace {}".format(namespace))
        ingresses_raw_list = networking_v1_api.list_namespaced_ingress(
            namespace=namespace
        )
    else:
        logger.debug("Retrieving ingresses from all namespaces")
        ingresses_raw_list = networking_v1_api.list_ingress_for_all_namespaces()

    # Format API output to facilitate utilization
    ingresses_list = []
    for ingress in ingresses_raw_list.items:
        # Validate that ingress is defining at least a rule
        if len(ingress.spec.rules) <= 0:  # pragma: no cover
            continue

        # Filter ingress annotations
        annotations_cleaned = _k8s_filter_annotations(
            ingress.metadata.annotations, prefix
        )

        # If we hide all ingresses by default and we didn't specify the "show" annotation, we skip the ingress
        if hide_by_default and not f"{prefix}/show" in annotations_cleaned:
            continue
        # If the "show" annotation isn't true , we skip the ingress
        if (
            f"{prefix}/show" in annotations_cleaned
            and annotations_cleaned[f"{prefix}/show"] == "false"
        ):
            continue

        # Append formatted ingress object
        ingresses_list.append(
            {
                "name": (
                    ingress.metadata.name
                    if f"{prefix}/name" not in annotations_cleaned
                    else annotations_cleaned[f"{prefix}/name"]
                ),
                "namespace": ingress.metadata.namespace,
                "annotations": annotations_cleaned,
                "url": ingress.spec.rules[0].host,
                "icon": (
                    default_icon
                    if f"{prefix}/icon" not in annotations_cleaned
                    else annotations_cleaned[f"{prefix}/icon"]
                ),
            }
        )

    # We sort ingresses to facilitate visualization
    ingresses_list = sorted(ingresses_list, key=lambda x: x["name"])

    # Finally return ingresses with some debug logs
    logger.debug(ingresses_list)
    return ingresses_list
