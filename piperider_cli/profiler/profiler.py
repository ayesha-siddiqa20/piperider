import concurrent.futures
import decimal
import math
import time
from datetime import datetime, date, timezone
from typing import Union, List, Tuple

from dateutil.relativedelta import relativedelta
from sqlalchemy import MetaData, Table, Column, String, Integer, Numeric, Date, DateTime, Boolean, ARRAY, select, func, \
    distinct, case, text, literal_column, inspect
from sqlalchemy.engine import Engine, Connection
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.pool import SingletonThreadPool
from sqlalchemy.sql import FromClause, text
from sqlalchemy.sql.elements import ColumnClause
from sqlalchemy.sql.expression import CTE, false, true, table as table_clause, column as column_clause
from sqlalchemy.types import Float
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session
from itertools import chain




from .event import ProfilerEventHandler, DefaultProfilerEventHandler
from ..configuration import Configuration

HISTOGRAM_NUM_BUCKET = 50


def dtof(value: Union[int, float, decimal.Decimal]) -> Union[int, float]:
    """
    dtof is helpler function to transform decimal value to float. Decimal is not json serializable type.

    :param value:
    :return:
    """
    if isinstance(value, decimal.Decimal):
        return float(value)
    return value


def format_float(val: Union[int, float]) -> str:
    """
    from the float to human-readable format.

    :param val:
    :return:
    """

    if val == 0:
        return "0"

    base = math.floor(math.log10(abs(val)))
    if base < -2:
        return f"{val:.2e}"
    elif base < 0:
        return f"{val:.3f}"
    elif base < 3:
        return f"{val:.2f}"
    elif base < 6:
        return f"{val / (10 ** 3):.1f}K"
    elif base < 9:
        return f"{val / (10 ** 6):.1f}M"
    elif base < 12:
        return f"{val / (10 ** 9):.1f}B"
    elif base < 15:
        return f"{val / (10 ** 12):.1f}T"
    else:
        return f"{val / (10 ** 12):.0f}T"


def percentage(number, total):
    if number is None:
        return None
    if not total:
        return None
    return number / total


