/**
 * Object Diff Library
 */

interface DiffResult {
  added: Record<string, any>;
  modified: Record<string, { from: any; to: any }>;
  removed: Record<string, any>;
}

class ObjectDiff {
  static diff(obj1: Record<string, any>, obj2: Record<string, any>): DiffResult {
    const result: DiffResult = {
      added: {},
      modified: {},
      removed: {}
    };

    // Find added and modified properties
    Object.keys(obj2).forEach(key => {
      if (!(key in obj1)) {
        result.added[key] = obj2[key];
      } else if (obj1[key] !== obj2[key]) {
        if (this.isObject(obj1[key]) && this.isObject(obj2[key])) {
          const nestedDiff = this.diff(obj1[key], obj2[key]);
          if (this.hasDifferences(nestedDiff)) {
            result.modified[key] = { from: obj1[key], to: obj2[key] };
          }
        } else {
          result.modified[key] = { from: obj1[key], to: obj2[key] };
        }
      }
    });

    // Find removed properties
    Object.keys(obj1).forEach(key => {
      if (!(key in obj2)) {
        result.removed[key] = obj1[key];
      }
    });

    return result;
  }

  static apply(obj: Record<string, any>, diff: DiffResult): Record<string, any> {
    const result = { ...obj };

    // Apply additions
    Object.assign(result, diff.added);

    // Apply modifications
    Object.keys(diff.modified).forEach(key => {
      result[key] = diff.modified[key].to;
    });

    // Apply removals
    Object.keys(diff.removed).forEach(key => {
      delete result[key];
    });

    return result;
  }

  static hasDifferences(diff: DiffResult): boolean {
    return (
      Object.keys(diff.added).length > 0 ||
      Object.keys(diff.modified).length > 0 ||
      Object.keys(diff.removed).length > 0
    );
  }

  private static isObject(value: any): boolean {
    return value !== null && typeof value === 'object' && !Array.isArray(value);
  }
}

export { ObjectDiff, type DiffResult };
export default ObjectDiff;
