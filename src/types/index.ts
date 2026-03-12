export type NodeType = 'hospital' | 'disposal';

export interface Node {
  id: string;
  type: NodeType;
  x: number;
  y: number;
  waste?: number;
  hospital_id?: number;
}

export interface Edge {
  from: string;
  to: string;
  distance: number;
}

export type Mode = 'add-node' | 'connect-nodes' | 'view-route';

export type Role = 'guest' | 'admin' | 'staff' | 'driver';

export interface Scale {
  label: string;
  factor: number;
  unit: string;
}
