import pandas as pd
import numpy as np
from numpy.typing import ArrayLike
from datetime import datetime, timedelta
from typing import List


def load_output_data_hydroshoot(filename: str, indices: List[int], target: str, warmup_days: int = 2) -> pd.DataFrame:
    """"Loads a dataframe from file and extracts relevant data.

    The data is loaded from a CSV-file. This file should have at least one column with label `t` with timestamp
    information at an hourly rate and one column with label `target`. The file is expected to be generated by WheatFSPM,
    usually named `element_states.csv`.

    @:param filename String that specifies the filename of the CSV-file that should be loaded.
    @:param indices: MTG vertices from which to extract data (None if all need to be loaded)
    @:param target Information to extract from data file.
    @:param warmup_days Numer of days at the start of the trace that are discarded to remove transients
    @:return Pandas DataFrame with target information (incl. index if different elements are present) and time information
    """
    df_original = pd.read_csv(filename)
    df_original.loc[:,"t"] = pd.to_datetime(df_original.loc[:,"t"])


    # we regroup per timestamp
    timestamp = -1
    max_index = (df_original.loc[len(df_original)-1, "t"] - df_original.loc[0, "t"]) / timedelta(hours=1)
    max_index = int(np.ceil(max_index)) + 1
    df = {"t": np.zeros(max_index)}
    for i in range(len(df_original)):
        if df_original.iloc[i]["t"] != timestamp:
            timestamp = df_original.iloc[i]["t"]
            t_int = int(np.ceil((timestamp - df_original.loc[0, "t"]) / timedelta(hours=1)))
            df["t"][t_int] = t_int
        index = int(df_original.iloc[i]["vid"])
        if (indices is not None) and (index not in indices):
            continue
        key = f"{target}_{index}"
        if key not in df:
            df[key] = np.zeros(max_index)
        df[key][t_int] = df_original.iloc[i][target]

    df = {i: df[i][24*warmup_days:] for i in df}

    df = pd.DataFrame(df)
    return df.set_index("t")


def load_output_data_wheatfspm(filename: str, target: str, incl_th: int = 500, warmup_days:int=2) -> pd.DataFrame:
    """"Loads a dataframe from file and extracts relevant data.

    The data is loaded from a CSV-file. This file should have at least one column with label `t` with timestamp
    information at an hourly rate and one column with label `target`. The file is expected to be generated by WheatFSPM,
    usually named `element_states.csv`.

    @:param filename String that specifies the filename of the CSV-file that should be loaded.
    @:param target Information to extract from data file.
    @:param incl_th Threshold value of numer of valid entries before item is included in the list
    @:param warmup_days Numer of days at the start of the trace that are discarded to remove transients
    @:return Pandas DataFrame with target information (incl. index if different elements are present) and time information
    """
    df_original = pd.read_csv(filename)

    # we regroup per timestamp
    timestamp = -1
    index = 0
    max_index = int(np.max(df_original["t"]) + 1)
    df = {"t": np.zeros(max_index)}
    for i in range(len(df_original)):
        if df_original.iloc[i]["t"] != timestamp:
            timestamp = int(df_original.iloc[i]["t"])
            df["t"][timestamp] = timestamp
            index = 0
        else:
            index += 1
        key = f"{target}_{index}"
        if key not in df:
            df[key] = np.zeros(max_index)
        df[key][timestamp] = df_original.iloc[i][target]
        key = f"mask_{index}"
        if key not in df:
            df[key] = np.zeros(max_index)
        df[key][timestamp] = df_original.iloc[i]["is_over"]

    for key in df:
        if key.startswith("mask"):
            new_array = np.repeat([True], len(df[key]))
            new_array[df[key] >= 0.5] = False
            df[key] = new_array

    index = len(df["t"])
    rm_keys = []
    for key in df:
        if key.startswith("mask"):
            try:
                end_index = list(df[key]).index(False)
            except ValueError:
                continue
            if end_index >= incl_th:
                index = min(index, end_index)
            else:
                rm_keys.append(key)

    # also add the data to be removed
    rm_keys += [i.replace("mask", target) for i in rm_keys]

    df = {i: df[i][24*warmup_days:index] for i in df if i not in rm_keys}

    df = {i: df[i] for i in df.keys() if not i.startswith("mask")}
    df = pd.DataFrame(df)
    return df.set_index("t")


