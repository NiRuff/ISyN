import pandas as pd
import numpy as np


def learning_rate_sucrose(df, path, group_dict, water_y_suc_n, water_y_suc_y, sucrose_label):

    # create out path
    out_path = path + "/Sucrose_Preference_nosepoke_learning_Data.xlsx"

    df["hourIntervall"] = df["StartTimecode"] // 3600
    df["NosepokePerAnimal"] = df.groupby("Animal")["VisitID"].expanding().count().reset_index(0)["VisitID"]

    # code 1/0 for Correct, Neutral and NotIncorrect
    df["NotIncorrect"] = np.where(df["SideCondition"] != "Incorrect", 1, 0)
    df[sucrose_label] = np.where(df["SideCondition"] == sucrose_label, 1, 0)
    df["Correct"] = np.where(df["SideCondition"] == "Correct", 1, 0)

    # now sum it up
    df["cumNotIncorrectNosepokes"] = df.groupby("Animal")["NotIncorrect"].expanding().sum().reset_index(0)[
        "NotIncorrect"]
    df["cumNeutralNosepokes"] = df.groupby("Animal")[sucrose_label].expanding().sum().reset_index(0)[sucrose_label]
    df["cumCorrectNosepokes"] = df.groupby("Animal")["Correct"].expanding().sum().reset_index(0)["Correct"]
    df["cumulativeLickDuration"] = df.groupby("Animal")["LickDuration"].expanding().sum().reset_index(0)["LickDuration"]
    df["cumNosepokes"] = df.groupby("Animal")["NosepokePerAnimal"].expanding().count().reset_index(0)[
        "NosepokePerAnimal"]

    df["cumNotIncorrectNosepokesRate"] = df["cumNotIncorrectNosepokes"] / df["cumNosepokes"]
    df["cumNeutralNosepokesRate"] = df["cumNeutralNosepokes"] / df["cumNosepokes"]
    df["cumCorrectNosepokesRate"] = df["cumCorrectNosepokes"] / df["cumNosepokes"]

    df["cumulativeLickDurationSucrose"] = \
    df[df["SideCondition"] == sucrose_label].groupby("Animal")["LickDuration"].expanding().sum().reset_index(0)[
        "LickDuration"]

    # set all first ratios per Animal to 0
    df.loc[df.groupby('Animal', as_index=False).head(1).index, 'sucrosePerTotalLickduration'] = 0
    df.loc[df.groupby('Animal', as_index=False).head(1).index, 'cumulativeLickDurationSucrose'] = 0
    df["cumulativeLickDurationSucrose"].fillna(method="ffill", inplace=True)

    df["sucrosePerTotalLickduration"] = df["cumulativeLickDurationSucrose"] / df["cumulativeLickDuration"]

    df_l = df[df["LickDuration"] > 0].copy()
    df_l["LickDurIndex"] = df_l.groupby("Animal")["NosepokePerAnimal"].expanding().count().reset_index(0)[
        "NosepokePerAnimal"]
    df_pivot = df_l.pivot(index="LickDurIndex", columns="Animal", values="sucrosePerTotalLickduration")

    # fill with previous value
    df_pivot.fillna(method="ffill", inplace=True)
    df_filled = df.copy()
    df_filled.fillna(method="ffill", inplace=True)
    df_hour = df_filled.drop_duplicates(subset=["Animal", "hourIntervall"], keep="last")
    df_pivotHour = df_hour.pivot(index="hourIntervall", columns="Animal", values="sucrosePerTotalLickduration")
    df_pivotHour.fillna(method="ffill", inplace=True)

    df_pivotHourNotIncorrect = df_hour.pivot(index="hourIntervall", columns="Animal",
                                             values="cumNotIncorrectNosepokesRate")
    df_pivotHourNotIncorrect.fillna(method="ffill", inplace=True)
    df_pivotHourNeutral = df_hour.pivot(index="hourIntervall", columns="Animal", values="cumNeutralNosepokesRate")
    df_pivotHourNeutral.fillna(method="ffill", inplace=True)
    df_pivotHourCorrect = df_hour.pivot(index="hourIntervall", columns="Animal", values="cumCorrectNosepokesRate")
    df_pivotHourCorrect.fillna(method="ffill", inplace=True)

    df_pivotNosepokeNotIncorrect = df.pivot(index="NosepokePerAnimal", columns="Animal",
                                            values="cumNotIncorrectNosepokesRate")
    df_pivotNosepokeNotIncorrect.fillna(method="ffill", inplace=True)
    df_pivotNosepokeNeutral = df.pivot(index="NosepokePerAnimal", columns="Animal", values="cumNeutralNosepokesRate")
    df_pivotNosepokeNeutral.fillna(method="ffill", inplace=True)
    df_pivotNosepokeCorrect = df.pivot(index="NosepokePerAnimal", columns="Animal", values="cumCorrectNosepokesRate")
    df_pivotNosepokeCorrect.fillna(method="ffill", inplace=True)

    df_pivot_transposed = df_pivot.transpose()
    df_pivotHour_transposed = df_pivotHour.transpose()
    df_pivotNosepokeNotIncorrect_transposed = df_pivotNosepokeNotIncorrect.transpose()
    df_pivotNosepokeNeutral_transposed = df_pivotNosepokeNeutral.transpose()
    df_pivotNosepokeCorrect_transposed = df_pivotNosepokeCorrect.transpose()
    df_pivotHourNotIncorrect_transposed = df_pivotHourNotIncorrect.transpose()
    df_pivotHourNeutral_transposed = df_pivotHourNeutral.transpose()
    df_pivotHourCorrect_transposed = df_pivotHourCorrect.transpose()

    all_dfs = [df_pivot_transposed, df_pivotHour_transposed, df_pivotNosepokeNotIncorrect_transposed,
               df_pivotNosepokeNeutral_transposed, df_pivotNosepokeCorrect_transposed,
               df_pivotHourNotIncorrect_transposed,
               df_pivotHourNeutral_transposed, df_pivotHourCorrect_transposed]

    for curr_df in all_dfs:
        for name, animals in group_dict.items():
            rowname = "Mean" + name
            curr_df.loc[rowname] = curr_df.loc[animals].mean()


    out_path = path + "/Sucrose_Preference_sucroseRate.xlsx"
    writer = pd.ExcelWriter(out_path, engine='xlsxwriter')

    df_pivot_transposed.to_excel(writer, sheet_name="SucroseLickDurationRatioPerNP")
    df_pivotHour_transposed.to_excel(writer, sheet_name="SucroseLickDurationRatioPerHour")

    sheets = ["SucroseLickDurationRatioPerNP", "SucroseLickDurationRatioPerHour"]
    tables = [df_pivot_transposed, df_pivotHour_transposed]

    for i in range(len(sheets)):
        # Access the XlsxWriter workbook and worksheet objects from the dataframe.
        workbook = writer.book
        worksheet = writer.sheets[sheets[i]]

        # Create a chart object
        chart = workbook.add_chart({'type': 'line'})

        # 1 Configure the series of the chart from the dataframe data
        for j in range(len(tables[i].index) - 6):
            row = j + 1
            chart.add_series({
                'name': [sheets[i], row, 0],
                'categories': [sheets[i], 0, 1, 0, len(tables[i].index) - 6],
                'values': [sheets[i], row, 1, row, len(tables[i].columns) + 1],
            })

        worksheet.insert_chart('A35', chart)
        chart2 = workbook.add_chart({'type': 'line'})

        for j in range(len(tables[i].index) - 6, len(tables[i].index)):
            row = j + 1
            chart2.add_series({
                'name': [sheets[i], row, 0],
                'categories': [sheets[i], 0, len(tables[i].index) - 6, 0, len(tables[i].index)],
                'values': [sheets[i], row, 1, row, len(tables[i].columns) + 1],
            })
        worksheet.insert_chart('M35', chart2)

    writer.save()

    out_path = path + "/Sucrose_Preference_learning_Data.xlsx"

    writer = pd.ExcelWriter(out_path, engine='xlsxwriter')
    sheets = []
    tables = []
    if water_y_suc_n:
        df_pivotNosepokeCorrect_transposed.to_excel(writer, sheet_name="CorrectNosepokeRate", startrow=0, startcol=0)
        df_pivotHourCorrect_transposed.to_excel(writer, sheet_name="CorrectNosepokeRateHour", startrow=0, startcol=0)
        sheets.extend(["CorrectNosepokeRate", "CorrectNosepokeRateHour"])
        tables.extend([df_pivotNosepokeCorrect_transposed, df_pivotHourCorrect_transposed])

    if water_y_suc_y:
        df_pivotNosepokeNotIncorrect_transposed.to_excel(writer, sheet_name="NotIncorrectNosepokesRate", startrow=0,
                                                         startcol=0)
        df_pivotHourNotIncorrect_transposed.to_excel(writer, sheet_name="NotIncorrectNosepokeRateHour", startrow=0,
                                                     startcol=0)
        sheets.extend(["NotIncorrectNosepokesRate", "NotIncorrectNosepokeRateHour"])
        tables.extend([df_pivotNosepokeNotIncorrect_transposed, df_pivotHourNotIncorrect_transposed])

    #if water_n_suc_y:
        #df_pivotNosepokeNeutral_transposed.to_excel(writer, sheet_name="NeutralNosepokesRate", startrow=0, startcol=0)
        #df_pivotHourNeutral_transposed.to_excel(writer, sheet_name="NeutralNosepokesRateHour", startrow=0, startcol=0)
        #sheets.extend(["NeutralNosepokesRate","NeutralNosepokesRateHour"])
        #tables.extend([df_pivotNosepokeNeutral_transposed, df_pivotHourNeutral_transposed])

    for i in range(len(sheets)):
        # Access the XlsxWriter workbook and worksheet objects from the dataframe.
        workbook = writer.book
        worksheet = writer.sheets[sheets[i]]

        # Create a chart object
        chart = workbook.add_chart({'type': 'line'})

        # Configure the series of the chart from the dataframe data
        for j in range(len(tables[i].index) - 6):
            row = j + 1
            chart.add_series({
                'name': [sheets[i], row, 0],
                'categories': [sheets[i], 0, 1, 0, len(tables[i].index) - 6],
                'values': [sheets[i], row, 1, row, len(tables[i].columns) + 1],
            })

        worksheet.insert_chart('A35', chart)
        chart2 = workbook.add_chart({'type': 'line'})

        for j in range(len(tables[i].index) - 6, len(tables[i].index)):
            row = j + 1
            chart2.add_series({
                'name': [sheets[i], row, 0],
                'categories': [sheets[i], 0, len(tables[i].index) - 6, 0, len(tables[i].index)],
                'values': [sheets[i], row, 1, row, len(tables[i].columns) + 1],
            })
        worksheet.insert_chart('M35', chart2)
    writer.save()
    print(out_path + " written")


