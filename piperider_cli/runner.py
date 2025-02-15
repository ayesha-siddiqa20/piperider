import json
import math
import os
import re
import sys
import uuid
from datetime import datetime

from rich import box
from rich.color import Color
from rich.console import Console
from rich.pretty import Pretty
from rich.progress import Progress, Column, TextColumn, BarColumn, TimeElapsedColumn, MofNCompleteColumn
from rich.style import Style
from rich.table import Table
from sqlalchemy.exc import NoSuchTableError

from piperider_cli import convert_to_tzlocal, datetime_to_str, clone_directory, \
    raise_exception_when_directory_not_writable
from piperider_cli import event
from piperider_cli.adapter import DbtAdapter
from piperider_cli.assertion_engine import AssertionEngine
from piperider_cli.assertion_engine.recommender import RECOMMENDED_ASSERTION_TAG
from piperider_cli.configuration import Configuration
from piperider_cli.datasource import DataSource
from piperider_cli.exitcode import EC_ERR_TEST_FAILED
from piperider_cli.filesystem import FileSystem
from piperider_cli.profiler import Profiler, ProfilerEventHandler

class RunEventPayload:

    def __init__(self):
        # all fields
        self.tables = 0
        self.columns = []
        self.rows = []
        self.dbt_command = ''
        self.passed_assertions = 0
        self.failed_assertions = 0
        self.passed_dbt_testcases = 0
        self.failed_dbt_testcases = 0
        self.build_in_assertions = 0
        self.custom_assertions = 0
        self.recommended_assertions = 0

    def to_dict(self):
        return self.__dict__


class RichProfilerEventHandler(ProfilerEventHandler):

    def __init__(self, tables):
        table_width, total_width = self._get_width(tables)
        total_column = TextColumn("{task.fields[coft]}", table_column=Column(width=total_width))
        text_column = TextColumn("{task.description}", table_column=Column(width=table_width))
        bar_column = BarColumn(bar_width=80, pulse_style=Style.from_color(Color.from_rgb(244, 164, 96)))
        mofn_column = MofNCompleteColumn(table_column=Column(width=5, justify="right"))
        time_elapsed_column = TimeElapsedColumn()

        self.progress = Progress(total_column, text_column, bar_column, mofn_column, time_elapsed_column)
        self.progress_started = False
        self.tasks = {}
        self.table_total = 0
        self.table_completed = 0

        title = "Fetch metadata"
        text_column = TextColumn("{task.description}", table_column=Column(width=len(title)))
        bar_column = BarColumn(bar_width=80, pulse_style=Style.from_color(Color.from_rgb(244, 164, 96)))
        mofn_column = MofNCompleteColumn(table_column=Column(width=5, justify="right"))
        time_elapsed_column = TimeElapsedColumn()
        self.progress_metadata = Progress(text_column, bar_column, mofn_column, time_elapsed_column)

    def _get_width(self, tables):
        return max([len(x) for x in tables]), len(str(len(tables))) * 2 + 2

    def handle_run_start(self, run_result):
        self.progress_metadata.start()

    def handle_run_progress(self, run_result, total, completed):
        self.table_total = total

    def handle_run_end(self, run_result):
        self.progress.stop()

    def handle_fetch_metadata_start(self):
        task_id = self.progress_metadata.add_task("Fetch metadata", total=None)
        self.tasks["__metadata__"] = task_id

    def handle_fetch_metadata_progress(self, table_name, total, completed):
        task_id = self.tasks["__metadata__"]
        self.progress_metadata.update(task_id, total=total, completed=completed)

    def handle_fetch_metadata_end(self):
        self.progress_metadata.stop()
        print("")
        self.progress.start()
        pass

    def handle_table_start(self, table_result):
        self.table_completed += 1
        table_name = table_result['name']
        padding = ' ' * (len(str(self.table_total)) - len(str(self.table_completed)))
        coft = f'[{padding}{self.table_completed}/{self.table_total}]'
        task_id = self.progress.add_task(table_name, total=None, coft=coft)
        self.tasks[table_name] = task_id
        self.progress.start()

    def handle_table_progress(self, table_result, total, completed):
        if completed == 0:
            table_name = table_result['name']
            task_id = self.tasks[table_name]
            self.progress.update(task_id, total=total)

    def handle_table_end(self, table_result):
        self.progress.stop()
        table_name = table_result['name']
        task_id = self.tasks[table_name]
        self.progress.remove_task(task_id)

    def handle_column_start(self, table_name, column_result):
        pass

    def handle_column_end(self, table_name, column_result):
        task_id = self.tasks[table_name]
        self.progress.update(task_id, advance=1)


