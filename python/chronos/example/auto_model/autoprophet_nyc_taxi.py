#
# Copyright 2016 The BigDL Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import numpy as np
import pandas as pd
import argparse
import time

from bigdl.chronos.forecaster.prophet_forecaster import ProphetForecaster
from bigdl.chronos.autots.model.auto_prophet import AutoProphet
from bigdl.orca.common import init_orca_context, stop_orca_context


def get_data(args):
    dataset = args.datadir if args.datadir else args.url
    df = pd.read_csv(dataset, parse_dates=[0])
    return df

if __name__ == '__main__':
    # arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--num_workers', type=int, default=2,
                        help="The number of nodes to be used in the cluster. "
                        "You can change it depending on your own cluster setting.")
    parser.add_argument('--cluster_mode', type=str, default='local',
                        help="The mode for the Spark cluster.")
    parser.add_argument('--cores', type=int, default=4,
                        help="The number of cpu cores you want to use on each node."
                        "You can change it depending on your own cluster setting.")
    parser.add_argument('--memory', type=str, default="10g",
                        help="The memory you want to use on each node."
                        "You can change it depending on your own cluster setting.")

    parser.add_argument('--cpus_per_trial', type=int, default=1,
                        help="Int. Number of cpus for each trial")
    parser.add_argument('--n_sampling', type=int, default=32,
                        help="Number of times to sample from the search_space.")
    parser.add_argument('--datadir', type=str,
                        help="Use local csv file by default.")
    parser.add_argument('--url', type=str, default="https://raw.githubusercontent.com/numenta/NAB"
                        "/v1.0/data/realKnownCause/nyc_taxi.csv",
                        help="Download link of dataset.")
    args = parser.parse_args()

    # data prepare
    df = get_data(args)
    df = df.rename(columns={'timestamp': 'ds', 'value': 'y'})

    # train/test split
    end_date = '2015-1-28'  # split by 1-28, which take the last 3 days as horizon
    df_train = df[df['ds'] <= end_date]
    df_test = df[df['ds'] > end_date]

    # use prophet forecaster
    prophet = ProphetForecaster()
    start_time = time.time()
    prophet.fit(df_train, validation_data=df_test)
    prophet_fit_time = time.time() - start_time

    # use autoprophet for HPO
    num_nodes = 1 if args.cluster_mode == "local" else args.num_workers
    init_orca_context(cluster_mode=args.cluster_mode, cores=args.cores,
                      memory=args.memory, num_nodes=num_nodes, init_ray_on_spark=True)
    autoprophet = AutoProphet(cpus_per_trial=args.cpus_per_trial)
    start_time = time.time()
    autoprophet.fit(df_train, cross_validation=True, n_sampling=args.n_sampling)
    autoprophet_fit_time = time.time() - start_time
    stop_orca_context()

    # save and load
    autoprophet.save("autoprophet.ckpt")
    autoprophet = AutoProphet(load_dir="autoprophet.ckpt")

    # evaluate
    auto_searched_mse = autoprophet.evaluate(df_test, metrics=['mse'])[0]
    nonauto_searched_mse = prophet.evaluate(df_test, metrics=['mse'])[0]
    print("Autoprophet improve the mse by",
          str(((nonauto_searched_mse - auto_searched_mse)/nonauto_searched_mse)*100), '%')
    print("auto_searched_mse:", auto_searched_mse)
    print("nonauto_searched_mse:", nonauto_searched_mse)
    print("auto_searched_time:", autoprophet_fit_time)
    print("nonauto_searched_time:", prophet_fit_time)
