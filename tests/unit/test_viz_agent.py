from agents.viz_agent import run_viz_agent
import pandas as pd


def test_viz_runs(sample_df):

    charts = run_viz_agent(sample_df)

    assert isinstance(charts, list)

def test_viz_empty_df():

    df = pd.DataFrame()

    charts = run_viz_agent(df)

    assert isinstance(charts, list)