def _execute_assertions(console: Console, engine, ds_name: str, output, profiler_result, created_at):
    # TODO: Implement running test cases based on profiling result
    assertion_engine = AssertionEngine(engine)
    assertion_engine.load_assertions(profiler_result)

    results = exceptions = []
    # Execute assertions
    if len(assertion_engine.assertions):
        console.rule('Testing')
        results, exceptions = assertion_engine.evaluate_all()
    return results, exceptions


def _show_dbt_test_result(dbt_test_results, title=None, failed_only=False):
    console = Console()
    ascii_table = Table(show_header=True, show_edge=True, header_style='bold magenta',
                        box=box.SIMPLE, title=title)
    ascii_table.add_column('Status', style='bold white')
    ascii_table.add_column('Test Subject', style='bold')
    ascii_table.add_column('Assertion', style='bold green')
    ascii_table.add_column('Message', style='bold')

    for r in dbt_test_results:
        if failed_only and r.get('status') == 'passed':
            continue
        success = True if r.get('status') == 'passed' else False
        test_name = r.get('display_name')
        table = r.get('table')
        column = r.get('column')
        target = f'[yellow]{table}[/yellow]'
        if column:
            target = f'{target}.[blue]{column}[/blue]'
        message = r.get('message')

        if success:
            ascii_table.add_row(
                '[[bold green]  OK  [/bold green]]',
                target,
                test_name,
                message
            )
        else:
            ascii_table.add_row(
                '[[bold red]FAILED[/bold red]]',
                target,
                test_name,
                message
            )

    if ascii_table.rows:
        console.print(ascii_table)


def _show_assertion_result(results, exceptions, failed_only=False, single_table=None, title=None):
    console = Console()

    def _wrap_pretty(obj):
        if obj is None:
            return '-'
        return obj if isinstance(obj, str) else Pretty(obj)

    if results:
        ascii_table = Table(show_header=True, show_edge=True, header_style='bold magenta',
                            box=box.SIMPLE, title=title)
        ascii_table.add_column('Status', style='bold white')
        ascii_table.add_column('Test Subject', style='bold')
        ascii_table.add_column('Assertion', style='bold green')
        ascii_table.add_column('Expected', style='bold')
        ascii_table.add_column('Actual', style='cyan')

        for assertion in results:
            if single_table and single_table != assertion.table:
                continue
            if failed_only and assertion.result.status():
                continue
            table = assertion.table
            column = assertion.column
            test_function = assertion.result.name
            success = assertion.result.status()
            target = f'[yellow]{table}[/yellow].[blue]{column}[/blue]' if column else f'[yellow]{table}[/yellow]'
            if success:
                ascii_table.add_row(
                    '[[bold green]  OK  [/bold green]]',
                    target,
                    test_function,
                    _wrap_pretty(assertion.result.expected),
                    _wrap_pretty(assertion.result.actual)
                )
            else:
                ascii_table.add_row(
                    '[[bold red]FAILED[/bold red]]',
                    target,
                    test_function,
                    _wrap_pretty(assertion.result.expected),
                    _wrap_pretty(assertion.result.actual)
                )
                if assertion.result.exception:
                    msg = f'[grey11 on white][purple4]{type(assertion.result.exception).__name__}[/purple4](\'{assertion.result.exception}\')[/grey11 on white]'
                    ascii_table.add_row('', '', '', msg)

        if ascii_table.rows:
            console.print(ascii_table)
    # TODO: Handle exceptions
    pass


