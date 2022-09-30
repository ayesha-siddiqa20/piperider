/* tslint:disable */
/**
 * This file was automatically generated by json-schema-to-typescript.
 * DO NOT MODIFY IT BY HAND. Instead, modify the source JSONSchema file,
 * and run json-schema-to-typescript to regenerate this file.
 */

export interface SingleReportSchema {
  tables: {
    [k: string]: TableSchema;
  };
  id: string;
  project_id?: string;
  user_id?: string;
  version?: string;
  metadata_version?: string;
  created_at: string;
  datasource: DataSource;
}
/**
 * This interface was referenced by `undefined`'s JSON-Schema definition
 * via the `patternProperty` ".+".
 */
export interface TableSchema {
  name: string;
  description?: string;
  /**
   * Number of rows in this table
   */
  row_count?: number;
  /**
   * Number of rows that have identical values across corresponding columns in this table
   */
  duplicate_rows?: number;
  /**
   * Number of rows after applying the row-limit configuration (rows will be unaffected if none is set)
   */
  samples?: number;
  /**
   * The time that this table created at in ISO 8601 format including time zone
   */
  created?: string;
  /**
   * The last time that this table modified at in ISO 8601 format including time zone
   */
  last_altered?: string;
  /**
   * The volume size of this table in bytes
   */
  bytes?: number;
  /**
   * Time differentiation between the current time and table's last altered time
   */
  freshness?: number;
  /**
   * Number of columns in this table
   */
  col_count?: number;
  columns: {
    [k: string]: ColumnSchema;
  };
  piperider_assertion_result: null | PipeRiderAssertionResult;
  dbt_assertion_result?: null | DbtAssertionResult;
}
/**
 * This interface was referenced by `undefined`'s JSON-Schema definition
 * via the `patternProperty` ".+".
 */
export interface ColumnSchema {
  /**
   * The total count of values, regardless of validity
   */
  total?: number;
  /**
   * Number of rows after applying the row-limit configuration (rows will be unaffected if none is set
   */
  samples?: number;
  /**
   * The count of values that are null type
   */
  nulls?: number;
  /**
   * The count of non null values
   */
  non_nulls?: number;
  /**
   * The count of distinct kinds of values (e.g. [a,b,c,c] => [a,b,c])
   */
  distinct?: number;
  /**
   * The count of values that are recurring (e.g. [a,b,c,c] => [c,c])
   */
  duplicates?: number;
  /**
   * The count of values that are non-recurring (e.g. [a,b,c,c] => [a,b])
   */
  non_duplicates?: number;
  distribution?: Distribution;
  histogram?: Histogram;
  topk?: Topk;
  /**
   * Name of this column
   */
  name: string;
  /**
   * Descriptor of this column
   */
  description?: string;
  /**
   * Generic types of schema, python-based
   */
  type: 'string' | 'numeric' | 'integer' | 'datetime' | 'boolean' | 'other';
  /**
   * The column type definition in SQL database
   */
  schema_type: string;
  /**
   * The count of values that are non-null and not invalid
   */
  valids?: number;
  /**
   * The count of values that don't match the schema type. For example, a string in a numeric column.
   */
  invalids?: number;
  /**
   * The count of numerical values that equal zero exactly
   */
  zeros?: number;
  /**
   * The count of numerical values that are less than zero
   */
  negatives?: number;
  /**
   * The count of numerical values that are more than zero
   */
  positives?: number;
  /**
   * The count of string values with zero lengths exactly
   */
  zero_length?: number;
  /**
   * The count of string values with non-zero lengths
   */
  non_zero_length?: number;
  /**
   * The count of boolean true values
   */
  trues?: number;
  /**
   * The count of boolean false values
   */
  falses?: number;
  profile_duration?: string;
  elapsed_milli?: number;
  /**
   * The sum of a column's values
   */
  sum?: number;
  /**
   * The average of a column's values
   */
  avg?: number;
  /**
   * The standard deviation of a column's values
   */
  stddev?: number;
  /**
   * The minimum value of a column's range
   */
  min?: string | number;
  /**
   * The maximum value of a columns's range
   */
  max?: string | number;
  /**
   * The quantile value of the dataset (5th percentile)
   */
  p5?: number;
  /**
   * The quantile value of the dataset (25th percentile)
   */
  p25?: number;
  /**
   * The quantile value of the dataset (50th percentile)
   */
  p50?: number;
  /**
   * The quantile value of the dataset (75th percentile)
   */
  p75?: number;
  /**
   * The quantile value of the dataset (95th percentile)
   */
  p95?: number;
}
export interface Distribution {
  type: string;
  labels: (string | null)[];
  counts: number[];
  bin_edges?: (number | string)[];
}
export interface Histogram {
  labels: (string | null)[];
  counts: number[];
  bin_edges: (number | string)[];
}
/**
 * The most common or frequent value
 */
export interface Topk {
  values: (string | number)[];
  counts: number[];
}
export interface PipeRiderAssertionResult {
  tests: AssertionTest[];
  columns: {
    /**
     * This interface was referenced by `undefined`'s JSON-Schema definition
     * via the `patternProperty` ".+".
     */
    [k: string]: AssertionTest[];
  };
}
export interface AssertionTest {
  name: string;
  status: 'passed' | 'failed';
  parameters?: {
    [k: string]: unknown;
  };
  tags?: string[];
  expected?: unknown;
  actual?: unknown;
}
export interface DbtAssertionResult {
  tests: AssertionTest[];
  columns: {
    /**
     * This interface was referenced by `undefined`'s JSON-Schema definition
     * via the `patternProperty` ".+".
     */
    [k: string]: AssertionTest[];
  };
}
export interface DataSource {
  name: string;
  type: string;
}