class Profiler:
    """
    Profiler profile tables and columns by a sqlalchemy engine.
    """
    engine: Engine = None
    event_handler: ProfilerEventHandler

    def __init__(self, engine: Engine, event_handler: ProfilerEventHandler = DefaultProfilerEventHandler(),
                 config: Configuration = None):
        self.engine = engine
        self.event_handler = event_handler
        self.config = config

    def _fetch_table_metadata(self, table_name):
        metadata = MetaData()
        if len(table_name.split('.')) == 2:
            schema, table_name = table_name.split('.')
            table = Table(table_name, metadata, autoload_with=self.engine, schema=schema)
        else:
            table = Table(table_name, metadata, autoload_with=self.engine)
        return table

    def profile(self, table_names: List[str] = None) -> dict:
        """
        profile all tables or specific table. With different column types, it would profile different metrics.

        The column can be categorized as these types
        - integer
        - numeric
        - string
        - datetime
        - boolean
        - Other

        :param table_names: optional, the tables to profile
        :return: the profile results
        """

        profiled_tables = {}
        result = {
            "tables": profiled_tables,
        }
        self.event_handler.handle_run_start(result)

        metadata = MetaData()
        tables = []

        self.event_handler.handle_fetch_metadata_start()
        if self.engine.url.get_backend_name() == 'postgresql' and not table_names:
            table_names = inspect(self.engine).get_table_names()

        if not table_names:
            metadata.reflect(bind=self.engine)
            table_names = list(metadata.tables.keys())
            table_names = self._apply_incl_excl_tables(table_names)
            tables = [metadata.tables[table_name] for table_name in table_names]
            self.event_handler.handle_fetch_metadata_progress(None, len(tables), len(tables))
        else:
            table_names = self._apply_incl_excl_tables(table_names)
            completed = 0
            self.event_handler.handle_fetch_metadata_progress(None, len(table_names), completed)

            if isinstance(self.engine.pool, SingletonThreadPool):
                for table_name in table_names:
                    table = self._fetch_table_metadata(table_name)
                    tables.append(table)
                    completed = completed + 1
                    self.event_handler.handle_fetch_metadata_progress(table_name, len(table_names), completed)
            else:
                with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                    future_to_table = {executor.submit(self._fetch_table_metadata, table_name): table_name for
                                       table_name in table_names}

                    for future in concurrent.futures.as_completed(future_to_table):
                        table_name = future_to_table[future]
                        table = future.result()
                        tables.append(table)
                        completed = completed + 1
                        self.event_handler.handle_fetch_metadata_progress(table_name, len(table_names), completed)

        self.event_handler.handle_fetch_metadata_end()

        table_count = len(table_names)
        table_index = 0
        self.event_handler.handle_run_progress(result, table_count, table_index)

        for table in tables:
            tresult = self._profile_table(table)
            profiled_tables[str(table.name)] = tresult
            table_index = table_index + 1
            self.event_handler.handle_run_progress(result, table_count, table_index)

        self.event_handler.handle_run_end(result)

        return result

    def _apply_incl_excl_tables(self, tables: List[str]) -> List[str]:
        if not self.config:
            return tables
        if self.config.includes is None and self.config.excludes is None:
            return tables

        if self.config.includes is None:
            allow_list = tables
        else:
            upper_includes = [t.upper() for t in self.config.includes]
            allow_list = [t for t in tables if t.upper() in upper_includes]

        if self.config.excludes is None:
            final_list = allow_list
        else:
            upper_excludes = [t.upper() for t in self.config.excludes]
            final_list = [t for t in allow_list if t.upper() not in upper_excludes]

        return final_list

    def _drop_unsupported_columns(self, table: Table):
        array_columns = []
        candidate_columns = []

        for column in table.columns:
            if isinstance(column.type, ARRAY):
                array_columns.append(column.name + '.')
            if any(column.name.startswith(bypass_column) for bypass_column in array_columns):
                # Skip columns under an array
                continue
            candidate_columns.append(column)
        return candidate_columns

    def _profile_table_metadata(self, result: dict, table: Table):
        row_count = created = last_altered = size_bytes = None
        with self.engine.connect() as conn:
            try:
                if self.engine.url.get_backend_name() == 'snowflake':
                    inspector = inspect(self.engine) if self.engine else None
                    default_schema = inspector.default_schema_name
                    metadata_table = table_clause('TABLES', column_clause("row_count"), column_clause("created"),
                                                  column_clause("last_altered"), column_clause("bytes"),
                                                  column_clause('table_schema'), column_clause('table_name'),
                                                  schema='INFORMATION_SCHEMA')
                    metadata_columns = {column.name: column for column in metadata_table.columns}
                    stmt = select([
                        metadata_columns['row_count'],
                        func.convert_timezone('UTC', metadata_columns['created']),
                        func.convert_timezone('UTC', metadata_columns['last_altered']),
                        metadata_columns['bytes']
                    ]).select_from(metadata_table).where(metadata_columns['table_schema'] == str.upper(default_schema),
                                                         metadata_columns['table_name'] == str.upper(table.name))
                    row_count, created, last_altered, size_bytes = conn.execute(stmt).fetchone()
                    # datetime object transformation
                    created = created.isoformat()
                    last_altered = last_altered.isoformat()
                elif self.engine.url.get_backend_name() == 'bigquery':
                    dataset = self.engine.url.database
                    metadata_table = table_clause(f'{dataset}.__TABLES__', column_clause("row_count"),
                                                  column_clause("creation_time"), column_clause("last_modified_time"),
                                                  column_clause("size_bytes"), column_clause('table_id'))
                    metadata_columns = {column.name: column for column in metadata_table.columns}
                    stmt = select([
                        metadata_columns['row_count'],
                        metadata_columns['creation_time'],
                        metadata_columns['last_modified_time'],
                        metadata_columns['size_bytes']
                    ]).select_from(metadata_table).where(metadata_columns['table_id'] == table.name)
                    row_count, created, last_altered, size_bytes = conn.execute(stmt).fetchone()
                    # timestamp transformation
                    created = datetime.fromtimestamp(created / 1000.0, timezone.utc).isoformat()
                    last_altered = datetime.fromtimestamp(last_altered / 1000.0, timezone.utc).isoformat()
                elif self.engine.url.get_backend_name() == 'redshift':
                    metadata_table = table_clause('SVV_TABLE_INFO', column_clause("tbl_rows"),
                                                  column_clause("size"), column_clause("table"))
                    metadata_columns = {column.name: column for column in metadata_table.columns}
                    stmt = select([
                        metadata_columns['tbl_rows'],
                        metadata_columns['size'],
                    ]).select_from(metadata_table).where(metadata_columns['table'] == table.name)
                    row_count, size_mbytes = conn.execute(stmt).fetchone()
                    row_count = int(row_count)
                    size_bytes = size_mbytes * 1024
            except Exception:
                # table's metadata is optional except row_count
                pass
            finally:
                if row_count is None:
                    stmt = select([
                        func.count(),
                    ]).select_from(table)
                    row_count, = conn.execute(stmt).fetchone()

        result['row_count'] = result['samples'] = row_count
        # result['samples_p'] = 1

        if self.config:
            limit = self.config.profiler_config.get('table', {}).get('limit', 0)
            if row_count > limit > 0:
                result['samples'] = limit
                # result['samples_p'] = percentage(limit, row_count)

        if created:
            result['created'] = created
        if last_altered:
            result['last_altered'] = last_altered
            freshness = datetime.now(timezone.utc) - datetime.fromisoformat(last_altered)
            result['freshness'] = int(freshness.total_seconds())
        if size_bytes:
            result['bytes'] = size_bytes

    def _profile_table_duplicate_rows(self, result: dict, table: Table):
        if not self.config:
            return
        if not self.config.profiler_config.get('table', {}).get('duplicateRows'):
            return

        limit = self.config.profiler_config.get('table', {}).get('limit', 0)
        columns = [column.label(f'_{column.name}') for column in table.columns]

        with self.engine.connect() as conn:
            if self.engine.url.get_backend_name() == 'snowflake':
                if limit <= 0:
                    cte = select([func.hash(*columns).label('h')]).select_from(table).cte()
                else:
                    cte = select([func.hash(*columns).label('h')]).select_from(table).limit(limit).cte()

                cte = select([
                    cte.c.h,
                    func.count().label('c')
                ]).select_from(cte).group_by(cte.c.h).having(func.count() > 1).cte()
                stmt = select([func.sum(cte.c.c)]).select_from(cte)
                duplicate_rows, = conn.execute(stmt).fetchone()
            else:
                if limit <= 0:
                    cte = select([
                        *columns,
                        func.count().label('c')
                    ]).select_from(table).group_by(*columns).having(func.count() > 1).cte()
                else:
                    cte = select([*columns]).select_from(table).limit(limit).cte()
                    columns = [column for column in cte.columns]
                    cte = select([
                        *columns,
                        func.count().label('c')
                    ]).select_from(cte).group_by(*columns).having(func.count() > 1).cte()

                stmt = select([func.sum(cte.c.c)]).select_from(cte)
                duplicate_rows, = conn.execute(stmt).fetchone()

            samples = result['samples']
            duplicate_rows = duplicate_rows if duplicate_rows is not None else 0

            result['duplicate_rows'] = duplicate_rows
            result['duplicate_rows_p'] = percentage(duplicate_rows, samples)

    def _profile_table(self, table: Table) -> dict:
        candidate_columns = self._drop_unsupported_columns(table)
        col_index = 0
        col_count = len(candidate_columns)
        columns = {}
        result = {
            "name": table.name,
            "row_count": 0,
            "samples": 0,
            "col_count": col_count,
            "duplicate_rows": None,
            "duplicate_rows_p": None,
            "columns": columns
        }

        if not self.engine:
            # unittest case
            return result

        self.event_handler.handle_table_start(result)
        profile_start = time.perf_counter()

        # Profile table metrics
        # self._profile_table_metadata(result, table)
        self._profile_table_duplicate_rows(result, table)
        self.event_handler.handle_table_progress(result, col_count, col_index)

        # Profile columns
        # samples_p = result['samples_p']
        if isinstance(self.engine.pool, SingletonThreadPool):
            for column in candidate_columns:
                columns[column.name] = self._profile_column(table, column)
                columns[column.name]['total'] = result['row_count']
                # columns[column.name]['samples_p'] = samples_p
                col_index = col_index + 1
                self.event_handler.handle_table_progress(result, col_count, col_index)
            profile_end = time.perf_counter()
            duration = profile_end - profile_start
            # result["profile_duration"] = f"{duration:.2f}"
            # result["elapsed_milli"] = int(duration * 1000)

            self.event_handler.handle_table_end(result)
        else:
            for column in candidate_columns:
                columns[column.name] = None
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                future_to_profile = {executor.submit(self._profile_column, table, column): column for column in
                                     candidate_columns}
                try:
                    for future in concurrent.futures.as_completed(future_to_profile):
                        column = future_to_profile[future]
                        try:
                            data = future.result()
                        except Exception as exc:
                            raise exc
                        else:
                            columns[column.name] = data
                            columns[column.name]['total'] = result['row_count']
                            # columns[column.name]['samples_p'] = samples_p
                            col_index = col_index + 1
                            self.event_handler.handle_table_progress(result, col_count, col_index)
                finally:
                    profile_end = time.perf_counter()
                    duration = profile_end - profile_start
                    # result["profile_duration"] = f"{duration:.2f}"
                    # result["elapsed_milli"] = int(duration * 1000)

                    self.event_handler.handle_table_end(result)

        return result

    def _profile_column(self, table: Table, column: Column) -> dict:
        profiler_config = self.config.profiler_config if self.config else {}
        if isinstance(column.type, String):
            # VARCHAR
            # CHAR
            # TEXT
            # CLOB
            generic_type = "string"
            profiler = StringColumnProfiler(self.engine, profiler_config, table, column)
        elif isinstance(column.type, Integer):
            # INTEGER
            # BIGINT
            # SMALLINT
            generic_type = "integer"
            profiler = NumericColumnProfiler(self.engine, profiler_config, table, column, is_integer=True)
        elif isinstance(column.type, Numeric):
            # NUMERIC
            # DECIMAL
            # FLOAT
            generic_type = "numeric"
            profiler = NumericColumnProfiler(self.engine, profiler_config, table, column, is_integer=False)
        elif isinstance(column.type, Date) or isinstance(column.type, DateTime) or \
            (self.engine.url.get_backend_name() == 'snowflake' and str(column.type).startswith('TIMESTAMP')):
            # DATE
            # DATETIME
            # TIMEZONE_NTZ
            generic_type = "datetime"
            profiler = DatetimeColumnProfiler(self.engine, profiler_config, table, column)
        elif isinstance(column.type, Boolean):
            # BOOLEAN
            generic_type = "boolean"
            profiler = BooleanColumnProfiler(self.engine, profiler_config, table, column)
        else:
            generic_type = "other"
            profiler = BaseColumnProfiler(self.engine, profiler_config, table, column)

        result = {
            "name": column.name,
            "type": generic_type,
            "schema_type": str(column.type)
        }

        self.event_handler.handle_column_start(table.name, result)

        profile_start = time.perf_counter()
        profile_result = profiler.profile()
        profile_end = time.perf_counter()
        duration = profile_end - profile_start

        result.update(profile_result)
        # result["profile_duration"] = f"{duration:.2f}"
        # result["elapsed_milli"] = int(duration * 1000)

        self.event_handler.handle_column_end(table.name, result)

        return result