def _show_recommended_assertion_notice_message(console: Console, results):
    for assertion in results:
        if assertion.result.status() is False and RECOMMENDED_ASSERTION_TAG in assertion.tags:
            console.print(
                f'\n[[bold yellow]Notice[/bold yellow]] You can use command '
                f'"{os.path.basename(sys.argv[0])} generate-assertions" '
                f'to re-generate recommended assertions with new profiling results.')
            break


def _show_dbt_test_result_summary(dbt_test_results, table: str = None):
    if not dbt_test_results:
        return None

    # Prepare DBT Tests Summary
    ascii_table = Table(show_header=True, show_edge=True, header_style='bold magenta', box=box.SIMPLE_HEAVY)
    ascii_table.add_column('Table Name', style='bold yellow')
    ascii_table.add_column('#DBT Tests Executed', style='bold blue', justify='right')
    ascii_table.add_column('#DBT Tests Failed', style='bold red', justify='right')

    test_count = {}
    for r in dbt_test_results:
        t = r.get('table')

        if table is not None and t != table:
            continue
        if t not in test_count:
            test_count[t] = dict(total=0, failed=0)

        test_count[t]['total'] += 1
        test_count[t]['failed'] += 1 if r.get('status') != 'passed' else 0

    for t in test_count:
        ascii_table.add_row(
            t,
            Pretty(test_count[t]['total']),
            Pretty(test_count[t]['failed']),
        )

    return ascii_table


def _show_summary(profiled_result, assertion_results, assertion_exceptions, dbt_test_results, table=None):
    console = Console()
    tables = profiled_result.get('tables', []) if table is None else [table]

    # Prepare PipeRider Assertions Summary
    ascii_table = Table(show_header=True, show_edge=True, header_style='bold magenta', box=box.SIMPLE_HEAVY)
    ascii_table.add_column('Table Name', style='bold yellow')
    ascii_table.add_column('#Columns Profiled', style='bold blue', justify='right')
    ascii_table.add_column('#Tests Executed', style='bold blue', justify='right')
    ascii_table.add_column('#Tests Failed', style='bold red', justify='right')

    ascii_dbt_table = _show_dbt_test_result_summary(dbt_test_results)
    for t in tables:
        _show_table_summary(ascii_table, t, profiled_result, assertion_results)

    if ascii_dbt_table:
        # Display DBT Tests Summary
        console.rule('dbt')
        console.print(ascii_dbt_table)
        _show_dbt_test_result(dbt_test_results, failed_only=True, title="Failed DBT Tests")
        if ascii_table.rows:
            console.rule('PipeRider')

    # Display PipeRider Assertions Summary
    if ascii_table.rows:
        console.print(ascii_table)
        _show_assertion_result(assertion_results, assertion_exceptions, failed_only=True,
                               title='Failed Assertions')


def _show_table_summary(ascii_table: Table, table: str, profiled_result, assertion_results):
    profiled_columns = profiled_result['tables'][table].get('col_count')
    num_of_testcases = 0
    num_of_failed_testcases = 0

    if assertion_results:
        for r in assertion_results:
            if r.table == table:
                num_of_testcases += 1
                if not r.result.status():
                    num_of_failed_testcases += 1

    ascii_table.add_row(
        table,
        Pretty(profiled_columns),
        Pretty(num_of_testcases),
        Pretty(num_of_failed_testcases),
    )


def _transform_assertion_result(table: str, results):
    tests = []
    columns = {}
    if results is None:
        return dict(tests=tests, columns=columns)

    for r in results:
        if r.table == table:
            entry = r.to_result_entry()
            if r.column:
                if r.column not in columns:
                    columns[r.column] = []
                columns[r.column].append(entry)
            else:
                tests.append(entry)

    return dict(tests=tests, columns=columns)


