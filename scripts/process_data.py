from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
OUTPUT_PATH = ROOT_DIR / "src" / "assets" / "graph_table_data.json"
INPUT_GLOB = "data_*.json"
CLONE_DETECTION_PATH = DATA_DIR / "clone_detection_result.json"


def _load_json(path: Path) -> dict[str, Any]:
	with path.open("r", encoding="utf-8") as file:
		return json.load(file)


def _load_json_array(path: Path) -> list[dict[str, Any]]:
	with path.open("r", encoding="utf-8") as file:
		payload = json.load(file)

	if not isinstance(payload, list):
		raise ValueError(f"Expected a JSON array in {path}")

	return [item for item in payload if isinstance(item, dict)]


def _load_all_source_payloads(data_dir: Path) -> list[dict[str, Any]]:
	payloads: list[dict[str, Any]] = []
	for path in sorted(data_dir.glob(INPUT_GLOB)):
		if not path.is_file():
			continue
		payloads.append(_load_json(path))

	if payloads:
		return payloads

	legacy_path = data_dir / "data.json"
	if legacy_path.exists() and legacy_path.is_file():
		return [_load_json(legacy_path)]

	raise FileNotFoundError(f"No input data files found under {data_dir} by pattern {INPUT_GLOB}")


def _parse_mapping_block(raw_text: str, var_name: str) -> dict[int, str]:
	block_match = re.search(rf"{re.escape(var_name)}\s*=\s*\{{(.*?)\}}", raw_text, re.S)
	if not block_match:
		raise ValueError(f"Can not find mapping block for {var_name}")

	block = block_match.group(1)
	entries = re.findall(r"(\d+)\s*:\s*\"([^\"]+)\"", block)
	return {int(key): value for key, value in entries}


def _parse_node_edge_defs(path: Path) -> tuple[dict[int, str], dict[int, str], dict[int, str]]:
	with path.open("r", encoding="utf-8") as file:
		content = file.read()

	node_type_dict = _parse_mapping_block(content, "node_type_dict")
	# Keep backward compatibility with current typo in source files.
	try:
		flow_node_type_dict = _parse_mapping_block(content, "flow_ndoe_type_dict")
	except ValueError:
		flow_node_type_dict = _parse_mapping_block(content, "flow_node_type_dict")
	edge_relation_dict = _parse_mapping_block(content, "edge_relation_dict")
	return node_type_dict, flow_node_type_dict, edge_relation_dict


def _parse_graph_structure(
	graph_structure_data: list[str],
	node_type_dict: dict[int, str],
	edge_relation_dict: dict[int, str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, str]]:
	nodes: list[dict[str, Any]] = []
	edges: list[dict[str, Any]] = []
	node_type_by_id: dict[str, str] = {}

	for line in graph_structure_data:
		parts = line.strip().split()
		if len(parts) < 4 and (not parts or parts[0] != "v"):
			continue

		if parts[0] == "v" and len(parts) >= 3:
			node_id = parts[1]
			type_code = int(parts[2])
			type_name = node_type_dict.get(type_code, f"UNKNOWN_{type_code}")
			node_type_by_id[node_id] = type_name

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

	return nodes, edges, node_type_by_id


def _normalize_page_path_list(page_path: Any) -> list[str]:
	if isinstance(page_path, list):
		return [str(item) for item in page_path if str(item).strip()]

	if isinstance(page_path, str):
		value = page_path.strip()
		return [value] if value else []

	return []


def _extract_top_level_name(component_id: Any) -> str:
	parts = [part for part in str(component_id).split("/") if part]
	return parts[0] if parts else ""


def _extract_top_level_dir(file_path: Any) -> str:
	parts = [part for part in str(file_path).split("/") if part]
	return parts[0] if parts else ""


def _extract_top_level_page(page_path: Any) -> str:
	parts = [part for part in str(page_path).split("/") if part]
	return parts[0] if parts else ""