class BaseColumnProfiler:
    """
    The base class of the column profiler. It will automatically profile the metrics according to the schema type
    """

    engine: Engine = None
    config: dict = None
    table: Table = None
    column: Column = None

    def __init__(self, engine: Engine, config: dict, table: Table, column: Column):
        self.engine = engine
        self.config = config
        self.table = table
        self.column = column

    def _get_database_backend(self) -> str:
        """
        Helper function to return the sqlalchemy engine backend
        :return:
        """
        return self.engine.url.get_backend_name()

    def _get_limited_table_cte(self):
        t = self.table
        c = self.column
        if not self.config:
            return t, c

        limit = self.config.get('table', {}).get('limit', 0)
        if limit <= 0:
            return t, c
        else:
            cte = select([c.label('c')]).select_from(t).limit(limit).cte()
            return cte, cte.c.c

    def _get_table_cte(self) -> CTE:
        """
        Get the CTE to normalize the
        - table name
        - column name as column "c"
        - (Optional) Remove the invalid data.

        Columns
        - "c": the transformed valid to use data
            null: if the column value is null or invalid
            otherwise: orginal column value or transformed value.
        - "orig": the original column

        so that

        valid       = count(c)
        non_nulls   = count(orig)
        invalids    = non_nulls - valid

        :return: CTE
        """
        t, c = self._get_limited_table_cte()

        return select([c.label("c")]).select_from(t).cte()

    def profile(self) -> dict:
        """
        Profile a column

        :return: the profiling result. The result dict is json serializable
        """

        with self.engine.connect() as conn:
            cte = self._get_table_cte()
            stmt = select([
                func.count().label("_total"),
                func.count(cte.c.c).label("_non_nulls"),
            ])
            result = conn.execute(stmt).fetchone()
            _total, _non_nulls, = result
            _nulls = _total - _non_nulls
            _valid = _non_nulls

            return {
                'total': None,
                'num_records': _total,
                'non_nulls': _non_nulls,
                'nulls': _nulls,
                'distribution': None,
            }


