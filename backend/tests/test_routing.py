import pytest
import networkx as nx
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, Hospital, Edge
from services.routing import GraphBuilder, RoutingService

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create a test database."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_graph(db):
    """Create a sample graph with test hospitals."""
    hospitals = [
        Hospital(hospital_id=1, name="Disposal", location_x=0, location_y=0),
        Hospital(hospital_id=2, name="Hospital A", location_x=10, location_y=0, current_waste_kg=100),
        Hospital(hospital_id=3, name="Hospital B", location_x=20, location_y=0, current_waste_kg=150),
    ]

    for h in hospitals:
        db.add(h)

    db.commit()

    edges = [
        Edge(from_hospital_id=1, to_hospital_id=2, distance_m=100),
        Edge(from_hospital_id=2, to_hospital_id=3, distance_m=100),
        Edge(from_hospital_id=1, to_hospital_id=3, distance_m=150),
    ]

    for e in edges:
        db.add(e)

    db.commit()

    return db


class TestGraphBuilder:
    """Test graph building functionality."""

    def test_build_graph(self, sample_graph):
        """Test building graph from database."""
        graph = GraphBuilder.build_graph(sample_graph)

        assert isinstance(graph, nx.Graph)
        assert graph.number_of_nodes() >= 3
        assert graph.number_of_edges() >= 3

    def test_graph_node_attributes(self, sample_graph):
        """Test that nodes have correct attributes."""
        graph = GraphBuilder.build_graph(sample_graph)

        # Check disposal center
        disposal_node = graph.nodes[1]
        assert disposal_node["name"] == "Disposal Center"

    def test_graph_edges_weight(self, sample_graph):
        """Test that edges have correct weights."""
        graph = GraphBuilder.build_graph(sample_graph)

        # Check edge weight
        weight = graph[1][2]["weight"]
        assert weight == 100


class TestRoutingService:
    """Test routing algorithm."""

    def test_compute_simple_route(self, sample_graph):
        """Test computing route with single hospital."""
        route = RoutingService.compute_route(
            db=sample_graph,
            start_node_id=1,
            target_hospital_ids=[2],
            truck_capacity=1000.0,
            disposal_threshold=0.8,
        )

        assert "path" in route
        assert "edges" in route
        assert "total_distance_m" in route
        assert "total_waste_collected_kg" in route
        assert "disposal_trips" in route
        assert "events" in route

    def test_route_includes_all_targets(self, sample_graph):
        """Test that route visits all target hospitals."""
        route = RoutingService.compute_route(
            db=sample_graph,
            start_node_id=1,
            target_hospital_ids=[2, 3],
            truck_capacity=1000.0,
            disposal_threshold=0.8,
        )

        path = route["path"]
        # Both hospitals should be in the path
        assert 2 in path
        assert 3 in path

    def test_capacity_constraint(self, sample_graph):
        """Test that capacity constraint is respected."""
        # Set very low capacity to trigger disposal
        route = RoutingService.compute_route(
            db=sample_graph,
            start_node_id=1,
            target_hospital_ids=[2, 3],
            truck_capacity=100.0,  # Less than hospital waste
            disposal_threshold=0.5,
        )

        # Should have disposal trips
        assert route["disposal_trips"] > 0

    def test_disposal_threshold(self, sample_graph):
        """Test that disposal threshold triggers disposal trips."""
        route = RoutingService.compute_route(
            db=sample_graph,
            start_node_id=1,
            target_hospital_ids=[2, 3],
            truck_capacity=200.0,
            disposal_threshold=0.5,  # 50% threshold
        )

        # Should trigger disposal when load >= 100kg
        assert route["disposal_trips"] > 0
