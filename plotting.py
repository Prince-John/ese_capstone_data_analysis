import pandas as pd
import json
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib as mpl
import numpy as np

# Load the JSON data from the file
def load_metrics(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data

# Convert the dictionary to a DataFrame
def dict_to_dataframe(metrics):
    # Convert the dictionary to DataFrame
    df = pd.DataFrame.from_dict(metrics, orient='index')
    return df

mpl.rcParams['xtick.labelsize'] = 15  # Change the value as needed
mpl.rcParams['ytick.labelsize'] = 15  # Change the value as needed

def plot_data3(df):
    # Group the DataFrame by both channel_long_buff_ratio and mean_arrival_time
    grouped = df.groupby(['channel_long_buff_ratio', 'mean_arrival_time'])

    # Calculate the mean and standard deviation for each combination
    means = grouped['probability_of_error'].mean().reset_index()
    stds = grouped['probability_of_error'].std().reset_index()

    # Create a single plot
    plt.figure(figsize=(10, 6))

    # Plot means with error bars for each channel_long_buff_ratio group
    for ratio, group_df in means.groupby('channel_long_buff_ratio'):
        std_df = stds[stds['channel_long_buff_ratio'] == ratio]
        plt.errorbar(group_df['mean_arrival_time'], group_df['probability_of_error']*100,
                     yerr=std_df['probability_of_error']*100, fmt='o-', capsize=5,
                     label=f'Channel to Long Buff Ratio: {ratio}', alpha=0.7)

    plt.title('Mean Arrival Rate vs. Probability of Loss', fontsize=20)
    plt.xlabel('Mean Arrival Rate', fontsize=18)
    plt.ylabel('Probability of Loss %', fontsize=18)
    plt.legend(fontsize = 16),
    plt.grid(True)
    plt.xscale('log')  # Set x-axis to log scale
    #plt.show()
    plt.savefig(f'plot.png', bbox_inches='tight', dpi=300)

# Load the metrics
metrics = load_metrics('metrics.json')

# Convert to DataFrame
df_metrics = dict_to_dataframe(metrics)

# Plotting the data
plot_data3(df_metrics)