class StringColumnProfiler(BaseColumnProfiler):
    def __init__(self, engine: Engine, config: dict, table: Table, column: Column):
        super().__init__(engine, config, table, column)

    def _get_table_cte(self) -> CTE:
        t, c = self._get_limited_table_cte()
        if self._get_database_backend() != 'sqlite':
            cte = select([
                c.label("c"),
                c.label("orig")
            ]).select_from(t).cte()
        else:
            cte = select([
                case(
                    [(func.typeof(c) == 'blob', None)],
                    else_=c
                ).label("c"),
                c.label("orig"),
            ]).select_from(t).cte()
        cte = select([
            cte.c.c,
            func.length(cte.c.c).label("len"),
            cte.c.orig
        ]).select_from(cte).cte()
        cte = select([
            cte.c.c,
            cte.c.len,
            case([(cte.c.len == 0, 1)], else_=None).label("zero_length"),
            cte.c.orig
        ]).select_from(cte).cte()
        return cte

    def profile(self):
        with self.engine.connect() as conn, Session(self.engine) as session:
            cte = self._get_table_cte()

            columns = [
                func.count().label("_total"),
                func.count(cte.c.orig).label("_non_nulls"),
                func.count(cte.c.c).label("_valids"),
                func.count(cte.c.zero_length).label("_zero_length"),
                func.count(distinct(cte.c.c)).label("_distinct"),
                func.avg(cte.c.len).label("_avg"),
                func.min(cte.c.len).label("_min"),
                func.max(cte.c.len).label("_max"),
            ]


            # code for trailing + leading spaces
            result2 = (session.query(func.count(cte.c.c).label("_num_values_with_trailing_leading_spaces")).\
                filter(or_(cte.c.c.like(" %"), cte.c.c.like("% ")))) 

            # code for leading only
            result3 = (session.query(func.count(cte.c.c).label("_num_leading_spaces_only")).\
                filter(and_(cte.c.c != func.ltrim(cte.c.c), cte.c.c != func.rtrim(cte.c.c)))) 

            # code for trailing only num_trailing_spaces_only
            result4 = (session.query(func.count(cte.c.c).label("_num_trailing_spaces_only")).\
                filter(cte.c.c.like("% "))) 

            # code for invalid_chars
            result5 = (session.query((cte.c.c).label("_invalid_chars")).\
                filter(func.REGEXP_CONTAINS(cte.c.c, '[^a-zA-Z0-9\s]'))).all()  
            result5_list = list(chain(*result5))

            # code for num_empty_values

            result6 = (session.query(func.count(cte.c.c).label("_num_empty_values")).\
                filter(and_(func.REGEXP_CONTAINS(cte.c.c, '[\s]+'), ~func.REGEXP_CONTAINS(cte.c.c, '[^\s]+'))))
            _num_empty_values = session.execute(result6).first()[0]

            # code for mode
            t1, c1 = self._get_limited_table_cte()
            query1 = select((c1).label("item"), func.count().label("cnt")).group_by(c1).cte("query1")
            query2 = select((query1.c.item).label("_mode")).where(query1.c.cnt.in_(select(func.max(query1.c.cnt))))

            if self._get_database_backend() == 'sqlite':
                columns.append((func.count(cte.c.len) * func.sum(
                    func.cast(cte.c.len, Float) * func.cast(cte.c.len, Float)) - func.sum(cte.c.len) * func.sum(
                    cte.c.len)) / ((func.count(cte.c.len) - 1) * func.count(cte.c.len)).label('_variance'))
                stmt = select(columns)
                result = conn.execute(stmt).fetchone() 

                _total, _non_nulls, _valids, _zero_length, _distinct, _avg, _min, _max, _variance = result
                _num_values_with_trailing_leading_spaces = session.execute(result2).first()[0]
                _num_leading_spaces_only = session.execute(result3).first()[0]
                _num_trailing_spaces_only = session.execute(result4).first()[0]
                _invalid_chars = result5_list
                # mode code continued .. 
                _mode = list(chain(*(session.execute(query2))))
                _stddev = None
                if _variance is not None:
                    _stddev = math.sqrt(_variance)
            else:
                columns.append(func.stddev(cte.c.len).label("_stddev"))
                stmt = select(columns)
                result = conn.execute(stmt).fetchone()                                  
                _total, _non_nulls, _valids, _zero_length, _distinct, _avg, _min, _max, _stddev = result
                _num_values_with_trailing_leading_spaces = session.execute(result2).first()[0]
                _num_leading_spaces_only = session.execute(result3).first()[0]
                _num_trailing_spaces_only = session.execute(result4).first()[0]
                _invalid_chars = result5_list
                _mode = list(chain(*(session.execute(query2))))

            if str(_mode) == "[None]":
                _mode = []

            _nulls = _total - _non_nulls
            _invalids = _non_nulls - _valids
            _non_zero_length = _valids - _zero_length
            _min = dtof(_min)
            _max = dtof(_max)
            _avg = dtof(_avg)
            _stddev = dtof(_stddev)
            _num_values_with_trailing_leading_spaces = dtof(_num_values_with_trailing_leading_spaces) # new code
            _num_leading_spaces_only = dtof(_num_leading_spaces_only)
            _num_trailing_spaces_only = dtof(_num_trailing_spaces_only)
            _num_empty_values = dtof(_num_empty_values)

            # code for empty_null_constraint

            if _nulls > 0 or _num_empty_values > 0:
                _empty_null_constraint = True
            else:
                _empty_null_constraint = False

            result = {
                'total': None,
                'num_records': _total,
                'non_nulls': _non_nulls,
                'nulls': _nulls,
                'distinct': _distinct,
                'min': _min,
                'max': _max,
                'min_length': _min,
                'max_length': _max,
                'avg': _avg,
                'avg_length': _avg,
                'stddev': _stddev,
                'stddev_length': _stddev,
                'num_values_with_trailing_leading_spaces': _num_values_with_trailing_leading_spaces, # new code
                'num_leading_spaces_only': _num_leading_spaces_only,
                'num_trailing_spaces_only': _num_trailing_spaces_only,
                'num_empty_values': _num_empty_values,
                'invalid_chars': _invalid_chars,
                'mode': _mode,
                'empty_null_constraint': _empty_null_constraint,

            }

            # uniqueness
            _non_duplicates = profile_non_duplicate(conn, cte, cte.c.c)
            _duplicates = _valids - _non_duplicates
            result.update({
                "duplicates": _duplicates,
                "non_duplicates": _non_duplicates,
            })

            # top k
            # topk = None
            # if _valids > 0:
            #     topk = profile_topk(conn, cte.c.c)
            # result['topk'] = topk

            # histogram of string length
            # histogram = None
            # if _valids > 0:
            #     histogram = profile_histogram(conn, cte, cte.c.len, _min, _max, True)
            # result['histogram'] = histogram
            # result['histogram_length'] = histogram

            # # deprecated
            # result['distribution'] = {
            #     "type": "topk",
            #     "labels": topk["values"],
            #     "counts": topk["counts"],
            # } if topk else None
            
            #new code: unique constraint
            result["unique_check"] = (percentage(_distinct, _valids) == 1)
            return result


