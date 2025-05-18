#!/usr/bin/env python
"""
pandas_atop_reader: A toolkit for parsing atop reports into pandas DataFrames.
Supports remote file sync, atop export, and customizable report parsing.
"""


from typing import Optional, List, Dict
import subprocess
import os
import pandas as pd

# SSH/Remote Operations Section


def sync_remote_to_local(
    ssh_connect_string: str,
    local_cache_dir: str = '.atop_cache',
    remote_path: str = "/var/log/atop/",
    rsync_options: str = "-avz"
) -> str:
    """
    Sync remote atop binary files to local cache directory using Rsync over SSH.

    Args:
        ssh_connect_string: SSH connection string (e.g. 'user@host')
        local_cache_dir: Path to local directory for storing binaries
        remote_path: Remote directory containing atop files

    Note:
        For run rsync to without asking password, you will need a ssh-agent.
    """
    # make directory if it doesn't exist
    if not os.path.exists(local_cache_dir):
        os.makedirs(local_cache_dir)
    return subprocess.run(f"rsync {rsync_options} {ssh_connect_string}:{remote_path} {local_cache_dir}/", shell=True, check=True);

# Atop Export Operations Section


def export_text_local(
    atop_file: str,
    kind: Optional[str] = 'cpufreq'
) -> str:
    """
    Run local atop export to text output using 'atop -r <file> -P ...'.

    Args:
        atop_file: Path to local atop binary file
    Returns:
        Pandas timeseries-indexed dataframe
    """
    atop_run_kind = 'cpu'  # default
    if kind == 'cpufreq':
        atop_run_kind = 'cpu'
    decode_cmd = f'atop -r {atop_file} -P {atop_run_kind}'
    process = subprocess.run(decode_cmd, shell=True, capture_output=True, text=True, check=True)
    output = process.stdout
    return parse_text_report(output, kind)


def export_text_remote(
    ssh_connect_string: str,
    atop_file: str,
    kind: Optional[str] = 'cpufreq'
) -> str:
    """
    Run remote atop export when local/remote atop versions differ.

    Args:
        ssh_connect_string: SSH connection target
        atop_file: Remote atop file path
        See export_atop_local() for other arguments

    Returns:
        Pandas timeseries-indexed dataframe
    """
    decode_cmd = f'atop -r {atop_file} -P {kind}'
    exec_string = f'ssh {ssh_connect_string} "{decode_cmd}"'
    process = subprocess.run(exec_string, shell=True, capture_output=True, text=True, check=True)
    output = process.stdout
    return parse_text_report(output, kind)

# Report Parsing Section


def parse_text_report(
    content: str,
    report_type: str = 'cpufreq',
    parsing_options: Optional[Dict] = None
) -> pd.DataFrame:
    """
    Convert atop text output to pandas DataFrame using type-specific parser.

    Args:
        content: Raw text from atop export
        report_type: Report subtype ('cpufreq', 'disk', 'mem', etc.)
        parsing_options: Dictionary with parser-specific configurations

    Returns:
        Parsed DataFrame with appropriate columns

    Raises:
        ValueError: On unsupported report types
    """
    parser_map = {
        'cpufreq': _parse_cpufreq_report,
        'disk': _parse_disk_report
    }

    if report_type not in parser_map:
        raise ValueError(f"Unsupported report type: {report_type}")

    return parser_map[report_type](content, parsing_options or {})


def _parse_cpufreq_report(
    content: str,
    options: Dict
) -> pd.DataFrame:
    """
    Parse CPU frequency scaling metrics from atop report.

    Args:
        content: Raw text input
        options: May contain 'aggregate_subsystems' bool flag

    Returns:
        DataFrame with timestamp-indexed CPU frequency metrics
    """

    lines = content.strip().split('\n')
    blocks = []
    current_block = []
    skip_reset = False

    for line in lines:
        # Handle mode switch signals
        if line == 'RESET':
            skip_reset = True
            current_block = []
        elif line == 'SEP':
            # Skip data immediately after RESET, otherwise finalize block
            if not skip_reset and current_block:
                blocks.append(current_block)
            current_block = []
            skip_reset = False
        else:
            if not skip_reset:
                current_block.append(line)

    # Prepare data structure for metrics
    records = []
    for block in blocks:
        # Quick block validation
        try:
            timestamps = {line.split()[2] for line in block}
            if len(timestamps) != 1:
                continue

            # Bulk data extraction from block
            data = [line.split() for line in block]
            ts = int(data[0][2])  # Unix timestamp
            #  7 for core id,  17 for Mhz value
            cpu_values = {int(row[7]): int(row[17]) for row in data}
            records.append((ts, cpu_values))
        except (IndexError, ValueError):
            continue

    # make timeseries dataframe
    if records:
        timestamps = [ts for ts, _ in records]
        cpu_data = [vals for _, vals in records]
        datetime_index = pd.to_datetime(timestamps, unit='s', utc=True)
        outdf = pd.DataFrame(
            cpu_data,
            index=datetime_index
        ).rename(columns=lambda x: f'cpu{x}').fillna(0).astype(int)
        outdf.index.name = 'timestamp'
    else:
        outdf = pd.DataFrame()

    return outdf


def _parse_disk_report(
    content: str,
    options: Dict
) -> pd.DataFrame:
    """
    Parse disk I/O metrics from atop report (not implemented)

    Args:
        content: Raw text input
        options: May contain 'device_aliases' mapping

    Returns:
        DataFrame with disk statistics
    """
    raise (NotImplementedError)


def get_local_cache(directory: str = './.atop_cache') -> List[str]:
    """
    Return list of full local cache files
    """
    file_list = []

    if not os.path.isdir(directory):
        return []

    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isfile(item_path) and item.startswith('atop'):
            file_list.append(item_path)
    file_list.sort()
    return file_list

# Batch Processing Section


def process_files_batch(
    file_paths: List[str],
    kind: str = 'cpufreq'
) -> pd.DataFrame:
    """
    Process multiple atop files into a single DataFrame.

    Args:
        file_paths: List of local/remote atop file paths
        report_type: Report subtype for parsing

    Returns:
        Combined DataFrame with concatenated results
    """
    dfs = []

    for file_path in file_paths:
        add_df = export_text_local(file_path, kind=kind)
        dfs.append(add_df)

    combined_df = pd.concat(dfs, axis=0) if dfs else pd.DataFrame()
    return combined_df


if __name__ == '__main__':
    # Example usage
    test_file_paths = get_local_cache()
    df = process_files_batch(test_file_paths)
    print(df)
