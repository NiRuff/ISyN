import pandas as pd
import numpy as np


def learning_rate(df, path, phase, group_dict):


    # define intervalls
    df["hourIntervall"] = df["StartTimecode"] // 3600

    # group and sum per animal
    df["totalNosepokes"] = df.groupby("Animal")["NosepokeNumber"].expanding().sum().reset_index(0)["NosepokeNumber"]
    df["totalSideErrors"] = df.groupby("Animal")["SideErrors"].expanding().sum().reset_index(0)["SideErrors"]
    df["totalPlaceErrors"] = df.groupby("Animal")["PlaceError"].expanding().sum().reset_index(0)["PlaceError"]
    df["totalVisits"] = df.groupby("Animal")["VisitOrder"].expanding().count().reset_index(0)["VisitOrder"]

    # calculate SideErrorRate and learningRate
    df["cumSideErrorRate"] = df["totalSideErrors"] / df["totalNosepokes"]
    df["cumPlaceErrorRate"] = df["totalPlaceErrors"] / df["totalVisits"]
    df["correctSidePerNosepoke"] = 1 - df["cumSideErrorRate"]
    df["correctPlacePerVisit"] = 1 - df["cumPlaceErrorRate"]

    # pivot tables per visit
    df_pi_visit_SE = df.pivot(index="VisitOrder", columns="Animal", values="correctSidePerNosepoke")
    df_pi_visit_PE = df.pivot(index="VisitOrder", columns="Animal", values="correctPlacePerVisit")
    df_hour = df.drop_duplicates(subset=["Animal", "hourIntervall"], keep="last")

    # pivot tables per hour
    df_pi_hour_SE = df_hour.pivot(index="hourIntervall", columns="Animal", values="correctSidePerNosepoke")
    df_pi_hour_PE = df_hour.pivot(index="hourIntervall", columns="Animal", values="correctPlacePerVisit")

    # impute missing values
    df_pi_visit_SE.fillna(method="ffill", inplace=True)
    df_pi_hour_SE.fillna(method="ffill", inplace=True)
    df_pi_visit_PE.fillna(method="ffill", inplace=True)
    df_pi_hour_PE.fillna(method="ffill", inplace=True)

    # create transposed datasets
    df_pi_visit_SE_transposed = df_pi_visit_SE.transpose()
    df_pi_hour_SE_transposed = df_pi_hour_SE.transpose()
    df_pi_visit_PE_transposed = df_pi_visit_PE.transpose()
    df_pi_hour_PE_transposed = df_pi_hour_PE.transpose()

    all_dfs = [df_pi_visit_SE_transposed, df_pi_hour_SE_transposed, df_pi_visit_PE_transposed,
               df_pi_hour_PE_transposed]

    for curr_df in all_dfs:
        for name, animals in group_dict.items():
            rowname = "Mean" + name
            curr_df.loc[rowname] = curr_df.loc[animals].mean()

    # create out path
    out_path = path + "/" + phase + "_visit_learning_Data.xlsx"

    # write files
    writer = pd.ExcelWriter(out_path, engine='xlsxwriter')
    df_pi_visit_SE_transposed.to_excel(writer, sheet_name="correctSidePerNosepoke", startrow=0, startcol=0)
    df_pi_hour_SE_transposed.to_excel(writer, sheet_name="correctSidePerNosepokeHour", startrow=0, startcol=0)
    df_pi_visit_PE_transposed.to_excel(writer, sheet_name="correctPlacePerVisit", startrow=0, startcol=0)
    df_pi_hour_PE_transposed.to_excel(writer, sheet_name="correctPlacePerVisitHour", startrow=0, startcol=0)

    sheets = ["correctSidePerNosepoke", "correctSidePerNosepokeHour", "correctPlacePerVisit",
              "correctPlacePerVisitHour"]
    tables = [df_pi_visit_SE_transposed, df_pi_hour_SE_transposed, df_pi_visit_PE_transposed,
              df_pi_hour_PE_transposed]

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