class NumericColumnProfiler(BaseColumnProfiler):
    is_integer: bool

    def __init__(self, engine: Engine, config: dict, table: Table, column: Column, is_integer: bool):
        super().__init__(engine, config, table, column)
        self.is_integer = is_integer

    def _get_table_cte(self) -> CTE:
        t, c = self._get_limited_table_cte()
        if self._get_database_backend() != 'sqlite':
            cte = select([
                c.label("c"),
                c.label("orig")
            ]).select_from(t).cte()
        else:
            cte = select([
                case(
                    [(func.typeof(c) == 'text', None),
                     (func.typeof(c) == 'blob', None)],
                    else_=c
                ).label("c"),
                c.label("orig")
            ]).select_from(t).cte(name="T")
        cte = select([
            cte.c.c,
            case([(cte.c.c == 0, 1)], else_=None).label("zero"),
            case([(cte.c.c < 0, 1)], else_=None).label("negative"),
            cte.c.orig
        ]).select_from(cte).cte()
        return cte

    def profile(self):
        with self.engine.connect() as conn, Session(self.engine) as session:
            cte = self._get_table_cte()

            columns = [
                func.count().label("_total"),
                func.count(cte.c.orig).label("_non_nulls"),
                func.count(cte.c.c).label("_valids"),
                func.count(cte.c.zero).label("_zeros"),
                func.count(cte.c.negative).label("_negatives"),
                func.count(distinct(cte.c.c)).label("_distinct"),
                func.sum(func.cast(cte.c.c, Float)).label("_sum"),
                func.max(func.length(func.ltrim(func.cast(cte.c.c, String), '0'))).label("_max_length_leading_zeroes"),
                func.max(func.length(func.replace(func.ltrim(func.replace(func.cast(cte.c.c, String), '0', ' ')), ' ', '0'))).label("_max_length_after_trim"),
                func.min(func.length(func.cast(cte.c.c, String))).label("_min_length"),
                func.max(func.length(func.cast(cte.c.c, String))).label("_max_length"),
                func.avg(cte.c.c).label("_avg"),
                func.avg(func.length(func.cast(cte.c.c, String))).label("_avg_length"),
                func.min(cte.c.c).label("_min"),
                func.max(cte.c.c).label("_max"),
            ]

            t1, c1 = self._get_limited_table_cte()
            query1 = select((c1).label("item"), func.count().label("cnt")).group_by(c1).cte("query1")
            query2 = select((query1.c.item).label("_mode")).where(query1.c.cnt.in_(select(func.max(query1.c.cnt))))

            # code for decimal_digits
            decimal_digits = (session.query(func.length(func.substr(func.cast(cte.c.c, String), func.instr(func.cast(cte.c.c, String), '.') + 1)).label("_decimal_digits"))).all()  
            _decimal_digits = list(chain(*decimal_digits))

            if self._get_database_backend() == 'sqlite':
                columns.append((func.count(cte.c.c) * func.sum(
                    func.cast(cte.c.c, Float) * func.cast(cte.c.c, Float)) - func.sum(cte.c.c) * func.sum(cte.c.c)) / (
                                   (func.count(cte.c.c) - 1) * func.count(cte.c.c)).label('_variance'))
                stmt = select(columns)
                result = conn.execute(stmt).fetchone() # new code
                _total, _non_nulls, _valids, _zeros, _negatives, _distinct, _sum, _max_length_leading_zeroes, _max_length_after_trim, _min_length, _max_length, _avg, _avg_length, _min, _max, _variance = result
                _stddev = None
                _mode = list(chain(*(session.execute(query2))))

                if _variance is not None:
                    _stddev = math.sqrt(_variance)
            else:
                columns.append(func.stddev(cte.c.c).label("_stddev"))
                stmt = select(columns)
                result = conn.execute(stmt).fetchone() # new code
                _total, _non_nulls, _valids, _zeros, _negatives, _distinct, _sum, _max_length_leading_zeroes, _max_length_after_trim, _min_length, _max_length, _avg, _avg_length, _min, _max, _stddev = result
                _mode = list(chain(*(session.execute(query2))))

            if str(_mode) == "[None]":
                _mode = []

            _nulls = _total - _non_nulls
            _invalids = _non_nulls - _valids
            _positives = _valids - _zeros - _negatives
            _sum = dtof(_sum)
            _min = dtof(_min)
            _max = dtof(_max)
            _max_length_leading_zeroes = dtof(_max_length_leading_zeroes) # new code
            _max_length_after_trim = dtof(_max_length_after_trim)
            _min_length = dtof(_min_length)
            _max_length = dtof(_max_length)
            _avg = dtof(_avg)
            _avg_length = dtof(_avg_length)
            _stddev = dtof(_stddev)
            quantile = {}
            if _valids > 0:
                quantile = self._profile_quantile(conn, cte, cte.c.c, _valids)
            _median = dtof(quantile.get('p50'))

            # code for empty_null_constraint

            if _nulls > 0:
                _empty_null_constraint = True
            else:
                _empty_null_constraint = False

            result = {
                'total': None,
                'num_records': _total,
                'non_nulls': _non_nulls,
                'nulls': _nulls,
                'distinct': _distinct,
                'min': _min,
                'max': _max,
                'min_length': _min_length,
                'max_length': _max_length,
                'sum': _sum,
                'max_length_leading_zeroes': _max_length_leading_zeroes, #new code
                'max_length_after_trim': _max_length_after_trim,
                'decimal_digits': _decimal_digits,
                'avg': _avg,
                'avg_length': _avg_length,
                'stddev': _stddev,
                'median': _median,
                'mode': _mode,
                'empty_null_constraint': _empty_null_constraint,

            }

            # uniqueness
            _non_duplicates = profile_non_duplicate(conn, cte, cte.c.c)
            _duplicates = _valids - _non_duplicates
            result.update({
                "duplicates": _duplicates,
                "non_duplicates": _non_duplicates,
            })

            # histogram
            # histogram = None
            # if _valids > 0:
            #     histogram = profile_histogram(conn, cte, cte.c.c, _min, _max, self.is_integer)
            # result['histogram'] = histogram

            # quantile
            # new code: modifying quantiles to get them into a single list
            _quantiles = [quantile.get('p5'), quantile.get('p25'), quantile.get('p50'), quantile.get('p75'), quantile.get('p95')]
            result["quantiles"] = _quantiles


            # # top k (integer only)
            # if self.is_integer:
            #     topk = None
            #     if _valids > 0:
            #         topk = profile_topk(conn, cte.c.c)
            #     result["topk"] = topk

            # deprecated
            # result["distribution"] = {
            #     "type": "histogram",
            #     "labels": histogram["labels"],
            #     "counts": histogram["counts"],
            #     "bin_edges": histogram["bin_edges"],
            # } if histogram else None

            # new code: skewness
            result["skewness"] = (3 * (result['avg'] - result["quantiles"][2]) / result['stddev'])
            
            # new code: kurtosis

            # 4th moment
            deviation = func.cast(cte.c.c, Float) - result['avg']
            moment = func.sum(deviation * deviation * deviation * deviation)
            stmt = select(moment)
            _moment = dtof(conn.execute(stmt).fetchone()[0])
            result["kurtosis"] = _moment / (result['samples'] * (result['stddev'] ** 4))
                    
            #new code: unique constraint
            result["unique_check"] = (percentage(_distinct, _valids)== 1)

            return result

    def _profile_quantile_via_window_function(
        self,
        conn: Connection,
        table: FromClause,
        column: ColumnClause,
        total: int
    ):
        # with t as (
        #   select
        #     column as c,
        #     ntile(20) over (order by column) as n
        #   from table
        # )
        # select n, min(c) from t group by n order by n
        n_bucket = total if total < 100 else 100
        t = select([
            column.label("c"),
            func.ntile(n_bucket).over(order_by=column).label("n")
        ]).where(column.isnot(None)).select_from(table).cte()
        stmt = select([t.c.n, func.min(t.c.c)]).group_by(t.c.n).order_by(t.c.n)
        result = conn.execute(stmt)
        quantile = []
        for row in result:
            n, v = row
            quantile.append(v)
        return {
            'p5': dtof(quantile[5 * n_bucket // 100]),
            'p25': dtof(quantile[25 * n_bucket // 100]),
            'p50': dtof(quantile[50 * n_bucket // 100]),
            'p75': dtof(quantile[75 * n_bucket // 100]),
            'p95': dtof(quantile[95 * n_bucket // 100]),
        }

    def _profile_quantile_via_query_one_by_one(
        self,
        conn: Connection,
        table: FromClause,
        column: ColumnClause,
        total: int
    ):
        # Query for each quantile
        def ntile(n):
            offset = n * total // 100

            stmt = select([
                column
            ]).select_from(
                table
            ).where(
                column.isnot(None)
            ).order_by(
                column
            ).offset(
                offset
            ).limit(1)
            result, = conn.execute(stmt).fetchone()
            return dtof(result)

        return {
            'p5': ntile(5),
            'p25': ntile(25),
            'p50': ntile(50),
            'p75': ntile(75),
            'p95': ntile(95),
        }

    def _profile_quantile(
        self,
        conn: Connection,
        table: FromClause,
        column: ColumnClause,
        total: int
    ) -> dict:
        """

        :param conn:
        :param table: a
        :param column:
        :param total:
        :return:
        """

        if self._get_database_backend() == 'sqlite':
            import sqlite3
            version = sqlite3.sqlite_version.split(".")

            major = int(version[0]) if len(version) >= 2 else 0
            minor = int(version[1]) if len(version) >= 2 else 0

            if major > 3 or (major == 3 and minor >= 25):
                # use window function if sqlite version >= 3.25.0
                # see https://www.sqlite.org/windowfunctions.html

                return self._profile_quantile_via_window_function(conn, table, column, total)
            else:
                return self._profile_quantile_via_query_one_by_one(conn, table, column, total)
        elif self._get_database_backend() == 'duckdb':
            selects = [
                func.approx_quantile(column, literal_column(f"{percentile}")) for percentile in
                [0.25]
                #[0.05, 0.25, 0.5, 0.75, 0.95]
            ]
        elif self._get_database_backend() == 'bigquery':
            # BigQuery does not support WITHIN, change to use over
            #   Ref: https://github.com/great-expectations/great_expectations/blob/develop/great_expectations/dataset/sqlalchemy_dataset.py#L1019:9
            selects = [
                func.percentile_disc(column, percentile).over() for percentile in [0.05, 0.25, 0.5, 0.75, 0.95]
            ]
        elif self._get_database_backend() == 'redshift':
            # ref: https://docs.aws.amazon.com/redshift/latest/dg/r_APPROXIMATE_PERCENTILE_DISC.html
            selects = [
                func.approximate_percentile_disc(percentile).within_group(column) for percentile in
                [0.05, 0.25, 0.5, 0.75, 0.95]
            ]
        else:
            # https://docs.sqlalchemy.org/en/14/core/functions.html#sqlalchemy.sql.functions.percentile_disc
            #
            # select
            #     percentile_disc(0.05) within group (order by column),
            #     percentile_disc(0.25) within group (order by column),
            #     percentile_disc(0.5) within group (order by column),
            #     percentile_disc(0.75) within group (order by column),
            #     percentile_disc(0.95) within group (order by column)
            # from table
            selects = [
                func.percentile_disc(percentile).within_group(column) for percentile in [0.25]#[0.05, 0.25, 0.5, 0.75, 0.95]
            ]

        stmt = select(selects).select_from(table)
        result = conn.execute(stmt).fetchone()
        return {
            'p5': dtof(result[0]),
            'p25': dtof(result[1]),
            'p50': dtof(result[2]),
            'p75': dtof(result[3]),
            'p95': dtof(result[4]),
        }

    def _profile_histogram(
        self,
        conn: Connection,
        table: FromClause,
        column: ColumnClause,
        min: Union[int, float],
        max: Union[int, float],
        is_integer: bool,
        num_buckets: int = HISTOGRAM_NUM_BUCKET
    ) -> dict:
        if is_integer:
            # min=0, max=50, num_buckets=50  => interval=1, num_buckets=51
            # min=0, max=70, num_buckets=50  => interval=2, num_buckets=36
            # min=0, max=100, num_buckets=50 => interval=2, num_buckets=51
            interval = math.ceil((max - min) / num_buckets) if max > min else 1
            num_buckets = math.ceil((max - min + 1) / interval)
        else:
            interval = (max - min) / num_buckets if max > min else 1

        cases = []
        for i in range(num_buckets):
            bound = min + interval * (i + 1)
            if i != num_buckets - 1:
                cases += [(column < bound, i)]
            else:
                cases += [(column < bound + interval / 100, i)]

        cte_with_bucket = select([
            column.label("c"),
            case(cases, else_=None).label("bucket")
        ]).select_from(
            table
        ).where(
            column.isnot(None)
        ).cte()

        stmt = select([
            cte_with_bucket.c.bucket,
            func.count().label("_count")
        ]).group_by(
            cte_with_bucket.c.bucket
        ).order_by(
            cte_with_bucket.c.bucket
        )

        result = conn.execute(stmt)

        counts = []
        labels = []
        bin_edges = []
        for i in range(num_buckets):
            if is_integer:
                start = min + i * interval
                end = min + (i + 1) * interval
                if interval == 1:
                    label = f"{start}"
                else:
                    label = f"{start} _ {end}"
            else:
                if interval >= 1:
                    start = min + i * interval
                    end = min + (i + 1) * interval
                else:
                    start = min + i / (1 / interval)
                    end = min + (i + 1) / (1 / interval)

                label = f"{format_float(start)} _ {format_float(end)}"

            labels.append(label)
            counts.append(0)
            bin_edges.append(start)
            if i == num_buckets - 1:
                bin_edges.append(end)

        for row in result:
            _bucket, v = row
            if _bucket is None:
                continue
            counts[int(_bucket)] = v
        return {
            "type": "histogram",
            "labels": labels,
            "counts": counts,
            "bin_edges": bin_edges,
        }


class DatetimeColumnProfiler(BaseColumnProfiler):
    def __init__(self, engine: Engine, config: dict, table: Table, column: Column):
        super().__init__(engine, config, table, column)

    def _get_table_cte(self) -> CTE:
        t, c = self._get_limited_table_cte()
        if self._get_database_backend() != 'sqlite':
            cte = select([
                c.label("c"),
                c.label("orig")
            ]).select_from(t).cte()
        else:
            cte = select([
                case(
                    [(func.typeof(c) == 'text', func.datetime(c)),
                     (func.typeof(c) == 'integer', func.datetime(c, 'unixepoch')),
                     (func.typeof(c) == 'real', func.datetime(c, 'unixepoch'))],
                    else_=None
                ).label("c"),
                c.label("orig"),
            ]).select_from(t).cte()
        return cte

    def profile(self):
        with self.engine.connect() as conn, Session(self.engine) as session:
            cte = self._get_table_cte()

            stmt = select([
                func.count().label("_total"),
                func.count(cte.c.orig).label("_non_nulls"),
                func.count(cte.c.c).label("_valids"),
                func.count(distinct(cte.c.c)).label("_distinct"),
                func.min(cte.c.c).label("_min"),
                func.max(cte.c.c).label("_max"),
            ])

            t1, c1 = self._get_limited_table_cte()
            query1 = select((c1).label("item"), func.count().label("cnt")).group_by(c1).cte("query1")
            query2 = select((query1.c.item).label("_mode")).where(query1.c.cnt.in_(select(func.max(query1.c.cnt))))

            result = conn.execute(stmt).fetchone()
            _total, _non_nulls, _valids, _distinct, _min, _max = result
            _nulls = _total - _non_nulls
            _invalids = _non_nulls - _valids
            _mode = list(chain(*(session.execute(query2))))

            # code for empty_null_constraint

            if _nulls > 0:
                _empty_null_constraint = True
            else:
                _empty_null_constraint = False


            if self._get_database_backend() == 'sqlite':
                if isinstance(self.column.type, Date):
                    _min = datetime.fromisoformat(_min).date() if isinstance(_min, str) else _min
                    _max = datetime.fromisoformat(_max).date() if isinstance(_max, str) else _max
                else:
                    _min = datetime.fromisoformat(_min) if isinstance(_min, str) else _min
                    _max = datetime.fromisoformat(_max) if isinstance(_max, str) else _max

            result = {
                'total': None,
                'num_records': _total,
                'non_nulls': _non_nulls,
                'nulls': _nulls,
                'distinct': _distinct,
                'min': _min.isoformat() if _min is not None else None,
                'max': _max.isoformat() if _max is not None else None,
                'empty_null_constraint': _empty_null_constraint,
                'mode': _mode,
            }

            # uniqueness
            _non_duplicates = profile_non_duplicate(conn, cte, cte.c.c)
            _duplicates = _valids - _non_duplicates
            result.update({
                "duplicates": _duplicates,
                "non_duplicates": _non_duplicates,
            })

            # histogram
            # histogram = None
            # _type = None
            # if _min and _max:
            #     histogram, _type = self._profile_histogram(conn, cte, cte.c.c, _min, _max)
            # result['histogram'] = histogram

            # # deprecated
            # result["distribution"] = {
            #     "type": _type,
            #     "labels": histogram["labels"],
            #     "counts": histogram["counts"],
            #     "bin_edges": histogram["bin_edges"],
            # } if histogram else None

            #new code: unique constraint
            result["unique_check"] = (percentage(_distinct, _valids) == 1)

            return result

    def _profile_histogram(
        self,
        conn: Connection,
        table: FromClause,
        column: ColumnClause,
        min: Union[date, datetime],
        max: Union[date, datetime]
    ) -> Tuple[dict, str]:
        """
        Profile the histogram of a datetime column. There are three way to create bins of the histogram


        :param conn:
        :param table:
        :param column:
        :param min:
        :param max:
        :return:
        """

        # if self._get_database_backend() == 'sqlite':
        #     min = datetime.fromisoformat(min).date() if min is not None else min
        #     max = datetime.fromisoformat(max).date() if max is not None else max
        # else:
        #     if isinstance(min, datetime):
        #         min = min.date()
        #     if isinstance(max, datetime):
        #         max = max.date()

        _type = None
        histogram = {
            "labels": [],
            "counts": [],
            "bin_edges": [],
        }

        def date_trunc(*args):
            if self._get_database_backend() == 'sqlite':
                if args[0] == "YEAR":
                    return func.strftime("%Y-01-01", args[1])
                elif args[0] == "MONTH":
                    return func.strftime("%Y-%m-01", args[1])
                else:
                    return func.strftime("%Y-%m-%d", args[1])
            elif self._get_database_backend() == 'bigquery':
                date_expression = args[1]
                date_part = args[0]
                return func.date_trunc(date_expression, text(date_part))
            else:
                return func.date_trunc(*args)

        days_delta = (max - min).days
        if days_delta > 365 * 4:
            _type = "yearly"
            dmin = date(min.year, 1, 1)
            dmax = date(max.year, 1, 1) + relativedelta(years=+1)
            interval_years = math.ceil((dmax.year - dmin.year) / 50)
            interval = relativedelta(years=+interval_years)
            num_buckets = math.ceil((dmax.year - dmin.year) / interval.years)
            cte = select([date_trunc("YEAR", column).label("d")]).select_from(table).cte()
        elif days_delta > 60:
            _type = "monthly"
            interval = relativedelta(months=+1)
            dmin = date(min.year, min.month, 1)
            dmax = date(max.year, max.month, 1) + interval
            period = relativedelta(dmax, dmin)
            num_buckets = (period.years * 12 + period.months)
            cte = select([date_trunc("MONTH", column).label("d")]).select_from(table).cte()
        else:
            _type = "daily"
            interval = relativedelta(days=+1)
            dmin = date(min.year, min.month, min.day)
            dmax = date(max.year, max.month, max.day) + interval
            num_buckets = (dmax - dmin).days
            cte = select([date_trunc("DAY", column).label("d")]).select_from(table).cte()

        stmt = select([
            cte.c.d,
            func.count(cte.c.d).label("_count")
        ]).group_by(
            cte.c.d
        ).order_by(
            cte.c.d
        )

        result = conn.execute(stmt)

        for i in range(num_buckets):
            label = f"{dmin + i * interval} - {dmin + (i + 1) * interval}"
            histogram["labels"].append(label)
            histogram["bin_edges"].append(str(dmin + i * interval))
            histogram["counts"].append(0)
        histogram["bin_edges"].append(str(dmin + num_buckets * interval))

        for row in result:
            date_truncated, v = row
            if date_truncated is None:
                continue
            elif isinstance(date_truncated, str):
                date_truncated = date.fromisoformat(date_truncated)
            elif isinstance(date_truncated, datetime):
                date_truncated = date_truncated.date()

            for i in range(num_buckets):
                date_edge = date.fromisoformat(histogram["bin_edges"][i + 1])
                if date_truncated < date_edge:
                    histogram["counts"][i] += v
                    break

        return histogram, _type


class BooleanColumnProfiler(BaseColumnProfiler):
    def __init__(self, engine: Engine, config: dict, table: Table, column: Column):
        super().__init__(engine, config, table, column)

    def _get_table_cte(self) -> CTE:
        t, c = self._get_limited_table_cte()
        if self._get_database_backend() != 'sqlite':
            cte = select([
                c.label("c"),
                c.label("orig")
            ]).select_from(t).cte()
        else:
            cte = select([
                case(
                    [(c == true(), c),
                     (c == false(), c)],
                    else_=None
                ).label("c"),
                c.label("orig"),
            ]).cte()
        cte = select([
            cte.c.c,
            case([(cte.c.c == true(), 1)], else_=None).label("true_count"),
            cte.c.orig
        ]).select_from(cte).cte()
        return cte

    def profile(self):
        cte = self._get_table_cte()

        with self.engine.connect() as conn, Session(self.engine) as session:
            stmt = select([
                func.count().label("_total"),
                func.count(cte.c.orig).label("_non_nulls"),
                func.count(cte.c.c).label("_valids"),
                func.count(cte.c.true_count).label("_trues"),
                func.count(distinct(cte.c.c)).label("_distinct"),
            ]).select_from(cte)

            t1, c1 = self._get_limited_table_cte()
            query1 = select((c1).label("item"), func.count().label("cnt")).group_by(c1).cte("query1")
            query2 = select((query1.c.item).label("_mode")).where(query1.c.cnt.in_(select(func.max(query1.c.cnt))))

            result = conn.execute(stmt).fetchone()
            _total, _non_nulls, _valids, _trues, _distinct = result
            _nulls = _total - _non_nulls
            _invalids = _non_nulls - _valids
            _falses = _valids - _trues
            _mode = list(chain(*(session.execute(query2))))

            if str(_mode) == "[None]":
                _mode = []

            # code for empty_null_constraint
            if _nulls > 0:
                _empty_null_constraint = True
            else:
                _empty_null_constraint = False

            result = {
                'total': None,
                'num_records': _total,
                'non_nulls': _non_nulls,
                'nulls': _nulls,
                'distinct': _distinct,
                'mode': _mode,
                'empty_null_constraint': _empty_null_constraint,

                # deprecated
                # 'distribution': {
                #     'type': "topk",
                #     'labels': ["False", "True"],
                #     'counts': [_falses, _trues]
                # }
            }

            #new code: unique constraint
            result["unique_check"] = (percentage(_distinct, _valids) == 1)

            return result


def profile_topk(conn, expr, k=50) -> dict:
    stmt = select([
        expr,
        func.count().label("_count")
    ]).where(
        expr.isnot(None)
    ).group_by(
        expr
    ).order_by(
        func.count().desc(),
    ).limit(k)
    result = conn.execute(stmt)

    topk = {
        "values": [],
        "counts": [],
    }
    for row in result:
        k, v = row
        if k is not None:
            k = str(k)
        topk["values"].append(k)
        topk["counts"].append(v)
    return topk


def profile_histogram(
    conn: Connection,
    table: FromClause,
    column: ColumnClause,
    min: Union[int, float],
    max: Union[int, float],
    is_integer: bool,
    num_buckets: int = HISTOGRAM_NUM_BUCKET
) -> dict:
    if is_integer:
        # min=0, max=50, num_buckets=50  => interval=1, num_buckets=51
        # min=0, max=70, num_buckets=50  => interval=2, num_buckets=36
        # min=0, max=100, num_buckets=50 => interval=2, num_buckets=51
        interval = math.ceil((max - min) / num_buckets) if max > min else 1
        num_buckets = math.ceil((max - min + 1) / interval)
    else:
        interval = (max - min) / num_buckets if max > min else 1

    cases = []
    for i in range(num_buckets):
        bound = min + interval * (i + 1)
        if i != num_buckets - 1:
            cases += [(column < bound, i)]
        else:
            cases += [(column < bound + interval / 100, i)]

    cte_with_bucket = select([
        column.label("c"),
        case(cases, else_=None).label("bucket")
    ]).select_from(
        table
    ).where(
        column.isnot(None)
    ).cte()

    stmt = select([
        cte_with_bucket.c.bucket,
        func.count().label("_count")
    ]).group_by(
        cte_with_bucket.c.bucket
    ).order_by(
        cte_with_bucket.c.bucket
    )

    result = conn.execute(stmt)

    counts = []
    labels = []
    bin_edges = []
    for i in range(num_buckets):
        if is_integer:
            start = min + i * interval
            end = min + (i + 1) * interval
            if interval == 1:
                label = f"{start}"
            else:
                label = f"{start} _ {end}"
        else:
            if interval >= 1:
                start = min + i * interval
                end = min + (i + 1) * interval
            else:
                start = min + i / (1 / interval)
                end = min + (i + 1) / (1 / interval)

            label = f"{format_float(start)} _ {format_float(end)}"

        labels.append(label)
        counts.append(0)
        bin_edges.append(start)
        if i == num_buckets - 1:
            bin_edges.append(end)

    for row in result:
        _bucket, v = row
        if _bucket is None:
            continue
        counts[int(_bucket)] = v
    return {
        "labels": labels,
        "counts": counts,
        "bin_edges": bin_edges,
    }


def profile_non_duplicate(
    conn: Connection,
    table: FromClause,
    column: ColumnClause,
) -> int:
    # with t as (
    #     select count(column) as c
    # from table
    # group by column
    # having c == 1
    # )
    # select
    # count(c) as non_duplicate
    # from t;
    cte = select([
        func.count(column).label("non_duplicates")
    ]).select_from(
        table
    ).where(
        column.isnot(None)
    ).group_by(
        column
    ).having(
        func.count(column) == 1
    ).cte()

    stmt = select([func.count(cte.c.non_duplicates)]).select_from(cte)
    non_duplicates, = conn.execute(stmt).fetchone()
    return non_duplicates
