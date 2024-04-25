import os
import json
import pandas as pd
from io import StringIO


def process_file(filepath):
    """
    Processes a single file to extract JSON configuration and CSV data.
    """
    with open(filepath, 'r') as file:
        next(file)  # Skip the first line that contains 'The system configuration is:'
        data = file.read()

    marker = "CSV FILE STARTS BELOW"
    parts = data.split(marker, 1)

    if len(parts) < 2:
        print(f"Skipping {filepath}: unable to find the marker.")
        return None, None, None, None  # Return None if the file format is incorrect

    json_part, csv_part = parts

    try:
        config_dict = json.loads(json_part.strip())
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON in file {filepath}: {e}")
        return None, None, None, None

    # Parse the CSV part into a DataFrame
    csv_io = StringIO(csv_part.strip())
    df = pd.read_csv(csv_io)

    # Calculate the False ratio in the 'state@end' column
    false_count = df['state@end'].value_counts().get(False, 0)
    total_count = len(df)
    false_ratio = false_count / total_count if total_count > 0 else 0

    # Calculate the ratio of num_channels to num_long_buffs
    channels = config_dict.get('num_channels', 0)
    long_buffs = config_dict.get('num_long_buffs', 1)  # Avoid division by zero
    channel_long_buff_ratio = channels / long_buffs if long_buffs > 0 else 0

    return config_dict, df, false_ratio, channel_long_buff_ratio


def process_directory(directory_path, existing_keys):
    """
    Processes all files in the specified directory.
    """
    configurations = {}
    dataframes = {}
    metrics = {}

    for filename in os.listdir(directory_path):
        filepath = os.path.join(directory_path, filename)
        print(f"Processing {filepath}...")
        config, df, false_ratio, channel_long_buff_ratio = process_file(filepath)
        if config is None or df is None:
            continue

        base_key = f"{config['num_channels']}_{config['mean_arrival_time']}"
        unique_key = generate_unique_key(base_key, existing_keys)
        existing_keys.add(unique_key)

        configurations[unique_key] = config
        dataframes[unique_key] = df
        metrics[unique_key] = {'false_ratio': false_ratio, 'channel_long_buff_ratio': channel_long_buff_ratio}

    return configurations, dataframes, metrics

def generate_unique_key(base_key, existing_keys):
    """
    Generates a unique key by appending a number to the base key.
    """
    count = 0
    new_key = f"{base_key}_{count}"
    while new_key in existing_keys:
        count += 1
        new_key = f"{base_key}_{count}"
    return new_key

def process_multiple_directories(directory_paths):
    all_configs = {}
    all_dfs = {}
    all_metrics = {}
    existing_keys = set()

    for directory_path in directory_paths:
        configs, dfs, metrics = process_directory(directory_path, existing_keys)
        all_configs.update(configs)
        all_dfs.update(dfs)
        all_metrics.update(metrics)

    return all_configs, all_dfs, all_metrics


directory_paths = ['data_from_curie', 'data_from_fermi']
all_configs, all_dfs, all_metrics = process_multiple_directories(directory_paths)

# Print out the configurations, data, and metrics
for key in all_configs:
    #print(f"Configuration for {key}:", all_configs[key])
    #print(f"Data for {key} (first few rows):", all_dfs[key].head())
    print(f"Metrics for {key}:", all_metrics[key])


# Saving the metrics to a JSON file
def save_metrics(metrics, filename):
    with open(filename, 'w') as file:
        json.dump(metrics, file)


save_metrics(all_metrics, 'metrics.json')
