from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
OUTPUT_PATH = ROOT_DIR / "src" / "assets" / "graph_table_data.json"


def _load_json(path: Path) -> dict[str, Any]:
	with path.open("r", encoding="utf-8") as file:
		return json.load(file)


def _parse_mapping_block(raw_text: str, var_name: str) -> dict[int, str]:
	block_match = re.search(rf"{re.escape(var_name)}\s*=\s*\{{(.*?)\}}", raw_text, re.S)
	if not block_match:
		raise ValueError(f"Can not find mapping block for {var_name}")

	block = block_match.group(1)
	entries = re.findall(r"(\d+)\s*:\s*\"([^\"]+)\"", block)
	return {int(key): value for key, value in entries}


def _parse_node_edge_defs(path: Path) -> tuple[dict[int, str], dict[int, str]]:
	with path.open("r", encoding="utf-8") as file:
		content = file.read()

	node_type_dict = _parse_mapping_block(content, "node_type_dict")
	edge_relation_dict = _parse_mapping_block(content, "edge_relation_dict")
	return node_type_dict, edge_relation_dict


def _parse_graph_structure(
	graph_structure_data: list[str],
	node_type_dict: dict[int, str],
	edge_relation_dict: dict[int, str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, str], dict[str, int]]:
	nodes: list[dict[str, Any]] = []
	edges: list[dict[str, Any]] = []
	node_type_by_id: dict[str, str] = {}
	node_type_code_by_id: dict[str, int] = {}

	for line in graph_structure_data:
		parts = line.strip().split()
		if len(parts) < 4 and (not parts or parts[0] != "v"):
			continue

		if parts[0] == "v" and len(parts) >= 3:
			node_id = parts[1]
			type_code = int(parts[2])
			type_name = node_type_dict.get(type_code, f"UNKNOWN_{type_code}")
			node_type_by_id[node_id] = type_name
			node_type_code_by_id[node_id] = type_code

			nodes.append(
				{
					"id": node_id,
					"type_code": type_code,
					"type_name": type_name,
					"display_name": f"{node_id}: {type_name}",
					"tooltip": [
						f"node_id: {node_id}",
						f"type_code: {type_code}",
						f"type_name: {type_name}",
					],
				}
			)

		if parts[0] == "e" and len(parts) >= 4:
			source = parts[1]
			target = parts[2]
			type_code = int(parts[3])
			relation = edge_relation_dict.get(type_code, f"UNKNOWN_{type_code}")

			edges.append(
				{
					"source": source,
					"target": target,
					"type_code": type_code,
					"relation": relation,
					"tooltip": [
						f"source: {source}",
						f"target: {target}",
						f"type_code: {type_code}",
						f"relation: {relation}",
					],
				}
			)

	return nodes, edges, node_type_by_id, node_type_code_by_id


def _build_instance_graph(
	subgraph_id: int,
	instance: dict[str, Any],
	base_edges: list[dict[str, Any]],
	node_type_by_id: dict[str, str],
	node_type_code_by_id: dict[str, int],
) -> tuple[str, dict[str, Any]]:
	mapped_vertex_data = instance.get("mapped_vertex_data", {})

	nodes: list[dict[str, Any]] = []
	for node_id in sorted(mapped_vertex_data.keys(), key=lambda item: int(item)):
		value = mapped_vertex_data[node_id]
		node_name = value.get("name", node_id)
		node_path = value.get("id", "")
		type_name = node_type_by_id.get(node_id, "UNKNOWN")
		type_code = node_type_code_by_id.get(node_id, -1)

		nodes.append(
			{
				"id": str(node_id),
				"display_name": f"{node_id}: {type_name}",
				"type_name": type_name,
				"type_code": type_code,
				"tooltip": [
					f"name: {node_name}",
					f"id: {node_path}",
					f"type_name: {type_name}",
					f"type_code: {type_code}",
				],
			}
		)

	instance_key = (
		f"{subgraph_id}:{instance.get('graph_id', -1)}:{instance.get('instance_id', -1)}"
	)

	chart_payload = {
		"title": (
			f"Instance {instance.get('instance_id', '-')}, "
			f"Graph {instance.get('graph_id', '-')}, "
			f"Subgraph {subgraph_id}"
		),
		"categories": sorted({node["type_name"] for node in nodes}),
		"nodes": nodes,
		"edges": base_edges,
	}
	return instance_key, chart_payload