def learning_rate_non_sucrose(df, path, phase, group_dict, no_lick_ex, no_lick_rem, no_lick_only):
    # create out path
    out_path = path + "/" + phase + "_nosepoke_learning_Data.xlsx"

    df["hourIntervall"] = df["StartTimecode"] // 3600

    # create df_licked with only those entries that were incorrect or correct and followed by a lick --> lickduration > 0
    df_temp = df[(df["SideCondition"] == "Incorrect") | (df["LickDuration"] > 0)]
    df_licked = df_temp.copy()

    df["CorrectNoLick"] = np.where((df["SideCondition"] == "Correct") & (df["LickDuration"] == 0), 1, 0)
    df["CorrectAndLick"] = np.where((df["SideCondition"] == "Correct") & (df["LickDuration"] > 0), 1, 0)

    df["NosepokePerAnimal"] = df.groupby("Animal")["VisitID"].expanding().count().reset_index(0)["VisitID"]
    df_licked["NosepokePerAnimal"] = df_licked.groupby("Animal")["VisitID"].expanding().count().reset_index(0)[
        "VisitID"]

    # code 1/0 for Correct, Neutral and NotIncorrect
    df["Correct"] = np.where(df["SideCondition"] == "Correct", 1, 0)
    df_licked["Correct"] = np.where(df_licked["SideCondition"] == "Correct", 1, 0)

    # now sum it up
    df["cumCorrectNoLick"] = df.groupby("Animal")["CorrectNoLick"].expanding().sum().reset_index(0)["CorrectNoLick"]
    df["cumCorrectAndLick"] = df.groupby("Animal")["CorrectAndLick"].expanding().sum().reset_index(0)["CorrectAndLick"]
    df["cumCorrectNosepokes"] = df.groupby("Animal")["Correct"].expanding().sum().reset_index(0)["Correct"]
    df["cumNosepokes"] = df.groupby("Animal")["NosepokePerAnimal"].expanding().count().reset_index(0)["NosepokePerAnimal"]
    df_licked["cumCorrectNosepokes"] = df_licked.groupby("Animal")["Correct"].expanding().sum().reset_index(0)["Correct"]
    df_licked["cumNosepokes"] = df_licked.groupby("Animal")["NosepokePerAnimal"].expanding().count().reset_index(0)["NosepokePerAnimal"]

    df["cumCorrectNosepokesRate"] = df["cumCorrectNosepokes"] / df["cumNosepokes"]
    df["cumCorrectNoLickRate"] = df["cumCorrectNoLick"] / df["cumNosepokes"]
    df["cumCorrectAndLickRate"] = df["cumCorrectAndLick"] / df["cumNosepokes"]
    df_licked["cumCorrectNosepokesRate"] = df_licked["cumCorrectNosepokes"] / df_licked["cumNosepokes"]

    # fill with previous value
    df_filled = df.copy()
    df_filled.fillna(method="ffill", inplace=True)
    df_hour = df_filled.drop_duplicates(subset=["Animal", "hourIntervall"], keep="last")

    df_licked_filled = df_licked.copy()
    df_licked_filled.fillna(method="ffill", inplace=True)
    df_licked_hour = df_licked_filled.drop_duplicates(subset=["Animal", "hourIntervall"], keep="last")

    df_pivotHourCorrect = df_hour.pivot(index="hourIntervall", columns="Animal", values="cumCorrectNosepokesRate")
    df_pivotHourCorrect.fillna(method="ffill", inplace=True)

    df_licked_pivotHourCorrect = df_licked_hour.pivot(index="hourIntervall", columns="Animal",
                                                      values="cumCorrectNosepokesRate")
    df_licked_pivotHourCorrect.fillna(method="ffill", inplace=True)

    df_pivotNosepokeCorrect = df.pivot(index="NosepokePerAnimal", columns="Animal", values="cumCorrectNosepokesRate")
    df_pivotNosepokeCorrect.fillna(method="ffill", inplace=True)

    df_licked_pivotNosepokeCorrect = df_licked.pivot(index="NosepokePerAnimal", columns="Animal",
                                                     values="cumCorrectNosepokesRate")
    df_licked_pivotNosepokeCorrect.fillna(method="ffill", inplace=True)

    df_pivotHourCorrectNoLick = df_hour.pivot(index="hourIntervall", columns="Animal", values="cumCorrectNoLickRate")
    df_pivotHourCorrectNoLick.fillna(method="ffill", inplace=True)

    df_pivotHourCorrectAndLick = df_hour.pivot(index="hourIntervall", columns="Animal", values="cumCorrectAndLickRate")
    df_pivotHourCorrectAndLick.fillna(method="ffill", inplace=True)

    df_licked_pivotNosepokeCorrect_transposed = df_licked_pivotNosepokeCorrect.transpose()
    df_licked_pivotHourCorrect_transposed = df_licked_pivotHourCorrect.transpose()
    df_pivotNosepokeCorrect_transposed = df_pivotNosepokeCorrect.transpose()
    df_pivotHourCorrect_transposed = df_pivotHourCorrect.transpose()
    df_pivotHourCorrectNoLick_transposed = df_pivotHourCorrectNoLick.transpose()
    df_pivotHourCorrectAndLick_transposed = df_pivotHourCorrectAndLick.transpose()

    all_dfs = [df_licked_pivotNosepokeCorrect_transposed, df_licked_pivotHourCorrect_transposed,
               df_pivotNosepokeCorrect_transposed, df_pivotHourCorrect_transposed, df_pivotHourCorrectNoLick_transposed,
               df_pivotHourCorrectAndLick_transposed]



    for curr_df in all_dfs:
        for name, animals in group_dict.items():
            rowname = "Mean" + name
            print(rowname)
            curr_df.loc[rowname] = curr_df.loc[animals].mean()


    writer = pd.ExcelWriter(out_path, engine='xlsxwriter')
    df_pivotNosepokeCorrect_transposed.to_excel(writer, sheet_name="CorrectNosepokeRate", startrow=0, startcol=0)
    df_pivotHourCorrect_transposed.to_excel(writer, sheet_name="CorrectNosepokeRateHour", startrow=0, startcol=0)
    if no_lick_ex:
        df_licked_pivotNosepokeCorrect_transposed.to_excel(writer, sheet_name="CorrNosepokeRateLicked", startrow=0,
                                                       startcol=0)
        df_licked_pivotHourCorrect_transposed.to_excel(writer, sheet_name="CorrNosepokeRateHourLicked", startrow=0,
                                                   startcol=0)
    if no_lick_only:
        df_pivotHourCorrectNoLick_transposed.to_excel(writer, sheet_name="CorrNosepokeNoLick", startrow=0, startcol=0)
    if no_lick_rem:
        df_pivotHourCorrectAndLick_transposed.to_excel(writer, sheet_name="CorrNosepokeAndLick", startrow=0, startcol=0)

    sheets = ["CorrectNosepokeRate", "CorrectNosepokeRateHour"]
    if no_lick_ex:
        sheets.extend(["CorrNosepokeRateLicked", "CorrNosepokeRateHourLicked"])
    if no_lick_only:
        sheets.append("CorrNosepokeNoLick")
    if no_lick_rem:
        sheets.append("CorrNosepokeAndLick")

    tables = [df_pivotNosepokeCorrect_transposed, df_pivotHourCorrect_transposed]
    if no_lick_ex:
        tables.extend([df_licked_pivotNosepokeCorrect_transposed, df_licked_pivotHourCorrect_transposed])
    if no_lick_only:
        tables.append(df_pivotHourCorrectNoLick_transposed)
    if no_lick_rem:
        tables.append(df_pivotHourCorrectAndLick_transposed)

    for i in range(len(sheets)):
        # Access the XlsxWriter workbook and worksheet objects from the dataframe.
        workbook = writer.book
        worksheet = writer.sheets[sheets[i]]

        # Create a chart object
        chart = workbook.add_chart({'type': 'line'})

        # Configure the series of the chart from the dataframe data
        for j in range(len(tables[i].index) - 6):
            row = j + 1
            chart.add_series({
                'name': [sheets[i], row, 0],
                'categories': [sheets[i], 0, 1, 0, len(tables[i].index) - 6],
                'values': [sheets[i], row, 1, row, len(tables[i].columns) + 1],
            })

        worksheet.insert_chart('A35', chart)
        chart2 = workbook.add_chart({'type': 'line'})

        for j in range(len(tables[i].index) - 6, len(tables[i].index)):
            row = j + 1
            chart2.add_series({
                'name': [sheets[i], row, 0],
                'categories': [sheets[i], 0, len(tables[i].index) - 6, 0, len(tables[i].index)],
                'values': [sheets[i], row, 1, row, len(tables[i].columns) + 1],
            })
        worksheet.insert_chart('M35', chart2)
    writer.save()
    print(out_path + " written")