def pivot(df, path, phase, group_dict, hour_intervals = []):

    times = ["StartDate"]
    for entry in hour_intervals:
        col_name = str(int(entry)) + "_hourIntervall"
        df[col_name] = df["StartTimecode"]//(3600*int(entry))
        times.append(col_name)

    #df["6_hourIntervall"] = df["StartTimecode"]//(3600*6)
    #df["12_hourIntervall"] = df["StartTimecode"]//(3600*12)

    values = ["LickDuration", "LickNumber", "NosepokeDuration", "NosepokeNumber"]
    #times = ["StartDate", "12_hourIntervall", "6_hourIntervall"]

    df_pivot_list = list()
    sheets = list()
    ori_col_names = []

    for value in values:
        for time in times:
            df_pivot_list.append(df.pivot_table(columns=time, index="Animal", values=value, aggfunc=np.sum))
            if time == "StartDate":
                sheets.append(value + "_" + "24h")
                ori_col_names.append(time)
            else:
                sheets.append(value + time.replace("_hourIntervall", "h"))
                ori_col_names.append(time)

    for curr_df in df_pivot_list:
        for name, animals in group_dict.items():
            rowname = "Mean" + name
            curr_df.loc[rowname] = curr_df.loc[animals].mean()

    # create out path
    out_path = path + "/" + phase + "_pivot_Data.xlsx"
    writer = pd.ExcelWriter(out_path, engine='xlsxwriter')

    # write df as csv to directory
    df.to_csv( path + "/" + phase + "data.csv")

    for i in range(len(sheets)):

        df_pivot_list[i].to_excel(writer, sheet_name=sheets[i], startrow=0 , startcol=0)
        # Access the XlsxWriter workbook and worksheet objects from the dataframe.
        workbook = writer.book
        worksheet = writer.sheets[sheets[i]]


        # if only one value per interval, insert bins instead of line chart
        # work with ori_col_names

        if (df[ori_col_names[i]].nunique() == 1):
            # Create a chart object
            chart = workbook.add_chart({'type': 'column'})

            # Configure the series of the chart from the dataframe data
            for j in range(len(df_pivot_list[i].index) - 6):
                row = j + 1
                chart.add_series({
                    'name': [sheets[i], row, 0],
                    'categories': [sheets[i], 0, 1, 0, len(df_pivot_list[i].index) - 6],
                    'values': [sheets[i], row, 1, row, len(df_pivot_list[i].columns) + 1],
                })
        else:
            # Create a chart object
            chart = workbook.add_chart({'type': 'line'})

            # Configure the series of the chart from the dataframe data
            for j in range(len(df_pivot_list[i].index)-6):
                row = j + 1
                chart.add_series({
                    'name':       [sheets[i], row, 0],
                    'categories': [sheets[i], 0, 1, 0, len(df_pivot_list[i].index)-6],
                    'values':     [sheets[i], row, 1, row, len(df_pivot_list[i].columns)+1],
                })

        worksheet.insert_chart('A35', chart)

        if (df[ori_col_names[i]].nunique() == 1):
            chart2 = workbook.add_chart({'type': 'column'})
            for j in range(len(df_pivot_list[i].index)-6, len(df_pivot_list[i].index)):
                row = j + 1
                chart2.add_series({
                    'name':       [sheets[i], row, 0],
                    'categories': [sheets[i], 0, 1, 0, len(df_pivot_list[i].index)],
                    'values':     [sheets[i], row, 1, row, len(df_pivot_list[i].columns)+1],
                })
            worksheet.insert_chart('M35', chart2)

        else:
            chart2 = workbook.add_chart({'type': 'line'})
            for j in range(len(df_pivot_list[i].index)-6, len(df_pivot_list[i].index)):
                row = j + 1
                chart2.add_series({
                    'name':       [sheets[i], row, 0],
                    'categories': [sheets[i], 0, 1, 0, len(df_pivot_list[i].index)],
                    'values':     [sheets[i], row, 1, row, len(df_pivot_list[i].columns)+1],
                })
            worksheet.insert_chart('M35', chart2)

    writer.save()
    print(out_path + " written")