def _validate_assertions(console: Console):
    assertion_engine = AssertionEngine(None)
    assertion_engine.load_all_assertions_for_validation()
    results = assertion_engine.validate_assertions()
    # if results
    for result in results:
        # result
        console.print(f'  [[bold red]FAILED[/bold red]] {result.as_user_report()}')

    if results:
        # stop runner
        return True

    # continue to run profiling
    console.print('everything is OK.')
    return False


def _get_table_list(table, default_schema, dbt_adapter):
    tables = None

    if table:
        table = re.sub(f'^({default_schema})\.', '', table)
        tables = [table]

    if dbt_adapter.is_ready():
        dbt_tables = dbt_adapter.list_dbt_tables(default_schema)
        if not dbt_tables:
            return None, "No table found in dbt project."

        if not table:
            tables = dbt_tables
        elif table not in dbt_tables:
            suggestion = ''
            lower_tables = [t.lower() for t in dbt_tables]
            if table.lower() in lower_tables:
                index = lower_tables.index(table.lower())
                suggestion = f"Do you mean '{dbt_tables[index]}'?"
            return None, f"Table '{table}' doesn't exist in dbt project. {suggestion}"

    return tables, None


def prepare_default_output_path(filesystem: FileSystem, created_at, ds):
    latest_symlink_path = os.path.join(filesystem.get_output_dir(), 'latest')
    latest_source = f"{ds.name}-{convert_to_tzlocal(created_at).strftime('%Y%m%d%H%M%S')}"
    output_path = os.path.join(filesystem.get_output_dir(), latest_source)

    if not os.path.exists(output_path):
        os.makedirs(output_path, exist_ok=True)

    # Create a symlink pointing to the latest output directory
    if os.path.islink(latest_symlink_path):
        os.unlink(latest_symlink_path)
    if not os.path.exists(latest_symlink_path):
        os.symlink(latest_source, latest_symlink_path)
    else:
        console = Console()
        console.print(f'[bold yellow]Warning: {latest_symlink_path} already exists[/bold yellow]')

    return output_path


def _append_descriptions(profile_result):
    for table_v in profile_result['tables'].values():
        table_v['description'] = 'Description: N/A'
        for column_v in table_v['columns'].values():
            column_v['description'] = 'Description: N/A'


def _clean_up_profile_null_properties(table_results):
    removed = []
    for t_metric, t_metric_val in table_results.items():
        if t_metric_val is None:
            removed.append(t_metric)
        elif isinstance(t_metric_val, float) and not math.isfinite(t_metric_val):
            removed.append(t_metric)

    for r in removed:
        del table_results[r]

    removed = []
    for col_name, props in table_results.get('columns', {}).items():
        for k, v in props.items():
            if v is None:
                removed.append(dict(col=col_name, key=k))
            elif isinstance(v, float) and not math.isfinite(v):
                removed.append(dict(col=col_name, key=k))

    for r in removed:
        del table_results['columns'][r['col']][r['key']]


def _append_descriptions_from_assertion(profile_result):
    engine = AssertionEngine(None)
    engine.load_assertion_content()
    for table_name, table_v in engine.assertions_content.items():
        if table_name not in profile_result['tables'] or table_v is None:
            continue
        table_desc = table_v.get('description', '')
        if table_desc:
            profile_result['tables'][table_name]['description'] = f'{table_desc} - via PipeRider'

        columns_content = table_v.get('columns') if table_v.get('columns') else {}
        for column_name, column_v in columns_content.items():
            if column_name not in profile_result['tables'][table_name]['columns'] or column_v is None:
                continue
            column_desc = column_v.get('description', '')
            if column_desc:
                profile_result['tables'][table_name]['columns'][column_name][
                    'description'] = f'{column_desc} - via PipeRider'