def _build_tree_payload(
	nodes: list[dict[str, Any]],
	edges: list[dict[str, Any]],
	node_type_by_id: dict[str, str],
) -> list[dict[str, Any]]:
	if not nodes:
		return []

	node_ids = [str(node.get("id", "")) for node in nodes]
	children_map: dict[str, list[str]] = {node_id: [] for node_id in node_ids}
	in_degree: dict[str, int] = {node_id: 0 for node_id in node_ids}

	for edge in edges:
		source = str(edge.get("source", ""))
		target = str(edge.get("target", ""))
		if source in children_map and target in children_map:
			children_map[source].append(target)
			in_degree[target] += 1

	root_ids = [node_id for node_id, degree in in_degree.items() if degree == 0]
	if not root_ids and node_ids:
		root_ids = [node_ids[0]]

	visited: set[str] = set()

	def build_node(node_id: str, ancestry: set[str]) -> dict[str, Any]:
		label = f"{node_id}: {node_type_by_id.get(node_id, 'UNKNOWN')}"
		if node_id in ancestry:
			return {"id": node_id, "label": f"{label} (cycle)", "children": []}

		next_ancestry = set(ancestry)
		next_ancestry.add(node_id)
		visited.add(node_id)
		children = [build_node(child_id, next_ancestry) for child_id in children_map.get(node_id, [])]
		return {"id": node_id, "label": label, "children": children}

	tree = [build_node(root_id, set()) for root_id in root_ids]

	for node_id in node_ids:
		if node_id not in visited:
			tree.append(build_node(node_id, set()))

	return tree


def _build_structure_rows(
	clusters: list[dict[str, Any]],
	node_type_dict: dict[int, str],
	flow_node_type_dict: dict[int, str],
	edge_relation_dict: dict[int, str],
	subgraph_charts: dict[str, Any],
	parent_cluster_name_map: dict[int, str],
) -> list[dict[str, Any]]:
	rows: list[dict[str, Any]] = []

	for cluster in clusters:
		cluster_id = int(cluster.get("structure_cluster_id", -1))
		graph_structure_data = cluster.get("graph_structure_data", [])
		instances = cluster.get("instances", [])
		cluster_type = str(cluster.get("type", "")).strip()
		active_node_type_dict = flow_node_type_dict if cluster_type == "流程" else node_type_dict

		base_nodes, base_edges, node_type_by_id = _parse_graph_structure(
			graph_structure_data,
			active_node_type_dict,
			edge_relation_dict,
		)

		subgraph_key = f"structure:{cluster_id}"
		subgraph_charts[subgraph_key] = {
			"title": f"Structure Cluster {cluster_id}",
			"categories": sorted({node["type_name"] for node in base_nodes}),
			"nodes": base_nodes,
			"edges": base_edges,
			"tree": _build_tree_payload(base_nodes, base_edges, node_type_by_id),
		}

		instance_rows: list[dict[str, Any]] = []
		for instance in instances:
			instance_id = instance.get("instance_id")
			page_path_list = _normalize_page_path_list(instance.get("page_path", []))
			component_ids = instance.get("component_id_list", instance.get("component_list", []))

			instance_rows.append(
				{
					"instance_id": instance_id,
					"page_path": page_path_list,
					"instance_summary": instance.get("instance_summary", ""),
					"component_id_list": component_ids if isinstance(component_ids, list) else [],
				}
			)

		rows.append(
			{
				"type": cluster.get("type", ""),
				"structure_cluster_id": cluster_id,
				"name": cluster.get("name", ""),
				"parent_cluster_name": parent_cluster_name_map.get(cluster_id, ""),
				"support": cluster.get("support", 0),
				"size": cluster.get("size", 0),
				"code_lines": cluster.get("code_lines", 0),
				"relevent_projects_num": cluster.get("relevent_projects_num", 0),
				"summary": cluster.get("summary", ""),
				"instance_defference": cluster.get("instance_defference", ""),
				"instances": instance_rows,
				"visualization": {
					"kind": "subgraph",
					"key": subgraph_key,
				},
			}
		)

	return rows


def _sort_structure_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
	return sorted(
		rows,
		key=lambda row: (
			-int(row.get("relevent_projects_num", 0)),
			-int(row.get("code_lines", 0)),
			-int(row.get("support", 0)),
			-int(row.get("structure_cluster_id", -1)),
		),
	)


