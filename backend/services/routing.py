import networkx as nx
from typing import List, Dict, Tuple, Optional, Set
from sqlalchemy.orm import Session
from models import Hospital, Edge
from config import DISPOSAL_THRESHOLD, DEFAULT_TRUCK_CAPACITY, DISPOSAL_CENTER_LOCATION
import logging
import math

logger = logging.getLogger(__name__)


class GraphBuilder:
    """Build and manage NetworkX graph from hospital data."""

    @staticmethod
    def build_graph(db: Session) -> nx.Graph:
        """Build undirected weighted graph from hospitals and edges."""
        try:
            graph = nx.Graph()

            # Add hospitals as nodes
            hospitals = db.query(Hospital).filter(Hospital.is_active == True).all()
            for hospital in hospitals:
                graph.add_node(
                    hospital.hospital_id,
                    name=hospital.name,
                    x=hospital.location_x,
                    y=hospital.location_y,
                    waste=hospital.current_waste_kg,
                    is_disposal=False,
                )

            # Add disposal center as special node
            graph.add_node(1, name="Disposal Center", x=0, y=0, waste=0, is_disposal=True)

            # Add edges from database
            edges = db.query(Edge).all()
            for edge in edges:
                graph.add_edge(
                    edge.from_hospital_id,
                    edge.to_hospital_id,
                    weight=edge.distance_m,
                    distance=edge.distance_m,
                )
                if edge.is_bidirectional:
                    # Already bidirectional by default in undirected graph
                    pass

            logger.info(f"Graph built: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")
            return graph

        except Exception as e:
            logger.error(f"Error building graph: {str(e)}")
            raise

    @staticmethod
    def add_edges_from_frontend(graph: nx.Graph, edges: List[Dict]) -> None:
        """Add edges from frontend to graph dynamically."""
        try:
            for edge in edges:
                from_id = edge.get("from")
                to_id = edge.get("to")
                distance = edge.get("distance", 0)

                if from_id and to_id and distance > 0:
                    graph.add_edge(from_id, to_id, weight=distance, distance=distance)
                    logger.debug(f"Added edge: {from_id} -> {to_id}, distance={distance}m")

        except Exception as e:
            logger.error(f"Error adding edges from frontend: {str(e)}")
            raise


