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
						# f"type_code: {type_code}",
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
						# f"type_code: {type_code}",
						f"relation: {relation}",
					],
				}
			)

	return nodes, edges, node_type_by_id, node_type_code_by_id


def _build_instance_graph(
	mode: str,
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
					# f"type_code: {type_code}",
				],
			}
		)

	instance_key = (
		f"{mode}:{subgraph_id}:{instance.get('graph_id', -1)}:{instance.get('instance_id', -1)}"
	)

	chart_payload = {
		"title": (
			f"{mode.title()} Cluster {subgraph_id} - "
			f"Instance {instance.get('instance_id', '-')}, "
			f"Graph {instance.get('graph_id', '-')}"
		),
		"categories": sorted({node["type_name"] for node in nodes}),
		"nodes": nodes,
		"edges": base_edges,
	}
	return instance_key, chart_payload


def _split_page_path(page_path: str) -> tuple[str, str, str]:
	parts = [item for item in str(page_path).split("/") if item]
	project = parts[0] if len(parts) > 0 else ""
	module = parts[1] if len(parts) > 1 else ""
	page = parts[2] if len(parts) > 2 else ""
	return project, module, page


def _build_cluster_rows(
	mode: str,
	clusters: list[dict[str, Any]],
	node_type_dict: dict[int, str],
	edge_relation_dict: dict[int, str],
	subgraph_charts: dict[str, Any],
	instance_charts: dict[str, Any],
) -> list[dict[str, Any]]:
	rows: list[dict[str, Any]] = []

	for subgraph in clusters:
		subgraph_id = int(subgraph.get("subgraph_id", -1))
		graph_structure_data = subgraph.get("graph_structure_data", [])
		instances = subgraph.get("instances", [])

		base_nodes, base_edges, node_type_by_id, node_type_code_by_id = _parse_graph_structure(
			graph_structure_data,
			node_type_dict,
			edge_relation_dict,
		)

		subgraph_key = f"{mode}:{subgraph_id}"
		subgraph_charts[subgraph_key] = {
			"title": f"{mode.title()} Cluster {subgraph_id}",
			"categories": sorted({node["type_name"] for node in base_nodes}),
			"nodes": base_nodes,
			"edges": base_edges,
		}

		instance_rows: list[dict[str, Any]] = []
		for instance in instances:
			graph_id = instance.get("graph_id")
			instance_id = instance.get("instance_id")
			page_path = str(instance.get("page_path", ""))
			project_name, module_name, page_name = _split_page_path(page_path)

			instance_key, instance_chart_payload = _build_instance_graph(
				mode,
				subgraph_id,
				instance,
				base_edges,
				node_type_by_id,
				node_type_code_by_id,
			)
			instance_charts[instance_key] = instance_chart_payload

			instance_rows.append(
				{
					"instance_id": instance_id,
					"graph_id": graph_id,
					"page_path": page_path,
					"project_name": project_name,
					"module_name": module_name,
					"page_name": page_name,
					"description": instance.get("description", ""),
					"visualization": {
						"kind": "instance",
						"key": instance_key,
					},
				}
			)

		rows.append(
			{
				"subgraph_id": subgraph_id,
				"type": subgraph.get("type", ""),
				"name": subgraph.get("name", ""),
				"support": subgraph.get("support", 0),
				"size": subgraph.get("size", 0),
				"code_lines": subgraph.get("code_lines", 0),
				"struc_cluster_num": subgraph.get("struc_cluster_num", 0),
				"relevent_projects_num": subgraph.get("relevent_projects_num", 0),
				"summary": subgraph.get("summary", ""),
				"semantic_same_points": subgraph.get("semantic_same_points", ""),
				"instance_defference": subgraph.get("instance_defference", ""),
				"instances": instance_rows,
				"visualization": {
					"kind": "subgraph",
					"key": subgraph_key,
				},
			}
		)

	return rows


