/**
 * Graph/Tree Data Structure Library
 */

interface GraphNode<T = any> {
  id: string;
  data: T;
  connections: Set<string>;
}

class Graph<T = any> {
  private nodes: Map<string, GraphNode<T>> = new Map();

  addNode(id: string, data: T): void {
    if (!this.nodes.has(id)) {
      this.nodes.set(id, {
        id,
        data,
        connections: new Set()
      });
    }
  }

  removeNode(id: string): boolean {
    const node = this.nodes.get(id);
    if (!node) return false;

    // Remove all connections to this node
    this.nodes.forEach(otherNode => {
      otherNode.connections.delete(id);
    });

    return this.nodes.delete(id);
  }

  addConnection(fromId: string, toId: string): boolean {
    const fromNode = this.nodes.get(fromId);
    const toNode = this.nodes.get(toId);
    
    if (!fromNode || !toNode) return false;
    
    fromNode.connections.add(toId);
    return true;
  }

  removeConnection(fromId: string, toId: string): boolean {
    const fromNode = this.nodes.get(fromId);
    if (!fromNode) return false;
    
    return fromNode.connections.delete(toId);
  }

  getNode(id: string): GraphNode<T> | undefined {
    return this.nodes.get(id);
  }

  getConnections(id: string): string[] {
    const node = this.nodes.get(id);
    return node ? Array.from(node.connections) : [];
  }

  getAllNodes(): GraphNode<T>[] {
    return Array.from(this.nodes.values());
  }

  hasPath(fromId: string, toId: string): boolean {
    const visited = new Set<string>();
    const queue = [fromId];

    while (queue.length > 0) {
      const currentId = queue.shift()!;
      
      if (currentId === toId) return true;
      if (visited.has(currentId)) continue;
      
      visited.add(currentId);
      const connections = this.getConnections(currentId);
      queue.push(...connections);
    }

    return false;
  }

  findShortestPath(fromId: string, toId: string): string[] | null {
    const visited = new Set<string>();
    const queue: { id: string; path: string[] }[] = [{ id: fromId, path: [fromId] }];

    while (queue.length > 0) {
      const { id: currentId, path } = queue.shift()!;
      
      if (currentId === toId) return path;
      if (visited.has(currentId)) continue;
      
      visited.add(currentId);
      const connections = this.getConnections(currentId);
      
      connections.forEach(connectionId => {
        if (!visited.has(connectionId)) {
          queue.push({ id: connectionId, path: [...path, connectionId] });
        }
      });
    }

    return null;
  }
}

export { Graph, type GraphNode };
export default Graph;
