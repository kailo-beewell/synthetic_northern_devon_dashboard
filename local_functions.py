# This is a file to locally develop funcitons used in this repository. These functions will later need to be added to the package. The imports in each file where they are used also need to be corrected.


# To be updated in /ynthesise_aggregate.py in package
def results_by_site_and_group(
    data,
    agg_func,
    no_pupils,
    response_col=None,
    labels=None,
    group_type="standard",
    site_col="school_lab",
):
    """
    Aggregate results for all possible sites (schools or areas) and groups
    (setting result to 0 or NaN if no pupils from a particular group are
    present).

    Parameters
    ----------
    data : pandas dataframe
        Pupil-level survey responses, with their school and demographics
    agg_func : function
        Method for aggregating the dataset
    no_pupils: pandas dataframe
        Output of agg_func() where all counts are set to 0 and other results
        set to NaN, to be used in cases where there are no pupils of a
        particular group (e.g. no FSM / SEN / Year 8)
    response_col : list
        Optional argument used when agg_func is aggregate_proportions(). It is
        the list of columns that we want to aggregate.
    labels : dictionary
        Optional argument used when agg_func is aggregate_proportions(). It is
        a dictionary with all possible questions as keys, then values are
        another dictionary where keys are all the possible numeric (or nan)
        answers to the question, and values are relevant label for each answer.
    group_type : string
        Links to the type of demographic groupings performed. Either
        'standard', 'symbol' or 'none' - default is standard.
    site_col: string
        Name of column with site - e.g. 'school_lab' (default), 'msoa'.

    Returns
    -------
    result : pandas DataFrame
        Dataframe where each row has the aggregation results, along with
        the relevant school and pupil groups used in that calculation
    """

    # Initialise list to store results
    result_list = list()

    # Define the groups that we want to aggregate by - when providing a filter,
    # first value is the name of the category and the second is the variable
    if group_type == "standard":
        groups = [
            "All",
            ["Year 8", "year_group_lab"],
            ["Year 10", "year_group_lab"],
            ["Girl", "gender_lab"],
            ["Boy", "gender_lab"],
            ["FSM", "fsm_lab"],
            ["Non-FSM", "fsm_lab"],
            ["SEN", "sen_lab"],
            ["Non-SEN", "sen_lab"],
        ]
    elif group_type == "symbol":
        groups = [
            "All",
            ["Year 7", "year_group_lab"],
            ["Year 8", "year_group_lab"],
            ["Year 9", "year_group_lab"],
            ["Year 10", "year_group_lab"],
            ["Year 11", "year_group_lab"],
            ["Girl", "gender_lab"],
            ["Boy", "gender_lab"],
            ["FSM", "fsm_lab"],
            ["Non-FSM", "fsm_lab"],
        ]
    elif group_type == "none":
        groups = ["All"]

    # For each of the sites (which we know will all be present at least once
    # as we base the site list on the dataset itself)
    sites = data[site_col].dropna().drop_duplicates().sort_values()
    for site in sites:
        # For each the groupings
        for group in groups:
            # Find results for that site. If group is not equal to all,
            # then apply additional filters
            to_agg = data[data[site_col] == site]
            if group != "All":
                to_agg = to_agg[to_agg[group[1]] == group[0]]

            # If the dataframe is empty (i.e. you applied a filter but there
            # were no students matching that filter) then set to the no_pupils
            # df. Otherwise, aggregate the data using the provided function
            if len(to_agg.index) == 0:
                res = no_pupils.copy()
            else:
                if response_col is None:
                    res = agg_func(to_agg)
                else:
                    res = agg_func(
                        data=to_agg, response_col=response_col, labels=labels
                    )

            # Specify what site it was
            res[site_col] = site

            # Set each group as all, replacing one if filter used
            if group_type != "none":
                res["year_group_lab"] = "All"
                res["gender_lab"] = "All"
                res["fsm_lab"] = "All"
                if group_type == "standard":
                    res["sen_lab"] = "All"
                if group != "All":
                    res[group[1]] = group[0]

            # Append results to list
            result_list.append(res)

    # Combine all the results into a single dataframe
    result = pd.concat(result_list)
    return result


# To be updated in ... in package