def _analyse_and_log_run_event(profiled_result, assertion_results, dbt_test_results, dbt_command):
    tables = profiled_result.get('tables', [])
    event_payload = RunEventPayload()
    event_payload.tables = len(tables)

    # Table info
    for t in tables:
        event_payload.columns.append(profiled_result['tables'][t]['col_count'])
        event_payload.rows.append(profiled_result['tables'][t]['row_count'])

    # Count PipeRider assertions
    for r in assertion_results or []:
        if r.is_builtin:
            event_payload.build_in_assertions += 1
        else:
            event_payload.custom_assertions += 1

        if RECOMMENDED_ASSERTION_TAG in r.tags:
            event_payload.recommended_assertions += 1

        if r.result.status():
            event_payload.passed_assertions += 1
        else:
            event_payload.failed_assertions += 1

    # Count dbt-test cases
    if dbt_test_results:
        for r in dbt_test_results:
            if r.get('status') == 'passed':
                event_payload.passed_dbt_testcases += 1
            else:
                event_payload.failed_dbt_testcases += 1

    event_payload.dbt_command = dbt_command
    event.log_event(event_payload.to_dict(), 'run')


def decorate_with_metadata(profile_result: dict):
    from piperider_cli import __version__
    from piperider_cli.profiler.version import schema_version

    configuration = Configuration.load()
    project_id = configuration.get_telemetry_id()

    profile_result['version'] = __version__
    profile_result['project_id'] = f'{project_id}'
    profile_result['user_id'] = f'{event._collector._user_id}'
    profile_result['metadata_version'] = schema_version()


def _check_test_status(assertion_results, assertion_exceptions, dbt_test_results):
    if assertion_exceptions and len(assertion_exceptions) > 0:
        return False

    if assertion_results:
        for assertion in assertion_results:
            if not assertion.result.status():
                return False

    if dbt_test_results:
        for r in dbt_test_results:
            if r.get('status') == 'failed':
                return False

    return True