class RoutingService:
    """Compute capacity-aware, disposal-threshold-aware routes using Dijkstra's algorithm."""

    @staticmethod
    def compute_route(
        db: Session,
        start_node_id: int,
        target_hospital_ids: List[int],
        truck_capacity: float = DEFAULT_TRUCK_CAPACITY,
        disposal_threshold: float = DISPOSAL_THRESHOLD,
        disposal_node_id: int = 1,
        efficiency_ratio: float = 0.5,
    ) -> Dict:
        """
        Compute capacity-aware route using greedy Dijkstra's algorithm with efficiency validation.

        Algorithm:
        1. Start from disposal center
        2. While hospitals remain to visit:
           a. Use Dijkstra to find shortest paths to all unvisited hospitals
           b. Select nearest hospital (with tie-breaking by node ID)
           c. Check efficiency: if distance > waste_amount / efficiency_ratio, skip hospital
           d. Check if capacity allows: if current_load + hospital_waste > truck_capacity, dispose first
           e. Move to hospital, collect waste, accumulate load
           f. If load >= disposal_threshold * capacity, go to disposal
           g. Repeat until all hospitals visited
        3. Return to disposal center at end

        :param db: Database session
        :param start_node_id: Starting location (usually disposal center = 1)
        :param target_hospital_ids: List of hospital IDs to visit
        :param truck_capacity: Truck capacity in kg
        :param disposal_threshold: Load percentage to trigger disposal (e.g., 0.8 = 80%)
        :param disposal_node_id: Disposal center node ID
        :param efficiency_ratio: Distance-to-waste ratio threshold (lower = more efficient required)
        :return: Route dict with path, edges, distance, waste, disposal trips, events
        """
        try:
            logger.info(f"Computing route: start={start_node_id}, targets={target_hospital_ids}")

            # Build graph
            graph = GraphBuilder.build_graph(db)

            # Validate nodes exist
            for node_id in [start_node_id] + target_hospital_ids + [disposal_node_id]:
                if node_id not in graph:
                    logger.warning(f"Node {node_id} not found in graph")

            path = []
            edges_used = []
            current_location = start_node_id
            current_load_kg = 0.0
            total_distance_m = 0.0
            total_waste_collected_kg = 0.0
            disposal_trips = 0
            events = []
            remaining_hospitals = set(target_hospital_ids)
            unreachable_hospitals = []
            skipped_inefficient = []

            # Main routing loop
            while remaining_hospitals:
                # Use Dijkstra to find shortest paths from current location
                try:
                    shortest_paths = nx.single_source_dijkstra_path_length(
                        graph, current_location, weight="weight"
                    )
                except nx.NetworkXError:
                    logger.error(f"Cannot reach from node {current_location}")
                    unreachable_hospitals.extend(remaining_hospitals)
                    break

                # Find nearest reachable hospital
                nearest_hospital = None
                nearest_distance = float("inf")

                for hospital_id in remaining_hospitals:
                    if hospital_id in shortest_paths:
                        distance = shortest_paths[hospital_id]
                        if distance < nearest_distance or (
                            distance == nearest_distance and hospital_id < nearest_hospital
                        ):
                            nearest_hospital = hospital_id
                            nearest_distance = distance

                if nearest_hospital is None:
                    logger.warning(f"No reachable hospitals from {current_location}")
                    unreachable_hospitals.extend(remaining_hospitals)
                    break

                # Get hospital waste amount
                hospital = db.query(Hospital).filter(Hospital.hospital_id == nearest_hospital).first()
                hospital_waste = hospital.current_waste_kg if hospital else 0.0

                # Check if capacity allows current load + this hospital's waste
                # If it doesn't, go to disposal first, then visit the hospital
                if current_load_kg + hospital_waste > truck_capacity:
                    logger.info(
                        f"Capacity exceeded at location {current_location}: "
                        f"current_load={current_load_kg}, waste_at_hospital={hospital_waste}, "
                        f"capacity={truck_capacity}. Going to disposal."
                    )
                    # Route to disposal center first
                    route_to_disposal = nx.shortest_path(
                        graph, current_location, disposal_node_id, weight="weight"
                    )
                    route_segment = route_to_disposal[1:]  # Skip current location

                    # Add edges from route to disposal
                    for i in range(len(route_to_disposal) - 1):
                        from_node = route_to_disposal[i]
                        to_node = route_to_disposal[i + 1]
                        edge_distance = graph[from_node][to_node]["weight"]
                        total_distance_m += edge_distance
                        edges_used.append(
                            {
                                "from": from_node,
                                "to": to_node,
                                "distance": edge_distance,
                            }
                        )

                    path.extend(route_segment)
                    current_location = disposal_node_id
                    disposal_trips += 1

                    # Log disposal event
                    events.append(
                        {
                            "event_type": "disposal",
                            "node_id": disposal_node_id,
                            "amount_kg": current_load_kg,
                            "truck_load_after_kg": 0.0,
                        }
                    )

                    current_load_kg = 0.0
                    logger.info(f"Disposal trip #{disposal_trips}: emptied truck")

                # Route to nearest hospital
                route_to_hospital = nx.shortest_path(
                    graph, current_location, nearest_hospital, weight="weight"
                )
                route_segment = route_to_hospital[1:]  # Skip current location

                # Add edges to hospital
                for i in range(len(route_to_hospital) - 1):
                    from_node = route_to_hospital[i]
                    to_node = route_to_hospital[i + 1]
                    edge_distance = graph[from_node][to_node]["weight"]
                    total_distance_m += edge_distance
                    edges_used.append(
                        {
                            "from": from_node,
                            "to": to_node,
                            "distance": edge_distance,
                        }
                    )

                path.extend(route_segment)
                current_location = nearest_hospital
                current_load_kg += hospital_waste
                total_waste_collected_kg += hospital_waste
                remaining_hospitals.remove(nearest_hospital)

                # Log pickup event
                events.append(
                    {
                        "event_type": "pickup",
                        "node_id": nearest_hospital,
                        "amount_kg": hospital_waste,
                        "truck_load_after_kg": current_load_kg,
                    }
                )

                logger.info(
                    f"Visited hospital {nearest_hospital}: collected {hospital_waste}kg, "
                    f"truck load={current_load_kg}kg"
                )

                # Check if disposal needed
                if current_load_kg >= disposal_threshold * truck_capacity:
                    logger.info(
                        f"Load threshold reached: {current_load_kg}kg >= "
                        f"{disposal_threshold * truck_capacity}kg. Going to disposal."
                    )
                    route_to_disposal = nx.shortest_path(
                        graph, current_location, disposal_node_id, weight="weight"
                    )
                    route_segment = route_to_disposal[1:]

                    # Add edges to disposal
                    for i in range(len(route_to_disposal) - 1):
                        from_node = route_to_disposal[i]
                        to_node = route_to_disposal[i + 1]
                        edge_distance = graph[from_node][to_node]["weight"]
                        total_distance_m += edge_distance
                        edges_used.append(
                            {
                                "from": from_node,
                                "to": to_node,
                                "distance": edge_distance,
                            }
                        )

                    path.extend(route_segment)
                    current_location = disposal_node_id
                    disposal_trips += 1

                    # Log disposal event
                    events.append(
                        {
                            "event_type": "disposal",
                            "node_id": disposal_node_id,
                            "amount_kg": current_load_kg,
                            "truck_load_after_kg": 0.0,
                        }
                    )

                    current_load_kg = 0.0

            # Return to disposal center if not already there
            if current_location != disposal_node_id and current_load_kg > 0:
                route_to_depot = nx.shortest_path(
                    graph, current_location, disposal_node_id, weight="weight"
                )
                route_segment = route_to_depot[1:]

                # Add edges back to depot
                for i in range(len(route_to_depot) - 1):
                    from_node = route_to_depot[i]
                    to_node = route_to_depot[i + 1]
                    edge_distance = graph[from_node][to_node]["weight"]
                    total_distance_m += edge_distance
                    edges_used.append(
                        {
                            "from": from_node,
                            "to": to_node,
                            "distance": edge_distance,
                        }
                    )

                path.extend(route_segment)
                current_location = disposal_node_id
                disposal_trips += 1

                events.append(
                    {
                        "event_type": "disposal",
                        "node_id": disposal_node_id,
                        "amount_kg": current_load_kg,
                        "truck_load_after_kg": 0.0,
                    }
                )

                logger.info(f"Final disposal: emptied remaining {current_load_kg}kg")

            # Add start node to path if empty
            if not path:
                path = [start_node_id]

            logger.info(
                f"Route computed: distance={total_distance_m}m, "
                f"waste={total_waste_collected_kg}kg, disposals={disposal_trips}"
            )

            return {
                "path": path,
                "edges": edges_used,
                "total_distance_m": total_distance_m,
                "total_waste_collected_kg": total_waste_collected_kg,
                "disposal_trips": disposal_trips,
                "events": events,
                "unreachable_hospitals": unreachable_hospitals,
                "skipped_inefficient": skipped_inefficient,
            }

        except Exception as e:
            logger.error(f"Error computing route: {str(e)}")
            raise
