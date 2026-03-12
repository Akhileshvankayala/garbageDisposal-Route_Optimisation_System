const API_BASE = 'http://localhost:8000/api';

/**
 * Save or update a hospital node to the database
 */
export async function postNode(node: any) {
  try {
    // If updating waste only
    if (node.id && node.waste !== undefined && !node.location_x) {
      return await updateNodeWaste(node.id, node.waste);
    }

    // If creating new hospital from Playground
    if (node.label && node.pixel_x !== undefined && node.pixel_y !== undefined) {
      const hospitalData = {
        name: node.label, // H1, H2, D1, etc.
        location_x: node.pixel_x,
        location_y: node.pixel_y,
        current_waste_kg: node.waste || 0,
        max_bin_capacity: 500.0,
        contact_number: null,
        contact_email: null,
      };
      
      const res = await fetch(`${API_BASE}/nodes`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(hospitalData),
      });
      if (!res.ok) throw new Error('Failed to save node');
      return res.json();
    }

    return null;
  } catch (err) {
    console.error('Error saving node:', err);
    return null;
  }
}

/**
 * Update hospital waste level
 */
async function updateNodeWaste(nodeId: string, wasteKg: number) {
  try {
    // Extract hospital ID from node ID (H1 -> 1)
    const hospitalId = parseInt(nodeId.replace(/[HD]/g, ''), 10);
    
    const res = await fetch(`${API_BASE}/nodes/${hospitalId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ current_waste_kg: wasteKg }),
    });
    if (!res.ok) throw new Error('Failed to update waste');
    return res.json();
  } catch (err) {
    console.error('Error updating waste:', err);
    return null;
  }
}

/**
 * Save an edge (connection between hospitals)
 */
export async function postEdge(edge: any) {
  try {
    // Extract hospital IDs from edge.from and edge.to (H1, D2, etc.)
    const fromId = parseInt(edge.from.replace(/[HD]/g, ''), 10);
    const toId = parseInt(edge.to.replace(/[HD]/g, ''), 10);
    
    const edgeData = {
      from_hospital_id: fromId,
      to_hospital_id: toId,
      distance_m: edge.distance || edge.pixel_length || 100.0,
    };

    const res = await fetch(`${API_BASE}/edges`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(edgeData),
    });
    if (!res.ok) {
      // Try to parse error details from backend
      let errText = 'Failed to save edge';
      try {
        const errJson = await res.json();
        if (errJson && errJson.detail) errText = `${errText}: ${errJson.detail}`;
      } catch (e) {
        // ignore JSON parse errors and fall back to status
        errText = `${errText} (status ${res.status})`;
      }
      throw new Error(errText);
    }
    return res.json();
  } catch (err) {
    console.error('Error saving edge:', err);
    return null;
  }
}

/**
 * Compute optimal route using Dijkstra algorithm
 */
export async function computeRoute(payload: any) {
  try {
    // Validate payload
    if (!payload || typeof payload !== 'object') {
      console.error('Invalid payload for route computation:', payload);
      return null;
    }

    const res = await fetch(`${API_BASE}/route/compute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!res) {
      console.error('No response from server');
      return null;
    }

    if (!res.ok) {
      const errorText = await res.text();
      console.error(`Failed to compute route: ${res.status}`, errorText);
      return null;
    }

    const data = await res.json();
    
    // Validate response structure
    if (!data || typeof data !== 'object') {
      console.error('Invalid response from server:', data);
      return null;
    }

    return data;
  } catch (err) {
    console.error('Error computing route:', err);
    return null;
  }
}