class Runner():
    @staticmethod
    def exec(datasource=None, table=None, output=None, skip_report=False, dbt_command='',
             report_dir: str = None):
        console = Console()

        raise_exception_when_directory_not_writable(output)

        configuration = Configuration.load()
        filesystem = FileSystem(report_dir=report_dir)
        datasources = {}
        datasource_names = []
        for ds in configuration.dataSources:
            datasource_names.append(ds.name)
            datasources[ds.name] = ds

        if len(datasource_names) == 0:
            console.print("[bold red]Error: no datasource found[/bold red]")
            return 1

        if datasource and datasource not in datasource_names:
            console.print(f"[bold red]Error: datasource '{datasource}' doesn't exist[/bold red]")
            console.print(f"Available datasources: {', '.join(datasource_names)}")
            return 1

        # Use the first datasource if no datasource is specified
        ds_name = datasource if datasource else datasource_names[0]
        ds = datasources[ds_name]

        passed, reasons = ds.validate()
        if not passed:
            console.print(f"[bold red]Error:[/bold red] The credential of '{ds.name}' is not configured.")
            for reason in reasons:
                console.print(f'    {reason}')
            console.print(
                "[bold yellow]Hint:[/bold yellow]\n  Please execute command 'piperider init' to move forward.")
            return 1

        if not datasource and len(datasource_names) > 1:
            console.print(
                f"[bold yellow]Warning: multiple datasources found ({', '.join(datasource_names)}), using '{ds_name}'[/bold yellow]\n")

        console.print(f'[bold dark_orange]DataSource:[/bold dark_orange] {ds.name}')
        console.rule('Validating')
        err = ds.verify_connector()
        if err:
            console.print(
                f'[[bold red]FAILED[/bold red]] Failed to load the \'{ds.type_name}\' connector.')
            raise err

        try:
            available_tables = ds.verify_connection()
        except Exception as err:
            console.print(
                f'[[bold red]FAILED[/bold red]] Failed to connect the \'{ds.name}\' data source.')
            raise err
        stop_runner = _validate_assertions(console)
        if stop_runner:
            console.print('\n\n[bold red]ERROR:[/bold red] Stop profiling, please fix the syntax errors above.')
            return 1

        default_schema = ds.credential.get('schema')

        dbt_config = ds.args.get('dbt')
        dbt_adapter = DbtAdapter(dbt_config)
        if dbt_config and not dbt_adapter.is_ready():
            raise dbt_adapter.get_error()

        tables = None
        if table:
            tables = [table]

        dbt_test_results = None
        dbt_test_results_compatible = None
        if dbt_command in ['build', 'test'] and dbt_adapter.is_ready():
            dbt_adapter.set_dbt_command(dbt_command)
            dbt_test_results, dbt_test_results_compatible = dbt_adapter.run_dbt_command(table, default_schema)

        console.rule('Profiling')
        run_id = uuid.uuid4().hex
        created_at = datetime.utcnow()
        engine = ds.create_engine()

        if table:
            # cli --table is specified, no inclusion and exclusion applied
            configuration.includes = None
            configuration.excludes = None

        run_result = {}
        profiler = Profiler(engine, RichProfilerEventHandler(tables if tables else available_tables), configuration)
        try:
            profiler_result = profiler.profile(tables)
            run_result.update(profiler_result)
        except NoSuchTableError as e:
            console.print(f"[bold red]Error:[/bold red] No such table '{str(e)}'")
            return 1
        except Exception as e:
            raise Exception(f'Profiler Exception: {type(e).__name__}(\'{e}\')')

        # TODO: refactor input unused arguments
        assertion_results, assertion_exceptions = _execute_assertions(console, engine, ds.name, output,
                                                                      profiler_result, created_at)

        run_result['tests'] = []
        if assertion_results or dbt_test_results:
            console.rule('Assertion Results')
            if dbt_test_results:
                console.rule('dbt')
                _show_dbt_test_result(dbt_test_results)
                run_result['tests'].extend(dbt_test_results)
                if assertion_results:
                    console.rule('PipeRider')
            if assertion_results:
                _show_assertion_result(assertion_results, assertion_exceptions)
                run_result['tests'].extend([r.to_result_entry() for r in assertion_results])

        console.rule('Summary')

        if dbt_test_results_compatible:
            for k, v in dbt_test_results_compatible.items():
                if k not in run_result['tables']:
                    continue
                run_result['tables'][k]['dbt_assertion_result'] = v

        for t in run_result['tables']:
            name_of_result_table = t
            run_result['tables'][t]['piperider_assertion_result'] = _transform_assertion_result(t, assertion_results)
            _clean_up_profile_null_properties(run_result['tables'][t])
        _show_summary(run_result, assertion_results, assertion_exceptions, dbt_test_results)
        _show_recommended_assertion_notice_message(console, assertion_results)

        if dbt_adapter.is_ready():
            dbt_adapter.append_descriptions(run_result, default_schema)
        _append_descriptions_from_assertion(run_result)

        run_result['id'] = run_id
        run_result['created_at'] = datetime_to_str(created_at)
        run_result['datasource'] = dict(name=ds.name, type=ds.type_name)
        decorate_with_metadata(run_result)

        output_path = prepare_default_output_path(filesystem, created_at, ds)
        output_file = os.path.join(output_path, 'run.json')

        # console.print(run_result)
        # console.print(run_result["tables"][name_of_result_table]["columns"])

        # console.print(value_of_mode)

        with open(output_file, 'w') as f:
            f.write(json.dumps(run_result["tables"][name_of_result_table]["columns"], separators=(',', ':')))

        if output:
            clone_directory(output_path, output)

        if skip_report:
            console.print(f'Results saved to {output if output else output_path}')

        _analyse_and_log_run_event(run_result, assertion_results, dbt_test_results, dbt_command)

        if not _check_test_status(assertion_results, assertion_exceptions, dbt_test_results):
            return EC_ERR_TEST_FAILED

        return 0
