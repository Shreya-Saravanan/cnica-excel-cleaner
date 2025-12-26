import gradio as gr
import pandas as pd

MAX_RESPONDENT_COUNT = 10
MAX_ADDRESS_COUNT = 10

def excel_file_changed(excel_path):
    if excel_path is None:
        return None

    return pd.read_excel(excel_path)

def respondent_slider_changed(respondent_count):
    respondent_tabs = []

    for i in range(MAX_RESPONDENT_COUNT):
        respondent_tab = gr.Tab(visible=i < respondent_count)

        respondent_tabs.append(respondent_tab)

    return respondent_tabs

with gr.Blocks(title="CNICA Excel Cleaner") as app:
    gr.Markdown("# CNICA Excel Cleaner")

    gr.Markdown("### Step 1: Upload Excel File ###")

    excel_file = gr.File(
        label="Excel file",
        file_types=[".xlsx", ".xls"]
    )

    excel_data_frame = gr.DataFrame(
        label="Excel data",
        column_count=0
    )

    gr.Markdown("### Step 2: Select No. of Respondents ###")

    respondent_slider = gr.Slider(
        label="No. of Respondents",
        minimum=1,
        maximum=MAX_RESPONDENT_COUNT,
        step=1,
        interactive=True
    )

    gr.Markdown("### Step 3: Select Respondent's Name and Address Column Headers ###")

    respondent_tabs = []

    for i in range(MAX_RESPONDENT_COUNT):
        with gr.Tab(label=f"Respondent {i + 1}", visible=i==0) as respondent_tab:
            respondent_tabs.append(respondent_tab)

            with gr.Row():
                with gr.Column():
                    gr.Dropdown(
                        label="Name column header"
                    )

                with gr.Column():
                    gr.Slider(
                        label="No. of Address column headers",
                        minimum=1,
                        maximum=MAX_ADDRESS_COUNT,
                        step=1,
                        interactive=True
                    )

                    for j in range(MAX_ADDRESS_COUNT):
                        gr.Dropdown(
                            label=f"Address column header {j + 1}"
                        )

    # Event Listeners

    excel_file.change(
        fn=excel_file_changed,
        inputs=excel_file,
        outputs=excel_data_frame
    )

    respondent_slider.change(
        fn=respondent_slider_changed,
        inputs=respondent_slider,
        outputs=respondent_tabs
    )

app.launch()