def _build_parent_cluster_rows(
	parent_clusters: list[dict[str, Any]],
	sorted_structure_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
	structure_row_map = {
		int(row.get("structure_cluster_id", -1)): row
		for row in sorted_structure_rows
	}

	used_cluster_ids: set[int] = set()
	grouped_rows: list[dict[str, Any]] = []

	for parent in parent_clusters:
		parent_id = int(parent.get("parent_cluster_id", -1))
		child_ids = [int(cluster_id) for cluster_id in parent.get("structure_cluster_ids", [])]
		children = [
			structure_row_map[cluster_id]
			for cluster_id in child_ids
			if cluster_id in structure_row_map
		]

		if not children:
			continue

		support_sum = sum(int(child.get("support", 0)) for child in children)
		project_names: set[str] = set()
		for child in children:
			for instance in child.get("instances", []):
				for component_id in instance.get("component_id_list", []):
					top_level = _extract_top_level_name(component_id)
					if top_level:
						project_names.add(top_level)

		used_cluster_ids.update([int(child.get("structure_cluster_id", -1)) for child in children])
		grouped_rows.append(
			{
				"parent_cluster_id": parent_id,
				"name": str(parent.get("name", "")),
				"support": support_sum,
				"relevent_projects_num": len(project_names),
				"children": children,
			}
		)

	orphan_children = [
		row
		for row in sorted_structure_rows
		if int(row.get("structure_cluster_id", -1)) not in used_cluster_ids
	]
	if orphan_children:
		support_sum = sum(int(child.get("support", 0)) for child in orphan_children)
		project_names: set[str] = set()
		for child in orphan_children:
			for instance in child.get("instances", []):
				for component_id in instance.get("component_id_list", []):
					top_level = _extract_top_level_name(component_id)
					if top_level:
						project_names.add(top_level)

		grouped_rows.append(
			{
				"parent_cluster_id": -1,
				"name": "未分组结构簇",
				"support": support_sum,
				"relevent_projects_num": len(project_names),
				"children": orphan_children,
			}
		)

	return grouped_rows


def _build_clone_detection_payload(
	clone_groups: list[dict[str, Any]],
	sorted_structure_rows: list[dict[str, Any]],
	parent_clusters: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
	used_ids: set[int] = set()

	for row in sorted_structure_rows:
		cluster_id = int(row.get("structure_cluster_id", -1))
		if cluster_id >= 0:
			used_ids.add(cluster_id)

	for parent in parent_clusters:
		parent_id = int(parent.get("parent_cluster_id", -1))
		if parent_id >= 0:
			used_ids.add(parent_id)
		for cluster_id in parent.get("structure_cluster_ids", []):
			value = int(cluster_id)
			if value >= 0:
				used_ids.add(value)

	max_type1_group_count = max(
		(len(group.get("type1_group", [])) for group in clone_groups),
		default=0,
	)
	block_size = max(max_type1_group_count + 1, 10)
	base_parent_id = (max(used_ids) if used_ids else 0) + block_size

	table_rows: list[dict[str, Any]] = []
	detail_groups: list[dict[str, Any]] = []

	for group_index, group in enumerate(clone_groups):
		summary = group.get("summary", {}) if isinstance(group.get("summary"), dict) else {}
		type1_groups = group.get("type1_group", []) if isinstance(group.get("type1_group"), list) else []
		relevant_projects = [
			str(project)
			for project in group.get("relevent_projects", [])
			if str(project).strip()
		]
		parent_cluster_id = base_parent_id + group_index * block_size
		parent_name = str(summary.get("group_name", "")).strip() or f"脚本函数组 {group_index + 1}"

		children: list[dict[str, Any]] = []
		detail_type1_groups: list[dict[str, Any]] = []

		for child_index, type1_group in enumerate(type1_groups, start=1):
			functions = type1_group.get("functions", []) if isinstance(type1_group.get("functions"), list) else []
			project_dirs = {
				_extract_top_level_dir(function_item.get("file_path", ""))
				for function_item in functions
				if _extract_top_level_dir(function_item.get("file_path", ""))
			}
			structure_cluster_id = parent_cluster_id + child_index
			child_row = {
				"type": "脚本",
				"structure_cluster_id": structure_cluster_id,
				"name": str(type1_group.get("group_name", "")).strip() or f"函数组 {child_index}",
				"size": None,
				"support": None,
				"relevent_projects_num": len(project_dirs),
				"clone_group_index": group_index,
				"type1_group_index": child_index - 1,
				"detail_key": f"clone-detail-{group_index}-{child_index - 1}",
			}
			children.append(child_row)
			detail_type1_groups.append(
				{
					"group_name": child_row["name"],
					"functionality": str(type1_group.get("functionality", "")).strip(),
					"functions": functions,
					"structure_cluster_id": structure_cluster_id,
					"detail_key": child_row["detail_key"],
				}
			)

		table_rows.append(
			{
				"parent_cluster_id": parent_cluster_id,
				"name": parent_name,
				"type": "脚本",
				"size": None,
				"support": None,
				"relevent_projects_num": len(relevant_projects),
				"clone_group_index": group_index,
				"children": children,
				"source": "clone-detection",
			}
		)

		similarity_values = [
			float(item.get("similarity"))
			for item in group.get("type1_group_similarity", [])
			if isinstance(item, dict) and isinstance(item.get("similarity"), (int, float))
		]
		detail_groups.append(
			{
				"group_key": f"clone-group-{group_index}",
				"parent_cluster_id": parent_cluster_id,
				"summary": summary,
				"relevent_projects": relevant_projects,
				"similarity_range": {
					"min": min(similarity_values) if similarity_values else None,
					"max": max(similarity_values) if similarity_values else None,
				},
				"type1_group_similarity": group.get("type1_group_similarity", []),
				"type1_group": detail_type1_groups,
			}
		)

	return table_rows, detail_groups


def _build_structure_cluster_name_map(clusters: list[dict[str, Any]]) -> dict[int, str]:
	return {
		int(cluster.get("structure_cluster_id", -1)): str(cluster.get("name", ""))
		for cluster in clusters
	}


def _build_parent_cluster_name_map(parent_clusters: list[dict[str, Any]]) -> dict[int, str]:
	parent_name_map: dict[int, list[str]] = {}

	for parent_cluster in parent_clusters:
		parent_name = str(parent_cluster.get("name", "")).strip()
		for structure_cluster_id in parent_cluster.get("structure_cluster_ids", []):
			cluster_id = int(structure_cluster_id)
			parent_name_map.setdefault(cluster_id, [])
			if parent_name and parent_name not in parent_name_map[cluster_id]:
				parent_name_map[cluster_id].append(parent_name)

	return {
		cluster_id: " / ".join(parent_names)
		for cluster_id, parent_names in parent_name_map.items()
	}


def _build_semantic_rows(
	joint_clusters: list[dict[str, Any]],
	structure_clusters: list[dict[str, Any]],
) -> list[dict[str, Any]]:
	structure_cluster_map: dict[int, dict[str, Any]] = {
		int(cluster.get("structure_cluster_id", -1)): cluster
		for cluster in structure_clusters
	}

	rows: list[dict[str, Any]] = []
	for cluster in joint_clusters:
		cluster_id = int(cluster.get("cluster_id", -1))
		items = cluster.get("items", [])

		unique_structure_ids: set[int] = set()
		unique_instance_ids: set[int] = set()
		covered_projects: set[str] = set()
		available_structure_cluster_ids: list[int] = []
		items_expanded: list[dict[str, Any]] = []

		for item in items:
			structure_cluster_id = int(item.get("structure_cluster_id", -1))
			instance_ids_raw = item.get("instance_ids", [])
			instance_ids: list[int] = []
			for instance_id in instance_ids_raw:
				try:
					instance_id_int = int(instance_id)
				except (TypeError, ValueError):
					continue
				instance_ids.append(instance_id_int)

			unique_structure_ids.add(structure_cluster_id)
			unique_instance_ids.update(instance_ids)

			structure_cluster = structure_cluster_map.get(structure_cluster_id, {})
			instances = structure_cluster.get("instances", []) if isinstance(structure_cluster, dict) else []
			instance_map = {
				int(instance.get("instance_id", -1)): instance
				for instance in instances
			}

			matched_instances: list[dict[str, Any]] = []
			item_projects: set[str] = set()
			for instance_id in instance_ids:
				instance = instance_map.get(instance_id)
				if not instance:
					continue

				page_path_list = _normalize_page_path_list(instance.get("page_path", []))
				for page_path in page_path_list:
					top_level_page = _extract_top_level_page(page_path)
					if top_level_page:
						item_projects.add(top_level_page)
						covered_projects.add(top_level_page)

				component_ids = instance.get("component_id_list", instance.get("component_list", []))
				matched_instances.append(
					{
						"instance_id": instance_id,
						"page_path": page_path_list,
						"instance_summary": str(instance.get("instance_summary", "")),
						"component_id_list": component_ids if isinstance(component_ids, list) else [],
					}
				)

			if structure_cluster_id in structure_cluster_map and structure_cluster_id not in available_structure_cluster_ids:
				available_structure_cluster_ids.append(structure_cluster_id)

			items_expanded.append(
				{
					"structure_cluster_id": structure_cluster_id,
					"domain_cluster_id": int(item.get("domain_cluster_id", -1)),
					"instance_ids": sorted(set(instance_ids)),
					"structure_name": str(structure_cluster.get("name", "")),
					"type": str(structure_cluster.get("type", cluster.get("type", ""))),
					"reuse_count": len(set(instance_ids)),
					"covered_projects_count": len(item_projects),
					"visualization": {
						"kind": "subgraph",
						"key": f"structure:{structure_cluster_id}",
					},
					"instances": matched_instances,
				}
			)

		rows.append(
			{
				"cluster_id": cluster_id,
				"structure_name": str(cluster.get("structure_name", "")),
				"domain_name": str(cluster.get("domain_name", "")),
				"type": str(cluster.get("type", "")),
				"structure_variant_count": len(unique_structure_ids),
				"reuse_count": len(unique_instance_ids),
				"covered_projects_count": len(covered_projects),
				"available_structure_cluster_ids": available_structure_cluster_ids,
				"items_expanded": items_expanded,
			}
		)

	return sorted(
		rows,
		key=lambda row: (
			str(row.get("domain_name", "")),
			-int(row.get("reuse_count", 0)),
			-int(row.get("covered_projects_count", 0)),
			int(row.get("cluster_id", -1)),
		),
	)


def _merge_statistic_blocks(statistics: list[dict[str, Any]]) -> dict[str, Any]:
	merged: dict[str, Any] = {}
	for stat in statistics:
		for key, value in stat.items():
			if isinstance(value, (int, float)):
				merged[key] = merged.get(key, 0) + value
			elif key not in merged:
				merged[key] = value
	return merged


def _merge_covered_repositories(meta_blocks: list[dict[str, Any]]) -> list[str]:
	repositories: set[str] = set()
	for meta in meta_blocks:
		for repository in meta.get("covered_repositories", []):
			name = str(repository).strip()
			if name:
				repositories.add(name)
	return sorted(repositories)


def _latest_meta_field(meta_blocks: list[dict[str, Any]], key: str) -> str:
	for meta in reversed(meta_blocks):
		value = str(meta.get(key, "")).strip()
		if value:
			return value
	return ""


def build_output() -> dict[str, Any]:
	payloads = _load_all_source_payloads(DATA_DIR)
	clone_groups = _load_json_array(CLONE_DETECTION_PATH) if CLONE_DETECTION_PATH.exists() else []
	node_type_dict, flow_node_type_dict, edge_relation_dict = _parse_node_edge_defs(
		DATA_DIR / "edge_and_vertex_mapping.txt"
	)

	parent_clusters = [
		cluster
		for payload in payloads
		for cluster in payload.get("parent_clusters", [])
	]
	structure_clusters = [
		cluster
		for payload in payloads
		for cluster in payload.get("structure_similar_clusters", [])
	]
	joint_clusters = [
		cluster
		for payload in payloads
		for cluster in payload.get("structure_domain_joint_clusters", [])
	]
	meta_blocks = [payload.get("meta_data", {}) for payload in payloads]
	statistics = [payload.get("statistic", {}) for payload in payloads]

	overview_stats = _merge_statistic_blocks(statistics)

	subgraph_charts: dict[str, Any] = {}
	parent_cluster_name_map = _build_parent_cluster_name_map(parent_clusters)

	structure_rows = _build_structure_rows(
		clusters=structure_clusters,
		node_type_dict=node_type_dict,
		flow_node_type_dict=flow_node_type_dict,
		edge_relation_dict=edge_relation_dict,
		subgraph_charts=subgraph_charts,
		parent_cluster_name_map=parent_cluster_name_map,
	)
	semantic_rows = _build_semantic_rows(joint_clusters, structure_clusters)

	sorted_structure_rows = _sort_structure_rows(structure_rows)
	grouped_structure_rows = _build_parent_cluster_rows(parent_clusters, sorted_structure_rows)
	clone_detection_rows, clone_detection_groups = _build_clone_detection_payload(
		clone_groups=clone_groups,
		sorted_structure_rows=sorted_structure_rows,
		parent_clusters=parent_clusters,
	)

	return {
		"meta": {
			"generated_at": datetime.now(timezone.utc).isoformat(),
			"report_date": _latest_meta_field(meta_blocks, "report_date"),
			"report_version": _latest_meta_field(meta_blocks, "report_version"),
			"generator_tool_version": _latest_meta_field(meta_blocks, "generator_tool_version"),
			"covered_repositories": _merge_covered_repositories(meta_blocks),
		},
		"overview_stats": overview_stats,
		"structure_hotspot": {
			"rows": grouped_structure_rows,
		},
		"clone_detection": {
			"rows": clone_detection_rows,
			"groups": clone_detection_groups,
		},
		"semantic_hotspot": {
			"rows": semantic_rows,
		},
		"charts": {
			"subgraphs": subgraph_charts,
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
