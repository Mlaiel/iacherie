/**
 * Query Builder Library
 */

interface QueryParams {
  [key: string]: string | number | boolean | Array<string | number>;
}

class QueryBuilder {
  private params: QueryParams = {};

  where(field: string, value: string | number | boolean): QueryBuilder {
    this.params[field] = value;
    return this;
  }

  whereIn(field: string, values: Array<string | number>): QueryBuilder {
    this.params[field] = values;
    return this;
  }

  select(fields: string[]): QueryBuilder {
    this.params['_select'] = fields;
    return this;
  }

  sort(field: string, direction: 'asc' | 'desc' = 'asc'): QueryBuilder {
    this.params['_sort'] = field;
    this.params['_order'] = direction;
    return this;
  }

  limit(count: number): QueryBuilder {
    this.params['_limit'] = count;
    return this;
  }

  offset(count: number): QueryBuilder {
    this.params['_offset'] = count;
    return this;
  }

  page(pageNumber: number, pageSize: number = 10): QueryBuilder {
    this.params['_page'] = pageNumber;
    this.params['_limit'] = pageSize;
    return this;
  }

  search(query: string, fields?: string[]): QueryBuilder {
    this.params['_search'] = query;
    if (fields) {
      this.params['_searchFields'] = fields;
    }
    return this;
  }

  filter(filters: QueryParams): QueryBuilder {
    Object.assign(this.params, filters);
    return this;
  }

  build(): string {
    const searchParams = new URLSearchParams();
    
    Object.entries(this.params).forEach(([key, value]) => {
      if (Array.isArray(value)) {
        value.forEach(v => searchParams.append(key, String(v)));
      } else {
        searchParams.set(key, String(value));
      }
    });

    return searchParams.toString();
  }

  buildObject(): QueryParams {
    return { ...this.params };
  }

  reset(): QueryBuilder {
    this.params = {};
    return this;
  }

  clone(): QueryBuilder {
    const newBuilder = new QueryBuilder();
    newBuilder.params = { ...this.params };
    return newBuilder;
  }

  static create(): QueryBuilder {
    return new QueryBuilder();
  }
}

export { QueryBuilder };
export default QueryBuilder;