def build_output() -> dict[str, Any]:
	frequent_subgraphs_json = _load_json(DATA_DIR / "frequent_subgraphs.json")
	graphs_json = _load_json(DATA_DIR / "graphs.json")
	node_type_dict, edge_relation_dict = _parse_node_edge_defs(DATA_DIR / "node_edge_defs.txt")

	frequent_subgraphs = frequent_subgraphs_json.get("frequent_subgraphs", [])
	graphs = graphs_json.get("graphs", [])
	graph_page_by_id = {item.get("graph_id"): item.get("page_path", "") for item in graphs}

	table_rows: list[dict[str, Any]] = []
	subgraph_charts: dict[str, Any] = {}
	instance_charts: dict[str, Any] = {}

	for subgraph in frequent_subgraphs:
		subgraph_id = subgraph.get("subgraph_id")
		support = subgraph.get("support")
		structure_analysis = subgraph.get("structure_analysis", "")
		graph_structure_data = subgraph.get("graph_structure_data", [])

		base_nodes, base_edges, node_type_by_id, node_type_code_by_id = _parse_graph_structure(
			graph_structure_data,
			node_type_dict,
			edge_relation_dict,
		)

		subgraph_charts[str(subgraph_id)] = {
			"title": f"Subgraph {subgraph_id}",
			"categories": sorted({node["type_name"] for node in base_nodes}),
			"nodes": base_nodes,
			"edges": base_edges,
		}

		instances = subgraph.get("instances", [])
		instance_lookup = {
			(item.get("graph_id"), item.get("instance_id")): item for item in instances
		}

		cluster_children: list[dict[str, Any]] = []
		clusters = (
			subgraph.get("domain_semantic_clusters", {})
			.get("clusters", {})
		)
		for cluster_key, cluster_instances in clusters.items():
			instance_rows: list[dict[str, Any]] = []
			for brief_instance in cluster_instances:
				graph_id = brief_instance.get("graph_id")
				instance_id = brief_instance.get("instance_id")
				domain_label = brief_instance.get("domain_label", "")
				instance = instance_lookup.get((graph_id, instance_id), {})
				page_path = graph_page_by_id.get(graph_id) or instance.get("page_path", "")

				if instance:
					instance_key, instance_chart_payload = _build_instance_graph(
						int(subgraph_id),
						instance,
						base_edges,
						node_type_by_id,
						node_type_code_by_id,
					)
					instance_charts[instance_key] = instance_chart_payload

				instance_rows.append(
					{
						"row_id": f"subgraph-{subgraph_id}-cluster-{cluster_key}-instance-{graph_id}-{instance_id}",
						"row_type": "instance",
						"group_name": f"Cluster {cluster_key}",
						"subgraph_id": subgraph_id,
						"instance_id": instance_id,
						"graph_id": graph_id,
						"support": "",
						"domain_label": domain_label,
						"page_path": page_path,
						"structure_analysis": "",
						"visualization": {
							"kind": "instance",
							"key": f"{subgraph_id}:{graph_id}:{instance_id}",
						},
					}
				)

			cluster_children.append(
				{
					"row_id": f"subgraph-{subgraph_id}-cluster-{cluster_key}",
					"row_type": "cluster",
					"group_name": f"Cluster {cluster_key}",
					"subgraph_id": subgraph_id,
					"instance_id": "",
					"graph_id": "",
					"support": "",
					"domain_label": "",
					"page_path": "",
					"structure_analysis": "",
					"visualization": None,
					"children": instance_rows,
				}
			)

		table_rows.append(
			{
				"row_id": f"subgraph-{subgraph_id}",
				"row_type": "subgraph",
				"group_name": "",
				"subgraph_id": subgraph_id,
				"instance_id": "",
				"graph_id": "",
				"support": support,
				"domain_label": "",
				"page_path": "",
				"structure_analysis": structure_analysis,
				"visualization": {
					"kind": "subgraph",
					"key": str(subgraph_id),
				},
				"children": cluster_children,
			}
		)

	return {
		"meta": {
			"generated_at": datetime.now(timezone.utc).isoformat(),
			"subgraph_count": len(table_rows),
		},
		"table_rows": table_rows,
		"charts": {
			"subgraphs": subgraph_charts,
			"instances": instance_charts,
		},
	}


def main() -> None:
	output = build_output()
	OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
	with OUTPUT_PATH.open("w", encoding="utf-8") as file:
		json.dump(output, file, ensure_ascii=False, indent=2)

	print(f"Wrote: {OUTPUT_PATH}")


if __name__ == "__main__":
	main()