def load_vertices(fn:str) -> List[int]:
    with open(fn) as f:
        header = f.readline().split(",")
        t_idx = header.index("t")
        vtc_idx = header.index("vid")
        data0 = f.readline().split(",")
        t0 = data0[t_idx]
        vtc = [data0[vtc_idx]]

        while True:
            data = f.readline().split(",")
            t = data[t_idx]
            v = data[vtc_idx]
            if t == t0:
                vtc.append(v)
            else:
                break

    return [int(float(i)) for i in vtc]


def generate_groups_and_masks(df, *, n_day_split=4, discard=(22,3)):
    """"Generates day-based masks for training and testing and day-based groups.

    @:param df: dataframe for which to generate the groups and masks
    @:param n_day_split: number of days to group in train/test interleaving
    @:param discard: time when data should be discarded to limit correlation between days

    @:return groups, train_mask, test_mask
    """
    assert (discard[0] <= 24) and (discard[0] >= 0), "Not within correct range"
    assert (discard[1] <= 24) and (discard[1] <= discard[0]) and (discard[1] >= 0), "Not within correct range"

    df_len = len(df)
    day_mask = [False]*discard[1] + [True]*(discard[0]-discard[1]) + [False]*(24-discard[0])
    train_mask = np.array([True]*24*n_day_split + [False]*24*n_day_split, dtype=bool)
    test_mask = np.array([False]*24*n_day_split + [True]*24*n_day_split, dtype=bool)

    day_mask = np.tile(day_mask, int(np.ceil(df_len / len(day_mask))))
    train_mask = np.tile(train_mask, int(np.ceil(df_len / len(train_mask))))
    test_mask = np.tile(test_mask, int(np.ceil(df_len / len(test_mask))))

    day_mask = day_mask[:df_len]
    train_mask = train_mask[:df_len]
    test_mask = test_mask[:df_len]

    train_mask[np.logical_not(day_mask)] = False
    test_mask[np.logical_not(day_mask)] = False

    groups = np.arange(0, np.ceil(df_len / 24), dtype=int)
    groups = np.repeat(groups, 24)
    groups = groups[:df_len] + 1

    return groups, train_mask, test_mask


def nmse(y: ArrayLike, yh: ArrayLike):
    """"Compute NMSE error metric.

    @:param y: measured values
    @:param yh: predicted values
    @:return NMSE value"""
    return np.mean(np.power(y - yh, 2) / np.var(y))


def load_output_data_grassleaf(filename: str, warmup_days: int = 2) -> pd.DataFrame:
    """"Loads a dataframe from file and extracts relevant data.

    The data is loaded from a CSV-file. This file should have at least one column with label `t` with timestamp
    information at an hourly rate and one column with label `target`. The file is expected to be generated by WheatFSPM,
    usually named `element_states.csv`.

    @:param filename String that specifies the filename of the CSV-file that should be loaded.
    @:param indices: MTG vertices from which to extract data (None if all need to be loaded)
    @:param target Information to extract from data file.
    @:param warmup_days Numer of days at the start of the trace that are discarded to remove transients
    @:return Pandas DataFrame with target information (incl. index if different elements are present) and time information
    """
    df = pd.read_csv(filename, index_col="t")

    df = {i: df[i][24*warmup_days:] for i in df}

    df = pd.DataFrame(df)
    return df


if __name__ == "__main__":
    fn_data_wheatfspm = "WheatFSPM/NEMA15_elements_postprocessing.csv"
    dfo_wheatfspm = load_output_data_wheatfspm(fn_data_wheatfspm, "Transpiration")
    dfi_wheatfspm = pd.read_csv("WheatFSPM/meteo.csv", index_col="t")