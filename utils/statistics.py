import pandas as pd
from pandas import DataFrame

from .utils import *


def default_analyser(extracted_data: dict[str, list[dict[str, Any]]], key: str) -> DataFrame:
    df = pd.DataFrame(flatten_list_in_dict(extracted_data))

    stat = {}
    for job, group in df.groupby('job'):
        describe = group[key].describe(percentiles=[0.25, 0.5, 0.75, 0.9])
        stat[job] = {
            'N': describe['count'],
            '90%': describe['90%'],
            '75%': describe['75%'],
            '50%': describe['50%'],
            '25%': describe['25%'],
            'Avg': describe['mean'],
            'Max': describe['max'],
            'Min': describe['min'],
        }

    stat_df = pd.DataFrame(stat).T
    stat_df.sort_values('75%', ascending=False, inplace=True)
    stat_df_fmt = stat_df.loc[:, stat_df.columns != 'N'].map(fmt)
    stat_df_fmt = pd.concat([stat_df['N'].to_frame('N'), stat_df_fmt], axis=1)

    return stat_df_fmt