def _collect_overview_stats(
	structure_clusters: list[dict[str, Any]],
	semantic_clusters: list[dict[str, Any]],
	node_type_dict: dict[int, str],
) -> dict[str, int]:
	all_clusters = [*structure_clusters, *semantic_clusters]

	project_names: set[str] = set()
	page_paths: set[str] = set()
	component_types: set[str] = set()
	service_types: set[str] = set()
	model_types: set[str] = set()
	instance_count = 0

	for cluster in all_clusters:
		instance_count += len(cluster.get("instances", []))

		for path in cluster.get("page_paths", []):
			if path:
				page_paths.add(str(path))
				project_names.add(str(path).split("/")[0])

		for instance in cluster.get("instances", []):
			path = str(instance.get("page_path", ""))
			if path:
				page_paths.add(path)
				project_names.add(path.split("/")[0])

		for line in cluster.get("graph_structure_data", []):
			parts = str(line).strip().split()
			if len(parts) >= 3 and parts[0] == "v":
				type_code = int(parts[2])
				type_name = node_type_dict.get(type_code, f"UNKNOWN_{type_code}")
				if type_name.startswith("COMPONENT"):
					component_types.add(type_name)
				if type_name.startswith("SERNODE"):
					service_types.add(type_name)
				if type_name.startswith("MODEL"):
					model_types.add(type_name)

	return {
		"hotspot_cluster_count": len(all_clusters),
		"hotspot_instance_count": instance_count,
		"project_count": len(project_names),
		"page_count": len(page_paths),
		"component_count": len(component_types),
		"service_count": len(service_types),
		"model_count": len(model_types),
	}


def _sort_hotspot_detail_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
	return sorted(
		rows,
		key=lambda row: (
			-int(row.get("relevent_projects_num", 0)),
			-int(row.get("code_lines", 0)),
			-int(row.get("support", 0)),
			-int(row.get("subgraph_id", -1)),
		),
	)


def build_output() -> dict[str, Any]:
	frequent_subgraphs_json = _load_json(DATA_DIR / "frequent_subgraphs.json")
	node_type_dict, edge_relation_dict = _parse_node_edge_defs(DATA_DIR / "edge_and_vertex_mapping.txt")

	structure_clusters = frequent_subgraphs_json.get("structure_similar_subgraphs", [])
	semantic_clusters = frequent_subgraphs_json.get("semantic_similar_subgraphs", [])

	overview_stats = _collect_overview_stats(
		structure_clusters,
		semantic_clusters,
		node_type_dict,
	)

	subgraph_charts: dict[str, Any] = {}
	instance_charts: dict[str, Any] = {}

	structure_rows = _build_cluster_rows(
		mode="structure",
		clusters=structure_clusters,
		node_type_dict=node_type_dict,
		edge_relation_dict=edge_relation_dict,
		subgraph_charts=subgraph_charts,
		instance_charts=instance_charts,
	)
	semantic_rows = _build_cluster_rows(
		mode="semantic",
		clusters=semantic_clusters,
		node_type_dict=node_type_dict,
		edge_relation_dict=edge_relation_dict,
		subgraph_charts=subgraph_charts,
		instance_charts=instance_charts,
	)

	sorted_structure_detail_rows = _sort_hotspot_detail_rows(structure_rows)
	sorted_semantic_detail_rows = _sort_hotspot_detail_rows(semantic_rows)

	return {
		"meta": {
			"generated_at": datetime.now(timezone.utc).isoformat(),
			"report_date": frequent_subgraphs_json.get("report_date", ""),
			"report_version": frequent_subgraphs_json.get("report_version", ""),
			"generator_tool_version": frequent_subgraphs_json.get("generator_tool_version", ""),
			"covered_repositories": frequent_subgraphs_json.get("covered_repositories", ""),
		},
		"overview_stats": overview_stats,
		"top_hotspot": {
			"structure_rows": structure_rows,
			"semantic_rows": semantic_rows,
		},
		"hotspot_details": {
			"structure_clusters": sorted_structure_detail_rows,
			"semantic_clusters": sorted_semantic_detail_rows,
		},
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
